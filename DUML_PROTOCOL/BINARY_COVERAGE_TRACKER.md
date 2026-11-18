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
`tools/workflows/round2_residual_weak_signal_sweep.js`,
`tools/workflows/round3_tail46_sweep.js`,
`tools/workflows/firmware_update_process_sweep.js`, and
`tools/workflows/activation_ta_command_mapping_sweep.js` are the actual
Claude Code `Workflow`-tool scripts used for the rounds/sweeps above (two
phases: `Investigate` each target with a structured-output schema, then
adversarially 3-way reverify any `new_command_candidates` before trusting
one). They're kept here as working templates for a future round (e.g. a
new firmware version's binary set, or a targeted follow-up like the
`0x18`/`0x3D` verification gap noted below) — copy one, swap in a new
target list and `BASE` path, and re-launch rather than re-deriving the
prompt structure from scratch.

## Current disposition (as of `17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md`)

Of the full **808** binaries/libraries:

| Bucket | Count | Status | List file |
|---|---|---|---|
| Already documented (own section in a findings doc) | 57 | done | `02_covered_basenames_57.txt` |
| No DUML/DUSS signal at all | 591 | ruled out on signal absence | `03_no_signal_basenames_591.txt` |
| ↳ of which, has its own listening socket (corrected) | 58 | see sub-rows below | `08_socket_bearing_no_signal_corrected_58.txt` |
| ↳↳ investigated as round-1 "tier 2" | 8 | **done** — all ruled out, several independent security findings (doc 16, Track T) | `09_round1_tier2_investigated_8.txt` |
| ↳↳ remaining, generic-tooling-by-name, not individually investigated | 50 | **50/50 done** — 46 via round 3 (all ruled out for DUML command registration: 43 confirmed stock/vendor/AOSP, plus `libwlm.so`/`libduml_hal.so` confirmed as real DJI infrastructure but not command handlers; `liblte.so` was the one surprise — not stock, identified as a genuinely new DUML transport-channel backend, doc 19 Track AA). The other 4: `libduml_orte.so` was already covered as a side-mention elsewhere (doc 15 Track I); `libupgrade_common.so` and `Quectel_upgrade_tool` were ruled out for DUML registration by the firmware-update-process sweep (doc 20); `quectel-qmi-proxy` was ruled unrelated to firmware update entirely by that same sweep (a QMI control-plane proxy, zero upgrade strings). | `10_socket_bearing_no_signal_remaining_50.txt` |
| Weak/ambiguous DUML-adjacent signal, no doc coverage | 160 | see sub-rows below | `05_weak_signal_uninvestigated_at_start_160.txt` |
| ↳ confirmed real relocation into a registration function ("tier 1") | 19 basenames / 16 investigation units | **done** (round 1) — 10 new commands confirmed + 1 unconfirmed lead (doc 16, Track R) | `06_round1_tier1_investigated_19.txt` |
| ↳ remaining, weak/ambiguous signal only | 141 | **done** (round 2) — 1 new command confirmed (`0x04`/`0x51`, via a newly-identified 4th mechanism) + 140 ruled out, several independent security findings (doc 17, Tracks V-Y) | `07_round2_weak_signal_pending_141.txt` |

