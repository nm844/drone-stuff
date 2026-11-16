# Exhaustive follow-up sweep: 24 previously-unexamined binaries, 10 new commands confirmed

This document continues directly from `15_SECOND_FOLLOWUP_DEEPDIVE_FINDINGS.md`
(Tracks I-P) with a full, from-scratch inventory of **every** binary and
shared library across both firmware images (`e1e_extracted` + `e2_extracted`,
808 files total), triaged down to the subset that had never been
individually examined by any prior pass of this project, and investigated
end to end.

**Methodology:** every investigation was run by an independent agent with
no access to any prior pass's reasoning, briefed on the project's three
known DUML command-registration mechanisms (direct
`duss_event_register_dynamic_command*` calls; the
`duss_mb_create_route_table`+`duss_event_create_client` named-route/client
idiom; a relocated `.data` array of `{function_pointer, cmd_word}` rows).
Every candidate *new* `(cmd_set, cmd_id)` pair was then independently
re-derived from the raw ELF by **three separate adversarial skeptic
passes**, each told to default to **refuted** unless it could reproduce
the claimed mechanism itself from raw bytes — the same adversarial-reverify
protocol used in docs 14 and 15. A candidate is only catalogued below if a
majority of its three reverify passes did **not** refute it. One candidate
(`0x00`/`0x84`) failed that bar and was deliberately left out — see Track R.
No safety-filter interruptions occurred this round (contrast docs 14/15,
each of which had 1-2). `libamt_util.so` (the `e91c9402...`
activation/secure-debug/DJICare TA) was not opened or disassembled in any
track — one investigation (`dji_ftpd`) noted it as an import but did not
touch it, consistent with the project's standing boundary. Static analysis
only; no binary was executed; no packet was crafted or sent; no exploit
code was written.

---

## Track Q — Scope: from 808 binaries to 24 candidates

Before any investigation began, every binary/shared-library file across
both firmware images was mechanically triaged in three stages:

1. **DUML signal filter.** Of 808 total files, 217 reference any
   DUML/DUSS-related symbol or string at all (`duss_event_*`,
   `duss_mb_*`, `cmd_set`, `duml`, etc.); the other 591 do not. Every one
   of those 591 with its own listening network socket was checked by name
   and confirmed to be a generic Linux/Android system utility (`adb`,
   `hostapd`, `dhcpcd`, and similar) rather than a DJI-authored,
   drone-specific component — none held a plausible DUML role.
2. **Existing-documentation cross-check.** Of the 217, 57 were already
   covered by name in some prior pass of this project's documentation.
3. **Real-relocation verification.** Of the remaining 160, a mechanical
   scan for genuine ELF relocations into one of the three known
   registration entry points (using `readelf -rW` — the wide format;
   the narrow/default format was found mid-scan to truncate symbol names
   on 32-bit ARM binaries, producing false negatives, and the scan was
   re-run after switching formats and re-validating against known-positive
   controls) surfaced **17 unique binaries/libraries (23 file-instances
   across both architectures)** with a real registration call site, plus
   **8 secondary candidates** — drone-specific daemons with their own
   socket but no direct registration call, worth a lighter check.

All **24** candidates (16 tier-1, 8 tier-2) were investigated this round.
None remain unexamined from this triage. See Track U for the
full-firmware completeness statement.

---

## Track R — 10 new DUML commands confirmed, 1 investigated-but-not-catalogued

Ten new `(cmd_set, cmd_id)` pairs survived independent, from-raw-bytes
re-derivation by at least 2 of 3 adversarial skeptic passes and are added
to `commands.json`/`ALL_COMMANDS.csv`/the per-cmd_set `.md` files this
pass. `commands.json` moves from 888 to **898** entries; the full-decode
count (157) is unchanged, since all 10 are name/mechanism-confirmed only
(no byte-level payload layout was recovered for any of them).

