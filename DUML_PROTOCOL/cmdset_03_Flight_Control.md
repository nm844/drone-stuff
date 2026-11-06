# Cmd Set 0x03 — Flight Control

Total known command IDs: 192

## 0x00 — FlyC Scan/Test

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x01 — FlyC Status Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x02 — FlyC Params Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — Origin GPS Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — Origin GPS Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — GPS Coordinate Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — Fly Limit Param Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x07 — Fly Limit Param Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x08 — Nofly Zone Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x09 — Nofly Status Get

Payload decoder: `flyc_flyc_forbid_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_forbid_status_flight_limit_area_state` (Flight Limit Area State) | uint8 | enum:`enums.FLYC_FORBID_STATUS_FLIGHT_LIMIT_AREA_STATE_DJI_FLIGHT_LIMIT_AREA_STATE_ENUM` |
  | 1 | 1 | `flyc_flyc_forbid_status_dji_flight_limit_action_event` (Dji Flight Limit Action Event) | uint8 | enum:`enums.FLYC_FORBID_STATUS_DJI_FLIGHT_LIMIT_ACTION_EVENT_ENUM` |
  | 2 | 1 | `flyc_flyc_forbid_status_limit_space_num` (Limit Space Num) | uint8 |  |
  | 3 | 4 | `flyc_flyc_forbid_status_unknown3` (Unknown3) | bytes |  |

## 0x0A — Battery Status Get

Payload decoder: `flyc_battery_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_battery_status_not_ready` (Not Ready) | uint8 |  |
  | 1 | 1 | `flyc_battery_status_comm_err` (Comm Err) | uint8 |  |
  | 2 | 1 | `flyc_battery_status_first_auth` (First Auth) | uint8 |  |
  | 3 | 1 | `flyc_battery_status_auth_fail` (Auth Fail) | uint8 |  |
  | 4 | 1 | `flyc_battery_status_need_re` (Need Re) | uint8 |  |
  | 5 | 1 | `flyc_battery_status_volverylow` (Voltage Very Low) | uint8 |  |
  | 6 | 1 | `flyc_battery_status_volnotsafe` (Voltage Not Safe) | uint8 |  |
  | 7 | 1 | `flyc_battery_status_vollevel1` (Voltage Level 1) | uint8 |  |
  | 8 | 1 | `flyc_battery_status_vollevel2` (Voltage Level 2) | uint8 |  |
  | 9 | 1 | `flyc_battery_status_caplevel1` (Capacity Level 1) | uint8 |  |
  | 10 | 1 | `flyc_battery_status_caplevel2` (Capacity Level 2) | uint8 |  |
  | 11 | 1 | `flyc_battery_status_smartcap1` (Smart Capacity 1) | uint8 |  |
  | 12 | 1 | `flyc_battery_status_smartcap2` (Smart Capacity 2) | uint8 |  |
  | 13 | 1 | `flyc_battery_status_d_flg` (D Flag) | uint8 |  |
  | 14 | 1 | `flyc_battery_status_ccsc` (CCSC) | uint8 |  |
  | 15 | 4 | `flyc_battery_status_all` (All Flags Combined) | uint32 |  |

## 0x0B — Motor Work Status Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0C — Motor Work Status Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0D — Statistical Info Save

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0E — Emergency Stop

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x10 — A2 Push Commom

Payload decoder: `flyc_a2_commom_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_a2_commom_a` (A) | uint8 |  |
  | 1 | 1 | `flyc_a2_commom_b` (B) | uint8 |  |
  | 2 | 4 | `flyc_a2_commom_c` (C) | uint32 |  |
  | 6 | 4 | `flyc_a2_commom_d` (D) | uint32 |  |
  | 10 | 1 | `flyc_a2_commom_control_mode` (Control Mode) | uint8 | enum:`enums.FLYC_A2_COMMOM_E_DJIA2_CTRL_MODE_ENUM` |
  | 11 | 1 | `flyc_a2_commom_f` (F) | uint8 |  |

## 0x11 — Sim Rc

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x16 — Sim Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1C — Date and Time Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1D — Initialize Onboard FChannel

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1E — Get Onboard FChannel Output

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1F — Set Onboard FChannel Output

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — Send GPS To Flyc

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — UAV Status Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — Upload Air Route

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x23 — Download Air Route

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x24 — Upload Waypoint

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x25 — Download Waypoint

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x26 — Enable Waypoint

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x27 — Exec Fly

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x28 — One Key Back

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x29 — Joystick

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2A — (name unknown)

Payload decoder: `flyc_function_control_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_function_control_function_command` (Function/Command) | uint8 | New value of g_real.wm610_app_command.function_command |

## 0x2A — Function Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2B — IOC Mode Type Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2C — IOC Mode Type Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2D — Limit Params Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2E — Limit Params Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2F — Battery Voltage Alarm Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x30 — Battery Voltage Alarm Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x31 — UAV Home Point Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x32 — FlyC Deform Status Get

