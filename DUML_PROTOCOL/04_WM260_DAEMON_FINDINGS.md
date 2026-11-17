# WM260 (Mavic 3) daemon/binary mining — findings

Two Workflow passes (7 agents, then a 3-agent follow-up) over the
Android system files extracted from the WM260 firmware package obtained
in this session (see `02_WM265_MAVIC3_NFZ_FINDINGS.md` §4c for how that
firmware was obtained and decrypted). Each finding below was independently
cross-checked against `duml_py/duml/commands.json` and, where possible,
verified by matching a disassembled callback pointer against `nm -D`'s
exported-symbol table — not just string-matched.

## Tooling notes (apply to any future pass on this file set)

- This sandbox's `objdump` (binutils 2.42) is built x86-64-only and
  cannot disassemble AArch64 at all (`can't disassemble for architecture
  UNKNOWN`), despite `readelf` correctly identifying the target. Use
  `llvm-objdump --triple=aarch64`, or a direct `capstone` (`CS_ARCH_ARM64`)
  + `pyelftools` script (vaddr→file-offset via `PT_LOAD` segment lookup) —
  both work. `objcopy` has the same x86-64-only limitation.
- Several stripped binaries (`dji_mb_ctrl`, `dji_mb_parser`, `dji_perception`,
  `dji_sys`) carry a `.gnu_debugdata` section — Fedora-style minidebuginfo,
  an XZ-compressed mini-ELF with a real, unstripped local symbol table.
  Extract via `pyelftools`' section `.data()` + `xz -d`; it can turn a
  "fully stripped, no symbols" binary into one with real function names,
  for free. Worth checking on every stripped binary in this tree before
  assuming a name can't be recovered.
- The command-registration convention, confirmed across multiple binaries:
  a literal `cmd_set` immediate loaded into `w1`, `cmd_id` into `w2`,
  immediately before a `bl` to `duss_event_register_dynamic_command`
  (exported from `libduml_frwk.so`). Not every daemon's registrations are
  statically recoverable this way, though — several route through
  runtime/Binder-driven tables instead (see the Automation section below).

## New cmd_sets: `0x22` (Demo Mode) and `0x51` (Route Switch)

Both outside this project's documented `0x00`-`0x11` range, both added to
the Lua dissector source (`dji-dumlv1-proto.lua`) and regenerated through
into `commands.json`/`registry_data.cpp` — not hand-patched only in this
repo's own derived files.

- **`0x51`/`0x05` "Route Switch"**: found in `libduml_frwk.so`'s built-in
  dynamic-command table (`duss_event_create_dynamic_cmd_tbl`, a literal
  data table at vaddr `0x190ff8` registered automatically for *every*
  message-bus client, i.e. every daemon that links this library — see
  also the three other new `0x00` commands below, from the same table).
  Callback pointer matches exported symbol `duss_event_route_switch`
  exactly; confirmed by its own debug strings (`"RS: route switch
  configuration error!"`, `"RS: route switch host id = %#x"`). Likely an
  internal link-mode control (e.g. wired/wireless), not obviously
  app/RC-facing. **Precision note, from `14_FOLLOWUP_DEEPDIVE_FINDINGS.md`
  Track E:** this table (and the 3 other `0x00` entries below from it) was
  decoded from the **E2 (aarch64)** build of `libduml_frwk.so`. The
  **E1E (32-bit ARM)** build's equivalent table, independently re-decoded,
  has identical content at a different address (`0x1098fc`) — so this
  finding holds for both chips, but future table dumps from this file
  should state which build they came from, since this document previously
  didn't.
