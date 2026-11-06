# Cmd Set 0x04 — Gimbal

Total known command IDs: 54

## 0x00 — Gimbal Reserved

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x01 — Gimbal Control

Payload decoder: `gimbal_control_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_control_unkn0` (Unknown0) | uint16 | Accepted values 363..1685 |
  | 2 | 2 | `gimbal_control_unkn1` (Unknown1) | uint16 | Accepted values 363..1685 |
  | 4 | 2 | `gimbal_control_unkn2` (Unknown2) | uint16 | Accepted values 363..1685 |

  *if (payload:len() >= 8) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 6 | 2 | `gimbal_control_padding` (Padding) | bytes | Unused |

## 0x02 — Gimbal Get Position

Payload decoder: `gimbal_get_position_dissector`

## 0x03 — Gimbal Set Param

Payload decoder: `gimbal_set_param_dissector`

## 0x04 — Gimbal Get Param

Payload decoder: `gimbal_get_param_dissector`

## 0x05 — Gimbal Params Get

Payload decoder: `gimbal_params_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_params_pitch` (Gimbal Pitch) | int16 | 0.1 degree |
  | 2 | 2 | `gimbal_params_roll` (Gimbal Roll) | int16 | 0.1 degree |
  | 4 | 2 | `gimbal_params_yaw` (Gimbal Yaw) | int16 | 0.1 degree |
  | 6 | 1 | `gimbal_params_masked06` (Masked06) | uint8 |  |
  | 6 | 1 | `gimbal_params_sub_mode` (Sub Mode) | uint8 | mask:`0x20` |
  | 6 | 1 | `gimbal_params_mode` (Mode) | uint8 | enum:`enums.GIMBAL_PARAMS_MODE_ENUM`; mask:`0xc0` |
  | 7 | 1 | `gimbal_params_roll_adjust` (Roll Adjust) | int8 |  |
  | 8 | 2 | `gimbal_params_yaw_angle` (Yaw Angle) | uint16 | Not sure whether Yaw angle or Joytick Direction |
  | 8 | 2 | `gimbal_params_joystick_ver_direction` (Joystick Ver Direction) | uint16 | mask:`0x03` |
  | 8 | 2 | `gimbal_params_joystick_hor_direction` (Joystick Hor Direction) | uint16 | mask:`0x0c` |
  | 10 | 1 | `gimbal_params_masked0a` (Masked0A) | uint8 |  |
  | 10 | 1 | `gimbal_params_pitch_in_limit` (Pitch In Limit) | uint8 | mask:`0x01`; Pitch arm is beyond its limit positions |
  | 10 | 1 | `gimbal_params_roll_in_limit` (Roll In Limit) | uint8 | mask:`0x02`; Roll arm is beyond its limit positions |
  | 10 | 1 | `gimbal_params_yaw_in_limit` (Yaw In Limit) | uint8 | mask:`0x04`; Yaw arm is beyond its limit positions |
  | 10 | 1 | `gimbal_params_auto_calibration` (Auto Calibration) | uint8 | mask:`0x08`; Auto calibration in progress |
  | 10 | 1 | `gimbal_params_auto_calibration_result` (Auto Calibration Result) | uint8 | mask:`0x10` |
  | 10 | 1 | `gimbal_params_stuck` (Stuck) | uint8 | mask:`0x40` |
  | 11 | 1 | `gimbal_params_masked0b` (Masked0B) | uint8 |  |
  | 11 | 1 | `gimbal_params_version` (Version) | uint8 | mask:`0x0f` |
  | 11 | 1 | `gimbal_params_double_click` (Double Click) | uint8 | mask:`0x20` |
  | 11 | 1 | `gimbal_params_triple_click` (Triple Click) | uint8 | mask:`0x40` |
  | 11 | 1 | `gimbal_params_single_click` (Single Click) | uint8 | mask:`0x80` |

  *if (payload:len() >= offset + 12) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 12 | 4 | `gimbal_params_unkn0c` (Unknown0c) | uint32 |  |
  | 16 | 4 | `gimbal_params_unkn10` (Unknown10-i32) | uint32 |  |
  | 20 | 4 | `gimbal_params_unkn14` (Unknown14) | uint32 |  |

  *elseif (payload:len() >= offset + 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 12 | 4 | `gimbal_params_unkn0c` (Unknown0c) | uint32 |  |
  | 16 | 3 | `gimbal_params_unkn10b` (Unknown10-bt) | bytes |  |

## 0x06 — Gimbal Push AETR

Payload decoder: `gimbal_push_aetr_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_push_aetr_unkn0` (Unknown0) | uint16 | Accepted values are 364..1684 |
  | 2 | 2 | `gimbal_push_aetr_unkn1` (Unknown1) | uint16 | Accepted values are 364..1684 |
  | 4 | 2 | `gimbal_push_aetr_unkn2` (Unknown2) | uint16 | Accepted values are 364..1684 |
  | 6 | 2 | `gimbal_push_aetr_unkn3` (Unknown3) | uint16 | Accepted values are 364..1684 |

## 0x07 — Gimbal Adjust Roll

Payload decoder: `gimbal_adjust_roll_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_adjust_roll_adjustment_val` (Adjustment Value) | int8 |  |

## 0x08 — Gimbal Calibration

Payload decoder: `gimbal_calibrate_dissector`

  *if (payload:len() <= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_calibrate_cmd` (Calib. Command) | uint8 | enum:`enums.GIMBAL_CALIBRATE_CMD_ENUM` |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_calibrate_status1` (Calib. Status1) | uint8 |  |
  | 1 | 1 | `gimbal_calibrate_status2` (Calib. Status2) | uint8 |  |

## 0x09 — Gimbal Reserved2

Payload decoder: `gimbal_reserved2_dissector`

## 0x0A — (name unknown)

Payload decoder: `gimbal_ext_ctrl_degree_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_ext_ctrl_degree_unknown0` (Unknown0) | int16 | angle in degrees * 10 |
  | 2 | 2 | `gimbal_ext_ctrl_degree_unknown2` (Unknown2) | int16 | angle in degrees * 10 |
  | 4 | 2 | `gimbal_ext_ctrl_degree_unknown4` (Unknown4) | int16 | angle in degrees * 10 |
  | 6 | 2 | `gimbal_ext_ctrl_degree_unknown6` (Unknown6) | int16 | unknown unit * 100 |
  | 8 | 1 | `gimbal_ext_ctrl_degree_unknown8` (Unknown8) | uint8 | flag fields |
  | 9 | 1 | `gimbal_ext_ctrl_degree_unknown9` (Unknown9) | uint8 | unknown unit / 2000 |

## 0x0A — Gimbal Ext Ctrl Degree

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0B — (name unknown)

Payload decoder: `gimbal_ext_ctrl_status_dissector`

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_ext_ctrl_status_status` (Status) | uint8 | Request processing status; always 0. |
  | 1 | 1 | `gimbal_ext_ctrl_status_flags` (Flags) | uint8 | Only the top bit is meaningful |
  | 2 | 2 | `gimbal_ext_ctrl_status_unknown2` (Unknown2) | int16 |  |

## 0x0B — Gimbal Get Ext Ctrl Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0C — (name unknown)

Payload decoder: `gimbal_ext_ctrl_accel_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_ext_ctrl_accel_unknown0` (Unknown0) | int16 | angle in degrees * 10 |
  | 2 | 2 | `gimbal_ext_ctrl_accel_unknown2` (Unknown2) | int16 | angle in degrees * 10 |
  | 4 | 2 | `gimbal_ext_ctrl_accel_unknown4` (Unknown4) | int16 | angle in degrees * 10 |
  | 6 | 1 | `gimbal_ext_ctrl_accel_unknown6` (Unknown6) | uint8 | flag fields |

## 0x0C — Gimbal Ext Ctrl Accel

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0D — Gimbal Suspend/Resume

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0D — (name unknown)

Payload decoder: `gimbal_suspend_resume_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_suspend_resume_cmd` (Command) | uint16 | enum:`enums.GIMBAL_SUSPEND_RESUME_CMD_ENUM` |

## 0x0E — Gimbal Thirdp Magn

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0E — (name unknown)

Payload decoder: `gimbal_thirdp_magn_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_thirdp_magn_unknown0` (Unknown0) | int16 |  |
  | 2 | 2 | `gimbal_thirdp_magn_unknown2` (Unknown2) | int16 |  |
  | 4 | 2 | `gimbal_thirdp_magn_unknown4` (Unknown4) | int16 |  |

## 0x0F — Gimbal User Params Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0F — (name unknown)

Payload decoder: `gimbal_user_params_set_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_user_params_set_param_idx` (Param Idx) | int8 |  |
  | 1 | 1 | `gimbal_user_params_set_param_size` (Param Size) | uint8 |  |

  *if param_size == 8 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 8 | `gimbal_user_params_set_param_value` (Param Value) | bytes |  |

  *elseif param_size == 4 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 4 | `gimbal_user_params_set_param_value` (Param Value) | bytes |  |

  *elseif param_size == 2 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 2 | `gimbal_user_params_set_param_value` (Param Value) | bytes |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 1 | `gimbal_user_params_set_param_value` (Param Value) | bytes |  |

## 0x10 — Gimbal User Params Get

Payload decoder: `gimbal_user_params_get_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_user_params_get_param_idx` (Param Idx) | int8 |  |

## 0x11 — Gimbal User Params Save

Payload decoder: `gimbal_user_params_save_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_user_params_save_reserved` (Reserved) | int8 | Unused value |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_user_params_save_resp_status` (Status) | uint8 | Request processing status; non-zero value means error. |

## 0x13 — Gimbal User Params Reset Default

Payload decoder: `gimbal_user_params_reset_def_dissector`

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_user_params_reset_def_resp_status` (Status) | uint8 | Request processing status; non-zero value means error. |

## 0x14 — Gimbal Abs Angle Control

Payload decoder: `gimbal_abs_angle_control_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_abs_angle_control_angle1` (Angle1) | int16 | in degrees * 10 |
  | 2 | 2 | `gimbal_abs_angle_control_angle2` (Angle2) | int16 | in degrees * 10 |
  | 4 | 2 | `gimbal_abs_angle_control_angle3` (Angle3) | int16 | in degrees * 10 |
  | 6 | 1 | `gimbal_abs_angle_control_flags` (Flags) | uint8 |  |
  | 7 | 1 | `gimbal_abs_angle_control_field7` (Field6) | uint8 |  |

## 0x15 — Gimbal Movement

Payload decoder: `gimbal_move_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_move_unknown0` (Unknown0) | int8 | 0.04 degree |
  | 1 | 1 | `gimbal_move_unknown1` (Unknown1) | int8 | 0.04 degree |
  | 2 | 1 | `gimbal_move_unknown2` (Unknown2) | int8 | 0.04 degree |
  | 3 | 1 | `gimbal_move_unknown3` (Unknown3) | int8 | 0.1 degree |
  | 4 | 1 | `gimbal_move_unknown4` (Unknown4) | int8 | 0.1 degree |
  | 5 | 1 | `gimbal_move_unknown5` (Unknown5) | int8 | 0.1 degree |
  | 6 | 1 | `gimbal_move_unknown6` (Unknown6) | uint8 | percent |
  | 7 | 1 | `gimbal_move_unknown7` (Unknown7) | uint8 | percent |
  | 8 | 1 | `gimbal_move_roll_adjust` (Roll Adjust) | uint8 |  |
  | 9 | 11 | `gimbal_move_reserved` (Reserved) | bytes | should be zero-filled |

## 0x1C — (name unknown)

Payload decoder: `gimbal_type_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_type_type` (Type) | uint8 | enum:`enums.GIMBAL_TYPE_TYPE_DJI_GIMBAL_TYPE_ENUM` |

## 0x1C — Gimbal Type Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1E — (name unknown)

Payload decoder: `gimbal_degree_info_subscription_dissector`

## 0x1E — Gimbal Degree Info Subscription

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — Gimbal TBD 20

Payload decoder: `gimbal_tbd_20_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `gimbal_tbd_20_unknown0` (Unknown0) | int32 |  |
  | 4 | 1 | `gimbal_tbd_20_unknown4` (Unknown4) | uint8 |  |
  | 5 | 1 | `gimbal_tbd_20_unknown5` (Unknown5) | uint8 |  |

## 0x21 — Gimbal TBD 21

Payload decoder: `gimbal_tbd_21_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_tbd_21_dry_run` (Dry Run) | int8 | When not zero |
  | 1 | 1 | `gimbal_tbd_21_unknown1` (Unknown1) | int8 |  |
  | 2 | 4 | `gimbal_tbd_21_arr0_field0` (Array el0 Field0) | uint32 |  |
  | 6 | 1 | `gimbal_tbd_21_arr0_field4` (Array el0 Field4) | uint8 |  |
  | 7 | 1 | `gimbal_tbd_21_arr0_field5` (Array el0 Field5) | uint8 |  |
  | 8 | 4 | `gimbal_tbd_21_arr1_field0` (Array el1 Field0) | uint32 |  |
  | 12 | 1 | `gimbal_tbd_21_arr1_field4` (Array el1 Field4) | uint8 |  |
  | 13 | 1 | `gimbal_tbd_21_arr1_field5` (Array el1 Field5) | uint8 |  |
  | 14 | 4 | `gimbal_tbd_21_arr2_field0` (Array el2 Field0) | uint32 |  |
  | 18 | 1 | `gimbal_tbd_21_arr2_field4` (Array el2 Field4) | uint8 |  |
  | 19 | 1 | `gimbal_tbd_21_arr2_field5` (Array el2 Field5) | uint8 |  |

## 0x24 — Gimbal User Params Get

Payload decoder: `gimbal_user_params_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `gimbal_user_params_unknown00` (Unknown00) | bytes |  |
  | 2 | 1 | `gimbal_user_params_preset_id` (Preset Id) | uint8 |  |
  | 3 | 6 | `gimbal_user_params_unknown03` (Unknown03) | bytes |  |
  | 9 | 2 | `gimbal_user_params_yaw_speed` (Yaw Speed) | uint16 |  |
  | 11 | 2 | `gimbal_user_params_unknown0b` (Unknown0B) | bytes |  |
  | 13 | 2 | `gimbal_user_params_pitch_speed` (Pitch Speed) | uint16 |  |
  | 15 | 2 | `gimbal_user_params_unknown0f` (Unknown0F) | bytes |  |
  | 17 | 2 | `gimbal_user_params_yaw_deadband` (Yaw Deadband) | uint16 |  |
  | 19 | 2 | `gimbal_user_params_unknown13` (Unknown13) | bytes |  |
  | 21 | 2 | `gimbal_user_params_pitch_deadband` (Pitch Deadband) | uint16 |  |
  | 23 | 2 | `gimbal_user_params_unknown17` (Unknown17) | bytes |  |
  | 25 | 2 | `gimbal_user_params_stick_yaw_speed` (Stick Yaw Speed) | uint16 |  |
  | 27 | 2 | `gimbal_user_params_unknown1b` (Unknown1B) | bytes |  |
  | 29 | 2 | `gimbal_user_params_stick_pitch_speed` (Stick Pitch Speed) | uint16 |  |
  | 31 | 2 | `gimbal_user_params_unknown1f` (Unknown1F) | bytes |  |
  | 33 | 2 | `gimbal_user_params_stick_yaw_smooth` (Stick Yaw Smooth) | uint16 |  |
  | 35 | 2 | `gimbal_user_params_unknown23` (Unknown23) | bytes |  |
  | 37 | 2 | `gimbal_user_params_stick_pitch_smooth` (Stick Pitch Smooth) | uint16 |  |
  | 39 | 8 | `gimbal_user_params_unknown27` (Unknown27) | bytes |  |
  | 47 | 2 | `gimbal_user_params_roll_speed` (Roll Speed) | uint16 |  |
  | 49 | 2 | `gimbal_user_params_unknown31` (Unknown31) | bytes |  |
  | 51 | 2 | `gimbal_user_params_roll_deadband` (Roll Deadband) | uint16 |  |
  | 53 | 2 | `gimbal_user_params_unknown35` (Unknown35) | bytes |  |
  | 55 | 2 | `gimbal_user_params_yaw_accel` (Yaw Accel) | uint16 |  |
  | 57 | 2 | `gimbal_user_params_unknown39` (Unknown39) | bytes |  |
  | 59 | 2 | `gimbal_user_params_pitch_accel` (Pitch Accel) | uint16 |  |
  | 61 | 2 | `gimbal_user_params_unknown3d` (Unknown3D) | bytes |  |
  | 63 | 2 | `gimbal_user_params_roll_accel` (Roll Accel) | uint16 |  |
  | 65 | 2 | `gimbal_user_params_unknown41` (Unknown41) | bytes |  |
  | 67 | 1 | `gimbal_user_params_yaw_smooth_track` (Yaw Smooth Track) | uint8 |  |
  | 68 | 2 | `gimbal_user_params_unknown44` (Unknown44) | bytes |  |
  | 70 | 1 | `gimbal_user_params_pitch_smooth_track` (Pitch Smooth Track) | uint8 |  |
  | 71 | 2 | `gimbal_user_params_unknown47` (Unknown47) | bytes |  |
  | 73 | 1 | `gimbal_user_params_roll_smooth_track` (Roll Smooth Track) | uint8 |  |

## 0x27 — Gimbal Abnormal Status Get

Payload decoder: `gimbal_abnormal_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_abnormal_status_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `gimbal_abnormal_status_roll_locked` (Roll Locked) | uint8 | mask:`0x01` |
  | 0 | 1 | `gimbal_abnormal_status_pitch_locked` (Pitch Locked) | uint8 | mask:`0x02` |
  | 0 | 1 | `gimbal_abnormal_status_yaw_locked` (Yaw Locked) | uint8 | mask:`0x04` |
  | 1 | 1 | `gimbal_abnormal_status_masked01` (Masked01) | uint8 |  |
  | 1 | 1 | `gimbal_abnormal_status_joint_lock_after_startup` (Joint Lock After Startup) | uint8 | mask:`0x01` |
  | 1 | 1 | `gimbal_abnormal_status_joint_lock_when_startup` (Joint Lock When Startup) | uint8 | mask:`0x02` |
  | 1 | 1 | `gimbal_abnormal_status_motor_protected` (Motor Protected) | uint8 | mask:`0x04` |
  | 1 | 1 | `gimbal_abnormal_status_error_recent_when_start_up` (Error Recent When Start Up) | uint8 | mask:`0x08` |
  | 1 | 1 | `gimbal_abnormal_status_upgrading` (Upgrading) | uint8 | mask:`0x10` |
  | 1 | 1 | `gimbal_abnormal_status_yaw_limit` (Yaw Limit) | uint8 | mask:`0x20` |
  | 1 | 1 | `gimbal_abnormal_status_error_recent_or_selfie` (Error Recent Or Selfie) | uint8 | mask:`0x40` |
  | 1 | 1 | `gimbal_abnormal_status_pano_ready` (Pano Ready) | uint8 | mask:`0x80` |
  | 2 | 1 | `gimbal_abnormal_status_masked02` (Masked02) | uint8 |  |
  | 2 | 1 | `gimbal_abnormal_status_fan_direction` (Fan Direction) | uint8 | mask:`0x02` |
  | 2 | 1 | `gimbal_abnormal_status_vertical_direction` (Vertical Direction) | uint8 | mask:`0x04` |
  | 2 | 1 | `gimbal_abnormal_status_in_flashlight` (In Flashlight) | uint8 | mask:`0x08` |
  | 2 | 1 | `gimbal_abnormal_status_portrait` (Portrait) | uint8 | mask:`0x10` |
  | 2 | 1 | `gimbal_abnormal_status_gimbal_direction_when_vertical` (Gimbal Direction When Vertical) | uint8 | mask:`0x20` |
  | 3 | 1 | `gimbal_abnormal_status_masked03` (Masked03) | uint8 |  |
  | 3 | 1 | `gimbal_abnormal_status_phone_out_gimbal` (Phone Out Gimbal) | uint8 | mask:`0x01` |
  | 3 | 1 | `gimbal_abnormal_status_gimbal_gravity` (Gimbal Gravity) | uint8 | mask:`0x06` |
  | 3 | 1 | `gimbal_abnormal_status_yaw_limited_in_tracking` (Yaw Limited In Tracking) | uint8 | mask:`0x20` |
  | 3 | 1 | `gimbal_abnormal_status_pitch_limited_in_tracking` (Pitch Limited In Tracking) | uint8 | mask:`0x40` |
  | 4 | 1 | `gimbal_abnormal_status_masked04` (Masked04) | uint8 |  |
  | 4 | 1 | `gimbal_abnormal_status_sleep_mode` (Sleep Mode) | uint8 | mask:`0x01` |

## 0x2B — Gimbal Tutorial Status Get

Payload decoder: `gimbal_tutorial_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_tutorial_status_cur_step` (Cur Step) | uint8 | enum:`enums.GIMBAL_TUTORIAL_STATUS_CUR_STEP_TUTORIAL_STATUS_ENUM` |
  | 1 | 4 | `gimbal_tutorial_status_step_status` (Step Status) | uint32 |  |
  | 1 | 4 | `gimbal_tutorial_status_is_unlock` (Is Unlock) | uint32 | mask:`0x01` |
  | 1 | 4 | `gimbal_tutorial_status_is_upright` (Is Upright) | uint32 | mask:`0x02` |
  | 1 | 4 | `gimbal_tutorial_status_is_follow_finish` (Is Follow Finish) | uint32 | mask:`0x04` |
  | 1 | 4 | `gimbal_tutorial_status_is_stick_finish` (Is Stick Finish) | uint32 | mask:`0x08` |
  | 1 | 4 | `gimbal_tutorial_status_is_lock_direction_finish` (Is Lock Direction Finish) | uint32 | mask:`0x10` |
  | 1 | 4 | `gimbal_tutorial_status_is_recent_finish` (Is Recent Finish) | uint32 | mask:`0x20` |
  | 1 | 4 | `gimbal_tutorial_status_is_selfie_finish` (Is Selfie Finish) | uint32 | mask:`0x40` |
  | 1 | 4 | `gimbal_tutorial_status_is_handle_push_finish` (Is Handle Push Finish) | uint32 | mask:`0x80` |
  | 1 | 4 | `gimbal_tutorial_status_is_app_control_finish` (Is App Control Finish) | uint32 | mask:`0x100` |

## 0x2C — Gimbal Tutorial Step Set

Payload decoder: `gimbal_tutorial_step_set_dissector`

## 0x30 — Gimbal Auto Calibration Status

Payload decoder: `gimbal_auto_calibration_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_auto_calibration_status_progress` (Progress) | uint8 |  |
  | 1 | 1 | `gimbal_auto_calibration_status_status` (Status) | uint8 |  |

## 0x31 — Robin Params Set

Payload decoder: `gimbal_robin_params_set_dissector`

## 0x32 — Robin Params Get

Payload decoder: `gimbal_robin_params_get_dissector`

## 0x33 — Robin Battery Info Push

Payload decoder: `gimbal_battery_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_battery_info_a` (A) | uint8 |  |

## 0x34 — Gimbal Handle Params Set

Payload decoder: `gimbal_handle_params_set_dissector`

## 0x36 — Gimbal Handle Params Get

Payload decoder: `gimbal_handle_params_get_dissector`

## 0x37 — Gimbal Timelapse Params Set

Payload decoder: `gimbal_timelapse_params_set_dissector`

## 0x38 — Gimbal Timelapse Status

Payload decoder: `gimbal_timelapse_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_timelapse_status_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `gimbal_timelapse_status_timelapse_status` (Timelapse Status) | uint8 | mask:`0x03` |

## 0x39 — Gimbal Lock

Payload decoder: `gimbal_lock_dissector`

## 0x3A — Gimbal Rotate Camera X Axis

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3A — (name unknown)

Payload decoder: `gimbal_rotate_camera_x_axis_dissector`

## 0x45 — Gimbal Get Temp

Payload decoder: `gimbal_get_temp_dissector`

## 0x47 — Gimbal TBD 47

Payload decoder: `gimbal_tbd_47_dissector`

## 0x4C — Gimbal Reset And Set Mode

Payload decoder: `gimbal_set_mode_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `gimbal_set_mode_mode` (Mode) | uint8 |  |
  | 1 | 1 | `gimbal_set_mode_cmd` (Cmd) | uint8 |  |

## 0x56 — Gimbal NotiFy Camera Id

Payload decoder: `gimbal_notify_camera_id_dissector`

## 0x57 — Handheld Stick State Get/Push

Payload decoder: `gimbal_handheld_stick_state_get_dissector`

## 0x58 — Handheld Stick Control Set

Payload decoder: `gimbal_handheld_stick_control_set_dissector`
