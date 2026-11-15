# The exhaustive binary sweep — triage + deep-dive of every remaining E1E/E2/vendor binary and library

This document completes the "keep going deeper until all libraries and
binaries are examined" directive: a 39-agent background Workflow that
systematically triaged every previously-unexamined executable and shared
library across the E1E (main aircraft Linux computer) and E2
(camera/gimbal computer) system images, plus the E1E vendor partition's
`/ta/` OP-TEE Trusted Applications, then deep-dived the ones triage flagged
as high-value. Everything here is **static analysis only** — disassembly
(capstone/pyelftools/llvm-objdump), `.gnu_debugdata` extraction,
string/import enumeration, and byte-level container-format inspection. No
binary was executed, no network traffic was sent or captured, and no
exploit code, crafted packet, or attack recipe was written at any point —
consistent with this project's standing boundary (see
`04_WM260_DAEMON_FINDINGS.md`, `05_DJI_SEC_FINDINGS.md`,
`06_NFZ_DATABASE_FINDINGS.md`, `09_DJI_AUTOTEST_EXPLOITABILITY_DEEPDIVE.md`
for the same stated boundary applied consistently).

**Methodology, in two passes:**

1. **Triage** (light pass — `file`/`readelf`/`nm -D`/`strings`, no
   disassembly): every binary/library not already covered by
   `01_BINARY_ANALYSIS_FINDINGS.md` through `11_DJI_NN_SERVER_FINDINGS.md`
   was classified by architecture, strip/debugdata status, whether it
   imports the `duss_event_register_dynamic_command` family or other
   DUML-bus symbols, notable strings, a purpose guess, and a priority
   (high/medium/low) with a stated reason. 65 binaries/libraries were
   triaged this way, across 9 batches (7 on the E1E image, 2 on the E2
   image).
2. **Deep-dive** (full disassembly pass, one binary per agent): the 28
   highest-priority triage results were escalated to a full
   capstone/pyelftools (or llvm-objdump) disassembly pass, confirming or
   correcting the triage's purpose guess with real control-flow evidence,
   enumerating actual DUML command registrations where present, and
   reporting concrete findings tagged weakness/impact-category/confidence.

Of those 28 deep-dives: **2** (`dji_flight`, `dji_navigation`) were already
covered by `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` from an earlier
pass — this pass's new detail is folded into that document as short
addenda rather than repeated here (see "Addenda to other documents"
below). **2** (`dji_cht`, `dji_nn_server`) were already written up as their
own standalone documents (`10_DJI_CHT_CAMHAL_TEST_FINDINGS.md`,
`11_DJI_NN_SERVER_FINDINGS.md`) directly from this same workflow — both
were sanity-checked against the raw deep-dive data for this report and
found to already match it closely (no corrections needed; see the note at
the end of this section). The remaining **24** get full sections below.

Separately, this workflow also re-confirmed `/adsb/adsb_soc.img` (the
ADS-B receiver SoC/MCU firmware image already documented in
`07_ADSB_SOC_FINDINGS.md`) and opened the four `/ta/*.ta` OP-TEE Trusted
Applications for the first time. The ADS-B re-confirmation found nothing
genuinely new — every structural detail it reported (the `TBLD`/`BLLK`/
`BLFA` sub-block tags, the embedded `2022-03-04` build date, the
`"bootloader"` component name) is already present in `07_ADSB_SOC_
FINDINGS.md`, so no addendum was needed there. The OP-TEE TA investigation
*is* genuinely new and architecturally significant enough to warrant its
own document: see `13_OPTEE_TA_FINDINGS.md`.

## Sanity-check of `10_DJI_CHT_CAMHAL_TEST_FINDINGS.md` and `11_DJI_NN_SERVER_FINDINGS.md`

Both documents' highest-confidence claims were checked against this
workflow's raw triage/deep-dive data for `dji_cht` and `dji_nn_server`
(the same workflow produced both the documents and the raw data). In both
cases the documents' content matches the raw deep-dive findings closely —
same confirmed-absent `duss_event_register_dynamic_command` family, same
113-slot/7-slot dispatch tables and vtable recovery, same bounded
stack-buffer-overflow and out-of-bounds-index findings with the same
confidence levels. **No accuracy problems were found in either document**;
no edits were made to them.

---

# Part 1 — Consolidated triage table (all 65 binaries/libraries)

"Disposition" says what happened next: a section number below, a pointer
to an existing document, or "not escalated" (triaged only, no deep dive —
the one-line purpose/priority here is the full extent of this project's
analysis of that file). No binary name repeats across the E1E and E2
batches below — the two images were triaged independently, and no binary
in this sweep's 65 entries happens to share an exact name across both
images (the handful of libraries confirmed present as separate per-arch
builds on *both* images — `libdji_fw_verify_util.so`, `libduml_payload.so`,
`libduml_rpc.so` — were only triaged once, on E1E, and the deep-dive agents
for those three independently checked and confirmed the E2 aarch64 build
carries the same logic; this is noted per-binary below rather than
double-counted as a separate triage row).

### E1E image — binaries (`system_files/bin/`)

| Binary | Purpose (one line) | Priority | Disposition |
|---|---|---|---|
| `dji_flight` | NFZ/geofence verification + WP2 waypoint-mission + ADS-B relay for the flight controller | high | Deep-dived → already in `08_...FINDINGS.md`; addendum below |
| `dji_navigation` | Vision/navigation perception computer: obstacle avoidance, ActiveTrack, NFZ-height-limit backstop | high | Deep-dived → already in `08_...FINDINGS.md`; addendum below |
| `dji_autotest` | Factory/engineering self-test + camera-calibration harness, TCP SDK networking | medium | Not escalated this pass (already fully covered by `08_...FINDINGS.md` / `09_...DEEPDIVE.md`) |
| `dji_blackbox` | Flight-log blackbox collector/exporter, multi-subsystem | high | Deep-dived → §1 below |
| `dji_bb_spliter` | Offline `.bb`-log-file splitter CLI, not a live bus participant | low | Not escalated |
| `dji_mb_ctrl` | General-purpose CLI DUML message-bus injector/debug tool | high | Deep-dived → §2 below |
| `dji_mb_parser` | Offline DUML dump-log decoder/analyzer, not a live bus participant | low | Not escalated |
| `dji_media_server` | Camera/media streaming control daemon (resolution/codec/live-streaming) | medium | Not escalated |
| `dji_ml` | DSP-accelerated person/vehicle detection + tracking for obstacle avoidance | high | Deep-dived → §3 below |
| `dji_ml_gtest` | gtest harness for `dji_ml`'s vision API | medium | Not escalated |
| `dji_network` | Wi-Fi/SDR link-management daemon, flight-regulation metadata persistence | high | Deep-dived → §4 below |
| `dji_sdrs_agent` | SDR-link log/diagnostic data agent (USB bulk/UART channels) | high | Deep-dived → §5 below |
| `dji_sw_uav` | Sliding-window reliability monitor for the OSD/stream/download link | low | Not escalated |
| `dji_vtwo_sdk` | Thin wrapper service around `libv2_sdk.so`'s file-pull protocol | medium | Not escalated |
| `dji_wlm` | Wireless Link Manager: device-identity ownership, multi-link fusion/forwarding | high | Deep-dived → §6 below |
| `dji_upgrade` | Firmware-upgrade orchestration daemon | high | Deep-dived → §7 below |
| `dji_fw_load` | Thin CLI wrapper around `libfw_util.so`'s chunk-extract function | low | Not escalated |
| `dji_fw_verify` | Thin CLI wrapper around `libfw_util.so`'s ION-backed verify function | high | Deep-dived → §8 below |
| `dji_verify` | Self-contained firmware-image auth/decrypt CLI (keymgr, enc/scramble keys) | high | Deep-dived → §9 below |
| `dji_kmsg` | Kernel-log (`/proc/kmsg`) capture/rotation daemon | low | Not escalated |
| `dji_top` | Generic `ps`/`top`-style process monitor | low | Not escalated |
| `dji_ftpd` | Network FTP server exposing flight-critical subsystem directory aliases | high | Deep-dived → §10 below |

### E1E image — binaries (`system_files/bin/`, batch 5)

| Binary | Purpose (one line) | Priority | Disposition |
|---|---|---|---|
| `duss_shell` | Interactive CLI DUML bus client/raw-injector | high | Deep-dived → §11 below |
| `check_secure_debug` | CLI that queries `libamt_util.so`'s `sec_debug_state()` | high | Deep-dived → §12 below |
| `rtos_debug` | CLI wrapper (`test_rtos`) around `librtos.so` reboot/recover/ramdump of the flight-control RTOS core | medium | Not escalated (recommend `librtos.so` itself for a future pass) |
| `tee-supplicant` | Standard, unmodified upstream OP-TEE normal-world supplicant (RPMB proxy, TA loader) | medium | Not escalated — well-known upstream code, no DJI-specific logic |
| `xtest` | 0-byte placeholder (upstream OP-TEE compliance-test harness, emptied before shipping) | low | Not escalated |
| `tee_helloworld` | 0-byte placeholder (upstream OP-TEE SDK sample) | low | Not escalated |

### E1E image — libraries (`system_files/lib/`, batch 6)

| Library | Purpose (one line) | Priority | Disposition |
|---|---|---|---|
| `libdji_crypto_lib.so` | Vendored mbedTLS build (526 of 549 exports are literal `mbedtls_*` functions) | low | Not escalated |
| `libdji_fw_verify_util.so` | ION-shared-memory client marshalling firmware bytes to the TEE for verification | high | Deep-dived → §13 below (also checked on E2) |
| `libdji_sec_ds_whitelist_upgrade.so` | Firmware-version anti-downgrade whitelist gate | high | Deep-dived → §14 below |
| `libmod_dji.so` | Misleadingly-named: ~3 MB of static IMX378 camera-ISP calibration tables, no DUML/security logic | low | Not escalated |
| `libduml_rpc.so` | Inter-Chip-Communication (ICC) RPC/transport layer carrying DUML across a chip boundary | high | Deep-dived → §15 below (also checked on E2) |
| `libduml_payload.so` | DUML device-negotiation wire-format parser | high | Deep-dived → §16 below (also checked on E2) |

### E1E image — libraries (`system_files/lib/`, batch 7)

