# Cmd Set 0x0d — Battery

Total known command IDs: 16

## 0x01 — Battery Static Data Get

Payload decoder: `battery_static_data_dissector`

  *if (payload:len() >= 40) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `battery_static_data_unk1` (Unknown) | bytes |  |
  | 2 | 4 | `battery_static_data_design_capacity` (Design Capacity [mAh]) | uint32 |  |
  | 6 | 2 | `battery_static_data_discharge_count` (Discharge Count) | uint16 |  |
  | 8 | 4 | `battery_static_data_design_voltage` (Design Voltage [mV]) | uint32 |  |
  | 14 | 2 | `battery_static_data_manufacture_date` (Manufacture Date (packed)) | uint16 |  |
  | 14 | 2 | `battery_static_data_serial_number` (Serial Number) | uint16 |  |
  | 16 | 8 | `battery_static_data_manufacturer_name` (Manufacturer Name) | string |  |
  | 24 | 2 | `battery_static_data_unk2` (Unknown) | bytes |  |
  | 26 | 5 | `battery_static_data_device_name` (Device Name) | string |  |
  | 31 | ? | `battery_static_data_loader_version` (Loader Version) | string |  |
  | 35 | ? | `battery_static_data_app_version` (App Version) | string |  |
  | 39 | 1 | `battery_static_data_state_of_health` (State of Health (%)) | uint8 |  |

## 0x02 — Battery Dynamic Data Get/Push

Payload decoder: `battery_dynamic_data_dissector`

  *if (payload:len() == 32) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `battery_dynamic_data_unk1` (Unknown) | bytes |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `battery_dynamic_data_index` (Index) | uint8 | Offset shifted by unknown value this.dataOffset |
  | 0 | 1 | `battery_dynamic_data_result` (Result) | uint8 | mask:`0xff` |

## 0x03 — Battery Cell Voltage Get/Push

Payload decoder: `battery_cell_voltage_dissector`

  *if (payload:len() >= 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `battery_cell_voltage_unk1` (Unknown) | bytes |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `battery_cell_voltage_index` (Index) | uint8 | Offset shifted by unknown value this.dataOffset |
  | 0 | 1 | `battery_cell_voltage_result` (Result) | uint8 | mask:`0xff` |

## 0x04 — Battery BarCode Data Get

Payload decoder: `battery_barcode_data_dissector`

  *if (payload:len() > 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `battery_barcode_data_unk1` (Unknown) | bytes |  |
  | 2 | 1 | `battery_barcode_data_length` (Data Length) | uint8 |  |

  *if ((payload:len() - offset) == data_length) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 3 | data_length | `battery_barcode_data_string` (Barcode String) | string |  |

## 0x05 — Battery History Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — Battery Push Common Info

Payload decoder: `battery_push_common_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `battery_push_common_info_design_capacity` (Design Capacity) | uint16 | mAh |
  | 2 | 2 | `battery_push_common_info_full_charge_capacity` (Full Charge Capacity) | uint16 | mAh |
  | 4 | 2 | `battery_push_common_info_remaining_capacity` (Remaining Capacity) | uint16 | mAh |
  | 6 | 2 | `battery_push_common_info_pack_voltage` (Pack Voltage) | uint16 | mV |
  | 8 | 2 | `battery_push_common_info_current` (Current) | int16 | mA |
  | 10 | 1 | `battery_push_common_info_life_percentage` (Life Percentage) | uint8 |  |
  | 11 | 1 | `battery_push_common_info_capacity_percentage` (Capacity Percentage) | uint8 |  |
  | 12 | 2 | `battery_push_common_info_temperature` (Temperature) | int16 | 0.1 degC |
  | 14 | 2 | `battery_push_common_info_cycle_count` (Cycle Count) | uint16 |  |
  | 16 | 2 | `battery_push_common_info_serial_number` (Serial Number) | uint16 |  |
  | 18 | 2 | `battery_push_common_info_cell1` (Cell 1 Voltage) | uint16 | mV |
  | 20 | 2 | `battery_push_common_info_cell2` (Cell 2 Voltage) | uint16 | mV |
  | 22 | 2 | `battery_push_common_info_cell3` (Cell 3 Voltage) | uint16 | mV |
  | 24 | 2 | `battery_push_common_info_cell4` (Cell 4 Voltage) | uint16 | mV |
  | 26 | 2 | `battery_push_common_info_cell5` (Cell 5 Voltage) | uint16 | mV |
  | 28 | 2 | `battery_push_common_info_cell6` (Cell 6 Voltage) | uint16 | mV |
  | 30 | 2 | `battery_push_common_info_average_current` (Average Current) | int16 | mA |
  | 32 | 1 | `battery_push_common_info_unknown20` (Unknown20) | uint8 |  |
  | 33 | 4 | `battery_push_common_info_error_count` (Error Count) | uint32 | possibly only low 8 bits used |
  | 37 | 4 | `battery_push_common_info_n_discharge_times` (Discharge Cycle Count) | uint32 |  |
  | 41 | 4 | `battery_push_common_info_current_status` (Current Status Flags) | uint32 |  |

## 0x11 — Battery SetSelfDischargeDays Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x12 — Battery ShutDown

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x13 — Battery Force ShutDown

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x14 — Battery StartUp

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x15 — Battery Pair Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x16 — Battery Pair Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — Battery Data Record Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x23 — Battery Authentication

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x31 — Battery Re-Arrangement Get/Push

Payload decoder: `battery_re_arrangement_dissector`

## 0x32 — Battery Mult Battery Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
