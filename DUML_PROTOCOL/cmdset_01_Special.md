# Cmd Set 0x01 — Special

Total known command IDs: 12

## 0x00 — Sdk Ctrl Mode Open/Close Nav

_Not decoded._ By name, this almost certainly toggles the aircraft's SDK/'Nav'-authority control mode on or off -- the gate a Mobile/Onboard SDK client must open before cmd_ids 0x05/0x1a/0x1b/0x20/0x21/0x22 in this same cmd_set are honoured. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x01 — Old Special App Control

Payload decoder: `special_old_special_app_control_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `special_old_special_app_control_unknown0` (Unknown0) | uint8 |  |
  | 1 | 1 | `special_old_special_app_control_unknown1` (Unknown1) | uint8 |  |
  | 2 | 2 | `special_old_special_app_control_unknown2` (Unknown2) | uint8 |  |
  | 4 | 1 | `special_old_special_app_control_unknown4` (Unknown4) | uint8 |  |
  | 5 | 1 | `special_old_special_app_control_unknown5` (Unknown5) | uint8 |  |
  | 6 | 1 | `special_old_special_app_control_unknown6` (Unknown6) | uint8 |  |
  | 7 | 2 | `special_old_special_app_control_unknown7` (Unknown7) | uint8 |  |
  | 9 | 1 | `special_old_special_app_control_checksum` (Checksum) | uint8 | Previous payload bytes xor'ed together with initial seed 0. |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `special_old_special_app_control_status` (Status) | uint8 |  |

## 0x02 — Old Special Remote Control

_Not decoded._ Legacy counterpart to cmd_id 0x01 'Old Special App Control' (which does have a public decoder) and to 0x04 'New Special Remote Control' -- plausibly an older RC-stick/virtual-RC-channel override frame sent by a special controller rather than the normal app. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x03 — New Special App Control

Payload decoder: `special_new_special_app_control_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 24 | `special_new_special_app_control_unknown0` (Unknown0) | bytes |  |

## 0x04 — New Special Remote Control

_Not decoded._ Newer counterpart to 0x02, and sibling to the already-decoded 0x03 'New Special App Control' (a flat 24-byte opaque blob per the public dissector) -- plausibly a newer-format virtual-RC/stick-override frame. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x05 — SDK Ctrl Mode Arm/Disarm

_Not decoded._ By name, an SDK-initiated motor arm/disarm command -- the kind of command a companion-computer flight-automation client would send to start or stop the motors without touching the physical RC stick/throttle gesture. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1A — SDK Ctrl Gimbal Speed Ctrl

_Not decoded._ By name, an SDK-initiated gimbal angular-velocity command (pitch/roll/yaw speed, analogous to the OSDK 'gimbal speed control' API) -- distinct from the normal cmd_set 0x04 Gimbal Control command because it carries SDK control authority rather than RC-stick authority. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1B — SDK Ctrl Gimbal Angle Ctrl

_Not decoded._ By name, an SDK-initiated absolute gimbal-angle command (pitch/roll/yaw target angle), the companion to 0x1a's rate-based control -- analogous to OSDK's 'gimbal angle control' API. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x20 — SDK Ctrl Camera Shot Ctrl

_Not decoded._ By name, an SDK-initiated 'take a photo now' trigger, bypassing the normal cmd_set 0x02 Camera 'Do Capture Photo' path's RC/app-button semantics in favour of SDK control authority. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — SDK Ctrl Camera Start Video Ctrl

_Not decoded._ By name, an SDK-initiated 'start recording video' trigger, the SDK-authority counterpart to the normal camera record-start command. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — SDK Ctrl Camera Stop Video Ctrl

_Not decoded._ By name, an SDK-initiated 'stop recording video' trigger, pairing with 0x21. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFF — UAV Loopback

_Not decoded._ Per the task hint and the 0xFF convention used elsewhere in DUML, this is plausibly a simple diagnostic echo: a client sends an arbitrary payload and the aircraft mirrors it back unchanged, used for link-latency/sanity testing. I was not able to confirm this structurally, only by naming convention. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
