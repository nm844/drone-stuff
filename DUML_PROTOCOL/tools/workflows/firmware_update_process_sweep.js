export const meta = {
  name: 'firmware-update-process-sweep',
  description: 'Investigate the WM260 firmware update/upgrade subsystem end-to-end (package verify, A/B OTA engine, upgrade orchestration, modem update)',
  phases: [{ title: 'Investigate' }, { title: 'Verify' }],
}

const ALL_ITEMS = [
  { key: 'dji_fw_verify', paths: ['e1e_extracted/system_files/bin/dji_fw_verify', 'e2_extracted/system_files/bin/dji_fw_verify'] },
  { key: 'dji_upgrade_orchestrator', paths: ['e1e_extracted/system_files/bin/dji_upgrade', 'e2_extracted/system_files/bin/dji_upgrade'] },
  { key: 'update_engine_ab_ota', paths: ['e1e_extracted/system_files/bin/update_engine', 'e2_extracted/system_files/xbin/dji_update_engine'] },
  { key: 'libupgrade_communication', paths: ['e1e_extracted/system_files/lib/libupgrade_communication.so', 'e2_extracted/system_files/lib64/libupgrade_communication.so'] },
  { key: 'libupgrade_module_mngr', paths: ['e1e_extracted/system_files/lib/libupgrade_module_mngr.so', 'e2_extracted/system_files/lib64/libupgrade_module_mngr.so'] },
  { key: 'libupgrade_status', paths: ['e1e_extracted/system_files/lib/libupgrade_status_control.so', 'e1e_extracted/system_files/lib/libupgrade_status_push.so', 'e2_extracted/system_files/lib64/libupgrade_status_control.so', 'e2_extracted/system_files/lib64/libupgrade_status_push.so'] },
  { key: 'libupgrade_lifecycle', paths: ['e1e_extracted/system_files/lib/libupgrade_event.so', 'e1e_extracted/system_files/lib/libupgrade_init.so', 'e1e_extracted/system_files/lib/libupgrade_register.so', 'e2_extracted/system_files/lib64/libupgrade_event.so', 'e2_extracted/system_files/lib64/libupgrade_init.so', 'e2_extracted/system_files/lib64/libupgrade_register.so'] },
  { key: 'libupgrade_product', paths: ['e1e_extracted/system_files/lib/libupgrade_product.so', 'e2_extracted/system_files/lib64/libupgrade_product.so'] },
  { key: 'libupgrade_upgrade_core', paths: ['e1e_extracted/system_files/lib/libupgrade_common.so', 'e1e_extracted/system_files/lib/libupgrade_upgrade.so', 'e2_extracted/system_files/lib64/libupgrade_common.so', 'e2_extracted/system_files/lib64/libupgrade_upgrade.so'] },
  { key: 'libupgrade_test_demo', paths: ['e1e_extracted/system_files/lib/libupgrade_commu_demo.so', 'e1e_extracted/system_files/lib/libupgrade_core_test.so', 'e2_extracted/system_files/lib64/libupgrade_commu_demo.so', 'e2_extracted/system_files/lib64/libupgrade_core_test.so'] },
  { key: 'libdji_sec_ds_whitelist_upgrade', paths: ['e1e_extracted/system_files/lib/libdji_sec_ds_whitelist_upgrade.so'] },
  { key: 'p7_sign', paths: ['e2_extracted/system_files/bin/p7_sign'] },
  { key: 'quectel_modem_upgrade', paths: ['e2_extracted/system_files/bin/Quectel_upgrade_tool', 'e2_extracted/system_files/bin/dongle_upgrade_test.sh', 'e2_extracted/system_files/bin/quectel-qmi-proxy'] },
  { key: 'upgrade_test_clis', paths: ['e1e_extracted/system_files/bin/test_upgrade', 'e2_extracted/system_files/bin/test_upgrade_modified'] },
]

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    ruled_out: { type: 'boolean' },
    new_command_candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          cmd_set: { type: 'string' }, cmd_id: { type: 'string' }, proposed_name: { type: 'string' },
          handler_function: { type: 'string' }, already_known: { type: 'boolean' }, evidence: { type: 'string' },
        },
        required: ['cmd_set', 'cmd_id', 'evidence'],
      },
    },
    architecture_findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: { summary: { type: 'string' }, impact_category: { type: 'string' }, confidence: { type: 'string' }, evidence: { type: 'string' } },
        required: ['summary', 'evidence'],
      },
    },
  },
  required: ['summary', 'ruled_out'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: { refuted: { type: 'boolean' }, reasoning: { type: 'string' } },
  required: ['refuted', 'reasoning'],
}