Payload decoder: `flyc_flyc_deform_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_deform_status_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `flyc_flyc_deform_status_deform_protected` (Deform Protected) | uint8 | mask:`0x01` |
  | 0 | 1 | `flyc_flyc_deform_status_deform_status` (Deform Status) | uint8 | enum:`enums.FLYC_DEFORM_STATUS_DEFORM_STATUS_TRIPOD_STATUS_ENUM`; mask:`0x0e` |
  | 0 | 1 | `flyc_flyc_deform_status_deform_mode` (Deform Mode) | uint8 | enum:`enums.FLYC_DEFORM_STATUS_DEFORM_MODE_ENUM`; mask:`0x30` |

## 0x33 — UAV User String Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x34 — UAV User String Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x35 — Change Param Ping

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x36 — Request SN

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x37 — Device Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x38 — Device Info Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x39 — Enter Flight Data Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3A — Ctrl Fly Data Recorder

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3B — RC Lost Action Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3C — RC Lost Action Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3D — Time Zone Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3E — FlyC Request Limit Update

Payload decoder: `flyc_flyc_request_limit_update_dissector`

## 0x3F — Set NoFly Zone Data

Payload decoder: `flyc_set_nofly_zone_data_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_set_nofly_zone_data_num_entries` (Number of entries) | uint8 | Amount of entries transfeered it this packet; value of 0 means end of transfer. |
  | 1 | 1 | `flyc_set_nofly_zone_data_frag_num` (Transfer fragment index) | uint8 | Fragment index |
  | 2 | 3 | `flyc_set_nofly_zone_data_reserved2` (Reserved2) | uint8 | Should be zeros |
  | 5 | 4 | `flyc_nofly_zone_entry_latitude` (Latitude) | uint8 |  |
  | 9 | 4 | `flyc_nofly_zone_entry_longitude` (Longitude) | uint8 |  |
  | 13 | 2 | `flyc_nofly_zone_entry_radius` (Radius) | uint8 |  |
  | 15 | 2 | `flyc_nofly_zone_entry_contry_code` (Contry Code) | uint8 |  |
  | 17 | 1 | `flyc_nofly_zone_entry_type` (Type) | uint8 |  |
  | 18 | 4 | `flyc_nofly_zone_entry_id` (Id) | uint8 |  |

## 0x41 — Upload Unlimit Areas

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x42 — FlyC Unlimit State / UAV Posture

Payload decoder: `flyc_flyc_unlimit_state_dissector`

  *if (payload:len() >= 35) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_uav_posture_param0` (Param0) | float | Sum of squares of params 0..3 must give 1.0 for the values to be accepted |
  | 4 | 4 | `flyc_uav_posture_param1` (Param1) | float |  |
  | 8 | 4 | `flyc_uav_posture_param2` (Param2) | float |  |
  | 12 | 4 | `flyc_uav_posture_param3` (Param3) | float |  |
  | 16 | 4 | `flyc_uav_posture_param4` (Param4) | float |  |
  | 20 | 4 | `flyc_uav_posture_param5` (Param5) | float |  |
  | 24 | 4 | `flyc_uav_posture_param6` (Param6) | float |  |
  | 28 | 4 | `flyc_uav_posture_param7` (Param7) | float |  |
  | 32 | 1 | `flyc_uav_posture_has8` (Has8-unknown) | uint8 |  |
  | 33 | 2 | `flyc_uav_posture_unkn21` (Unknown21) | uint16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_unlimit_state_is_in_unlimit_area` (Is In Unlimit Area) | uint8 |  |
  | 1 | 1 | `flyc_flyc_unlimit_state_unlimit_areas_action` (Unlimit Areas Action) | uint8 |  |
  | 2 | 1 | `flyc_flyc_unlimit_state_unlimit_areas_size` (Unlimit Areas Size) | uint8 |  |
  | 3 | 1 | `flyc_flyc_unlimit_state_unlimit_areas_enabled` (Unlimit Areas Enabled) | uint8 |  |

## 0x43 — OSD General Data Get

Payload decoder: `flyc_osd_general_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `flyc_osd_general_longtitude` (Longtitude) | double |  |
  | 8 | 8 | `flyc_osd_general_latitude` (Latitude) | double |  |
  | 16 | 2 | `flyc_osd_general_relative_height` (Relative Height) | int16 | 0.1m |
  | 18 | 2 | `flyc_osd_general_vgx` (Vgx speed) | int16 | 0.1m/s |
  | 20 | 2 | `flyc_osd_general_vgy` (Vgy speed) | int16 | 0.1m/s; // offset = 20 |
  | 22 | 2 | `flyc_osd_general_vgz` (Vgz speed) | int16 | 0.1m/s |
  | 24 | 2 | `flyc_osd_general_pitch` (Pitch) | int16 | 0.1 |
  | 26 | 2 | `flyc_osd_general_roll` (Roll) | int16 |  |
  | 28 | 2 | `flyc_osd_general_yaw` (Yaw) | int16 |  |
  | 30 | 1 | `flyc_osd_general_ctrl_info` (Control Info) | uint8 |  |
  | 30 | 1 | `flyc_osd_general_flyc_state` (FC State) | uint8 | enum:`enums.FLYC_OSD_GENERAL_FLYC_STATE_ENUM`; mask:`0x7F`; Flight Controller state1 |
  | 30 | 1 | `flyc_osd_general_no_rc_state` (No RC State Received) | uint8 | mask:`0x80` |
  | 31 | 1 | `flyc_osd_general_latest_cmd` (Latest App Cmd) | uint8 | enum:`enums.FLYC_OSD_GENERAL_COMMAND_ENUM`; controller exccute lastest cmd |
  | 32 | 4 | `flyc_osd_general_controller_state` (Controller State) | uint32 | Flight Controller state flags |
  | 32 | 4 | `flyc_osd_general_e_can_ioc_work` (E Can IOC Work) | uint32 | mask:`0x01` |
  | 32 | 4 | `flyc_osd_general_e_on_ground` (E On Ground) | uint32 | mask:`0x02` |
  | 32 | 4 | `flyc_osd_general_e_in_air` (E In Air) | uint32 | mask:`0x04` |
  | 32 | 4 | `flyc_osd_general_e_motor_on` (E Motor On) | uint32 | mask:`0x08`; Force allow start motors ignoring errors |
  | 32 | 4 | `flyc_osd_general_e_usonic_on` (E Usonic On) | uint32 | mask:`0x10`; Ultrasonic wave sonar in use |
  | 32 | 4 | `flyc_osd_general_e_gohome_state` (E Gohome State) | uint32 | enum:`enums.FLYC_OSD_GENERAL_GOHOME_STATE_ENUM`; mask:`0xe0` |
  | 32 | 4 | `flyc_osd_general_e_mvo_used` (E MVO Used) | uint32 | mask:`0x100`; Monocular Visual Odometry is used as horizonal velocity sensor |
  | 32 | 4 | `flyc_osd_general_e_battery_req_gohome` (E Battery Req Gohome) | uint32 | mask:`0x200` |
  | 32 | 4 | `flyc_osd_general_e_battery_req_land` (E Battery Req Land) | uint32 | mask:`0x400`; Landing required due to battery voltage low |
  | 32 | 4 | `flyc_osd_general_e_still_heating` (E Still Heating) | uint32 | mask:`0x1000`; IMU Preheating |
  | 32 | 4 | `flyc_osd_general_e_rc_state` (E RC Mode Channel) | uint32 | enum:`enums.FLYC_OSD_GENERAL_MODE_CHANNEL_RC_MODE_CHANNEL_ENUM`; mask:`0x6000` |
  | 32 | 4 | `flyc_osd_general_e_gps_used` (E GPS Used) | uint32 | mask:`0x8000`; Satellite Positioning System is used as horizonal velocity sensor |
  | 32 | 4 | `flyc_osd_general_e_compass_over_range` (E Compass Over Range) | uint32 | mask:`0x10000` |
  | 32 | 4 | `flyc_osd_general_e_wave_err` (E Wave Error) | uint32 | mask:`0x20000`; Ultrasonic sensor error |
  | 32 | 4 | `flyc_osd_general_e_gps_level` (E GPS Level) | uint32 | mask:`0x3C0000`; Satellite Positioning System signal level |
  | 32 | 4 | `flyc_osd_general_e_battery_type` (E Battery Type) | uint32 | enum:`enums.FLYC_OSD_GENERAL_BATT_TYPE_ENUM`; mask:`0xC00000` |
  | 32 | 4 | `flyc_osd_general_e_accel_over_range` (E Acceletor Over Range) | uint32 | mask:`0x1000000` |
  | 32 | 4 | `flyc_osd_general_e_is_vibrating` (E Is Vibrating) | uint32 | mask:`0x2000000` |
  | 32 | 4 | `flyc_osd_general_e_press_err` (E Press Err) | uint32 | mask:`0x4000000`; Barometer error |
  | 32 | 4 | `flyc_osd_general_e_esc_stall` (E ESC is stall) | uint32 | mask:`0x8000000`; ESC reports motor blocked |
  | 32 | 4 | `flyc_osd_general_e_esc_empty` (E ESC is empty) | uint32 | mask:`0x10000000`; ESC reports not enough force |
  | 32 | 4 | `flyc_osd_general_e_propeller_catapult` (E Propeller Catapult) | uint32 | mask:`0x20000000` |
  | 32 | 4 | `flyc_osd_general_e_gohome_height_mod` (E GoHome Height Mod) | uint32 | mask:`0x40000000`; Go Home Height is Modified |
  | 32 | 4 | `flyc_osd_general_e_out_of_limit` (E Is Out Of Limit) | uint32 | mask:`0x80000000` |
  | 36 | 1 | `flyc_osd_general_gps_nums` (Gps Nums) | uint8 | Number of Global Nav System positioning satellites |
  | 37 | 1 | `flyc_osd_general_gohome_landing_reason` (Gohome or Landing Reason) | uint8 | enum:`enums.FLYC_OSD_GENERAL_GOHOME_REASON_ENUM`; Reason for automatic GoHome or Landing |
  | 38 | 1 | `flyc_osd_general_start_fail_state` (Motor Start Failure State) | uint8 |  |
  | 38 | 1 | `flyc_osd_general_start_fail_reason` (Motor Start Fail Reason) | uint8 | enum:`enums.FLYC_OSD_GENERAL_START_FAIL_REASON_ENUM`; mask:`0x7f`; Reason for failure to start motors |
  | 38 | 1 | `flyc_osd_common_start_fail_happened` (Motor Start Fail Happened) | uint8 | mask:`0x80` |
  | 39 | 1 | `flyc_osd_general_controller_state_ext` (Controller State Ext) | uint8 |  |
  | 39 | 1 | `flyc_osd_general_e_gps_state` (E Gps State) | uint8 | enum:`enums.FLYC_OSD_GENERAL_GPS_STATE_ENUM`; mask:`0x0f`; Cause of not being able to switch to GPS mode |
  | 39 | 1 | `flyc_osd_general_e_wp_limit_md` (E Wp Limit Mode) | uint8 | mask:`0x10`; Waypoint Limit Mode |
  | 40 | 1 | `flyc_osd_general_batt_remain` (Battery Remain) | uint8 | Battery Remaining Capacity; // offset = 40 |
  | 41 | 1 | `flyc_osd_general_ultrasonic_height` (Ultrasonic Height) | uint8 | Height as reported by ultrasonic wave sensor |
  | 42 | 2 | `flyc_osd_general_motor_startup_time` (Motor Started Time) | uint16 | aka Fly Time |
  | 44 | 1 | `flyc_osd_general_motor_startup_times` (Motor Starts Count) | uint8 | aka Motor Revolution |
  | 45 | 1 | `flyc_osd_general_bat_alarm1` (Bat Alarm1) | uint8 |  |
  | 45 | 1 | `flyc_osd_general_bat_alarm1_ve` (Alarm Level 1 Voltage) | uint8 | mask:`0x7F` |
  | 45 | 1 | `flyc_osd_general_bat_alarm1_fn` (Alarm Level 1 Function) | uint8 | mask:`0x80` |
  | 46 | 1 | `flyc_osd_general_bat_alarm2` (Bat Alarm2) | uint8 |  |
  | 46 | 1 | `flyc_osd_general_bat_alarm2_ve` (Alarm Level 2 Voltage) | uint8 | mask:`0x7F` |
  | 46 | 1 | `flyc_osd_general_bat_alarm2_fn` (Alarm Level 2 Function) | uint8 | mask:`0x80` |
  | 47 | 1 | `flyc_osd_general_version_match` (Version Match) | uint8 | Flight Controller version |
  | 48 | 1 | `flyc_osd_general_product_type` (Product Type) | uint8 | enum:`enums.FLYC_OSD_GENERAL_PRODUCT_TYPE_ENUM` |
  | 49 | 1 | `flyc_osd_general_imu_init_fail_reson` (IMU init Fail Reason) | int8 | enum:`enums.FLYC_OSD_GENERAL_IMU_INIT_FAIL_RESON_ENUM` |

  *if (payload:len() >= offset + 5) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 50 | 1 | `flyc_osd_common_motor_fail_reason` (Motor Fail Reason) | uint8 | enum:`enums.FLYC_OSD_GENERAL_START_FAIL_REASON_ENUM` |
  | 51 | 1 | `flyc_osd_common_motor_start_cause_no_start_action` (Motor Start Cause No Start Action) | uint8 | enum:`enums.FLYC_OSD_GENERAL_START_FAIL_REASON_ENUM` |
  | 52 | 1 | `flyc_osd_common_sdk_ctrl_device` (Sdk Ctrl Device) | uint8 | enum:`enums.FLYC_OSD_GENERAL_SDK_CTRL_DEVICE_ENUM` |
  | 53 | 2 | `flyc_osd_common_unknown35` (Unknown35) | uint16 |  |

