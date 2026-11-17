# Cmd Set 0x00 — General

Total known command IDs: 85

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

> **Binary investigation note (`0x07`-`0x0A`, `0x40`/`0x41`/`0x43`):** this
> project specifically searched the real WM260/Mavic 3 firmware for these
> 7 commands' dispatch logic — `Enter Loader`/`Update Confirm`/
> `Update Transmit`/`Update Finish` (`0x07`-`0x0A`) and
> `Fw Update Desc Push`/`Fw Update Push Control`/`Fw Upgrade Finish`
> (`0x40`/`0x41`/`0x43`) — on the **receive/handler** side (`dji_sys`,
> `libduml_frwk.so`, the 4-library upgrade plugin chain) and could not
> resolve it there. **Update (firmware-update-process sweep,
> `20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md`): 5 of these 7 —
> `0x07`/`0x08`/`0x09`/`0x0A`/`0x41` — are now independently confirmed
> live from the SENDER side.** DJI's own `test_upgrade` QA harness
> (E1E/ARM32) builds and sends exactly these 5 literal cmd_ids to
> `dji_sys` (module address `0x0801`) via `duss_event_send_sync`, in
> `check_fw_entry`/`check_fw_start`/`check_fw_transmit`/`check_fw_finish`/
> `check_update_control` respectively — confirming these are real, live
> DUML traffic, not dead/legacy surface, even though the *handler*-side
> dispatch inside `dji_sys` that receives them still hasn't been
> disassembled with confidence (that remains the open half of this gap).
> `0x40` and `0x43` remain fully unresolved on both sides. Original
> handler-side investigation: neither `libduml_frwk.so`'s one built-in
> dynamic-command table nor `dji_sys`'s 11 direct command registrations
> cover any of these cmd_ids, and a full disassembly of the
> firmware-upgrade daemon's entire 4-library plugin chain
> (`libupgrade_register.so` → `libupgrade_communication.so` →
> `libupgrade_commu_demo.so` → `libupgrade_upgrade.so`) found no
> cmd_id-matching dispatch logic with confidence — its event callback
> parses fixed struct-offset fields that don't look like a raw DUML cmd_id
> switch. This may be because the real handler lives in a `dlopen()`'d
> per-product plugin not present in this extraction, or because this is
> dead/legacy protocol surface the upgrade subsystem has moved away from
> (the upstream community Lua dissector's stubs for these same cmd_ids are
> also empty `TODO` placeholders, with no payload-format knowledge to
> borrow either). See `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track E for the
> original investigation.

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

> **Binary investigation note (`0x20`-`0x28`/`0x2A` file-transfer range):**
> this project confirmed the real underlying mechanism these commands'
> names describe: a shared `duss_file_trans_event`/`_req`/`_data`/
> `_checksum`/`_data_lost_list` module inside `libduml_frwk.so`, reused by
> 6 consumer daemons (`dji_sys`, `dji_perception`, `dji_blackbox`,
> `dji_config_store`, `dji_sec`, `libupgrade_commu_demo.so`). It's
> dispatched internally by a payload "phase" byte (matching the
> `phase == 1/2/3` branches decoded above for `0x2A`) rather than by a
> separate literal cmd_id per phase — so which exact cmd_id(s) in this
> range route into it *per daemon* could not be read off a literal
> register table (none exists; it's wired via a bus-client callback-struct
> field, an `R_ARM_ABS32` relocation, not the literal-immediate pattern
> used elsewhere in this firmware). The `0x24`/`0x2A` names/payloads above
> are independently confirmed by a field-for-field match against this
> real handler. The confirmed `duss_file_trans_req` "start transfer" path
> (phase=1) builds its destination path from a per-daemon fixed base
> directory plus a wire-supplied filename, with **no authentication/
> authorization check of any kind** on who may initiate a transfer — see
> `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track E for the full security-relevant
> findings (including a corrected, bounded single-hop `".."` path-traversal
> primitive, and a refuted unbounded-`fallocate()` DoS claim).

## 0x2F — Trans Diag Event

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware._

- **Handler:** `duss_trans_diag_event`
- **Purpose:** a transport/transfer diagnostics event — most plausibly
  reports or queries status/error information about an in-progress bus
  transfer (consistent with the "Trans Diag" name and its numeric
  adjacency to the `0x20`-`0x2A` file-transfer range above), though the
  handler's own logic was not disassembled, only its registration.