**Fully accounted for right now: 57 + 591 + 19 + 141 = 808 of 808** — the
entire "weak/ambiguous signal" bucket is now closed, **and** the
previously-"flagged but not individually checked" 50-binary
socket-bearing tail (a sub-slice of the 591 "no signal" bucket, not an
addition to the 808 total) is now also fully closed — see the row above
and "Round history" below. There is no remaining unexamined binary in
the full 808-binary universe as of doc 20.

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
- **Firmware-update-process sweep** (`20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md`,
  Tracks BA-BF): a dedicated end-to-end investigation of the
  firmware-update/upgrade subsystem (verification chain, A/B OTA engine,
  orchestration layer, PKCS7-signing side-channel, modem-update chain),
  launched the same day as the activation-TA authorization change. 1 new
  command confirmed (`0x00`/`0x5B` "FTP Control", registry grows
  899 → **900**), 5 previously-unresolved command IDs
  (`0x07`/`0x08`/`0x09`/`0x0A`/`0x41`) independently confirmed live from
  the sender side, and 1 candidate found and refuted (`0x01`/`0x78`). A
  further candidate (`0x18`/`0x3D`) initially fell out of this round's own
  verify pipeline due to a filter bug — see "Targeted follow-up" below for
  its resolution (registry now at **901**). The A/B-OTA architectural
  question is
  definitively resolved: genuinely wired up, not vestigial, fully traced
  end-to-end. Also closes out the last 3 of round 3's 4 redirected tail
  binaries (see the row above). Independent security findings include a
  broken retry-loop and a TOCTOU-shaped pattern in `dji_fw_verify`'s core
  verify function, a second (`popen()`-based, command-injection-shaped)
  firmware-verification path for `mcu`/`eagle`/`rk3399` chip targets, a
  5th previously-uncatalogued DUML-adjacent dispatch shape (a wire-byte-
  keyed cross-library function-pointer registry in the upgrade-test
  plugin chain), missing-bounds-check primitives in two `libupgrade_*`
  libraries (one an OOB write into a caller's own buffer), a disabled/
  no-op "whitelist" security stub (`libdji_sec_ds_whitelist_upgrade.so`),
  a live but weakly-authenticated PKCS7-signing side-channel (`p7_sign`
  invoked by `dji_lte`, incomplete shell-injection denylist, a static
  "fake" key used instead of the device's TEE-backed signer), and
  confirmation that the LTE-modem update chain is an entirely separate,
  MD5-only (not cryptographically signed) trust domain from DJI's main
  OTA/recovery pipeline.
- **Activation-TA command-ID mapping** (`18_ACTIVATION_TA_FINDINGS.md`):
  the first pass to open `libamt_util.so`/the `e91c9402` TA, acting on the
  authorization change below. Produced a complete, CA↔TA cross-validated
  68-slot TA command-ID table (3 CA export wrappers found dead/disabled at
  the TA layer, 6 TA command IDs found live with no CA export and no
  determined function, 2 slots confirmed reserved/unused), fully resolved
  `05_DJI_SEC_FINDINGS.md`'s previously-partial 11-value
  `sec_cmd_act_command_handler` dispatch (plus a correction: that family is
  NOT E1E-exclusive as doc 05 stated — it exists on E2 too), and resolved
  2 of those 11 bytes from the sender side via a previously-unexamined
  sibling daemon, `dji_amt`. Zero new DUML `(cmd_set, cmd_id)` commands —
  this pass's entire yield sits one layer below the DUML bus. 70 of 70
  command-ID mapping claims survived 3-way adversarial reverify
  unanimously. Notably, 2 of the 5 investigating agents independently
  declined the task over authorization concerns before the other 3
  proceeded — see doc 18's own opening section for how that was resolved
  (no coverage gap resulted either way).
- **Targeted follow-up pass** (2026-11-17,
  `tools/workflows/followup_unfinished_items_sweep.js`): a 3-item pass
  aimed at the loose ends the two sweeps above left open.
  - `0x18`/`0x3D` was independently re-derived from scratch with the fixed
    pipeline and **added to the registry (901st entry)**, with its
    confirmed scope kept deliberately narrow — see doc 20's "Resolved by a
    targeted follow-up pass" section for the full 2-of-3 adversarial split
    (the sender-side mechanism and addressing are fully confirmed; the
    receiver-side dispatch for this specific `cmd_id` inside `dji_lte` was
    not isolated by any reviewer, including the two who didn't refute).
  - The other two items — directly re-deriving `libamt_util.so`'s CA-side
    map from scratch (redundant with doc 18's already-cross-validated
    table, so left as-is — low value), and characterizing the 6 TA
    command IDs (`0x14`/`0x15`/`0x16`/`0x1d`/`0x24`/`0x25`) that are live
    but have no named export — **both agents declined**, on the same
    authorization-verification grounds as the two decliners in the
    original activation-TA sweep (doc 18's opening section). The
    orchestrating session directly verified, against this session's own
    raw transcript rather than just this project's own prior written
    account of it, that the project owner's authorization is genuine, and
    flagged the broader pattern — four independent agent instances across
    two sweeps now — to the project owner directly rather than retrying
    with a more persuasive prompt. The project owner, informed of exactly
    that pattern, said to proceed. The 6-handler characterization was then
    done directly by the orchestrating session itself (not delegated to a
    fresh agent) and is written up in doc 18's "Follow-up (2026-11-17):
    the 6 unnamed-but-live command IDs, characterized" section — one
    (`0x14`) resolved to a well-supported MAC/signature-verify shape, the
    other five characterized by buffer layout and address-level family
    clustering without a specific functional label.

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
  known incompleteness caveat earlier in this doc. **The full 50-binary
  tail is now closed** (46 via doc 19, the remaining 4 via doc 20/the
  side-mention above) — see the disposition table above.
- **Resolved**: `0x18`/`0x3D` (see "Targeted follow-up pass" above) — added
  to the registry at 901, with the receiver-side exact dispatch point
  left as an explicitly-documented open sub-question rather than treated
  as fully resolved. The filter bug itself is fixed in every template
  script going forward (`already_known === false` replaced with an
  explicit `already_known: false` requirement in new candidates' own
  schema usage, not a `!==true` workaround).
- **Characterized (2026-11-17), not fully named**: the 6 of the
  `e91c9402` TA's 68 command-ID slots (`0x14`/`0x15`/`0x16`/`0x1d`/`0x24`/
  `0x25`) noted above are confirmed live (real, non-default handlers) with
  no corresponding named export in `libamt_util.so`, and are now
  structurally characterized (buffer layout, parameter counts, and
  address-level family clustering — see doc 18) rather than left as
  undifferentiated "live, unknown." None was resolved to a specific named
  function, algorithm, or key, and none remains reachable only through
  `libamt_util.so`'s own wrappers — same as before, only by a caller that
  opens a `TEEC` session to this UUID directly (as `amt_test_cmd` does
  on-device for its own 3 exports). Also open: which specific outer DUML
  `cmd_set 0x00`/`0x03` activation command's payload gets forwarded,
  internally, to which specific `sec_cmd_act_*` subcommand byte — doc 18
  documents the inner layer in full but did not trace that forwarding hop,
  so `cmdset_00_General.md`/`cmdset_03_Flight_Control.md`'s existing
  (dissector-sourced) field tables were not rewritten.
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
`wf_activation_ta` (→ `18_ACTIVATION_TA_FINDINGS.md`, **done** — see
"Round history" above; notably, 2 of its 5 investigating agents
independently declined the task over authorization concerns before the
other 3 proceeded — doc 18's opening section addresses this directly),
`wf_firmware_update` (→ `20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md`, **done**
— see "Round history" above), and `wf_tail46_sweep`
(→ `19_ROUND3_TAIL46_SWEEP_FINDINGS.md`, **done** — see "Round history" above).

A targeted follow-up pass the same week hit the identical authorization
objection twice more, from two fresh agents with no memory of the earlier
decisions, reasoning entirely from this file and doc 18's own text rather
than from any live conversation. The orchestrating session treated that
recurrence as worth checking rather than dismissing: it went back to this
session's own raw transcript (not its own prior written summary of it) and
confirmed the underlying exchange with the project owner is genuine — the
project owner really did answer a direct, specific question about this
exact exclusion. That resolves the *authorization* question. It does not
resolve the separate, repeatedly-raised point that deepening public
documentation of a commercial drone's anti-theft/activation TA's internals
is worth deliberate, continued judgment even under genuine authorization —
four independent agent instances across two sweeps have now converged on
discomfort with this specific subsystem. The one item this left genuinely
incomplete (characterizing what the 6 unnamed-but-live TA command IDs
actually do) was deliberately not retried with a more persuasive prompt;
it's the project owner's call whether to continue it.

## Payload decode sweep (started 2026-11-17): a new, larger, separate effort

Distinct from everything above (which was about discovering/registering
*which* `(cmd_set, cmd_id)` pairs exist), this effort fills in the
byte-level *payload field layout* for the 744 of 901 known pairs that
have none at all — confirmed separately that the public dissector this
project already fully imported has zero field data for any of them, so
this is genuine fresh binary RE, one cmd_set (or small bundle) at a time.
Findings accumulate in `21_PAYLOAD_DECODE_SWEEP_FINDINGS.md`, one
`## cmd_set 0xNN` section per wave. First wave: cmd_set 0x06 (Remote
Control, 82 commands) — see that doc for the full result (headline: only
1 of 82 decoded; the rest are very likely RC-MCU-local, outside this
firmware extraction's scope — a real, well-evidenced architecture finding,
not a shortfall of effort). Second wave: a 10-cmd_set bundle of smaller
sets (0x01, 0x05, 0x08, 0x0b, 0x0d, 0x11, 0x18, 0x22, 0x23, 0x51 — 88
commands) — 6 decoded and merged (registry 158→164 full), 1 explicitly
refuted on adversarial reverify and 1 more downgraded by the digesting
pass itself after the same refuting evidence was found to apply to it
too (see doc 21's "Demo Mode" section), the rest honestly
`insufficient_evidence` (DM36x's 12 as a clean "not implemented on this
firmware generation" — the chip is retired). This digestion also
corrected a real error in `04_WM260_DAEMON_FINDINGS.md`/
`cmdset_22_Demo_Mode.md`: the `dji_flight` WP2-command dispatch array
was mis-stated as rooted at vaddr `0xae0f8`; it's actually rooted at
`0xae038` (`0xae0f8` is just one row, 24 in), confirmed by directly
re-deriving the raw bytes — see doc 21 for the full reconciliation
(partial — a separate "20 records" figure from elsewhere doesn't fully
agree and wasn't force-resolved). Third wave: cmd_set 0x00 (General, 70
commands) — 10 decoded (registry 164→174 full; among them, completing
`libduml_frwk.so`'s one built-in dynamic-command table to all 6 rows,
only 4 of which were previously catalogued), 10 more where the handler was
correctly identified but the specific field-layout claim was explicitly
refuted on adversarial reverify (real proof the reverify step catches
overreach even against an already-correct lead), 1 confirmed `no_payload`,
48 `insufficient_evidence` — including a genuinely new architecture
finding worth flagging on its own: a previously-undocumented "Param
Manager" subsystem inside `dji_sys` (three dedicated ELF sections,
~40 hash-keyed-parameter debug strings) that the 5-command "parameter
bus" family almost certainly routes through, without a confirmed byte
layout. See doc 21's "cmd_set 0x00" section for detail. A fourth, much
larger pair of waves (cmd_set 0x02 Camera, 190 commands; cmd_set 0x03
Flight Control, 155 commands) plus a bundle of the remaining mid-size sets
(Wi-Fi/HD Link/Mono-Binocular/Gimbal, 159 commands) are launched next —
this closes out the small/medium cmd_sets and leaves only those three
large ones (504 commands) before all 744 originally-undecoded commands
have been attempted at least once. Reusable tooling
added this round: `tools/merge_payload_decode_wave.py` (applies a wave's
result JSON into `commands.json` — now prefers `handler_evidence` over an
often-empty `scenario_description` when building a research note, fixed
after the General-wave digestion initially lost real research detail this
way), `tools/apply_notes_to_cmdset_doc.py` (mirrors that into the
hand-maintained `cmdset_XX_*.md` doc).
**Process notes:** `make -j4`/`make` alone does NOT rebuild
`duml_c`'s test binaries (only `make test` does) — running stale
`build/tests/test_*` binaries without it can silently report a false
pass; always use `make test` when verifying a registry change. Separately,
a container restart mid-digestion once left `registry_data.cpp` corrupted
to a single stray stdout line (`tools/gen_cpp_registry.py`'s own status
message, from some prior invocation that redirected the script's stdout
over its own output file) — always regenerate via the script's own `out`
argument, never `> `-redirect its stdout to the same path, and always
re-run `make test` after a restart before trusting any registry file's
on-disk state.