## 0x44 — OSD Home Point Get

Payload decoder: `flyc_osd_home_point_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `flyc_osd_home_point_osd_lon` (OSD Longitude) | double |  |
  | 8 | 8 | `flyc_osd_home_point_osd_lat` (OSD Latitude) | double |  |
  | 16 | 4 | `flyc_osd_home_point_osd_alt` (OSD Altitude) | float | 0.1m |
  | 20 | 2 | `flyc_osd_home_point_osd_home_state` (OSD Home State) | uint16 |  |
  | 20 | 2 | `flyc_osd_home_point_e_homepoint_set` (E Homepoint Set) | uint16 | mask:`0x01`; Is Home Point Recorded |
  | 20 | 2 | `flyc_osd_home_point_e_go_home_mode` (E Go Home Mode) | uint16 | mask:`0x02` |
  | 20 | 2 | `flyc_osd_home_point_e_heading` (E Heading) | uint16 | mask:`0x04`; Aircraft Head Direction |
  | 20 | 2 | `flyc_osd_home_point_e_is_dyn_homepoint` (E Is Dyn Homepoint) | uint16 | mask:`0x08`; Dynamic Home Piont Enable |
  | 20 | 2 | `flyc_osd_home_point_e_reach_limit_distance` (E Reach Limit Distance) | uint16 | mask:`0x10` |
  | 20 | 2 | `flyc_osd_home_point_e_reach_limit_height` (E Reach Limit Height) | uint16 | mask:`0x20` |
  | 20 | 2 | `flyc_osd_home_point_e_multiple_mode_open` (E Multiple Mode Open) | uint16 | mask:`0x40` |
  | 20 | 2 | `flyc_osd_home_point_e_has_go_home` (E Has Go Home) | uint16 | mask:`0x80` |
  | 20 | 2 | `flyc_osd_home_point_e_compass_cele_status` (E Compass Cele Status) | uint16 | mask:`0x300` |
  | 20 | 2 | `flyc_osd_home_point_e_compass_celeing` (E Compass Celeing) | uint16 | mask:`0x400` |
  | 20 | 2 | `flyc_osd_home_point_e_beginner_mode` (E Beginner Mode) | uint16 | mask:`0x800` |
  | 20 | 2 | `flyc_osd_home_point_e_ioc_enable` (E Ioc Enable) | uint16 | mask:`0x1000` |
  | 20 | 2 | `flyc_osd_home_point_e_ioc_mode` (E Ioc Mode) | uint16 | enum:`enums.FLYC_OSD_HOME_IOC_MODE_ENUM`; mask:`0xe000` |
  | 22 | 2 | `flyc_osd_home_point_go_home_height` (Go Home Height) | uint16 | aka Fixed Altitude |
  | 24 | 2 | `flyc_osd_home_point_course_lock_angle` (Course Lock Angle) | uint16 | Course Lock Torsion |
  | 26 | 1 | `flyc_osd_home_point_data_recorder_status` (Data Recorder Status) | uint8 |  |
  | 27 | 1 | `flyc_osd_home_point_data_recorder_remain_capacity` (Data Recorder Remain Capacity) | uint8 |  |
  | 28 | 2 | `flyc_osd_home_point_data_recorder_remain_time` (Data Recorder Remain Time) | uint16 |  |
  | 30 | 2 | `flyc_osd_home_point_cur_data_recorder_file_index` (Cur Data Recorder File Index) | uint16 |  |

  *if (payload:len() < 68) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 32 | 2 | `flyc_osd_home_point_ver1_masked20` (Masked20) | uint16 |  |
  | 32 | 2 | `flyc_osd_home_point_ver1_flyc_in_simulation_mode` (FlyC In Simulation Mode) | uint16 | mask:`0x01` |
  | 32 | 2 | `flyc_osd_home_point_ver1_flyc_in_navigation_mode` (FlyC In Navigation Mode) | uint16 | mask:`0x02` |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 32 | 4 | `flyc_osd_home_point_masked20` (Masked20) | uint32 |  |
  | 32 | 4 | `flyc_osd_home_point_flyc_in_simulation_mode` (FlyC In Simulation Mode) | uint32 | mask:`0x01` |
  | 32 | 4 | `flyc_osd_home_point_flyc_in_navigation_mode` (FlyC In Navigation Mode) | uint32 | mask:`0x02` |
  | 32 | 4 | `flyc_osd_home_point_wing_broken` (Wing Broken) | uint32 | mask:`0x1000` |
  | 32 | 4 | `flyc_osd_home_point_big_gale` (Big Gale) | uint32 | mask:`0x4000` |
  | 32 | 4 | `flyc_osd_home_point_big_gale_warning` (Big Gale Warning) | uint32 | mask:`0x100000` |
  | 32 | 4 | `flyc_osd_home_point_compass_install_err` (Compass Install Err) | uint32 | mask:`0x800000` |
  | 32 | 4 | `flyc_osd_home_point_height_limit_status` (Height Limit Status) | uint32 | enum:`enums.FLYC_OSD_HOME_HEIGHT_LIMIT_STATUS_ENUM`; mask:`0x1f000000` |
  | 32 | 4 | `flyc_osd_home_point_use_absolute_height` (Use Absolute Height) | uint32 | mask:`0x20000000` |
  | 36 | 4 | `flyc_osd_home_point_height_limit_value` (Height Limit Value) | float |  |
  | 40 | 5 | `flyc_osd_home_point_unknown28` (Unknown28) | bytes |  |
  | 45 | 1 | `flyc_osd_home_point_force_landing_height` (Force Landing Height) | uint8 |  |
  | 46 | 22 | `flyc_osd_home_point_unknown2E` (Unknown2E) | bytes |  |

## 0x45 — FlyC GPS SNR Get

Payload decoder: `flyc_flyc_gps_snr_dissector`

## 0x46 — FlyC GPS SNR Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x47 — Enable Unlimit Areas

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x49 — Push Encrypted Package

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4A — Push Att IMU Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4B — Push RC Stick Value

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4C — Push Fussed Pos Speed Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x50 — Imu Data Status

Payload decoder: `flyc_imu_data_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_imu_data_status_start_fan` (Start Fan) | uint8 | On P3 |
  | 1 | 1 | `flyc_imu_data_status_led_status` (Led Status) | uint8 | On P3 |

## 0x51 — FlyC Battery Status Get

Payload decoder: `flyc_flyc_battery_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_flyc_battery_status_useful_time` (Useful Time) | uint16 |  |
  | 2 | 2 | `flyc_flyc_battery_status_go_home_time` (Go Home Time) | uint16 |  |
  | 4 | 2 | `flyc_flyc_battery_status_land_time` (Land Time) | uint16 |  |
  | 6 | 2 | `flyc_flyc_battery_status_go_home_battery` (Go Home Battery) | uint16 |  |
  | 8 | 2 | `flyc_flyc_battery_status_land_battery` (Land Battery) | uint16 |  |
  | 10 | 4 | `flyc_flyc_battery_status_safe_fly_radius` (Safe Fly Radius) | float |  |
  | 14 | 4 | `flyc_flyc_battery_status_volume_comsume` (Volume Comsume) | float |  |
  | 18 | 4 | `flyc_flyc_battery_status_status` (Status) | uint32 |  |
  | 22 | 1 | `flyc_flyc_battery_status_go_home_status` (Go Home Status) | uint8 | enum:`enums.FLYC_SMART_BATTERY_GO_HOME_STATUS_SMART_GO_HOME_STATUS_ENUM` |
  | 23 | 1 | `flyc_flyc_battery_status_go_home_count_down` (Go Home Count Down) | uint8 |  |
  | 24 | 2 | `flyc_flyc_battery_status_voltage` (Voltage) | uint16 |  |
  | 26 | 1 | `flyc_flyc_battery_status_battery_percent` (Battery Percent) | uint8 |  |
  | 27 | 1 | `flyc_flyc_battery_status_masked1b` (Masked1B) | uint8 |  |
  | 27 | 1 | `flyc_flyc_battery_status_low_warning` (Low Warning) | uint8 | mask:`0x7f` |
  | 27 | 1 | `flyc_flyc_battery_status_low_warning_go_home` (Low Warning Go Home) | uint8 | mask:`0x80` |
  | 28 | 1 | `flyc_flyc_battery_status_masked1c` (Masked1C) | uint8 |  |
  | 28 | 1 | `flyc_flyc_battery_status_serious_low_warning` (Serious Low Warning) | uint8 | mask:`0x7f` |
  | 28 | 1 | `flyc_flyc_battery_status_serious_low_warning_landing` (Serious Low Warning Landing) | uint8 | mask:`0x80` |
  | 29 | 1 | `flyc_flyc_battery_status_voltage_percent` (Voltage Percent) | uint8 |  |

## 0x52 — Smart Low Battery Actn Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x53 — FlyC Vis Avoidance Param Get

Payload decoder: `flyc_flyc_vis_avoid_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_flyc_vis_avoid_param_masked00` (Masked00) | uint16 |  |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_obstacle_enable` (Avoid Obstacle Enable) | uint16 | mask:`0x01` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_user_avoid_enable` (User Avoid Enable) | uint16 | mask:`0x02` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_get_avoid_obstacle_work_flag` (Get Avoid Obstacle Work Flag) | uint16 | mask:`0x04` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_get_emergency_brake_work_flag` (Get Emergency Brake Work Flag) | uint16 | mask:`0x08` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_gohome_avoid_enable` (Gohome Avoid Enable) | uint16 | mask:`0x10` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_ground_force_landing` (Avoid Ground Force Landing) | uint16 | mask:`0x20` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_radius_limit_working` (Radius Limit Working) | uint16 | mask:`0x40` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_airport_limit_working` (Airport Limit Working) | uint16 | mask:`0x80` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_obstacle_working` (Avoid Obstacle Working) | uint16 | mask:`0x100` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_horiz_near_boundary` (Horiz Near Boundary) | uint16 | mask:`0x200` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_overshot_act` (Avoid Overshot Act) | uint16 | mask:`0x400` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_vert_low_limit_work_flag` (Vert Low Limit Work Flag) | uint16 | mask:`0x800` |

## 0x55 — FlyC Limit State Get

Payload decoder: `flyc_flyc_limit_state_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `flyc_flyc_limit_state_latitude` (Latitude) | double |  |
  | 8 | 8 | `flyc_flyc_limit_state_longitude` (Longitude) | double |  |
  | 16 | 2 | `flyc_flyc_limit_state_inner_radius` (Inner Radius) | uint16 |  |
  | 18 | 2 | `flyc_flyc_limit_state_outer_radius` (Outer Radius) | uint16 |  |
  | 20 | 1 | `flyc_flyc_limit_state_type` (Type) | uint8 |  |
  | 21 | 1 | `flyc_flyc_limit_state_area_state` (Area State) | uint8 |  |
  | 22 | 1 | `flyc_flyc_limit_state_action_state` (Action State) | uint8 |  |
  | 23 | 1 | `flyc_flyc_limit_state_enable` (Enable) | uint8 |  |

