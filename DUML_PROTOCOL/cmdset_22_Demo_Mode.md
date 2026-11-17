# Cmd Set 0x22 — Demo Mode

Total known command IDs: 17

**Not part of the public `dji-firmware-tools` Wireshark dissector** — this
cmd_set is entirely outside that project's documented `0x00`-`0x11` range.
Every entry below was found by direct disassembly of this project's own
WM260 (Mavic 3) firmware (`dji_sys`, `dji_flight`), not borrowed from any
existing capture, community reference, or public dissector source. Full
methodology and verification history: `04_WM260_DAEMON_FINDINGS.md`,
`14_FOLLOWUP_DEEPDIVE_FINDINGS.md` (Track H), and
`21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` (the full table, re-derived and
corrected).

The name "Demo Mode" comes from the one cmd_id (`0x60`) found first, inside
`dji_sys`; the other 16 cmd_ids were found later, in a completely different
binary (`dji_flight`), and are **not** demo/retail-mode related — most are
real waypoint-mission ("WP2") flight commands that simply happen to share
this cmd_set number, though a few (see `0x01` below) turn out to be
unrelated ADS-B logging code bound to a WP2-numbered slot. Treat "Demo
Mode" as this cmd_set's historical label, not a description of everything
registered under it.

## 0x01 — (name unknown)

- **Handler:** unresolved — func at `0x10238` inside `dji_flight`
  (`0x10238`–`0x10eb4`, ~1660B; this range likely holds more than one
  function, only the entry point is attributed here). No self-identifying
  log string was found for this specific entry point.
- **Purpose:** the disassembled content at this address is thematically
  **ADS-B logging/directory setup** (`"set adsb receiver successfully!"`,
  `"creat adsb directory successfully!"`, a log path
  `/blackbox/adsb/adsb_log_wm231_%0d.txt`, and CSV column headers
  `center_lon`/`heading`/`air_groud`/`time`) — i.e. this handler sets up
  ADS-B receiver logging, despite being registered under a Demo-Mode/WP2
  cmd_id. Flagged as a cross-subsystem reuse, not a misread.
- **Evidence:** same confirmed `R_ARM_RELATIVE`-relocated `.data` array as
  every other entry in this file, row at vaddr `0xae0d8`. Full raw-byte
  re-derivation in `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §3/§6.
- **Confidence:** high on the `(cmd_set, cmd_id)` → function-address
  mapping; low on the handler's name (none recovered) and on whether the
  ~1660B disassembly window is entirely this one function.
- **Not determined:** payload format/fields; which client is expected to
  send it; whether this function's full extent was correctly bounded.

## 0x02 — Upload Waypoint Ack Rec

- **Handler:** `upload_wp_ack_rec_handler` (medium confidence — one clean
  self-name hit; see caveat below), inside `dji_flight`, func at `0x1badc`.
- **Purpose:** receives/processes the acknowledgement for a waypoint
  upload.
- **Evidence:** `.data` array row at vaddr `0xae0e0`. Name resolved via
  PC-relative literal-pool string decoding (no `.gnu_debugdata` on this
  binary — see `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §4 for the
  method).
- **Confidence:** high on the mapping; medium on the name (found once,
  ~330B into the function). **Caveat:** strings appearing later in this
  function's naive disassembly window (`add_node_to_list_tail`,
  `get_node_by_index`, `autotest_config`, then an abrupt shift into
  GIMBAL/CAMERA receive-handler text) almost certainly belong to separate,
  unregistered neighboring functions — not claimed as part of this
  handler.
- **Not determined:** payload format/fields; reachability.

## 0x03 — WP2 Waypoints Upload

- **Handler:** `api_wp2_waypoints_upload`, inside `dji_flight`, func at
  `0x1acc4`.
- **Purpose:** drives a waypoint-mission upload — fits the existing
  `api_wp2_*` family exactly.
- **Evidence:** `.data` array row at vaddr `0xae0e8`. Name recovered by
  hand-correcting a padding-boundary miss in the automated string
  resolver; raw bytes confirm `...ad_handle\0api_wp2_waypoints_upload\0...`.
  **This independently resolves an open lead in
  `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md`**, which had found this
  exact function name by string search but reported "no call site... and
  no stored pointer referencing [it] anywhere" and "no numeric cmd_id
  recoverable" — this table supplies the missing cmd_id.
