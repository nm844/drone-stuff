# Cmd Set 0x01 — Special

Total known command IDs: 12

## 0x00 — Sdk Ctrl Mode Open/Close Nav

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

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

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — New Special App Control

Payload decoder: `special_new_special_app_control_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 24 | `special_new_special_app_control_unknown0` (Unknown0) | bytes |  |

## 0x04 — New Special Remote Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — SDK Ctrl Mode Arm/Disarm

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1A — SDK Ctrl Gimbal Speed Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1B — SDK Ctrl Gimbal Angle Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — SDK Ctrl Camera Shot Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — SDK Ctrl Camera Start Video Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — SDK Ctrl Camera Stop Video Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFF — UAV Loopback

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
