export const meta = {
  name: 'wm260-exhaustive-command-sweep',
  description: 'Sweep remaining undocumented WM260 binaries for undiscovered DUML commands, with adversarial reverify on any new finds',
  phases: [
    { title: 'Investigate', detail: '24 binaries/libraries never individually examined for DUML command registration' },
    { title: 'Verify', detail: 'Adversarial 3-skeptic reverify on every genuinely new (cmd_set,cmd_id) candidate' },
  ],
}

const BASE = '/home/user/wm260_fw/decrypted'

const TIER1 = [
  { key: 'app_echo', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/bin/app_echo`, `${BASE}/e2_extracted/system_files/bin/app_echo`] },
  { key: 'ss_dsp_manager', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/bin/ss_dsp_manager`, `${BASE}/e2_extracted/system_files/bin/ss_dsp_manager`] },
  { key: 'test_dji_blackbox', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/bin/test_dji_blackbox`, `${BASE}/e2_extracted/system_files/bin/test_dji_blackbox`] },
  { key: 'upgrade_test_family', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/bin/test_upgrade`, `${BASE}/e1e_extracted/system_files/bin/upgrade_test`, `${BASE}/e2_extracted/system_files/bin/upgrade_test`, `${BASE}/e2_extracted/system_files/bin/test_upgrade_modified`] },
  { key: 'libdcam_observer_dsh.so', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/lib/camera/plugins/observer/libdcam_observer_dsh.so`, `${BASE}/e2_extracted/system_files/lib64/camera/plugins/observer/libdcam_observer_dsh.so`] },
  { key: 'libMipiHandshake.so', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/lib/libMipiHandshake.so`] },
  { key: 'libWorkModeLiveview.so', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/lib/libWorkModeLiveview.so`] },
  { key: 'libhyperlapse_eis.so', tier: 1, paths: [`${BASE}/e1e_extracted/system_files/lib/libhyperlapse_eis.so`] },
  { key: 'DDSClientv1', tier: 1, paths: [`${BASE}/e2_extracted/system_files/bin/DDSClientv1`] },
  { key: 'duml_googletest', tier: 1, paths: [`${BASE}/e2_extracted/system_files/bin/duml_googletest`] },
  { key: 'stress_test_mb_family', tier: 1, paths: [`${BASE}/e2_extracted/system_files/bin/stress_test_mb_benchmark_local`, `${BASE}/e2_extracted/system_files/bin/stress_test_mb_publish_local`] },
  { key: 'libdcam_imu_handle_link_node.so', tier: 1, paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/link_node/libdcam_imu_handle_link_node.so`] },
  { key: 'libdcam_cs_duss_proxy.so', tier: 1, paths: [`${BASE}/e2_extracted/system_files/lib64/camera/plugins/proxy/libdcam_cs_duss_proxy.so`] },
  { key: 'libdcam_event_client_pool.so', tier: 1, paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_event_client_pool.so`] },
  { key: 'libdcam_vtx_sm.so', tier: 1, paths: [`${BASE}/e2_extracted/system_files/lib64/libdcam_vtx_sm.so`] },
  { key: 'librcam.so', tier: 1, paths: [`${BASE}/e2_extracted/system_files/lib64/librcam.so`] },
]

const TIER2 = [
  { key: 'dji_ftpd', tier: 2, paths: [`${BASE}/e1e_extracted/system_files/bin/dji_ftpd`, `${BASE}/e2_extracted/system_files/bin/dji_ftpd`] },
  { key: 'bsa_server', tier: 2, paths: [`${BASE}/e2_extracted/system_files/bin/bsa_server`] },
  { key: 'cam_dt_cmdline', tier: 2, paths: [`${BASE}/e1e_extracted/system_files/bin/cam_dt_cmdline`, `${BASE}/e2_extracted/system_files/bin/cam_dt_cmdline`] },
  { key: 'wms_ipc_dsock.so', tier: 2, paths: [`${BASE}/e2_extracted/system_files/lib64/wms_ipc_dsock.so`] },
  { key: 'libmt_client.so', tier: 2, paths: [`${BASE}/e2_extracted/system_files/lib64/libmt_client.so`] },
  { key: 'libsrv_um.so', tier: 2, paths: [`${BASE}/e2_extracted/system_files/lib64/libsrv_um.so`] },
  { key: 'libdcamecg_process.so', tier: 2, paths: [`${BASE}/e1e_extracted/system_files/lib/libdcamecg_process.so`, `${BASE}/e2_extracted/system_files/lib64/libdcamecg_process.so`] },
  { key: 'libdcam_base.so', tier: 2, paths: [`${BASE}/e1e_extracted/system_files/lib/libdcam_base.so`, `${BASE}/e2_extracted/system_files/lib64/libdcam_base.so`] },
]

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    ruled_out: { type: 'boolean', description: 'true if this binary/library has no DUML command-registration role at all' },
    new_command_candidates: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          cmd_set: { type: 'string', description: 'hex, e.g. 0x02' },
          cmd_id: { type: 'string', description: 'hex, e.g. 0x1A' },
          proposed_name: { type: 'string' },
          handler_function: { type: 'string' },
          already_known: { type: 'boolean', description: 'true if this pair already exists in ALL_COMMANDS.csv -- check before reporting' },
          evidence: { type: 'string' },
          confidence: { type: 'string' },
        },
        required: ['cmd_set', 'cmd_id', 'proposed_name', 'already_known', 'evidence', 'confidence'],
      },
    },
    architecture_findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          summary: { type: 'string' },
          impact_category: { type: 'string' },
          confidence: { type: 'string' },
          evidence: { type: 'string' },
        },
        required: ['summary', 'impact_category', 'confidence', 'evidence'],
      },
    },
  },
  required: ['summary', 'ruled_out', 'new_command_candidates', 'architecture_findings'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reasoning: { type: 'string' },
  },
  required: ['refuted', 'reasoning'],
}

function investigatePrompt(item) {
  return `You are reverse-engineering DJI WM260/Mavic 3 drone firmware as part of an authorized, ongoing security-research project. This is dual-use RE work on the owner's own drone firmware -- architecture/vulnerability documentation only, never exploit code.

TARGET: ${item.key} (tier ${item.tier})
File path(s) on disk (ELF binaries/shared libraries, already extracted from the firmware images -- E1E = ARM32, E2 = aarch64):
${item.paths.map(p => `  - ${p}`).join('\n')}

BACKGROUND: This project has fully reverse-engineered DJI's DUML v1 wire protocol (11-byte frame header + CRC16, a 1-byte cmd_set + 1-byte cmd_id addressing every command). It has already catalogued 888 known (cmd_set, cmd_id) pairs, most from the public dji-firmware-tools Wireshark dissector, plus several found by this project's own binary disassembly. The master list of everything ALREADY known is at /home/user/drone-stuff/DUML_PROTOCOL/ALL_COMMANDS.csv (CSV, columns include cmd_set and cmd_id as hex strings) -- READ THIS FIRST so you can tell a genuinely NEW command apart from one already catalogued.

Three known command-registration mechanisms this project has found elsewhere in this same firmware (use these as your search patterns, but also recognize a plausible NEW mechanism if you find one):
1. Direct calls to the imported function \`duss_event_register_dynamic_command(cmd_set, cmd_id, handler_fn, ...)\` -- cmd_set/cmd_id are usually loaded as small-integer literals into registers immediately before the \`bl\`/\`blx\` call site (ARM32: r0-r3 convention; aarch64: x0-x3). Find the PLT/GOT entry for this symbol via \`readelf -rW <file>\`, then disassemble (objdump -d, or capstone via python3) the call sites and read back the immediately-preceding mov/movw/movt (ARM32) or mov/movz (aarch64) instructions for literal operand values.
2. The \`duss_mb_create_route_table\` + \`duss_event_create_client\` idiom (seen in dji_media_server) -- registers a named client/route rather than individual cmd_ids directly; look for associated route-table name strings and any numeric command IDs handled downstream of that client.
3. An R_ARM_RELATIVE / R_AARCH64_RELATIVE relocated \`.data\` array of 8-byte rows shaped {function_pointer, cmd_word}, where cmd_word's low byte is cmd_set and high byte is cmd_id (seen in dji_flight at vaddr 0xae0f8) -- scan relocated .data sections for repeating 8-byte-stride patterns where one half of each row resolves to a function address inside the binary's own .text.

YOUR TASK for ${item.key}:
- Determine whether this binary/library registers or handles ANY DUML (cmd_set, cmd_id) pair via mechanism 1, 2, 3, or any other plausible mechanism you find (describe it if novel).
${item.tier === 2 ? '- This is a TIER-2 (lighter-check) target: a prior mechanical scan found it opens its own listening socket and references DUML-adjacent symbols weakly or not at all, but it has NOT been checked for an actual registration call. Spend a bounded amount of effort (don\'t go down a multi-hour rabbit hole) -- determine whether it participates in the DUML bus at all, and if not, say so plainly with brief evidence (ruled_out: true) rather than speculating.' : '- This is a TIER-1 (strong-signal) target: a prior mechanical scan already confirmed a real ELF relocation from this binary to one of the three registration APIs above. You should find at least one real registration call site -- your job is to extract the EXACT (cmd_set, cmd_id) literal values at each call site and the handler function each one points to, plus check for any adjacent relocated-array mechanism (#3) that might hide additional commands beyond the directly-registered ones (this pattern -- direct calls AND a hidden array -- is exactly how dji_flight\'s extra commands were found in earlier work).'}
- For EVERY (cmd_set, cmd_id) pair you find, check it against ALL_COMMANDS.csv and set already_known accordingly. Only pairs with already_known: false are "new command candidates" in the sense that matters here -- but report pairs you confirm even if already known, since confirming a real implementation behind an existing public-dissector-only entry is also valuable (put those under architecture_findings instead, not new_command_candidates).
- If this binary/library plays no DUML command-registration role whatsoever, set ruled_out: true, leave new_command_candidates empty, and give a one-paragraph summary of what it actually does and why it's unrelated.
- Also report any genuine architecture/security-relevant facts you notice along the way (auth gaps, injection-shaped primitives, etc.) as architecture_findings, in the same impact_category/confidence/evidence style this project always uses -- weakness-naming and architecture-fact level ONLY, never exploit code, crafted packets, or attack recipes.

HARD BOUNDARIES (non-negotiable, this project enforces these everywhere):
- Never open, disassemble, or analyze \`libamt_util.so\` (OP-TEE TA UUID e91c9402-64a0-470f-88e7-bf5d3c606b6a) under any circumstances, even as a side reference.
- Document architecture/weaknesses only -- no working exploit payloads, crafted attack packets, forged tokens, or step-by-step attack recipes, ever.
- OP-TEE TA command IDs (TEEC_InvokeCommand namespace) are a DIFFERENT, non-DUML protocol -- do not conflate them with DUML cmd_set/cmd_id even if you encounter them.

Standard RE tools available: readelf, objdump, nm, strings, file, and python3 with capstone/pyelftools installed. Work efficiently -- this is one of 24 parallel investigations, not the only one.`
}

