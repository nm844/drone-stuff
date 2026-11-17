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

_Not decoded._ Name suggests a getter for stored historical battery records (e.g. indexed past-cycle/event log entries kept in the smart battery's own flash) rather than live telemetry; this is inferred only from the command name, not from any disassembled handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ DJI smart batteries have a user-configurable 'self-discharge after N days of inactivity' feature (exposed in the DJI Fly app's battery settings, typically a small set of day-count options). This is almost certainly a getter for that single stored configuration value, inferred from the command name alone — no handler was found to confirm the actual wire encoding (e.g. whether it's a raw day-count byte, an enum index, or something else). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x12 — Battery ShutDown

_Not decoded._ Name suggests a command telling the smart battery to power itself off (e.g. issued by the app/aircraft after a controlled landing+disarm sequence, or via a long-press pairing-button-equivalent over the wire). Inferred from the name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x13 — Battery Force ShutDown

_Not decoded._ Likely a forced/unconditional variant of 0x12 (bypassing any safety interlocks such as 'not while in flight' or 'not while charging'), inferred from the name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x14 — Battery StartUp

_Not decoded._ Likely the counterpart to 0x12/0x13 — a command telling the smart battery to power itself on / wake from shutdown. Inferred from the name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x15 — Battery Pair Get

_Not decoded._ Likely a getter for the battery-to-aircraft pairing/binding state (DJI smart batteries can be bound to a specific aircraft for anti-theft/compatibility reasons). Inferred from the name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x16 — Battery Pair Set

_Not decoded._ Likely the setter counterpart to 0x15 (initiates or clears the battery-aircraft pairing/binding). Inferred from the name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — Battery Data Record Control

_Not decoded._ Likely a control command toggling the smart battery's own internal data-logging (start/stop/interval for whatever generates the records that 'Battery History Get' (0x05) would retrieve). Inferred from the name and its numeric proximity/pairing with 0x05 only — not confirmed by any code. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x23 — Battery Authentication

_Not decoded._ Likely a challenge/response or SN-verification exchange used to confirm the connected battery is a genuine/authorized DJI battery before allowing flight — architecturally analogous to the DJICare/activation device-binding chain this project's docs 13/18 already mapped, but for the battery rather than the aircraft-to-cloud relationship. Inferred from the name and the adjacent evidence below, not from a disassembled 0x0d/0x23 handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x31 — Battery Re-Arrangement Get/Push

Payload decoder: `battery_re_arrangement_dissector`

## 0x32 — Battery Mult Battery Info Get

_Not decoded._ Likely a telemetry getter that aggregates status for multiple batteries at once — relevant to DJI airframes with dual/parallel battery bays (the WM260/Mavic 3 itself uses a single battery, so this cmd_id may be a cmd-set-wide command inherited from a shared battery-subsystem codebase shared with multi-battery airframes). Inferred from the name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