- **`0x22`/`0x60` "Demo Mode Handle"**: found via direct disassembly of
  `dji_sys`, registered from 4 separate platform-init functions
  (`sys_platform_{e1e,e2}_wm260[l]_post_init`), each with its own named
  handler (`sys_wm260_demo_mode_handle` and 3 platform siblings, recovered
  from `dji_sys`'s `.gnu_debugdata`). Never observed exercised from any
  external-facing path examined — plausibly a factory/retail-demo-unit
  feature not normally reachable over the production app/RC link.

## New commands under already-known cmd_sets

All four found by the same literal-immediate-before-`bl` pattern, in
`libduml_frwk.so`'s built-in table or `dji_sys`'s platform-init functions:

| cmd_set | cmd_id | Name | Handler | Confidence |
|---|---|---|---|---|
| 0x00 General | 0x2f | Trans Diag Event | `duss_trans_diag_event` | high |
| 0x00 General | 0x89 | Shell Command | `duss_event_shell` (confirmed via `"SHELL: duss shell_command %s"` strings) | high |
| 0x00 General | 0xaa | Node Sniffer Request | `duss_event_node_sniffer_req` | high |
| 0x00 General | 0xa3 | USB State Report | `sys_wm260_usb_state_handle` (+ platform siblings) | high |
| 0x04 Gimbal | 0x69 | Event Input Report | `sys_event_input_report` | **medium** — the numeric `(cmd_set, cmd_id)` pair is as solid as the others; the "Gimbal" semantic label is only `enums.py`'s generic cmd_set-level convention, and the handler's name doesn't obviously fit gimbal control. Flagged, not asserted. |

**Independent confirmation of already-known-but-undecoded commands** (not
new, but now binary-verified rather than only dissector-asserted):
`cmd_set 3/0xd7` "FlyC Flight Record Get" (handler `request_fc_log`),
`cmd_set 0/0xf0` "Log Push" (handler `delete_v1_obj`/`create_v1_obj`),
`cmd_set 6/0x3a` "RC 2014 Usb Mode Set" (handler `sys_ac103_usb_otg` /
`sys_wm162_usb_otg` — also served as the ground-truth check validating
the `w1=cmd_set, w2=cmd_id` argument order used throughout this document).

**Correction (2026-11-17, see `21_PAYLOAD_DECODE_SWEEP_FINDINGS.md`):** this
binding does not hold up on re-examination. `sys_ac103_usb_otg`/
`sys_wm162_usb_otg` are real code in `dji_sys`, but reached only from
`sys_platform_ac103_init`/`sys_platform_e1e_wm162_init` — different DJI
product boards' platform-init paths, confirmed by their own embedded
source-file strings, distinct from this WM260 image's own
`sys_platform_e1e_wm260_init`/`sys_platform_e2_wm260_init`. `dji_sys` is a
shared multi-product binary; the ac103/wm162 branch is never reached at
runtime on this aircraft (board selection is a boot-time Android property
per `02_DEVICE_ADDRESSING_EXTENDED.md`). Separately, the handler's own
internal dispatch key (a `uint16` compared against `0x0500`/`0x1301`)
doesn't cleanly decode as `(cmd_set, cmd_id) = (6, 0x3a)` under either byte
order anyway, so it may not even be DUML-triggered. No replacement handler
for `0x3a` was found on this firmware — left as unresolved, not
re-asserted.

**Field-level confirmation of existing Camera commands**, from
`dji_camera3`'s own embedded parameter-name strings, cross-checked
programmatically against all 877 (now 884) `commands.json` entries: ~25
confirmed matches (`focus_mode`→0x24/0x25, `shutter_speed`→0x28/0x29,
`aperture`→0x26/0x27, `ae_meter`→0x22/0x23, and about 20 more — see the
full list in the workflow transcript if needed). A further ~35 parameter
strings (`shutter_angle`, `beauty`, `cinema_metadata`, `eis_status`,
`slowmotion_ratio`, …) do **not** match any existing cmd_id; the most
likely explanation, not confirmed, is that they're valid payload *values*
of the existing generic `0xc2`/`0xc3` "Param Name Set/Get" commands
(decode_status still `none`) rather than separate numbered commands —
a good lead for whoever decodes those two commands' payload format next.

## Device addressing: resolved

Full write-up moved to `02_DEVICE_ADDRESSING_EXTENDED.md` (the right home
for it, next to the existing route-table material) — summary: device
identity is centralized per-board in `dji_sys`, sourced from one Android
boot property (`ro.boot.device`) per board image, with a disassembly-
confirmed canonical 32-slot DeviceType name table in `libduml_frwk.so`
that both confirms and extends what that doc already had from the JSON
route tables.

## Automation (`cmd_set 0x10`) — still undocumented; real mechanism located, not statically enumerable

**Update, see `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track H:** the one
still-open lead mentioned below (`dji_flight`'s `api_wp2_*` handlers) was
chased further. Cmd_set `0x10` itself is now confirmed **not present
anywhere** in `dji_flight` — ruling it out directly rather than leaving it
open on a technicality. A specific 19-entry dispatch table the follow-up
pass initially thought it had recovered turned out, on independent
re-verification, to be misread C++ RTTI/vtable data, not a real table —
that specific claim should not be trusted. A different, separately-found
`.data` array (confirmed via real `R_ARM_RELATIVE` relocations) tags
three of the `api_wp2_*` cruise-velocity/pause-recovery functions under
cmd_set `0x22` — `set_global_cruise_vel`→cmd_id `0x06`,
`get_global_cruise_vel`→cmd_id `0x07`, `pause_recovery`→cmd_id `0x08` —
and a fourth (`break_restore_waypoint_fly`) under `0x22`/`0x44`: cmd_set
`0x10` is not registered in `dji_flight` at all, and these specific
waypoint functions belong to `0x22` ("Demo Mode") instead. This mapping,
including the exact per-function ordering, is now **independently
confirmed** by a dedicated third pass done entirely from scratch (an
earlier correction had the three-function order transposed —
`pause_recovery` is last, `0x08`, not first).

**Correction (2026-11-17), see `21_PAYLOAD_DECODE_SWEEP_FINDINGS.md` and
`cmdset_22_Demo_Mode.md`'s "Known gap" section for the full detail:** this
array is actually rooted at vaddr `0xae038`, not `0xae0f8` as earlier
stated here (`0xae0f8` is just the row for `0x06`, 24 rows into the
table, not the table's start) — directly re-derived from the raw bytes.
From `0xae038`, the array decodes to sensible `(cmd_set, cmd_id)` pairs
across 8 cmd_sets (`0x00, 0x02, 0x03, 0x04, 0x0a, 0x11, 0x1f, 0x22`)
through vaddr `0xae190` inclusive — **44 raw 8-byte rows total**, closely
confirming (not correcting) this doc's original "43+" estimate. A
separate 2026-11-17 re-count, from a different payload-decode pass,
reported "20 records... spanning only cmd_sets `{0x02, 0x04, 0x0a, 0x1f,
0x22}`" — that figure was not independently reconciled against this
direct recount (it may describe a subset or a different counting
convention) and the two should not be assumed to agree. Of the 44 rows,
cmd_set `0x22` alone accounts for 16; only 4 of those 16 (`0x06, 0x07,
0x08, 0x44`) plus `0x60` (found separately, in `dji_sys`) have been
decoded and tied to a named function so far. The remaining ~12 `cmd_set
0x22` rows, plus the rows for the other 7 cmd_sets in this same array,
are a concrete, bounded lead for a future pass.

**Update, see `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` for the full
follow-up pass:** the "Binder-exposed command agent" framing further below
is **corrected** by that later pass — `sys_command_agent_*` turns out
to have zero `.dynsym` exports, so nothing outside `dji_sys` can call it;
the actual `cmd_set`/`cmd_id` values are populated from a local JSON config
file read by `dji_sys` itself at startup (not injected by another daemon
over Binder), and that file's path isn't captured in this firmware
extraction. That same follow-up pass also checked and ruled out `dji_flight`,
`dji_navigation`, and (more specifically than the one-line note below)
`dji_autoflight` as the cmd_set `0x10` registrar — see that document for
details, including one still-open, low-confidence lead (`dji_flight`'s
`api_wp2_*` waypoint-mission handler functions, reachable through an
indirection this project's tooling couldn't resolve).

`dji_perception` looked like a promising lead (plaintext
`waypoint_mis_state`/`waypoint_job_state`/mission-config strings) but is
a dead end for this purpose: those strings are field names of an embedded
ROS-style self-describing message schema (`dji_flightsystem_msgs/
WpProtocolStorage`) used by this binary's black-box/bag telemetry-logging
subsystem, not DUML cmd_id names — confirmed by an exhaustive check that
none of those string addresses is referenced by any instruction anywhere
in the binary's `.text` (triple cross-checked: full capstone disassembly
scan, full relocation-table scan, raw hex-operand grep). `dji_perception`
imports no `duss_event_register_dynamic_command`-family symbol at all.

The real mechanism was found in `dji_sys`: a "command agent" framework
(`sys_command_agent_init/_add/_config/_request/_task`) that, per the
original hypothesis here, let *other* daemons register their own
`cmd_set`+`cmd_id` arrays at runtime over Android Binder IPC. This is
architecturally real (the registration loop, `sys_command_agent_config`,
does call `duss_event_register_dynamic_command` once per entry) — **but
the Binder-IPC part of that hypothesis is now disproven** (see the Update
note above): the actual `cmd_set`/`cmd_id` values live in a local JSON
config file `dji_sys` reads itself, not in a runtime Binder registration
from another daemon. This is still the same "needs full control-flow
decompilation of the specific daemon, or live traffic" limitation
`01_BINARY_ANALYSIS_FINDINGS.md` §3 already flagged — now narrowed to a
specific, named (and corrected) mechanism rather than a general
"per-daemon tables exist somewhere" statement.

A direct `grep` sweep across the whole extracted tree for
ESC/Automation-adjacent terms (run directly, not via a declining
sub-agent — see "What I didn't push on" below) found `libdsp_frwk.so`'s
`MODULE_NAV_WAYPOINT` string, which turned out to be 1 of 42 generic
`MODULE_NAV_*` logging-subsystem tags, unrelated to cmd dispatch.

## ESC (`cmd_set 0x0c`) — no conclusive finding

Still nothing concrete. `libdsp_frwk.so` does contain a second, distinct,
non-`duss_event_register_dynamic_command`-based cmd-dispatch mechanism
(`ss_hal_mb_set_req_callback` over a runtime `.bss` table, with a log
string literally naming `"cmd_set 0x%02x"`), but it has zero found
callers within that binary and no static table content to read — a
plausible ESC/motor-mailbox cousin of the main DUML dispatch mechanism,
but not enumerable from the files examined this session.

## Ruled out: `dji_dcs`

Not a DUML daemon at all — confirmed via its minimal imports and
decompressed `.gnu_debugdata`. It's a trivial CLI (`dji_config_store`
client tool) for getting/setting arbitrary string keys in a separate
Android-Binder key/value config-store service (`libdcs.so`, `IDCSService`
over Binder) that has no `duss_event_*` references anywhere.

## What I didn't push on

Two sub-agent tasks in the first workflow pass declined to run, each
citing the dual-use sensitivity of activation/unlock-mechanism research:
one assigned to `dji_sec`/`dji_amt` (the activation/account-binding
daemon — the part of this that's genuinely closest to the sensitive
area), and one assigned to a whole-tree grep sweep for ESC/Automation
terms (which, on reflection, isn't actually about NFZ/unlock at all — ESC
is motor control, Automation is waypoint missions — so that sweep was
re-run directly, by hand, with the result above). `dji_sec` itself
remains unanalyzed; left for the project owner's explicit call rather
than decided unilaterally either way.
