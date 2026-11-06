# Cmd Set 0x0a — Mono/Binocular (Vision)

Total known command IDs: 48

## 0x01 — Eye Bino Info

Payload decoder: `mbino_bino_info_dissector`

## 0x02 — Eye Mono Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — Eye Ultrasonic Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — Eye Oa Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — Eye Relitive Pos

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — Eye Avoidance Param

Payload decoder: `mbino_avoidance_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_avoidance_param_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `mbino_avoidance_param_braking` (Braking) | uint8 | mask:`0x01` |
  | 0 | 1 | `mbino_avoidance_param_visual_sensor_working` (Visual Sensor Working) | uint8 | mask:`0x02` |
  | 0 | 1 | `mbino_avoidance_param_avoid_open` (Avoid Open) | uint8 | mask:`0x04` |
  | 0 | 1 | `mbino_avoidance_param_be_shuttle_mode` (Be Shuttle Mode) | uint8 | mask:`0x08` |
  | 0 | 1 | `mbino_avoidance_param_avoid_front_work` (Avoid Front Work) | uint8 | mask:`0x10` |
  | 0 | 1 | `mbino_avoidance_param_avoid_right_work` (Avoid Right Work) | uint8 | mask:`0x20` |
  | 0 | 1 | `mbino_avoidance_param_avoid_behind_work` (Avoid Behind Work) | uint8 | mask:`0x40` |
  | 0 | 1 | `mbino_avoidance_param_avoid_left_work` (Avoid Left Work) | uint8 | mask:`0x80` |
  | 1 | 1 | `mbino_avoidance_param_masked01` (Masked01) | uint8 |  |
  | 1 | 1 | `mbino_avoidance_param_avoid_front_distance_level` (Avoid Front Distance Level) | uint8 | mask:`0x0f` |
  | 1 | 1 | `mbino_avoidance_param_avoid_front_alert_level` (Avoid Front Alert Level) | uint8 | mask:`0xf0` |
  | 2 | 1 | `mbino_avoidance_param_masked02` (Masked02) | uint8 |  |
  | 2 | 1 | `mbino_avoidance_param_avoid_right_distance_level` (Avoid Right Distance Level) | uint8 | mask:`0x0f` |
  | 2 | 1 | `mbino_avoidance_param_avoid_right_alert_level` (Avoid Right Alert Level) | uint8 | mask:`0xf0` |
  | 3 | 1 | `mbino_avoidance_param_masked03` (Masked03) | uint8 |  |
  | 3 | 1 | `mbino_avoidance_param_avoid_behind_distance_level` (Avoid Behind Distance Level) | uint8 | mask:`0x0f` |
  | 3 | 1 | `mbino_avoidance_param_avoid_behind_alert_level` (Avoid Behind Alert Level) | uint8 | mask:`0xf0` |
  | 4 | 1 | `mbino_avoidance_param_masked04` (Masked04) | uint8 |  |
  | 4 | 1 | `mbino_avoidance_param_avoid_left_distance_level` (Avoid Left Distance Level) | uint8 | mask:`0x0f` |
  | 4 | 1 | `mbino_avoidance_param_avoid_left_alert_level` (Avoid Left Alert Level) | uint8 | mask:`0xf0` |
  | 5 | 1 | `mbino_avoidance_param_masked05` (Masked05) | uint8 |  |
  | 5 | 1 | `mbino_avoidance_param_allow_front` (Allow Front) | uint8 | mask:`0x01` |
  | 5 | 1 | `mbino_avoidance_param_allow_right` (Allow Right) | uint8 | mask:`0x02` |
  | 5 | 1 | `mbino_avoidance_param_allow_back` (Allow Back) | uint8 | mask:`0x04` |
  | 5 | 1 | `mbino_avoidance_param_allow_left` (Allow Left) | uint8 | mask:`0x08` |
  | 6 | 1 | `mbino_avoidance_param_index` (Index) | uint8 |  |

## 0x07 — Eye Obstacle Info

Payload decoder: `mbino_obstacle_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_obstacle_info_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `mbino_obstacle_info_observe_count` (Observe Count) | uint8 | mask:`0x1f` |
  | 0 | 1 | `mbino_obstacle_info_sensor_type` (Sensor Type) | uint8 | enum:`enums.MBINO_OBSTACLE_INFO_SENSOR_TYPE_ENUM`; mask:`0xe0` |

## 0x08 — Eye TapGo Obst Avo Info

