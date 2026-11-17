# Cmd Set 0x08 — DM36x

Total known command IDs: 15

## 0x00 — DM36x Reserved

_Not decoded._ A "Reserved" cmd_id is, by DUML convention, a placeholder slot that was never assigned a real payload even on DM36x-equipped aircraft; the Lua dissector that this project imported already shows it name-only with no fields. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ On DM36x-era aircraft this would have been the air-side push of UAV control/encoder parameters (paired conceptually with the already-catalogued 0x01 "Gnd Ctrl Info Send"/0x02 "Gnd Ctrl Info Recv" in this same cmd_set) down to the ground DM36x decoder chip. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — DM36x UAV Ctrl Info Recv

_Not decoded._ The acknowledgement/echo counterpart to 0x03 in the legacy DM36x ground-control-info exchange (mirroring the existing 0x01 Send / 0x02 Recv pair already catalogued for the DM36x "Gnd Ctrl Info" side). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Would have told the DM36x encoder which decoded/displayed vision frame buffer(s) can be recycled back to the air unit's frame pool — a buffer-lifecycle management message typical of hardware video-encoder control protocols of that generation. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x20 — DM36x Bitrate Set

_Not decoded._ Would have set the DM36x H.264 encoder's target bitrate for the downlink video stream. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — DM36x Bitrate Get

_Not decoded._ Query counterpart to 0x20 — would have returned the DM36x encoder's current bitrate setting. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x30 — DM36x Foresight Showed Set

_Not decoded._ 'Foresight' commands on legacy DJI aircraft toggled a predictive/latency-compensation overlay in the liveview video path; this would have told the DM36x pipeline whether that overlay is currently being displayed to the user. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x31 — DM36x Foresight Showed Get

_Not decoded._ Query counterpart to 0x30 — would have returned whether the foresight/predictive overlay is currently shown. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x60 — Active Track Camera Set

_Not decoded._ Would have told the legacy DM36x vision/encoder pipeline which camera feed to use as the source for ActiveTrack subject-tracking cropping/processing. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