- **Evidence:** found via the literal-cmd_set-then-cmd_id-immediate
  pattern immediately preceding a `bl` to
  `duss_event_register_dynamic_command`, confirmed in `libduml_frwk.so`'s
  built-in dynamic-command table.
- **Confidence:** high on the `(cmd_set, cmd_id)` to handler mapping.
  See `04_WM260_DAEMON_FINDINGS.md`.

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

## 0x5B — FTP Control (Start/Stop)

_Not from the public dissector — found by this project's own binary RE._
No byte-level payload decoder recovered yet; only the cmd_id itself is
confirmed. Found in DJI's own `test_upgrade` QA harness (E1E/ARM32):
`check_ftpd_start_control`/`check_ftpd_stop_control` both build a DUML
request with cmd_id literal `0x5B` targeting `dji_sys` (module address
`0x0801`) via `duss_event_send_sync`, differing only in a flag byte at
request-struct offset `0x14` (`1` for start, `0`/unset for stop). 3/3
adversarial reverify, independently re-derived from raw ELF bytes by all
three skeptics. See `20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md`. Not a
conflict with the unrelated `0x02`/`0x5B` ("Discon State Get", Camera) —
different cmd_set namespace.

## 0x5C — UAV Fly Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x60 — Auto Test Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x61 — Set Product Newest Ver

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x62 — Get Product Newest Ver

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x83 — External Upgrade Request

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware._

- **Handler:** `send_fn` (generic upgrade-center message-send wrapper) →
  `duss_event_send_sync` (imported from `libduml_frwk.so`).
- **Purpose:** issues an "external upgrade" request to the on-device
  "upgrade center" service — triggered by the `upgrade_test` CLI tool's
  `external_upgrade` subcommand, which installs a firmware package from
  an operator-supplied path rather than the normal OTA flow.
- **Evidence:** literal `mov w9, #0x83` immediately before a call to the
  shared `send_fn` wrapper, found in `upgrade_test` (both the E1E/ARM32
  and E2/aarch64 builds, at different addresses per architecture but an
  identical immediate-then-call pattern); the call path is reached only
  from the code handling the `external_upgrade_test_client` CLI
  subcommand. `cmd_set=0x00` is inferred by this project's established
  "General" convention for the upgrade-center channel (consistent with
  already-catalogued `0x41`/`0x4f`), not a directly observed wire byte.
