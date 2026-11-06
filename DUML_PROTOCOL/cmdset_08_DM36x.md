# Cmd Set 0x08 — DM36x

Total known command IDs: 15

## 0x00 — DM36x Reserved

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x01 — DM36x Gnd Ctrl Info Send

Payload decoder: `dm36x_send_gnd_ctrl_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `dm36x_gnd_ctrl_info_param_id` (Param ID) | uint8 |  |
  | 1 | 1 | `dm36x_gnd_ctrl_info_param_len` (Param Len) | uint8 |  |
  | 2 | 1 | `dm36x_gnd_ctrl_info_param_val8` (Param 8-bit Val) | uint8 |  |

## 0x02 — DM36x Gnd Ctrl Info Recv

Payload decoder: `dm36x_recv_gnd_ctrl_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `dm36x_gnd_ctrl_info_param_id` (Param ID) | uint8 |  |

## 0x03 — DM36x UAV Ctrl Info Send

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — DM36x UAV Ctrl Info Recv

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — DM36x Gnd Stat Info Send

Payload decoder: `dm36x_send_gnd_stat_info_dissector`

## 0x06 — DM36x UAV Stat Info Send

Payload decoder: `dm36x_send_uav_stat_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 3 | `dm36x_uav_stat_info_unknown00` (Unknown00) | bytes |  |
  | 3 | 1 | `dm36x_uav_stat_info_disable_liveview` (Disable Liveview) | uint8 |  |
  | 4 | 1 | `dm36x_uav_stat_info_encode_mode` (Encode Mode) | uint8 |  |
  | 5 | 1 | `dm36x_uav_stat_info_dual_encode_mode_percentage` (Dual Encode Mode Percentage) | uint8 |  |

## 0x07 — DM36x Gnd Stat Info Recv

Payload decoder: `dm36x_recv_gnd_stat_info_dissector`

## 0x0E — DM36x App Connect Stat Get

Payload decoder: `dm36x_get_app_conn_stat_dissector`

## 0x0F — DM36x Recycle Vision Frame Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — DM36x Bitrate Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — DM36x Bitrate Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x30 — DM36x Foresight Showed Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x31 — DM36x Foresight Showed Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x60 — Active Track Camera Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
