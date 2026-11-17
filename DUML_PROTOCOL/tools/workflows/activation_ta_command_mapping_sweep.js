export const meta = {
  name: 'activation-ta-command-mapping',
  description: 'Map libamt_util.so / e91c9402 activation TA command-ID tables and deepen dji_sec activation handshake (newly authorized target)',
  phases: [{ title: 'Investigate' }, { title: 'Verify' }],
}

const ALL_ITEMS = [
  { key: 'libamt_util_ca', paths: ['e1e_extracted/system_files/lib/libamt_util.so', 'e2_extracted/system_files/lib64/libamt_util.so'] },
  { key: 'e91c9402_ta_elf_decrypted', paths: ['/tmp/claude/ta_extract/unsign_out/e91c9402-64a0-470f-88e7bf5d3c606b6a.elf'] },
  { key: 'libdji_secure_act_dispatch', paths: ['e1e_extracted/system_files/lib/libdji_secure.so', 'e2_extracted/system_files/lib64/libdji_secure.so'] },
  { key: 'dji_amt_daemon', paths: ['e1e_extracted/system_files/bin/dji_amt', 'e2_extracted/system_files/bin/dji_amt'] },
  { key: 'amt_test_cmd_cli', paths: ['e1e_extracted/system_files/bin/amt_test_cmd', 'e2_extracted/system_files/bin/amt_test_cmd'] },
]

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    ruled_out: { type: 'boolean' },
    ta_command_mappings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          component: { type: 'string' },
          exported_or_internal_name: { type: 'string' },
          command_id_hex: { type: 'string' },
          side: { type: 'string', description: '"CA" (normal-world client wrapper) or "TA" (inside the TEE binary itself)' },
          evidence: { type: 'string' },
          confidence: { type: 'string' },
        },
        required: ['component', 'exported_or_internal_name', 'command_id_hex', 'side', 'evidence'],
      },
    },
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
  return `You are doing vulnerability-research-style reverse engineering on DJI WM260/Mavic 3 drone firmware, part of a long-running project in the repo nm844/drone-stuff documenting the DUML protocol and firmware architecture.

NEWLY AUTHORIZED SCOPE (read carefully, this changes a prior standing rule): the project owner has now explicitly authorized opening, disassembling, and mapping command IDs inside \`libamt_util.so\` and the OP-TEE Trusted Application it talks to (UUID \`e91c9402-64a0-470f-88e7-bf5d3c606b6a\`, the activation / secure-debug ("SSD") / DJICare / RPMB-key-repository TA). This was previously off-limits project-wide (see \`DUML_PROTOCOL/13_OPTEE_TA_FINDINGS.md\`, \`14_FOLLOWUP_DEEPDIVE_FINDINGS.md\` Track F, and every sweep doc since — all of them explicitly declined to touch this one file while mapping the other three TAs' command tables). That exclusion is lifted now, specifically for this file and this TA, and for this project's activation-process research going forward.

HARD BOUNDARIES THAT STILL APPLY, UNCHANGED:
- Static analysis only: disassembly (readelf/objdump/capstone/pyelftools), string/export enumeration, relocation parsing. Never execute a binary, never craft or send a wire packet.
- Never write or produce working exploit code, a crafted attack packet, or a forged authorization/activation/one-time-auth token/MAC/signature.
- Never attempt cryptanalysis of a live cryptographic mechanism — do not try to break, derive, or extract the ECC challenge-response keys, RPMB-backed secrets, RSA/AES keys, or any MAC/signature scheme. You may fully document *what* a function does, *what* it checks, and *any* missing-validation/logic gap you can see directly in the disassembly (naming the weakness, its impact category, and your confidence) — exactly like this project's existing findings docs do for the three already-mapped TAs (e.g. doc 14 Track F found the NFZ TA's CA forwards its caller's argument into TEEC_InvokeCommand with no local range check — an architecture observation, not a demonstrated bypass). You must NOT go further than that documentation step.
- If you find yourself about to write code that would actually compute a valid activation MAC, forge a DJICare whitelist entry, or bypass the SSD challenge-response, STOP — that crosses the line. Report it as an architectural description instead ("function X computes a MAC over fields A/B/C using an HMAC-like construction; the key material is TEE/RPMB-resident and was not extracted").

BACKGROUND YOU SHOULD KNOW (don't re-derive from scratch):
- Doc 13 already decrypted the TA container and mapped \`e91c9402\`'s ~45 CA-side exports in \`libamt_util.so\` by name only (no command-ID mapping): \`dji_active_rpmb_get/set\`, \`dji_ssd_bind/verify/get_challenge/get_status/unbind\`, \`dji_generate_active_mac\`, \`dji_generate_onetime_active_mac\`, \`dji_verify_onetime_active_sign_msg\`, \`dji_device_bind_*\`, \`djicare_*\`, \`dji_keyrepo_*\`, \`dec_calibration_file\`, \`enc_fc_dtcm\`, \`https_client_sign\`, \`https_check_private_key\`, \`pkcs12_parse\`, \`cloud_get_device_secret\`, \`amt_get_derive_adsb_key\`, \`amt_get_derive_log_key\`. Use \`readelf --dyn-syms\`/\`nm -D\` on your actual target file to get the real, complete export list rather than trusting this list from memory — it may be incomplete.
- Doc 14 Track F already mapped the OTHER three TAs' command-ID tables using this method: resolve \`TEEC_InvokeCommand\`'s PLT/GOT relocation, find each exported wrapper's call site, read the literal command-id immediate loaded into the register right before the call (same "literal immediate before the call" pattern this project uses everywhere for DUML registration). A working script for exactly this, written for a prior pass, is at \`/tmp/claude/ta_extract/find_cmdids.py\` (pyelftools + capstone) — read it and adapt it; don't reinvent the PLT-stub-resolution logic from zero if it already works.
- Doc 5 (\`DUML_PROTOCOL/05_DJI_SEC_FINDINGS.md\`) already disassembled \`libdji_secure.so\`'s E1E (32-bit) build and found \`sec_cmd_act_command_handler\` (vaddr \`0xbb44\`) dispatches on the first message byte over at least 11 values: \`0x00, 0x31, 0x35, 0x37, 0x38, 0x39, 0x3b, 0x3c, 0x3f, 0xf4, 0xf5\`, each routing to one of the imported \`sec_cmd_act_*\`/one-time-auth functions. That mapping of byte-value to function name was NOT fully written out in the existing doc — if your item is \`libdji_secure_act_dispatch\`, try to recover it completely and also look for any further byte-level field structure (offsets after the leading subcommand byte) visible directly in the disassembly.
- Tooling gotcha this project hit before: \`readelf -r\` (narrow) truncates relocation symbol names on 32-bit ARM — always use \`readelf -rW\` (wide).
- Four known DUML command-registration/send mechanisms exist in this codebase (direct \`duss_event_register_dynamic_command\` call with literal cmd_set/cmd_id immediates; the \`duss_mb_create_route_table\`+\`duss_event_create_client\` idiom, which does NOT always mean a real per-command registration; a relocated \`.data\` array of \`{function_pointer, cmd_word}\` 8-byte rows; and \`imss_link_v1_send(cmd_set, cmd_id, ...)\` with literal immediates in r0/r1, discovered in a gimbal-calibration plugin) — check for these too if your target (\`dji_amt_daemon\`, \`amt_test_cmd_cli\`) looks like it might participate in the DUML bus directly, not just the TEE side.

YOUR SPECIFIC TARGET for this investigation — key "${item.key}":
${item.paths.map(p => `  - ${p.startsWith('/') ? p : BASE + '/' + p}`).join('\n')}

${item.key === 'e91c9402_ta_elf_decrypted' ? `This file is the actual decrypted OP-TEE TA ELF (ARM32, ET_DYN, stripped but has .dynsym). Its command dispatch lives in its \`TA_InvokeCommandEntryPoint\` export (or whatever function that symbol/the TA's small export table resolves to) — disassemble it to recover the TA-SIDE command-ID switch/table (a literal integer compare/switch on the \`cmd_id\` argument). This is the authoritative, independent cross-check against the CA-side (libamt_util.so) mapping — matching exactly how Track F validated the FW-verify TA (clean sequential 0-5) and ADS-B TA (0x11-0x14) from both angles.` : ''}