Payload decoder: `mbino_tapgo_obst_avo_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_tapgo_obst_avo_info_alert_level` (Alert Level) | uint8 |  |
  | 1 | 1 | `mbino_tapgo_obst_avo_info_observe_count` (Observe Count) | uint8 |  |

## 0x0A — Eye Push Vision Debug Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0B — Eye Push Control Debug Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0D — Eye Track Log

Payload decoder: `mbino_track_log_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | ? | `mbino_track_log_text` (Track Log) | string |  |

## 0x0E — Eye Point Log

Payload decoder: `mbino_point_log_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | ? | `mbino_point_log_text` (Point Log) | string |  |

## 0x0F — Eye Push SDK Control Cmd

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x10 — Eye Enable Tracking Taptogo

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x11 — Eye Push Target Speed Pos Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x12 — Eye Push Target Pos Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x13 — Eye Push Trajectory

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x14 — Eye Push Expected Speed Angle

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x15 — Eye Receive Frame Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x19 — Eye Flat Check

Payload decoder: `mbino_flat_check_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_flat_check_tink_count` (Tink Count) | uint8 |  |

## 0x1D — Eye Fixed Wing Ctrl

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1E — Eye Fixed Wing Status Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — Eye Marquee Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — Eye Tracking Cnf Cancel

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — Eye Move Marquee Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x23 — Eye Tracking Status Push

Payload decoder: `mbino_tracking_status_push_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_tracking_status_push_rect_mode` (Rect Mode) | uint8 | enum:`enums.MBINO_TRACK_STATUS_RECT_MODE_TRACK_MODE_ENUM` |
  | 1 | 4 | `mbino_tracking_status_push_center_x` (Center X) | float |  |
  | 5 | 4 | `mbino_tracking_status_push_center_y` (Center Y) | float |  |
  | 9 | 4 | `mbino_tracking_status_push_width` (Width) | float |  |
  | 13 | 4 | `mbino_tracking_status_push_height` (Height) | float |  |
  | 17 | 1 | `mbino_tracking_status_push_unknown11` (Unknown11) | uint8 |  |
  | 18 | 2 | `mbino_tracking_status_push_session_id` (Session Id) | uint16 |  |
  | 20 | 1 | `mbino_tracking_status_push_masked14` (Masked14) | uint8 |  |
  | 20 | 1 | `mbino_tracking_status_push_human_target` (Human Target) | uint8 | mask:`0x01` |
  | 20 | 1 | `mbino_tracking_status_push_head_lock` (Head Lock) | uint8 | mask:`0x02` |
  | 21 | 1 | `mbino_tracking_status_push_tracking_mode` (Tracking Mode) | uint8 | enum:`enums.MBINO_TRACK_STATUS_TRACKING_MODE_ENUM` |
  | 22 | 1 | `mbino_tracking_status_push_target_type` (Target Type) | uint8 | enum:`enums.MBINO_TRACK_STATUS_TARGET_TYPE_TARGET_OBJ_TYPE_ENUM` |
  | 23 | 1 | `mbino_tracking_status_push_target_action` (Target Action) | uint8 | enum:`enums.MBINO_TRACK_STATUS_TARGET_ACTION_ENUM` |

## 0x24 — Eye Position Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x25 — Eye Fly Ctl Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x26 — Eye TapGo Status Push

