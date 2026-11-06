# Cmd Set 0x05 — Center Board

Total known command IDs: 18

## 0x00 — Center Open/Close Virtual RC

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x01 — Center Virtual RC Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x02 — Center Push Batt Dynamic Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — Center Control Uav Status Led

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — Center Transform Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — Center Req Push Bat Normal Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — Center Battery Common

Payload decoder: `center_brd_center_battery_common_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `center_brd_center_battery_common_relative_capacity` (Relative Capacity) | uint8 | Remaining Capacity percentage |
  | 1 | 2 | `center_brd_center_battery_common_current_pv` (Current Pv) | uint16 | Current Pack Voltage |
  | 3 | 2 | `center_brd_center_battery_common_current_capacity` (Current Capacity) | uint16 | Current Remaining Capacity |
  | 5 | 2 | `center_brd_center_battery_common_full_capacity` (Full Capacity) | uint16 | Full Charge Capacity |
  | 7 | 1 | `center_brd_center_battery_common_life` (Life) | uint8 | Life Percentage |
  | 8 | 2 | `center_brd_center_battery_common_loop_num` (Loop Num) | uint16 | Cycle Count |
  | 10 | 4 | `center_brd_center_battery_common_error_type` (Error Type) | uint32 |  |
  | 14 | 2 | `center_brd_center_battery_common_current` (Current) | uint16 |  |
  | 16 | 4 | `center_brd_center_battery_common_cell_voltage_0` (Cell Voltage 0) | uint32 |  |
  | 20 | 4 | `center_brd_center_battery_common_cell_voltage_1` (Cell Voltage 1) | uint32 |  |
  | 24 | 4 | `center_brd_center_battery_common_cell_voltage_2` (Cell Voltage 2) | uint32 |  |
  | 28 | 2 | `center_brd_center_battery_common_serial_no` (Serial No) | uint16 | Battery Serial Number |
  | 30 | 2 | `center_brd_center_battery_common_unknown1e` (Unknown1E) | bytes |  |
  | 32 | 2 | `center_brd_center_battery_common_temperature` (Temperature) | uint16 | In Degrees Celcius x100? |
  | 34 | 1 | `center_brd_center_battery_common_conn_status` (Conn Status) | uint8 | enum:`enums.CENTER_BRD_CENTER_BATTERY_COMMON_CONN_STATUS_ENUM` |

  *if (payload:len() >= offset+6) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 35 | 2 | `center_brd_center_battery_common_total_study_cycle` (Total Study Cycle) | uint16 |  |
  | 37 | 2 | `center_brd_center_battery_common_last_study_cycle` (Last Study Cycle) | uint16 |  |
  | 39 | 2 | `center_brd_center_battery_common_battery_on_charge` (Battery On Charge) | uint16 |  |

## 0x07 — Center Query Bat Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x08 — Center Query Bat Hisoty Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x09 — Center Bat SelfDischarge Days

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0A — Center Bat Storage Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — Center Req Bat Static Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — Center Req Bat Dynamic Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x23 — Center Req Bat Auth Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x24 — Center Req Bat Auth Result

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x31 — Center Req Bat SelfDischarge Time

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x32 — Center Set Bat SelfDischarge Time

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x33 — Center Req Bat Barcode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
