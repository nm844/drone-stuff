# Cmd Set 0x22 — Demo Mode

Total known command IDs: 5

**Not part of the public `dji-firmware-tools` Wireshark dissector** — this
cmd_set is entirely outside that project's documented `0x00`-`0x11` range.
Every entry below was found by direct disassembly of this project's own
WM260 (Mavic 3) firmware (`dji_sys`, `dji_flight`), not borrowed from any
existing capture, community reference, or public dissector source. Full
methodology and verification history: `04_WM260_DAEMON_FINDINGS.md` and
`14_FOLLOWUP_DEEPDIVE_FINDINGS.md` (Track H).

The name "Demo Mode" comes from the one cmd_id (`0x60`) found first, inside
`dji_sys`; the other 4 cmd_ids were found later, in a completely different
binary (`dji_flight`), and are **not** demo/retail-mode related — they are
real waypoint-mission ("WP2") flight commands that simply happen to share
this cmd_set number. Treat "Demo Mode" as this cmd_set's historical label,
not a description of everything registered under it.

## 0x06 — Set Global Cruise Vel

- **Handler:** `api_wp2_set_global_cruise_vel` (inside `dji_flight`)
- **Purpose:** sets a single global cruise velocity value used by the
  aircraft's own waypoint/mission-automation layer — i.e. the speed the
  aircraft flies between waypoints during an automated ("WP2") mission.
  This is the kind of command a companion app's "mission cruise speed"
  slider would plausibly send.
- **Evidence:** tagged by one row of a confirmed `R_ARM_RELATIVE`-relocated
  `.data` array inside `dji_flight`, rooted at vaddr `0xae0f8`. Each row is
  an 8-byte `{function pointer, cmd word}` pair; the cmd word's low byte
  decodes as cmd_set (`0x22`) and high byte as cmd_id (`0x06`) — a reading
  corroborated by all 4 of this binary's recovered entries agreeing on the
  same cmd_set byte, not just inferred by analogy.
- **Confidence:** high that this exact `(cmd_set, cmd_id)` → function
  mapping is correct — independently re-derived twice, with the final
  cmd_id ordering among the three cruise/pause functions below confirmed
  only on a third, from-scratch pass (two earlier passes had it transposed).
  Low/unresolved on runtime reachability: no caller, vtable slot, or any
  other reference to this function's address was found anywhere else in
  the binary, so how a real DUML frame reaches this handler at runtime
  (or whether it ever does in production) is not established.
- **Not determined:** payload format/fields (the array gives only the
  dispatch tag, not a parameter layout); which client (APP/PC/internal)
  is expected to send it.

**2026-11-17 payload-decode attempt (refuted on adversarial reverify):**
a candidate field layout (a single 4-byte `float32` cruise-velocity
value) was proposed and then explicitly refuted 3-of-3 — all three
reviewers independently traced the handler's generic send primitive
(`duss_event_resp_data_without_retcode` in `libduml_frwk.so`) down to its
actual `memcpy(dest, arg4, arg5)` call, which treats the candidate
"value" argument as a **pointer**, not the payload value itself, and the
companion 16-bit value as a **variable copy length**, not a fixed 4-byte
size — directly contradicting the single-float32 model. The real
per-command payload serialization happens inside a C++ vtable override on
a `.bss` object whose constructor could not be statically located (same
unresolved-reachability gap as the original pass). **Payload format
remains not determined** — see `21_PAYLOAD_DECODE_SWEEP_FINDINGS.md` for
the full adversarial-review record.

## 0x07 — Get Global Cruise Vel

- **Handler:** `api_wp2_get_global_cruise_vel` (inside `dji_flight`)
- **Purpose:** reads back the current global cruise velocity set by `0x06`
  above.
- **Evidence / confidence / gaps:** identical basis to `0x06` — same
  `.data` array, same verification history, same unresolved-reachability
  caveat.