| Library | Purpose (one line) | Priority | Disposition |
|---|---|---|---|
| `libduml_orte.so` | Standalone C implementation of ORTE/DDS-RTPS pub-sub middleware (older bus transport) | medium | Not escalated |
| `libduml_osal.so` | Core DUSS OS-abstraction layer (threads, mutexes, timers, cgroup limits) | low | Not escalated |
| `libduml_dn.so` | Device-node client library: registers a device, sends/parses `HOST: cmd` bus messages | high | Deep-dived → §17 below |
| `libduml_f2d.so` | Thin wrapper around a vendor 2D-blit/scale hardware accelerator | low | Not escalated |
| `libduml_fb.so` | Framebuffer/display-controller abstraction | low | Not escalated |
| `libduml_ffremux.so` | FFmpeg-based remux/dejitter library for flight-video recording | low | Not escalated |
| `libduml_fastrtps.so` | Vendored eProsima Fast-RTPS/Fast-DDS — likely the primary modern bus transport | medium | Not escalated (recommend for a future pass: real network-facing RTPS parser) |

### E1E image — libraries (`system_files/lib/`, batch 8)

| Library | Purpose (one line) | Priority | Disposition |
|---|---|---|---|
| `libduml_async_remux.so` | Dummy/stub mux-demux implementation — every exported function just logs "not implemented" | low | Not escalated |
| `libduml_dev_hb.so` | Per-target DUML heartbeat/liveness scheduling + timeout watchdog | high | Deep-dived → §18 below |
| `libduml_shineIO.so` | "Shine" internal SSD/flash storage I/O engine (async disk writer, NVMe passthrough) | medium | Not escalated |
| `libduml_vcodec.so` | DUML HAL video-codec plugin over Imagination VXE codec IP | low | Not escalated |
| `libduml_watermark.so` | On-video watermark/overlay compositor (FreeType text + static picture) | low | Not escalated |
| `libDjiMediaPlayerServer.so` | Media playback: Binder service + DUML route-table bridge to local OMX playback | high | Deep-dived → §19 below |
| `lib_hal_dji_gdc.so` | Low-level HAL driver wrapper for the lens geometric-distortion-correction accelerator | low | Not escalated |
| `libdcam_dewarp_dji_gdc.so` | Camera-pipeline plugin wiring the GDC dewarp HAL into the E1E post-processing framework | low | Not escalated |

### E2 image — binaries (`system_files/bin/`)

| Binary | Purpose (one line) | Priority | Disposition |
|---|---|---|---|
| `dji_cht` | Camera HAL manual/interactive engineering test harness (Eagle2) | high | Deep-dived → already in `10_DJI_CHT_CAMHAL_TEST_FINDINGS.md` |
| `dji_cst` | Camera Seal Test (`cam_seal`) engineering regression-test harness | high | Deep-dived → §20 below |
| `dji_fcali_test` | Factory calibration (`lib_fcali`) blob loader test tool | low | Not escalated |
| `dji_fnm_test` | File Name Manager (DCF2) indexing/naming test tool | low | Not escalated |
| `dji_hms` | Health Management System daemon (error/health-code collector, history, OSD relay) | high | Deep-dived → §21 below |
| `dji_http_server` | Embedded lighttpd-derived HTTP server for photo/video/thumbnail retrieval | high | Deep-dived → §22 below |
| `dji_lte` | 4G/LTE cellular-dongle transmission + activation daemon | high | Deep-dived → §23 below |
| `dji_nn_server` | `ml_proxy` NN-inference Binder service for DSP-core inference | high | Deep-dived → already in `11_DJI_NN_SERVER_FINDINGS.md` |
| `dji_pbt` | Playback/transcode CLI test tool | low | Not escalated |
| `dji_ppt` | Post-processing (image-pipeline algorithm) CLI test harness | low | Not escalated |
| `dji_wlm_slave` | "Slave" side of the Wireless Link Manager's data-sync subsystem on E2 | medium | Not escalated |

### E2 image — libraries (`system_files/lib64/`)

| Library | Purpose (one line) | Priority | Disposition |
|---|---|---|---|
| `libduml_audio.so` | DUSS audio HAL (APU codec, ALSA PCM, ffmpeg filtering) | low | Not escalated |
| `libduml_databuffer.so` | Generic multi-transport bulk data-transfer engine (TCP/UDT/USB/bus bridging) | high | Deep-dived → §24 below |
| `libduml_dsocket.so` | Local file-descriptor-passing utility over a Unix domain socket | low | Not escalated |
| `libDjiMediaPlayer.so` | Client-side Binder wrapper around DJI's MediaPlayer service (no decode logic itself) | low | Not escalated |
| `lib_hal_dji_ycc.so` | Thin HAL for a YCbCr colour-space conversion ISP block | low | Not escalated |

---

# Part 2 — Addenda to other documents

The following short additions were made to existing documents; see each
document directly for full context. They are summarized here for
traceability.

## Addendum to `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` — `dji_flight`

This pass's full disassembly of `dji_flight` traced all six `system()`/
`popen()` call sites in the binary to their actual arguments, resolving
doc 08's open "worth checking whether any `%s` is externally influenced,
inconclusive" note about `dji_verify -n geofense -H %s %s` and
`dji_fw_verify -n 1105 -c 1105 -o %s %s`. **Resolution: no, not
exploitable through any call site this pass could locate.** Every one of
the six call sites' arguments is either a compile-time string literal or a
securely `mkstemp()`-generated temp path; none is built from DUML/network-
received data. The two `dji_verify`/`dji_fw_verify` call sites specifically
use `('/data/dynamic.db','/data/dynamic.sig')` /
`('/data/dynamic_temp.db','/data/dynamic_temp.sig')` and
`('/vendor/nfz/nfz.fw', <mkstemp path>)` / `('/data/nfz/.backup/nfz.fw',
<mkstemp path>)` respectively. The command-building wrapper itself
applies zero shell-metacharacter sanitization (a latent, not currently
exploitable, missing-defense-in-depth note), and a large statically-linked
GoogleTest death-test harness (including its own `execve()`-based
subprocess runner) was confirmed compiled into this production binary —
unnecessary attack surface, not itself a vulnerability.

## Addendum to `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` — `dji_navigation`

This pass fully disassembled the NFZ-height-limit backstop handler doc 08
already described architecturally. The handler (matching the triage's
`nav_event_cb_security_nfz_limit_height` log-tag string, confirmed at
vaddr `0x5c89c`) reads a 16-bit field directly from an incoming
message-bus event payload (`[event+6]`) and passes it straight into the
internal height-limit setter (`nav_flight_update_nfz_height_limit`,
vaddr `0x16b408`) with no additional cryptographic or application-layer
integrity check performed at this layer. This confirms doc 08's framing
exactly; whether the underlying route-table/event-client layer
authenticates the sender before delivery (which would be the real
determinant of exploitability) remains unresolved, same as doc 08 already
stated.

## Cross-reference note added to `09_DJI_AUTOTEST_EXPLOITABILITY_DEEPDIVE.md`

This pass's deep dive of `check_secure_debug` (§12 below) and the OP-TEE
TA investigation (`13_OPTEE_TA_FINDINGS.md`) together clarify that this
firmware contains **two architecturally distinct "secure debug" gates**,
which should not be conflated: `dji_autotest`'s `get_eagle_mode()` (the
subject of doc 09) is a simple, local text parse of `/proc/cmdline`;
`check_secure_debug`/`libamt_util.so`'s `sec_debug_state()` is a separate,
TEE/RPMB-backed cryptographic state machine (now confirmed to execute
inside the `e91c9402` TA — see `13_...`). This does not change doc 09's
"no confirmed remote path" conclusion, but it does add one small
corroborating data point to doc 09's `duss_event_shell` sub-handler
question: this pass's disassembly of the **separate** standalone
`duss_shell` CLI tool (§11 below) found it exposes named subcommands
`ping`/`asym_ping`/`trans_heartbeat`/`async_ping`/`route_control`/
`msg_send` — names strikingly close to doc 09's speculative
`duss_shell_asym_ping_task_entry`/`duss_shell_trans_heartbeat_task_entry`
candidates for `duss_event_shell`'s own internal dispatch table. The two
are different binaries (a standalone CLI vs. a cmd_set 0/cmd_id 0x89
in-process handler), and this pass did not confirm they are related beyond
the naming coincidence — flagged as a lead for whoever next disassembles
`duss_event_shell`'s dispatch table, not asserted as resolved.

## `07_ADSB_SOC_FINDINGS.md`

No addendum needed. The re-confirmation pass's findings (sub-block tags
`TBLD`/`BLLK`/`BLFA`, the `2022-03-04` build date, the `"bootloader"`
component name) are already fully present in that document.

---

# Part 3 — Deep-dive findings (24 not-yet-documented binaries/libraries)

## §1. `dji_blackbox` — flight-data blackbox daemon, multi-subsystem

**Role, confirmed and substantially extended beyond the triage guess.**
A large, multi-subsystem flight-data blackbox daemon (confirmed via ~30
recovered internal function names and embedded source paths): log
collection/rotation/export (`bb_log_exporter`/`bb_log_handler`/
`bb_log_download`/`bb_log_copy`), SD/flash space monitoring, a
`libduml_fastrtps`-based internal pub/sub channel ("DTBT") for telemetry
distribution, health-management and battery-prognostics forwarding, and
config parsing of `/system/etc/dji.json`/`blackbox.json`. It joins the bus
as a plain message-bus **client** (`duss_mb_create_route_table` →
`duss_event_create_client` → `duss_event_start_client`), not a dynamic
command registrar — `duss_event_register_dynamic_command` is confirmed
absent from `.dynstr` entirely (not just uncalled).