${item.key === 'libamt_util_ca' ? `For every exported wrapper function, find its TEEC_InvokeCommand call site and the literal command-id immediate passed. Do this for BOTH the e1e (32-bit ARM, readelf -rW) and e2 (64-bit aarch64) builds and cross-check they agree.` : ''}

For your target, report back using the given schema: a summary, whether you're ruling it out (no reachable/mappable signal), any \`ta_command_mappings\` rows you can support with evidence, any \`new_command_candidates\` (DUML cmd_set/cmd_id — only if you genuinely find one, this is NOT the main expected outcome here), and any \`architecture_findings\` (vulnerability-research style: name the weakness, impact category, confidence — never an exploit).`
}

function verifyPrompt(candidate) {
  return `Adversarially try to REFUTE this claim from a DJI drone firmware reverse-engineering project. Default to refuted=true unless you can independently reproduce the claim from the raw bytes yourself (disassemble/parse the actual file referenced in the evidence). This is static-analysis-only vulnerability research — do not execute anything, do not attempt to forge, bypass, or cryptanalyze anything; just check whether the evidence actually supports the claim as stated.

CLAIM: ${JSON.stringify(candidate)}

Report {refuted: boolean, reasoning: string}.`
}

phase('Investigate')
const investigations = await pipeline(ALL_ITEMS, item => agent(investigatePrompt(item), { label: `investigate:${item.key}`, phase: 'Investigate', schema: FINDINGS_SCHEMA }))

const taMappingCandidates = investigations.filter(Boolean).flatMap(r => (r.ta_command_mappings || []).map(m => ({ ...m, _type: 'ta_command_mapping' })))
const newCmdCandidates = investigations.filter(Boolean).flatMap(r => (r.new_command_candidates || []).filter(c => c.already_known === false).map(c => ({ ...c, _type: 'new_duml_command' })))
const allCandidates = [...taMappingCandidates, ...newCmdCandidates]

log(`Investigate phase done. ${taMappingCandidates.length} TA command-ID mapping claims, ${newCmdCandidates.length} new DUML command candidates to verify.`)

phase('Verify')
const verifyDetail = await pipeline(allCandidates, async candidate => {
  const votes = await parallel([1, 2, 3].map(() => () => agent(verifyPrompt(candidate), { phase: 'Verify', schema: VERDICT_SCHEMA })))
  const refuteCount = votes.filter(Boolean).filter(v => v.refuted).length
  const survives = refuteCount < 2
  return { candidate, votes, survives }
})

const verified = verifyDetail.filter(v => v.survives).map(v => v.candidate)

return {
  investigations,
  all_candidates_considered: allCandidates.length,
  verified_count: verified.length,
  verified,
  verify_detail: verifyDetail,
  stats: { items: ALL_ITEMS.length, ta_mapping_claims: taMappingCandidates.length, new_cmd_candidates: newCmdCandidates.length },
}