| New pair | Name | Source binary | Reverify |
|---|---|---|---|
| `0x00`/`0x83` | External Upgrade Request | `upgrade_test` (E1E+E2) | 3/3 not refuted |
| `0x00`/`0x85` | Transfer Complete Notification | `upgrade_test` (E2) | 2/3 not refuted |
| `0x00`/`0x93` | Begin Single Module Upgrade | `upgrade_test` (E2) | 3/3 not refuted |
| `0x00`/`0x94` | Set Upgrade Flag | `upgrade_test` (E2) | 3/3 not refuted |
| `0x02`/`0xEC` | Camera Subscribe Push | `libWorkModeLiveview.so` | 3/3 not refuted |
| `0x09`/`0xA9` | Liveview Pigeon State Heartbeat | `libWorkModeLiveview.so` | 3/3 not refuted |
| `0x09`/`0xAA` | MIPI/HDVT Live-View Parameter Set | `libMipiHandshake.so` | 3/3 not refuted |
| `0x23`/`0x20` (**new cmd_set**) | Register As Smart Owner | `ss_dsp_manager` **and** `libhyperlapse_eis.so` (independently) | 3/3 + 3/3 not refuted |
| `0x23`/`0x21` | Calling For Smart Owner | same two binaries | 3/3 + 3/3 not refuted |
| `0x23`/`0x22` | Finish Working On Smart | same two binaries | 3/3 + 3/3 not refuted |

Full per-command writeups, with handler names, exact call sites, and
confidence/evidence breakdowns, are in `cmdset_00_General.md`,
`cmdset_02_Camera.md`, `cmdset_09_HD_Link.md`, and the new
`cmdset_23_Smart.md`.

**Notable: the same wire command found twice, independently, via two
different mechanisms.** `0x23`'s three commands were found registering
real handlers in both `ss_dsp_manager` (via a private, non-imported
dispatch table structurally mirroring `duss_event_register_dynamic_command`)
and, separately, `libhyperlapse_eis.so` (via a different, HAL-level API,
`ss_hal_mb_set_req_callback`, reached only after joining the generic DUSS
message bus). The authoritative cmd_set name, "Smart", and its three
handler names (`register_as_dspN_owner_callback`,
`calling_for_dspN_callback`, `finish_working_on_dspN_callback`) come from
`libhyperlapse_eis.so`'s own DWARF debug info (`SS_MB_CMD_SET_SMART`
enumerator) — not stripped, unlike most binaries in this sweep. Two
independent binaries landing on the exact same `(cmd_set, cmd_id)` triplet,
via two different registration code paths, is meaningfully stronger
evidence than either alone, and also means this specific trio of wire
commands can genuinely be driven by more than one local process — see
`cmdset_23_Smart.md` for the ownership-arbitration-protocol reading and
two related architecture findings (an unchecked-index heap read/write risk
and a silent-handler-overwrite weakness) found along the way.

**One candidate investigated but deliberately not catalogued: `0x00`/`0x84`
("Negotiate", transfer parameters).** This pair was found with equally
solid mechanism-level evidence (`mov w9, #0x84` immediately before the
shared upgrade-center `send_fn` wrapper, in `upgrade_test`/E2, corroborated
by a log string literally naming `"Send cmd 0x84 to up_center..."`) — but
2 of 3 reverify passes refuted the claim **as originally written**, because
that write-up asserted the finding was present across 4 cited binaries
when independent re-derivation showed it was only ever present in 2 of
them (`upgrade_test` on both architectures; the other two cited files,
`test_upgrade`/`test_upgrade_modified`, are a different, unrelated "test
upgrade service" daemon with a confusingly similar name). This exact
same file-scope overstatement was present in the write-ups for `0x83`,
`0x85`, `0x93`, and `0x94` above too, but did not reach a refuting majority
there. Rather than catalogue `0x84` on a technicality while its underlying
mechanism is almost certainly real, or silently "fix" a reverify result
after the fact, it is recorded here as a credible, well-evidenced, but
formally unconfirmed lead for a future pass — and the file-scope claim is
corrected for the record: **all five `upgrade_test` findings in this track
(`0x83`/`0x84`/`0x85`/`0x93`/`0x94`) are scoped to the `upgrade_test` CLI
binary itself (both E1E/ARM32 and E2/aarch64 builds where evidenced), not
to `test_upgrade`/`test_upgrade_modified`**, which are confirmed-unrelated
daemons that happen to share a confusingly similar name.

---

## Track S — Tier-1 architecture findings (no new commands, but real findings)

Of the 16 tier-1 (strong relocation-signal) candidates, several genuinely
touch DUML registration mechanisms without yielding a new catalogued
command — either because the mechanism was mechanism #2 (named route/client,
no literal cmd_id at that layer) or because the target was ruled out on
closer inspection. These are real, useful architecture findings in their
own right.

