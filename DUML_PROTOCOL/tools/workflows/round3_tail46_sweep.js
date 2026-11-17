export const meta = {
  name: 'wm260-tail46-socket-binary-sweep',
  description: 'Investigate the remaining 46 socket-bearing, no-DUML-signal WM260 binaries (round 3 of the binary coverage tracker)',
  phases: [{ title: 'Investigate' }, { title: 'Verify' }],
}

const ALL_ITEMS = [
 {"key":"QAndroidLog","paths":["e2_extracted/system_files/bin/QAndroidLog"]},
 {"key":"adb","paths":["e1e_extracted/system_files/bin/adb","e2_extracted/system_files/bin/adb"]},
 {"key":"debuggerd","paths":["e1e_extracted/system_files/bin/debuggerd","e2_extracted/system_files/bin/debuggerd"]},
 {"key":"dhcpcd","paths":["e1e_extracted/system_files/bin/dhcpcd"]},
 {"key":"dhcpcd-6.8.2","paths":["e2_extracted/system_files/bin/dhcpcd-6.8.2"]},
 {"key":"dumpstate","paths":["e1e_extracted/system_files/bin/dumpstate"]},
 {"key":"fastboot","paths":["e1e_extracted/system_files/bin/fastboot","e2_extracted/system_files/bin/fastboot"]},
 {"key":"fio","paths":["e2_extracted/system_files/bin/fio"]},
 {"key":"hostapd","paths":["e1e_extracted/system_files/bin/hostapd","e2_extracted/system_files/bin/hostapd"]},
 {"key":"hostapd_cli","paths":["e1e_extracted/system_files/bin/hostapd_cli"]},
 {"key":"iozone","paths":["e1e_extracted/system_files/bin/iozone"]},
 {"key":"ip","paths":["e1e_extracted/system_files/bin/ip","e2_extracted/system_files/bin/ip"]},
 {"key":"iperf-2.0.5","paths":["e2_extracted/system_files/bin/iperf-2.0.5"]},
 {"key":"iperf3","paths":["e1e_extracted/system_files/bin/iperf3"]},
 {"key":"iw","paths":["e1e_extracted/system_files/bin/iw","e2_extracted/system_files/bin/iw"]},
 {"key":"libc.so","paths":["e1e_extracted/system_files/lib/libc.so","e2_extracted/system_files/lib64/libc.so"]},
 {"key":"libcryptoopenssl.so","paths":["e2_extracted/system_files/lib64/libcryptoopenssl.so"]},
 {"key":"libcurl.so","paths":["e1e_extracted/system_files/lib/libcurl.so","e2_extracted/system_files/lib64/libcurl.so"]},
 {"key":"libcutils.so","paths":["e1e_extracted/system_files/lib/libcutils.so","e2_extracted/system_files/lib64/libcutils.so"]},
 {"key":"libduml_hal.so","paths":["e1e_extracted/system_files/lib/libduml_hal.so","e2_extracted/system_files/lib64/libduml_hal.so"]},
 {"key":"libhardware_legacy.so","paths":["e1e_extracted/system_files/lib/libhardware_legacy.so","e2_extracted/system_files/lib64/libhardware_legacy.so"]},
 {"key":"libiprouteutil.so","paths":["e1e_extracted/system_files/lib/libiprouteutil.so","e2_extracted/system_files/lib64/libiprouteutil.so"]},
 {"key":"liblte.so","paths":["e2_extracted/system_files/lib64/liblte.so"]},
 {"key":"libmosquitto.so","paths":["e2_extracted/system_files/lib64/libmosquitto.so"]},
 {"key":"libnetdutils.so","paths":["e2_extracted/system_files/lib64/libnetdutils.so"]},
 {"key":"libnetlink.so","paths":["e1e_extracted/system_files/lib/libnetlink.so","e2_extracted/system_files/lib64/libnetlink.so"]},
 {"key":"libnetutils.so","paths":["e1e_extracted/system_files/lib/libnetutils.so","e2_extracted/system_files/lib64/libnetutils.so"]},
 {"key":"libnl.so","paths":["e1e_extracted/system_files/lib/libnl.so","e2_extracted/system_files/lib64/libnl.so"]},
 {"key":"libpcap.so","paths":["e2_extracted/system_files/lib64/libpcap.so"]},
 {"key":"libselinux.so","paths":["e1e_extracted/system_files/lib/libselinux.so","e2_extracted/system_files/lib64/libselinux.so"]},
 {"key":"libsrt.so","paths":["e2_extracted/system_files/lib64/libsrt.so"]},
 {"key":"libsysutils.so","paths":["e1e_extracted/system_files/lib/libsysutils.so","e2_extracted/system_files/lib64/libsysutils.so"]},
 {"key":"libusb.so","paths":["e1e_extracted/system_files/lib/libusb.so","e2_extracted/system_files/lib64/libusb.so"]},
 {"key":"libusbmuxd.so","paths":["e1e_extracted/system_files/lib/libusbmuxd.so","e2_extracted/system_files/lib64/libusbmuxd.so"]},
 {"key":"libwlm.so","paths":["e1e_extracted/system_files/lib/libwlm.so","e2_extracted/system_files/lib64/libwlm.so"]},
 {"key":"libwpa_client.so","paths":["e1e_extracted/system_files/lib/libwpa_client.so"]},
 {"key":"lmkd","paths":["e2_extracted/system_files/bin/lmkd"]},
 {"key":"netd","paths":["e2_extracted/system_files/bin/netd"]},
 {"key":"ping","paths":["e2_extracted/system_files/bin/ping"]},
 {"key":"tcpdump","paths":["e1e_extracted/system_files/xbin/tcpdump","e2_extracted/system_files/bin/tcpdump"]},
 {"key":"tombstoned","paths":["e2_extracted/system_files/bin/tombstoned"]},
 {"key":"toybox","paths":["e1e_extracted/system_files/bin/toybox","e2_extracted/system_files/bin/toybox"]},
 {"key":"traceroute6","paths":["e1e_extracted/system_files/bin/traceroute6"]},
 {"key":"vold","paths":["e1e_extracted/system_files/bin/vold","e2_extracted/system_files/bin/vold"]},
 {"key":"wpa_cli","paths":["e1e_extracted/system_files/bin/wpa_cli","e2_extracted/system_files/bin/wpa_cli"]},
 {"key":"wpa_supplicant","paths":["e1e_extracted/system_files/bin/wpa_supplicant","e2_extracted/system_files/bin/wpa_supplicant"]}
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
  return `You are doing vulnerability-research-style reverse engineering on DJI WM260/Mavic 3 drone firmware, part of a long-running project in nm844/drone-stuff. This is round 3 of a binary-coverage sweep: a prior mechanical triage flagged this binary/library as having its own listening socket but NO detected DUML/DUSS signal via string matching. Most binaries in this round are expected to be stock Android/Linux/BusyBox-class system tooling (adb, hostapd, wpa_supplicant, netd, toybox, iperf3, tcpdump, etc.) that genuinely has nothing to do with DJI's DUML protocol — a clean "ruled out, no DJI-specific logic" verdict is a perfectly good and expected result for most of these. Don't force a finding.

HARD BOUNDARIES: static analysis only (disassembly, ELF/relocation/string parsing) — never execute a binary, never craft/send a packet. Never write working exploit code or a crafted attack packet. Document weaknesses vulnerability-research style only: name the weakness, impact category, confidence.

CHECK FOR THESE FOUR KNOWN DUML command-registration/send mechanisms before ruling out:
1. Direct call to \`duss_event_register_dynamic_command(cmd_set, cmd_id, handler_fn, ...)\` with literal immediates in registers before the call.
2. \`duss_mb_create_route_table\`+\`duss_event_create_client\` — does NOT always mean a real registration; check whether a literal handler function pointer is actually wired up (a route/client can exist with zero command handlers).
3. A relocated (\`R_ARM_RELATIVE\`/\`R_AARCH64_RELATIVE\`) \`.data\` array of 8-byte \`{function_pointer, cmd_word}\` rows — but also check this isn't just a compiler-generated C++/unwinder function-pointer table (same shape, unrelated purpose).
4. \`imss_link_v1_send(cmd_set, cmd_id, ...)\`/\`imss_link_register_v1_callback\` from \`libimss.so\`, with literal immediates in r0/r1 — a private transport outside the main DUSS event bus, found in a gimbal-calibration plugin.

Tooling gotcha: \`readelf -r\` (narrow) truncates relocation symbol names on 32-bit ARM — always use \`readelf -rW\`.

A FEW TARGETS IN THIS BATCH ARE WORTH EXTRA SCRUTINY (don't skip to a quick "stock tool" verdict for these just because of a generic-sounding name): \`libduml_hal.so\` (name literally contains "duml"), \`liblte.so\` (possible counterpart to the already-examined \`dji_lte\` daemon — check if it's linked by anything DUML-relevant), \`libwlm.so\` (possible counterpart to the already-examined \`dji_wlm_slave\`/Wireless Link Manager subsystem). For these three specifically, actually resolve every imported/exported symbol and check DT_NEEDED backlinks (what links this library?) before ruling out — for everything else in this batch a faster pass (check imports for \`duss_*\`, check strings for DUML-ish content, confirm it's upstream/stock code via symbol-table fingerprint) is proportionate.

YOUR SPECIFIC TARGET for this investigation — key "${item.key}":
${item.paths.map(p => `  - ${p.startsWith('/') ? p : BASE + '/' + p}`).join('\n')}

Report using the given schema: a summary, whether you're ruling it out, any \`new_command_candidates\` (only if genuinely found), and any \`architecture_findings\` (vulnerability-research style, only if something is genuinely notable — e.g. a known-vulnerable bundled version, an insecure IPC/temp-file pattern, missing auth on a local socket).`
}

function verifyPrompt(candidate) {
  return `Adversarially try to REFUTE this claim from a DJI drone firmware reverse-engineering project, about a specific DUML command registration. Default to refuted=true unless you can independently re-derive the (cmd_set, cmd_id) pair from the raw ELF bytes yourself. Static analysis only.

CLAIM: ${JSON.stringify(candidate)}

Report {refuted: boolean, reasoning: string}.`
}

phase('Investigate')
const investigations = await pipeline(ALL_ITEMS, item => agent(investigatePrompt(item), { label: `investigate:${item.key}`, phase: 'Investigate', schema: FINDINGS_SCHEMA }))

const newCmdCandidates = investigations.filter(Boolean).flatMap(r => (r.new_command_candidates || []).filter(c => c.already_known === false))
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
