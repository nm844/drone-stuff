# Cmd Set 0x00 — General

Total known command IDs: 76

## 0x00 — Ping

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x01 — Version Inquiry

Payload decoder: `general_version_inquiry_dissector`

  *if (payload:len() >= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_version_inquiry_rq_unknown0` (RqUnknown0) | uint8 | Some kind of request type/flags? |

## 0x02 — Push Param Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x03 — Push Param Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x04 — Push Param Start

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x05 — Multi Param Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x06 — Multi Param Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x07 — Enter Loader

Payload decoder: `general_enter_loader_dissector`

## 0x08 — Update Confirm

Payload decoder: `general_update_confirm_dissector`

## 0x09 — Update Transmit

Payload decoder: `general_update_transmit_dissector`

## 0x0A — Update Finish

Payload decoder: `general_update_finish_dissector`

## 0x0B — Reboot Chip

Payload decoder: `general_reboot_chip_dissector`

  *if (payload:len() >= 6) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `general_reboot_chip_unknown0` (Unknown0) | uint16 |  |
  | 2 | 4 | `general_reboot_chip_sleep_time` (Reboot Sleep Time) | uint32 |  |

  *elseif (payload:len() >= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_reboot_chip_response` (Response) | uint8 | Non-zero if request was rejected |

## 0x0C — Get Device State

Payload decoder: `general_get_device_state_dissector`

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_get_device_state_status` (Status) | uint8 |  |
  | 1 | 1 | `general_get_device_state_unknown1` (Unknown1) | uint8 |  |
  | 2 | 4 | `general_get_device_state_state` (Device State) | uint32 |  |

## 0x0D — Set Device Version

Payload decoder: `general_set_device_version_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_set_device_version_unknown0` (Unknown0) | uint8 |  |
  | 1 | 4 | `general_set_device_version_hw_ver` (HW Version) | bytes |  |
  | 5 | 4 | `general_set_device_version_ldr_ver` (Loader Version) | bytes |  |
  | 9 | 4 | `general_set_device_version_app_ver` (App Version) | bytes |  |
  | 13 | 4 | `general_set_device_version_unk4_ver` (Unk4 Version) | bytes |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_set_device_version_status` (Status) | uint8 |  |
  | 1 | 1 | `general_set_device_version_flags1` (Flags1) | uint8 |  |
  | 2 | 16 | `general_set_device_version_unknown2` (Unknown2) | bytes |  |

## 0x0E — Heartbeat/Log Message

Payload decoder: `general_heartbeat_log_message_dissector`

  *if (payload:len() > 0) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_heartbeat_log_message_group` (Group) | uint8 |  |

## 0x0F — Upgrade Self Request

Payload decoder: `general_upgrade_self_request_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_upgrade_self_request_unknown0` (Unknown0) | uint8 |  |
  | 1 | 1 | `general_upgrade_self_request_unknown1` (Unknown1) | uint8 |  |

## 0x10 — Set SDK Std Msgs Frequency

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — File List

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x21 — File Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x22 — File Send

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x23 — File Receive

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x24 — File Sending

Payload decoder: `general_file_sending_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `general_file_sending_index` (Index) | int32 |  |
  | 4 | 495 | `general_file_sending_data` (Data) | bytes |  |

## 0x25 — File Segment Err

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x26 — FileTrans App 2 Camera

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x27 — FileTrans Camera 2 App

Payload decoder: `general_camera_file_dissector`

## 0x28 — FileTrans Delete

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2A — FileTrans General Trans

Payload decoder: `general_filetrans_general_trans_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_filetrans_general_trans_phase` (Transfer Phase) | uint8 | enum:`enums.COMMON_FILETRANS_GENERAL_TRANS_PHASE_ENUM` |

  *if phase == 1 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 4 | `general_filetrans_general_trans_datalen` (Total Length) | uint32 | File size in bytes |
  | 5 | 1 | `general_filetrans_general_trans_fname_len` (File Name Length) | uint8 |  |
  | 6 | fname_len | `general_filetrans_general_trans_fname` (File Name) | string |  |

  *elseif phase == 2 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 4 | `general_filetrans_general_trans_partno` (Part No) | uint32 |  |
  | 5 | data_len | `general_filetrans_general_trans_data` (Data) | bytes |  |

  *elseif phase == 3 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 16 | `general_filetrans_general_trans_unknown1` (Unknown1) | bytes | After file transfer |

## 0x30 — Encrypt Config

Payload decoder: `general_encrypt_config_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_encrypt_config_cmd_type` (Cmd Type) | uint8 | enum:`enums.COMMON_ENCRYPT_CONFIG_CMD_TYPE_ENUM` |

  *elseif cmd_type == 3 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `general_encrypt_config_oper_type` (Oper Type) | uint8 | enum:`enums.COMMON_ENCRYPT_CONFIG_OPER_TYPE_ENUM` |
  | 2 | 8 | `general_encrypt_config_magic` (Magic value) | bytes | Should be `F0 BD E3 06 81 3E 85 CB` |
  | 10 | 1 | `general_encrypt_config_mod_type` (Module Type) | uint8 | Type of the module; selects encryption key to use; Camera supports keys 1 |
  | 11 | 10 | `general_encrypt_config_board_sn` (Board SN) | bytes | Factory Serial Number of the Board |
  | 21 | 32 | `general_encrypt_config_key` (Encrypt Key) | bytes | New AES encryption key |
  | 53 | 16 | `general_encrypt_config_secure_num` (Security Num) | bytes | MD5 of Board SN and Encrypt Key |

  *elseif cmd_type == 4 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `general_encrypt_config_mod_type` (Module Type) | uint8 | Type of the module; selects encryption key to use; Camera supports keys 1 |
  | 2 | 32 | `general_encrypt_config_buf_data` (Buffer data) | bytes |  |

## 0x32 — Activate Config

Payload decoder: `general_activation_actn_dissector`

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_activation_actn_action` (Action) | uint8 |  |
  | 1 | 1 | `general_activation_actn_state` (State) | uint8 |  |

  *if (payload:len() >= 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 9 | 7 | `general_activation_actn_ts` (Timestamp) | bytes |  |
  | 9 | 1 | `general_activation_actn_mc_serial_len` (MC Serial length) | uint8 |  |

## 0x33 — MFi Cert

Payload decoder: `general_mfi_cert_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_mfi_cert_cmd_type` (Cmd Type) | uint8 | enum:`enums.COMMON_MFI_CERT_CMD_TYPE_ENUM`; 'Made For iPod' concerns Apple devices only. |

  *if cmd_type == 1 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `general_mfi_cert_part_sn` (Part SN) | uint8 | Selects which 128-byte part of certificate to return |

## 0x34 — Safe Communication

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x40 — Fw Update Desc Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x41 — Fw Update Push Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x42 — Fw Upgrade Push Status

Payload decoder: `general_common_upgrade_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_common_upgrade_status_upgrade_state` (Upgrade State) | uint8 | enum:`enums.COMMON_UPGRADE_STATUS_UPGRADE_STATE_ENUM` |

  *if upgrade_state == 2 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `general_common_upgrade_status_user_time` (User Time) | uint8 | For upgrade_state==2 |
  | 2 | 1 | `general_common_upgrade_status_user_reserve` (User Reserve) | uint8 | For upgrade_state==2 |

  *elseif upgrade_state == 3 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `general_common_upgrade_status_upgrade_process` (Upgrade Process) | uint8 | For upgrade_state==3 |
  | 2 | 1 | `general_common_upgrade_status_cur_upgrade_index` (Cur Upgrade Index) | uint8 | mask:`0xe0`; For upgrade_state==3 |
  | 2 | 1 | `general_common_upgrade_status_upgrade_times_3` (Upgrade Times) | uint8 | mask:`0x1f`; For upgrade_state==3 |

  *elseif upgrade_state == 4 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `general_common_upgrade_status_upgrade_result` (Upgrade Result) | uint8 | enum:`enums.COMMON_UPGRADE_STATUS_UPGRADE_COMPLETE_REASON_ENUM`; For upgrade_state==4 |
  | 2 | 1 | `general_common_upgrade_status_upgrade_times_4` (Upgrade Times) | uint8 | For upgrade_state==4 |

## 0x43 — Fw Upgrade Finish

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x45 — Sleep Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x46 — Shutdown Notification

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x47 — Power State

Payload decoder: `general_power_state_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_power_state_a` (A) | uint8 | TODO values from enum P3.DataNotifyDisconnect |
  | 1 | 2 | `general_power_state_b` (B) | uint16 |  |

## 0x48 — LED Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4A — Set Date/Time

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4B — Get Date/Time

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4C — Get Module Sys Status

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4D — Set RT

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4E — Get RT

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x4F — Get Cfg File

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x50 — Set Serial Number

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x51 — Get Serial Number

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x52 — Set Gps Push Config

Payload decoder: `general_set_gps_push_config_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_set_gps_push_config_is_start` (Is Start) | uint8 |  |
  | 1 | 4 | `general_set_gps_push_config_get_push_interval` (Get Push Interval) | uint32 |  |

## 0x53 — Push Gps Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x54 — Get Temperature Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x55 — Get Alive Time

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x56 — Over Temperature

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x57 — Send Network Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x58 — Time Sync

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x59 — Test Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x5A — Play Sound

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x5C — UAV Fly Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x60 — Auto Test Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x61 — Set Product Newest Ver

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x62 — Get Product Newest Ver

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xEF — Send Reserved Key

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF0 — Log Push

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF1 — Component Self Test State

Payload decoder: `general_compn_state_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `general_compn_state_current_state` (Current state) | uint32 |  |

  *if sender == 0x09 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `general_compn_state_ofdm_curr_state_fpga_boot` (E FPGA Boot error) | uint32 | mask:`0x01`; Error in FPGA boot state |
  | 0 | 4 | `general_compn_state_ofdm_curr_state_fpga_conf` (E FPGA Config error) | uint32 | mask:`0x02` |
  | 0 | 4 | `general_compn_state_ofdm_curr_state_exec_fail1` (E Exec fail 1) | uint32 | mask:`0x04`; Meaning uncertain |
  | 0 | 4 | `general_compn_state_ofdm_curr_state_exec_fail2` (E Exec fail 2) | uint32 | mask:`0x08`; Meaning uncertain |
  | 0 | 4 | `general_compn_state_ofdm_curr_state_ver_match` (E RC vs OFDM version mismatch?) | uint32 | mask:`0x20`; Meaning uncertain |
  | 0 | 4 | `general_compn_state_ofdm_curr_state_tcx_reg` (E Transciever Register error) | uint32 | mask:`0x40`; Error in either ad9363 reg 0x17 or ar8003 reg 0x7C |
  | 0 | 4 | `general_compn_state_ofdm_curr_state_rx_bad_crc` (E Received data CRC fail) | uint32 | mask:`0x400`; Meaning uncertain |
  | 0 | 4 | `general_compn_state_ofdm_curr_state_rx_bad_seq` (E Received data sequence fail) | uint32 | mask:`0x800`; Meaning uncertain |

## 0xF2 — Log Control Global

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF3 — Log Control Module

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF4 — Test Start

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF5 — Test Stop

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF6 — Test Query Result

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF7 — Push Test Result

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF8 — Get Metadata

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFA — Log Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFB — Selftest State

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFC — Selftest State Count

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFD — Dump Frame Buffer

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFE — Self Define

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xFF — Query Device Info

Payload decoder: `general_query_device_info_dissector`

---

## Appendix: additional structs from `comm_mkdupc.py` (not in the Lua dissector)

These are ctypes `LittleEndianStructure` payload definitions from
`dji-firmware-tools/comm_mkdupc.py`, which documents some payloads the Lua
Wireshark dissector does not decode in detail. All offsets below are
relative to the start of the DUML payload (frame byte 11).

### 0x01 — Version Inquiry — Response: `DJIPayload_General_VersionInquiryRe`
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | unknown0 | uint8 |
| 1 | 1 | unknown1 | uint8 |
| 2 | 16 | hw_version | char[16] |
| 18 | 4 | ldr_version | uint32 |
| 22 | 4 | app_version | uint32 |
| 26 | 4 | unknown1A | uint32 |
| 30 | 1 | unknown1E | uint8 |

### 0x0B — Reboot Chip — Response: `DJIPayload_General_ChipRebootRe`
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | status | uint8 |

### 0x30 — Encrypt — Request variants (selected by `command` byte)
`command` values: 1=GetChipState, 2=GetModuleState, 3=Config, 4=DoEncrypt

**GetChipState/GetModuleState Rq** (`DJIPayload_General_EncryptGetStateRq`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | command | uint8 |

**Config Rq, single-module variant** (`DJIPayload_General_EncryptConfigRq`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | command | uint8 |
| 1 | 1 | oper_type | uint8 (0=WriteTarget, 1=WriteSH204, 2=WriteAll) |
| 2 | 8 | config_magic | uint8[8] |
| 10 | 1 | mod_type | uint8 |
| 11 | 10 | board_sn | uint8[10] |
| 21 | 32 | key | uint8[32] |
| 53 | 16 | secure_num | uint8[16] |

**Config Rq, 3-module variant** (`DJIPayload_General_EncryptConfig3Rq`) —
same as above but with `m01_*`/`m04_*`/`m08_*` triplicated (module types 01,
04, 08 configured in one request): command(1) + oper_type(1) + config_magic(8)
+ 3×[mod_type(1) + board_sn(10) + key(32) + secure_num(16)] = 2+8+3×59 = 187 bytes.

**DoEncrypt Rq** (`DJIPayload_General_EncryptDoEncryptRq`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | command | uint8 |
| 1 | 1 | mod_type | uint8 |
| 2 | 32 | data | uint8[32] |

**GetChipState Response** (`DJIPayload_General_EncryptGetChipStateRe`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | status | uint8 |
| 1 | 1 | state_flags | uint8 |
| 2 | 10 | m01_boardsn | uint8[10] |
| 12 | 10 | m04_boardsn | uint8[10] |
| 22 | 10 | m08_boardsn | uint8[10] |

**GetModuleState Response** (`DJIPayload_General_EncryptGetModuleStateRe`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | status | uint8 |
| 1 | 1 | state_flags | uint8 |

**Config Response** (`DJIPayload_General_EncryptConfigRe`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | status | uint8 |

Note: cmd_id 0x30 under cmd_set General overlaps with the "binding/DJICare"
command IDs documented in `disasm/binding/ANALYSIS.md` for cmd_set values
seen inside `libamt_util.so`/`libdji_secure.so` — those use **different**
semantics gated behind the TEE (see that analysis for `dji_device_bind_verify_relationship_msg`=0x38,
`generate_djicare_binding_mac_msg`=0x31, `djicare_verify_binding_mac_msg`=0x32,
`rc_write_djicare_whitelist`=0x39). These command-ID numbers are TEE
Trusted-Application command IDs (an internal RPC layer, TEEC_InvokeCommand),
**not** DUML `cmd_id` values — do not confuse the two numeric spaces.
