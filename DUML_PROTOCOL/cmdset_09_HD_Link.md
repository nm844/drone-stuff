# Cmd Set 0x09 — HD Link

Total known command IDs: 67

## 0x01 — HDLnk OSD General Data Get/Push

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

## 0x02 — HDLnk OSD Home Point Get/Push

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

## 0x03 — HDLnk Baseband State Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — HDLnk FPGA Write

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — HDLnk FPGA Read

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — HDLnk TCX Hardware Reg Write

Payload decoder: `hd_link_write_hardware_reg_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `hd_link_hardware_reg_addr` (Register addr) | uint16 | Address within AD9363 |
  | 2 | 1 | `hd_link_hardware_reg_val` (Register value) | uint8 | Value of the hardware register |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_opertation_status_byte` (Operation status) | uint8 | Returned error code of the operation; 0 means success |

## 0x07 — HDLnk TCX Hardware Reg Read

Payload decoder: `hd_link_read_hardware_reg_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `hd_link_hardware_reg_addr` (Register addr) | uint16 | Address within AD9363 |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_hardware_reg_val` (Register value) | uint8 | Value of the hardware register |

## 0x08 — HDLnk VT Signal Quality Push

Payload decoder: `hd_link_push_vt_signal_quality_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_push_vt_signal_quality_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `hd_link_push_vt_signal_quality_up_signal_quality` (Up Signal Quality) | uint8 | mask:`0x7f` |

## 0x09 — HDLnk Sweep Frequency Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0A — HDLnk Sweep Frequency Get/Push

Payload decoder: `hd_link_push_freq_energy_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 32 | `hd_link_push_freq_energy_unknown0` (Unknown0) | bytes |  |

## 0x0B — HDLnk Device Status Get/Push

Payload decoder: `hd_link_push_device_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_push_device_status_unknown0` (Unknown0) | uint8 |  |
  | 1 | 4 | `hd_link_push_device_status_unknown1` (Unknown1) | uint32 |  |

## 0x0C — HDLnk VT Config Info Get/Push

Payload decoder: `hd_link_get_vt_config_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_get_vt_config_info_channel` (Channel) | uint8 |  |
  | 1 | 1 | `hd_link_get_vt_config_info_unknown01` (Unknown01) | uint8 |  |
  | 2 | 1 | `hd_link_get_vt_config_info_get_is_auto` (Get Is Auto) | uint8 |  |
  | 3 | 1 | `hd_link_get_vt_config_info_get_is_master` (Get Is Master) | uint8 |  |
  | 4 | 5 | `hd_link_get_vt_config_info_unknown04` (Unknown04) | bytes |  |
  | 9 | 1 | `hd_link_get_vt_config_info_mcs` (Mcs) | uint8 |  |
  | 10 | 1 | `hd_link_get_vt_config_info_single_or_double` (Single Or Double) | uint8 |  |
  | 11 | 1 | `hd_link_get_vt_config_info_band_width_percent` (Band Width Percent) | uint8 |  |
  | 12 | 3 | `hd_link_get_vt_config_info_unknown0c` (Unknown0C) | bytes |  |
  | 15 | 1 | `hd_link_get_vt_config_info_working_freq` (Working Freq) | uint8 |  |

## 0x0D — HDLnk VT Config Info Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0E — HDLnk USB Iface Change

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0F — HDLnk Reset Cy68013

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x10 — HDLnk Upgrade Tip Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x11 — HDLnk Wl Env Quality Get/Push

Payload decoder: `hd_link_push_wl_env_quality_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_push_wl_env_quality_channel_status` (Channel Status) | uint8 | enum:`enums.HD_LINK_WL_ENV_QUALITY_CHANNEL_STATUS_ENUM` |

## 0x12 — HDLnk Factory Test Set

