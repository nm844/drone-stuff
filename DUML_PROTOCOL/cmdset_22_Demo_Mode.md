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
  dispatch tag, not a parameter layout — no byte-level decode was
  attempted); which client (APP/PC/internal) is expected to send it.

## 0x07 — Get Global Cruise Vel

- **Handler:** `api_wp2_get_global_cruise_vel` (inside `dji_flight`)
- **Purpose:** reads back the current global cruise velocity set by `0x06`
  above.
- **Evidence / confidence / gaps:** identical basis to `0x06` — same
  `.data` array, same verification history, same unresolved-reachability
  caveat.

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
- **Not determined:** the handler's actual logic/payload format; whether
  it is reachable from outside `dji_sys`.

## Known gap: this cmd_set likely has more unmapped commands

The `0xae0f8`-rooted `.data` array in `dji_flight` that supplies `0x06`,
`0x07`, `0x08`, and `0x44` above continues for **at least 43 records total**
(vaddr `0xae0f8`–`0xae190`), all with the same confirmed 8-byte
`{function pointer, cmd word}` layout and real `R_ARM_RELATIVE`
relocations. Only these 4 have been decoded and tied to a named function so
far — the remaining ~39 records are a concrete, bounded lead for a future
pass (decode each row's function pointer and cmd word, then check whether
each one's cmd_set byte is also `0x22` or something else). See
`14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track H, "Not determined."