const BASE = '/home/user/wm260_fw/decrypted'

function investigatePrompt(item) {
  return `You are doing vulnerability-research-style reverse engineering on DJI WM260/Mavic 3 drone firmware, part of a long-running project in nm844/drone-stuff documenting the DUML protocol and firmware architecture. This investigation's topic: the firmware UPDATE/UPGRADE process end-to-end (how an update package is verified, how it gets applied, what daemons orchestrate it).

HARD BOUNDARIES: static analysis only (disassembly, ELF/relocation/string parsing) — never execute a binary, never craft/send a packet. Never write working exploit code, a crafted attack packet, or forged signature/cert/token material. Document weaknesses vulnerability-research style only: name the weakness, impact category, confidence — do not attempt to defeat anything (e.g. do not try to actually forge a signed update package or bypass a signature check — just document that the check exists, what it checks, and any gap you can see directly in the disassembly, like a missing length check or a TOCTOU window).

BACKGROUND YOU SHOULD KNOW:
- This project already found (round 1 of an earlier sweep) that \`upgrade_test\` registers 4 DUML commands under cmd_set 0x00 (\`0x83\`/\`0x85\`/\`0x93\`/\`0x94\`) via \`duss_event_register_dynamic_command\` with literal immediates — that binary is already covered, NOT one of your targets, but if any of your targets' commands look related, check \`DUML_PROTOCOL/cmdset_00_General.md\` before claiming something new.
- Shell scripts already read directly (don't re-derive, just know this context): \`ota.sh\` unzips \`/cache/ota.zip\` to get \`normal.img\`, runs \`dji_fw_verify -n normal /tmp/normal.img\`, then writes \`/cache/recovery/command\` and reboots into recovery mode to apply it. \`recovery_update.sh\` separately flashes \`recovery.img\` itself: compares a live MD5 against the target image, and if different, calls \`dji_fw_verify -n recovery\` before \`dd\`-ing the new image onto the raw recovery partition block device, then re-reads and re-MD5s to confirm the write. Both scripts rely entirely on \`dji_fw_verify\`'s exit code as the trust gate.
- A quick \`strings\` pass on \`update_engine\`/\`dji_update_engine\` already surfaced \`[AB_OTA]\` log-prefixed strings, \`slot_%d.status_%s\`, \`androidboot.slot_suffix=1/2\`, \`boot_partition%d.slot\` — strongly suggesting this firmware ALSO supports (or is derived from code that supports) an Android-style A/B seamless-update slot scheme, architecturally distinct from the simpler single-partition \`ota.sh\`/recovery flow above. If your item is \`update_engine_ab_ota\`, confirm/characterize this properly: is it genuinely wired up and used on this device, or is it vestigial/unused code carried over from a shared codebase? Look for what actually calls/invokes this binary (check other binaries' strings/argv usage, init scripts, etc. if accessible) and what partition layout evidence (via \`e1e-wm260-k2.dtb\`/\`eagle2-wm260-k2.dtb\` or partition-table strings) supports or contradicts real A/B usage.
- \`dji_fw_verify\` and the already-mapped Firmware-Verify OP-TEE TA (\`09db16c0-873b-4fed-b87e-a5d2b86293a2\`, command IDs 0-5 already mapped in \`DUML_PROTOCOL/14_FOLLOWUP_DEEPDIVE_FINDINGS.md\` Track F) back the signature/antirollback checks referenced by both shell scripts above, via \`libfw_util_ca.so\`. If your item is \`dji_fw_verify\`, trace how it invokes that chain and what its CLI argument structure (\`-n <module_name> <path>\`) maps onto the TA's checks.
- Four known DUML command-registration/send mechanisms exist in this codebase: direct \`duss_event_register_dynamic_command\` call with literal cmd_set/cmd_id immediates in registers; the \`duss_mb_create_route_table\`+\`duss_event_create_client\` idiom (does NOT always mean a real per-command registration — check whether a literal handler function pointer is actually wired up); a relocated \`.data\` array of \`{function_pointer, cmd_word}\` 8-byte rows; and \`imss_link_v1_send(cmd_set, cmd_id, ...)\` with literal immediates in r0/r1. Check your target for all four — \`libupgrade_communication.so\`/\`libupgrade_status_push.so\` in particular sound like plausible candidates for sending DUML-formatted progress/status updates.
- Tooling gotcha: \`readelf -r\` (narrow) truncates relocation symbol names on 32-bit ARM — always use \`readelf -rW\`.
- \`libdji_sec_ds_whitelist_upgrade.so\`'s name suggests a security/whitelist gate specifically for upgrades (do-not-downgrade list? signed-module whitelist?) — investigate directly, don't assume from the name alone.
- \`p7_sign\` (PKCS#7 signing tool) ships only on the E2 (camera/gimbal) image's \`bin/\` — check whether anything on this firmware actually invokes it at runtime (grep other binaries' strings for \`p7_sign\`, check init scripts if visible) versus it being leftover build/factory tooling that shouldn't be in a production image at all (a real finding either way).
- \`Quectel_upgrade_tool\`/\`quectel-qmi-proxy\`/\`dongle_upgrade_test.sh\` form a separate firmware-update chain for the LTE/cellular modem dongle — document how it authenticates/verifies the modem firmware it flashes, and whether it reuses any of the \`dji_fw_verify\`/TA infrastructure above or has its own separate (possibly weaker) trust mechanism.

YOUR SPECIFIC TARGET for this investigation — key "${item.key}":
${item.paths.map(p => `  - ${p.startsWith('/') ? p : BASE + '/' + p}`).join('\n')}

Report using the given schema: a summary, whether you're ruling it out, any \`new_command_candidates\` (DUML cmd_set/cmd_id — only if genuinely found, not forced), and any \`architecture_findings\` (vulnerability-research style).`
}

