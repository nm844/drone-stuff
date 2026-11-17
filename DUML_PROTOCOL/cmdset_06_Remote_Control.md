# Cmd Set 0x06 — Remote Control

Total known command IDs: 85

## 0x01 — RC Channel Params Get

_Not decoded._ Almost certainly a Get query for the physical RC's current per-channel (aileron/elevator/throttle/rudder, and on some RCs a wheel/dial) logical stick parameters -- endpoint/travel, trim, and reversal settings as currently configured in the RC hardware, the counterpart read to 0x02's write. This is config state that lives entirely inside the RC's own stick-ADC/calibration subsystem, not aircraft flight state (that's cmd_id 0x05 'RC Parameter Get/Push', already decoded by the imported dissector and NOT in this batch). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x02 — RC Channel Params Set

_Not decoded._ The write counterpart to 0x01: almost certainly used to push new per-channel endpoint/travel/trim/reversal configuration into the RC, e.g. from an app-side 'RC settings' screen. Same channel-calibration-adjacent subject matter as 0x01. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x03 — RC Calibiration Set

_Not decoded._ Likely triggers or drives the physical RC's own stick/wheel calibration routine (e.g. writing per-channel min/center/max raw-ADC calibration points captured during an app-guided 'move sticks to each extreme' wizard). The project's existing dissector-sourced name already carries the upstream source's own typo ('Calibiration'), preserved here rather than silently corrected. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — RC Physical Channel Parameter Get

_Not decoded._ The name ('Physical Channel') suggests this queries the RAW, uncalibrated physical channel readings (raw ADC/PWM counts per stick/dial axis) as opposed to 0x01's calibrated/logical channel parameters -- plausibly used live during a calibration wizard to show real-time raw stick movement before it has been mapped through endpoint/trim calibration. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ DJI RCs support a dual-controller 'master/slave' pairing mode (one RC has full control authority, a second paired RC has partial/handoff authority, e.g. for instructor/student flying). This command plausibly sets which role (master or slave) the local physical RC is currently configured as. This is squarely RC-pairing-UI logic that has no obvious reason to be terminated on the aircraft rather than relayed to/between the RC units themselves. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x07 — RC Master/Slave Mode Get

_Not decoded._ The read counterpart to 0x06: queries the local physical RC's currently configured master/slave role. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x08 — RC Name Set