function verifyPrompt(candidate) {
  return `Adversarially verify this specific reverse-engineering claim about DJI WM260/Mavic 3 drone firmware. Try to REFUTE it by independently re-deriving it from the raw binary -- default to refuted: true if you cannot independently confirm it.

CLAIM: In the file(s) ${candidate._paths ? candidate._paths.join(', ') : '(see evidence)'}, there is a previously-undocumented DUML command (cmd_set=${candidate.cmd_set}, cmd_id=${candidate.cmd_id}), proposed name "${candidate.proposed_name}", handler function "${candidate.handler_function || '(unspecified)'}".

ORIGINAL EVIDENCE PROVIDED: ${candidate.evidence}

Independently re-derive this from the raw ELF: find the actual relocation/call site or data-array row yourself (do not just trust the description -- re-run readelf/objdump/capstone yourself), confirm the exact cmd_set and cmd_id byte values, and confirm this pair is NOT already in /home/user/drone-stuff/DUML_PROTOCOL/ALL_COMMANDS.csv (re-check it yourself, don't trust the original claim's already_known flag). Report refuted:true if the mechanism doesn't hold up, the byte values are wrong, or the pair turns out to already be known. Report refuted:false only if you independently confirm it holds.

Remember: never touch libamt_util.so; this is architecture-fact verification only, not exploit development.`
}

