# Payload decode sweep: filling in byte-level field layouts for undecoded commands

This document covers a new, larger effort distinct from everything before
it in this project: of the 901 known `(cmd_set, cmd_id)` pairs, only 157
had an actual byte-level payload field decode before this sweep started —
the other 744 were name-only. The public Wireshark dissector this project
already fully imported (see `README.md`) has **zero** field data for any
of those 744 — confirmed directly: every Lua dissector function with a
real field-extraction call (`add`-kind event, not just a boilerplate/raw
dump) was already imported, with zero gap. Filling in the rest means
genuine fresh binary reverse engineering, one `(cmd_set, cmd_id)` pair (or
small batch) at a time, organized in waves by cmd_set. Each wave appends
its own `## cmd_set 0xNN (Name)` section to this document — do not
overwrite a prior section when adding a new one.

**Methodology, common to every wave:** static analysis only (disassembly,
relocation/string parsing, reading already-decrypted firmware) — never
execute a binary, never craft/send a real packet, never write exploit
code. Investigating agents construct realistic example request/response
payload bytes for documentation purposes where a real field layout is
found (ordinary representative values, not attack-shaped edge cases) —
this is normal protocol-documentation practice, not an exception to the
project's standing rules. Every candidate field layout goes through this
project's usual 3-way adversarial reverify before being trusted. A command
that can't be resolved is reported as `insufficient_evidence` with what
was actually tried — a legitimate, expected, and separately valuable
outcome, not a gap to paper over. Verified decodes are merged into
`commands.json` with `source: "binary_re"` (a new value alongside the
existing `"dissector"` and `"flyrec_crossref"`), and `commands.json`'s
existing (if previously underused) `note` field is used to carry a short,
specific research summary for every `insufficient_evidence`/`no_payload`
command — so the next pass doesn't silently redo the same search. Worked
examples live in the relevant `cmdset_XX_*.md` doc only (hand-maintained —
`render_docs.py` doesn't know about `binary_re` entries or examples at
all; see the tooling note at the end of this section).