function verifyPrompt(candidate) {
  return `Adversarially try to REFUTE this claim from a DJI drone firmware reverse-engineering project, about a specific DUML command registration. Default to refuted=true unless you can independently re-derive the (cmd_set, cmd_id) pair from the raw ELF bytes yourself (disassemble the actual binary/function named in the evidence). Static analysis only.

CLAIM: ${JSON.stringify(candidate)}

Report {refuted: boolean, reasoning: string}.`
}

phase('Investigate')
const investigations = await pipeline(ALL_ITEMS, item => agent(investigatePrompt(item), { label: `investigate:${item.key}`, phase: 'Investigate', schema: FINDINGS_SCHEMA }))

// NOTE: use `!== true` (not `=== false`), so a candidate whose JSON simply omits
// `already_known` (undefined) still reaches verify instead of silently vanishing
// -- this exact bug dropped a real candidate (cmd_set 0x18/cmd_id 0x3D) from
// verification in the firmware-update-process sweep; see DUML_PROTOCOL/20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md.
const newCmdCandidates = investigations.filter(Boolean).flatMap(r => (r.new_command_candidates || []).filter(c => c.already_known !== true))
log(`Investigate phase done. ${newCmdCandidates.length} new DUML command candidates to verify.`)

phase('Verify')
const verifyDetail = await pipeline(newCmdCandidates, async candidate => {
  const votes = await parallel([1, 2, 3].map(() => () => agent(verifyPrompt(candidate), { phase: 'Verify', schema: VERDICT_SCHEMA })))
  const refuteCount = votes.filter(Boolean).filter(v => v.refuted).length
  const survives = refuteCount < 2
  return { candidate, votes, survives }
})

const verified = verifyDetail.filter(v => v.survives).map(v => v.candidate)

return {
  investigations,
  all_candidates_considered: newCmdCandidates.length,
  verified_count: verified.length,
  verified,
  verify_detail: verifyDetail,
  stats: { items: ALL_ITEMS.length, new_cmd_candidates: newCmdCandidates.length },
}
