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

---

## cmd_sets 0x01, 0x05, 0x08, 0x0b, 0x0d, 0x11, 0x18, 0x22, 0x23, 0x51 (bundled, 88 commands)

Second wave: a bundle of 10 small/misc cmd_sets, run as 8 investigate
groups (32 agents total). Net yield: **6 decoded and merged** (registry
158→164 full; `total` unchanged at 901, since this wave only enriches
existing "none" rows), **1 decoded-but-refuted on reverify**, 1 further
command downgraded by the digesting pass itself after the refuted
sibling's evidence was found to apply to it too (see "Demo Mode" below),
and the remaining 80 honestly reported `insufficient_evidence` (including
12 under a `"confirmed not implemented on this firmware generation"`
variant for DM36x) with specific research notes, not guesses.

### Special (0x01) — all 10 insufficient_evidence; a concrete new lead

All 10 "SDK Ctrl"/arm-disarm/gimbal/camera-shutter bridge commands came
back `insufficient_evidence` after an unusually thorough pass: this
investigation fully decoded `dji_flight`'s relocated dispatch array
(independently re-confirmed by this digestion to be rooted at vaddr
`0xae038`, running 44 raw rows to `0xae190` — see the `cmdset_22_Demo_
Mode.md`/`04_WM260_DAEMON_FINDINGS.md` corrections below), resolved its
generic route+client registration (a hardcoded 10-cmd_set array:
`{0x00,0x02,0x03,0x04,0x05,0x11,0x1f,0x22,0x0a,0x3c}`), checked all 11 of
`dji_sys`'s literal `duss_event_register_dynamic_command` call sites, and
swept every other binary in both images importing any
`duss_event_register_dynamic_command*` variant. cmd_set `0x01` appears in
none of them.

**Concrete new lead, not yet chased:** a 4.5MB non-ELF blob,
`e1e_extracted/rtos_dec_RTOS.bin` (`file` reports plain "data", no
recoverable ELF/symbol structure), is the most likely candidate for where
arm/disarm, gimbal, and camera-shutter logic actually lives — if
`ALL_COMMANDS.csv`'s `typical_receiver: Flight Controller` designation
for these commands means the flight-controller **MCU's own RTOS
firmware**, not the Android-side `dji_flight` daemon of the same
descriptive name (a real ambiguity this project hasn't previously had to
resolve, relevant to other still-undecoded commands too, not just these
10). Determining this blob's load address/ISA and disassembling it is a
concrete, bounded lead for a future pass.

### Center Board (0x05) — 3 decoded, 14 insufficient_evidence

- **`0x02` "Center Push Batt Dynamic Info"** — decoded. Handler:
  `dji_sys`'s `sys_battery_get_dynamic_info` (generic request dispatcher)
  → a per-board-model callback at device-context offset `+0xb0` → a
  32-byte response via `duss_event_resp_data`. Only one field is
  confirmed WM260-specific-reachable with full confidence
  (`remaining_capacity_percent`, offset 20, a standard SBS/SMBus register
  `0x0D` read); the surrounding 20+11 bytes are confirmed-zeroed-by-the-
  generic-handler but their real per-board content for WM260 specifically
  wasn't independently confirmed (the one per-board callback actually
  disassembled was for a different DJI product). See
  `cmdset_05_Center_Board.md` for the full field table and worked example.
- **`0x21`/`0x22` "Center Req Bat Static/Dynamic Data"** — decoded (11
  and 37 fields respectively). Both trace to `dji_blackbox`'s
  `phm_bat_data_upload`/`parse_bat_static_data`/`parse_bat_dynamic_data`
  functions (already known by this project, `12_WM260_EXHAUSTIVE_BINARY_
  SWEEP_FINDINGS.md`, as battery health-management/prognostics
  forwarding) — field names/positions read directly from each function's
  own `.rodata` format-label strings during a ~170-instruction disassembly
  walk. See `cmdset_05_Center_Board.md`.
- The other 14 Center Board commands (LED control, virtual RC,
  self-discharge days/time, barcode, auth data) came back
  `insufficient_evidence` — real functions were found for some (e.g.
  `led_control_thread`, `sys_fc_led_exit` for `0x03`) but none could be
  tied to a specific `duss_event_register_dynamic_command` call site or
  anchored by a matching log/format string.