phase('Investigate')
const ALL_ITEMS = [...TIER1, ...TIER2]
const investigations = await pipeline(
  ALL_ITEMS,
  (item) => agent(investigatePrompt(item), { label: `investigate:${item.key}`, phase: 'Investigate', schema: FINDINGS_SCHEMA })
    .then(r => r ? { ...r, _key: item.key, _tier: item.tier, _paths: item.paths } : null)
)

const validInvestigations = investigations.filter(Boolean)
const trulyNewCandidates = validInvestigations.flatMap(inv =>
  (inv.new_command_candidates || [])
    .filter(c => c.already_known === false)
    .map(c => ({ ...c, _source_key: inv._key, _paths: inv._paths }))
)

log(`Investigate phase done: ${validInvestigations.length}/${ALL_ITEMS.length} returned, ${trulyNewCandidates.length} candidate new commands to verify`)

phase('Verify')
const verifiedCandidates = trulyNewCandidates.length === 0 ? [] : await parallel(
  trulyNewCandidates.map(c => () =>
    parallel([1, 2, 3].map(() => () => agent(verifyPrompt(c), { phase: 'Verify', schema: VERDICT_SCHEMA })))
      .then(votes => {
        const valid = votes.filter(Boolean)
        const refuteCount = valid.filter(v => v.refuted).length
        return { ...c, votes: valid, survives: valid.length > 0 && refuteCount < Math.ceil(valid.length / 2) }
      })
  )
)

return {
  investigations: validInvestigations.map(inv => ({
    key: inv._key,
    tier: inv._tier,
    paths: inv._paths,
    summary: inv.summary,
    ruled_out: inv.ruled_out,
    architecture_findings: inv.architecture_findings,
    already_known_commands_confirmed: (inv.new_command_candidates || []).filter(c => c.already_known === true),
  })),
  candidate_new_commands_verified: verifiedCandidates,
  stats: {
    total_targets: ALL_ITEMS.length,
    tier1: TIER1.length,
    tier2: TIER2.length,
    ruled_out_count: validInvestigations.filter(i => i.ruled_out).length,
    candidates_proposed: trulyNewCandidates.length,
    candidates_surviving_reverify: verifiedCandidates.filter(v => v.survives).length,
  },
}
