# Cmd Set 0x07 — Wi-Fi

Total known command IDs: 64

## 0x00 — WiFi Reserved

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x01 — WiFi Ap Scan Results Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x02 — WiFi Ap Channel SNR Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — WiFi Ap Channel Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — WiFi Ap Channel Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — WiFi Ap Tx Pwr Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — WiFi Ap Tx Pwr Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x07 — WiFi Ap SSID Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x08 — WiFi Ap SSID Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x09 — WiFi Ap RSSI Push

Payload decoder: `wifi_ap_push_rssi_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_push_rssi_signal` (Signal) | uint8 |  |

## 0x0A — WiFi Ap Ant RSSI Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0B — WiFi Ap Mac Addr Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0C — WiFi Ap Mac Addr Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0D — WiFi Ap Passphrase Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0E — WiFi Ap Passphrase Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x0F — WiFi Ap Factory Reset

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x10 — WiFi Ap Band Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x11 — WiFi Ap Sta MAC Push

Payload decoder: `wifi_ap_push_sta_mac_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 6 | `wifi_ap_push_sta_mac_mac` (Mac) | ether |  |

## 0x12 — WiFi Ap Phy Param Get

Payload decoder: `wifi_ap_get_phy_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_get_phy_param_signal_status` (Signal Status) | uint8 | enum:`enums.WIFI_ELEC_SIGNAL_SIGNAL_STATUS_ENUM` |

## 0x13 — WiFi Ap Power Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x14 — WiFi Ap Calibrate

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x15 — WiFi Ap Wifi Restart

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x16 — WiFi Ap Selection Mode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x17 — WiFi Ap Selection Mode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x18 — WiFi Ap 18

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x19 — WiFi Ap 19

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1A — WiFi Ap 1A

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1B — WiFi Ap 1B

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1C — WiFi Ap 1C

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1D — WiFi Ap 1D

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1E — WiFi SSID Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x1F — WiFi Ap 1F

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — WiFi Ap Wifi Frequency Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — WiFi Ap Set Bw

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — WiFi Ap 22

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x23 — WiFi Ap 23

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x24 — WiFi Ap 24

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x25 — WiFi Ap 25

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x26 — WiFi Ap Realtime Acs

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x27 — WiFi Ap Manual Switch SDR

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x28 — WiFi Ap Channel List Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x29 — WiFi Ap Channel Noise/SNR Req

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2A — WiFi Ap Channel Noise/SNR Push

Payload decoder: `wifi_ap_push_chan_noise_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `wifi_ap_push_chan_noise_total` (Total) | uint32 |  |

## 0x2B — WiFi Ap Set Hw Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2C — Wifi Ap Code Rate Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2D — Wifi Ap Cur Code Rate Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2E — WiFi Ap Set Usr Pref

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2F — WiFi Ap Get Usr Pref

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x30 — WiFi Ap Set Country Code

Payload decoder: `wifi_ap_set_country_code_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `wifi_set_country_code_str1` (Region Str1) | string |  |
  | 4 | 4 | `wifi_set_country_code_str2` (Region Str2) | string |  |
  | 8 | 2 | `wifi_set_country_code_unkn8` (Unknown8) | uint16 |  |

## 0x31 — WiFi Ap Reset Freq

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x32 — WiFi Ap Del Country Code

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x33 — WiFi Ap Verify Cc

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x39 — WiFi Get Work Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3A — WiFi Set Work Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x3B — WiFi Config By Qrcode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x80 — WiFi Push Mac Stat

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x82 — WiFi Master/Slave Status Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x83 — WiFi Master/Slave AuthCode Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x84 — WiFi Scan Master List

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x85 — WiFi Connect Master With Id AuthCode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x89 — WiFi AuthCode Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x8B — WiFi MS Error Info Get/Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x91 — WiFi Rc Info Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x92 — WiFi Update Sw State

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._
