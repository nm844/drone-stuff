# Binary coverage tracker

This is a living reference, not a findings document: it records the
methodology and current disposition of every binary/shared-library across
both WM260 firmware images (`e1e_extracted`, `e2_extracted`) with respect
to the DUML command surface, so future passes don't have to reconstruct
the triage from scratch or re-derive numbers that already drifted once.
Findings themselves live in the numbered `*_FINDINGS.md` docs; this file
only tracks *what has and hasn't been looked at, and how to look*.

Update this file (don't just leave the fact in a chat transcript or `/tmp`)
whenever a new sweep changes the disposition of any binary. The raw list
files this doc references are committed under `tools/triage/` — treat
`/tmp` and any session scratchpad as **ephemeral**; nothing durable should
live only there.

## The four known DUML command-registration/send mechanisms

Every investigation in this project checks a binary for these four,
using `readelf`/`objdump`/`capstone`/`pyelftools` — not string greps alone:

1. **Direct registration call.** A call to the imported function
   `duss_event_register_dynamic_command(cmd_set, cmd_id, handler_fn, ...)`,
   with `cmd_set`/`cmd_id` loaded as literal immediates into registers
   immediately before the `bl`/`blx` (ARM32: `r0`-`r3`; aarch64: `x0`-`x3`).
2. **Named route/client idiom.** `duss_mb_create_route_table(...)` followed
   by `duss_event_create_client(...)`. This does **not** necessarily
   register a specific `(cmd_set, cmd_id)` — see the `app_echo` writeup in
   `16_EXHAUSTIVE_SWEEP_FINDINGS.md` (Track Q) for a worked example of a
   binary that uses this idiom but registers zero commands (the route id
   passed to `create_client` is a dynamically-assigned out-parameter, not a
   literal, and no handler function pointer is ever passed). Always check
   whether the call site actually wires up a per-command handler before
   calling this a real command registration.
3. **Relocated command-dispatch array.** An `R_ARM_RELATIVE`/
   `R_AARCH64_RELATIVE`-relocated `.data` array of 8-byte
   `{function_pointer, cmd_word}` rows (`cmd_word` low byte = `cmd_set`,
   high byte = `cmd_id`) — the `dji_flight` vaddr `0xae0f8` precedent, and
   independently reconfirmed in two different binaries for the new `0x23`
   "Smart" cmd_set. **Caveat**: a repeating relocated-pointer array can
   also be a compiler-generated C++/unwinder function-pointer table (same
   shape, unrelated purpose) — confirmed as a false lead once, on
   `app_echo`'s ARM32 build, and several more times in round 2 (C++
   vtables, RTTI/locale-facet data, EHABI unwinder tables, FSM/lifecycle
   enum tables, V4L2 format-name tables — see
   `17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md` Track Y for the specific shapes).
   Always check where the resolved pointers actually point before calling
   this a command table.
4. **Direct client-side send via a private link framework.** A call to an
   imported `*_v1_send(cmd_set, cmd_id, ...)`-style function from a
   framework *other than* `libduml_frwk.so`'s DUSS event bus — confirmed
   via `imss_link_v1_send` (from `libimss.so`) in two `at_*.so` factory
   test/calibration plugins, with `cmd_set`/`cmd_id` loaded as literal
   immediates into `r0`/`r1` immediately before the call, structurally
   parallel to mechanism #1's calling convention but reached through a
   wholly separate transport and registration/callback API
   (`imss_link_register_v1_callback`/`imss_link_register_sdk_callback`).
   See `17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md` Track W. A binary can carry
   real wire-level DUML traffic with zero footprint in mechanisms #1-#3 if
   it goes through a private transport like this one — don't conclude "no
   registration signal" from those three alone without also checking for
   imported `*_send`/`*_link_send`-shaped functions called with small
   literal immediates.

## Tooling gotcha: `readelf -r` truncates on 32-bit ARM

`readelf -r` (narrow/default output) silently truncates the `Sym. Name`
column on 32-bit ARM binaries, producing **false negatives** when
grep-matching relocation target names — this cost one full round of
mechanical triage before being caught (sanity-checked against known
positives `dji_sys`/`dji_flight`, which both initially showed 0 matches).
**Always use `readelf -rW`** (wide) on 32-bit ARM. aarch64 (`e2_extracted`)
binaries are not affected, but use `-rW` everywhere for consistency.

## Known data-quality caveat: `comm -23` basename leakage