## 0x56 — FlyC LED Status Get

Payload decoder: `flyc_flyc_led_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_led_status_led_reason` (Led Reason) | uint32 | enum:`enums.FLYC_LED_STATUS_LED_REASON_ENUM` |

## 0x57 — GPS GLNS Info

Payload decoder: `flyc_gps_glns_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_gps_glns_gps_lon` (Gps Lon) | int32 |  |
  | 4 | 4 | `flyc_gps_glns_gps_lat` (Gps Lat) | int32 |  |
  | 8 | 4 | `flyc_gps_glns_hmsl` (Hmsl) | int32 |  |
  | 12 | 4 | `flyc_gps_glns_vel_n` (Vel N) | float |  |
  | 16 | 4 | `flyc_gps_glns_vel_e` (Vel E) | float |  |
  | 20 | 4 | `flyc_gps_glns_vel_d` (Vel D) | float |  |
  | 24 | 4 | `flyc_gps_glns_hdop` (Hdop) | float |  |
  | 28 | 2 | `flyc_gps_glns_numsv` (NumSV) | uint16 | Number of Global Nav System positioning satellites |
  | 30 | 2 | `flyc_gps_glns_gpsglns_cnt` (Gps Glns Count) | uint16 | Sequence counter increased each time the packet of this type is prepared |
  | 32 | 1 | `flyc_gps_glns_unkn20` (Unknown 20) | uint8 |  |
  | 33 | 1 | `flyc_gps_glns_homepoint_set` (Homepoint Set) | uint8 |  |

