# Cmd Set 0x0b — Simulator

Total known command IDs: 21

## 0x01 — Simu Connect Heart Packet

Payload decoder: `sim_connect_heart_packet_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `sim_connect_heart_packet_unknown00` (Unknown00) | uint8 |  |
  | 1 | 1 | `sim_connect_heart_packet_result` (Result) | uint8 |  |

## 0x02 — Simu IMU Status Push

_Not decoded._ Inferred from the name only (never confirmed): the simulator-in-the-loop (SIL) host periodically pushes synthetic accelerometer/gyro IMU samples to the flight controller so it behaves as if real IMU hardware were reporting data while on a test bench. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x03 — Simu SDR Status Push

Payload decoder: `sim_sdr_status_push_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `sim_sdr_status_push_drone_type` (Drone Type) | uint8 |  |

## 0x04 — Simu Get Headbelt SN

_Not decoded._ Inferred from the name only: a query for the serial number of a 'headbelt' peripheral (likely the FPV-goggle head-tracking strap/module) as surfaced through the simulator subsystem, possibly for binding/pairing a real headbelt unit to a simulated flight session. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Inferred from the name only: likely sets the simulated flight-permitted area/boundary (e.g. a virtual NFZ or arena limit) so the simulator's physics/geofence logic constrains the synthetic flight the same way a real GPS-fenced area would. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x09 — Simu GetAirParams Set

_Not decoded._ Inferred from the name only: likely sets synthetic air/atmosphere parameters (air density, pressure, temperature-adjacent values) feeding the simulator's aerodynamic model, which would plausibly be a multi-field float struct as the task brief anticipates — but no evidence of the actual layout was recoverable. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0A — Simu Force Moment

_Not decoded._ Inferred from the name only: likely injects a synthetic external force/moment (e.g. simulated wind gust or collision impulse) directly into the simulated rigid-body dynamics, which would plausibly carry 3-axis force + 3-axis moment floats — but no evidence of the actual layout was recoverable. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0B — Simu GetTemperature Set

_Not decoded._ Inferred from the name only: likely sets a synthetic ambient/component temperature value (feeding thermal-dependent sensor models such as barometer or battery temperature compensation) into the simulated environment. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0C — Simu GetGravity Set

_Not decoded._ Inferred from the name only: likely sets a synthetic local-gravity vector/magnitude for the simulated dynamics model — plausibly a 3-axis float vector as the task brief anticipates, but no evidence of the actual layout was recoverable. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0D — Simu Crash ShutDown

_Not decoded._ Inferred from the name only: likely a notification/command that the simulated aircraft has 'crashed' in the synthetic physics, triggering a motor/flight shutdown in the simulated session — possibly carrying a crash-cause/severity code rather than a wide struct. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0E — Simu Ctrl Motor

_Not decoded._ Inferred from the name only: likely a direct per-motor control/override command for the simulated motors (bypassing the normal flight-control mixer) used for bench motor-response testing under simulation. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0F — Simu Momentum

_Not decoded._ Inferred from the name only: likely injects or reports a synthetic linear/angular momentum state into the simulated dynamics, conceptually adjacent to 'Simu Force Moment' (0x0a). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x10 — Simu GetArmLength Set

_Not decoded._ Inferred from the name only: likely sets the simulated aircraft's arm length (motor-to-center-of-mass distance), a single-float airframe-geometry parameter feeding the simulated flight-dynamics model. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x11 — Simu GetMassInertia Set

_Not decoded._ Inferred from the name only: likely sets the simulated aircraft's mass and moment-of-inertia tensor (mass plus 3x3 or diagonal inertia terms) — plausibly one of the widest/most float-heavy payloads in this group, but no evidence of the actual layout was recoverable. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x12 — Simu GetMotorSetting Set

_Not decoded._ Inferred from the name only: likely sets simulated per-motor characteristic parameters (thrust/RPM curve coefficients, response time constant, etc.) feeding the simulated motor-response model. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x13 — Simu GetBatterySetting Set

_Not decoded._ Inferred from the name only: likely sets simulated battery characteristics (capacity, voltage curve, internal resistance) feeding a synthetic battery-state model for the simulated flight, so battery-dependent flight behavior can be exercised without a real pack. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x14 — Simu Frequency Get

_Not decoded._ Inferred from the name only: likely a query for the simulator's update/push frequency (how often the synthetic sensor-push commands in this same group are expected to arrive), possibly a near-trivial single-scalar response rather than a wide struct. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1A — Simu Set Sim Vision Mode

_Not decoded._ Inferred from the name only: likely switches the vision/perception subsystem between real-camera and simulated-vision (synthetic image/feature feed) modes for SIL testing of vision-dependent flight features. This is the one command in the group with a genuine, named-but-unresolved lead (see evidence). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1B — Simu Get Sim Vision Mode

_Not decoded._ Inferred from the name only: a query returning the current vision-mode state that cmd_id 0x1a would set (real-camera vs. simulated-vision), likely as this group's response counterpart. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