Several of this tracker's intermediate sets were built with
`comm -23 fileA fileB` to subtract one basename list from another. `comm`
requires both inputs to be identically sorted (byte-collation), and a
mismatch silently leaks entries through rather than erroring. This was
caught twice:

- The original 591-binary "no signal" set (`03_no_signal_basenames_591.txt`)
  leaked a handful of already-DUML-touching names (e.g. `dji_sys`,
  `libduml_frwk.so`) that should have been excluded. It didn't change any
  conclusion (the leaked names were already covered elsewhere and easy to
  recognize as such), but don't trust this file as a clean negative set
  without cross-checking against `04_duml_signal_basenames_217.txt` and
  `02_covered_basenames_57.txt` first.
- The 109-path "no-signal-with-a-socket" candidate pool leaked **16**
  already-covered/DUML-touching basenames (`dji_blackbox`,
  `dji_http_server`, `dji_lte`, `dji_network`, `dji_rcam`,
  `dji_sdrs_agent`, `dji_sys`, `dji_wlm`, `libdcam_cs_duss_proxy.so`,
  `libduml_databuffer.so`, `libduml_dsocket.so`, `libduml_fastrtps.so`,
  `libduml_frwk.so`, `libduml_util.so`, `libv2_sdk.so`,
  `test_imgtec_venc_new`). This has been corrected; see
  `08_socket_bearing_no_signal_corrected_58.txt` below. **Before reusing
  any list in this directory for a new sweep, re-derive the subtraction
  with `comm -12`/`comm -23` on freshly `sort -u`'d inputs, or use
  `grep -Fxf` instead of `comm`, and re-check against the covered/signal
  lists** — don't assume a previous "no signal" list is still accurate
  once new binaries get documented elsewhere.
