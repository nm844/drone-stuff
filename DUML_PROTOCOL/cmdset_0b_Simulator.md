# Cmd Set 0x0b — Simulator

Total known command IDs: 21

## 0x01 — Simu Connect Heart Packet

Payload decoder: `sim_connect_heart_packet_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `sim_connect_heart_packet_unknown00` (Unknown00) | uint8 |  |
  | 1 | 1 | `sim_connect_heart_packet_result` (Result) | uint8 |  |

## 0x02 — Simu IMU Status Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — Simu SDR Status Push

Payload decoder: `sim_sdr_status_push_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `sim_sdr_status_push_drone_type` (Drone Type) | uint8 |  |

## 0x04 — Simu Get Headbelt SN

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — Simu Flight Status Params

Payload decoder: `sim_flight_status_params_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `sim_flight_status_params_length` (Length) | uint8 |  |
  | 1 | 1 | `sim_flight_status_params_masked01` (Masked01) | uint8 |  |
  | 1 | 1 | `sim_flight_status_params_has_motor_turned_on` (Has Motor Turned On) | uint8 | mask:`0x01` |
  | 1 | 1 | `sim_flight_status_params_in_the_air` (In The Air) | uint8 | mask:`0x02` |

## 0x07 — Simu GetWind Set

Payload decoder: `sim_wind_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `sim_wind_wind_speed_x` (Wind Speed X) | uint16 |  |
  | 2 | 2 | `sim_wind_wind_speed_y` (Wind Speed Y) | uint16 |  |

## 0x08 — Simu GetArea Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x09 — Simu GetAirParams Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0A — Simu Force Moment

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0B — Simu GetTemperature Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0C — Simu GetGravity Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0D — Simu Crash ShutDown

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0E — Simu Ctrl Motor

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0F — Simu Momentum

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x10 — Simu GetArmLength Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x11 — Simu GetMassInertia Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x12 — Simu GetMotorSetting Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x13 — Simu GetBatterySetting Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x14 — Simu Frequency Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1A — Simu Set Sim Vision Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1B — Simu Get Sim Vision Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
