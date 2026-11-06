# Cmd Set 0x0e — Data Logger

Total known command IDs: 2

## 0x22 — DLog Battery Data

Payload decoder: `datlog_battery_data_dissector`

  *if (payload:len() > 4) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `datlog_battery_data_block_id` (Block ID) | uint16 |  |
  | 2 | 1 | `datlog_battery_data_length` (Data Length) | uint8 |  |

  *if(payload:len() - offset == data_length) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 3 | 2 | `datlog_battery_data_voltage` (Pack Voltage [mV]) | uint16 |  |
  | 5 | 4 | `datlog_battery_data_current` (Current [mA]) | int32 |  |
  | 9 | 2 | `datlog_battery_data_full_charge_capacity` (Full Charge Capacity [mAh]) | uint16 |  |
  | 11 | 2 | `datlog_battery_data_current_capacity` (Current Capacity [mAh]) | uint16 |  |
  | 13 | 2 | `datlog_battery_data_temperature` (Temperature [deg C]) | int16 |  |
  | 15 | 2 | `datlog_battery_data_state_of_charge` (State of Charge [%]) | uint16 |  |
  | 17 | 1 | `datlog_battery_data_status1` (Status 1) | uint8 |  |
  | 18 | 1 | `datlog_battery_data_status2` (Status 2) | uint8 |  |
  | 19 | 1 | `datlog_battery_data_status3` (Status 3) | uint8 |  |
  | 20 | 1 | `datlog_battery_data_status4` (Status 4) | uint8 |  |
  | 21 | 2 | `datlog_battery_data_cell1_voltage` (Cell 1 Voltage [mV]) | uint16 |  |
  | 23 | 2 | `datlog_battery_data_cell2_voltage` (Cell 2 Voltage [mV]) | uint16 |  |
  | 25 | 2 | `datlog_battery_data_cell2_voltage` (Cell 2 Voltage [mV]) | uint16 |  |

## 0x23 — DLog Battery Message

Payload decoder: `datlog_battery_msg_dissector`

  *if (payload:len() > 2) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | message_len | `datlog_battery_msg_message` (Message) | string |  |