**2026-11-17 payload-decode attempt:** a candidate field layout (mirroring
`0x06`'s) survived this pass's own 3-way adversarial reverify 2-of-3, but
is deliberately **not** carried into the registry here: `0x06`'s own
reverify found concrete, specific evidence (the `memcpy`-based send
primitive — see `0x06` above) that undermines the identical architecture
this command shares, and that finding was judged to apply equally here
even though only 1 of this command's 3 reviewers independently found it.
Payload format remains not determined.

## 0x08 — Pause Recovery

- **Handler:** `api_wp2_pause_recovery` (inside `dji_flight`)
- **Purpose:** pause/resume ("recovery") control for an in-progress
  waypoint mission — functionally, the kind of command behind a companion
  app's "pause mission" / "resume mission" control.
- **Evidence:** same `.data` array as `0x06`/`0x07`. **Note on history:**
  two earlier analysis passes had this function's cmd_id transposed with
  `0x06`'s (reporting `pause_recovery` as the *first* entry, cmd_id `0x06`);
  a dedicated from-scratch third pass corrected this — `pause_recovery` is
  the *third* of the three cruise/pause entries, cmd_id `0x08`.
- **Confidence / gaps:** same as `0x06` — mapping high-confidence,
  reachability unresolved, payload format not decoded.

**2026-11-17 payload-decode attempt:** same generic 6-arg/2-surviving-scalar
send-wrapper shape as `0x06`/`0x07`/`0x44` was confirmed again, but unlike
those three, this command's name gives no external hint about what the
surviving scalar/length pair represents, and no command-specific
disassembly evidence (a distinguishing comparison, an enum check) was
found. Reported `insufficient_evidence` rather than guessed — payload
format not decoded.

## 0x44 — Break Restore Waypoint Fly

- **Handler:** `api_wp2_break_restore_waypoint_fly` (inside `dji_flight`)
- **Purpose:** "break" (abort/interrupt) or "restore" (resume) a
  waypoint-mission flight already in progress — plausibly a lower-level
  primitive that `0x08`'s pause/recovery logic calls into, though that
  specific relationship was not traced or confirmed.
- **Evidence:** same `.data` array as the three entries above, at a
  different offset within it (confirmed `R_ARM_RELATIVE`-backed, cmd word
  decoding to cmd_set `0x22` / cmd_id `0x44`).
- **Confidence / gaps:** same as `0x06` — mapping high-confidence,
  reachability unresolved (no caller found), payload format not decoded.

**2026-11-17 payload-decode attempt:** same generic send-wrapper shape
confirmed again. This command's name ("Break" *and* "Restore" in one
`cmd_id`) strongly suggests a 1-byte action/enum field distinguishing the
two operations, but no disassembly evidence (no comparison, no switch)
lets that enum be assigned to a specific byte offset or to either
surviving generic scalar — the only place that distinction could be made
is inside the same unresolved vtable override as `0x06`-`0x08`. Reported
`insufficient_evidence` — payload format not decoded.

## 0x60 — Demo Mode Handle