Payload decoder: `mbino_tapgo_status_push_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_tapgo_status_push_traget_mode` (Traget Mode) | uint8 | enum:`enums.MBINO_TAPGO_STATUS_PUSH_TRAGET_MODE_POINT_MODE_ENUM` |
  | 1 | 3 | `mbino_tapgo_status_push_masked01` (Masked01) | uint24 |  |
  | 1 | 3 | `mbino_tapgo_status_push_rc_not_in_f_mode` (Rc Not In F Mode) | uint24 | mask:`0x01` |
  | 1 | 3 | `mbino_tapgo_status_push_cant_detour` (Cant Detour) | uint24 | mask:`0x02` |
  | 1 | 3 | `mbino_tapgo_status_push_braked_by_collision` (Braked By Collision) | uint24 | mask:`0x04` |
  | 1 | 3 | `mbino_tapgo_status_push_detour_up` (Detour Up) | uint24 | mask:`0x08` |
  | 1 | 3 | `mbino_tapgo_status_push_detour_left` (Detour Left) | uint24 | mask:`0x10` |
  | 1 | 3 | `mbino_tapgo_status_push_detour_right` (Detour Right) | uint24 | mask:`0x20` |
  | 1 | 3 | `mbino_tapgo_status_push_stick_add` (Stick Add) | uint24 | mask:`0x40` |
  | 1 | 3 | `mbino_tapgo_status_push_out_of_range` (Out Of Range) | uint24 | mask:`0x80` |
  | 1 | 3 | `mbino_tapgo_status_push_user_quick_pull_pitch` (User Quick Pull Pitch) | uint24 | mask:`0x100` |
  | 1 | 3 | `mbino_tapgo_status_push_in_low_flying` (In Low Flying) | uint24 | mask:`0x200` |
  | 1 | 3 | `mbino_tapgo_status_push_running_delay` (Running Delay) | uint24 | mask:`0x400` |
  | 1 | 3 | `mbino_tapgo_status_push_in_pointing` (In Pointing) | uint24 | mask:`0x800` |
  | 1 | 3 | `mbino_tapgo_status_push_terrian_follow` (Terrian Follow) | uint24 | mask:`0x1000` |
  | 1 | 3 | `mbino_tapgo_status_push_paused` (Paused) | uint24 | mask:`0x2000` |
  | 1 | 3 | `mbino_tapgo_status_push_front_image_over_exposure` (Front Image Over Exposure) | uint24 | mask:`0x10000` |
  | 1 | 3 | `mbino_tapgo_status_push_front_image_under_exposure` (Front Image Under Exposure) | uint24 | mask:`0x20000` |
  | 1 | 3 | `mbino_tapgo_status_push_front_image_diff` (Front Image Diff) | uint24 | mask:`0x40000` |
  | 1 | 3 | `mbino_tapgo_status_push_front_demark_error` (Front Demark Error) | uint24 | mask:`0x80000` |
  | 1 | 3 | `mbino_tapgo_status_push_non_in_flying` (Non In Flying) | uint24 | mask:`0x100000` |
  | 1 | 3 | `mbino_tapgo_status_push_had_tap_stop` (Had Tap Stop) | uint24 | mask:`0x200000` |
  | 4 | 4 | `mbino_tapgo_status_push_axis_x` (Axis X) | float |  |
  | 8 | 4 | `mbino_tapgo_status_push_axis_y` (Axis Y) | float |  |
  | 12 | 4 | `mbino_tapgo_status_push_axis_z` (Axis Z) | float |  |
  | 16 | 2 | `mbino_tapgo_status_push_max_speed` (Max Speed) | uint16 |  |
  | 18 | 2 | `mbino_tapgo_status_push_session_id` (Session Id) | uint16 |  |
  | 20 | 1 | `mbino_tapgo_status_push_tap_mode` (Tap Mode) | uint8 | enum:`enums.MBINO_TAPGO_STATUS_PUSH_TAP_MODE_ENUM` |

## 0x27 — Eye Common Ctl Cmd

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x28 — Eye Get Para Cmd

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x29 — Eye Set Para Cmd

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2A — Eye Com Status Update