## 0x58 — Push Att Stick Speed Pos Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x59 — Push Sdk Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x5A — Push FC Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x60 — SVO API Transfer

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x61 — FlyC Activation Info

Payload decoder: `flyc_flyc_active_request_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_active_request_app_id` (App Id) | uint32 |  |
  | 4 | 4 | `flyc_flyc_active_request_app_level` (App Level) | uint32 |  |
  | 8 | 4 | `flyc_flyc_active_request_app_version` (App Version) | uint32 |  |

## 0x62 — FlyC Activation Exec

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x63 — FlyC On Board Recv

Payload decoder: `flyc_flyc_board_recv_dissector`

## 0x64 — Send On Board Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x67 — FlyC Power Param Get

Payload decoder: `flyc_flyc_power_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_power_param_esc_average_speed` (Esc Average Speed) | float |  |
  | 4 | 4 | `flyc_flyc_power_param_lift` (Lift) | float |  |

## 0x69 — RTK Switch

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x6A — FlyC Avoid

Payload decoder: `flyc_flyc_avoid_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_avoid_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `flyc_flyc_avoid_visual_sensor_enable` (Visual Sensor Enable) | uint8 | mask:`0x01` |
  | 0 | 1 | `flyc_flyc_avoid_visual_sensor_work` (Visual Sensor Work) | uint8 | mask:`0x02` |
  | 0 | 1 | `flyc_flyc_avoid_in_stop` (In Stop) | uint8 | mask:`0x04` |

## 0x6B — Recorder Data Cfg

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x6C — FlyC RTK Location Data Get

Payload decoder: `flyc_flyc_rtk_location_data_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `flyc_flyc_rtk_location_data_longitude` (Longitude) | double |  |
  | 8 | 8 | `flyc_flyc_rtk_location_data_latitude` (Latitude) | double |  |
  | 16 | 4 | `flyc_flyc_rtk_location_data_height` (Height) | float |  |
  | 20 | 2 | `flyc_flyc_rtk_location_data_heading` (Heading) | uint16 |  |
  | 22 | 1 | `flyc_flyc_rtk_location_data_rtk_connected` (Rtk Connected) | uint8 |  |
  | 23 | 1 | `flyc_flyc_rtk_location_data_rtk_canbe_used` (Rtk Can be Used) | uint8 |  |

  *if (payload:len() >= offset + 8) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 24 | 4 | `flyc_flyc_rtk_location_data_unknown18` (Unknown18) | uint32 |  |
  | 28 | 4 | `flyc_flyc_rtk_location_data_unknown1C` (Unknown1C) | uint32 |  |

## 0x6D — Upload Hotpoint

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x6E — Download Hotpoint

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x70 — Set Product SN

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x71 — Get Product SN

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x72 — Reset Product SN

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x73 — Set Product Id

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x74 — Get Product Id

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x75 — Write EEPROM FC0

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x76 — Read EEPROM FC0

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x80 — Navigation Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x81 — Mission IOC: Set Lock Yaw

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x82 — Miss. WP: Upload Mission Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x83 — Miss. WP: Download Mission Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x84 — Upload Waypoint Info By Idx

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x85 — Download Waypoint Info By Idx

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x86 — Mission WP: Go/Stop

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x87 — Mission WP: Pasue/Resume

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x88 — Push Navigation Status Info

Payload decoder: `flyc_flyc_way_point_mission_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_way_point_mission_info_mission_type` (Mission Type) | uint8 | enum:`enums.FLYC_WAY_POINT_MISSION_INFO_MISSION_TYPE_ENUM` |

  *if (mission_type == 0x01) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_target_way_point` (Target Way Point) | uint8 |  |
  | 2 | 2 | `flyc_flyc_way_point_mission_info_limited_height` (Limited Height) | uint16 |  |
  | 4 | 1 | `flyc_flyc_way_point_mission_info_running_status` (Way Point Running Status) | uint8 | enum:`enums.FLYC_WAY_POINT_MISSION_INFO_RUNNING_STATUS_ENUM` |
  | 5 | 1 | `flyc_flyc_way_point_mission_info_wp_unknown5` (Way Point Unknown5) | uint8 |  |

  *elseif (mission_type == 0x02) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_hot_point_mission_status` (Hot Point Mission Status) | uint8 |  |
  | 2 | 2 | `flyc_flyc_way_point_mission_info_hot_point_radius` (Hot Point Radius) | uint16 |  |
  | 4 | 1 | `flyc_flyc_way_point_mission_info_hot_point_reason` (Hot Point Reason) | uint8 |  |
  | 5 | 1 | `flyc_flyc_way_point_mission_info_hot_point_speed` (Hot Point Speed) | uint8 |  |

  *elseif (mission_type == 0x03) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_follow_me_flags` (Follow Me Flags) | uint8 |  |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_follow_me_status` (Follow Me Status) | uint8 | mask:`0x0f` |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_follow_me_gps_level` (Follow Me Gps Level) | uint8 | mask:`0xf0` |
  | 2 | 2 | `flyc_flyc_way_point_mission_info_follow_me_distance` (Follow Me Distance) | uint16 |  |
  | 4 | 1 | `flyc_flyc_way_point_mission_info_follow_me_reason` (Follow Me Reason) | uint8 |  |
  | 5 | 1 | `flyc_flyc_way_point_mission_info_follow_me_unknown6` (Follow Me Unknown6) | uint8 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_mission_flags` (Mission Flags) | uint8 |  |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_mission_status` (Mission Status) | uint8 | mask:`0x03` |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_position_valid` (Position Valid) | uint8 | mask:`0x04` |
  | 2 | 1 | `flyc_flyc_way_point_mission_info_current_status` (Current Status) | uint8 |  |
  | 3 | 1 | `flyc_flyc_way_point_mission_info_error_notification` (Error Notification) | uint8 |  |
  | 4 | 2 | `flyc_flyc_way_point_mission_info_current_height` (Current Height) | uint16 |  |

