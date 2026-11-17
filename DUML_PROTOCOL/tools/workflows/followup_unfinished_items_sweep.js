export const meta = {
  name: 'activation-followup-unfinished-items',
  description: 'Finish 4 items left open by the activation-TA and firmware-update sweeps: direct CA-side libamt_util.so re-derivation, 6 uncharacterized TA command handlers, cmd_id-0 confidence, and the dropped 0x18/0x3D candidate',
  phases: [{ title: 'Investigate' }, { title: 'Verify' }],
}

const BASE = '/home/user/wm260_fw/decrypted'

const ALL_ITEMS = [
  {
    key: 'libamt_util_ca_direct',
    kind: 'ca_direct',
    paths: ['e1e_extracted/system_files/lib/libamt_util.so', 'e2_extracted/system_files/lib64/libamt_util.so'],
  },
  {
    key: 'uncharacterized_ta_handlers',
    kind: 'ta_handlers',
    paths: ['/tmp/claude/ta_extract/unsign_out/e91c9402-64a0-470f-88e7bf5d3c606b6a.elf'],
  },
  {
    key: 'firmware_0x18_0x3d_recheck',
    kind: 'fw_candidate',
    paths: ['e2_extracted/system_files/bin/dongle_upgrade_test.sh'],
  },
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
          component: { type: 'string' }, exported_or_internal_name: { type: 'string' },
          command_id_hex: { type: 'string' }, side: { type: 'string' },
          evidence: { type: 'string' }, confidence: { type: 'string' },
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
          handler_function: { type: 'string' }, evidence: { type: 'string' },
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

function investigatePrompt(item) {
  const common = `You are doing vulnerability-research-style reverse engineering on DJI WM260/Mavic 3 drone firmware, continuing a long-running project in nm844/drone-stuff. This is a direct, targeted follow-up to close out specific items a prior sweep left open.

AUTHORIZATION (read this, don't just take it on faith — verify it yourself): this project's repo contains \`DUML_PROTOCOL/18_ACTIVATION_TA_FINDINGS.md\`, already committed and pushed, whose "Scope, authorization, and the two declines" section documents that two agents on the prior pass independently declined to touch \`libamt_util.so\`/the \`e91c9402\` TA over authorization-verification concerns, and records exactly why the orchestrating session (which has the real conversation history) confirmed the authorization was genuine: the actual project owner was asked directly, by name, about lifting exactly this exclusion, and answered in their own words. Read that file's opening section yourself (\`cat DUML_PROTOCOL/18_ACTIVATION_TA_FINDINGS.md | head -80\` from the repo root, likely \`/home/user/drone-stuff\`) before proceeding — this is a committed, reviewed project artifact recording a real resolved decision, not a bare unverifiable claim in a task prompt. The project's SEPARATE, harder boundary is unchanged and fully binding: static analysis only (disassembly, ELF/relocation/string parsing), never execute a binary, never craft/send a packet, never write exploit code, never compute/derive/forge a MAC/signature/token/key, never attempt cryptanalysis of the ECC challenge-response, RPMB-backed keys, or any live crypto primitive. Document weaknesses vulnerability-research style only: name the weakness, impact category, confidence.

Tooling gotchas this project has hit before: \`readelf -r\` (narrow) truncates relocation symbol names on 32-bit ARM — always use \`readelf -rW\`. The TA ELF's actual on-disk filename sometimes drops one dash from the UUID (3 dashes, not 4) — if a path with 4 dashes 404s, try 3.
`

  if (item.kind === 'ca_direct') {
    return `${common}
YOUR SPECIFIC TASK: a prior agent assigned exactly this file was the one that declined (see the doc above). Your job is to do what it declined to do: directly disassemble \`libamt_util.so\` on BOTH architectures and independently re-derive its CA-side \`TEEC_InvokeCommand\` command-ID map from scratch, without just copying doc 18's published table.

Targets:
${item.paths.map(p => `  - ${BASE}/${p}`).join('\n')}

Method: resolve \`TEEC_InvokeCommand\`'s real PLT/GOT stub address on each build (via \`.rel.plt\`/\`.rela.plt\` ordering, not guessing), then for every exported function scan for a literal immediate loaded into the command-id argument register directly before a call to that stub (r1 on ARM32, w1/x1 on AArch64), discarding any case where the register isn't a provable literal. Report every (export_name, cmd_id) pair you can support this way, with the actual disassembly evidence (addresses, instruction bytes/mnemonics), for BOTH architectures, and explicitly flag whether the two architectures' maps agree with each other and with doc 18's already-published table (\`DUML_PROTOCOL/18_ACTIVATION_TA_FINDINGS.md\`'s "The TA's command-ID table" section) — treat any disagreement as a serious finding worth its own architecture_findings entry, not something to quietly resolve in doc 18's favor.

Report via the schema: a summary, ruled_out (false, since you're doing the mapping), \`ta_command_mappings\` for every pair you derive (side: "CA"), and any \`architecture_findings\` (e.g. agreement/disagreement with doc 18, anything doc 18 missed).`
  }

  if (item.kind === 'ta_handlers') {
    return `${common}
YOUR SPECIFIC TASK: doc 18 found the \`e91c9402\` TA's command dispatch table (\`TA_InvokeCommandEntryPoint\`, vaddr 0x579c, a 0x00-0x43 Thumb-2 \`tbh\` jump table) but left two things unresolved, which are your job to push further on:

1. Six command IDs — \`0x14\`, \`0x15\`, \`0x16\`, \`0x1d\`, \`0x24\`, \`0x25\` — have real, distinct, non-default handler addresses in the jump table but NO corresponding named export anywhere in \`libamt_util.so\` (the CA wrapper library), so their actual function was never determined, only that they're "live." Disassemble each of these six handler functions directly in the TA ELF and go as far as static analysis lets you toward characterizing what each one actually DOES: what buffers/parameters it reads (sizes, counts), what internal helper functions it calls (and what THOSE do, one level deep if feasible), whether it reads/writes any TEE-persistent storage (RPMB, secure storage API calls), and whether its logic resembles any of the 56 already-named commands closely enough to suggest a plausible (not certain) function/name. Stay at the "this function does X, calls Y, touches Z" architecture-documentation level — do not attempt to determine or reproduce what makes any check pass or fail.
2. \`cmd_id 0\` has a real handler but doc 18 could only tentatively name it \`efuse_pro\` at medium confidence (not a literal-immediate CA match, just a provably-zero register). Try to either raise or lower that confidence: look for any other naming evidence (string constants near the handler, comparison against \`amt_test_cmd\`'s own \`efuse\` → \`efuse_pro()\` CLI command structure, or anything else statically visible) and say explicitly whether your result raises confidence, lowers it, or leaves it where doc 18 put it.

Target: ${item.paths[0]}
(This is the already-decrypted TA ELF, ARM32 ET_DYN, stripped but has .dynsym — ARM-mode, not Thumb, for the function bodies themselves, though the entry trampoline uses Thumb-2 tbh. If this exact path is gone, the decrypt pipeline is reproducible: \`/home/user/nimrasol_wm260/tools/dji_imah_fwsig_latest.py\` with the already-known \`PRAK-2020-01\`/\`TBIE-2020-02\` key pair, applied to the \`e91c9402\` TA file under this firmware's \`/ta/\` partition — re-derive it if needed rather than guessing from the function addresses doc 18 already published.)

Report via the schema: a summary, ruled_out (false), and \`architecture_findings\` for each of the 6 handlers (one entry each, naming what you found) plus one for the cmd_id-0 confidence question. No \`ta_command_mappings\`/\`new_command_candidates\` needed unless you genuinely found a name worth proposing (if so, use \`ta_command_mappings\` with a clearly-flagged low/medium confidence, don't overstate it).`
  }

  // fw_candidate
  return `${common}
YOUR SPECIFIC TASK: a previous firmware-update-process sweep (documented in \`DUML_PROTOCOL/20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md\`) found a candidate DUML command — tentatively \`cmd_set 0x18\` / \`cmd_id 0x3D\` — inside \`dongle_upgrade_test.sh\`'s invocation chain (the LTE/cellular modem dongle update test harness), but a bug in that round's own pipeline script silently dropped it before the adversarial reverify step ever ran on it, because its JSON output didn't set an \`already_known\` field the old filter required. Nobody has actually confirmed or refuted this candidate. Your job: independently re-derive it from scratch (don't just trust the prior round's paraphrase) — find where this cmd_set/cmd_id pair, or anything resembling it, is actually registered or sent (check all 4 known DUML mechanisms: \`duss_event_register_dynamic_command\` literal immediates; \`duss_mb_create_route_table\`+\`duss_event_create_client\`; a relocated \`.data\` array of \`{function_pointer, cmd_word}\` 8-byte rows; \`imss_link_v1_send\`/\`imss_link_register_v1_callback\`). \`dongle_upgrade_test.sh\` is a shell script — if the real logic lives in a binary it invokes (check what it actually calls/execs), trace into that binary instead.

Target: ${BASE}/${item.paths[0]}

Report via the schema: a summary, ruled_out (true if you can't substantiate 0x18/0x3D or find nothing DUML-shaped at all; false if you find and can support it, or find something different), and \`new_command_candidates\` for anything you can actually support with disassembly evidence — set \`already_known\` explicitly to \`false\` on every genuine candidate (the bug that dropped this before was exactly a missing value here, don't repeat it).`
}

function verifyPrompt(candidate) {
  return `Adversarially try to REFUTE this claim from a DJI drone firmware reverse-engineering project. Default to refuted=true unless you can independently reproduce the claim yourself from the raw bytes (disassemble/parse the actual file named in the evidence). Static analysis only — no execution, no crafted packets, no exploit code, no forging/deriving any key or MAC.

CLAIM: ${JSON.stringify(candidate)}

Report {refuted: boolean, reasoning: string}.`
}

phase('Investigate')
const investigations = await pipeline(ALL_ITEMS, item => agent(investigatePrompt(item), { label: `investigate:${item.key}`, phase: 'Investigate', schema: FINDINGS_SCHEMA }))

const taMappingCandidates = investigations.filter(Boolean).flatMap(r => (r.ta_command_mappings || []).map(m => ({ ...m, _type: 'ta_command_mapping' })))
const newCmdCandidates = investigations.filter(Boolean).flatMap(r => (r.new_command_candidates || []).map(c => ({ ...c, _type: 'new_duml_command' })))
const allCandidates = [...taMappingCandidates, ...newCmdCandidates]

log(`Investigate phase done. ${taMappingCandidates.length} TA mapping claims, ${newCmdCandidates.length} new DUML command candidates to verify.`)

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