Payload decoder: `mbino_com_status_update_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `mbino_com_status_update_masked00` (Masked00) | uint16 |  |
  | 0 | 2 | `mbino_com_status_update_track_system_abnormal` (Track System Abnormal) | uint16 | mask:`0x01` |
  | 0 | 2 | `mbino_com_status_update_point_system_abnormal` (Point System Abnormal) | uint16 | mask:`0x02` |
  | 0 | 2 | `mbino_com_status_update_disparity_pack_lost` (Disparity Pack Lost) | uint16 | mask:`0x04` |
  | 0 | 2 | `mbino_com_status_update_imu_pack_lost` (Imu Pack Lost) | uint16 | mask:`0x08` |
  | 0 | 2 | `mbino_com_status_update_gimbal_pack_lost` (Gimbal Pack Lost) | uint16 | mask:`0x10` |
  | 0 | 2 | `mbino_com_status_update_rc_pack_lost` (Rc Pack Lost) | uint16 | mask:`0x20` |
  | 0 | 2 | `mbino_com_status_update_visual_data_abnormal` (Visual Data Abnormal) | uint16 | mask:`0x40` |
  | 0 | 2 | `mbino_com_status_update_fron_image_over_exposure` (Fron Image Over Exposure) | uint16 | mask:`0x100` |
  | 0 | 2 | `mbino_com_status_update_fron_image_under_exposure` (Fron Image Under Exposure) | uint16 | mask:`0x200` |
  | 0 | 2 | `mbino_com_status_update_front_image_diff` (Front Image Diff) | uint16 | mask:`0x400` |
  | 0 | 2 | `mbino_com_status_update_front_sensor_demark_abnormal` (Front Sensor Demark Abnormal) | uint16 | mask:`0x800` |
  | 0 | 2 | `mbino_com_status_update_non_flying` (Non Flying) | uint16 | mask:`0x1000` |
  | 0 | 2 | `mbino_com_status_update_user_tap_stop` (User Tap Stop) | uint16 | mask:`0x2000` |
  | 0 | 2 | `mbino_com_status_update_tripod_folded` (Tripod Folded) | uint16 | mask:`0x4000` |
  | 2 | 1 | `mbino_com_status_update_masked02` (Masked02) | uint8 |  |
  | 2 | 1 | `mbino_com_status_update_rc_disconnect` (Rc Disconnect) | uint8 | mask:`0x1` |
  | 2 | 1 | `mbino_com_status_update_app_disconnect` (App Disconnect) | uint8 | mask:`0x2` |
  | 2 | 1 | `mbino_com_status_update_out_of_control` (Out Of Control) | uint8 | mask:`0x4` |
  | 2 | 1 | `mbino_com_status_update_in_non_fly_zone` (In Non Fly Zone) | uint8 | mask:`0x8` |
  | 2 | 1 | `mbino_com_status_update_fusion_data_abnormal` (Fusion Data Abnormal) | uint8 | mask:`0x10` |
  | 3 | 1 | `mbino_com_status_update_masked03` (Masked03) | uint8 |  |
  | 3 | 1 | `mbino_com_status_update_in_tracking` (In Tracking) | uint8 | mask:`0x01` |
  | 3 | 1 | `mbino_com_status_update_in_tap_fly` (In Tap Fly) | uint8 | mask:`0x02` |
  | 3 | 1 | `mbino_com_status_update_in_advance_homing` (In Advance Homing) | uint8 | mask:`0x04` |
  | 3 | 1 | `mbino_com_status_update_in_precise_landing` (In Precise Landing) | uint8 | mask:`0x08` |
  | 3 | 1 | `mbino_com_status_update_face_detect_enable` (Face Detect Enable) | uint8 | mask:`0x10` |
  | 3 | 1 | `mbino_com_status_update_moving_object_detect_enable` (Moving Object Detect Enable) | uint8 | mask:`0x20` |
  | 3 | 1 | `mbino_com_status_update_gps_tracking_enable` (Gps Tracking Enable) | uint8 | mask:`0x40` |
  | 4 | 1 | `mbino_com_status_update_masked04` (Masked04) | uint8 |  |

  *if (true) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 4 | 1 | `mbino_com_status_update_gps_error` (Gps Error) | uint8 | mask:`0x01` |
  | 4 | 1 | `mbino_com_status_update_front_visoin_error` (Front Visoin Error) | uint8 | mask:`0x02` |
  | 4 | 1 | `mbino_com_status_update_advance_go_home_state` (Advance Go Home State) | uint8 | enum:`enums.MBINO_COM_STATUS_UPDATE_ADVANCE_GO_HOME_STATE_ENUM`; mask:`0x1c` |
  | 4 | 1 | `mbino_com_status_update_advance_go_home_strategy` (Advance Go Home Strategy) | uint8 | enum:`enums.MBINO_COM_STATUS_UPDATE_ADVANCE_GO_HOME_STRATEGY_ENUM`; mask:`0x60` |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 4 | 1 | `mbino_com_status_update_track_status` (Track Status) | uint8 | enum:`enums.MBINO_COM_STATUS_UPDATE_TRACK_EXCEPTION_STATUS_ENUM`; mask:`0x0f` |
  | 4 | 1 | `mbino_com_status_update_aircraft_gps_abnormal` (Aircraft Gps Abnormal) | uint8 | mask:`0x10` |
  | 4 | 1 | `mbino_com_status_update_phone_gps_abnormal` (Phone Gps Abnormal) | uint8 | mask:`0x20` |
  | 4 | 1 | `mbino_com_status_update_gps_tracking_flusion_abnormal` (Gps Tracking Flusion Abnormal) | uint8 | mask:`0x40` |

## 0x2C — Eye Ta Lock Update

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2D — Eye Smart Landing

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2E — Eye Function List Push

Payload decoder: `mbino_function_list_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_function_list_tink_count` (Tink Count) | uint8 |  |
  | 1 | 4 | `mbino_function_list_masked01` (Masked01) | uint32 |  |
  | 1 | 4 | `mbino_function_list_support_self_cal` (Support Self Cal) | uint32 | mask:`0x01` |
  | 1 | 4 | `mbino_function_list_sensor_status_source` (Sensor Status Source) | uint32 | mask:`0x02` |
  | 5 | 1 | `mbino_function_list_front_disable` (Front Disable) | uint8 |  |
  | 5 | 1 | `mbino_function_list_front_disable_when_auto_landing` (Front Disable When Auto Landing) | uint8 | mask:`0x01` |
  | 5 | 1 | `mbino_function_list_front_disable_by_tripod` (Front Disable By Tripod) | uint8 | mask:`0x02` |
  | 5 | 1 | `mbino_function_list_front_disable_by_switch_sensor` (Front Disable By Switch Sensor) | uint8 | mask:`0x04` |
  | 5 | 1 | `mbino_function_list_front_atti_too_large` (Front Atti Too Large) | uint8 | mask:`0x08` |
  | 6 | 1 | `mbino_function_list_back_disable` (Back Disable) | uint8 |  |
  | 6 | 1 | `mbino_function_list_back_disable_when_auto_landing` (Back Disable When Auto Landing) | uint8 | mask:`0x01` |
  | 6 | 1 | `mbino_function_list_back_disable_by_tripod` (Back Disable By Tripod) | uint8 | mask:`0x02` |
  | 6 | 1 | `mbino_function_list_back_disable_by_switch_sensor` (Back Disable By Switch Sensor) | uint8 | mask:`0x04` |
  | 6 | 1 | `mbino_function_list_back_atti_too_large` (Back Atti Too Large) | uint8 | mask:`0x08` |
  | 7 | 1 | `mbino_function_list_right_disable` (Right Disable) | uint8 |  |
  | 7 | 1 | `mbino_function_list_right_disable_when_auto_landing` (Right Disable When Auto Landing) | uint8 | mask:`0x01` |
  | 7 | 1 | `mbino_function_list_right_disable_by_tripod` (Right Disable By Tripod) | uint8 | mask:`0x02` |
  | 7 | 1 | `mbino_function_list_right_atti_too_large` (Right Atti Too Large) | uint8 | mask:`0x08` |
  | 8 | 1 | `mbino_function_list_left_disable` (Left Disable) | uint8 |  |
  | 8 | 1 | `mbino_function_list_left_disable_when_auto_landing` (Left Disable When Auto Landing) | uint8 | mask:`0x01` |
  | 8 | 1 | `mbino_function_list_left_disable_by_tripod` (Left Disable By Tripod) | uint8 | mask:`0x02` |
  | 8 | 1 | `mbino_function_list_left_atti_too_large` (Left Atti Too Large) | uint8 | mask:`0x08` |

## 0x2F — Eye Sensor Status Push

Payload decoder: `mbino_sensor_status_push_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_sensor_status_push_cnt_index` (Cnt Index) | uint8 |  |
  | 1 | 2 | `mbino_sensor_status_push_masked01` (Masked01) | uint16 |  |
  | 1 | 2 | `mbino_sensor_status_push_bottom_image_exposure_too_long` (Bottom Image Exposure Too Long) | uint16 | mask:`0x08` |
  | 1 | 2 | `mbino_sensor_status_push_bottom_image_diff` (Bottom Image Diff) | uint16 | mask:`0x10` |
  | 1 | 2 | `mbino_sensor_status_push_bottom_under_exposure` (Bottom Under Exposure) | uint16 | mask:`0x20` |
  | 1 | 2 | `mbino_sensor_status_push_bottom_over_exposure` (Bottom Over Exposure) | uint16 | mask:`0x40` |
  | 1 | 2 | `mbino_sensor_status_push_bottom_image_exception` (Bottom Image Exception) | uint16 | mask:`0x80` |
  | 3 | 2 | `mbino_sensor_status_push_masked03` (Masked03) | uint16 |  |
  | 3 | 2 | `mbino_sensor_status_push_front_image_exposure_too_long` (Front Image Exposure Too Long) | uint16 | mask:`0x08` |
  | 3 | 2 | `mbino_sensor_status_push_front_image_diff` (Front Image Diff) | uint16 | mask:`0x10` |
  | 3 | 2 | `mbino_sensor_status_push_front_under_exposure` (Front Under Exposure) | uint16 | mask:`0x20` |
  | 3 | 2 | `mbino_sensor_status_push_front_over_exposure` (Front Over Exposure) | uint16 | mask:`0x40` |
  | 3 | 2 | `mbino_sensor_status_push_front_image_exception` (Front Image Exception) | uint16 | mask:`0x80` |
  | 5 | 2 | `mbino_sensor_status_push_masked05` (Masked05) | uint16 |  |
  | 5 | 2 | `mbino_sensor_status_push_back_image_exposure_too_long` (Back Image Exposure Too Long) | uint16 | mask:`0x08` |
  | 5 | 2 | `mbino_sensor_status_push_back_image_diff` (Back Image Diff) | uint16 | mask:`0x10` |
  | 5 | 2 | `mbino_sensor_status_push_back_under_exposure` (Back Under Exposure) | uint16 | mask:`0x20` |
  | 5 | 2 | `mbino_sensor_status_push_back_over_exposure` (Back Over Exposure) | uint16 | mask:`0x40` |
  | 5 | 2 | `mbino_sensor_status_push_back_image_exception` (Back Image Exception) | uint16 | mask:`0x80` |
  | 7 | 2 | `mbino_sensor_status_push_masked07` (Masked07) | uint16 |  |
  | 7 | 2 | `mbino_sensor_status_push_right3_dtof_abnormal` (Right3 Dtof Abnormal) | uint16 | mask:`0x01` |
  | 7 | 2 | `mbino_sensor_status_push_right_image_exposure_too_long` (Right Image Exposure Too Long) | uint16 | mask:`0x08` |
  | 7 | 2 | `mbino_sensor_status_push_right_image_diff` (Right Image Diff) | uint16 | mask:`0x10` |
  | 7 | 2 | `mbino_sensor_status_push_right_under_exposure` (Right Under Exposure) | uint16 | mask:`0x20` |
  | 7 | 2 | `mbino_sensor_status_push_right_over_exposure` (Right Over Exposure) | uint16 | mask:`0x40` |
  | 7 | 2 | `mbino_sensor_status_push_right_image_exception` (Right Image Exception) | uint16 | mask:`0x80` |
  | 9 | 2 | `mbino_sensor_status_push_masked09` (Masked09) | uint16 |  |
  | 9 | 2 | `mbino_sensor_status_push_left3_dtof_abnormal` (Left3 Dtof Abnormal) | uint16 | mask:`0x01` |
  | 9 | 2 | `mbino_sensor_status_push_left_image_exposure_too_long` (Left Image Exposure Too Long) | uint16 | mask:`0x08` |
  | 9 | 2 | `mbino_sensor_status_push_left_image_diff` (Left Image Diff) | uint16 | mask:`0x10` |
  | 9 | 2 | `mbino_sensor_status_push_left_under_exposure` (Left Under Exposure) | uint16 | mask:`0x20` |
  | 9 | 2 | `mbino_sensor_status_push_left_over_exposure` (Left Over Exposure) | uint16 | mask:`0x40` |
  | 9 | 2 | `mbino_sensor_status_push_left_image_exception` (Left Image Exception) | uint16 | mask:`0x80` |

## 0x30 — Eye Self Calibration

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x32 — Eye Easy Self Calib State

Payload decoder: `mbino_easy_self_calib_state_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_easy_self_calib_state_tink_count` (Tink Count) | uint8 |  |
  | 1 | 1 | `mbino_easy_self_calib_state_unknown01` (Unknown01) | uint8 |  |
  | 2 | 1 | `mbino_easy_self_calib_state_sensor_type` (Sensor Type) | uint8 | enum:`enums.MBINO_EASY_SELF_CALIB_STATE_VISION_SENSOR_TYPE_ENUM` |

## 0x37 — Eye QRCode Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x39 — Eye Vision Tip

Payload decoder: `mbino_vision_tip_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_vision_tip_a` (A) | uint8 |  |
  | 1 | 1 | `mbino_vision_tip_b` (B) | uint8 | enum:`enums.MBINO_VISION_TIP_B_TRACKING_TIP_TYPE_ENUM` |
  | 2 | 1 | `mbino_vision_tip_c` (C) | uint8 |  |
  | 3 | 1 | `mbino_vision_tip_d` (D) | uint8 |  |

## 0x3A — Eye Precise Landing Energy

Payload decoder: `mbino_precise_landing_energy_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_precise_landing_energy_enery` (Enery) | uint8 |  |

## 0x46 — Eye RC Packet

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x47 — Eye Set Buffer Config

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x48 — Eye Get Buffer Config

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA3 — Eye Enable SDK Func

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA4 — Eye Detection Msg Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xA5 — Eye Get SDK Func

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
