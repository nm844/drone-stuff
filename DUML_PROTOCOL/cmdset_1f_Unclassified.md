# Cmd Set 0x1f — Unclassified

Total known command IDs: 2

**Not part of the public `dji-firmware-tools` Wireshark dissector, and not
previously catalogued anywhere in this project** — confirmed absent from
both `ALL_COMMANDS.csv` and `INDEX.md` (`cut -d',' -f1 ALL_COMMANDS.csv |
sort -u` lists no `0x1f` cmd_set at all) before this pass. Found by direct
disassembly of `dji_flight`'s confirmed `R_ARM_RELATIVE`-relocated `.data`
command array (vaddr `0xae040`–`0xae190`), the same array documented in
full in `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` and
`cmdset_22_Demo_Mode.md`.

**No name is given for this cmd_set.** Unlike this project's other two
binary-RE'd cmd_sets (`0x22` "Demo Mode," named from a handler found in a
different binary; `0x23` "Smart," named from a literal DWARF enumerator,
`SS_MB_CMD_SET_SMART`), no string, enum, or comment anywhere in either
examined binary names "`0x1f`" itself, and its two known cmd_ids belong to
two entirely unrelated subsystems (an NFZ-database-upgrade device-state
query, and a WP2 waypoint-mission-action accessor) with no shared theme.
Inventing a domain label here would overstate what's actually known; the
filename/title use "Unclassified" as a neutral placeholder, not a
discovered name.

## 0x05 — GS Get Min/Max Action Id

- **Handler:** `gs_api_get_min_max_action_id` (high confidence, clean,
  repeats), inside `dji_flight`, func at `0x1e348` (`0x1e348`–`0x1e3fc`,
  180B).
- **Purpose:** part of the `gs_act_*`/`gs_mission_wp_action_*` WP2
  mission-action family documented under cmd_set `0x22` elsewhere in this
  array (see `cmdset_22_Demo_Mode.md`'s `0x19`/`0x1a`/`0x1e`) — returns
  the minimum/maximum valid action-id range for that subsystem. **Not**
  NFZ-related, despite sharing this cmd_set with `0x11` below.
- **Evidence:** confirmed `R_ARM_RELATIVE`-relocated `.data` array row at
  vaddr `0xae158`; cmd word decodes to cmd_set `0x1f` / cmd_id `0x05`.
- **Confidence:** high on the `(cmd_set, cmd_id)` → function mapping and
  the name. Low/unresolved on runtime reachability — no caller, vtable
  slot, or other reference to this function's address was found anywhere
  else in the binary.
- **Not determined:** payload format/fields; which client is expected to
  send it.

## 0x11 — NFZ Upgrade Get Device State

- **Handler:** `nfz_upgrade_get_device_state` (high confidence, clean),
  inside `dji_flight`, func at `0x20d3c` (`0x20d3c`–`0x20d78`, 60B).
- **Purpose:** part of the same NFZ (no-fly-zone) geofence-database
  upgrade family documented under cmd_set `0x00` in
  `cmdset_00_General.md` (`nfz_upgrade_get_version`/`_entry`/`_start`/
  `_data`/`_end`, all compiled from the embedded source path
  `hardware/dji/service/flight/src/applications/nfz_data_upgrade/...`
  that `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` already found in
  this same binary) — reuses the "get device state" semantic of cmd_set
  `0x00`/`0x0c` under this new cmd_set instead of (or in addition to) it.
- **Evidence:** `.data` array row at vaddr `0xae070`; cmd word decodes to
  cmd_set `0x1f` / cmd_id `0x11`.
- **Confidence:** high on mapping and name; reachability unresolved;
  payload format not decoded (though see `cmdset_00_General.md`'s `0x0c`
  for a sibling function's ack-result/ack-buf-len format-string clue,
  which may apply here too but was not independently confirmed for this
  specific function).

See `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` for the full array
re-derivation, name-resolution method, and every caveat that applies here.