## 0x89 — Push Navigation Event Info

Payload decoder: `flyc_flyc_way_point_mission_current_event_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_way_point_mission_current_event_event_type` (Event Type) | uint8 | enum:`enums.FLYC_WAY_POINT_MISSION_CURRENT_EVENT_EVENT_TYPE_ENUM` |

  *if (event_type == 0x02) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_current_event_reach_incident_way_point_index` (Reach Incident Way Point Index) | uint8 | mask:`0xff` |
  | 2 | 1 | `flyc_flyc_way_point_mission_current_event_reach_incident_current_status` (Reach Incident Current Status) | uint8 | mask:`0xff` |
  | 3 | 1 | `flyc_flyc_way_point_mission_current_event_reach_incident_reserved` (Reach Incident Reserved) | uint8 | mask:`0xff` |

  *elseif (event_type == 0x03) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_current_event_upload_incident_is_valid` (Upload Incident Is Valid) | uint8 | mask:`0xff` |
  | 2 | 2 | `flyc_flyc_way_point_mission_current_event_upload_incident_estimated_time` (Upload Incident Estimated Time) | uint16 | mask:`0xffff` |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_current_event_finish_incident_is_repeat` (Finish Incident Is Repeat) | uint8 |  |
  | 2 | 2 | `flyc_flyc_way_point_mission_current_event_finish_incident_resrved` (Finish Incident Resrved) | uint16 |  |

## 0x8A — Miss. HotPoint: Start With Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x8B — Miss. HotPoint: Cancel

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x8C — Miss. HotPoint: Pasue/Resume

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x8D — App Set API Sub Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x8E — App Joystick Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x8F — Noe Mission pasue/resume

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x90 — Miss. Follow: Start With Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x91 — Miss. Follow: Cancel

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x92 — Miss. Follow: Pasue/Resume

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x93 — Miss. Follow: Get Target Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x94 — Mission Noe: Start

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x95 — Mission Noe: Stop

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x96 — Mission HotPoint: Download

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x97 — Mission IOC: Start

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x98 — Mission IOC: Stop

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x99 — Miss. HotPoint: Set Params

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x9A — Miss. HotPoint: Set Radius

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x9B — Miss. HotPoint: Set Head

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x9C — Miss. WP: Set Idle Veloc

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x9D — Miss. WP: Get Idle Veloc

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x9E — App Ctrl Mission Yaw Rate

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x9F — Miss. HotPoint: Auto Radius Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA0 — Send AGPS Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA1 — FlyC AGPS Status Get

Payload decoder: `flyc_flyc_agps_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_agps_status_time_stamp` (Time Stamp) | uint32 |  |
  | 4 | 4 | `flyc_flyc_agps_status_data_length` (Data Length) | uint32 |  |
  | 8 | 2 | `flyc_flyc_agps_status_crc16_hash` (Crc16 Hash) | uint16 |  |

## 0xA2 — Race Drone OSD Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA3 — Miss. WP: Get BreakPoint Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA4 — Miss. WP: Return To Cur Line

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA5 — App Ctrl Fly Sweep Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA6 — Set RKT Homepoint

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xAA — Sbus Packet

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xAB — Ctrl Attitude Data Send

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xAC — Ctrl Taillock Data Send

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xAD — FlyC Install Error Get

Payload decoder: `flyc_flyc_flyc_install_error_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_flyc_install_error_masked00` (Masked00) | uint32 |  |
  | 0 | 4 | `flyc_flyc_flyc_install_error_yaw_install_error_level` (Yaw Install Error Level) | uint32 | mask:`0x03` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_roll_install_error_level` (Roll Install Error Level) | uint32 | mask:`0x0c` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_pitch_install_error_level` (Pitch Install Error Level) | uint32 | mask:`0x30` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_gyro_x_install_error_level` (Gyro X Install Error Level) | uint32 | mask:`0xc0` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_gyro_y_install_error_level` (Gyro Y Install Error Level) | uint32 | mask:`0x300` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_gyro_z_install_error_level` (Gyro Z Install Error Level) | uint32 | mask:`0xc00` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_acc_x_install_error_level` (Acc X Install Error Level) | uint32 | mask:`0x3000` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_acc_y_install_error_level` (Acc Y Install Error Level) | uint32 | mask:`0xc000` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_acc_z_install_error_level` (Acc Z Install Error Level) | uint32 | mask:`0x30000` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_thrust_install_error_level` (Thrust Install Error Level) | uint32 | mask:`0xc0000` |

## 0xAE — Cmd Handler RC App Chl Handler

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xAF — Product Config

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xB0 — Get Battery Groups Single Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xB5 — FlyC Fault Inject Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xB6 — FlyC Fault Inject Get

Payload decoder: `flyc_flyc_fault_inject_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_fault_inject_status` (Status) | uint8 | enum:`enums.FLYC_FAULT_INJECT_STATUS_ENUM` |

## 0xB7 — Redundancy IMU Index Set and Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xB8 — Redundancy Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xB9 — Push Redundancy Status

Payload decoder: `flyc_flyc_redundancy_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_redundancy_status_cmd_type` (Command Type) | uint8 | enum:`enums.FLYC_REDUNDANCY_STATUS_CMD_TYPE_ENUM` |
  | 1 | 1 | `flyc_flyc_redundancy_status_unknown1` (Unknown1) | uint8 |  |
  | 2 | 1 | `flyc_flyc_redundancy_status_unknown2` (Unknown2) | uint8 |  |
  | 3 | 1 | `flyc_flyc_redundancy_status_unknown3` (Unknown3) | uint8 |  |
  | 4 | 1 | `flyc_flyc_redundancy_status_unknown4` (Unknown4) | uint8 |  |
  | 5 | 1 | `flyc_flyc_redundancy_status_unknown5` (Unknown5) | uint8 |  |
  | 6 | 1 | `flyc_flyc_redundancy_status_unknown6` (Unknown6) | uint8 |  |
  | 7 | 1 | `flyc_flyc_redundancy_status_unknown7` (Unknown7) | uint8 |  |
  | 8 | 1 | `flyc_flyc_redundancy_status_unknown8` (Unknown8) | uint8 |  |
  | 9 | 1 | `flyc_flyc_redundancy_status_unknown9` (Unknown9) | uint8 |  |
  | 10 | 1 | `flyc_flyc_redundancy_status_unknownA` (UnknownA) | uint8 |  |
  | 11 | 1 | `flyc_flyc_redundancy_status_unknownB` (UnknownB) | uint8 |  |

