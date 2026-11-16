# Round 2 of the exhaustive sweep: 141 residual weak-signal binaries, 1 new command confirmed

This document continues directly from `16_EXHAUSTIVE_SWEEP_FINDINGS.md`
(Tracks Q-U). That pass triaged the full 808-binary universe down to 24
candidates with a *strong* relocation-based registration signal and
investigated all 24. This pass takes the next tier down: the **141**
binaries/libraries that carried only weak/ambiguous DUML-adjacent
signal (a `duml`/`duss_` string or framework link, but no confirmed
registration relocation) and were left individually uninvestigated by
round 1 — see `BINARY_COVERAGE_TRACKER.md` for the exact bucket
(`tools/triage/07_round2_weak_signal_pending_141.txt`).

**Methodology:** identical protocol to round 1 — each of the 141 targets
was investigated by an independent agent briefed on the project's known
DUML registration mechanisms and false-positive precedents, with no
access to any other agent's reasoning. Every candidate new
`(cmd_set, cmd_id)` pair was then independently re-derived from the raw
ELF by **three separate adversarial skeptic passes**, default-refuting
unless the mechanism could be reproduced from raw bytes. `libamt_util.so`
(the `e91c9402...` activation/secure-debug/DJICare TA) was not opened,
disassembled, or discussed by any of the 141 investigations beyond noting
its presence as an import where applicable, consistent with the project's
standing boundary. Static analysis only; no binary was executed; no
packet was crafted or sent; no exploit code was written.

**Bottom line:** of 141 targets, exactly **one** candidate new command
was found, and it survived adversarial reverify 3/3 (Track V). The other
140 were ruled out as true negatives — the large majority because they
link the DUML/DUSS framework (`libduml_util.so`/`libduml_frwk.so`/
`libduml_hal.so`/`libduml_osal.so`) purely for generic logging/OSAL
utility calls without importing any of the three known registration APIs,
or because a relocated `.data` array that superficially resembles the
mechanism-#3 `{function_pointer, cmd_word}` command table turned out, on
resolving what the pointers actually point to, to be an ordinary C++
vtable, RTTI/unwinder table, FSM/lifecycle table, or similar
compiler/framework artifact (Track Y). A meaningful minority yielded real,
independent architecture/security findings unrelated to DUML registration
(Track X).

---

## Track V — One new DUML command confirmed: `0x04`/`0x51`

| New pair | Name | Source binary | Mechanism | Reverify |
|---|---|---|---|---|
| `0x04`/`0x51` | Gimbal Calibration Result Query | `at_gimbalcali.so` | 4th mechanism — `imss_link_v1_send` (see Track W) | 3/3 not refuted |

`commands.json`/`ALL_COMMANDS.csv` move from 898 to **899** entries; the
full-decode count (157) is unchanged (name/mechanism-confirmed only, no
byte-level payload layout recovered). Full writeup, with the exact call
site and cross-validation evidence, is in `cmdset_04_Gimbal.md`.

The handler (`gc_v1_gimbal_api_query_cali_result`) sends no request
payload and copies up to 99 raw response bytes into a caller-supplied
buffer via `memcpy` on success, with no length/format validation beyond
the fixed 99-byte cap visible in the immediate call path —
**missing-validation, confidence low-medium** (minor; the cap itself
bounds the obvious overflow, and the response's actual format/trust
level was not independently established).

---

## Track W — A 4th client-side DUML send mechanism: `imss_link_v1_send`

`at_gimbalcali.so` and `at_v1trigger.so` (two of a 16-member family of
`at_*.so` "automated test" / factory-calibration plugin libraries living
in the same `system_files/lib` directory) implement none of this
project's three previously-documented registration mechanisms, but
directly construct and send real wire-level DUML v1 traffic via a
**4th, distinct client-side pattern**: a call to the imported
`imss_link_v1_send(cmd_set, cmd_id, ...)` (from `libimss.so`), with
`cmd_set`/`cmd_id` loaded as literal immediates into `r0`/`r1`
immediately before each `blx` site — structurally parallel to mechanism
#1's calling convention, but reached through a completely separate
transport (`libimss.so`'s private "AT link" framework, not the DUSS
event bus `libduml_frwk.so` hosts) with its own registration/callback
API (`imss_link_register_v1_callback`, `imss_link_register_v1_callback_full`,
`imss_link_register_sdk_callback`, `imss_link_sdk_send`).

