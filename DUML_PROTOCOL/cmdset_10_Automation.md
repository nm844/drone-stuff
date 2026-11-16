# Cmd Set 0x10 — Automation

Total known command IDs: 0

This cmd_set is empty in the public `dji-firmware-tools` Wireshark
dissector itself (`AUTO_UART_CMD_TEXT` exists as a table name in the
dissector source but is literally `{}` — no public source documents DJI's
waypoint/mission-automation command set at all), and remains at 0
concretely-enumerated cmd_ids after this project's own direct binary
disassembly. Unlike cmd_set `0x0c` (ESC), however, this project did
locate and then **rule out** every plausible registrar candidate, and
found the real architectural mechanism — so this gap is now well
understood, not just unresolved.

## What was found: the real mechanism, and why cmd_set 0x10 itself is a dead end

The real mechanism is in `dji_sys`: a "command agent" framework
(`sys_command_agent_init`/`_add`/`_config`/`_request`/`_task`) whose
registration loop (`sys_command_agent_config`) does call
`duss_event_register_dynamic_command` once per entry, using
`cmd_set`/`cmd_id` values that are **populated from a local JSON
configuration file `dji_sys` reads at its own startup** — not injected by
another daemon over Android Binder IPC, as an earlier pass of this project
originally hypothesized. That config file's path is not captured anywhere
in this firmware extraction, so its contents (and therefore any concrete
`cmd_set 0x10` cmd_ids it might register) could not be read. See
`04_WM260_DAEMON_FINDINGS.md`'s "Automation" section (as corrected) and
`08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md`'s "`dji_sys`'s
command-agent framework" section.

Every other plausible registrar was checked and ruled out directly,
rather than left open on a technicality:

- **`dji_flight`** (the actual flight-control-adjacent daemon): a
  dedicated follow-up pass, using a corrected PIC-addressing disassembly
  technique specific to this binary, confirmed cmd_set `0x10` is **not
  present anywhere** in it — not in any recovered table, any string, or
  any literal immediate before a registration-style call. See
  `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track H.
  - This same pass did find 4 real, named `dji_flight` waypoint-mission
    ("WP2") commands — but they belong to cmd_set `0x22` ("Demo Mode"),
    not `0x10`. See `cmdset_22_Demo_Mode.md`.
  - A separate, low-confidence lead — 4 fully-spelled `api_wp2_*` API
    strings reached only through an unresolved indirection, with no
    numeric cmd_id recoverable — was the origin of this track, and is
    superseded by the above resolution. See
    `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md`.
- **`dji_navigation`** (OpenCV-heavy waypoint/vision-tracking service):
  confirmed to not be a cmd_set endpoint at all.
- **`dji_autoflight`**: confirmed ruled out for cmd_set `0x10`, with a
  specific architectural reason (see
  `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md`).
- **`dji_perception`**: looked like a promising lead (plaintext
  `waypoint_mis_state`/`waypoint_job_state`/mission-config strings), but is
  a dead end for this purpose — those strings are field names of an
  embedded ROS-style self-describing message schema used by this binary's
  black-box/telemetry-logging subsystem, not DUML cmd_id names. Confirmed
  by an exhaustive triple cross-check (full disassembly scan, full
  relocation-table scan, raw hex-operand grep): none of those string
  addresses is referenced by any instruction anywhere in `.text`.
  `dji_perception` imports no `duss_event_register_dynamic_command`-family
  symbol at all. See `04_WM260_DAEMON_FINDINGS.md`.
- A whole-tree grep sweep for ESC/Automation-adjacent terms found
  `libdsp_frwk.so`'s `MODULE_NAV_WAYPOINT` string, which turned out to be
  1 of 42 generic `MODULE_NAV_*` logging-subsystem tags, unrelated to
  cmd dispatch — a dead end, not a lead.

**Bottom line:** cmd_set `0x10` is architecturally real (DJI's own naming
convention for it, `AUTO_UART_CMD_TEXT`, exists in the public dissector
source) and is registered somewhere via `dji_sys`'s command-agent
framework, driven by a local config file not present in this firmware
extraction — but no concrete `(cmd_set 0x10, cmd_id)` pair has been
recovered, and every binary that could plausibly host it in this
extraction has been checked. This is reported as a genuine, now
architecturally-explained gap, not an open mystery.