## 0xBA — Forearm LED Status Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xBB — Open LED Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xBC — Open Led Action Register

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xBD — Open Led Action Logout

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xBE — Open Led Action Status Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xBF — Flight Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xC6 — Shell Test

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xCD — Update Nofly Area

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xCE — Push Forbid Data Infos

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xCF — New Nofly Area Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xD4 — Additional Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xD7 — FlyC Flight Record Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xD9 — Process Sensor Api Data

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xDA — FlyC Detection

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xDF — Assistant Unlock Handler

Payload decoder: `flyc_assistant_unlock_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_assistant_unlock_lock_state` (Lock State) | uint32 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_assistant_unlock_status` (Status) | uint8 |  |

## 0xE0 — Config Table: Get Tbl Attribute

Payload decoder: `flyc_config_table_get_tbl_attribute_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_tbl_attribute_table_no` (Table No) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_tbl_attribute_status` (Status) | uint16 |  |

  *if (payload:len() - offset >= 6) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 2 | `flyc_config_table_get_tbl_attribute_table_no` (Table No) | int16 |  |
  | 4 | 4 | `flyc_config_table_get_tbl_attribute_entries_crc` (Table Entries Checksum) | uint32 |  |
  | 8 | 4 | `flyc_config_table_get_tbl_attribute_entries_num` (Table Entries Number) | uint32 |  |

## 0xE1 — Config Table: Get Item Attribute

