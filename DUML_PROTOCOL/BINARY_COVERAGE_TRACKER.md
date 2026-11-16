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

## The three known DUML command-registration mechanisms

Every investigation in this project checks a binary for these three,
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
   `app_echo`'s ARM32 build. Always check where the resolved pointers
   actually point before calling this a command table.

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
#    duss_mb_create_route_table / duss_event_create_client. Sanity-check the method
#    against known positives (dji_sys, dji_flight) before trusting a zero result.
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

`tools/workflows/round1_tier1_tier2_sweep.js` and
`tools/workflows/round2_residual_weak_signal_sweep.js` are the actual
Claude Code `Workflow`-tool scripts used for rounds 1 and 2 above (two
phases: `Investigate` each target with a structured-output schema, then
adversarially 3-way reverify any `new_command_candidates` before trusting
one). They're kept here as working templates for a future round (e.g.
against `10_socket_bearing_no_signal_remaining_50.txt`, or a new firmware
version's binary set) — copy one, swap in a new target list and `BASE`
path, and re-launch rather than re-deriving the prompt structure from
scratch.

## Current disposition (as of `16_EXHAUSTIVE_SWEEP_FINDINGS.md`, round 2 in progress)

Of the full **808** binaries/libraries:

| Bucket | Count | Status | List file |
|---|---|---|---|
| Already documented (own section in a findings doc) | 57 | done | `02_covered_basenames_57.txt` |
| No DUML/DUSS signal at all | 591 | ruled out on signal absence | `03_no_signal_basenames_591.txt` |
| ↳ of which, has its own listening socket (corrected) | 58 | see sub-rows below | `08_socket_bearing_no_signal_corrected_58.txt` |
| ↳↳ investigated as round-1 "tier 2" | 8 | **done** — all ruled out, several independent security findings (doc 16, Track T) | `09_round1_tier2_investigated_8.txt` |
| ↳↳ remaining, generic-tooling-by-name, not individually investigated | 50 | **not done** — lower priority; mostly stock Android/Linux tooling (`adb`, `hostapd`, `iperf3`, `toybox`, etc.) by name, but a few DJI/vendor-named libraries in here (`liblte.so`, `libwlm.so`, `libduml_hal.so`, `libupgrade_common.so`, `quectel-qmi-proxy`, `Quectel_upgrade_tool`) haven't actually been disassembled despite the generic-sounding bucket — worth a closer look before calling this bucket fully closed | `10_socket_bearing_no_signal_remaining_50.txt` |
| Weak/ambiguous DUML-adjacent signal, no doc coverage | 160 | see sub-rows below | `05_weak_signal_uninvestigated_at_start_160.txt` |
| ↳ confirmed real relocation into a registration function ("tier 1") | 19 basenames / 16 investigation units | **done** (round 1) — 10 new commands confirmed + 1 unconfirmed lead (doc 16, Track R) | `06_round1_tier1_investigated_19.txt` |
| ↳ remaining, weak/ambiguous signal only | 141 | **in progress** (round 2) — Workflow task `wjeclp5ew`, run `wf_f4eae03d-334`, launched 2026-11-16; results not yet written up as of this doc's last edit | `07_round2_weak_signal_pending_141.txt` |

**Fully accounted for right now: 57 + 591 + 19 = 667 of 808** (either
documented, or ruled out with real evidence). **In progress: 141**
(round 2, running). **Flagged-but-not-individually-checked: 50**
(socket-bearing, no detected signal — lower priority, see above).

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
- **Round 2** (in progress): the 141 remaining weak-signal binaries. A
  follow-up findings doc (continuing the Track-lettering sequence from
  wherever doc 16 left off) should be written once this completes, and
  this tracker's table above updated to reflect the new disposition.

## What's genuinely still open after round 2 lands

- The 50-binary "socket-bearing, no detected signal, not individually
  investigated" tail above — flag it again rather than silently dropping
  it, and consider at least checking the handful of DJI/vendor-named
  libraries in it named explicitly above.
- Any firmware version newer than what's currently decrypted/extracted
  here (e.g. the `V01.00.1500` package referenced from the unrelated
  `nimrasol_wm260` repo) is out of scope for this tracker entirely — it's
  a different firmware revision, not part of this 808-binary universe.
