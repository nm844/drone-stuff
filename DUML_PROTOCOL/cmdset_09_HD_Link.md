# Cmd Set 0x09 — HD Link

Total known command IDs: 69

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

_Not decoded._ No Linux-userspace handler found. Checked all binaries importing duss_event_register_dynamic_command (dji_sdrs_agent, test_rtos_raw, dji_sys ARM32+AArch64) for a literal cmd_set=0x09 registration -- none exists (the only literal sites found anywhere were cmd_set 0x22/id 0x60 x3, cmd_set 0x00/id 0xa3 x2, cmd_set 0x06/id 0x3a x2, cmd_set 0x04/id 0x69 x1). Grepped both firmware trees for 'baseband' -- the only hit in a DUML-relevant binary (bin/dji_sys) is the string 'baseband_1090' in an ADS-B 1090MHz-receiver status message, unrelated to the OcuSync radio baseband. ALL_COMMANDS.csv (this project's own import of the public dissector) tags this cmd_set's typical_receiver as 'HD-Link MCU (air)' for essentially every row, consistent with this command being handled entirely on the separate air-unit radio MCU, outside this Linux filesystem extraction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — HDLnk FPGA Write

_Not decoded._ No Linux-userspace handler found. Grepped both firmware trees for 'fpga' (case-insensitive): hits are bin/dji_perception, lib_test_cases.sh, test_mdev, test_dsp/test_dsp_e1e, lib/modules/vmipi_acc.ko, lib/modules/vision_acc.ko, lib/libOmxCore.so, lib/libLLVM.so, lib/libdsp_frwk.so, lib/libimss.so, lib/libduml_frwk.so -- all generic DSP/video-codec/GPU FPGA-acceleration references (camera/vision pipeline), none naming the OcuSync radio FPGA or carrying a cmd_set-0x09 registration. Same negative result as 0x03 for every known DUML-registration mechanism in this firmware. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x05 — HDLnk FPGA Read

_Not decoded._ Same disposition and same search as 0x04 (FPGA Write) -- no native Linux-side implementation found, 'fpga' string hits are all unrelated vision/DSP-pipeline code, no cmd_set=0x09 registration anywhere. Given 0x04/0x05 are almost certainly a matched write/read pair implemented identically to the already-decoded 0x06/0x07 'TCX Hardware Reg Write/Read' pair (register addr + value, per the public dissector's hd_link_write_hardware_reg_dissector/hd_link_read_hardware_reg_dissector), the most defensible inference is that they target a different chip (the radio-link FPGA rather than the AD9363 TCX) via the same request/response shape, but this is an architectural analogy, not a byte-level finding confirmed by disassembly of a real handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ No Linux-userspace handler found. The sibling PUSH/GET direction (0x0A 'HDLnk Sweep Frequency Get/Push') already has a public-dissector decode but only as 32 raw unparsed bytes (hd_link_push_freq_energy_dissector, field name 'unknown0') -- i.e. even the public community RE effort never resolved this family's byte layout. The SDR-era sweep commands in the same cmd_set (0x20 'SDR Downward Sweep Frequency', 0x29 'SDR Upward Sweep Frequency') are likewise undecoded by the public dissector and had no Linux-side owner found either during this pass. No binary in either firmware image registers cmd_set=0x09/cmd_id=0x09. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ No Linux-userspace handler found. The sibling GET/PUSH direction (0x0C 'HDLnk VT Config Info Get/Push') has a real public-dissector byte layout (16-byte struct: channel u8@0, unknown u8@1, is_auto u8@2, is_master u8@3, 5 unknown bytes@4, mcs u8@9, single_or_double u8@10, bandwidth_percent u8@11, 3 unknown bytes@12, working_freq u8@15), which is strong structural evidence for what the SET direction's request payload likely mirrors (a SET typically carries the same fields the GET/PUSH reports back), but this project found no native Linux handler for either 0x0C or 0x0D to confirm that inference against real code, and 'VT' commands throughout this cmd_set are consistently HD-Link-MCU-side per ALL_COMMANDS.csv. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0E — HDLnk USB Iface Change

_Not decoded._ Got further than most of this batch on a real lead that ultimately did not close: bin/dji_sys (e1e, ARM32) imports init_libusb and usbsocket_init from lib/libduml_hal.so, called from a function at vaddr 0x52114 that does nothing but log + init_libusb() + usbsocket_init() (a USB-socket bring-up, no DUML dispatch visible inside it). That function's identity was confirmed via a {flags, name_ptr, fn_ptr} thread-descriptor table found in dji_sys's own .data.rel.ro (entry at file/vaddr 0xa26b8): the name string at 0x79267 is literally 'sys_platform_zv900_init', one of three mutually-exclusive hardware-platform bring-up threads (siblings 'sys_platform_wm169_init' at 0xa269c/0x79233 and 'sys_platform_e1e_wm162_init' at 0xa26a8/0x7924b). 'zv900' is therefore the hardware-platform codename that uses a USB-attached Cy68013 bridge chip for the HD-Link radio. However, no register_dynamic_command call (literal or data-driven) was found anywhere near this code, so there is no confirmed link from DUML cmd_id 0x0e specifically to any USB-interface-switch logic in this thread or elsewhere -- it may simply never surface as a distinct Linux-visible command (the interface change could be entirely internal to the MCU/bridge firmware). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0F — HDLnk Reset Cy68013

_Not decoded._ Strongest circumstantial lead in this batch, still unconfirmed. lib/libduml_hal.so exports a real function literally named Reset_68013 (vaddr 0x23600/128 bytes) that is fully disassembled and semantically exact for this command's name: duss_log_gen_head/print('reset 68013'), sleep(2), then two system() calls with the literal shell commands 'devgpio -n 60 -w 0' then 'devgpio -n 60 -w 1' -- i.e. a GPIO-60 reset pulse (drive low, then high) to the Cy68013 (Cypress EZ-USB FX2) chip. It takes no arguments (pure trigger, consistent with this command needing no payload). However, exhaustive search (every direct branch target in the whole libduml_hal.so disassembly, plus a raw 4-byte-aligned byte scan of the entire file for both the Thumb-bit-set and plain forms of its address) found zero callers anywhere in the file, and no external binary in either firmware image imports Reset_68013 via dynamic relocation (checked across every file in both trees). So the function exists and is semantically on-point, but its link to the DUML cmd_set=0x09/cmd_id=0x0f dispatch path could not be statically confirmed -- it may be reached only via a runtime-populated dispatch table (as seen elsewhere in this cmd_set's investigation) or may be dead/vestigial code. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x10 — HDLnk Upgrade Tip Set

_Not decoded._ No Linux-userspace handler found. Checked the firmware-upgrade orchestration chain this project already catalogued (12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md Sec.7 dji_upgrade; 20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md's A/B-OTA tracks): dji_upgrade is a JSON-config-driven orchestrator (/system/etc/upgrade.json, fallback dji.json) that dlopen()s product-specific plugins and drives a fixed register_init/.../post_init sequence -- a config/orchestration client, not a DUML command registrar (consistent with doc12's own characterization). No register_dynamic_command site for cmd_set 0x09 exists in dji_upgrade or any libupgrade_*.so (none of those import duss_event_register_dynamic_command at all). The name plausibly means 'tell the HD-Link MCU an upgrade is about to happen, show a UI tip/LED pattern' rather than carrying actual firmware bytes, but no Linux-side code implementing that was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ No Linux-userspace handler found. The sibling SET direction (0x12 'HDLnk Factory Test Set') has a real public-dissector 4-byte layout naming an AD9363 TX-attenuation register plus 3 flag bytes, strongly implying this chip (AD9363, a Linux-invisible radio IC on the HD-Link board) is configured only from the MCU side. Searched both firmware trees for 'AD9363'/'atten' (case-insensitive): the only non-trivial hit, lib/libfactory_cali.so, is a false positive -- the matched substring 'atten' is inside an unrelated C++-mangled symbol ('...FlattenMembershipMap...'), and libfactory_cali.so is not linked by any binary in bin/ at all. No evidence of a Linux-side factory-test GET handler exists for this or the sibling SET command. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x14 — HDLnk Max Video Bandwidth Set

_Not decoded._ No Linux-userspace handler found. The sibling GET/PUSH direction (0x15 'HDLnk Max Video Bandwidth Get/Push') has a public-dissector 1-byte layout (max_mcs u8@0), which is a plausible template for this SET command's request payload (a single MCS-index byte), but no native handler was found for either direction in this firmware to confirm it. No binary registers cmd_set=0x09/cmd_id=0x14 via any known mechanism. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ The already-decoded, non-SDR sibling 0x0C 'VT Config Info Get/Push' (hd_link_get_vt_config_info_dissector, a 16-byte struct: channel/is_auto/is_master/mcs/single_or_double/band_width_percent/working_freq) is a strong structural precedent for what 0x21's reply likely looks like, since 'SDR Vt Config Info Get' reads as the SDR-specific analogue of the already-documented non-SDR 0x0C. But no code in dji_sdrs_agent (or dji_sys, whose 11 literal registrations never touch cmd_set 0x09) implements or even references VT-config-like fields, and the same 'no separate SDR module firmware in this package' architectural gap applies here as for 0x20/0x29. Reusing 0x0C's layout for 0x21 without any firmware-side confirmation would be inventing a layout, not deriving one -- declined per the task's instructions. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Explicitly refuted lead, reported with the same rigor as a 'refuted' finding rather than left as a misleadingly-plausible one: the one function that looks exactly like a 'set a named status by name' handler is real and disassembled, but its only confirmed callers are unrelated local config-driven channel setup, not cmd_set 0x09 dispatch. No other candidate code, and no literal cmp against 0x23 in a dispatch-like context, was found anywhere in dji_sdrs_agent or dji_sys. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ The single strongest lead found in this whole investigation (concrete named function, concrete byte-level field semantics, strong name/behavior match), but the cmd_id/cmd_set binding -- and even basic reachability -- could not be confirmed on either architecture after an unusually thorough search. Per the task's instructions this is reported as insufficient_evidence with full detail rather than asserted as decoded. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x27 — HDLnk SDR Debug/Assitant Write

_Not decoded._ Paired with 0x26: the read and write operations are two branches of the exact same function, gated on one mode byte, so whatever uncertainty applies to the cmd_id binding for 0x26 applies identically here. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x28 — HDLnk SDR Start Log Set

_Not decoded._ 'Start Log Set' most plausibly triggers logging on the physically separate SDR module itself (the module whose log bytes dji_sdrs_agent's sdrs_log subsystem subsequently captures over USB/UART), rather than being a DUML command this daemon parses and acts on directly -- consistent with the same 'generic relay, no per-cmd-id branching' pattern found for sa_relay*.c, and with the absence of any separate SDR-module firmware image anywhere in this firmware package. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x29 — HDLnk SDR Upward Sweep Frequency

Payload decoder: `hd_link_push_sdr_ul_freq_energy_dissector`

## 0x2A — HDLnk SDR Upward Select Channel

Payload decoder: `hd_link_push_sdr_ul_auto_vt_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `hd_link_push_sdr_ul_auto_vt_info_channel_type` (Select Channel Type) | float |  |
  | 4 | 4 | `hd_link_push_sdr_ul_auto_vt_info_get_select_channel_count` (Get Select Channel Count) | uint32 |  |

## 0x2B — HDLnk SDR Revert Role

_Not decoded._ 'Role' strongly suggests the OcuSync/HD-Link master-slave link-role model. This project's own prior work (12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md §6) documents `dji_wlm` as the daemon with an explicit Master/Slave role model, and a later pass (21_PAYLOAD_DECODE_SWEEP_FINDINGS.md) already flagged two cmd_set-0x06 commands ('Quiry Role'/'Quiry Ms Link Status') as plausibly dji_wlm-owned but unresolved due to ARM32/Thumb2 tooling limits. 'Revert Role' (cmd_set 0x09) looks like a sibling of that same family, but on the SDR/HD-Link side rather than dji_wlm specifically -- dji_wlm itself was not re-disassembled in this pass (out of this batch's primary candidate, dji_sdrs_agent, which shows no trace of it). This is a concrete lead for a future pass with a dedicated dji_wlm deep-dive, not a resolved finding here. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2C — HDLnk SDR Amt Process

_Not decoded._ 'Amt' plausibly refers to the same AMT (Activation Management Tool) subsystem this project's own doc 18 (18_ACTIVATION_TA_FINDINGS.md) already maps in detail via libamt_util.so and the e91c9402 TEE TA, which that doc independently notes is reached on the DUML bus under the route name/tag 'amt_service'/'AMT'. 'Amt Process' may be a trigger for an AMT-side processing/challenge step distinct from the NVRAM read/write pair (0x26/0x27), but dji_sdrs_agent's own sa_event_amt_nvram_rw has no confirmed caller (see 0x26/0x27), and libamt_util.so itself was not re-disassembled in this pass -- it is the clear next candidate for a future pass given doc 18's existing deep-dive into its activation/secure-debug command-ID table. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2D — HDLnk SDR LBT Status Get

_Not decoded._ LBT (Listen-Before-Talk) is a radio-regulatory channel-occupancy-sensing feature intrinsic to the SDR/OcuSync PHY itself, reinforcing the same 'implemented on physically separate radio hardware, relayed opaquely by dji_sdrs_agent' conclusion documented for the sweep-frequency commands (0x20/0x29) and the firmware-package-level finding that no separate SDR/baseband module image exists anywhere in this download. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2E — HDLnk SDR LBT Status Set

_Not decoded._ LBT = "Listen Before Talk", a regulatory transmit-gating requirement in several ISM-band jurisdictions (EU/Japan 5.8GHz rules in particular) that DJI's own public dissector metadata already names this cmd_id's Get counterpart (0x2d) for. 0x2e is almost certainly the paired Set: enabling/disabling (or configuring parameters of) LBT compliance mode on the OcuSync/SDR radio. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2F — HDLnk SDR Link Test

_Not decoded._ Likely a diagnostic trigger that runs a radio link self-test on the SDR module (possibly minimal/trigger-only payload, e.g. a single start/stop byte), analogous to other 'Factory Test'/'Link Test' style commands elsewhere in this cmd_set (0x12/0x13). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x30 — HDLnk SDR Wireless Env State

Payload decoder: `hd_link_sdr_wireless_env_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `hd_link_sdr_wireless_env_event_code` (Event Code) | uint16 | enum:`enums.HD_LINK_SDR_WIRELESS_ENV_EVENT_CODE_SDR_WIRELESS_STATE_ENUM` |

## 0x31 — HDLnk SDR Scan Freq Cfg

_Not decoded._ Likely configures parameters (range/step/dwell) for the SDR's automatic frequency-scanning behavior, complementing the already-documented 0x20/0x29 sweep-frequency push commands and the 0x2A channel-selection command in this same cmd_set. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x32 — HDLnk SDR Factory Mode Set

_Not decoded._ Likely enables/disables a factory or engineering test mode on the SDR radio module, conceptually adjacent to the already-documented 0x12/0x13 'Factory Test' Set/Get pair. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x33 — HDLnk Tracking State Ind

_Not decoded._ An 'Ind' (indication/push) rather than a Set/Get -- given its position between SDR Factory Mode Set (0x32) and SDR Liveview Mode Set/Get (0x34/0x35), and the fact every neighboring cmd_id in this stretch is an SDR-radio-internal control, this is most plausibly a push of the SDR link's own tracking/lock state (frequency or timing-lock acquired/lost on the demodulator), not a visual subject-tracking indicator from an unrelated vision subsystem -- though this is an inference from naming and position only, not confirmed by any disassembled handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x34 — HDLnk SDR Liveview Mode Set

_Not decoded._ Sets the liveview (video) transmission mode over the SDR/OcuSync link (e.g. single- vs dual-channel transport, or a bandwidth-tier selector), paired with the Get at 0x35. This is the one cmd_id in the batch where the task hint's suspicion of a separate video-pipeline-daemon owner (by analogy with 0xa9/0xaa) seemed most plausible, so I specifically traced that possibility. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x35 — HDLnk SDR Liveview Mode Get

_Not decoded._ The Get counterpart of 0x34 (HDLnk SDR Liveview Mode Set) -- queries the SDR link's current liveview transmission mode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Likely sets a transmission rate / modulation-coding-scheme parameter for the SDR link, conceptually adjacent to the already-documented 0x36 'SDR Liveview Rate Ind' push (a float code-rate value) in this same cmd_set -- this Set is plausibly the command that drives that indication. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x39 — HDLnk Liveview Config Set

_Not decoded._ A broader liveview configuration command than 0x34's 'Mode' Set -- plausibly bundles multiple related fields (e.g. resolution/bitrate/channel-count) into one packed struct. Checked for a video-pipeline-daemon owner given the name, same as 0x34/0x35. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Plausibly tied to firmware-upgrade-time RF power control of the SDR module (e.g. forcing the radio to a safe/low-power RF state while the HD-Link MCU's own firmware is being reflashed) -- this would connect naturally to the USB-hotplug-triggered brload/fastboot flashing path dji_sdrs_agent's sa_bootctrl module already implements (doc 12 Sec.5), though no direct call-site link between that flashing logic and this specific cmd_id was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3E — HDLnk Slave RT Status Push

_Not decoded._ Searched for a direct literal-immediate registration (cmd_set=9 + cmd_id=0x3e) across every binary in both firmware trees that imports any duss_event_register_dynamic_command* variant (dji_sys e1e/e2, dji_sdrs_agent, test_rtos_raw, duml_googletest, libMipiHandshake.so, libWorkModeLiveview.so, libdcam_event_client_pool.so — confirmed to be the complete set via readelf -sW UND-symbol scan on both trees). None registers cmd_set=9 with this cmd_id via a literal immediate. The only remaining candidates are two confirmed-present but statically-unresolvable data-driven dispatch mechanisms inside dji_sdrs_agent and dji_sys (see shared_infrastructure_found) whose backing arrays could not be located despite brute-force branch-target scanning (validated against this project's own doc15 baseline for test_rtos_raw) and exhaustive literal-pointer scanning of every data section plus inline .text literal pools. dji_sdrs_agent exports a suggestively-named but unconfirmed candidate handler string, `sa_event_rt_control_by_name` (no direct cross-reference to a numeric cmd_id was found — the name match to "RT Status" is coincidental-strength only, not evidence). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3F — HDLnk RC Conn Status Push

_Not decoded._ Same exhaustive sweep as 0x3e (all 8 binaries importing the registration family checked; none has a literal cmd_set=9/cmd_id=0x3f call site). Also specifically checked dji_network (doc12 §4's 'Wi-Fi/SDR link-management daemon', the most plausible owner by name) for both the registration import and any 'rc_conn'/'conn_status' strings — it imports neither duss_event_register_dynamic_command nor duss_event_modify_dynamic_command at all, ruling it out as a direct DUML registrant for this or any new cmd_set-0x09 command (it must relay through a separate IPC path not examined here). dji_wlm was also checked and ruled out: it imports only duss_event_modify_dynamic_command, and its one confirmed literal call site overrides cmd_set 0x51/cmd_id 5 (already documented) — it registers nothing new. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x41 — HDLnk Racing Set Modem Info

_Not decoded._ No literal registration found in the exhaustive 8-binary sweep. Independent architectural evidence makes this plausibly a pass-through to a physically separate SDR/modem coprocessor rather than a locally-parsed command: the on-device QA script `/system_files/bin/modem_info.sh` (hardware/dji/service/sdrs_agent tree) issues real `dji_mb_ctrl -g 9 -t 0 -s 9 -c 0x55 <payload>` DUML frames — confirmed cmd_set=9 (the `-s` flag, per dji_mb_ctrl's own usage string `-s cmd_set`) with payload bytes selecting a modem sub-operation (0000=reverse, 0001=reboot, 0002=cps/status-query) — and dji_sdrs_agent's own export strings include `sa_relay_reset_pigeon`, `sa_relay_shutdown_pigeon`, `sa_hold_modem_reset`, confirming it manages a USB-attached 'pigeon' modem/SDR chip whose own firmware is not present under system_files. cmd_id 0x55 itself is not even in this project's known 69-command list for cmd_set 0x09 (a new finding, out of this batch's scope but corroborating context). This does not prove 0x41 specifically routes the same way, but it is the strongest available lead and was not resolvable further with static analysis of the binaries actually present. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x42 — HDLnk Racing Get Modem Info

_Not decoded._ Same search and same architectural reasoning as 0x41 (its paired Set/Get sibling). No literal registration found in the 8-binary sweep; no numeric cross-reference to 0x42 found in any string table, disassembly, or shell script on the filesystem. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x50 — HDLnk LED Set

_Not decoded._ No literal cmd_set=9/cmd_id=0x50 registration found in the 8-binary sweep. A tempting-looking lead turned out to be a false match and was explicitly ruled out: `/system_files/bin/fc_led_ctrl.sh` and string hits for `fc_led_set_type`/`net_fc_led_set_action_id` (in libupgrade_product.so, dji_sys, dji_network) all belong to a *different*, already-distinguishable LED mechanism — the Flight Controller's own status-LED registration/action API, which runs on cmd_set 0x03 (FC) with cmd_ids 0xBC (register)/0xBD (unregister)/0xBE (set action), confirmed directly from the script's own `FC_CMDSET=3` / `REGISTER_LED_CMDID=0xbc` / `SET_LED_CMDID=0xbe` constants. That family is unrelated to cmd_set 0x09's own, presumably OcuSync-air-unit-or-RC-side, LED indicator. No alternative handler for the real cmd_set-0x09 LED Set was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x51 — HDLnk Power Set

_Not decoded._ No literal cmd_set=9/cmd_id=0x51 registration found in the 8-binary sweep. Notably, this cmd_id's sibling Get/Push command, 0x52 'HDLnk Power Status Get/Push', already HAS a documented byte-level decode in cmdset_09_HD_Link.md (`hd_link_power_status_info_dissector`: offset0 u8 power_status, offset1 u8 get_is_power_off) sourced from the public Wireshark dissector — but that dissector has zero field data for 0x51 itself (name-only), and this pass's own binary search (registration-call-site scan across all 8 relevant binaries, plus the generic-loop/module-descriptor mechanisms in dji_sdrs_agent/dji_sys, both unresolved) could not independently recover 0x51's handler or payload layout either. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x52 — HDLnk Power Status Get/Push

Payload decoder: `hd_link_power_status_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_power_status_info_power_status` (Power Status) | uint8 |  |
  | 1 | 1 | `hd_link_power_status_info_get_is_power_off` (Get Is Power Off) | uint8 |  |

## 0x53 — HDLnk SDR Cp Status Get

_Not decoded._ No literal cmd_set=9/cmd_id=0x53 registration found in the 8-binary sweep. Strong architectural (but not numerically confirmed) evidence ties this family to dji_sdrs_agent's modem/'pigeon'-chip management role: the on-device QA script modem_info.sh's `cps` command (literally 'CP status', matching this cmd_id's name almost exactly) sends cmd_set=9/cmd_id=0x55 (NOT 0x53) with a 2-byte sub-opcode payload of 0x0002, and parses a 3-byte response: byte0=ret_code (hex, "00"=success), byte1=role (00=UAV,01=GND,02=GLASS), byte2=state (00=Idle,01=Pair,02=Connected,03=Loss,04=CPA7_ERR,05=DSP_ERR,06=AMT). cmd_id 0x55 is not itself in this project's known 69-entry command list for cmd_set 0x09, so it is evidently a distinct, closely-related sibling command (a generic multi-function 'modem control' op whose sub-function is chosen by payload) rather than 0x53 itself. Given the name 'Cp Status Get' (vs. 0x55's multi-purpose control-with-subop shape), 0x53 is plausibly a dedicated, payload-less or near-payload-less accessor that returns the same {role, state} shape directly — but this is architectural inference from a *sibling* command's live traffic, not a disassembly-confirmed decode of 0x53 itself, and is reported as such rather than as a found layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x54 — Osmo Calibration Push

Payload decoder: `hd_link_osmo_calibration_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_osmo_calibration_a` (A) | uint8 |  |
  | 1 | 1 | `hd_link_osmo_calibration_b` (B) | uint8 |  |

## 0x57 — HDLnk Mic Gain Set

_Not decoded._ No literal cmd_set=9/cmd_id=0x57 registration found in the 8-binary sweep. One lead was checked and found unconvincing: libdcam_audio_frwk.so (and its several linking consumers — stream-writer plugins, dji_pbt, dji_cht) contains a `main_mic_gain_ctl` struct field, but none of libdcam_audio_frwk.so's linking consumers is a DUML-bus registrant (none imports any duss_event_register_dynamic_command* symbol), and the naming/consumer set (camera stream writers, playback/camhal-test tools) points to the camera's own recording microphone, not the RC/air-unit intercom microphone cmd_set 0x09's 'HD Link' commands would plausibly cover — i.e. this is very likely a different 'mic' subsystem entirely, not confirmed as unrelated but not a positive match either. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x58 — HDLnk Mic Gain Get

_Not decoded._ Same search and same inconclusive libdcam_audio_frwk.so lead as its Set sibling (0x57). No literal cmd_set=9/cmd_id=0x58 registration found anywhere in the 8-binary sweep. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x59 — HDLnk Mic Info Get/Push

Payload decoder: `hd_link_mic_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hd_link_mic_info_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `hd_link_mic_info_mic_type` (Mic Type) | uint8 | enum:`enums.HD_LINK_OSD_MIC_INFO_MIC_TYPE_ENUM`; mask:`0x01` |
  | 0 | 1 | `hd_link_mic_info_mic_volume` (Mic Volume) | uint8 | mask:`0xfe` |

## 0x62 — HDLnk Mic Enable Get

_Not decoded._ No literal cmd_set=9/cmd_id=0x62 registration found in the 8-binary sweep. No distinct lead (beyond the same inconclusive libdcam_audio_frwk.so mic-gain struct noted for 0x57/0x58) was found specifically for the enable/disable toggle; its sibling 0x63 'HDLnk Mic Enable Set' and 0x59 'HDLnk Mic Info Get/Push' are both adjacent in the command space and 0x59 already has a real dissector-sourced decode (`hd_link_mic_info_dissector`: a single packed byte with a 1-bit mic_type field at mask 0x01 and a 7-bit mic_volume field at mask 0xfe) suggesting the whole 0x57-0x63 mic cluster is a coherent small family, but that existing decode covers 0x59 only, not 0x62, and this pass's binary search could not independently locate 0x62's own handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x63 — HDLnk Mic Enable Set

_Not decoded._ Presumably toggles the HD-Link audio/mic-passthrough channel on or off (sibling of the already-documented 0x09/0x62 'Mic Enable Get' and 0x09/0x59 'Mic Info Get/Push'), but no handler could be located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x71 — HDLnk Main Camera Bandwidth Percent Set

_Not decoded._ Presumably sets what percentage of the total OcuSync/HD-Link video bitrate budget is allocated to the main (vs. auxiliary/FPV) camera stream — a natural sibling of libwlm.so's libwlm_share_liveview_bandwidth(_v2) exports and dji_wlm's multi-link bandwidth-fusion role, but no concrete (cmd_set,cmd_id)-to-handler binding was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x72 — HDLnk Main Camera Bandwidth Percent Get

_Not decoded._ Presumably the paired Get for 0x71 (reads back the current main-camera bandwidth-percent allocation). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA9 — Liveview Pigeon State Heartbeat

_Not decoded._ A periodic push of SDR liveview resolution/rate parameters from the OcuSync 'Pigeon' video-link object into the receiving device's cached state, used to detect and react to a resolution/rate change. Handler correctly identified (_ZN3dji32_on_event_pigeon_state_heartbeatEP17duss_event_clientP10duss_eventPv (dji::_on_event_pigeon_state_heartbeat), registered at vaddr 0x8440 inside dji::LiveviewObjectPigeon::initEventCallback via duss_event_register_dynamic_command_with_user_data(client, cmd_set=9 [movs r1,#9], cmd_id=0xA9 [movs r2,#169], handler=&_on_event_pigeon_state_heartbeat, user_data). Re-confirmed independently of the prior pass's finding (same (cmd_set,cmd_id,handler) triple).), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

- **Handler:** `_ZN3dji32_on_event_pigeon_state_heartbeatEP17duss_event_clientP10duss_eventPv`
  (`dji::_on_event_pigeon_state_heartbeat`), registered by
  `dji::LiveviewObjectPigeon::initEventCallback`.
- **Purpose:** a periodic heartbeat/liveness or state-push for the
  live-view "pigeon" object (inferred from mangled C++ naming only). No
  matching teardown/cancel call was found for this pair in this library
  — `LiveviewObjectPigeon` has no exported deinit counterpart, which may
  simply mean cleanup happens elsewhere.
- **Evidence:** direct call to
  `duss_event_register_dynamic_command_with_user_data(client, cmd_set=0x09,
  cmd_id=0xA9, user_data)` at the registration call site inside
  `libWorkModeLiveview.so` (ARM32/E1E), inside
  `LiveviewObjectPigeon::initEventCallback`.
- **Confidence:** high on the `(cmd_set, cmd_id)` pair and registration
  mechanism; low on the exact semantic purpose (inferred from naming
  only, no payload/dispatch logic traced). See
  `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.

## 0xAA — HDLnk MIPI/HDVT Live-View Parameter Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _ZN3dji26hu_hdvt_set_liveview_paramEP17duss_event_clientP10duss_eventPv (dji::hu_hdvt_set_liveview_param), registered at vaddr 0x296c inside dji::MipiHsRecvV1::initEventClientCallback via duss_event_register_dynamic_command_with_user_data(client, cmd_set=9 [movs r1,#9], cmd_id=0xAA [movs r2,#170], handler=&hu_hdvt_set_liveview_param, user_data). Re-confirmed independently of the prior pass's finding (same (cmd_set,cmd_id,handler) triple, same registering function name).`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mipi_lv_param_reserved0` (Reserved/Header Byte) | uint8 | Copied into the validated buffer but never read by any instruction in this handler -- not used for any branch or forwarded field. Present purely because the wire format is a fixed 21-byte block. |
  | 1 | 2 | `mipi_lv_param_width` (Liveview Width) | uint16 | Must be nonzero or the handler rejects the request (duss_event_resp_err, code 0xE6). Forwarded (after validation) into the MipiConfig struct passed to MipiHsRecvBase::sendNewConfigCmdToQueue. |
  | 3 | 2 | `mipi_lv_param_height` (Liveview Height) | uint16 | Same nonzero validation and forwarding as width. |
  | 5 | 2 | `mipi_lv_param_dim3` (Third Dimension Parameter (unit not confirmed; candidate: frame rate or stride)) | uint16 | Validated nonzero exactly like width/height and forwarded into the same MipiConfig struct, so it is clearly a third required dimension of the video configuration, but no instruction in this handler reveals its unit -- named conservatively per the task's own guidance to flag genuinely uncertain fields. |
  | 7 | 1 | `mipi_lv_param_color_fmt` (Pixel/Color Format Code) | uint8 | Passed directly to the exported getOmxColor() helper to resolve an OMX_COLOR_FORMATTYPE value; that resolved value must be nonzero or the request is rejected (0xE6). Confirmed to be a color/pixel-format selector by this direct call, exact enum-value table not extracted (getOmxColor's own body was not disassembled). |
  | 8 | 13 | `mipi_lv_param_unused_tail` (Unused Tail Bytes) | bytes | Part of the fixed 21-byte wire length this handler requires, copied into the local buffer, but never read by any instruction after the copy -- confirmed unused by this specific handler. |

**Worked example:**

- Request payload: `00 80 07 38 04 1E 00 01 00 00 00 00 00 00 00 00 00 00 00 00 00`
  21-byte payload: reserved byte 0x00; width=1920 (0x0780 LE = 80 07); height=1080 (0x0438 LE = 38 04); third dimension=30 (0x001E LE = 1E 00, illustrative placeholder since its unit is unconfirmed); color-format code=0x01 (an ordinary nonzero value that getOmxColor() must resolve to a valid OMX format for the request to succeed); 13 trailing bytes are present only to satisfy the 21-byte length gate and are not read by this handler.
- Response payload: `00`
  On success the handler calls duss_event_resp_ok(client, event) -- represented here as the conventional 1-byte 0x00 success retcode used elsewhere in this project's ack documentation. On any validation failure (length<21, width/height/dim3==0, unresolved color format, or a null context pointer) it instead calls duss_event_resp_err(client, event, 0xE6) -- i.e. the same ack slot would instead carry error code 0xE6.

- **Handler:** `dji::hu_hdvt_set_liveview_param`, registered by
  `dji::MipiHsRecvV1::initEventClientCallback`.
- **Purpose:** sets MIPI/HDVT live-view parameters for the receive path.
  The handler performs real input validation before acting: it requires
  the incoming event payload-length field to be ≥ 0x15 (21) bytes, and
  copies exactly 21 fixed bytes into a stack buffer matching that length
  check (no length-driven overflow found).
- **Evidence:** direct call to
  `duss_event_register_dynamic_command_with_user_data(client, cmd_set=0x09,
  cmd_id=0xAA, handler=&dji::hu_hdvt_set_liveview_param, this)` inside
  `libMipiHandshake.so` (ARM32), cross-confirmed by a matching teardown
  call to `duss_event_cancel_dynamic_command`. This is the only
  `(cmd_set, cmd_id)` pair registered anywhere in this library.
- **Confidence:** high on the `(cmd_set, cmd_id)` pair, registration
  mechanism, and the handler's input-validation behavior (all directly
  disassembly-confirmed). See `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.