Payload decoder: `flyc_config_table_get_item_attribute_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_attribute_table_no` (Table No) | int16 |  |
  | 2 | 2 | `flyc_config_table_get_item_attribute_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_attribute_status` (Status) | uint16 |  |

  *if (payload:len() >= 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 2 | `flyc_config_table_get_item_attribute_table_no` (Table No) | int16 |  |
  | 4 | 2 | `flyc_config_table_get_item_attribute_index` (Param Index) | int16 |  |
  | 6 | 2 | `flyc_config_table_get_item_attribute_type_id` (TypeID) | uint16 |  |
  | 8 | 2 | `flyc_config_table_get_item_attribute_size` (Size) | int16 |  |

  *if (type_id <= 3) or (type_id == 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 10 | 4 | `flyc_config_table_get_item_attribute_limit_u_def` (LimitU defaultValue) | uint32 |  |
  | 14 | 4 | `flyc_config_table_get_item_attribute_limit_u_min` (LimitU minValue) | uint32 |  |
  | 18 | 4 | `flyc_config_table_get_item_attribute_limit_u_max` (LimitU maxValue) | uint32 |  |

  *elseif (type_id >= 4) and (type_id <= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 10 | 4 | `flyc_config_table_get_item_attribute_limit_i_def` (LimitI defaultValue) | int32 |  |
  | 14 | 4 | `flyc_config_table_get_item_attribute_limit_i_min` (LimitI minValue) | int32 |  |
  | 18 | 4 | `flyc_config_table_get_item_attribute_limit_i_max` (LimitI maxValue) | int32 |  |

  *elseif (type_id == 8) or (type_id == 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 10 | 4 | `flyc_config_table_get_item_attribute_limit_f_def` (LimitF defaultValue) | float |  |
  | 14 | 4 | `flyc_config_table_get_item_attribute_limit_f_min` (LimitF minValue) | float |  |
  | 18 | 4 | `flyc_config_table_get_item_attribute_limit_f_max` (LimitF maxValue) | float |  |

## 0xE2 — Config Table: Get Item Value

Payload decoder: `flyc_config_table_get_item_value_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_value_table_no` (Table No) | int16 |  |
  | 2 | 2 | `flyc_config_table_get_item_value_unknown1` (Unknown1) | int16 |  |
  | 4 | 2 | `flyc_config_table_get_item_value_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_value_status` (Status) | uint16 |  |
  | 2 | 2 | `flyc_config_table_get_item_value_unknown1` (Unknown1) | int16 |  |

  *if (payload:len() >= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 4 | 2 | `flyc_config_table_get_item_value_index` (Param Index) | int16 |  |

  *if (payload:len() - offset >= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 6 | ? | `flyc_config_table_get_item_value_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

## 0xE3 — Config Table: Set Item Value

Payload decoder: `flyc_config_table_set_item_value_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_set_item_value_table_no` (Table No) | int16 |  |
  | 2 | 2 | `flyc_config_table_set_item_value_unknown1` (Unknown1) | int16 |  |
  | 4 | 2 | `flyc_config_table_set_item_value_index` (Param Index) | int16 |  |

  *if (payload:len() - offset >= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 6 | ? | `flyc_config_table_set_item_value_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

## 0xE4 — Config Table: Reset Def. Item Value

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xE5 — Push Config Table: Get Tbl Attribute

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xE6 — Push Config Table: Get Item Attribute

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xE7 — Push Config Table: Set Item Param

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xE8 — Push Config Table: Clear

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xE9 — Config Command Table: Get or Exec

Payload decoder: `flyc_config_command_table_get_or_exec_dissector`

## 0xEA — Register Open Motor Error Action

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xEB — Logout Open Motor Error Action

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xEC — Set Open Motor Error Action Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xED — ESC Echo Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xEE — GoHome CountDown Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF0 — Config Table: Get Param Info by Index

Payload decoder: `flyc_config_table_get_param_info_by_index_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_param_info_by_index_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_get_param_info_by_index_status` (Status) | uint8 |  |

  *if (payload:len() >= 8) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 2 | `flyc_config_table_get_param_info_by_index_type_id` (TypeID) | uint16 |  |
  | 3 | 2 | `flyc_config_table_get_param_info_by_index_size` (Size) | int16 |  |
  | 5 | 2 | `flyc_config_table_get_param_info_by_index_attribute` (Attribute) | uint16 |  |

  *if (type_id <= 3) or (type_id == 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_index_limit_u_min` (LimitU minValue) | uint32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_index_limit_u_max` (LimitU maxValue) | uint32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_index_limit_u_def` (LimitU defaultValue) | uint32 |  |

  *elseif (type_id >= 4) and (type_id <= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_index_limit_i_min` (LimitI minValue) | int32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_index_limit_i_max` (LimitI maxValue) | int32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_index_limit_i_def` (LimitI defaultValue) | int32 |  |

  *elseif (type_id == 8) or (type_id == 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_index_limit_f_min` (LimitF minValue) | float |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_index_limit_f_max` (LimitF maxValue) | float |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_index_limit_f_def` (LimitF defaultValue) | float |  |

## 0xF1 — Config Table: Read Params By Index

Payload decoder: `flyc_config_table_read_param_by_index_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_read_param_by_index_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_read_param_by_index_index` (Param Index) | int16 |  |

## 0xF2 — Config Table: Write Params By Index

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF3 — Config Table: Reset Default Param Val

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF4 — Config Table: Set Item By Index

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF5 — Ver Phone Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF6 — Push Param PC Log

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF7 — Config Table: Get Param Info By Hash

Payload decoder: `flyc_config_table_get_param_info_by_hash_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_config_table_get_param_info_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_get_param_info_by_hash_status` (Status) | uint8 |  |

  *if (payload:len() >= 8) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 2 | `flyc_config_table_get_param_info_by_hash_type_id` (TypeID) | uint16 |  |
  | 3 | 2 | `flyc_config_table_get_param_info_by_hash_size` (Size) | int16 |  |
  | 5 | 2 | `flyc_config_table_get_param_info_by_hash_attribute` (Attribute) | uint16 |  |

  *if (type_id <= 3) or (type_id == 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_hash_limit_u_min` (LimitU minValue) | uint32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_hash_limit_u_max` (LimitU maxValue) | uint32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_hash_limit_u_def` (LimitU defaultValue) | uint32 |  |

  *elseif (type_id >= 4) and (type_id <= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_hash_limit_i_min` (LimitI minValue) | int32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_hash_limit_i_max` (LimitI maxValue) | int32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_hash_limit_i_def` (LimitI defaultValue) | int32 |  |

  *elseif (type_id == 8) or (type_id == 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_hash_limit_f_min` (LimitF minValue) | float |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_hash_limit_f_max` (LimitF maxValue) | float |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_hash_limit_f_def` (LimitF defaultValue) | float |  |

## 0xF8 — Config Table: Read Param By Hash

Payload decoder: `flyc_config_table_read_param_by_hash_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | ? | `flyc_config_table_read_param_by_hash_rq_num` (Request Number) | uint8 | // Add request number detached, without related byte within packet (it is just index of the value) |
  | 0 | 4 | `flyc_config_table_read_param_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |

## 0xF9 — Config Table: Write Param By Hash

Payload decoder: `flyc_config_table_write_param_by_hash_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_config_table_write_param_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |
  | 4 | ? | `flyc_config_table_write_param_by_hash_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_write_param_by_hash_status` (Status) | uint8 |  |

  *if (payload:len() - offset >= 5) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 4 | `flyc_config_table_write_param_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |
  | 5 | ? | `flyc_config_table_write_param_by_hash_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

## 0xFA — Config Table: Reset Params By Hash

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFB — Config Table: Read Params By Hash

Payload decoder: `flyc_config_table_read_params_by_hash_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_read_params_by_hash_unknown00` (Unknown00) | uint8 |  |
  | 1 | 4 | `flyc_config_table_read_params_by_hash_first_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |

## 0xFC — Config Table: Write Params By Hash

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFD — Product Type Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFE — Motor Force Disable Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFF — Motor Force Disable Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

---

## Appendix: newer (2015/2017-era) parameter-table protocol structs
(from `comm_mkdupc.py`; these are the generic flight-parameter read/write
commands used by DJI Assistant 2 / the SDK to enumerate and tune hundreds of
named flight-controller parameters — "FlyC Param" style. All offsets
relative to the start of the DUML payload.)

### 0xDF — Assistant Unlock
**Request** (`DJIPayload_FlyController_AssistantUnlockRq`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 4 | lock_state | uint32 |

**Response** (`DJIPayload_FlyController_AssistantUnlockRe`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | status | uint8 |

### 0xE0 — Get Table Attribute (2017 protocol)
**Request**: `table_no` (uint16, off 0).
**Response**: `status`(u16,0) `table_no`(u16,2) `entries_crc`(u32,4) `entries_num`(u32,8)
— or the shorter EOL form: `status`(u16,0) only.

### 0xE1 — Get Param Info By Index (2017 protocol)
**Request**: `table_no`(u16,0) `param_index`(u16,2).
**Response** (`U`=unsigned/`I`=signed/`F`=float variants, selected by `type_id`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 2 | status | uint16 |
| 2 | 2 | table_no | uint16 |
| 4 | 2 | param_index | uint16 |
| 6 | 2 | type_id | uint16 (see DJIPayload_FlyController_ParamType below) |
| 8 | 2 | size | uint16 |
| 10 | 4 | limit_def | uint32 / int32 / float |
| 14 | 4 | limit_min | uint32 / int32 / float |
| 18 | 4 | limit_max | uint32 / int32 / float |
| 22 | 160 | name | char[160] |
EOL short form: `status`(u16,0) only.

`DJIPayload_FlyController_ParamType` enum (`type_id` field above):
`0x0`=ubyte `0x1`=ushort `0x2`=ulong `0x3`=ulonglong `0x4`=byte(i8)
`0x5`=short(i16) `0x6`=long(i32) `0x7`=longlong(i64) `0x8`=float `0x9`=double
`0xA`=array `0xB`=bool. Values 0x4-0x7 are signed → response decodes with the
`I` struct variant (`limit_*` as signed int); 0x8/0x9 → `F` variant (float).

### 0xE2 — Read Param Value By Index (2017 protocol)
**Request**: `table_no`(u16,0) `unknown1`(u16,2) `param_index`(u16,4).
**Response**: `status`(u16,0) `unknown1`(u16,2) `param_index`(u16,4)
`param_value`(u8[160],6) — actual value occupies the first `size` bytes per
the param's type_id, rest is padding to the fixed 160-byte max.

### 0xE3 — Write Param Value By Index (2017 protocol)
**Request**, size varies by value width — `table_no`(u16,0) `unknown1`(u16,2)
`param_index`(u16,4) `param_value`(u8/u16/u32/u64/u8[16]/u8[160] at off 6,
width selected by how many bytes the caller sends: 1/2/4/8/16/≤160).
**Response**: `status`(u16,0) `table_no`(u16,2) `param_index`(u16,4)
`param_value`(u8[160],6).

### 0xF0 — Get Param Info By Index (2015 protocol, legacy — superseded by 0xE1)
**Request** (`DJIPayload_FlyController_GetParamInfoByIndex2015Rq`): `param_index`(u16,0).
**Response** (`U`/`I`/`F` variants by `type_id`, same enum as above):
| Off | Size | Field |
|---|---|---|
| 0 | 1 | status (uint8, not uint16 — legacy protocol) |
| 1 | 2 | type_id |
| 3 | 2 | size |
| 5 | 2 | attribute |
| 7 | 4 | limit_min |
| 11 | 4 | limit_max |
| 15 | 4 | limit_def |
| 19 | 160 | name |
EOL short form: `status`(u8,0) only. (cmd_id 0xF7 shares this same response shape.)

### 0xF8 — Read Param Value By Hash (2015 protocol — params addressed by name-hash, not index)
**Request** (`DJIPayload_FlyController_ReadParamValByHash2015Rq`): `param_hash`(u32,0).
**Response**: `status`(u8,0) `param_hash`(u32,1) `param_value`(u8[160],5).

Parameter name → hash function (`flyc_parameter_compute_hash` in
`comm_mkdupc.py`), confirmed matching DJI Assistant 2 behavior:
```python
def flyc_parameter_compute_hash(parname):
    parhash = 0
    parbt = parname.encode('gbk')
    for ncode in parbt:
        parhash = ((parhash & 0xffffffff) << 8) + ncode
        parhash %= 0xfffffffb   # note: NOT 0xffffffff - a prime-ish modulus just below 2^32
    return parhash
```

### 0xF9 — Write Param Value By Hash (2015 protocol)
**Request**: `param_hash`(u32,0) `param_value`(variable width 1/2/4/8/16/≤160, off 4).
**Response**: `status`(u8,0) `param_hash`(u32,1) `param_value`(u8[160],5).

These hash/index parameter-table commands are how DJI Assistant 2 and the
mobile SDK enumerate and tune the hundreds of named flight parameters (PID
gains, limits, feature toggles, etc.) without a fixed per-parameter `cmd_id`
— the parameter *name* (hashed) or a *table index* (looked up via 0xE0/0xE1)
is the real addressing scheme, layered on top of a handful of generic DUML
commands.