_Not decoded._ Plausibly sets a user-assigned friendly/display name string for the local physical RC unit (shown in the app's device/pairing list, useful for telling multiple paired RCs apart in master/slave setups). Likely payload is a short fixed- or length-prefixed ASCII/UTF-8 string buffer, but no field layout could be confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x09 — RC Name Get

_Not decoded._ The read counterpart to 0x08: queries the local physical RC's currently configured friendly/display name. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0A — RC Password Set

_Not decoded._ Plausibly sets a pairing/access password or PIN on the local physical RC (used to gate a second 'slave' RC joining a 'master', or to restrict re-binding of the RC to a new aircraft/app) -- companion to the adjacent, also-undecoded 'RC Password Get' (cmd_id 0x0B, outside this batch but visible in the existing doc). Likely payload is a short fixed-length password/PIN buffer, but no field layout could be confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0B — RC Password Get

_Not decoded._ Almost certainly queries the pairing password/PIN stored in a physical remote controller's own NVRAM, used to gate a second (slave) RC joining a master RC's dual-operator session (DJI's "Multiple Remote Controllers" / Master-Slave feature, exposed in the Mavic 3 app's RC settings). This is a plausible reconstruction from the command name only -- no code was found to confirm it. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0C — RC Connected Master Id Set

_Not decoded._ Plausibly tells a slave RC which master RC's ID to bind to, committing the pairing handshake after a discovery/search phase (see 0x0e/0x0f below). Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0D — RC Connected Master Id Get

_Not decoded._ Plausibly the read-back counterpart to 0x0c -- queries which master RC ID a slave is currently connected to. Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0E — RC Available Master Id Get

_Not decoded._ Plausibly returns the list of master-RC IDs discovered during a search/scan phase (companion to 0x0f/0x10 Search Mode), for the app to present as join candidates. Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0F — RC Search Mode Set

_Not decoded._ Plausibly starts/stops the RC's own radio-level scan for nearby master RCs broadcasting a joinable session -- a discovery process that would run entirely inside the RC's own radio/MCU stack. Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x10 — RC Search Mode Get

_Not decoded._ Plausibly the read-back counterpart to 0x0f -- queries whether the RC is currently in search/scan mode. Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x11 — RC Master/Slave Switch Set

_Not decoded._ Plausibly commands the RC to switch its own operating role between Master and Slave (or toggles a dedicated hardware switch state used by that role), distinct from the already-undecoded, more general 0x06/0x07 "RC Master/Slave Mode Set/Get" pair in this same cmd_set. Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x12 — RC Master/Slave Switch Conf Get

_Not decoded._ Plausibly returns the confirmation/result (success/fail code, or current role) of the 0x11 switch operation. Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x13 — RC Request Join By Slave

_Not decoded._ Plausibly the message a slave RC sends to request joining a specific master RC's session -- an early step in the pairing handshake, likely preceding the password check (0x0a/0x0b) and the connected-master-id commit (0x0c/0x0d). Reconstructed from the command name only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x14 — RC List Request Join Slave

_Not decoded._ A second physical remote controller ("slave RC") that wants to join an existing master-RC/aircraft pair asks the aircraft (or is asked by it) to enumerate/announce pending join requests. This is master/slave multi-RC pairing management, a feature of DJI's dual-RC accessory mode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x15 — RC Delete Slave

_Not decoded._ The master RC (or the aircraft, on the master RC's behalf) removes a previously-joined slave RC from the pairing, e.g. by its RC device ID. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x16 — RC Delete Master

_Not decoded._ A slave RC un-pairs itself from its current master RC (the inverse direction of 0x15), e.g. to re-pair with a different master or go solo. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x17 — RC Slave Control Right Set

_Not decoded._ Grants or revokes the slave RC's temporary right to take over stick/gimbal control from the master RC (the master typically retains ultimate authority and uses this to hand off control). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x18 — RC Slave Control Right Get

_Not decoded._ Queries current slave-control-right status (which RC currently holds/can hold control), the read-side counterpart to 0x17. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x19 — RC Control Mode Set

_Not decoded._ Sets the RC's stick-input control mode (the classic DJI Mode 1/Mode 2/Mode 3/Custom throttle-and-yaw-vs-pitch-and-roll stick-layout assignment, a setting local to how the RC itself maps its physical sticks to AETR channels). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1A — RC Control Mode Get

_Not decoded._ Reads back the RC's current stick-control-mode setting, the read-side counterpart to 0x19. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1B — RC GPS Info Get/Push

_Not decoded._ The RC pushes its own GPS fix (the controller's physical location, from a GPS chip inside the remote controller itself) -- used by DJI's app, when this is implemented, to show pilot location on the map or for RC-location-based geofence/no-fly-zone features local to the controller. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1C — RC RTC Info Get/Push

_Not decoded._ The RC pushes or reports its own real-time-clock value (wall-clock date/time as kept by the controller's own RTC chip) -- plausibly for app-side display, or to let another component cross-check/sync time against the RC's clock. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1D — RC Temperature Info Get/Push

_Not decoded._ Periodic push (or polled get) of the physical remote controller's own internal temperature telemetry (board/case temp, possibly multiple sensors) for display in the companion app; purely informational RC-health telemetry, not anything the flight controller needs to act on. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1E — RC Battery Info Get/Push

_Not decoded._ Periodic push (or polled get) of the physical remote controller's own internal battery telemetry (its built-in Li-ion pack, separate from the aircraft's flight battery) -- by analogy with the already-fully-decoded cmd_set 0x0d/0x06 'Battery Push Common Info' this would plausibly carry a smaller/simpler version of the same struct shape (design/full/remaining capacity, pack voltage, current, temperature, cycle count -- likely without the 6-cell per-cell-voltage breakdown, since RC packs are typically 1-2S rather than 6S), but this is an analogy, not something read off real RC-side code. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1F — RC Master/Slave Conn Info Get/Push

_Not decoded._ Push (or polled get) of the dual-RC 'master/slave' link's connection state -- e.g. whether a second (slave) remote controller is currently paired/connected, device identity, and which one currently holds flight-control authority -- for display in the app and/or for the aircraft to track which controller to trust for stick input. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x20 — RC Power Mode CE/FCC Set

_Not decoded._ Set the RC's RF regulatory power mode (CE for Europe vs. FCC for the US/other regions), which controls transmit power limits and channel/frequency selection for the OcuSync control+video link. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — RC Power Mode CE/FCC Get

_Not decoded._ Query the RC's currently active RF regulatory power mode (CE vs. FCC), the read counterpart to 0x20. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — RC Gimbal Ctr Permission Request

_Not decoded._ Sent by a controller (plausibly a slave/second RC, or a secondary app client) to request gimbal-control authority from the aircraft, presumably answered by 0x23 (Ack). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x23 — RC Gimbal Ctr Permission Ack

_Not decoded._ The aircraft's (or arbitrating controller's) acknowledgment/grant-or-deny response to a 0x22 Request, presumably carrying a simple granted/denied result code. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x24 — RC Simulate Flight Mode Set

_Not decoded._ Toggle the RC into/out of a 'simulate flight' mode -- most plausibly a single on/off flag telling the aircraft not to actually arm/spin motors so the pilot can practice stick movements on the real hardware safely, distinct from the much larger cmd_set 0x0b 'Simulator' subsystem (which models full flight dynamics with wind/altitude/speed parameters and already has its own, separately-documented, partially-decoded commands). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x25 — RC Simulate Flight Mode Get

_Not decoded._ Query the RC's/aircraft's current simulate-flight-mode state, the read counterpart to 0x24. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x26 — RC AETR Value Push

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE, inferred by cross-reference (no disassembled cmd_id-0x26-specific parser found): matches sibling cmd_id 0x05 "RC Parameter Get/Push"'s exact field layout/order, backed by DJI's own internal "dji_flightsystem_msgs" struct schema (int16 aileron/elevator/throttle/rudder, this exact order) embedded verbatim in dji_perception, and dji_navigation's nav_rc_get_stick_value/nav_rc_update_stick_value plus its 4-value "PANO_MOIVE: stick_value" debug string. See doc 21.`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `rc_aetr_push_aileron` (Aileron) | int16 | Roll/aileron stick axis (A of AETR). Signed per DJI's own internal struct (dji_perception's embedded schema types this field exactly 'int16 aileron'); the sibling cmd_id 0x05 payload at the identical offset is documented uint16 with center≈1024 and typical travel ≈364-1684 — shown here as the same raw convention for a realistic example, but the signed-vs-unsigned interpretation for 0x26 specifically is inferred, not directly confirmed on the wire. |
  | 2 | 2 | `rc_aetr_push_elevator` (Elevator) | int16 | Pitch/elevator stick axis (E of AETR). |
  | 4 | 2 | `rc_aetr_push_throttle` (Throttle) | int16 | Throttle stick axis (T of AETR). |
  | 6 | 2 | `rc_aetr_push_rudder` (Rudder) | int16 | Yaw/rudder stick axis (R of AETR). |

**Worked example:**

- Request payload: `00 04 00 04 6C 01 00 04`
  Payload bytes only (cmd_set=0x06, cmd_id=0x26 would precede this in the full DUML frame per 00_FRAME_FORMAT.md). Scenario: pilot has just powered on and armed, sticks centered, throttle held at minimum — aileron=1024 (0x0400), elevator=1024 (0x0400), throttle=364 (0x016C, the low end of the ~364-1684 DJI stick-travel convention used by the already-decoded sibling command 0x05), rudder=1024 (0x0400). All 4 values little-endian uint16/int16 at offsets 0/2/4/6.
- Response: One-way telemetry/control push, not a request/response exchange: '... Value Push' commands in this cmd_set (and the already-decoded sibling 0x05 'RC Parameter Get/Push') stream RC stick state at a high fixed rate for flight control, so a per-packet ACK round-trip would be wasted bus bandwidth. Expected behavior is no substantive response frame; at most a bare link-layer ACK with an empty payload if the frame's ack_type bit requests one, never application data.

## 0x27 — RC Detection Info Get

_Not decoded._ A 'Get' query, likely for status of some RC-local detection feature (possibly nearby-device/pairing detection, given this cmd_id sits directly between the flight-critical 0x26 AETR push and the master/slave-control cluster 0x28-0x2e); may be answered entirely within the physical remote controller or relayed opaquely. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x28 — RC Gimbal Control Access Right Get

_Not decoded._ Queries whether the requesting RC currently holds gimbal control authority (relevant only when multiple remote controllers are paired to one aircraft). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x29 — RC Slave Control Mode Set

_Not decoded._ Sets whether a secondary ('slave') remote controller is currently permitted to send flight-control input. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2A — RC Slave Control Mode Get

_Not decoded._ Queries the current slave-control-mode state set by 0x29. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2B — RC Gimbal Control Speed Set

_Not decoded._ Sets how fast gimbal movement responds to RC stick/wheel input (a sensitivity/rate-curve preference). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2C — RC Gimbal Control Speed Get

_Not decoded._ Queries the current gimbal-control speed/sensitivity setting set by 0x2b. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2D — RC Self Defined Key Func Set

_Not decoded._ Assigns a function (e.g. a camera shortcut) to a user-customizable physical button on the remote controller. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2E — RC Self Defined Key Func Get

_Not decoded._ Queries the current custom-button-to-function mapping set by 0x2d. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2F — RC Pairing

_Not decoded._ By name, this almost certainly triggers the RF pairing handshake between the physical remote controller and the aircraft's radio module (the initial bind/link-establishment step). Given the complete absence of any aircraft-side decode logic and the confirmed byte-blind relay architecture for this cmd_set, this is best explained as a command whose real processing happens entirely inside the remote controller's own MCU firmware (not present in this extraction), with dji_sys (if it forwards it at all) doing so without ever inspecting the payload -- likely RC-firmware-local, not decoded on the aircraft side. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x30 — RC Test GPS

_Not decoded._ Likely a factory/engineering-mode trigger asking the handheld controller (some DJI RC models have an onboard GPS/GLONASS module, used e.g. as a return-point aid if the RC itself gets lost) to run or report a self-test of its own GPS receiver. No aircraft-side test harness for this exists in the extraction; most plausibly RC-firmware-local. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x31 — RC RTC Clock Set

_Not decoded._ Sets the real-time clock inside the physical remote controller's own hardware (separate from the aircraft's system clock, which is set via cmd_set 0x00 instead). No local aircraft-side consumer of this value was found; most plausibly handled entirely by the RC's own MCU firmware. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x32 — RC RTC Clock Get

_Not decoded._ Queries the RC's own real-time clock value (the Get counterpart of 0x31). Same conclusion: no aircraft-side decode exists; likely RC-firmware-local. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x33 — RC Gimbal Control Sensitivity Set

_Not decoded._ By name, configures the sensitivity/response curve of the RC's own physical gimbal-control wheel (how far a given wheel deflection maps to a gimbal pitch-rate command) -- a setting most naturally stored and applied inside the RC hardware before it ever sends a control value onward, which would explain why no aircraft-side consumer was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x34 — RC Gimbal Control Sensitivity Get

_Not decoded._ Queries the current gimbal-control-wheel sensitivity setting from the RC. Same conclusion as 0x33. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x35 — RC Gimbal Control Mode Set

_Not decoded._ Likely selects which mode the RC's physical gimbal-control wheel/dial operates in (e.g. absolute-angle vs. rate/velocity control, or enabling/disabling a follow mode) -- again plausibly an RC-hardware-resident setting, consistent with the complete absence of any aircraft-side trace. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x36 — RC Gimbal Control Mode Get

_Not decoded._ Queries the current gimbal-control-wheel mode setting from the RC. Same conclusion as 0x35. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x37 — RC Enter App Mode Request

_Not decoded._ By name, requests that the physical RC switch out of its normal direct-stick-input mode into an app/SDK-driven input mode (plausibly relevant to simulator mode or onboard-SDK/companion-computer control hand-off). This is a mode transition inside the RC's own control-input firmware; no aircraft-side Linux binary shows any awareness of it. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x38 — RC Calibration Value Get

_Not decoded._ Almost certainly reads back raw stick/dial potentiometer calibration-curve data (min/center/max ADC counts per axis) that lives entirely on the RC's own MCU — it sits in a cluster of sibling RC-hardware-calibration commands that are ALL likewise undecoded in this project (0x03 'RC Calibiration Set', 0xf9 'RC Post Calibiration Set', 0xfa 'RC Stick Middle Value Get', 0xf8 'RC Stick Verification Data Get'), none of which have any aircraft-side footprint found across two separate investigation passes. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x39 — RC Master Slave Connect Status Push

_Not decoded._ A push notification about the link/connection status between two paired remote controllers in a master/slave (instructor/student) multi-RC setup. This is architecturally an RC-to-RC radio-link feature; the aircraft has no obvious reason to parse it and no decode logic for it was found anywhere in this extraction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3A — RC 2014 Usb Mode Set

_Not decoded._ This narrows/corrects the earlier project finding rather than confirming it: the handler candidate is real code in the shared dji_sys binary, but it is dead code on this specific WM260/Mavic 3 firmware (gated to other DJI products' platform-init paths), and its own internal dispatch key doesn't line up with cmd_set 0x06/cmd_id 0x3a anyway. Left as insufficient_evidence rather than asserting a layout built on a binding that doesn't hold up under re-examination. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3B — RC Id Set

_Not decoded._ Plausibly sets the RC's own identifier/serial as part of the same small cluster as 0x08 'RC Name Set' and 0x0c/0x0d 'RC Connected/Available Master Id' — all already undecoded in this project — rather than anything the aircraft itself needs to parse. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3C — RC Coach Mode

_Not decoded._ 'Coach mode' on DJI RCs is an instructor/student dual-stick-input arbitration feature; while it's plausible dji_flight would ultimately need SOME awareness of which stick input is authoritative, no such logic was locatable — dji_flight is fully stripped with no recoverable symbols in this extraction, and no string evidence of this feature exists anywhere in either firmware tree. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3F — RC Mater/Slave Id

_Not decoded._ Almost certainly the paired-RC identifier(s) exchanged during master/slave RC pairing setup — an RC-to-RC-only exchange with no found aircraft-side counterpart. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x42 — RC Follow Focus Get/Push

_Not decoded._ A physical follow-focus control wheel accessory mounted on the RC (used with DJI's lens/follow-focus hardware). Given the complete absence of any trace in the aircraft firmware, this is very likely RC-local end-to-end, or — if it ever reaches the aircraft at all — gets re-expressed as an already-separately-numbered camera/lens command rather than being parsed under its own 0x06/0x42 cmd_id anywhere in this extraction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x47 — RC App Special Control

_Not decoded._ Likely an opaque App->RC passthrough channel for RC-local special functions (the kind of catch-all 'vendor extension' command many DUML cmd_sets have) with no aircraft-side decode found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x48 — RC Freq Mode Info Get

_Not decoded._ Sits next to the already-undecoded 0x20/0x21 'RC Power Mode CE/FCC Set/Get' in the same cmd_set — plausibly a query of the RC's own radio-frontend regulatory/frequency mode (band plan, CE/FCC/SRRC region), answered entirely by the RC's own radio hardware rather than the aircraft's OcuSync air-interface stack (which is a separate, already-documented cmd_set 0x09 'HD Link'). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4C — RC Pro Custom Buttons Status Get/Push

_Not decoded._ Status/assignment of the RC Pro controller's physical programmable 'custom' buttons (C1/C2-style). By name this is specific to the RC Pro hardware variant's own button array. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x50 — RC Push Rmc Key Info

_Not decoded._ DJI's own source (file path embedded in the binary: hardware/dji/service/lte/control_xfer/common/lte_control_convert.c) models this as a 9-integer 'RMC_KEY_INFO' struct carrying RC physical-key/button state that control_convert() translates into camera shutter/record/playback/ISO commands and forwards to other cmd_sets (gimbal 0x0401/0x0406, camera 0x027c, flight-controller 0x03aa/0x2270, etc). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x51 — RC Push To Glass

_Not decoded._ By name, pushing UI/overlay content to a display referred to as 'glass' — most plausibly the RC unit's own built-in screen, or an attached FPV-goggles accessory. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x52 — RC Push LCD To MCU

_Not decoded._ By name, the RC unit's own LCD/touchscreen module pushing rendered-frame or touch data to the RC's own MCU — intra-RC-hardware traffic. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x53 — RC Unit Language Get

_Not decoded._ By name, reads the RC unit's own on-screen-display/UI language preference — an RC-local setting. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x54 — RC Unit Language Set

_Not decoded._ Same RC-local UI language preference as 0x53, write side. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x55 — RC Test Mode Set

_Not decoded._ Likely a manufacturing/factory test-mode toggle for the RC unit; possibly also puts the aircraft link into a test state. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x56 — RC Quiry Role

_Not decoded._ Queries which multi-RC role (master vs. slave) the querying RC currently holds in a dual-RC master/slave setup. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x57 — RC Quiry Ms Link Status

_Not decoded._ Queries the current status of the master-slave RC link (connected/disconnected, link quality, etc.) in a dual-RC setup. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x58 — RC Work Function Set

_Not decoded._ Configures which 'work function' set (custom-button/wheel/mode assignment profile) the RC's physical controls currently drive. Most plausibly an App-or-aircraft-to-RC configuration write that only the RC's own MCU needs to act on. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x59 — RC Work Function Get

_Not decoded._ Reads back the RC's currently-active 'work function' set (the Get counterpart of 0x58). Same reasoning: a query the RC's own MCU would answer about its own local button/wheel configuration. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x98 — Follow Focus2 Get/Push

_Not decoded._ Most plausibly reports live follow-focus-wheel position / lens-focus-distance telemetry from an RC accessory with a focus wheel (e.g. a cine-style controller or external follow-focus unit) toward the camera/gimbal subsystem so the lens driver can track it. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x99 — Follow Focus Info Set

_Not decoded._ The Set counterpart of 0x98 -- likely pushes follow-focus configuration/range info (e.g. calibrated near/far limits) from the RC accessory to the camera/gimbal side. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Factory/QA command for live raw stick-axis ADC readings during production test, so a test jig can verify joystick response across its mechanical range before a unit ships. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF6 — RC Factory Get Board Id

_Not decoded._ Factory command reading the physical remote controller's own PCB/hardware board-revision identifier, for production traceability. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF7 — RC Push Buzzer To MCU

_Not decoded._ Tells the RC's own MCU to sound its physical buzzer (pairing confirmation, alert, 'find my RC' feedback, etc.). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF8 — RC Stick Verification Data Get

_Not decoded._ Factory readback of stick-calibration verification data (e.g. recorded min/max/center samples from a prior calibration pass), for QA sign-off. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF9 — RC Post Calibiration Set

_Not decoded._ Sets a flag/state marking that stick calibration has just completed (likely a 'calibration done' acknowledgment/latch, possibly also used to re-enable normal stick input after a calibration sequence). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFA — RC Stick Middle Value Get

_Not decoded._ Factory readback of each stick axis's calibrated center/trim ADC value, used during or after calibration to confirm the neutral position was captured correctly. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