This matters for future sweeps: a binary can carry real
`(cmd_set, cmd_id)` wire traffic with **zero footprint** in any of the
three mechanisms `BINARY_COVERAGE_TRACKER.md` previously listed, if it
goes through this transport instead. 12 of the 16 `at_*.so` sibling
family are built against this same private framework. `at_gimbalcali.so`
alone has 8 call sites through it; 7 reproduce already-catalogued
`(cmd_set, cmd_id)` pairs exactly matching their enclosing function's own
name/semantics (e.g. `gc_v1_camera_api_set_camera_focus_mode` →
`0x02`/`0x24` "Focus Mode Set"; `gc_gimbal_send_cali_command` →
`0x04`/`0x08` "Gimbal Calibration") — independent cross-validation of the
`r0`=cmd_set/`r1`=cmd_id convention for this call, which is what makes
the 8th (Track V's new command) credible despite the novel transport.
`BINARY_COVERAGE_TRACKER.md` has been updated to a 4-mechanism list.

A separate, structurally different API in the same family,
`imss_link_register_sdk_callback`, takes a single scalar ID and a
callback pointer with no second cmd_id-shaped argument — a distinct
internal "SDK callback" numbering namespace inside `imss_link` that must
not be conflated with the cmd_set/cmd_id convention above
(taxonomy-caution, medium confidence, single-instance observation).

No secure_debug/`/proc/cmdline` gating logic was found inside
`at_gimbalcali.so` itself (unlike the project's `app_echo` precedent),
but no other ELF in this firmware has a `DT_NEEDED` entry for it, and its
plugin-loader host (`dji_autotest`/`dji_autotest_on.sh`/
`switch_autotest.sh`) was out of this pass's scope — whether invocation
is gated is an unconfirmed scope gap, not a finding about this binary's
own code.

---

## Track X — Real architecture/security findings (not DUML, or DUML-adjacent)

None of these touch DUML command registration, but several are genuine,
independent findings worth recording in vulnerability-research style —
name the weakness, impact category, confidence. No exploit code or
crafted payload was produced for any of them.

| Binary | Finding | Impact category | Confidence |
|---|---|---|---|
| `file_transfer` | `main()` builds a shell command from unsanitized `argv`-derived path components (`system("rm %s%s", ...)`-shaped) with no metacharacter escaping. Real-world exploitability depends entirely on what invokes this CLI and with what arguments — out of this pass's scope. | command-injection-shaped primitive | medium |
| `libdcam_audio_frwk.so` (ARM32 only) | A device-local TSF config key (`audio/main_mic_cap_route_sh`), read via `tsf_get_string()`, is passed directly to `system()` immediately before opening the main-microphone ALSA PCM device, with no sanitization in this binary. Exploitability depends on who can set that config key. | potential-command-injection-primitive (config-driven) | medium |
| `libupgrade_product.so` | `package_compare()` (reached from the remote-storage-upgrade path) builds shell command lines with `snprintf` and runs them via `system()`/`popen()`, including a hardcoded root-identity FTP pull (`busybox ftpget -v -u root 192.168.2.3 ...`) with no visible authentication argument. Full taint-tracing of the substituted values to their ultimate source (sibling upgrade-negotiation libraries) was out of scope. | insecure IPC / command-construction, cleartext unauthenticated-looking control-plane traffic | medium |
| `libOmxVideoPyramidGen.so` | The vendor `OMX_SetConfig` handler for a proprietary 3D-LUT config index takes a caller-supplied file path and passes it directly into `fopen()`/`fread()` with no path normalization, allow-listing, or canonicalization. Remote/DUML reachability of the IL call itself (who feeds this library) was not traced — out of scope. | input-validation weakness / local arbitrary-file-read if reachable | low-to-medium |
| `test_dsp2` | Opens `/dev/mem` and `mmap`s physical I/O register space for a CLI-driven register read/modify/write (i2c-id, slave address, register address, value, write-enable all taken as unvalidated CLI args). Real-world reachability depends on who can already invoke this binary (likely requires root, as `/dev/mem` access normally does). | access-control-gap / direct-physical-memory-access diagnostic tool in production image | high (capability) / low (reachability, undetermined) |
| `test_v2d` | Opens the raw hardware device `/dev/dji_v2d` and the ION allocator `/dev/ion` directly from a plain userspace CLI, with no credential/capability/token check visible in the binary itself before issuing hardware scale commands. Device-node filesystem permissions were not inspected. | access-control-gap (informational; depends on unchecked device-node permissions) | medium |
| `test_c2d` | Accepts an unauthenticated local free-text command line, parsed with plain `atoi()`, passed straight through to kernel 2D-compositor driver calls with no bounds-check logic in this binary's own code. | access-control / local-attack-surface | medium |
| `c2d_ut` | Root-owned diagnostic/stress-test CLI that opens the 2D hardware accelerator device node and ION allocator directly, bypassing any DUML/application-layer mediation. | attack-surface inventory (informational) | high |
| `usb_bulk_xfer_test_v2` | Local-shell USB stress/diagnostic utility (host and device/gadget modes) performing raw reads/writes over USB with only shallow bounds checking, shipped as a standalone production executable. | attack-surface / diagnostic-tool-in-production | medium (low severity) |
| `test_wl_venc` | Vendor test/diagnostic CLI that can drive the hardware video encoder and open a "wireless link" test transport against raw device nodes, with bitrate/resolution/codec/GDR parameters fully attacker-controllable via CLI flags. | attack-surface / debug-tooling-in-production | medium |
| `testWlSinkUsbBulk` | Manual bench-test CLI for the encode→wireless-sink→USB-bulk pipeline, giving local shell access a ready-made entry point to drive the production OMX/venc/ION HAL stack with attacker-chosen raw video files. | attack-surface / debug-tooling-in-production | medium (low standalone severity) |
| `libcam_util.so` | `osd_bitmap_rct()` (both builds) dumps raw OSD bitmap pixel data to a fixed, predictable debug path on `/data` via `fopen`/`fwrite`, with no permission/gating check in the immediate call path. | debug-surface / information-disclosure | medium |
| `libdcam_observer.so` | A property-gated raw camera-frame-dump debug feature is present and reachable from the production `on_frame` path. | information-disclosure / debug-surface-in-production | medium |
| `libdcam_audiodev.so` | This "stripped" shared library still ships a complete recoverable local symbol table via an embedded `.gnu_debugdata` (GNU MiniDebugInfo) section, largely defeating the stripping. | information-disclosure / methodology-note | high |
| `libdcam_scap1_capeng.so` | An embedded, unstripped assertion string leaks the internal build source-tree path and naming convention for DJI's camera capture-strategy plugin architecture. | information-disclosure (low severity) | high |
| `omx_camcapeng_source_test` | Shipped world-readable/executable, root-owned, production-image GoogleTest binary retaining its full test-harness surface including network result-streaming (`--gtest_stream_result_to=HOST:PORT`) and a fork/exec-capable death-test path — a debug/test surface left in production, similar in kind to doc 16's `test_dji_blackbox` finding. | information-disclosure / debug-surface-in-production | medium |
| `dji_media_play_service_test`, `omx_converter_test`, `stress_test_osal_msgq`, `test_imgtec_venc`, `test_flight_lite`, `test_disp` | Further instances of the "debug/QA/stress-test executable shipped as a regular, world-executable production binary" pattern doc 16 already flagged for `test_dji_blackbox`/`stress_test_mb_family`/`upgrade_test_family` — none with a DUML role; several have no visible access-control gate at all (`test_flight_lite` has none, unlike the `app_echo` precedent, and unconditionally opens raw AP↔MCU ICC device nodes once invoked). | debug-tooling-in-production | medium (one binary's exact `system()` call site, `test_disp`, could not be fully traced in bounded effort — recorded as low-confidence/informational, not a claimed path) |
| `libdcam_disp_wm260.so`, `libdcam_iq_tplgy_util.so`, `libdcam_meta_convert.so`, `libdcam_pp_mee_ebh.so`, `libdcam_pp_raw_stack_15.so`, `libdcam_pp_yuv_fusion_20.so`, `libdcam_shooter_raw_reprocess.so`, `libdcam_subscribe.so`, `libdcam_tino_ceva.so` | A recurring crash-only error-handling pattern across the camera-pipeline plugin family: malformed/unexpected *internal* metadata (produced by other camera-pipeline components, not DUML wire input) hits an assert-style check and the plugin calls `exit(1)`/`abort()`, taking down the whole hosting camera process rather than failing gracefully. None of these paths were shown to be reachable from DUML/network input in this pass — informational, not a demonstrated vulnerability. | availability / robustness (informational, internal-input-only in every case checked) | low |
| `libdcam_blur_stream_filter.so`, `libdcam_camdev.so`, `libdcam_dewarp_gdc_stitching.so`, `libdcam_mctf.so`, `libdcam_pp_sisr_strategy.so`, `libdcam_shooter_base_still.so`, `libdcam_shooter_video_multi.so` | Each registers runtime debug toggles through the internal `dcam_dbg_option_register_by_gid`/`dcam_dbg_option_value_register` camera-debug framework (small integer "debug group id" + registration call) — structurally similar-looking to DUML's `(cmd_set, cmd_id)` space but a completely separate, non-wire-level namespace. Flagged repeatedly across this family to pre-empt the exact conflation this project's boundary rules warn about in any future scan. | namespace-disambiguation (not a vulnerability) | high |

---

## Track Y — New false-positive-disambiguation precedents (methodology notes)

The large majority of the 140 ruled-out targets were true negatives for
one of two already-documented reasons (links the DUML framework for
logging/OSAL only; or a relocated array that isn't mechanism #3 after
resolving its pointer targets) — not enumerated individually here, since
`BINARY_COVERAGE_TRACKER.md` already states both patterns and doc 16
already established the precedent. A few **new concrete shapes** for the
second pattern are worth recording as precedents for future scans,
alongside the GoogleTest-vtable and FSM-table false positives doc 16
already flagged:

- **OMX/IL plugin-registration tables** (`libOmxProresDec.so`'s
  `getComponentFactory()` → `std::vector<{name, factory_fn}>`) — table-shaped,
  but a documented, unrelated plugin convention.
- **Statically-linked C++ unwinder/EHABI vtables**
  (`libdcam_hyperlapse_ae_ceva.so`) and **RTTI/locale-facet data**
  (`libOmxPlayer.so`) — same relocated-array shape, resolves into
  `.rodata`/unwind metadata, never into callable `.text`.
- **Internal lifecycle/stream-metadata enum tables**
  (`libdcam_frwk.so`'s two genuine 8-byte-row relocated tables, whose
  pointers resolve to stream-port-name and stream-lifecycle-message
  strings with non-byte-range tag values) and **per-DSP-device descriptor
  tables** (`dji_dsp_load`).
- **V4L2 pixel-format name-string tables** (`libdcam_iq_tplgy_util.so`).
- A real **architecture-divergence data point**: `libcam_util.so`'s
  OSD-class vtable exists only in the ARM32 (E1E) build; the aarch64 (E2)
  build of the same library has no equivalent structure at all — a
  reminder that a relocated-array false positive can be
  build-specific, not a property of the library's logical design.

None of these were close calls on the merits (every one was confirmed by
tracing where the resolved pointers actually land, not by shape alone),
but cataloguing the shapes makes the next mechanical pre-triage faster to
disambiguate without re-deriving each from scratch.

---

## Track Z — Completeness statement

Of this round's **141** targets: **141 investigated**, **1** new command
confirmed and catalogued (Track V, 3/3 reverify), **0** credible-but-unconfirmed
leads left on the table (unlike round 1's `0x00`/`0x84`), and **140**
ruled out as true negatives for DUML command registration — of which
roughly a third yielded an independent, non-DUML architecture or security
finding worth recording (Track X), and the remainder confirmed one of the
two already-known true-negative shapes (Track Y). No investigation this
round was interrupted by a safety-filter false positive. No investigation
opened, disassembled, or discussed `libamt_util.so` beyond noting its
absence or presence as a plain import. No exploit code, crafted packet,
or forged-token material was produced.

Combined with round 1 (doc 16) and the pre-existing 57+591 already
accounted for, this closes out the full **808**-binary universe's
"weak/ambiguous signal" bucket entirely. The only remaining,
lower-priority gap is the 50-binary "socket-bearing, no detected signal,
not individually investigated" tail noted in `BINARY_COVERAGE_TRACKER.md`
— out of scope for this pass.
