# Cmd Set 0x06 — Remote Control

Total known command IDs: 85

## 0x01 — RC Channel Params Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x02 — RC Channel Params Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — RC Calibiration Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — RC Physical Channel Parameter Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — RC Parameter Get/Push

Payload decoder: `rc_push_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `rc_push_param_aileron` (Aileron) | uint16 |  |
  | 2 | 2 | `rc_push_param_elevator` (Elevator) | uint16 |  |
  | 4 | 2 | `rc_push_param_throttle` (Throttle) | uint16 |  |
  | 6 | 2 | `rc_push_param_rudder` (Rudder) | uint16 |  |
  | 8 | 2 | `rc_push_param_gyro_value` (Gyro Value) | uint16 |  |
  | 10 | 1 | `rc_push_param_wheel_info` (Wheel Info) | uint8 |  |
  | 10 | 1 | `rc_push_param_wheel_click_status` (Wheel Click Status) | uint8 | mask:`0x01` |
  | 10 | 1 | `rc_push_param_wheel_offset` (Wheel Offset) | uint8 | mask:`0x3e` |
  | 10 | 1 | `rc_push_param_not_wheel_positive` (Not Wheel Positive) | uint8 | mask:`0x40` |
  | 10 | 1 | `rc_push_param_wheel_changed` (Wheel Changed) | uint8 | mask:`0x80` |
  | 11 | 1 | `rc_push_param_masked0b` (Masked0B) | uint8 |  |
  | 11 | 1 | `rc_push_param_go_home_button_pressed` (Go Home Button Pressed) | uint8 | mask:`0x08` |
  | 11 | 1 | `rc_push_param_mode` (Mode) | uint8 | mask:`0x30` |
  | 11 | 1 | `rc_push_param_get_foot_stool` (Get Foot Stool) | uint8 | mask:`0xc0` |
  | 12 | 1 | `rc_push_param_masked0c` (Masked0C) | uint8 |  |
  | 12 | 1 | `rc_push_param_custom2` (Custom2) | uint8 | mask:`0x08` |
  | 12 | 1 | `rc_push_param_custom1` (Custom1) | uint8 | mask:`0x10` |
  | 12 | 1 | `rc_push_param_playback_status` (PlayBack Status) | uint8 | mask:`0x20` |
  | 12 | 1 | `rc_push_param_shutter_status` (Shutter Status) | uint8 | mask:`0x40` |
  | 12 | 1 | `rc_push_param_record_status` (Record Status) | uint8 | mask:`0x80` |

  *if (payload:len() >= offset+1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 13 | 1 | `rc_push_param_band_width` (Band Width) | uint8 |  |

## 0x06 — RC Master/Slave Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x07 — RC Master/Slave Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x08 — RC Name Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x09 — RC Name Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0A — RC Password Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0B — RC Password Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0C — RC Connected Master Id Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0D — RC Connected Master Id Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0E — RC Available Master Id Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0F — RC Search Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x10 — RC Search Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x11 — RC Master/Slave Switch Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x12 — RC Master/Slave Switch Conf Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x13 — RC Request Join By Slave

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x14 — RC List Request Join Slave

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x15 — RC Delete Slave

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x16 — RC Delete Master

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x17 — RC Slave Control Right Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x18 — RC Slave Control Right Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x19 — RC Control Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1A — RC Control Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1B — RC GPS Info Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1C — RC RTC Info Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1D — RC Temperature Info Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1E — RC Battery Info Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1F — RC Master/Slave Conn Info Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — RC Power Mode CE/FCC Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — RC Power Mode CE/FCC Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — RC Gimbal Ctr Permission Request

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x23 — RC Gimbal Ctr Permission Ack

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x24 — RC Simulate Flight Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x25 — RC Simulate Flight Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x26 — RC AETR Value Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x27 — RC Detection Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x28 — RC Gimbal Control Access Right Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x29 — RC Slave Control Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2A — RC Slave Control Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2B — RC Gimbal Control Speed Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2C — RC Gimbal Control Speed Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2D — RC Self Defined Key Func Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2E — RC Self Defined Key Func Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2F — RC Pairing

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x30 — RC Test GPS

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x31 — RC RTC Clock Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x32 — RC RTC Clock Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x33 — RC Gimbal Control Sensitivity Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x34 — RC Gimbal Control Sensitivity Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x35 — RC Gimbal Control Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x36 — RC Gimbal Control Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x37 — RC Enter App Mode Request

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x38 — RC Calibration Value Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x39 — RC Master Slave Connect Status Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3A — RC 2014 Usb Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3B — RC Id Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3C — RC Coach Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3F — RC Mater/Slave Id

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x42 — RC Follow Focus Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x47 — RC App Special Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x48 — RC Freq Mode Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4C — RC Pro Custom Buttons Status Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x50 — RC Push Rmc Key Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x51 — RC Push To Glass

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x52 — RC Push LCD To MCU

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x53 — RC Unit Language Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x54 — RC Unit Language Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x55 — RC Test Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x56 — RC Quiry Role

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x57 — RC Quiry Ms Link Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x58 — RC Work Function Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x59 — RC Work Function Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x98 — Follow Focus2 Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x99 — Follow Focus Info Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF0 — RC RF Cert Config Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF0 — (name unknown)

Payload decoder: `rc_set_rf_cert_config_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `rc_set_rf_cert_config_field0` (Field 0) | uint8 |  |
  | 1 | 1 | `rc_set_rf_cert_config_field1` (Field 1) | uint8 |  |
  | 2 | 1 | `rc_set_rf_cert_config_field2` (Field 2) | uint8 |  |
  | 3 | 2 | `rc_set_rf_cert_config_field3` (Field 3) | uint16 |  |
  | 5 | 1 | `rc_set_rf_cert_config_field5` (Field 5) | uint8 |  |
  | 6 | 1 | `rc_set_rf_cert_config_field6` (Field 6) | uint8 |  |
  | 7 | 1 | `rc_set_rf_cert_config_field7` (Field 7) | uint8 |  |

## 0xF5 — RC Test Stick Value

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF6 — RC Factory Get Board Id

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF7 — RC Push Buzzer To MCU

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF8 — RC Stick Verification Data Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF9 — RC Post Calibiration Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFA — RC Stick Middle Value Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
