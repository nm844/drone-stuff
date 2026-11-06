# Extended device addressing — from the aircraft's own routing config

The classic DUML wire header's 5-bit `sender`/`receiver` field (see
`00_FRAME_FORMAT.md`) only has 32 device-type slots. This firmware's newer
message-bus layer (the `duss_*`/`mb_*` API noted in
`01_BINARY_ANALYSIS_FINDINGS.md` §3) uses a wider addressing scheme, and the
mapping from that scheme's names to hex IDs is stored in plain JSON on the
aircraft's own Linux filesystem — no disassembly needed:
`1502_WM260_E1E/unzipped/system.img:/etc/dji.json`, under each service's
own `mb_route_table`.

Cross-referencing every service's route table in that file against its
`target` name gives this device-name → ID-range table (IDs are hex, as
written in the JSON):

| Name | IDs seen | Likely maps to classic DeviceType |
|---|---|---|
| `whoami` | `00` | (self) |
| `camera` | `1,10-17` | Camera (1) |
| `mobile` | `20,21,25,27` | App (2) |
| `flight` | `30,36` | Flight Controller (3) |
| `gimbal` | `40` | Gimbal (4) |
| `cboard` | `50` | Center Board (5) |
| `rc` | `60,61,65` | Remote Control (6) |
| `network` | `70,71,76` | Wi-Fi (7) |
| `ve_air` | `80-87` | HD transmission MCU air side (9)? |
| `vt_air` | `1,90-96` | — new in this generation, see below |
| `pc` | `a0,a1,a3,a7` | PC (10) |
| `battery` | `b0,b1,b2` | Battery (11) |
| `esc` | `c0-c3` | ESC (12) |
| `ve_gnd` | `d0-d5` | — |
| `vt_gnd` | `e0,e5-e7` | — |
| `s_to_p_air` | `f0-f5` | Serial-to-parallel air (15) |
| `mvision` | `1,110-116` | Monocular (17)-adjacent, newer numbering |
| `bvision` | `3,4,120-127` | Binocular (18)-adjacent, newer numbering |
| `glass` | `1c0-1c6` | — (AR/FPV glasses accessory) |
| `test` | `1e0-1e2` | — (factory test harness) |
| `blackbox` | `1d0,1d1,1d7` | — (flight data recorder service) |
| `misc` | `174` | — |

Two things worth noting:
- The one-digit IDs (`camera`→`1`, `vt_air`→`1`, `mvision`→`1`) collide
  because they come from *different services'* route tables, each of which
  only needs to disambiguate targets relevant to itself — this is a
  per-service local table, not one global flat address space.
- `vt_air`/`vt_gnd`/`ve_air`/`ve_gnd`/`mvision`/`bvision`/`glass`/`blackbox`
  are **not** in the classic 32-entry `DJI_DUMLv1_SRC_DEST_TEXT` table (see
  `00_FRAME_FORMAT.md`) — they're newer subsystems (video transmission,
  monocular/binocular vision computers, AR glasses, the flight-data-recorder
  service) that this product generation added on top of the original DUML
  device-type space, addressed through the message-bus layer rather than
  the raw 11-byte DUML header.

## A few more command-meaning fragments, read (not disassembled) from binaries

Plain `strings` extraction (reading embedded text, not disassembling code)
on a few daemons turned up some direct confirmation of existing
documentation and a couple of small new facts:

- `dji_perception` (1502 image) contains the message-bus layer's own
  error-path format strings, e.g. `"[ERROR][ADS-B]cmd_id:0x%x NOT registet
  ack func."` / `"...NOT registet request func."` / `"...register FAIL."`
  — confirming that cmd_set 0x11 (ADS-B) commands are dispatched through a
  **register-a-callback-per-cmd_id** model at this layer (consistent with
  the `duss_event_register_dynamic_command` API noted in
  `01_BINARY_ANALYSIS_FINDINGS.md`), rather than a fixed switch table.
- `dji_rcam` (the lens-control daemon, 1502 image) contains these internal
  function-name strings: `lens_ctrl_cmd_set_adjustment_data`,
  `lens_ctrl_cmd_set_aperture`, `lens_ctrl_cmd_set_log_level`,
  `lens_ctrl_cmd_set_mode`, `lens_ctrl_cmd_set_shutter_para` — independent
  confirmation that the real camera control surface groups aperture,
  shutter, mode, and lens-adjustment settings exactly as the public Camera
  command set (cmd_set 0x02) documents, consistent with the `dji_camera3`
  parameter strings already noted in `01_BINARY_ANALYSIS_FINDINGS.md` §4.

No new byte-level payload decodes came out of this pass — these are
architecture/addressing confirmations, not new field layouts. The
`fly_action_*.json` / `test_action.json` files on the aircraft's filesystem
were also found during this search; they are the factory QA flight-test
harness's maneuver and PID-tuning configuration (take-off/hover/fly-route
test sequences with their control gains), not DUML protocol data, and were
set aside as out of scope for this document.