Payload decoder: `hd_link_set_factory_test_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_set_factory_test_flag_20001A28_D_E` (flag 20001A28 D and E) | uint8 |  |
  | 1 | 1 | `hd_link_set_factory_test_flag_20001A28_A_B` (flag 20001A28 A and B) | uint8 |  |
  | 2 | 1 | `hd_link_set_factory_test_attenuation` (Tcx Attenuation) | uint8 | dB; attenuation set to REG_TXn_ATTEN_0 register of AD9363 |
  | 3 | 1 | `hd_link_set_factory_test_flag_20001A28_C` (flag 20001A28 C) | uint8 |  |

## 0x13 — HDLnk Factory Test Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x14 — HDLnk Max Video Bandwidth Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x15 — HDLnk Max Video Bandwidth Get/Push

Payload decoder: `hd_link_push_max_video_bandwidth_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_push_max_video_bandwidth_max_mcs` (Max Mcs) | uint8 |  |

## 0x16 — HDLnk Debug Info Push

Payload decoder: `hd_link_push_debug_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_push_debug_info_type` (Type) | uint8 | TODO values from enum P3.DataOsdGetPushDebugInfo |

## 0x20 — HDLnk SDR Downward Sweep Frequency

Payload decoder: `hd_link_push_sdr_dl_freq_energy_dissector`

## 0x21 — HDLnk SDR Vt Config Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — HDLnk SDR Dl Auto Vt Info Get/Push

Payload decoder: `hd_link_push_sdr_dl_auto_vt_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `hd_link_push_sdr_dl_auto_vt_info_nf` (NF) | uint16 |  |
  | 2 | 1 | `hd_link_push_sdr_dl_auto_vt_info_band` (Band) | uint8 |  |
  | 3 | 1 | `hd_link_push_sdr_dl_auto_vt_info_unknown3` (Unknown3) | uint8 |  |
  | 4 | 4 | `hd_link_push_sdr_dl_auto_vt_info_auto_mcs` (Auto Mcs) | float |  |
  | 8 | 1 | `hd_link_push_sdr_dl_auto_vt_info_mcs_type` (Mcs Type) | uint8 |  |

## 0x23 — HDLnk SDR Rt Status Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x24 — HDLnk SDR UAV Rt Status Get/Push

Payload decoder: `hd_link_push_sdr_rt_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `hd_link_push_sdr_rt_status_name` (Name) | string |  |
  | 8 | 4 | `hd_link_push_sdr_rt_status_value` (Value) | float |  |

## 0x25 — HDLnk SDR Gnd Rt Status Get/Push

Payload decoder: `hd_link_push_sdr_rt_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `hd_link_push_sdr_rt_status_name` (Name) | string |  |
  | 8 | 4 | `hd_link_push_sdr_rt_status_value` (Value) | float |  |

## 0x26 — HDLnk SDR Debug/Assitant Read

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x27 — HDLnk SDR Debug/Assitant Write

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x28 — HDLnk SDR Start Log Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x29 — HDLnk SDR Upward Sweep Frequency

Payload decoder: `hd_link_push_sdr_ul_freq_energy_dissector`

## 0x2A — HDLnk SDR Upward Select Channel

Payload decoder: `hd_link_push_sdr_ul_auto_vt_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `hd_link_push_sdr_ul_auto_vt_info_channel_type` (Select Channel Type) | float |  |
  | 4 | 4 | `hd_link_push_sdr_ul_auto_vt_info_get_select_channel_count` (Get Select Channel Count) | uint32 |  |

## 0x2B — HDLnk SDR Revert Role

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2C — HDLnk SDR Amt Process

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2D — HDLnk SDR LBT Status Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2E — HDLnk SDR LBT Status Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2F — HDLnk SDR Link Test

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x30 — HDLnk SDR Wireless Env State

Payload decoder: `hd_link_sdr_wireless_env_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `hd_link_sdr_wireless_env_event_code` (Event Code) | uint16 | enum:`enums.HD_LINK_SDR_WIRELESS_ENV_EVENT_CODE_SDR_WIRELESS_STATE_ENUM` |

## 0x31 — HDLnk SDR Scan Freq Cfg

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x32 — HDLnk SDR Factory Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x33 — HDLnk Tracking State Ind

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x34 — HDLnk SDR Liveview Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x35 — HDLnk SDR Liveview Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x36 — HDLnk SDR Liveview Rate Ind

Payload decoder: `hd_link_sdr_liveview_rate_ind_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `hd_link_sdr_liveview_rate_ind_code_rate` (Code Rate) | float |  |