- **Confidence:** medium-high on the name/mapping; reachability still
  unresolved (same caveat as every other entry in this file); payload
  format not decoded.

## 0x05 — (name unknown — single-4-byte accessor)

- **Handler:** unresolved, inside `dji_flight`, func at `0x1b830`
  (`0x1b830`–`0x1b860`, 48B).
- **Purpose:** no logging/self-name was found, but the raw disassembly is
  clean and small enough to characterize directly: null-checks its first
  argument (returns immediately if null); otherwise calls a sub-function
  (`0x1b664`) with a local 4-byte output slot, and if that sub-call
  reports a non-zero count, loads one 4-byte value and stores it through
  the caller-supplied pointer argument, returning `4` (else returns `0`).
  A "get a single 4-byte value, report byte-count-or-zero" accessor shape
  — concrete payload-layout evidence even without a recovered name.
- **Evidence:** `.data` array row at vaddr `0xae0f0`; behavior read
  directly off the disassembly (see
  `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §6 for the raw trace).
- **Confidence:** high on the `(cmd_set, cmd_id)` mapping and on the
  described accessor shape; no name recovered.

## 0x06 — Set Global Cruise Vel

- **Handler:** `api_wp2_set_global_cruise_vel` (inside `dji_flight`)
- **Purpose:** sets a single global cruise velocity value used by the
  aircraft's own waypoint/mission-automation layer — i.e. the speed the
  aircraft flies between waypoints during an automated ("WP2") mission.
  This is the kind of command a companion app's "mission cruise speed"
  slider would plausibly send.
- **Evidence:** tagged by one row of a confirmed `R_ARM_RELATIVE`-relocated
  `.data` array inside `dji_flight`. A later independent pass established
  this array's real extent as vaddr `0xae040`–`0xae190` (43 rows total,
  not just the 4 rows originally decoded here) — see
  `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md`. The cmd word's low byte
  decodes as cmd_set (`0x22`) and high byte as cmd_id (`0x06`) — a reading
  corroborated by every one of this array's 43 rows agreeing on a
  plausible cmd_set byte, not just inferred by analogy.
- **Confidence:** high that this exact `(cmd_set, cmd_id)` → function
  mapping is correct — independently re-derived three times now (twice
  before, once more as part of the full-table pass). Low/unresolved on
  runtime reachability: no caller, vtable slot, or any other reference to
  this function's address was found anywhere else in the binary, so how a
  real DUML frame reaches this handler at runtime (or whether it ever
  does in production) is not established.
- **Not determined:** payload format/fields (the array gives only the
  dispatch tag, not a parameter layout — no byte-level decode was
  attempted); which client (APP/PC/internal) is expected to send it.

## 0x07 — Get Global Cruise Vel

- **Handler:** `api_wp2_get_global_cruise_vel` (inside `dji_flight`)
- **Purpose:** reads back the current global cruise velocity set by `0x06`
  above.
- **Evidence / confidence / gaps:** identical basis to `0x06` above.

## 0x08 — Pause Recovery

- **Handler:** `api_wp2_pause_recovery` (inside `dji_flight`)
- **Purpose:** pause/resume ("recovery") control for an in-progress
  waypoint mission — functionally, the kind of command behind a companion
  app's "pause mission" / "resume mission" control.
- **Evidence:** same `.data` array as `0x06`/`0x07`. **Note on history:**
  two earlier analysis passes had this function's cmd_id transposed with
  `0x06`'s (reporting `pause_recovery` as the *first* entry, cmd_id `0x06`);
  a dedicated from-scratch third pass corrected this — `pause_recovery` is
  the *third* of the three cruise/pause entries, cmd_id `0x08`. Sits
  immediately before `0x09` (`api_wp2_download_wp_init_info`, below) in
  both array order and the broader `api_wp2_*` numbering.
- **Confidence / gaps:** same as `0x06` — mapping high-confidence,
  reachability unresolved, payload format not decoded.

## 0x09 — WP2 Download Waypoint Init Info

- **Handler:** `api_wp2_download_wp_init_info` (high confidence, clean
  self-name), inside `dji_flight`, func at `0x1b8c4`.
- **Purpose:** returns waypoint-mission init/header info ahead of a
  waypoint download — fits neatly between `pause_recovery` (`0x08`) and
  `download_waypoint` (`0x0d`) in the existing `api_wp2_*` numbering.
- **Evidence:** `.data` array row at vaddr `0xae110`. See
  `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §4/§6.
- **Confidence:** high on mapping and name; reachability unresolved;
  payload format not decoded.

## 0x0D — WP2 Download Waypoint

- **Handler:** `api_wp2_download_waypoint` (high confidence, clean
  self-name, repeats 3×), inside `dji_flight`, func at `0x1ad24`.
- **Purpose:** downloads waypoint-mission data to the requester.
- **Evidence:** `.data` array row at vaddr `0xae118`. **Independent
  confirmation of a name this project already had from a different
  source** — `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` lists
  `api_wp2_download_waypoint` among `dji_flight`'s known-by-string
  functions; the two sources agree exactly, and this table supplies the
  cmd_id that earlier pass couldn't recover.
- **Confidence:** high on mapping and name; reachability still unresolved;
  payload format not decoded.

## 0x0E — Get Max Point Num

- **Handler:** unresolved as a C identifier (medium confidence on
  purpose, from log text only), inside `dji_flight`, func at `0x1b41c`
  (48B).
- **Purpose:** the function's only identifying text is the log phrase
  `"flight reveice get_max_point_num"` (sic — reported verbatim, likely a
  source-level typo for "receive"). Read as "get the maximum waypoint
  count."
- **Evidence:** `.data` array row at vaddr `0xae120`.
- **Confidence:** medium on purpose (derived from a descriptive log
  string, not a confirmed C function identifier); high on the
  `(cmd_set, cmd_id)` mapping itself.

## 0x17 — WP2 Get Waypoint Index In List

- **Handler:** `api_wp2_get_wp_index_in_list` (high confidence, clean,
  early self-name), inside `dji_flight`, func at `0x1b44c`.
  **Not** to be confused with cmd_set `0x11` (ADSB)'s unrelated cmd_id
  `0x17` ("Push Avoidance Action Get") — different cmd_set entirely, just
  a coincidentally identical cmd_id byte.
- **Purpose:** looks up a waypoint's index within the active mission list.
- **Evidence:** `.data` array row at vaddr `0xae128`. The same ~1000B
  disassembly window also contains `go_stop_wp_ack_rec_handler` and
  `api_wp2_go_cmd_handle` — thematically consistent WP2 "go/stop waypoint"
  logic, so this may genuinely be one larger function cluster rather than
  a boundary-crossing artifact, but that was not confirmed by tracing
  control flow; reported with that caveat.
- **Confidence:** high on mapping and name; payload format not decoded.

## 0x18 — WP2 Info To Flight

- **Handler:** `api_wp2_info_to_flight` (high confidence, clean, early
  self-name), inside `dji_flight`, func at `0x1b220`.
- **Purpose:** pushes waypoint-mission info into the flight-control-facing
  side of `dji_flight` (exact mechanism not traced further).
- **Evidence:** `.data` array row at vaddr `0xae138`.
- **Confidence:** high on mapping and name; payload format not decoded.

## 0x19 — WP2 Mission Action Upload

- **Handler:** unresolved as a C identifier, inside `dji_flight`, func at
  `0x1e2a8` (84B).
- **Purpose:** the function's identifying text is the log line `"flight
  receive action upload cmd, data len = %d, buf[3] = %d"` — a WP2
  mission-action upload. That same log format is itself a concrete
  payload-shape clue: a length field and the byte at payload offset 3 are
  both referenced directly by the handler.
- **Evidence:** `.data` array row at vaddr `0xae140`. Companion/upload
  counterpart to `0x1a`'s download, immediately following it in array
  order.
- **Confidence:** medium on purpose (log-string-derived); high on the
  `(cmd_set, cmd_id)` mapping.

## 0x1A — GS Action Download

- **Handler:** `gs_api_action_download` (high confidence, clean — found by
  hand-correcting a padding-boundary miss; raw bytes confirm
  `...gs_api_action_download\0\0gs_mission_wp_...`), inside `dji_flight`,
  func at `0x1e2fc`.
- **Purpose:** download-direction counterpart to `0x19`'s upload, in the
  `gs_act_*`/`gs_mission_wp_action_*` WP2-mission-action family.
- **Evidence:** `.data` array row at vaddr `0xae148`.
- **Confidence:** high on mapping and name; payload format not decoded.

## 0x1E — GS Get Action Memory Info

- **Handler:** `gs_api_get_action_memory_info` (high confidence, clean,
  right at entry), inside `dji_flight`, func at `0x1e3fc`.
- **Purpose:** reports memory-usage info for the WP2 mission-action
  subsystem.
- **Evidence:** `.data` array row at vaddr `0xae150`. **Bounding note:**
  the next table row's address is ~8700 bytes away — that span is **not**
  one function; it's the start of a dense cluster of small
  `gs_act_*`/`gs_mission_wp_action_*` and `upgrade_*`/`read_nfz_data_file`
  (NFZ-upgrade family, see `cmdset_00_General.md`) helper functions with
  no other table row pointing into them. Only
  `gs_api_get_action_memory_info` itself (its first ~20-40 instructions)
  is attributed to this cmd_id.
- **Confidence:** high on mapping and name; payload format not decoded.

## 0x44 — Break Restore Waypoint Fly

- **Handler:** `api_wp2_break_restore_waypoint_fly` (inside `dji_flight`)
- **Purpose:** "break" (abort/interrupt) or "restore" (resume) a
  waypoint-mission flight already in progress — plausibly a lower-level
  primitive that `0x08`'s pause/recovery logic calls into, though that
  specific relationship was not traced or confirmed.
- **Evidence:** same `.data` array as the entries above, at a different
  offset within it (confirmed `R_ARM_RELATIVE`-backed, cmd word decoding
  to cmd_set `0x22` / cmd_id `0x44`).
- **Confidence / gaps:** same as `0x06` — mapping high-confidence,
  reachability unresolved (no caller found), payload format not decoded.

## 0x60 — Demo Mode Handle

- **Handler:** `sys_wm260_demo_mode_handle`, registered identically from 4
  separate platform/board-init functions inside `dji_sys`:
  `sys_platform_e1e_wm260_post_init`, `sys_platform_e1e_wm260l_post_init`,
  `sys_platform_e2_wm260_post_init`, `sys_platform_e2_wm260l_post_init`
  (names recovered from `dji_sys`'s `.gnu_debugdata` minidebuginfo — a
  genuine minidebuginfo section, unlike `dji_flight`, which only carries a
  `.gnu_debuglink` with no companion file; see
  `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §3).
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

## This cmd_set's `dji_flight` table is now fully decoded — 43 of 43 rows

The `.data` array in `dji_flight` that supplies every `0x22` entry above
(and several entries filed under other cmd_sets — `0x00`, `0x03`, `0x04`,
`0x11`, `0x1f`, and handler-confirmations under `0x02`/`0x0a`, all tagged
by the same table) runs vaddr `0xae040`–`0xae190`, **43 rows, all 43
decoded**. This corrects, rather than extends, the gap note that used to
be here: that note said the array was "rooted at vaddr `0xae0f8`" while
also claiming "at least 43 records total" — self-contradictory on its own
terms, since `0xae0f8`–`0xae190` is only 20 rows. The correct start
address, `0xae040`, was actually already on record in this project
(`14_FOLLOWUP_DEEPDIVE_FINDINGS.md`, Track H) — it just hadn't been
reconciled into this file, and that document had explicitly left all 39
of the array's extra rows as "Not determined." A dedicated
re-verification pass independently re-confirmed the `0xae040` start from
raw bytes and relocations, and — the actual new work here — decoded the
contents of all 39 previously-undecoded rows. See
`21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` for the full raw-byte table, the
name-resolution method (no `.gnu_debugdata` on this binary — a
string/log-based fallback was used instead), the shared `api_wp2_*`
dispatcher's calling convention, and every per-row caveat.