- **Handler:** `sys_wm260_demo_mode_handle`, registered identically from 4
  separate platform/board-init functions inside `dji_sys`:
  `sys_platform_e1e_wm260_post_init`, `sys_platform_e1e_wm260l_post_init`,
  `sys_platform_e2_wm260_post_init`, `sys_platform_e2_wm260l_post_init`
  (names recovered from `dji_sys`'s `.gnu_debugdata` minidebuginfo).
- **Purpose:** handles a "demo mode" feature — most plausibly a
  factory/retail-demo-unit behavior (e.g. an in-store display aircraft
  running a canned routine, or with certain controls disabled/altered)
  rather than a normal end-user flight feature. This reading is inferred
  from the handler's name and registration context, not from disassembling
  the handler body itself.
- **Evidence:** literal `cmd_set`/`cmd_id` immediates loaded immediately
  before a `bl` to `duss_event_register_dynamic_command`, in all 4
  platform-init functions — the same registration convention confirmed
  elsewhere in this firmware (see `04_WM260_DAEMON_FINDINGS.md`).
- **Confidence:** high on the `(cmd_set, cmd_id)` → handler-name mapping.
  Low/speculative on the specific "demo mode" semantic. Never observed
  exercised from any externally-reachable code path examined this project
  — plausibly not reachable over the production app/RC link at all.
- **Not determined (as of the original pass):** the handler's actual
  logic/payload format; whether it is reachable from outside `dji_sys`.

### Payload fields (added 2026-11-17, direct disassembly of the handler)

- **Field:** `demo_mode_action` — offset 0, size 1, type `uint8 (enum)`.
  Read directly from the incoming event at the handler's own event-struct
  offset `0x14` (mapped to payload offset 0; the payload is a single
  byte). Enum values: `0` = disable/clear the demo-mode flag; `1` =
  enable/set the demo-mode flag; `2` = query whether the current
  platform/product name string equals the literal `"factory"` (a
  factory-build check); any other value is rejected with error code
  `0xE3` (227).
- **Evidence:** the handler's identity was confirmed directly from the
  compiler's own embedded debug/log strings at the very top of the
  function — the source file path
  `hardware/dji/service/system/products/sys_platform_e1e_wm260.c` and the
  literal function name `sys_wm260_demo_mode_handle` — not a name guess.

**Worked example:** a factory/production test station enables "demo
mode" (a retail-display/factory behavior) on a newly assembled aircraft
before it ships to a store display unit.

- Request payload: `01` (`demo_mode_action` = 1, "enable")
- Response payload: `01` — the handler's non-error paths always send
  exactly one response byte via `duss_event_resp_data`; for action 0 or 1
  that byte is an unmodified copy of the request byte (confirmed: the
  response buffer is initialized from the request byte and never
  rewritten on either path), so the aircraft confirms "demo mode is now
  enabled" by echoing the same value back.

## Known gap: this cmd_set likely has more unmapped commands

**Correction (2026-11-17):** the `.data` array supplying `0x06`, `0x07`,
`0x08`, and `0x44` above is actually rooted at vaddr **`0xae038`**, not
`0xae0f8` as this doc previously stated — `0xae0f8` is merely the row for
`0x06` itself, partway through the table, not the table's start (directly
re-derived from the raw bytes: `0xae0f8` - `0xae038` = `0xc0` = exactly 24
rows in). From `0xae038`, the array's rows decode to sensible, plausible
`(cmd_set, cmd_id)` pairs — matching this project's other known cmd_sets
(`0x00, 0x02, 0x03, 0x04, 0x0a, 0x11, 0x1f, 0x22`) — through vaddr
`0xae190` inclusive (**44 raw 8-byte rows total**, closely matching this
doc's original "at least 43 records" estimate, now confirmed rather than
approximate). Past `0xae190`, the next rows decode to cmd_set bytes
(`0xb4`, `0xa9`, `0x40`) that don't correspond to any cmd_set known
anywhere in this project, strongly suggesting the real table ends at
`0xae190` and anything read past it is unrelated adjacent data, not more
dispatch rows — a naive scan for a double-zero terminator overruns to
`0xae1b8` and should not be trusted as the table's true boundary. A
*separate* re-count (from a sibling payload-decode pass, see
`21_PAYLOAD_DECODE_SWEEP_FINDINGS.md`) reported "20 records... spanning
only cmd_sets `{0x02, 0x04, 0x0a, 0x1f, 0x22}`" — that figure describes
some other subset or counting method than a full enumeration from
`0xae038`; it was **not** independently reconciled against this direct
recount and the two should not be assumed to agree. Of the 44 rows
confirmed here, cmd_set `0x22` alone accounts for 16 of them (`0x01, 0x02,
0x03, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0d, 0x0e, 0x17, 0x18, 0x19, 0x1a,
0x1e, 0x44`) — only 5 of those 16 (`0x06, 0x07, 0x08, 0x44`, plus `0x60`
in a different binary) have been decoded and tied to a named function so
far. The remaining ~11 `cmd_set 0x22` rows, plus the rows for the other 7
cmd_sets in this same array, are a concrete, bounded lead for a future
pass. See `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track H, "Not determined."
