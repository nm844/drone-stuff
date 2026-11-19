# Cmd Set 0x05 — Center Board

Total known command IDs: 18

## 0x00 — Center Open/Close Virtual RC

_Not decoded._ Attempted: grepped DUML_PROTOCOL/*.md (no prior decode); searched dji_sys's recovered .gnu_debugdata symbol names and a full `strings` sweep of every binary on both E1E/E2 images for 'vrc'/'virtual_rc'/'virtualrc' -- the only hit anywhere on either image is an unrelated blackbox-log field formula, `Op.expr E_virtual_rc_on_off bitand(shift_r(bit_S,4),1)`, found in dji_flight (E1E) and libmt_client.so (E2). That is a flight-log telemetry-channel definition (a named log column computed by extracting bit 4 of some other internal status word called bit_S for post-flight analysis), not a DUML payload dissector -- this project's own 04_WM260_DAEMON_FINDINGS.md hit the exact same kind of dead end previously with dji_perception's self-describing ROS-style schema strings. Also checked: no literal cmd_set=5 immediate registration in any of the 4 binaries that import duss_event_register_dynamic_command; no `dji_mb_ctrl -s 5` invocation in any shell script on either image. The real handler most plausibly lives in the Center Board's own bare-metal MCU firmware (module 0500_PD_MCU), whose decrypted binary is not present in this session's firmware root. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x01 — Center Virtual RC Data

_Not decoded._ Same search as 0x05/0x00 (these two are an open/close + data pair). No handler-specific evidence found beyond the same single, unrelated 'E_virtual_rc_on_off' blackbox-log-formula string noted for 0x05/0x00. Given 0x00 is presumably the enable/disable toggle and this is the actual channel-data payload, a per-channel u16 array is a plausible guess by analogy with Flight Control's RC-channel-data commands, but I have no binary evidence for the channel count, ordering, or scaling, so I am not asserting a layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x02 — Center Push Batt Dynamic Info

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: sys_battery_get_dynamic_info (generic request handler) -> per-board-model callback at offset +0xb0 of a device-context struct -> duss_event_resp_data (confirmed real PLT import, resolved by name) sends the 32-byte result back`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 20 | `reserved_0` (Reserved / board-model-specific (bytes 0x00-0x13)) | bytes | Zeroed by the generic handler before the per-board callback runs; for the one named per-board callback actually disassembled (a different DJI product, not WM260) these bytes stay zero. WM260's own callback was not identified by name, so these bytes' real WM260 content is unknown. |
  | 20 | 1 | `remaining_capacity_percent` (Remaining Capacity (%)) | uint8 | Confirmed via disassembly of sys_update_battery_info: an SBS/SMBus i2c_write_then_read of standard register 0x0D (RelativeStateOfCharge), low byte of the 2-byte result; defaults to 100 on I2C failure. Confirmed at this exact offset (0x14) for the one per-board callback disassembled; very likely the same slot for WM260 given the shared generic dispatcher, but not independently confirmed for WM260's own callback. |
  | 21 | 11 | `reserved_1` (Reserved / board-model-specific (bytes 0x15-0x1F)) | bytes | Same caveat as reserved_0. |

**Worked example:**

- Request payload: `00`
  The app (or another bus client) queries the Center Board for the current battery charge level mid-flight. The incoming request's payload carries at least 1 byte that the handler reads and caches into its device-context struct before calling the fill-callback -- most plausibly a battery/selector index, since this is a single-battery aircraft the value is very likely always 0. No other request-side fields were found read by the generic handler.
- Response payload: `00000000000000000000000000000000000000004c0000000000000000000000`
  32-byte response for a battery reporting 76% remaining capacity (0x4C), all other bytes zero/unconfirmed for this product.

## 0x03 — Center Control Uav Status Led

_Not decoded._ Searched dji_sys's recovered symbol table for LED-related functions: found led_control_thread (0x44960), sys_fc_led_exit (0x37888), sys_fc_logout_led_ctrl_action (0x37548) -- all real, but (a) none appear as the handler/arg-struct of any of the 12 literal duss_event_register_dynamic_command call sites found in dji_sys, (b) `strings` on both E1E/E2 dji_sys binaries found zero human-readable 'led'-related log/format strings to anchor them semantically, and (c) no BL caller or static-data relocation tying them to a cmd_set/cmd_id pair was found in the time available. These read as the aircraft's own internal status-LED driver thread, not confirmed as the wire-facing handler for this specific command. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — Center Transform Control

_Not decoded._ Searched dji_sys/dji_blackbox/dji_perception symbol tables and full `strings` output on both images for 'transform' -- zero hits anywhere except unrelated camera-playback 'Center X'/'Center Y' coordinate fields (cmdset_02_Camera.md, a different, already-documented command) and C++ RTTI/vtable noise. No literal cmd_set=5 registration found either. No handler identified; most plausibly lives in the Center Board's own MCU firmware (out of this round's scoped firmware root). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x05 — Center Req Push Bat Normal Data

_Not decoded._ No handler distinct from 0x05/0x02 was found. This command's name strongly suggests it is in the same family as 0x02 ('Push Batt Dynamic Info'), and may in fact be dispatched through the exact same generic sys_battery_get_dynamic_info path in dji_sys (which is config-driven and could plausibly serve more than one cmd_id) -- but I found no second static reference, no second handler-name string, and no literal immediate anywhere tying a distinct cmd_id to that dispatcher or to any other function. Reporting this honestly as unconfirmed rather than assuming it shares 0x02's layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Searched dji_sys/dji_blackbox symbol tables and `strings` for 'bat_status'/'battery status' -- no distinct hits beyond the generic battery-dynamic-info and PHM telemetry code already attributed to 0x02/0x21/0x22. No literal cmd_set=5 registration found. No handler identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x08 — Center Query Bat Hisoty Status

_Not decoded._ Searched for 'history'/'hisoty' (matching the command's own misspelling) and 'bat_history' across every binary on both images -- zero hits. The already-known cmd_set 0x0D sibling ('Battery History Get', 0x0D/0x05) is itself undecoded in the existing dissector too, so there was no cross-reference to borrow from either. No handler identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x09 — Center Bat SelfDischarge Days

_Not decoded._ Searched for 'selfdis'/'self_dis'/'discharge'/'sleep_mode'/'ship_mode'/'hibernat' across dji_sys and dji_blackbox (the two binaries with confirmed real battery-telemetry code) on both images -- zero hits on either, despite dji_blackbox's PHM telemetry struct (see 0x05/0x22) containing dozens of other confirmed battery-health field names (sohc_fsm, bms_mode, qcell_max, etc.) in the immediate vicinity; self-discharge specifically never appears as a string anywhere. The task hint's suggestion that cmd_set 0x05 and 0x0D might share a handler was checked directly: cmd_set 0x0D's own 'SetSelfDischargeDays' (0x0D/0x11) is ALSO undecoded in the existing dissector, so there was no existing decode to confirm sharing against. No handler identified in the scoped firmware root; most plausibly implemented entirely in the smart-battery MCU itself (which negotiates its own sleep/ship-mode timers) with the Center Board/dji_sys acting as a pure passthrough needing no field-aware parsing on the Linux side. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0A — Center Bat Storage Info

_Not decoded._ Searched for 'storage_info'/'bat_storage'/'storage_mode' across dji_sys/dji_blackbox on both images -- the only 'storage' hits found anywhere are unrelated (filesystem/SD-card storage functions: get_data_storage_size, init_storage, etc., and an unrelated log string 'get free storage memory fail'). No battery-storage-mode-specific string or function found. No handler identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — Center Req Bat Static Data

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: parse_bat_static_data (0x25090), called from phm_bat_data_upload (0x243b8)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 32 | `sn` (Serial Number (string)) | string | Read via strlen() starting at offset 0; log label is literally 'sn'. Buffer size inferred from the gap to the next field (0x20), not independently confirmed as exactly 32. |
  | 32 | 2 | `active_time_year` (Active Time - Year) | uint16 | First of 6 fields combined under one log label 'active_time', formatted as '%04d-%02d-%02d %02d:%02d:%02d'. |
  | 34 | 1 | `active_time_month` (Active Time - Month) | uint8 | See active_time_year. |
  | 35 | 1 | `active_time_day` (Active Time - Day) | uint8 | See active_time_year. |
  | 36 | 1 | `active_time_hour` (Active Time - Hour) | uint8 | See active_time_year. |
  | 37 | 1 | `active_time_min` (Active Time - Minute) | uint8 | See active_time_year. |
  | 38 | 1 | `active_time_sec` (Active Time - Second) | uint8 | See active_time_year; byte at offset 39 appears to be 1 byte of padding before product_time, inferred from offsets, not separately labeled in the log code. |
  | 40 | 4 | `product_time` (Product Time (packed manufacture date)) | uint32 | Log label 'product_time'. Code unpacks it via bitfield extraction (ubfx at bits 4 and 9, plus a +0x7bc / 1980-style year-bias constant) consistent with a classic packed DOS-date encoding (day/month/year-since-1980), matching the sibling field 'manufacture_date' already documented for cmd_set 0x0D/0x01 in this project's existing dissector. Exact bit boundaries not re-verified to the bit. |
  | 44 | 4 | `design_voltage` (Design Voltage) | uint32 | Log label 'design_voltage'; units not independently confirmed (likely mV, by analogy to cmd_set 0x0D/0x01's existing 'design_voltage [mV]' field). |
  | 48 | 4 | `design_capacity` (Design Capacity) | uint32 | Log label 'design_capacity'; units not independently confirmed (likely mAh, by analogy to cmd_set 0x0D/0x01). |
  | 52 | -1 | `factory_info` (Factory Info (string)) | string | Log label 'factory_info'; length-via-strlen, variable length, exact max size not determined. |

**Worked example:**

- Request payload: ``
  A bus client (app, or dji_blackbox itself during its periodic health-management sweep) asks the Center Board for the battery's static/nameplate data once per boot or on connect. No request-side fields were identified anywhere in this pass; treated as a bare, payload-less query.
- Response payload: `5733503343333235303932304142303100000000000000000000000000000000e60709140e1e0000942a0000283c0000881300004654592d535a30310000000000000000`
  68-byte static-data response for a battery with serial 'W3P3C3250920AB01', last activated 2022-09-20 14:30:00, packed manufacture-date raw value 0x00002a94, design voltage 15400 (mV), design capacity 5000 (mAh), factory info 'FTY-SZ01'.

## 0x22 — Center Req Bat Dynamic Data

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: phm_bat_data_upload (0x243b8)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `current` (Current) | int32 | Signed; units not independently confirmed, likely mA by analogy with the already-documented cmd_set 0x0D/0x06 'Current' field. |
  | 4 | 2 | `voltage` (Voltage) | uint16 | Likely mV by analogy with cmd_set 0x0D/0x06. |
  | 6 | 2 | `mcu_temp` (MCU Temperature) | int16 | Signed; likely 0.1 degC scale. |
  | 8 | 2 | `mos_temp` (MOSFET Temperature) | int16 | Battery discharge/charge MOSFET temperature sensor. |
  | 10 | 2 | `conn_temp_0` (Connector Temperature 0) | int16 | Battery-to-aircraft power connector temperature sensor, position 0. |
  | 12 | 2 | `conn_temp_1` (Connector Temperature 1) | int16 | Connector temperature sensor, position 1. |
  | 14 | 2 | `fcc` (Full Charge Capacity) | uint16 | Likely mAh, by analogy with cmd_set 0x0D/0x01 and 0x0D/0x06's existing fcc-equivalent fields. |
  | 16 | 2 | `rm` (Remaining Capacity) | uint16 | Likely mAh. |
  | 18 | 1 | `soc` (State of Charge (%)) | uint8 | Raw/cell-model SOC percentage. |
  | 19 | 1 | `soc_dji` (DJI-adjusted State of Charge (%)) | uint8 | The value shown to the user in the app, per common DJI practice of smoothing/rescaling the raw SOC for display. |
  | 20 | 2 | `mos_state` (MOSFET State) | uint16 | Likely a bitmask of charge/discharge FET on/off states; not decoded bit by bit. |
  | 22 | 1 | `fsm_state` (FSM State) | uint8 | Overall battery state-machine state (e.g. idle/charging/discharging/fault). |
  | 23 | 2 | `status_flags` (Status Flags) | uint16 | Byte-unaligned read (ldurh); general status bitmask, bits not individually decoded. |
  | 25 | 2 | `vol_pack` (Pack Voltage) | uint16 | Byte-unaligned read; likely an alternate/aggregate voltage reading alongside the earlier 'voltage' field. |
  | 27 | 2 | `cycle` (Cycle Count) | uint16 | Byte-unaligned read; charge cycle count. |
  | 29 | 2 | `protect_flag` (Protection Flag) | uint16 | Battery protection-circuit flags (e.g. over-temp/over-current trip). |
  | 31 | 1 | `bms_mode` (BMS Mode) | uint8 | Battery-management-system operating mode. |
  | 32 | 2 | `no_sleep_flag` (No-Sleep Flag) | uint16 | Likely indicates something is holding the battery out of its low-power sleep state. |
  | 34 | 1 | `sdsg_fsm` (Self-Discharge State Machine) | uint8 | 'SDSG' read as Self-DiScharGe; directly relevant to this batch's self-discharge commands (0x09/0x31/0x32) even though it did not resolve their own handler -- this confirms self-discharge is tracked as a battery-internal state machine value. |
  | 35 | 1 | `host_state` (Host State) | uint8 | Likely the state of whatever host (aircraft) the battery is currently plugged into/communicating with. |
  | 36 | 4 | `app_ver` (Application Firmware Version) | bytes | 4 raw bytes formatted as 'V%02d.%02d.%02d.%02d' -- a major.minor.patch.build style version quad. |
  | 40 | 2 | `hw_ver` (Hardware Version) | uint16 | Battery PCB/hardware revision. |
  | 42 | 2 | `algo_ver` (Algorithm Version) | uint16 | SOC/health-estimation algorithm version. |
  | 44 | 2 | `algo_state` (Algorithm State) | uint16 | State of the SOC/health estimation algorithm. |
  | 46 | 4 | `avg_curr` (Average Current) | int32 | Signed; averaged/filtered current reading. |
  | 50 | 1 | `sohc_fsm` (State-of-Health-Capacity State Machine) | uint8 | 'SOHC' = State Of Health Capacity; a distinct state machine from sdsg_fsm. |
  | 51 | 4 | `passedq` (Passed Charge (coulomb count)) | int32 | Byte-unaligned read (ldur); accumulated charge passed through the coulomb counter. |
  | 55 | 2 | `qbat` (Battery Charge Quantity) | uint16 | Byte-unaligned read. |
  | 57 | 1 | `qcell_max` (Max Cell Charge) | uint8 | Highest individual-cell charge-quantity reading. |
  | 58 | 1 | `qcell_min` (Min Cell Charge) | uint8 | Lowest individual-cell charge-quantity reading. |
  | 59 | 1 | `soc1_0` (SOC Model 1, reading 0) | uint8 | One of two parallel SOC estimation models tracked by this battery's firmware. |
  | 60 | 1 | `soc1_1` (SOC Model 1, reading 1) | uint8 | See soc1_0. |
  | 61 | 1 | `soc2_0` (SOC Model 2, reading 0) | uint8 | Second SOC estimation model. |
  | 62 | 1 | `soc2_1` (SOC Model 2, reading 1) | uint8 | See soc2_0. |
  | 63 | 2 | `sop_avg` (State of Power, Average) | uint16 | Byte-unaligned read; see handler_evidence for the sop_avg/sop_pulse same-offset caveat. |
  | 63 | 2 | `sop_pulse` (State of Power, Pulse) | uint16 | Disassembly reads this from the SAME offset as sop_avg (0x3f) -- flagged as an open inconsistency, not silently resolved. |
  | 67 | 2 | `kf_res_max` (Kalman-Filter Resistance Estimate, Max) | uint16 | Byte-unaligned read; internal-resistance estimate from a Kalman-filter-based SOC/health algorithm. Structure continues past this point; not traced further. |

**Worked example:**

- Request payload: ``
  The app polls the Center Board for full real-time battery telemetry (e.g. to render the in-app battery detail screen, or for dji_blackbox's own periodic health-management sweep). No request-side fields were identified; treated as a bare, payload-less query.
- Response payload: `24faffff603bfd000401ff0002018813d80e4c4c0300040000603b2a00000001000000020102030401000300010056faffff02c0d40100881338364c4c4b4d550000007800`
  69-byte dynamic-data response: discharging at 1500 mA, 15200 mV pack voltage, temperatures around 25-26 degC-scale, 5000/3800 mAh full/remaining capacity, 76% SOC, 42 charge cycles, app firmware v01.02.03.04, average current -1450 mA, ~120000 coulomb-count units passed, cell charge spread 54-56, two SOC-model readings around 75-77%, state-of-power ~85, Kalman resistance estimate 120.

## 0x23 — Center Req Bat Auth Data

_Not decoded._ Searched for 'bat_auth'/'battery auth'/'auth_data' across all binaries on both images. Found exactly one, isolated string 'is_bat_auth_fail' in dji_perception (E1E) via a plain `strings` dump; dji_perception has no .gnu_debugdata (fully stripped, no symbol names recoverable), and finding the function that references this string and determining whether it is even reachable from the DUML bus (vs. an unrelated internal sensor-battery check within the vision/perception subsystem) would require substantially more disassembly than the time available for this batch allowed. Reporting this as a real but unconfirmed lead rather than a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x24 — Center Req Bat Auth Result

_Not decoded._ Same lead and same caveat as 0x05/0x23 ('is_bat_auth_fail' in dji_perception, unconfirmed). Given the predicate-style naming ('is_X_fail'), if this string does turn out to be relevant it would suggest the auth-result payload reduces to a simple pass/fail boolean somewhere, but I have no byte-offset evidence to back that up, so I am not asserting a layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x31 — Center Req Bat SelfDischarge Time

_Not decoded._ Same search as 0x05/0x09 ('selfdis'/'self_dis'/'discharge') across dji_sys and dji_blackbox on both images -- zero hits. No handler identified. Note for whoever picks this up next: dji_blackbox's PHM dynamic-data struct (see 0x05/0x22) does carry a confirmed 'sdsg_fsm' (self-discharge state machine) byte at offset 0x22 of that struct, so the self-discharge STATE is tracked somewhere, but that is a state-machine value inside a different command's payload, not evidence of this Req/Set Time pair's own wire format. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x32 — Center Set Bat SelfDischarge Time

_Not decoded._ Same search and same result as 0x05/0x31. No handler identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x33 — Center Req Bat Barcode

_Not decoded._ Searched for 'barcode'/'bat_barcode' across every binary on both images -- zero hits anywhere (including dji_sys and dji_blackbox, which otherwise have rich, confirmed battery-telemetry vocabulary). Checked the task's shared-handler hint against the already-documented cmd_set 0x0D/0x04 'Battery BarCode Data Get' sibling: that command's existing dissector is itself thin (unk1[2 bytes] + length[1 byte] + variable string), so there was nothing substantive to confirm sharing against even if the handler were the same. No handler identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