### DM36x (0x08) — 12 "confirmed not implemented on this firmware generation"

Clean negative result, exactly the outcome this group's task hint
anticipated: the DM36x video-encoder chip is retired this firmware
generation (device-type 8's firmware string is now the generic `"ve_air"`,
not DM36x-specific — independently corroborated by this same wave's own
`0x18`/`0x3D` finding, below). No handler was found for any of the 12
DM36x-named commands.

### Simulator (0x0b) — all 17 insufficient_evidence

The flight-simulator subsystem's physics-parameter commands (air params,
gravity, arm length, mass/inertia, motor/battery settings) could not be
tied to a registration site in `dji_flight` or any other binary checked.

### Battery (0x0d) — all 11 insufficient_evidence

No new decodes; cross-referenced against the project's existing
flyrec-crossref-sourced "Battery Push Common Info" entry for field-naming
convention, but no handler was located for any of these 11 commands'
own registration.

### ADSB (0x11) — all 11 insufficient_evidence

Correctly kept the TEE-internal command-ID space (already mapped in docs
13/14, a completely different numbering system inside the ADS-B OP-TEE
TA) separate from these DUML wire-level cmd_ids throughout — no
conflation found in this investigation's evidence. No DUML-level handler
was located for any of the 11 licensing/whitelist/warning commands.

### LTE/Dongle Diagnostic (0x18) + Route Switch (0x51) — both decoded

- **`0x18`/`0x3D`** formalized into a full field table (new doc,
  `cmdset_18_LTE-Dongle_Diagnostic.md`) from the exact payload bytes
  already known from `20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md`. One
  correction to that prior doc's own hint: the real payload is **16**
  bytes (1 operation byte + 15 filler bytes of `0x61`), not 17 as
  previously described.
- **`0x51`/`0x05`** — a 7-field, 3-sub-layout payload (dispatched on a
  leading `operation` byte: Port Switch / Route Switch / Switch Done)
  recovered directly from the handler's own embedded `printf`-style debug
  strings in `libduml_frwk.so`, confirmed identically on both
  architecture builds. See `cmdset_51_Route_Switch.md` for the full
  table and worked example. (One correction to this wave's own task
  hint: `0x51`/`0x05`'s pre-existing lead was `cmdset_51_Route_Switch.md`
  itself, not the round-2-sweep's `imss_link_v1_send` discovery — that
  discovery was for a *different* command, `0x51`/`0x04` "Gimbal
  Calibration Result Query", which merely shares the same cmd_set.)

### Demo Mode (0x22) + Smart (0x23) — 1 decoded, 1 refuted, 1 downgraded, 5 insufficient_evidence

- **`0x60` "Demo Mode Handle"** — decoded (1 field, a mode-selector
  byte with 3 enum values). Handler identity confirmed directly from the
  compiler's own embedded debug strings (source file path + literal
  function name), not a guess.
- **`0x06` "Set Global Cruise Vel"** — a candidate single-`float32`
  field layout was proposed and **explicitly refuted 3-of-3** on
  adversarial reverify. All three reviewers independently traced the
  shared generic send primitive (`duss_event_resp_data_without_retcode`
  in `libduml_frwk.so`) down to its actual `memcpy(dest, arg4, arg5)`
  call, proving the candidate "value" register is used as a **pointer**
  and the companion 16-bit value as a **variable length** — directly
  contradicting the fixed-4-byte-scalar model, despite every other piece
  of the claim's supporting dispatch-table/relocation evidence being
  independently and precisely reproduced. **Not added to the registry.**