| Binary | Finding | Impact category | Confidence |
|---|---|---|---|
| `app_echo` | Registers a named DUSS bus route/client (mechanism #2) toward the "App" domain but never registers a handler for any specific `(cmd_set, cmd_id)` — a diagnostic send-only tool, not a command handler. All bus activity (including its one outbound send, carrying a hardcoded, low-confidence-only tag that coincidentally matches already-catalogued `0x00`/`0x02`) is gated behind `secure_debug=1` in `/proc/cmdline`. | access-control | high |
| `ss_dsp_manager` (E2/aarch64 build) | The aarch64 build of this identically-named binary performs **zero** DUML registration of any kind, despite 20 relevant symbol names being present — architecturally a different, lower-level component from its ARM32/E1E namesake, which is the one that yields Track R's `0x23` commands. | architecture_note | high |
| `test_dji_blackbox` | **Ruled out** as a command handler, but confirms real internal `duss_mb` addressing conventions (service/role name strings, numeric target_type/target_index examples) otherwise undocumented, and is a QA/test harness capable of writing raw blackbox records under operator-chosen identity, shipped as a standalone production binary. | information-disclosure / debug-surface-in-production | high |
| `libdcam_observer_dsh.so` | **Ruled out.** Uses the mechanism-#2 idiom purely for internal, non-DUML camera-frame-buffer-sharing IPC with a "remote observer" process — confirms the idiom is reused for non-DUML purposes elsewhere in this firmware, a useful disambiguation for future scans. | architecture_note | high |
| `libWorkModeLiveview.so` | Beyond the two confirmed commands in Track R: does not itself create or authenticate the `duss_event_client` it registers on — it only accepts a pre-built client handle via constructor parameters, binding real commands onto whatever identity the caller already established. | trust-boundary note | high |
| `libhyperlapse_eis.so` | Beyond Track R's 3 commands: joins the generic bus via mechanism #2 as domain `ss_dsp_manager`/role `ss_dsp_manager_service`, and separately implements the 4th registration-mechanism pattern (`ss_hal_mb_set_req_callback`) documented in `cmdset_23_Smart.md`. | architecture_note (new mechanism pattern) | high |
| `DDSClientv1` | DJI's own Fast-DDS/"DUML v1 transaction" load-test harness, confirmed by an embedded compile-time source path (not inference). `duss_trans_send_by_v1` is an opaque passthrough that never parses/validates any cmd_set/cmd_id bytes a caller's payload might contain. `CalCrc16`/`CalCrc8`/`sendto` are imported but dead (zero call sites) in this build — this build's DUML-v1 path never computes a wire CRC or transmits raw. | architecture_note | high |
| `duml_googletest` | DJI's own statically-linked GoogleTest suite for the DUML "middle layer." Its two real `duss_event_register_dynamic_command` call sites both register the already-catalogued `0x00`/`0x02` — unit-test code, not a new finding, but confirms this project's registration-detection methodology against known-good ground truth. Also confirms a long, structurally mechanism-3-*shaped* relocated array in this binary is actually GoogleTest's own internal test-case vtable machinery, not a command table — a useful false-positive-avoidance note for future scans. | methodology confirmation | high |
| `stress_test_mb_family` | **Ruled out** as DUML handlers (both are internal message-bus benchmark/stress harnesses). Confirms the internal `duss_mb` "message bus" routing layer uses its own, architecturally distinct 16-bit host/route-address namespace, separate from wire-level DUML `(cmd_set, cmd_id)` addressing — these must not be conflated. Also: debug/benchmark executables with embedded internal test-tree source paths are shipped as regular, attacker-invokable binaries in production `system_files/bin`. | namespace-disambiguation / debug-tooling-in-production | high / medium |
| `libdcam_imu_handle_link_node.so` | **Ruled out** as a DUML handler — a camera-pipeline plugin node using mechanism #2 for an internal IMU-data pub/sub topic, not wire-protocol registration. Flags two taxonomy-caution coincidences: a 32-bit internal event ID and a log-tag constant that numerically happen to look like DUML values but aren't. Crash-only error handling (`exit(1)`) on malformed internal messages. | taxonomy-caution / availability | medium / low |
| `libdcam_cs_duss_proxy.so` | **Not ruled out** — genuinely registers a dedicated mechanism-#2 DUSS route/client for a high-throughput file-download (photo/video offload) channel, separate from the generic Camera command channel, and exports its own `(cmd_set, cmd_id, handler)` array-driven override hook — a hybrid of mechanisms #1 and #3 not previously catalogued. A locally-defined handler on the camera command-dispatch surface copies a length-clamped, host/wire-supplied buffer into a debug-command interpreter with no visible authorization check in the immediate call path. | duml-command-registration-confirmed / auth-gap-debug-surface | high / medium |
| `libdcam_event_client_pool.so` | **Not ruled out** — confirmed generic, reusable middleware wrapping both mechanism #2 and the `_table_with_user_data` variant of mechanism #1, but forwards (doesn't itself hold) the concrete `(cmd_set, cmd_id)` literals its 3 real-world consumers (`libdcam_camdev.so`, `libdcam_cs_cbb.so`, `libdcam_topmode_comm.so` — outside this pass's scope) supply. No ownership/allow-list validation on the registered command word before forwarding it, though registration/unregistration pointer-matching and mutex-guarded list integrity are both genuinely present (positive hygiene). | missing-validation / positive-hygiene | medium / high |
| `libdcam_vtx_sm.so` | **Ruled out** — the mechanical scan's tier-1 flag was a real but false-positive-for-DUML hit: this binary's mechanism-#2 calls are scoped to an internal camera-service FSM lifecycle, and its relocated `.data` arrays are FSM state-transition tables, not `{function_pointer, cmd_word}` command tables. The message-bus client it creates has no visible sender authentication, so any local process able to address its named routes can drive internal video-transmitter state transitions. A coincidental numeric match (`0x0900`) to cmd_set `0x09` convention is flagged as unresolved, not claimed. | false_positive_disambiguation / trust_boundary | high / medium |
| `librcam.so` | **Not ruled out** — the camera daemon's shared library registers at least two named DUSS clients via mechanism #2 under route table `camera_service`, but no literal numeric `(cmd_set, cmd_id)` binding was found for them directly in this library within this pass's scope (the ~206-entry Camera command jump table it would need lives in one of 15 other linked libraries, not traced here). A separate, internal, non-DUML lens-mount protocol (`BLCOMM`, its own CHANID/CMDID numbering over I2C) exists alongside the DUML surface and must not be conflated with it. | command-registration-architecture / protocol-separation | high / medium |
| `upgrade_test_family` | Beyond Track R's new commands: confirms a real, working client implementation of the already-catalogued `0x00`/`0x41` and `0x00`/`0x4f`; the `upgrade_test`↔"upgrade center" channel is addressed purely by bus client identity, which the CLI itself lets the invoking user override at runtime with no additional token visible in this binary before issuing firmware-update-affecting commands; and every outbound upgrade-center message's envelope "type" field is a constant `0x40` regardless of cmd_id — the real discriminator is entirely in the payload, not the envelope. | local-trust-boundary / protocol-detail | medium / high |

---

## Track T — Tier-2 findings (secondary candidates, all ruled out — several with real, independent security notes)

All 8 tier-2 targets (drone-specific daemons with a listening socket but
no direct DUML registration call) were confirmed unrelated to the DUML
command surface. Several yielded real, independent architecture/security
findings worth recording even though none touches DUML:

| Binary | Finding | Impact category | Confidence |
|---|---|---|---|
| `dji_ftpd` | A standalone cleartext FTP daemon (USER/PASS/PASV/RETR/STOR, no DUML imports at all). Links `libamt_util.so`/`libteec.so` (OP-TEE TEE Client — import table only inspected, not opened/disassembled, per this project's standing boundary) for session/log-key material. Shells out via `popen()`/`system()` to check `androidboot.secure_debug=1` on the kernel command line; the exact branch logic was not traced (tier-2 bounded effort), so this is flagged as unconfirmed, not claimed as an exploit path. | config/attack-surface | medium |
| `bsa_server` | The stock third-party Broadcom BSA Bluetooth-stack daemon — no DJI/DUML code at all (imports only `libc`/`libdl`). Its own internal Bluetooth IPC command namespace (hundreds of `BSA_*_MSGID_*` IDs) must not be conflated with DUML's. Legacy pre-SSP (plain PIN-code) Bluetooth pairing coexists with modern SSP/passkey pairing, meaning the stack can fall back to weaker pairing depending on runtime negotiation. The loopback BSA control socket a prior mechanical scan flagged has no authentication beyond kernel peer-address info (never read by the code). | crypto/pairing-weakness (class-level) / access-control | low |
| `cam_dt_cmdline` | A local camera-debug CLI speaking its own private, unauthenticated plaintext protocol to a `camera_dbg_server` peer, with its command vocabulary itself loadable from an XML file on `/data` — entirely separate from DUML. | local-trust-boundary / unauthenticated-debug-interface (non-DUML) | medium |
| `wms_ipc_dsock.so` | Pure local-IPC transport glue (`AF_UNIX` datagram sockets) connecting several internal daemons (Bluetooth, Wi-Fi, camera) — not a DUML participant. Its debug-log rotation uses `system("mv %s %s")` against fixed `/tmp` paths opened with a plain `fopen()` — a classic insecure-predictable-tempfile pattern (symlink/TOCTOU exposure for any local attacker able to pre-create those paths). | local-tmp-file-handling | medium |
| `libmt_client.so` | DJI's LTE/4G cloud livestream relay client, not a DUML participant. **TLS hostname verification is explicitly disabled** (`CURLOPT_SSL_VERIFYHOST=0`) on the HTTPS channel used to fetch cloud livestream auth tokens, while peer certificate-chain verification stays on (`CURLOPT_SSL_VERIFYPEER=1`) — a real MITM weakness in this one specific channel (not the whole TLS stack). The per-device mTLS client key/cert used to authenticate the aircraft to the cloud relay are read from fixed, predictable filesystem paths, and a copy is staged in world-writable `/tmp` at runtime. | transport/MITM weakness / key-material-exposure | high / medium |
| `libsrv_um.so` | Stock Imagination Technologies PowerVR GPU driver client library — confirmed entirely unrelated to DJI/DUML code (no `duss_*` import anywhere; symbol table is 100% PowerVR `PVRSRV*`/`RGX*` GPU-driver API). No findings beyond scope confirmation. | — | high |
| `libdcamecg_process.so` | A camera-subsystem self-diagnostic ("CAM_ECG") helper, not DUML. Its status-reporting `AF_UNIX` socket has no sender authentication; its bind path is `remove()`'d then `bind()`'d with no ownership/type check (a classic unlink-then-create local race window); and a kernel character device (`/dev/cam_ecg`) accepts raw, unvalidated 176-byte writes directly from this userspace code with no framing/sanity checks. | local-ipc-auth-gap / local-race-toctou / kernel-attack-surface | medium / low / low |
| `libdcam_base.so` | A camera-subsystem base/utility library (buffers, FSM helpers, event framework) — confirmed zero DUML registration imports or lookups on either architecture. Its `CamDebugTool` local diagnostic socket parses ASCII commands and can trigger XML export to a caller-influenced filename. Exported file-helper functions (`cam_cp`/`cam_rm`/`cam_mv`/`cam_mkdir`) are internally tagged `CAM_SYS_CALL` and the library imports `system@LIBC`, suggesting (not confirmed — call graph not traced) these may shell out rather than use direct syscalls, a shape that becomes a command-injection primitive if ever fed unsanitized input. | local debug interface exposure / potential command-injection-shaped primitive (unconfirmed) | medium / low |

---

## Track U — Completeness statement

Of the full **808** binaries/shared-libraries across both firmware images:

- **57** were already individually documented before this pass.
- **591** carry no DUML/DUSS signal of any kind and were confirmed to be
  generic Linux/Android system tooling (every one with its own socket was
  individually name-checked) — ruled out on signal absence.
- **160** carried DUML-adjacent strings/symbols but no confirmed real
  registration relocation; of those, **24** (this pass's 16 tier-1 + 8
  tier-2 candidates) were individually investigated to a disassembly
  level this round, and the other **136** remain triaged-but-not-escalated
  on weak/ambiguous signal (same bounded-effort status as doc 15's
  Track O low-priority re-sweep covered for a different 20-binary subset;
  not claimed as individually ruled out).

Every one of this round's 24 candidates now has a documented disposition:
10 new commands catalogued (Track R), 1 credible-but-unconfirmed lead
recorded rather than catalogued (`0x00`/`0x84`, Track R), and 23 confirmed
either as real-but-non-command DUML/DUSS participants (Track S) or as
fully unrelated to the DUML surface (Track S/T, ruled out). No
investigation this round was interrupted by a safety-filter false
positive, and none touched `libamt_util.so` beyond noting its presence as
an import. The 136 lower-signal binaries noted above remain a bounded,
honestly-flagged gap for any future pass — not claimed as covered by this
one.