- Separately: `02_covered_basenames_57.txt` is a best-effort list of
  binaries with their **own** heading/section in a findings doc. Some
  libraries get examined only as a *side-mention inside another binary's
  section* (e.g. `libduml_orte.so`, examined as part of `dji_sys` in
  `15_SECOND_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track I) and so won't appear
  in `02_` even though they're genuinely covered. A quick
  `grep -rl <name> DUML_PROTOCOL/*.md` is a cheap sanity check before
  spending effort re-investigating something that looks "uncovered."

## How to regenerate the triage from scratch

```bash
FW=/home/user/wm260_fw/decrypted   # e1e_extracted/ and e2_extracted/ live here

# 1. Enumerate every binary/library across both images, deduplicated by basename.
find "$FW"/e1e_extracted "$FW"/e2_extracted -type f \( -perm -u+x -o -name '*.so' \) \
  -exec basename {} \; | sort -u > all_basenames.txt   # -> 01_all_basenames_808.txt

# 2. Which basenames already have a section in an existing findings doc?
#    (best-effort grep against DUML_PROTOCOL/*.md headings; hand-verify)

# 3. Which basenames reference any DUML/DUSS-adjacent string or symbol at all?
#    e.g. grep -l -e duss_ -e duml -e DUML (strings + readelf -sW) across every binary
#    -> 04_duml_signal_basenames_217.txt; subtract the covered set -> 05_ (160, "weak signal")

# 4. Of the weak-signal set, which have a REAL relocation into a registration
#    function? Use readelf -rW (not -r) against duss_event_register_dynamic_command /
#    duss_mb_create_route_table / duss_event_create_client -- AND check imports for
#    a private-transport send function (e.g. imss_link_v1_send) called with small
#    literal immediates, per mechanism #4. Sanity-check the method against known
#    positives (dji_sys, dji_flight) before trusting a zero result.
#    -> strong_candidates (became round 1's 16 tier-1 units, 19 basenames)

# 5. Of the 591 "no signal" binaries, which have their own listening socket
#    (grep for socket()/bind()/listen() imports, or netstat-style static analysis)?
#    Cross-check the result against steps 2-3's outputs before trusting it as
#    genuinely signal-free (see the comm -23 caveat above).
#    -> 08_socket_bearing_no_signal_corrected_58.txt
```

No single script currently runs all of this end-to-end — it was done as a
sequence of ad hoc shell commands across several sessions. If this
triage needs to be redone for a future firmware version, write a real
script rather than repeating the ad hoc version; `tools/` is the right
place for it.

### Reusable sweep templates

`tools/workflows/round1_tier1_tier2_sweep.js`,
`tools/workflows/round2_residual_weak_signal_sweep.js`, and
`tools/workflows/round3_tail46_sweep.js` are the actual Claude Code
`Workflow`-tool scripts used for rounds 1-3 above (two phases: `Investigate`
each target with a structured-output schema, then adversarially 3-way
reverify any `new_command_candidates` before trusting one). They're kept
here as working templates for a future round (e.g. the 4 binaries pulled
out of round 3's scope, or a new firmware version's binary set) — copy one,
swap in a new target list and `BASE` path, and re-launch rather than
re-deriving the prompt structure from scratch.

## Current disposition (as of `17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md`)

Of the full **808** binaries/libraries:

| Bucket | Count | Status | List file |
|---|---|---|---|
| Already documented (own section in a findings doc) | 57 | done | `02_covered_basenames_57.txt` |
| No DUML/DUSS signal at all | 591 | ruled out on signal absence | `03_no_signal_basenames_591.txt` |
| ↳ of which, has its own listening socket (corrected) | 58 | see sub-rows below | `08_socket_bearing_no_signal_corrected_58.txt` |
| ↳↳ investigated as round-1 "tier 2" | 8 | **done** — all ruled out, several independent security findings (doc 16, Track T) | `09_round1_tier2_investigated_8.txt` |
| ↳↳ remaining, generic-tooling-by-name, not individually investigated | 50 | **46/50 done (round 3)** — all 46 ruled out for DUML command registration (43 confirmed stock/vendor/AOSP, plus `libwlm.so`/`libduml_hal.so` confirmed as real DJI infrastructure but not command handlers); `liblte.so` was the one surprise — not stock, and identified as a genuinely new DUML transport-channel backend (doc 19, Track AA) despite registering no commands itself. Several independent security findings (doc 19, Track AB). The other 4 (`libupgrade_common.so`, `Quectel_upgrade_tool`, `quectel-qmi-proxy`, `libduml_orte.so`) are tracked under the firmware-update sweep / doc 15 respectively, not here. | `10_socket_bearing_no_signal_remaining_50.txt` |
| Weak/ambiguous DUML-adjacent signal, no doc coverage | 160 | see sub-rows below | `05_weak_signal_uninvestigated_at_start_160.txt` |
| ↳ confirmed real relocation into a registration function ("tier 1") | 19 basenames / 16 investigation units | **done** (round 1) — 10 new commands confirmed + 1 unconfirmed lead (doc 16, Track R) | `06_round1_tier1_investigated_19.txt` |
| ↳ remaining, weak/ambiguous signal only | 141 | **done** (round 2) — 1 new command confirmed (`0x04`/`0x51`, via a newly-identified 4th mechanism) + 140 ruled out, several independent security findings (doc 17, Tracks V-Y) | `07_round2_weak_signal_pending_141.txt` |

**Fully accounted for right now: 57 + 591 + 19 + 141 = 808 of 808** — the
entire "weak/ambiguous signal" bucket is now closed.
**Flagged-but-not-individually-checked: 50** (socket-bearing, no detected
signal — lower priority, see above; the only remaining gap in the full
808-binary universe).

## Round history

- **Doc 12** (`12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md`): the original
  pre-triage sweep, 65 binaries triaged + 24 deep-dived. Predates the
  808-binary full-universe accounting in this tracker; its targets are
  folded into the 57 "already documented" above.
- **Docs 14/15** (`14_FOLLOWUP_DEEPDIVE_FINDINGS.md`,
  `15_SECOND_FOLLOWUP_DEEPDIVE_FINDINGS.md`): further rounds of deep-dive
  on specific binaries/subsystems, also folded into the 57.
- **Doc 16** (`16_EXHAUSTIVE_SWEEP_FINDINGS.md`, Tracks Q-U): round 1 of
  this tracker's methodology — the 16 tier-1 + 8 tier-2 candidates above.
  Registry grew 888 → 898 (10 new commands, including the new `0x23`
  cmd_set).
- **Round 2** (`17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md`, Tracks V-Z): the
  141 remaining weak-signal binaries, all investigated. One new command
  confirmed (`0x04`/`0x51` "Gimbal Calibration Result Query", in
  `at_gimbalcali.so`) via a newly-identified 4th registration/send
  mechanism (`imss_link_v1_send`, a private client-side transport
  distinct from the DUSS event bus — see the four-mechanism list above).
  Registry grew 898 → 899. The other 140 were ruled out, with several
  independent architecture/security findings (command-injection-shaped
  primitives in `file_transfer`/`libdcam_audio_frwk.so`/
  `libupgrade_product.so`; several diagnostic CLIs with direct raw
  hardware-device access shipped in production; a path-traversal-shaped
  weakness in `libOmxVideoPyramidGen.so`) and new false-positive
  precedents for the mechanism-#3 relocated-array shape (OMX
  plugin-registration tables, C++ unwinder/RTTI data, internal
  lifecycle/stream-metadata enum tables, V4L2 format-name tables).
- **Round 3** (`19_ROUND3_TAIL46_SWEEP_FINDINGS.md`, Tracks AA-AC): the
  46-of-50 slice of the tail bucket pulled out for direct investigation
  (see "What's genuinely still open after round 2" below for the other
  4). Zero new DUML commands (none of the 46 implement any of the four
  known mechanisms), but `liblte.so` turned out to be real,
  previously-undocumented DJI transport code — the LTE/cellular-relay
  backend for a DUML message-bus channel, parallel to the USB and WLM
  (`libwlm.so`) channels, cloud-relayed via `relay.djigate.com`/
  `relay-service.djicdn.com` — even though it registers no commands of
  its own. 43 of the 46 were confirmed stock/vendor/AOSP tooling with no
  DJI logic at all. Independent findings include a bundled `libsrt.so`
  (v1.4.1) carrying two real, publicly-disclosed CVEs fixed only in
  1.5.6 (CVE-2026-55869 stack buffer overflow, CVE-2026-55868 encryption
  downgrade — verified against public records during digestion, not
  just taken on the investigating subagent's word), an unauthenticated
  local IPC socket pattern in `libwlm.so`, a DJI-added undocumented
  `vold` sub-command namespace, and several further old-bundled-OSS-
  version findings in the same vein as doc 17 Track X.

## What's genuinely still open after round 2

- The 50-binary "socket-bearing, no detected signal, not individually
  investigated" tail above — flag it again rather than silently dropping
  it, and consider at least checking the handful of DJI/vendor-named
  libraries in it named explicitly above. **Round 3, launched 2026-11-17**
  (`tools/workflows/round3_tail46_sweep.js`), covered 46 of the 50 — see
  "Round history" above for the result — the other 4
  (`libupgrade_common.so`, `Quectel_upgrade_tool`, `quectel-qmi-proxy`,
  `libduml_orte.so`) were pulled out: the first three fall under the
  firmware-update-process sweep below instead, and the fourth turned out
  to already be covered as a side-mention in
  `15_SECOND_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track I despite not appearing
  in `02_covered_basenames_57.txt` — another instance of that list's
  known incompleteness caveat earlier in this doc. **The 46-binary slice
  is now closed** (doc 19); only the 4 redirected binaries remain open,
  tracked under the firmware-update sweep / doc 15.
- Any firmware version newer than what's currently decrypted/extracted
  here (e.g. the `V01.00.1500` package referenced from the unrelated
  `nimrasol_wm260` repo) is out of scope for this tracker entirely — it's
  a different firmware revision, not part of this 808-binary universe.

## Authorization change (2026-11-17): `libamt_util.so`/activation TA exclusion lifted

The project owner explicitly lifted the standing exclusion on
`libamt_util.so` and the `e91c9402` activation/secure-debug/DJICare OP-TEE
TA (previously: never opened, disassembled, or command-mapped absent
separate explicit authorization — honored consistently across docs 05, 09,
12, 13, 14, 15, 16, and 17; see `13_OPTEE_TA_FINDINGS.md`'s own
"Authorization change" note). This is now authorized, for this and all
future work in this project. **This did not lift the project's other
standing rule**, which was separately asked about and explicitly declined:
no working exploit code, no crafted attack packets, no forged
authorization/activation/DJICare tokens or signatures, no cryptanalysis of
any live cryptographic mechanism. That rule remains in force exactly as
before — command-ID/architecture mapping is in scope for this TA exactly
as it already was for the other three OP-TEE TAs; breaking or forging
anything is not, and never was, regardless of whose device is involved
(the mechanisms gated behind this TA — geofence/NFZ enforcement and
anti-theft/activation — protect interests beyond the device owner's own,
so a working bypass doesn't stay scoped to "one consenting owner" even
when requested in that framing). Three sweeps launched the same day:
`wf_activation_ta` (→ `18_ACTIVATION_TA_FINDINGS.md`, pending), `wf_firmware_update`
(→ a new firmware-update-process findings doc, pending), and `wf_tail46_sweep`
(→ `19_ROUND3_TAIL46_SWEEP_FINDINGS.md`, **done** — see "Round history" above).