- **Confidence:** high on the `(cmd_set, cmd_id)` pair and call site;
  medium on the semantic "external upgrade package install" purpose
  (drawn from the CLI subcommand name, not the handler's internal logic).
  See `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.

## 0x85 — Transfer Complete Notification

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware._

- **Handler:** `send_fn` (generic upgrade-center message-send wrapper) →
  `duss_event_send_sync` (imported from `libduml_frwk.so`).
- **Purpose:** notifies the upgrade-center service that a firmware
  package transfer has completed, confirmed by this call site's own
  adjacent log string: `"up_center: send transfer complete message,
  len = %d, timeout = %d"`.
- **Evidence:** literal `mov w8, #0x85` immediately before the log call
  and the `send_fn` call, found in `upgrade_test` (E2/aarch64 build).
  `cmd_set=0x00` inferred by the same General-channel convention as
  `0x83` above.
- **Confidence:** high on the `(cmd_set, cmd_id)` pair, call site, and
  purpose (the log string names the exact semantics). See
  `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.

## 0x89 — Shell Command

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware, with
notable security relevance._

- **Handler:** `duss_event_shell`
- **Purpose:** lets a DUML message invoke a shell command on the device.
  Confirmed by this handler's own embedded debug string, logged verbatim:
  `"SHELL: duss shell_command %s"` — i.e. the payload (or a field within
  it) is passed through to a shell-command execution path, not merely
  logged as text.
- **Evidence:** found via the literal-cmd_set-then-cmd_id-immediate
  pattern immediately preceding a `bl` to
  `duss_event_register_dynamic_command`, confirmed in `libduml_frwk.so`'s
  built-in dynamic-command table (shared by every daemon that links this
  library, not opted into per-daemon).
- **Confidence:** high on the `(cmd_set, cmd_id)` to handler mapping and
  on the debug-string evidence that it reaches a shell-command path.
  **Not determined / explicitly out of scope for this project:** whether
  this command is reachable from outside the device without prior root/
  ADB access, what authentication (if any) gates it, and the exact
  argument-passing/escaping mechanism — consistent with this project's
  standing no-exploit-recipe boundary, this is reported as an architectural
  fact (the command exists and is wired to a shell-exec path), not
  investigated or demonstrated as a usable attack. See
  `04_WM260_DAEMON_FINDINGS.md`.

## 0x93 — Begin Single Module Upgrade

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware._

- **Handler:** `send_fn` (generic upgrade-center message-send wrapper) →
  `duss_event_send_sync` (imported from `libduml_frwk.so`).
- **Purpose:** begins a single-module firmware upgrade and, separately,
  sets upgrade flags — reached from two different code paths inside
  `upgrade_test`: one logging `"single_module_upgrading_test_entry"` /
  `"Will send msg:0x%x(%d bytes) require to upgrade center(0x%x) to
  begin single module upgrade!!!"`, the other from the CLI's
  `set_up_flags_request` subcommand (which sets the `UP_AB_BOTH` /
  `FORCE_UP_ALL` flags per its own `--help` text).
- **Evidence:** literal `mov w8, #0x93` immediately before 3 separate
  calls to the shared `send_fn` wrapper, found in `upgrade_test`
  (E2/aarch64 build). `cmd_set=0x00` inferred by the same General-channel
  convention as `0x83`/`0x85` above.
- **Confidence:** high on the `(cmd_set, cmd_id)` pair and call sites;
  medium on which of the two reached code paths is the "primary" purpose
  (both share the same cmd_id). See `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.

## 0x94 — Set Upgrade Flag

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware._

- **Handler:** `send_fn` (generic upgrade-center message-send wrapper,
  internally tagged `"client_send_with_ack"`) → `duss_event_send_sync`
  (imported from `libduml_frwk.so`).
- **Purpose:** sets an upgrade flag (paired with `0x93`'s query/set
  pattern for the `UP_AB_BOTH` / `FORCE_UP_ALL` CLI flags), with the
  sender explicitly waiting for an acknowledgement per the internal
  `send_fn` tag name.
- **Evidence:** literal `mov w8, #0x94` before 2 calls to `send_fn`,
  found in `upgrade_test` (E2/aarch64 build), in the same
  `set_up_flags_request` function as `0x93` above. `cmd_set=0x00`
  inferred by the same General-channel convention.
- **Confidence:** high on the `(cmd_set, cmd_id)` pair and call sites.
  See `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.

## 0xA3 — USB State Report

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware._

- **Handler:** `sys_wm260_usb_state_handle` (plus platform-variant siblings,
  the same registration convention as cmd_set `0x22`/`0x60`'s "Demo Mode
  Handle")
- **Purpose:** reports the device's USB connection/mode state (e.g.
  connected/disconnected, host vs. device/OTG mode) into the DUML bus —
  consistent with the "USB State Report" name and this project's separate
  confirmation of a real `sys_ac103_usb_otg`/`sys_wm162_usb_otg`-style USB
  OTG mode-set handler under cmd_set `0x06`/`0x3A`.
- **Evidence:** literal `cmd_set`/`cmd_id` immediates before
  `duss_event_register_dynamic_command`, inside `dji_sys`'s platform-init
  functions.
- **Confidence:** high on the `(cmd_set, cmd_id)` to handler mapping. See
  `04_WM260_DAEMON_FINDINGS.md`.

## 0xAA — Node Sniffer Request

_No byte-level payload decoder in source dissector (name-only / unparsed
payload) — but independently binary-confirmed live on this firmware._

- **Handler:** `duss_event_node_sniffer_req`
- **Purpose:** requests some form of DUML bus "node sniffer" — most
  plausibly a diagnostic/discovery query enumerating the devices/nodes
  currently present on the bus (consistent with the "Node Sniffer" name),
  though the handler's own logic was not disassembled, only its
  registration.
- **Evidence:** found in `libduml_frwk.so`'s built-in dynamic-command
  table (the same table that supplies cmd_set `0x51`/`0x05` "Route
  Switch" and this cmd_set's `0x2F`/`0x89` above) — registered
  automatically for every message-bus client, not opted into per-daemon.
- **Confidence:** high on the `(cmd_set, cmd_id)` to handler mapping. See
  `04_WM260_DAEMON_FINDINGS.md`.

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