- **`0x07` "Get Global Cruise Vel"** — the identical candidate layout
  survived reverify 2-of-3 (only 1 of 3 reviewers independently traced
  deep enough to find the same `memcpy` disproof). The digesting pass
  judged this a near-miss in the automated adversarial process rather
  than a genuine disagreement: `0x07` shares the *exact* architecture,
  generic send-wrapper, and unresolved-vtable situation as `0x06` (the
  claim's own evidence says so explicitly), so the same disproof applies
  regardless of the vote count. **Downgraded and not added to the
  registry**, with the reasoning recorded verbatim in both `commands.json`
  (`note` field) and `cmdset_22_Demo_Mode.md`.
- **`0x08`/`0x44`** (the other two `dji_flight` WP2 commands in this same
  array) — `insufficient_evidence`; same generic send-wrapper confirmed,
  but no command-specific disassembly evidence (comparison, enum check)
  found to assign a meaning to the surviving scalar/length pair.
- **`0x20`/`0x21`/`0x22` "Smart"** — `insufficient_evidence` for payload
  fields, but this pass *did* independently re-confirm (byte-for-byte,
  not just name-matched) both of this project's previously-documented
  registration mechanisms for all three commands, plus a consistent
  `0`/`1`/`2` discriminator-constant pattern across their three near-
  identical handlers — see `cmdset_23_Smart.md`.

**Correction to `04_WM260_DAEMON_FINDINGS.md` and `cmdset_22_Demo_Mode.md`
(made during this digestion, not by the investigating agents):** the
`dji_flight` dispatch array supplying `0x06`/`0x07`/`0x08`/`0x44` was
previously described as "rooted at vaddr `0xae0f8`," with "~43" or "20"
records depending on which prior pass's account you read. Directly
re-deriving the raw bytes during this digestion found the array is
actually rooted at **`0xae038`** (`0xae0f8` is merely the `0x06` row, 24
rows in) and runs **44 raw 8-byte rows** through vaddr `0xae190`
inclusive, after which the data becomes structurally incoherent (cmd_set
bytes like `0xb4`/`0xa9`/`0x40` that match no known cmd_set) — strongly
suggesting `0xae190` is the table's true end and a naive scan to the next
double-zero (`0xae1b8`) overruns into unrelated data. This directly
reconciles with, and essentially confirms, this project's original
"43+" estimate. It does **not** fully reconcile with the separate "20
records, cmd_sets `{0x02,0x04,0x0a,0x1f,0x22}`" figure reported elsewhere
(possibly a different subset or counting convention) — that discrepancy
is recorded, not resolved, here.

---

## cmd_set 0x00 (General, 70 commands)

Of 70 targets: **10 decoded and added to the registry** (900→... no new
rows — this wave only enriches existing `(cmd_set, cmd_id)` entries that
were already catalogued name-only, so the registry's *total* stays 901;
its `full` count grows), **10 more where the HANDLER was correctly
identified but the proposed field layout was explicitly refuted** on
3-way adversarial reverify, **1 confirmed `no_payload`**, and **48
`insufficient_evidence`**.

**Decoded** (all `source: "binary_re"`, `dissector_fn` naming the real
handler, in `commands.json`/`cmdset_00_General.md`):

| `cmd_id` | Name | Handler |
|---|---|---|
| `0x00` | Ping | `duss_event_ping` (`libduml_frwk.so`) — a 3-instruction trampoline that echoes the request payload back verbatim via `duss_event_resp_data_v2`; no fixed fields, genuinely request/response |
| `0x07` | Enter Loader | `check_fw_entry` (sender-side only; the receiving `dji_sys`-side parser was not independently located — same gap already flagged in this project's prior docs for `0x07`-`0x0A`) |
| `0x08` | Update Confirm | `check_fw_start` (sender-side only, same receiver gap) |
| `0x0A` | Update Finish | `check_fw_finish` (sender-side only, same receiver gap) |
| `0x4A` | Set Date/Time | `sys_event_set_date` (builds/validates a `struct tm`, calls `mktime()`) |
| `0x4B` | Get Date/Time | `sys_event_rtc_get_date` (builds the response from the live system clock) |
| `0x4C` | Get Module Sys Status | `sys_event_report_status` |
| `0x51` | Get Serial Number | `sys_event_get_serial_number` |
| `0xFA` | Log Control | `duss_event_log_control` |
| `0xFF` | Query Device Info | `sys_event_query_device_info` |

Two of these (`0x00` Ping, `0xFA` Log Control) came from re-reading
`libduml_frwk.so`'s one built-in 6-entry dynamic-command table
(`duss_event_create_dynamic_cmd_tbl`) directly from its raw `.data`
bytes — this project's prior docs had only catalogued 4 of its 6 rows
(`0x00/0x2f`, `0x00/0x89`, `0x00/0xaa`, `0x51/0x05`); **all 6 rows are
now known**: `{0x00/0x00, 0x00/0x2f, 0x00/0x89, 0x00/0xaa, 0x00/0xfa,
0x51/0x05}`.

**Decoded-then-refuted** (handler identification survives, the specific
byte-offset/size/type claims do not — `commands.json`'s `note` field says
so explicitly for each, distinguishing this from a plain miss):

| `cmd_id` | Name | Handler (correctly identified) |
|---|---|---|
| `0x09` | Update Transmit | `check_fw_transmit` (sender-side only) |
| `0x2F` | Trans Diag Event | `duss_trans_diag_event` (already known from doc 04) |
| `0x54` | Get Temperature Info | `sys_event_get_temp_info` |
| `0x5A` | Play Sound | `sys_event_play_sound` |
| `0x60` | Auto Test Info | `sys_event_auto_test_info` |
| `0x89` | Shell Command | `duss_event_shell` (already known from doc 04) |
| `0x93` | Begin Single Module Upgrade | a local static `send_fn` helper inside `upgrade_test` → `duss_event_send_sync` |
| `0x94` | Set Upgrade Flag | same `upgrade_test` `send_fn` helper |
| `0xA3` | USB State Report | `sys_wm260_usb_state_handle` (already known from doc 04) |
| `0xAA` | Node Sniffer Request | `duss_event_node_sniffer_req` (already known from doc 04) |

Notably, 4 of these 10 (`0x2F`, `0x89`, `0xA3`, `0xAA`) were specifically
given a head start pointing at their already-confirmed doc-04 handlers —
proof the adversarial reverify step is doing real work: an already-correct
handler identification didn't save an unsupported field-layout guess from
being caught and rejected.

**No payload:** `0x59` (Test Mode) — disassembly of `sys_event_test_mode`
is two instructions, `b duss_event_resp_ok; udf #0` (unreachable padding)
— it unconditionally acks without reading the request payload at all.

**Headline architecture finding from the 48 `insufficient_evidence`
commands — a previously-undocumented "Param Manager" subsystem inside
`dji_sys`:** the 5-command "parameter bus" family (`0x02` Push Param Set,
`0x03` Push Param Get, `0x04` Push Param Start, `0x05` Multi Param Set,
`0x06` Multi Param Get) could not be pinned to a specific handler, but the
search for one surfaced something genuinely new: three custom ELF sections
literally named `param_manager_local` (56 bytes), `param_manager_buf_local`
(32 bytes), and `param_manager_remote` (12 bytes) inside `dji_sys`, backing
~40 `"PM:"`-prefixed debug strings that describe a real, hash-keyed
named-parameter protocol with push-frequency subscriptions — e.g.
`"PM:register remote param item err, name: %s, freq: %d"`,
`"PM:recieved push remote param hash was not register, hash: %u"`,
`"PM:[%s]param is out of range,%s"`. Two of `dji_sys`'s registration call
sites are data-driven (reading `cmd_set`/`cmd_id` from a runtime-populated
table rather than a literal immediate) and trace back to this same
`param_manager_*` global state, strongly suggesting this family is a real,
live subsystem — just not one this pass could resolve to literal
`(cmd_set, cmd_id)`-to-handler bindings or exact wire-payload offsets with
confidence. **Not added to the registry** (no confirmed byte layout), but
recorded prominently here and in each of the 5 commands' `commands.json`
`note` fields, since this is a genuine, reusable lead for a future pass —
whoever revisits this family should start from these three section names
and string literals rather than re-deriving them.

**Process note — a lost-then-recovered digestion detail:** this wave's
first digestion pass initially let several `insufficient_evidence`
commands' rich, per-command research text (including the Param Manager
finding above) get replaced by `merge_payload_decode_wave.py`'s generic
fallback note, because the tool preferred an (often-empty, for
`insufficient_evidence` commands) `scenario_description` field over the
richer `handler_evidence` field. Caught and fixed in the same digestion,
both for this wave's 33 affected commands (notes rebuilt from
`handler_evidence` directly) and in the tool itself (now falls back to
`handler_evidence` when `scenario_description` is empty) so future waves
don't lose this kind of detail by default.