| Weakness | Impact category | Confidence |
|---|---|---|
| A hardcoded plaintext FTP credential (`dji_ftp`/`DJi_dajiang001`) is built into a live shell command (via `__snprintf_chk` → the shared `bb_misc_system()` wrapper) targeting `192.168.100.1`, the internal companion/debug network | hardcoded_credentials / local-lateral access to an internal FTP service | high |
| The log exporter's SD-card "detach_pc" step (exposing the SD card for direct host/PC access) is gated by a device/runtime flag (`androidboot.secure_debug` from `/proc/cmdline`) rather than cryptographic authorization at this specific call site | feature gated by boot flag, not crypto, at this call site | high for the gate's existence and location; not extended to how the flag itself is set (ties into `05_DJI_SEC_FINDINGS.md`/`13_OPTEE_TA_FINDINGS.md`, not re-investigated here) |
| The log-handler framework (LGH/DLD/CPY) builds and executes at least 8 distinct `system()`/`popen()` shell-command templates assembled with `snprintf` from filenames/paths ultimately originating from JSON config and internal log/tag bookkeeping state | broad reliance on `system()`/`popen()` for routine filesystem operations is a classic injection-prone pattern | medium — the pattern is confirmed; whether any specific field (e.g. a tag's `module_name` from the `add_tag` DUML event) can carry shell metacharacters into one of these templates was not fully traced end to end |
| A fully static (non-parameterized) shell command invokes `dji_mb_ctrl` with a hardcoded raw DUML message (`cmd_id 0xea`) to fetch an "export_list" | confirms shell-based DUML injection via `dji_mb_ctrl` is a normal, load-bearing pattern in this firmware, not an anomaly | none directly exploitable at this call site (fully static string); raises the value of `dji_mb_ctrl` itself as a target (see §2) |

**Not determined:** whether any specific externally-reachable field can
carry shell metacharacters into the LGH/DLD/CPY/TAG command templates; the
exact numeric `(cmd_set, cmd_id)` values routed to the 17 recovered
`bb_event_cb_*` handlers (dispatch happens at a layer outside this
binary's own code); whether the `0xea` raw-DUML-injection call site is
reachable only at startup/sync or from elsewhere.

## §2. `dji_mb_ctrl` — general-purpose DUML message-bus injector CLI

**Role, confirmed exactly as triage guessed.** A single-purpose CLI that
builds and sends one arbitrary DUML message per invocation (target
machine/host/type/idx, seq_id, cmd_set, cmd_id, attrib, up to 8 typed
payload fields or raw hex), confirmed to share one internal
build-and-send subroutine between its `getopt` CLI mode and its
interactive camera-command submenu. `dji_blackbox` (§1) is a confirmed
real caller.

| Weakness | Impact category | Confidence |
|---|---|---|
| Fully general, OS-permission-gated-only DUML message injector shipped on the production image with no in-binary authentication, allow-list, or capability check of any kind | missing_authz / local command-injection onto the internal message bus, privilege-equivalent to whatever can execute this binary | high |
| `dji_mb_ctrl` carries no dedicated SELinux exec label — `vendor_files/etc/file_contexts` assigns `dji_service_exec` to real DUML daemons and the stricter `dji_sec_exec` to the activation daemon, but has no entry for this raw bus-injection tool | missing hardening relative to the project's own production daemons | high for the labeling gap itself; medium on how much practical difference the fallback domain makes (not analyzed) |
| The per-target advisory lock file is `open()`ed at a predictable path (`/tmp/dji_mb_ctrl_<addr>.flock`) with `O_CREAT`, no `O_EXCL`/`O_NOFOLLOW`, then unconditionally `ftruncate()`d and written to | local file clobber / TOCTOU primitive if `/tmp` is world-writable at runtime (not independently confirmed for this image) and a caller's target address is predictable | medium — mechanism confirmed in disassembly; real-world exploitability depends on `/tmp`'s runtime mount mode and caller privilege, neither confirmed |

**Not determined:** the exact numeric cmd_id/attrib values baked into the
4 hardcoded interactive camera-submenu presets; whether `/tmp` is actually
world-writable at runtime on a real unit; the effective runtime UID/
SELinux context of `dji_mb_ctrl`'s typical callers beyond the one
confirmed `dji_blackbox` invocation.

## §3. `dji_ml` — DSP-accelerated person/vehicle detection for obstacle avoidance

**Role, confirmed with real control-flow evidence.** The navigation
subsystem's ML-vision perception engine: a DSP-core firmware lifecycle
(`duss_hal_dsp_acquire/halt/launch` + `dji_fw_load_file`), a separate
verify-then-copy path for CNN/model blobs (`dji_fw_verify_load2mem`), and
a MOT/ReID/DynamicROI(privacy-blur) detection-and-tracking lifecycle.
`duss_event_register_dynamic_command` is confirmed absent — this binary
is reached through the internal navigation bus or direct library calls,
not as a DUML command endpoint in its own right (a *negative* finding
that narrows its own attack surface relative to the triage's assumption).

| Weakness | Impact category | Confidence |
|---|---|---|
| ML model/weight decryption for MOT/ReID/DynamicROI is wired up via an application-supplied callback registered with the vendor CV libraries (`RegisterMOTDecryptCallback` etc.), i.e. the decrypt trust boundary is ordinary unprivileged process memory, not a TEE/secure-element | confidentiality / IP-protection architecture note for proprietary model weights — not a flight-safety memory-corruption issue | medium-high for the mechanism's existence; explicitly not extended to the strength of whatever the callback does (not traced further) |
| A second, separate DSP CNN model-loading path uses a local by-name "key item" lookup (strings: `'failed to find key item %s'`) rather than a callback, feeding into the same `dji_fw_verify_load2mem`-gated load path | same confidentiality/IP-protection category, different mechanism | medium — existence and integration point confirmed; key-lookup implementation itself not examined |
| `dji_ml` has its own private in-process `[ML_FWK]` request/response dispatch surface (`func_id`/`host_id`/`req_cmd`) entirely separate from DUML — should not be conflated with wire-level cmd_set/cmd_id | architecture documentation only | medium |

**Not determined:** several imported `duss_event_*`/`duss_mb_*` bus symbols
are linked but no direct branch target could be found for them (likely
reached through a C++ vtable abstraction a static immediate-branch scan
can't resolve) — a methodology limitation, not a security claim; no
exhaustive memory-safety audit of the 866 KB binary was attempted.

## §4. `dji_network` — Wi-Fi/SDR link-management daemon

**Role, confirmed and extended.** Owns the full lifecycle of
`wpa_supplicant`/`hostapd`, an internal state machine governing Wi-Fi
AP/STA, SDR, and DJI's proprietary 802.11p ad-hoc mode, debugfs-based
tuning of the `ath6kl` driver, and persistence of Wi-Fi config and
flight-regulation/flight-purpose metadata. Confirmed as a narrow bus
*sender* (no `duss_event_register_dynamic_command` import), not a command
dispatcher.

**This is the single richest set of concrete, high-confidence findings in
this sweep.**

| Weakness | Impact category | Confidence |
|---|---|---|
| The DJI-proprietary 802.11p link/pairing key is derived from only 4 time-seeded `rand()%26` characters concatenated with 3 hardcoded literal characters (`'ABC'`) — an ~8-char key with roughly 18–19 bits of true entropy from a non-cryptographic PRNG | weak cryptographic key generation / predictable secret | **high** |
| The same function unconditionally logs the full generated key value in cleartext via `duss_log_print("generate random key: %s", ...)` | sensitive-data exposure via logging | **high** |
| When the loaded Wi-Fi PSK field is empty, the code logs `"psk is weak, force to be 12341234"` and `strcpy()`s the literal, purely-numeric 8-character passphrase `"12341234"` into the active config | hardcoded/weak default credential | **high** |
| A code path self-labeled by the vendor's own log string `"w_ctrl_cc factory backdoor*****"` forces the Wi-Fi/SDR regulatory country code to a fixed value (`'K','3'`) when an internal state flag is set, overriding the normally-validated country code | hidden maintenance/regulatory-override mode (architecture note; what sets the triggering flag was deliberately not traced, per scope boundary) | medium |
| (Ruled out) the two flight-regulation/flight-purpose length-validation functions the triage flagged both check length against a fixed limit *before* any copy and use a FORTIFY-matched `__memcpy_chk` bound | no vulnerability found — defense-in-depth confirmed | high |

**Not determined:** what external trigger sets the "factory backdoor"
country-code gating flag (deliberately not pursued, per scope boundary —
documenting the mechanism, not how to trigger it); most of this binary's
~250 `net_*`/`wifi_*`/`sdr_*` function names could not be tied to specific
addresses (fully stripped, no `.gnu_debugdata`).

## §5. `dji_sdrs_agent` — SDR-link log/diagnostic/control agent

**Role, confirmed with refinement.** Built from many small `sdrs_log`/
`sa_relay` modules plus a top-level `sa_*` service layer: USB-hotplug-
triggered modem firmware flashing (`sa_bootctrl`), NVRAM parameter
storage (`sa_nvram`), physical pairing-button handling (`sa_pair`), and
heartbeat/reset of a USB-attached modem. `duss_event_register_dynamic_
command` is real here (the only binary in this sweep's batch 3 confirmed
to import it) but used via a **data-driven** registration loop — a
caller-supplied array of 12-byte records is iterated at runtime, so the
actual registered `(cmd_set, cmd_id)` values are not statically
recoverable from this binary alone.

| Weakness | Impact category | Confidence |
|---|---|---|
| Local NVRAM parameter files backing device-identity fields (production SN, `uav_dev_id`/`mrc_dev_id`/`arc_dev_id`/`gls_dev_id`) are integrity-checked with a plain CRC16, not a cryptographic MAC or signature | data-integrity / device-identity-spoofing if filesystem write access is otherwise obtained (requires a prior foothold; the check itself, not a demonstrated bypass) | medium-high |
| `sa_bootctrl.c` builds `brload`/`fastboot` flashing commands and invokes them via `system()` automatically on a USB-hotplug uevent whose VID/PID matches a JSON-configured value, with no cryptographic check of the attached device's identity performed by this agent | automatic privileged external-tool invocation gated only by a USB VID/PID string match | medium — command construction confirmed at instruction level; whether the flashed image is separately authenticated by the receiving chip's own secure boot was not checked (out of scope) |
| `sa_pair.c` invokes `system("dji_mb_ctrl -S test -R diag -g 9 -t 0 -s 6 -c 0x2f -1 0x01")` — a bare command name, not an absolute path — in direct response to a physical-button keycode on `/dev/input/event0` | insecure coding practice (relative-path `system()`, `$PATH`-dependent) | high for the mechanism; low practical relevance absent an attacker-controllable `$PATH` |
| The `duss_util_crc16_verify` import the earlier triage flagged as SDR-link-relevant is, in this binary, used only on local NVRAM file reads, not on incoming SDR USB/UART traffic | documentation correction, not itself a vulnerability | medium |

**Not determined:** the actual registered `(cmd_set, cmd_id)` table
contents (runtime-supplied, not statically recoverable); whether the
`-1 0x01` CLI argument literally encodes `cmd_id=0x01` in `dji_mb_ctrl`'s
own parser (not analyzed); the full USB-hotplug condition tree gating the
`brload`/`fastboot` flashing path.

## §6. `dji_wlm` — Wireless Link Manager daemon

**Role, confirmed and sharpened.** The canonical source of chip/board/
production serial numbers in this firmware (`get_chip_sn`/`get_board_sn`/
`get_product_sn` are **exported, non-hidden** symbols of this plain
executable — unique to this binary on the image). Also owns multi-link
(OcuSync/LTE/Wi-Fi) fusion/bandwidth estimation and data forwarding. Joins
the bus as exactly **one** client with a single, narrow command override
(`duss_event_modify_dynamic_command` on the already-framework-registered
cmd_set `0x51`/cmd_id `0x05` "Route Switch", confirmed by direct literal
immediates `movs r1,#0x51` / `movs r2,#5` at the one call site) — not the
broad command-dispatch footprint the triage's import list implied.

| Weakness | Impact category | Confidence |
|---|---|---|
| Device identity (chip/board/production serial numbers) is sourced from `/proc/cmdline`, a conventionally world-readable file, via the exported `get_chip_sn`/`get_board_sn`/`get_product_sn` functions | local information disclosure — any unprivileged local process could read these identity values directly, bypassing the DUML bus and its access control entirely | high for the mechanism; medium for severity (`/proc/cmdline`'s actual on-device permissions were not independently re-verified) |
| `wlm_route_switch_ack_proc` (the custom Route-Switch ack handler) dispatches on a single byte at a fixed offset with a 3-way state switch, and checks only transaction-sequence continuity before acting on an acknowledgement | message-validation robustness observation; adequacy of the sequence check against a spoofed/replayed bus peer was not assessed | medium |
| A per-second background thread (`wlm_common_dbg`) builds shell command lines via `snprintf` from fixed templates containing backticks (e.g. `` pidstat -t -p `pgrep dji_wlm` >> %s ``) and passes the result to `system()` | use of `system()` with shell-metacharacter-containing templates — hardening concern | high for the pattern; medium-low on exploitability since both the enabling flag and the `%s` path appear to originate from local startup config, not DUML/RC-controlled input |

**Not determined:** full struct layout of the dynamic-command descriptor
beyond the handler-pointer field; whether the exported SN getters are
consumed by any other process via `dlopen`/`dlsym` (no static reference
found elsewhere on the image); the relationship between `dji_wlm` and the
separate `dji_wlm_slave` process name (same ELF under a different role,
most likely, not directly confirmed).

## §7. `dji_upgrade` — firmware-upgrade orchestration daemon

**Role, confirmed.** A JSON-config-driven orchestrator (`/system/etc/
upgrade.json`, fallback `/system/etc/dji.json`): converts JSON peer-id
fields to v1 DUML host IDs, `dlopen()`s a product-specific plugin library,
and drives a fixed `upgrade_register_init → ... → upgrade_post_init`
sequence. Confirmed as a config/orchestration client, not a DUML
registrar — the real motor/power/LED/battery-ratio enforcement logic
lives in `libupgrade_init.so`/`libupgrade_register.so`/
`libupgrade_common.so` (out of scope for this file-specific pass).

| Weakness | Impact category | Confidence |
|---|---|---|
| A single JSON-configured boolean flag chooses between two mutually-exclusive ways the process's DUML v1 client handle gets established — delegated registration, or a handle taken verbatim from another JSON/config-supplied field with no validation visible in this binary | config-driven trust-boundary switch for bus-handle provisioning | medium — exploitable only if the backing JSON config is reachable by an untrusted party before this daemon reads it, which was not evaluated |
| `dji_upgrade` `dlopen()`s a plugin `.so` whose path comes directly from the `product_lib_name` JSON key, then resolves and calls 5 lifecycle entry points from it, with no signature, hash, or path-allowlist check found in this binary between reading that value and the `dlopen` call | unverified dynamic-library load from a configuration-supplied path | medium — real-world exploitability depends entirely on whether the config file/plugin path is reachable by an untrusted party, likely gated upstream by firmware-partition verification not analyzed here |

**Not determined:** the real implementation of `str_to_v1_host_id`/
`standard_demo_communication_init`/`get_duss_v1_client_handle` (live in
other libraries, out of scope); the exact enforcement logic for
`safe_bat_ratio`/`prerequisite_item_1..6` (dji_upgrade only copies these
JSON values; the real gating lives in consumer libraries); whether
`upgrade.json`/`dji.json` are writable by an untrusted party.

## §8. `dji_fw_verify` — thin CLI wrapper around `libfw_util.so`'s verify function

**Role, confirmed.** A getopt_long wrapper calling exactly two imports
(`str2id`, `dji_fw_verify_file`) from `libfw_util.so`; performs no I/O, no
ION/mmap/secure-memory handling of its own. No DUML bus participation.

| Weakness | Impact category | Confidence |
|---|---|---|
| The tool's own `--help` text documents `-o, --output=FILE` and `-s, --size`, but the real `getopt_long` table registers `--outoftime` for `-o` and no long form at all for `-s` | stale/incorrect self-documentation — automation scripted against the documented long options would fail silently where the real (undocumented) `--outoftime` works | confirmed (byte-level `struct option` decode) |
| The real return code from `dji_fw_verify_file` is discarded; any nonzero result is normalized to exit code `-1` and a single generic "verify fail" message | loss of diagnostic/forensic granularity at the CLI boundary | confirmed |
| The `-c`/`--chunk` value is parsed into a global but never read again anywhere in this binary's traced code — dead/ineffective in this build | possible logic/trust gap if any part of the update pipeline assumes `-c` scopes which chunk is verified | plausible, not independently confirmed against callers |
| All CLI-supplied strings (file path, name, output value, size) are forwarded essentially unvalidated across the call boundary into `libfw_util.so` | this binary offers zero defense-in-depth of its own; robustness of the whole chain rests entirely on the library | confirmed for this binary's own code; `libfw_util.so`'s side not examined |

**Not determined:** the precise semantic meaning of `-o`/`--outoftime`
inside `libfw_util.so`; the exact return-value contract distinguishing
different failure causes.

## §9. `dji_verify` — self-contained firmware-image authentication/decryption CLI

**Role, confirmed and corrected.** Unlike `dji_fw_verify`, this tool
implements real image-authentication/decryption logic **itself** (no TEE/
keystore library linked at all — `libc`/`libstdc++`/`libm` only): a local
"keymgr", an enc/auth-key lookup, header authentication, and a final
digest comparison. Confirmed as a real runtime dependency of the firmware
upgrade pipeline (`libupgrade_upgrade.so`'s literal command template
`dji_verify -n %s -c %s -o %s '%s'`) **and** of `dji_flight`'s geofence/NFZ
database authentication (`dji_verify -n geofense -H %s %s`, per §1's
`dji_flight` addendum above); carries the dedicated `dji_service_exec`
SELinux label.

**This is a different check from `libdji_sec_ds_whitelist_upgrade.so`'s
version-whitelist gate (§14) — the two should not be conflated.** No
weakness was found in `dji_verify`'s own cryptographic checks; this
section documents their architecture, not a break.

| Weakness | Impact category | Confidence |
|---|---|---|
| The local "keymgr init" routine only `memcpy`s three fixed-size constant blobs out of the binary's own data section and **always returns 0** — there is no code path that can produce a failure, so the "keymgr init failure" error branch in `main()` is dead code in this build | key-management-architecture note: the "keymgr" is a trivial, always-succeeding copy of built-in constants, not a handshake with hardware-backed key storage | high |
| The "get enc/auth key" lookup is a hardcoded ID-dispatch table over a handful of fixed numeric IDs, each returning a pointer into the same constant blobs | key material is selected by a small hardcoded table pointing at embedded constants, not derived from any hardware root of trust visible in this component | medium-high |
| Header authenticity is gated by a 256-byte check (size consistent with an RSA-2048 signature or similar MAC); payload integrity by a 32-byte digest comparison (size consistent with SHA-256) | crypto architecture is consistent with real public-key signature + hash verification; exact algorithms not confirmed | medium — sizes are suggestive, not proof; the primitives themselves were deliberately not reverse engineered |

**Not determined:** the exact cryptographic algorithm inside the key-set/
scramble-key-derivation primitives; whether the three embedded constant
blobs are genuine production key material, device-class-generic constants,
or placeholder/test values (deliberately not extracted or dumped); whether
`dji_verify`'s check is the sole/authoritative gate during a real OTA
flash or geofence-DB load, or one of several redundant checks elsewhere.

## §10. `dji_ftpd` — network FTP server exposing flight-critical directory aliases

**Role, confirmed — with one triage claim explicitly refuted by
disassembly.** A complete, custom-written (not vsftpd/busybox-derived)
FTP daemon implementing a broad RFC959+ command set, with a static
7-entry alias table (`camera`, `dji_perception`, `flyctrl`, `gimbal`,
`navigation`, `system`, `dji_flight`) matched against a client-supplied
top-level path component before further handling.

**Refuted:** the triage guessed FTP login was tied to a TEE-derived
device key (based on `amt_get_derive_log_key`/`libteec.so` imports being
present in this binary). Disassembly shows those calls are confined to a
**separate, independently-named** function (`dji_log_header_init`) that
builds a log-file-header key, unrelated to the FTP login path. The actual
USER/PASS check `fopen()`s `/etc/ftp.conf`, splits each line on `:`, and
does two plain `strcmp()`s against the client-supplied credentials.

| Weakness | Impact category | Confidence |
|---|---|---|
| Network-exposed FTP authentication for a daemon exposing `/flyctrl`, `/navigation`, `/gimbal`, `/camera`, `/dji_perception`, `/dji_flight`, `/system`, and `/blackbox/upgrade/` is a flat `/etc/ftp.conf` colon-delimited username:password list compared with plain `strcmp()` — **not** a TEE/device-bound check | authentication / credential-management | confirmed for the mechanism; real-world severity depends on `/etc/ftp.conf`'s actual contents/permissions, not examined (outside this binary alone) |
| A cached `system("cat /proc/cmdline \| busybox grep androidboot.secure_debug=1")` check (run once, memoized) globally disables a per-file "skip encryption/processing" flag while `secure_debug` is set; independently, any requested path containing the substring `emmc_index`, `latest`, or `/blackbox/export_tmp/info` gets the same "skip" treatment regardless of `secure_debug` | content-protection/access-control (information handling) | confirmed for the gating mechanism; what the downstream "encryption/processing" step actually does was deliberately not traced (crypto internals, out of scope) |
| The path-sanitizing helper protecting `/blackbox/upgrade/` uses `realpath()` canonicalization but then checks containment with `strstr()` (substring-anywhere) rather than a strict canonical-prefix comparison | weaker denylist-style path/access-control pattern | plausible — mechanism confirmed; practical bypassability depends on the real filesystem layout, not inspected |
| One network-facing daemon exposes read/write FTP access to all 7 flight-critical mount aliases once any one plaintext-file credential succeeds, with no further per-command privilege separation observed between aliases | attack-surface / architecture | confirmed for the alias table and resolution loop; a per-alias permission-flag byte was observed but not traced to a consumer |

**Not determined:** what the secure_debug/path-substring-gated
"encryption/processing" step actually does cryptographically; whether
`/etc/ftp.conf` on a real device contains static or provisioned
credentials, and what writes it; the exact semantics of the per-alias
permission byte.

## §11. `duss_shell` — interactive CLI DUML bus client/raw-injector

**Role, confirmed.** An interactive command-line tool matching argv[1]
against an 11-entry table (`dump`/`ping`/`log`/`stat`/`capture`/
`asym_ping`/`trans_heartbeat`/`async_ping`/`route_control`/`msg_send`, plus
`config`), joining the bus via the same shared attach routine regardless
of subcommand, with `msg_send` as the single call site for raw packet
transmission. No `duss_event_register_dynamic_command` import — a bus
client/injector, not a dispatcher. (See also the cross-reference note to
doc 09 in Part 2 above, re: this tool's subcommand names.)

| Weakness | Impact category | Confidence |
|---|---|---|
| `msg_send` is a fully user-controlled raw DUML packet injector — target_machine, host_id, cmd_set, cmd_id, and raw hex payload all flow directly from `argv` into the sole `duss_event_send_sync_v2` call site with no validation beyond hex/format parsing | missing_authz / internal command injection (precondition: local shell access already required) | high |
| Every invocation unconditionally inserts a route-table entry and spins up a new named bus endpoint (identity sourced from `/data/dji/duss_shell.conf` or config_id), serialized only by a predictable, world-writable-path `flock` | message-bus identity/route-table spoofing surface (precondition: local shell access) | medium — call sites confirmed; the exact wiring of `route_control`'s parameters into the one `duss_mb_create_route_table` call site was not fully traced |

**Not determined:** whether `log`/`stat`/`capture` send any bus traffic
at all or are purely local diagnostics (no additional send-primitive call
sites found, but each subcommand's method body was not individually
disassembled); the exact meaning of two constant bytes written into the
outgoing packet struct during `msg_send`.

## §12. `check_secure_debug` — CLI query of `libamt_util.so`'s secure-debug state

**Role, corrected.** The triage guessed it "likely prints/exits with the
state." Disassembly shows it **never prints anything** — `main()` is an
11-instruction pure exit-code predicate: calls `sec_debug_state()`
(imported from `libamt_util.so`, the same library `05_DJI_SEC_FINDINGS.md`
and `13_OPTEE_TA_FINDINGS.md` already name as the activation/secure-debug
backend); exit code 0 means the call succeeded **and** wrote a non-zero
state value; exit code 1 covers everything else.

| Weakness | Impact category | Confidence |
|---|---|---|
| Both of `main()`'s only two execution paths — `sec_debug_state()` itself failing, and it succeeding with state `0` — terminate with the identical exit code `1` | error-handling/observability weakness: a calling script cannot distinguish "secure debug confirmed disabled" from "the query to `libamt_util.so` failed for an unrelated reason" | high (directly observed: both paths converge on the same `movs r0,#1` return) |
| The binary performs zero local validation; it is architecturally a pure pass-through onto `libamt_util.so`'s `sec_debug_state()`, with the entire trust boundary placed in the dynamically-linked library | trust-boundary / dynamic-linking dependency — any component able to influence which `libamt_util.so` loads controls what every caller of this CLI observes | medium — architecture confirmed; real tamperability depends on filesystem/verified-boot properties not re-examined here |

**Scope-boundary stop point, stated plainly:** the real secure-debug logic
(`sec_debug_state` plus sibling `sec_debug_generate/verify_internal_msg`
exports) lives in `libamt_util.so`, very likely TEE/RPMB-backed per
`13_OPTEE_TA_FINDINGS.md`'s mapping of the `e91c9402` TA's `ssd_bind`/
`ssd_verify`/`decrypt_ssd_root_key` functions. This pass confirms those
exports exist and are this CLI's sole dependency; it deliberately does not
disassemble `libamt_util.so` or attempt any bypass of the challenge/
response mechanism. See Part 2's cross-reference note to doc 09 above for
how this relates to (and is architecturally distinct from) `dji_autotest`'s
`get_eagle_mode()` gate.

## §13. `libdji_fw_verify_util.so` — ION-shared-memory client for TEE-backed firmware verification

**Role, confirmed and upgraded from "strongly suggests a TEE TA" to
confirmed.** Exactly 3 public entry points (`dji_fw_verify_file_init/
update/final`) that stage firmware bytes into an ION DMA-buf and hand the
resulting fd/vaddr to `fw_util_verify_*` (imported from `libfw_util.so`/
`libfw_util_ca.so`). `libfw_util_ca.so` in turn imports the full
GlobalPlatform TEE Client API (`TEEC_OpenSession`, `TEEC_InvokeCommand`,
`TEEC_AllocateSharedMemory`, etc.) — confirmed identically on both the
E1E (32-bit) and E2 (aarch64) builds, tying directly into
`13_OPTEE_TA_FINDINGS.md`'s `09db16c0` "FW UTIL TA". The real caller is
`libupgrade_upgrade.so`'s `upgrade_package_verify_image()` (that library
itself out of scope for this pass).

| Weakness | Impact category | Confidence |
|---|---|---|
| `dji_fw_verify_file_init` computes the ION buffer size as `size_kb << 10` using a 32-bit shift, and only falls back to a 16 MB default when the **pre-shift** `size_kb == 0` — a sufficiently large `size_kb` wraps the shift to 0, which then slips through as the real buffer size | denial of service / resource-exhaustion in the firmware-verification path — explicitly **not** a signature-bypass, since the TEE-backed final check is never reached if the chunking loop hangs | confirmed mechanism (re-derived independently on both ISAs/compilers); whether `size_kb` is ever attacker-influenced was not determined (originates in the unexamined `libupgrade_upgrade.so`) |
| When the (possibly wrapped-to-0) buffer size is 0, `dji_fw_verify_file_update`'s chunking loop computes `chunk_len=0` and never advances its "remaining" counter, so the loop never terminates | denial of service (hang); fails closed, not open | confirmed mechanism; external reachability not determined |
| `init`/`update`/`final` share one process-wide global ION-handle pointer with no visible application-level locking | correctness/race risk only if the (sole known) caller ever invokes these APIs concurrently — not confirmed either way | confirmed that the state is unlocked; concurrency of the real caller not examined |

**Not determined:** whether `size_kb` can ever reach the overflow
threshold via any externally-reachable path; anything about what
`fw_util_verify_*` actually checks inside the TA itself (deliberately not
pursued, per the TEE scope boundary — see `13_OPTEE_TA_FINDINGS.md`).

## §14. `libdji_sec_ds_whitelist_upgrade.so` — firmware anti-downgrade whitelist gate

**This is the single clearest "no gate at all"-class finding in this
sweep, with the same rigor as `09_DJI_AUTOTEST_EXPLOITABILITY_DEEPDIVE.md`'s
`process_get_file_list` finding.**

**Role, corrected from the triage's "unclear semantics" guess.** The
library's single exported function, `upgrade_check_version_whitelist`
(confirmed byte-for-byte: a 4-byte body, `movs r0,#0; bx lr`), is a
**hardcoded, unconditional stub that always returns 0** — it reads none
of its arguments and performs no comparison, table lookup, or string/
memory inspection of any kind. The remaining ~6 KB of the library is
generic Android CRT glue plus a statically-linked minimal libunwind/
libc++abi block, confirmed by matching literal LLVM source-file strings —
not application logic.

The one confirmed caller anywhere in the examined firmware
(`libupgrade_upgrade.so`'s `ex_up_module_upgrade`, at its single call
site) branches on the return value: `cmp r0,#0; beq <skip-error-block>`,
and only logs/handles the self-documenting rodata string `"version %s is
blocked by whitelist\n"` when the result is **nonzero**. This fixes the
ABI unambiguously: 0 = allowed, nonzero = blocked.

| Weakness | Impact category | Confidence |
|---|---|---|
| The firmware-version anti-downgrade/whitelist gate always returns the "allowed" value and never actually checks anything, so the one known call site that branches on its result can never see a "blocked" outcome in this shipped build — the control is permanently inert | integrity / anti-downgrade and upgrade-authorization architecture — the named control enforces nothing at this call site | **high** (function body and its 4-byte size independently verified byte-for-byte via capstone against the raw ELF; the caller's branch and the self-documenting log string were both directly disassembled) |
| Root cause of the stub-ification cannot be determined from this one file: equally consistent with (a) deliberate simplification for this product/market variant, (b) an engineering/debug build artifact that should not have shipped, or (c) the real check having been relocated to another binary not examined here | unknown / insufficient evidence for root cause | n/a — explicitly not determined rather than guessed |

**Not determined:** why the function is a stub; the function's originally-
intended parameter types (only 2 of up to 4 AAPCS registers are populated
at the one call site, but since the stub reads none of them the "real"
signature can't be reconstructed); whether any other caller of this exact
symbol exists outside the examined `system_files` tree (a targeted string
search of `vendor.img` found none, but it was not exhaustively unpacked);
the full downstream consequence in `ex_up_module_upgrade` had a real
"blocked" value ever been returned.

## §15. `libduml_rpc.so` — Inter-Chip-Communication RPC/transport layer

**Role, confirmed and refined.** The RPC/transport layer carrying DUML
command/ack packets across an Inter-Chip-Communication (ICC) channel
(e.g. between the main SoC and a sub-MCU such as gimbal or ESC) —
confirmed on both the E1E (32-bit) and E2 (aarch64, which carries a real
`.gnu_debugdata`) builds. `duss_event_register_dynamic_command` is
confirmed absent on both architectures; instead the library implements its
own small, **caller-supplied** 13-slot dispatch table (`cmd_tbl`, built
and owned by whichever daemon calls `dji_rpc_init` for a given ICC link —
not resolvable from this library alone), functionally parallel to, but
architecturally distinct from, the global DUML cmd_set/cmd_id space.

| Weakness | Impact category | Confidence |
|---|---|---|
| On ack receipt, when the received message exceeds the caller-supplied ack-buffer capacity, the payload copy is correctly skipped — but the full, un-clamped peer-controlled length is still written unconditionally into the `*ack_len` out-parameter, and `dji_rpc_write_cmd_sync` still returns its normal success code | information-disclosure / out-of-bounds-read risk in the *calling* daemon, which trusts `*ack_len` to size a subsequent read of its own smaller buffer | high for the library-side defect itself; real exploitability depends on how each specific caller uses the returned length (outside this file) |
| The RX chunked-reassembly loop derives its completion bound entirely from a 16-bit peer-declared `payload_len` field before any check that the value is achievable within the destination buflist node's actual (fixed, 128-byte-payload) capacity — only *received-so-far vs. declared-total* is checked, never *declared-total vs. buffer-capacity* | denial of service — a peer declaring an oversized `payload_len` can stall the RX thread on a never-completing receive | medium — missing upfront check confirmed; the precise runtime consequence depends on `duss_hal_icc_receive` (not analyzed) |
| (Validated non-finding) the length-overflow detection path (`received_len > declared total`) is correctly implemented — logs and discards rather than acting on the anomalous buffer | none — correctly-implemented defensive check | high |
| (Validated non-finding) `handle_task_entry`'s cmd_id-indexed dispatch is fully bounds- and null-checked at every step | none | high |

**Not determined:** the real-world meaning of the 13 internal RPC
message-type values (caller-supplied, per-link); the exact behavior of
`duss_hal_icc_receive` on a never-satisfiable request (in `libduml_hal.so`,
not analyzed); which specific daemon(s) instantiate this library's RPC
objects for which ICC link.

## §16. `libduml_payload.so` — DUML device-negotiation wire-format parser

**Role, confirmed.** The parser for DUML's device-negotiation protocol
(`hardware/dji/duml/utility/protocol/device_negotiate.c`): decodes a
connected peer's identity/channel/data descriptors during bus negotiation.
Pure parse/accessor/destroy library — no DUML dispatch imports, confirmed
on both the E1E and E2 builds.

**Confirmed, concrete memory-safety findings** — the clearest classic
length-prefixed-TLV over-read pattern in this sweep:

| Weakness | Impact category | Confidence |
|---|---|---|
| `dn_dev_info_parse_chnl_info` checks the input `len` exactly once, against only the fixed 9-byte sub-header, then trusts a **wire-supplied channel count** to drive a loop reading up to that many 10- or 23-byte records — with no check that the implied end stays within the real buffer | memory-safety / out-of-bounds read → denial of service (crash) and potential heap-data disclosure (stale/adjacent bytes land in the returned channel-descriptor array) | **high** — exhaustive instruction-level review of every comparison in the function found the length register referenced in exactly one place |
| `dn_dev_info_parse_data_info` has the identical defect, compounded: a wire-supplied `data_nr` drives an outer loop, and for **each** entry a second wire-supplied byte (`chnl_type_nr`) drives an additional unchecked `malloc`+`memcpy` of up to 255 bytes | same impact, compounded (nested unchecked length) | **high** |
| `dn_dev_info_parse_command` checks `len > 1` (i.e. ≥ 2) but unconditionally reads a 4-byte structure — a 2-byte over-read when `len` is exactly 2 or 3 | minor out-of-bounds read; this is the very first sub-parser called on every device-negotiation message | **high** |
| (Contrast, non-finding) the two fixed-size record parsers (`'DEV'`/`'HST'` magic) correctly compute and check their minimum required length before any read | informational — the gap above is specific to the two variable-count array parsers, not a blanket defect | high |

**Not determined:** which upstream DUML daemon(s) actually call these
parsers (would require examining other binaries); whether the production
receive buffer is heap- or stack-allocated and what lies adjacent to it
(determines crash vs. info-leak); whether the aarch64 (E2) copy, confirmed
to export the same symbols, has the identical bugs (very likely, given
identical source, but not independently re-verified instruction-by-
instruction there).

## §17. `libduml_dn.so` — device-node bus client library

**Role, confirmed and extended.** Two subsystems: a synchronous request/
response layer (`dn_device_regist`/`subscribe`/`info_query`, each over
`duss_event_send_sync` with a fixed timeout) and a separate local
async-callback subsystem (`dn_device_link_create`/`set`/`destroy`, a
worker thread blocking on an OSAL event). `duss_event_register_dynamic_
command` confirmed absent — sender/consumer side, not a registrar.

**A second confirmed, concrete memory-safety finding:**

| Weakness | Impact category | Confidence |
|---|---|---|
| `dn_device_info_parse()` masks the first 16 bits of its input to just 4 bits (0–15) with **no further range check**, then uses that as an index×8 into a 14-slot `.data.rel.ro.local` table and calls through the loaded pointer. The sibling function `dn_dev_info_size_get`, which indexes the **same table**, explicitly rejects any index > 4 (`cmp r0,#4; bhi→return 0`) — proving the table's intended valid range is 0–4 and that this function's bare 4-bit mask is a real inconsistency. Reading all 16 slots directly from the file confirms: indices 0, 1, 2, 5 are `NULL` (indirect call to address `0x0`); index 14 lands in `.fini_array`/`.dynamic` data (indirect call to address `0x3`); index 15 likewise (`0x2`); index 10 is a genuine function from the statically-linked libunwind blob that dereferences its argument as a vtable pointer and makes a *further* indirect call through it | memory_corruption: for indices {0,1,2,5,14,15} — a **deterministic crash** (branch to address `0x0`/`0x2`/`0x3`); for index 10 (and plausibly the unexamined 8/9/11/12/13) — a type-confusion indirect-call primitive, architecturally the kind of thing that could be escalated toward attacker-influenced control flow if an attacker can also influence memory at the address the input buffer's first word points to | **high** confidence for the OOB-index mechanism and the specific crash targets for 0/1/2/5/14/15/10 (all read directly from the file's own bytes at the correct offsets); **not independently confirmed** whether any real caller elsewhere in the firmware can deliver an out-of-{3,4} type nibble with attacker-influenced content — no escalation was attempted or validated, consistent with this project's scope boundary |

**Not determined:** the precise behavior of dispatch slots 8/9/11/12/13
(not individually decoded, though likely more of the same libunwind-
internal code, by position); whether any real caller can reach
`dn_device_info_parse()` with an out-of-range type nibble and
attacker-influenced buffer content. (A minor, non-security code-quality
note: the background worker thread's own log line for an event-destroy
failure is a copy-pasted format string naming a different, unrelated
function — misleading for log-based triage only.)

## §18. `libduml_dev_hb.so` — per-target DUML heartbeat/timeout watchdog

**Role, confirmed and corrected on one point.** Two subsystems:
`device_heartbeat` (an active prober — sends and receives heartbeat
packets by DUML device-address) and `device_monitor` (a passive timeout
watchdog driving a 4-state machine). **Correction:** the triage guessed
this library performs the GPIO hardware reset itself; disassembly shows
it imports **neither** GPIO HAL symbol and never calls either — on
timeout, it only invokes a caller-supplied opaque function-pointer
callback. The only binary on the image confirmed to import both the GPIO
symbols and this library's exports is `dji_sdrs_agent` (§5) — strongly
indicating that daemon is the real host that performs the actual reset.

| Weakness | Impact category | Confidence |
|---|---|---|
| `device_heartbeat_handle()` accepts and acks an inbound heartbeat purely on a 16-bit device-address field match, with no sequence/nonce/signature check before refreshing that target's liveness timestamp | spoofed-liveness / safety-watchdog bypass: any bus participant able to address a given target's device-address could refresh its heartbeat and suppress the timeout-driven reset callback for an actually-unresponsive subsystem | medium — missing-authentication behavior directly confirmed; whether this is practically reachable depends on message-bus-level address authenticity, not re-examined here |
| `device_heartbeat_ack()`, an exported symbol whose name implies real ack bookkeeping, is a dead 2-instruction no-op stub | dead-code / silent monitoring gap | high |
| The GPIO-reset trigger is a raw, caller-supplied C function pointer stored into a global struct at init time with minimal validation and no visible re-init guard | integrity-of-safety-callback (architectural observation — not independently exploitable from within this library alone) | low-medium |
| A watchdog helper writes diagnostic text directly to `/dev/kmsg`, bypassing the normal log pipeline used everywhere else in the binary | least-privilege / attack-surface widening (fixed format strings only — not a format-string bug) | medium |

**Not determined:** the exact `(cmd_set, cmd_id)` that ultimately
dispatches to `device_heartbeat_handle`/`_ack` (not present in this
library at all; almost certainly lives in `dji_sdrs_agent`, not
independently disassembled for this); whether `device_heartbeat_init`/
`device_monitor_init` guard against a second call.

## §19. `libDjiMediaPlayerServer.so` — media playback DUML bridge

**Role, confirmed with correction.** Both an Android Binder service
(wrapping OMX-based local playback) **and** a `dji::MediaDussEvent` class
that joins the bus as a named route-table client (`media_service`/
`media_server`) exposing `SetPlaybackSource`/`SetPlaybackControl`.
**Correction:** no `duss_event_register_dynamic_command` import, and —
critically — no internal caller of either method exists anywhere in this
`.so`'s own code (confirmed by two independent full-coverage disassembly
passes). The actual bridge that decodes a raw DUML `RX_CAMERA_PLAYBACK_
CONTROL` wire frame and invokes these methods is **not present in this
file** — it lives in a separate, unexamined process or is reached via a
callback threaded through `libduml_frwk.so`'s generic event machinery.

| Weakness | Impact category | Confidence |
|---|---|---|
| `SetPlaybackControl`'s enum-range check is **upper-bound-only** (`cmp r1,#5; ble valid`), with no corresponding `cmp r1,#0; bge` — a negative `cmd` value satisfies the check and is used as a scaled index into a fixed 6-entry/48-byte read-only lookup table | out-of-bounds read (low severity: static, read-only, single byte, feeds only a local message field forwarded over the bus — no write, no code-execution path shown from this file alone) | medium — the missing-lower-bound mechanism is confirmed; whether a genuinely negative value is reachable from real DUML traffic is unknown, since the actual wire-frame dispatcher is not in this file |

**Not determined:** where the real wire-frame-to-method dispatcher lives
(a separate "media_server" process or an indirect callback, neither
located); whether this command's numeric DUML cmd_id matches any entry
already catalogued in `ALL_COMMANDS.csv`.

## §20. `dji_cst` — Camera Seal Test engineering harness (E2)

**Role, confirmed.** A getopt-driven CLI regression-test harness for the
`cam_seal` camera subsystem on E2 — hundreds of named `cst_duss_test_*`
functions, not a production daemon. No DUML command registration
(confirmed absent, same three-way check used throughout this sweep). A
second, Android-Binder-based test backend is compiled in but every one of
its entry points is the identical 2-instruction no-op stub — inert in
this build.

| Finding | Impact category | Confidence |
|---|---|---|
| The triage's "session id verify failed" flag (originally associated with a possible "vision vs camera-push" trust boundary) is, on disassembly, a local anti-staleness consistency check inside the test harness's own pano-status push handler — a correctness check for the test tool's own scoring, not a security boundary and not related to nav-OSD handling as the triage implied | test-tool result integrity, not aircraft security — documentation correction | high |
| This CST client identifies itself to the bus purely by a fixed node-name string pair (`"camera_service"`, `"camera_test"`), with no visible per-call credential in this binary | possible name-based trust (whether the server side performs further authorization could not be determined from this file alone) | low — existence of the name-only call is high-confidence; any security implication is unconfirmed |
| 3 of 49 `system()`/`popen()` call sites were spot-checked and build commands from fixed strings/integer substitutions only; no injection pattern found in the sites examined | command injection: none found in the checked sites; the remaining 46 sites were not individually inspected | medium for the checked sites; not determined for the rest |

**Not determined:** whether `libduml_frwk.so`/the camera_service process
perform any authorization beyond the node name; full semantics of
internal looper message IDs; exhaustive audit of all 49 shell-exec sites.

## §21. `dji_http_server` — embedded media HTTP server (E2 only)

**Role, confirmed.** A genuinely forked lighttpd (confirmed via
`.gnu_debugdata` source-tree path strings matching DJI's own AOSP
`hardware/` tree) extended with a DJI media-serving layer hooked directly
into the core request pipeline (`http_response_prepare()` calls
`dji_get_file_path_by_url()` and overwrites the resolved physical path on
success). Confirmed as a **standalone network listener** — despite
listing six `libduml_*` libraries as `NEEDED`, it imports zero symbols
from any of them.

| Weakness | Impact category | Confidence |
|---|---|---|
| The media URL "v2" string API builds the served path as `root_path + "/" + rel_path` using a hardcoded **denylist** (reject if the path contains `".."`, or any of `~ $ # * :`) rather than canonicalize-then-verify-containment | path-traversal (potential) / input-validation weakness — a recognized weaker sanitization pattern | medium — the denylist design is confirmed by disassembly; no attempt was made to find or confirm an actual bypass, so exploitability is not claimed, only the weaker design |
| No TLS/SSL capability is compiled in at all (`libssl.so`/`libcrypto.so` absent from `NEEDED`; literal fallback string `'ssl support is missing, recompile with e.g. --with-openssl'`) | confidentiality / credential exposure — any auth credentials and all served media travel in cleartext at this layer | high for the absence of TLS; medium on real-world impact (no runtime config file was found to confirm which auth backend, if any, is actually active) |
| The stock lighttpd "extern" auth backend (`mod_auth_check_extern`) trusts whatever value is present in the `REMOTE_USER` env var with no verification of its origin | auth-bypass, configuration-dependent — by-design lighttpd behavior, risky only if `auth.backend=extern` is the deployed configuration | low-medium — mechanism confirmed; the actually-deployed configuration could not be found on either image |
| (Clean result) the numeric "v1" media API builds paths purely from fixed literal strings and integer formatting — no path-traversal surface by construction | none | confirmed |

**Not determined:** the actual deployed server configuration (no
lighttpd-style config file was found on either image); why six
`libduml_*` libraries are listed as `NEEDED` with zero symbols imported
from any of them.

## §22. `dji_hms` — Health Management System daemon (E2)

**Role, confirmed.** The HMS error/health-code collector: an in-memory
pool plus rolling on-disk JSON history, with callbacks for get/clear
history, OSD message relay, reboot trigger, and subscriber management.
Registers its 10 handlers via two compiled-in static function-pointer
tables passed in one call to `duss_event_create_client` (confirmed via
`.rela.dyn` relocations) — not `duss_event_register_dynamic_command`,
confirmed absent.

| Weakness | Impact category | Confidence |
|---|---|---|
| `hms_event_cb_msg_osd` computes its per-message record-processing loop count as `(len_field - 3) / 6`, where `len_field` is a 32-bit value read directly from the incoming message with **no preceding check that it is ≥ 3**. A peer sending `len_field ∈ {0,1,2}` underflows the subtraction to a huge value, producing a garbage record count and a loop that walks far past the actual message buffer | memory-safety / integer-underflow → out-of-bounds read and a long/garbage-length loop (DoS; possible further corruption depending on what the insert function does with out-of-bounds data) — reachable from any DUML peer, including on the very first packet to a never-before-seen module | medium-high: the arithmetic/control-flow is directly confirmed by disassembly; not fully confirmed whether the message-bus framework enforces a minimum payload length at a layer above this binary, which would preclude the underflow |
| `hms_event_cb_set_subscriber` accepts a subscription request (host_id, subscribe_cmd) and registers/modifies a subscriber-table entry with **no visible authorization or allow-list check** on which host_id values may subscribe — only a bound check on the command value itself | authorization gap: any bus peer able to reach this handler can register itself to receive forwarded HMS/OSD events for other modules | medium — confirmed from this binary alone that no additional check exists here; whether the bus/route-table layer restricts senders was not confirmed |
| The history-export path shells out via `system()` three times with fixed-string arguments only | defense-in-depth note, not an injection as implemented | high |

**Not determined:** the exact numeric `(cmd_set, cmd_id)` values dispatched
to each of the 10 handlers (resolved inside `duss_event_create_client`'s
implementation in `libduml_frwk.so`, not disassembled here); a
speculative, **unconfirmed** lead that the integer literal `0xFB` baked
into the registration descriptor might correspond to this project's own
documented General cmd_set `0xFB` "Selftest State" — flagged only as a
lead for a future pass on `libduml_frwk.so`, not asserted; what
`hms_event_cb_reboot` actually triggers downstream (it only acks and
flips a dump-enable flag itself).

## §23. `dji_lte` — 4G/LTE cellular-dongle transport/relay daemon (E2 only)

**Role, confirmed.** One binary running in three personalities (UAV/
GND-GLS/GND-RC) selected by config bytes, driving a multi-vendor modem HAL
(Huawei/Notion/Fibocom/generic-RIL/DJI's own Quectel-based dongle) and
relaying video/control/firmware-download traffic between a ground and air
instance. Dongle activation/authenticity gating matches the triage: a
PKCS#12 client certificate load, a signed `/data/cert.crt`+`/data/sign.in`/
`sign.out` server round-trip, and RSA wrappers (`https_client_sign`,
`https_check_private_key`) — all confirmed present and called in the
expected places, none of their internal crypto examined further (same
scope boundary already applied to `dji_sec`).

**One nuance beyond the triage note:** country-code regulatory gating is
actually **two independent mechanisms** — a purely local, client-side
blacklist (a simple `strncmp` loop over a list loaded from local JSON
config) and a separate server-returned whitelist obtained only via the
signed HTTPS exchange. The two are architecturally independent trust
boundaries and should not be conflated.

| Weakness | Impact category | Confidence |
|---|---|---|
| A USB-hotplug-derived network interface name is substituted via `%s` into two `system()`-executed shell command templates (`busybox ifconfig %s down`, `ip link set %s name %s`) with no escaping visible in the traced path | potential local command injection / availability | low — unsanitized construction confirmed; whether the interface name can ever contain shell metacharacters (depends on kernel/udev naming conventions, not raw USB descriptor text) was not traced further |
| The country-code blacklist check is enforced entirely from local, unauthenticated config data, architecturally separate from and weaker than the server-whitelist path | regulatory/geofencing integrity architecture note — not itself demonstrated bypassable | confirmed via disassembly of the blacklist check and config-parsing strings |
| An unexamined `popen()` call exists inside the function that owns the activation/whitelist-exchange (`lte_get_relay_service_info`) | undetermined — flagged for a future, separately-scoped pass | existence confirmed; content/risk not evaluated, per scope boundary |

**Not determined:** whether `duss_event_register_dynamic_command` is used
— **definitively no** (all 194 PLT stubs individually resolved, none
matches); whether log-string function names `uav_send_0401_to_gimbal`/
`uav_send_2270_to_fc` are literal cmd_set:cmd_id values or just descriptive
labels (suggestive of this project's documented `0x04`/`0x01` Gimbal
Control pairing, but not numerically confirmed); contents of three
referenced-but-unlocated config paths (`/system/etc/ca.crt`,
`/system/etc/fake.priv`, `/system/etc/rsa_public_key.pem`).

## §24. `libduml_databuffer.so` — generic multi-transport bulk data-transfer engine (E2)

**Role, confirmed with an important scope correction.** A generic
DataSender/DataReceiver/DataDownloader class hierarchy pluggable onto
many transports (TCP, UDT, USB bulk/accessory, wireless-link, and the
internal DUSS message bus). **Scope correction:** an exhaustive consumer
survey of every ELF on this E2 image found the library's **only actually
exercised** use is a purely local, in-process media-remux pipe
(`MuxBuffer_*`, gluing an OMX encoder to an AV muxer via `bin/test_remux`)
— not a network/USB bridge. The network-or-USB-receiver-to-message-bus
bridging capability is real, exported, and fully disassembled below, but
**no binary on this specific image was found calling into it**.

| Weakness | Impact category | Confidence |
|---|---|---|
| `MBusDataSender::sendData` bridges externally-received bytes directly onto the internal DUSS message bus, taking sender/receiver identity fields **verbatim from the externally-supplied bytes** (gated only by the embedded DUML v1 frame's own length/CRC16 check), with no revalidation of true origin | internal message-bus sender/route-identity spoofing primitive — real, exported capability, reachable in principle wherever some other binary (not found on this image) wires a network/USB receiver to `MBusDataSender` via this library's public factory | medium — high confidence the forwarding mechanics are real (directly disassembled); medium-low on real-world reachability on *this* image, since no actual caller was found anywhere in the exhaustively-checked E2 tree |
| The exported `DataSender::processDataCRC`/`parseData` trust the frame's own embedded length field to locate where to write the CRC, with no check against any actual destination-buffer-size parameter — but neither function has any internal caller in this `.so` | potential out-of-bounds write, entirely contingent on an unidentified external caller passing an undersized buffer | medium on the trust assumption being real; low on practical exploitability since no caller was identified |
| All receive-side transport classes (Tcp/Udt/UsbBulk/UsbAcc/WL) are confirmed thin, non-parsing byte-pipe wrappers with no framing logic of their own — correcting the triage's description of the receivers specifically | architecture correction, narrows (not widens) the receive-side semantic-parsing surface to zero | high |
| (Clean result) `MuxBuffer_write` — the one path actually exercised by a confirmed consumer on this image — correctly bounds its copy to `min(ring-buffer-free-space, requested length)` | none — no overflow found in the real production use case | high |

**Not determined:** whether any binary elsewhere in the broader WM260
firmware package (outside this E2 image's `system_files`) actually
instantiates the network/USB-to-`MBusDataSender` bridge; which external
binary, if any, calls the exported `parseData`/`processDataCRC` and what
validation it applies first.

---

# Part 4 — Consolidated findings table

Same shape as the tables in `08_...FINDINGS.md`/`09_...DEEPDIVE.md`:
every genuine weakness identified in Part 3 above, in one place. Pure
architecture-correction/negative findings and validated non-findings are
omitted here (they remain in their per-binary sections above); this table
is for things with real security weight.

| Weakness | Impact category | Confidence | Preconditions |
|---|---|---|---|
| `libdji_sec_ds_whitelist_upgrade.so`'s version-whitelist gate always returns "allowed," never checking anything | integrity / anti-downgrade bypass (inert control) | high | The one confirmed call site (`libupgrade_upgrade.so`); real-world impact depends on whether this is the only anti-downgrade check in the pipeline |
| `dji_network`'s 802.11p pairing key is derived from 4 time-seeded `rand()%26` chars + 3 hardcoded chars (~18–19 bits entropy) | weak cryptographic key generation / predictable secret | high | Attacker can bound the approximate generation time |
| `dji_network` logs the freshly-generated 802.11p key in cleartext | sensitive-data exposure via logging | high | Attacker can read the daemon's log output |
| `dji_network` falls back to the hardcoded passphrase `"12341234"` when no PSK is configured | hardcoded/weak default credential | high | Config file missing/corrupted/factory-reset state |
| `dji_ftpd`'s TEE-derived-login hypothesis is refuted — real auth is a plaintext `/etc/ftp.conf` colon-delimited credential compare, exposed across 7 flight-critical directory aliases | authentication / credential-management | high (mechanism); real severity depends on file contents/permissions, not examined | Network reachability of the FTP service |
| `libduml_payload.so`'s `dn_dev_info_parse_chnl_info`/`_data_info` trust wire-supplied repeat counts with no check against remaining buffer length | memory-safety / out-of-bounds read → DoS, possible heap-data disclosure | high | A DUML peer able to send a device-negotiation frame |
| `libduml_dn.so`'s `dn_device_info_parse()` indexes a 5-valid-slot table with an unbounded 4-bit mask, causing deterministic crashes for 6 values and a type-confusion indirect call for at least 1 (likely more) | memory corruption: crash_dos (confirmed) / indirect-call type confusion (architectural, unconfirmed exploitability) | high (mechanism and specific crash targets); not independently confirmed exploitable beyond crash | Caller must deliver an out-of-{3,4} type nibble with attacker-influenced buffer content |
| `dji_hms`'s `hms_event_cb_msg_osd` computes a record-processing loop count from `(len-3)/6` with no minimum-length check | memory-safety / integer underflow → OOB read, DoS | medium-high | Any DUML peer; framework-layer minimum-length enforcement not ruled out |
| `dji_hms`'s `hms_event_cb_set_subscriber` has no authorization/allow-list check on which host_id may subscribe | authorization gap — any reaching peer can subscribe to forwarded HMS/OSD events | medium | Bus/route-table-layer restrictions not confirmed |
| `dji_mb_ctrl` and `duss_shell` are both fully general, unauthenticated raw-DUML-message injectors shipped on the production image | missing_authz / internal command injection | high | Local shell access already required |
| `libduml_rpc.so`'s `*ack_len` out-parameter reports the full peer-supplied length even when the corresponding copy was skipped for being too large | info_disclosure / OOB-read risk in the calling daemon | high (library-side defect); caller-dependent severity | Depends on how each specific caller uses the returned length |
| `libDjiMediaPlayerServer.so`'s `SetPlaybackControl` enum check is upper-bound-only, missing a lower bound | OOB read (low severity — static, read-only table) | medium | Real-world reachability of a negative value unconfirmed (real dispatcher not in this file) |
| `dji_http_server`'s v2 media-path API uses a denylist (not canonicalize+containment) for path sanitization | path-traversal (potential) / weaker input-validation pattern | medium | No bypass found or attempted |
| `dji_http_server` has no compiled-in TLS support | confidentiality / credential exposure | high (absence confirmed) | Depends on network topology and whether auth is in use |
| `dji_sdrs_agent`'s device-identity NVRAM files are integrity-checked only by CRC16, not a crypto MAC | data-integrity / identity-spoofing | medium-high | Requires prior filesystem write access |
| `dji_sdrs_agent` automatically flashes modem firmware via `system()` on USB-hotplug VID/PID match with no cryptographic check of the attached device | automatic privileged tool invocation on weak physical-device matching | medium | USB hotplug event with matching VID/PID |
| `dji_upgrade` `dlopen()`s a JSON-config-path-supplied plugin with no signature/hash/allowlist check in this binary | unverified dynamic-library load / code execution | medium | Config file or plugin path reachable by an untrusted party (not established) |
| `libdji_fw_verify_util.so`'s `size_kb << 10` shift wraps to 0 for large `size_kb`, hanging the verify-chunking loop | denial of service (fails closed) | medium | Whether `size_kb` is ever attacker-influenced not determined |
| `libduml_databuffer.so` exports a network/USB-to-internal-bus identity bridge (`MBusDataSender`) with no origin revalidation | internal bus identity-spoofing primitive | medium (mechanism); low-medium (no caller found on this image) | Some other binary must wire a network/USB receiver to this sender — not found on E2 |
| `dji_wlm`'s device-identity serial numbers are sourced from `/proc/cmdline`, exported without further protection | local information disclosure | high (mechanism); medium (severity) | Local unprivileged process able to read `/proc/cmdline` |
| `dji_lte`'s USB-hotplug interface-rename path builds `system()` commands with an unescaped `%s` interface name | potential local command injection | low | Interface-name value space likely kernel/udev-restricted (not confirmed) |

---

# Part 5 — What wasn't pursued / scope boundary

Stated plainly, in the same spirit as `09_DJI_AUTOTEST_EXPLOITABILITY_
DEEPDIVE.md`'s closing section:

- **No exploit code, crafted packet, or attack recipe was written anywhere
  in this sweep.** Every finding above stops at "X lacks a check at Y,
  impact category Z, confidence W" — none was turned into a working
  trigger, and no finding was validated by actually sending traffic to a
  real or emulated target.
- **The OP-TEE TA command-ID dispatch tables were not reversed** (see
  `13_OPTEE_TA_FINDINGS.md`'s own scope section) — in particular, how the
  activation/AMT TA's SSD/secure-debug state machine is driven over
  `TEEC_InvokeCommand` was deliberately left unmapped.
- **37 of the 65 triaged binaries/libraries were not escalated to a full
  disassembly pass** (see the Part 1 table's "Not escalated" rows) —
  mostly media/codec/HAL plumbing with no DUML-dispatch imports and no
  flight/safety/crypto-relevant strings, per the triage's own stated
  low-priority criteria. A few medium-priority ones worth a future pass
  are flagged inline in Part 1 (`libduml_fastrtps.so` as the likely real
  network-facing RTPS parser; `librtos.so`, reached via `rtos_debug`, for
  the flight-control RTOS core's own reboot/recover/ramdump mechanism;
  `libduml_shineIO.so` for its exFAT/NVMe-passthrough parsing surface).
- **Several confirmed-real mechanisms were deliberately described, not
  attacked**, mirroring this project's existing treatment of `dji_sec`:
  `dji_verify`'s header-auth/digest checks (§9); `dji_lte`'s RSA/
  certificate activation exchange (§23); `dji_ftpd`'s secure_debug-gated
  "encryption/processing" step (§10); `check_secure_debug`'s backing
  TEE state (§12).
- **Reachability of several findings from real DUML/app traffic, as
  opposed to from a local process with existing shell/bus access, was
  often explicitly left open** rather than assumed in either direction —
  this follows `04_WM260_DAEMON_FINDINGS.md`'s established convention of
  reporting a message-bus-addressable surface honestly as "reachable by
  whatever the bus's own addressing/authentication model allows," which
  this sweep did not re-derive for each binary individually.
- **No binary outside this sweep's 28 deep-dives was given more than the
  light triage pass** — the triage table in Part 1 is the full extent of
  this project's current knowledge of the other 37 files.