**Process note for future waves:** this project's C++ test suite is
*not* rebuilt by `make -j4`/`make` alone — that only builds the library
and CLI (see `duml_c/Makefile`'s `all` target). Running the existing
`build/tests/test_*` binaries without first running `make test` silently
re-executes stale, pre-change binaries and can report a false pass. Always
run `make test` (which both rebuilds and runs) before trusting a C++ test
result, and update `duml_c/tests/test_registry.cpp`'s `EXPECT_EQ(s.full,
...)` whenever a wave adds a real decode (not just `s.total`, which only
changes if a new `(cmd_set, cmd_id)` pair is added — enriching an existing
"none" entry with real fields does not change `total`). A tooling script,
`DUML_PROTOCOL/tools/merge_payload_decode_wave.py`, mechanically applies
one wave's result JSON into `commands.json` (decode_status/fields for
verified decodes, `note` for everything else); run
`duml_c/tools/gen_cpp_registry.py` and
`DUML_PROTOCOL/tools/export_master_list.py` afterward to regenerate
`registry_data.cpp`/`ALL_COMMANDS.csv` from it rather than hand-editing
those two. `DUML_PROTOCOL/tools/apply_notes_to_cmdset_doc.py` does the
matching mechanical replacement in the hand-maintained `cmdset_XX_*.md`
doc.

---

## cmd_set 0x06 (Remote Control)

**Headline finding: this cmd_set is almost entirely opaque to this
firmware extraction, and that's the real result, not a failure to
decode it.** Of the 82 undecoded commands, exactly **1** got a real
decode (medium confidence, by architectural inference rather than a
disassembled command-specific parser), **0** were confirmed to have no
payload, and **81** came back `insufficient_evidence` — each with a
specific, individually-researched reason, not a generic shrug. Nine
independent investigating agents, working on non-overlapping batches with
no access to each other's reasoning, converged on the same architecture
conclusion from different angles: aside from one already-catalogued
command whose binding this pass actually disproves (`0x3a`, see below),
**no aircraft-side binary in either firmware image (E1E/32-bit ARM,
E2/64-bit AArch64) registers a single `cmd_set 0x06` handler** via any of
this project's known DUML registration mechanisms. The most plausible
explanation, consistent with every binary checked: cmd_set 0x06 traffic
is either (a) handled entirely inside the physical remote controller's
own MCU firmware, which is not part of this project's extraction at all
(this firmware image is the aircraft's own, not the RC's), or (b) relayed
byte-blind by a JSON-config-driven proxy pattern (below) that never
parses payload bytes regardless of which specific command it's carrying.

### New methodology: a 5th DUML registration-mechanism variant

This project's existing methodology names four DUML command-registration/
send mechanisms. This sweep found and fully reverse-engineered a 5th: a
**table-driven batch variant of mechanism #3**. `dji_sys` (recovered via
its `.gnu_debugdata` minidebuginfo symbol table) exports a helper named
`duss_register_cmd` that walks a caller-supplied array of 24-byte
`{u16 cmd_set; u16 cmd_id; ...; u64 handler_ptr}` rows, calling
`duss_event_register_dynamic_command` once per row. This generalizes the
project's existing single-entry literal-immediate convention to batch
registration from a static table, and was used (alongside a direct
enumeration of every individual literal-immediate call site, and a full
decode of `libduml_frwk.so`'s universal built-in dynamic-command table —
auto-registered for every DUSS message-bus client) to exhaustively search
for any `cmd_set 0x06` registration. None was found by any variant of any
of the five mechanisms, on either architecture.

One minor cross-group inconsistency, recorded rather than smoothed over:
different investigating agents reported different total counts for
`dji_sys`'s literal `duss_event_register_dynamic_command` call sites (4 in
some groups' accounting, 11-12 in others). This appears to be a counting-
methodology difference — whether a batch registration driven by the new
`duss_register_cmd` helper's loop body is counted as "1 call site" or as
"N rows" — not a factual contradiction: every group that gave specifics
agreed on the *same* underlying registrations (Demo Mode `0x22/0x60`,
USB-state-report `0x00/0xa3`, Gimbal event-input `0x04/0x69`, and RC USB
mode `0x06/0x3a`), and every group agreed zero `cmd_set 0x06` entries
beyond `0x3a` exist. The core finding is solid; the exact tallying
convention isn't, and should be nailed down explicitly if a future pass
needs a precise count.

### Correction to doc 04: the `0x3a` binding doesn't hold on this firmware

Doc 04 (`04_WM260_DAEMON_FINDINGS.md`) previously cited `cmd_set 6/0x3a`
("RC 2014 Usb Mode Set", handler `sys_ac103_usb_otg`/`sys_wm162_usb_otg`)
as "ground-truth, binary-verified." Re-examining it this round surfaces
two problems: the handler is real code in `dji_sys`, but reached only
from `sys_platform_ac103_init`/`sys_platform_e1e_wm162_init` — different
DJI product boards' platform-init paths (confirmed by their own embedded
source-file strings), never this WM260 image's own
`sys_platform_e1e_wm260_init`/`sys_platform_e2_wm260_init` branch.
`dji_sys` is a shared multi-product binary; the ac103/wm162 code is
compiled in but never executes at runtime on this aircraft. Separately,
the handler's own internal dispatch key (a `uint16` compared against
`0x0500`/`0x1301`) doesn't cleanly decode as `(cmd_set, cmd_id) = (6,
0x3a)` under either byte order, so it may not be DUML-triggered at all on
*any* product. Doc 04 is corrected in place with a pointer to this
section. No replacement handler for `0x3a` was found — left open, not
re-asserted with a different binding.

### Correction to doc 04: the dji_flight `{fn_ptr, cmd_word}` array is 20 records, not "43+"

Doc 04 separately estimated this relocated `.data` array (vaddr `0xae0f8`
in `dji_flight`) "now known to continue for 43+ records total." Two
independent groups in this sweep each re-dumped it byte-for-byte via
relocation-aware parsing and got the same answer: **exactly 20 records**,
spanning only cmd_sets `{0x02, 0x04, 0x0a, 0x1f, 0x22}` — not 43+, and not
`0x06`. Corrected in doc 04.

### The one real decode: `0x26` "RC AETR Value Push" (medium confidence, inferred by analogy)

No disassembled `cmd_id`-0x26-specific parser was found anywhere — be
precise about what this decode actually rests on. `dji_navigation`
contains live functions `nav_rc_get_stick_value`/`nav_rc_update_stick_value`
and the debug string `"PANO_MOIVE: stick_value(%d %d %d %d)"` (4 values),
confirming a real aircraft-side consumer of a 4-value RC stick struct.
`dji_perception` separately embeds DJI's own internal
`dji_flightsystem_msgs` schema, containing verbatim, in this exact order,
twice over: `int16 aileron / int16 elevator / int16 throttle / int16
rudder`. This is byte-for-byte the same field order as the already-decoded
sibling command `0x05` ("RC Parameter Get/Push", `rc_push_param_*`,
`uint16`, offsets 0/2/4/6). Three independent adversarial reviewers each
re-derived every checkable fact directly from the binaries and agreed the
claim survives — but all three also agreed the one thing that can't be
checked (a wire parser keyed specifically on `cmd_id 0x26`) doesn't exist
to check, and the claim discloses this up front rather than hiding it.
Added to the registry as `decode_status: "full"` with that caveat
preserved in the field-level `desc` text, not silently upgraded to the
same confidence as a directly-disassembled decode.

| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 2 | `rc_aetr_push_aileron` (Aileron) | int16 |
| 2 | 2 | `rc_aetr_push_elevator` (Elevator) | int16 |
| 4 | 2 | `rc_aetr_push_throttle` (Throttle) | int16 |
| 6 | 2 | `rc_aetr_push_rudder` (Rudder) | int16 |

**Worked example** (full detail also in `cmdset_06_Remote_Control.md`):
request payload `00 04 00 04 6C 01 00 04` — aileron=1024, elevator=1024,
throttle=364 (the low end of the ~364-1684 DJI stick-travel convention
used by sibling command `0x05`), rudder=1024: sticks centered, throttle
at minimum, as if just armed on the ground. One-way telemetry/control
push — no distinct response payload (a per-packet ACK round-trip would be
wasted bandwidth for a high-rate control stream).

### A genuinely dead but informative lead: `0x50` "RC Push Rmc Key Info"

`dji_lte` contains a dead/unreachable `control_convert` feature (source
path `hardware/dji/service/lte/control_xfer/common/lte_control_convert.c`)
whose `.rodata` literally contains the DUML command word `0650` and a
9-field `"RMC_KEY_INFO: %d %d %d %d %d %d %d %d %d"` format string, with
follow-on log lines referencing shutter/record/playback/ISO. This is
strong, direct proof that DJI's own source models `0x50`'s payload as 9
integers encoding RC-button state, translated by `control_convert()` into
commands under *other* cmd_sets this project hasn't decoded yet either —
gimbal `0x04/0x01`/`0x04/0x06`, camera `0x02/0x7c`, flight-controller
`0x03/0xaa`/`0x22/0x70` (exact hex values as embedded in the string
cluster; not independently re-verified against `commands.json`'s current
numbering in this pass — check before reusing). But exhaustive register
constant-propagation over all 4,827 `adrp` instructions in the binary's
`.text`, plus a full relocation scan, found **zero live code path** that
ever loads this string cluster's address — compiled in, never reached on
this aircraft build. No byte offsets recovered; flagged as a concrete,
well-evidenced lead for whoever eventually tackles cmd_set 0x04 (Gimbal)
or cmd_set 0x02 (Camera)'s own sweep.

### Everything else: 79 commands, genuinely RC-MCU-local or config-relay-only

The remaining 79 `insufficient_evidence` commands each got a specific,
individually-reasoned research note (not a copy-pasted group template) —
see `cmdset_06_Remote_Control.md` for the full per-command text, and
`commands.json`'s `note` field for the machine-readable version. In
aggregate: master/slave RC pairing (`0x06`-`0x18`, `0x2f`-`0x39`, `0x3b`,
`0x3f`), stick/channel calibration (`0x01`-`0x04`, `0x38`, `0xf5`,
`0xf8`-`0xfa`), RC-local UI/hardware (name/password `0x08`-`0x0b`, unit
language `0x53`/`0x54`, custom buttons `0x2d`/`0x2e`/`0x4c`, "push to
glass"/LCD `0x51`/`0x52`, buzzer `0xf7`, board-id `0xf6`), gimbal-control-
wheel settings (`0x2b`-`0x36`), and RC-side telemetry pushes (GPS/RTC/
temperature/battery, `0x1b`-`0x1e`) are all plausibly RC-hardware-local by
name and by the complete absence of any aircraft-side trace. A factory-
calibration cross-check independently supports this for the stick-related
subset: `dji_autotest`'s 16 `at_*.so` calibration plugins cover every
other physical-sensor domain the aircraft owns (barometer, compass,
gimbal, IMU, vision, SDR, ...) — **no stick/joystick plugin exists at
all**, consistent with stick calibration being entirely the RC's own
concern. Two commands (`0x56`/`0x57`, "Quiry Role"/"Quiry Ms Link Status")
have a plausible semantic candidate daemon (`dji_wlm`, which implements an
explicit Master/Slave role model) that this pass's tooling couldn't
disassemble with confidence — stripped 32-bit ARM/Thumb2 with no mapping
symbols defeated the available disassemblers past the PLT — flagged as a
concrete lead for a future pass with better ARM32 tooling (a heuristic
Thumb-aware disassembler, or Ghidra) rather than asserted either way.