## 0x37 — HDLnk Abnormal Event Ind

Payload decoder: `hd_link_abnormal_event_ind_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_abnormal_event_ind_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `hd_link_abnormal_event_ind_post` (Post) | uint8 | mask:`0x01` |

## 0x38 — HDLnk SDR Set Rate

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x39 — HDLnk Liveview Config Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3A — HDLnk Dl Freq Energy Push

Payload decoder: `hd_link_push_dl_freq_energy_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_push_dl_freq_energy_1_km_offset` (1 Km Offset) | uint8 | value bias  - 256 |
  | 1 | 1 | `hd_link_push_dl_freq_energy_path_loss_offset` (Path Loss Offset) | uint8 |  |
  | 2 | 1 | `hd_link_push_dl_freq_energy_rc_link_offset` (Rc Link Offset) | uint8 |  |
  | 3 | 1 | `hd_link_push_dl_freq_energy_tx_power_offset` (Tx Power Offset) | uint8 |  |
  | 4 | 1 | `hd_link_push_dl_freq_energy_dis_loss_ind` (Dis Loss Ind) | uint8 | enum:`enums.HD_LINK_PUSH_DL_FREQ_ENERGY_DIS_LOSS_EVENT_ENUM` |
  | 5 | 1 | `hd_link_push_dl_freq_energy_sig_bar_ind` (Sig Bar Ind) | uint8 |  |
  | 6 | 1 | `hd_link_push_dl_freq_energy_dl_pwr_accu` (Dl Pwr Accu) | uint8 |  |
  | 7 | 2 | `hd_link_push_dl_freq_energy_max_nf20_m` (Max Nf20 M) | uint16 |  |
  | 9 | 2 | `hd_link_push_dl_freq_energy_min_nf20_m` (Min Nf20 M) | uint16 |  |
  | 11 | 2 | `hd_link_push_dl_freq_energy_max_nf10_m` (Max Nf10 M) | uint16 |  |
  | 13 | 2 | `hd_link_push_dl_freq_energy_min_nf10_m` (Min Nf10 M) | uint16 |  |

## 0x3B — HDLnk SDR Tip Interference

Payload decoder: `hd_link_sdr_tip_interference_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_sdr_tip_interference_be_interfered` (Be Interfered) | uint8 |  |

## 0x3C — HDLnk SDR Upgrade Rf Power

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3E — HDLnk Slave RT Status Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3F — HDLnk RC Conn Status Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x41 — HDLnk Racing Set Modem Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x42 — HDLnk Racing Get Modem Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x50 — HDLnk LED Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x51 — HDLnk Power Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x52 — HDLnk Power Status Get/Push

Payload decoder: `hd_link_power_status_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_power_status_info_power_status` (Power Status) | uint8 |  |
  | 1 | 1 | `hd_link_power_status_info_get_is_power_off` (Get Is Power Off) | uint8 |  |

## 0x53 — HDLnk SDR Cp Status Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x54 — Osmo Calibration Push

Payload decoder: `hd_link_osmo_calibration_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_osmo_calibration_a` (A) | uint8 |  |
  | 1 | 1 | `hd_link_osmo_calibration_b` (B) | uint8 |  |

## 0x57 — HDLnk Mic Gain Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x58 — HDLnk Mic Gain Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x59 — HDLnk Mic Info Get/Push

Payload decoder: `hd_link_mic_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_mic_info_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `hd_link_mic_info_mic_type` (Mic Type) | uint8 | enum:`enums.HD_LINK_OSD_MIC_INFO_MIC_TYPE_ENUM`; mask:`0x01` |
  | 0 | 1 | `hd_link_mic_info_mic_volume` (Mic Volume) | uint8 | mask:`0xfe` |

## 0x62 — HDLnk Mic Enable Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x63 — HDLnk Mic Enable Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x71 — HDLnk Main Camera Bandwidth Percent Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x72 — HDLnk Main Camera Bandwidth Percent Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
