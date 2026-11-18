# Cmd Set 0x00 — General

Total known command IDs: 85

## 0x00 — Ping

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: duss_event_ping (vaddr 0x87d08, E1E/ARM32 build)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 0 | `echo_payload` (Echo payload (opaque)) | bytes | duss_event_ping is a 3-instruction trampoline: it reads the incoming event struct's length field (struct offset 0x10) and data pointer (struct offset 0x14) and tail-calls duss_event_resp_data_v2(ctx, len, data) with them unchanged. It never inspects or validates the payload at all -- whatever bytes the sender puts here are echoed back verbatim as the response. Length and content are entirely sender-defined; in practice this is used to carry a counter/timestamp for round-trip-time or liveness checks, exactly like ICMP ping, but the wire format itself has no fixed fields. |

**Worked example:**

- Request payload: `01 02 03 04`
  The app or RC sends dji_sys a 4-byte liveness/round-trip probe (here an arbitrary 32-bit sequence counter) to confirm the DUML link to the flight-controller's General module is alive and to measure latency. Any length/content would work identically since the handler never parses it.
- Response payload: `01 02 03 04`
  dji_sys's duss_event_ping handler echoes the exact same 4 bytes back unmodified -- this is a synchronous request/response exchange (duss_event_resp_data_v2 builds a real ack frame), not one-way.

## 0x01 — Version Inquiry

Payload decoder: `general_version_inquiry_dissector`

  *if (payload:len() >= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_version_inquiry_rq_unknown0` (RqUnknown0) | uint8 | Some kind of request type/flags? |

## 0x02 — Push Param Set

_Not decoded._ Checked, in order: (1) libduml_frwk.so's one built-in 6-entry dynamic-command table (duss_event_create_dynamic_cmd_tbl, vaddr 0x1098fc on E1E) -- fully dumped and decoded; its 6 entries are cmd_set/cmd_id {0x00/0x00, 0x00/0x2f, 0x00/0x89, 0x00/0xaa, 0x00/0xfa, 0x51/0x05}. None is 0x00/0x02-0x06. (2) dji_sys's direct, literal-immediate duss_event_register_dynamic_command call sites (11 total, confirmed by `blx 9bd0 <duss_event_register_dynamic_command@plt>` xrefs): 3x cmd_set 0x22/cmd_id 0x60 (Demo Mode, matches prior doc04 finding), 2x cmd_set 0x00/cmd_id 0xa3 (USB State Report, matches catalog), 2x cmd_set 0x06/cmd_id 0x3a, 1x cmd_set 0x04/cmd_id 0x69 -- none under cmd_set 0x00 match 0x02-0x06. (3) The remaining 2 of those 11 call sites (vaddr 0x2da62 and 0x70048 in dji_sys) are NOT literal-immediate: they loop over a runtime-populated table of {cmd_set, N cmd_ids, shared handler} sub-tables, reading cmd_set from a per-table field and cmd_id from array position -- architecturally exactly the shape the task describes for a generic cross-chip param bus. Traced the table pointer back to a lazily-initialized .bss global, which in turn traces to three custom ELF sections literally named `param_manager_local` (0xa8250, 56 bytes), `param_manager_buf_local` (0xa8288, 32 bytes) and `param_manager_remote` (0xa82a8, 12 bytes) in dji_sys -- strong confirmation a real 'Param Manager' subsystem exists and matches ~40 'PM:'-prefixed debug strings describing a hash-keyed named-parameter protocol with push-frequency subscriptions and remote get/set (e.g. 'PM:register remote param item err, name: %s, freq: %d', 'PM:recieved push remote param hash was not register, hash: %u', 'PM:request_remote_param_fix_send failed, freq: %d, ret: %d'). However: (a) param_manager_local on this specific image contains only one populated entry (name 'sysmode_param_block'), (b) I could not resolve which literal (cmd_set, cmd_id) values the data-driven loop registers for it (the loop itself derives them from table position/fields at runtime, not a literal I could read statically with confidence), and (c) repeated attempts to find the actual wire-payload-parsing function by cross-referencing the 'PM:' debug strings (both the standard PIC ldr+add-pc idiom and a direct absolute-pointer scan) found zero code xrefs within this pass's effort -- these strings appear to be reached through a call path this method could not resolve (possibly a shared format-string table indexed by id rather than per-callsite literal pool loads). I did not invent a field layout without this evidence. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x03 — Push Param Get

_Not decoded._ Same investigation as cmd_id 0x02 (Push Param Set) above -- these 5 commands (0x02-0x06) were searched together since they are the generic 'parameter bus' family. Not covered by libduml_frwk.so's 6-entry built-in table or any of dji_sys's 9 literal-immediate registrations. The 2 data-driven registration loops in dji_sys, and the dedicated `param_manager_local`/`param_manager_buf_local`/`param_manager_remote` ELF sections and ~40 'PM:' hash-keyed-parameter debug strings they correlate with, are the right architectural shape for this command but the specific (cmd_set, cmd_id)-to-handler binding and the wire-payload-parsing function for 'Get' specifically could not be resolved with the string-cross-reference methods available in this pass (see 0x02's entry for full detail). Not guessed. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — Push Param Start

_Not decoded._ Same investigation as cmd_id 0x02 (Push Param Set). Of all 5 commands in this family, 'Start' is the one the correlated debug strings speak to most directly ('PM:register remote param item err, name: %s, freq: %d', 'PM:register remote param done, name: %s, freq: %d, hash:%u(0x%x)', 'PM:request_remote_param_fix_send failed, freq: %d, ret: %d') -- strongly suggesting its real wire payload carries at minimum a parameter-name string (or its hash) and a push-frequency value, consistent with 'start pushing me this named parameter at rate X'. This is a plausible, evidence-aligned hypothesis, not a confirmed byte layout: I could not locate the actual function that reads these specific bytes off the wire (see 0x02's entry for the cross-referencing attempts that did not resolve), so no offsets/sizes can be stated with confidence. Flagged honestly rather than guessed. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x05 — Multi Param Set

_Not decoded._ Same investigation as cmd_id 0x02 (Push Param Set). The correlated debug strings ('PM:%s: write param failed, check hash:%u ret_hash:%u or retcode %d', 'PM:[%s]param can not be wrote,%s', 'PM:[%s]param is out of range,%s') show the underlying param-manager protocol writes parameters by a 32-bit name-hash plus a value, and that it supports batching language ('Multi'), but I could not trace a specific function parsing a wire payload for this literal cmd_id down to byte offsets within this pass's effort (same tooling gap described under 0x02). Not guessed. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x06 — Multi Param Get

_Not decoded._ Same investigation as cmd_id 0x02 (Push Param Set). Correlated debug strings ('PM:%s: read param failed, check hash:%u ret_hash:%u or retcode %d', 'PM:read remote param hash %u(0x%x) size err, read_size: %u, param_size: %u', 'PM:remote param not exist, hash: %u, name: %s ret= %d') confirm a hash-keyed read path exists in the same param-manager subsystem, but as with the other 4 commands in this family I could not pin the exact wire-level byte layout to a disassembled parsing function within this pass (see 0x02's entry). Not guessed. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x07 — Enter Loader

Payload decoder: `general_enter_loader_dissector`

## 0x08 — Update Confirm

Payload decoder: `general_update_confirm_dissector`

## 0x09 — Update Transmit

Payload decoder: `general_update_transmit_dissector` (names a dissector function but extracts no real fields — boilerplate/raw dump only).

_Binary RE note:_ Handler correctly identified (`check_fw_transmit`, sender-side, vaddr `0x3044`), but the proposed field-layout did not survive 3-way adversarial reverify — refuted, not just unfound; the receiving `dji_sys`-side parser was not independently located (same gap already flagged in this project's prior docs for `0x07`-`0x0A`). See `DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md` for full search methodology.

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

_Not decoded._ Checked all 4 known registration mechanisms with no match. (a) Literal-immediate scan: wrote a capstone-based scanner that resolves the PLT stub for duss_event_register_dynamic_command[_with_user_data] in an ELF, finds every bl/blx call site to it (Thumb mode with skipdata=True to survive embedded literal pools), and reads back the preceding literal r1(cmd_set)/r2(cmd_id) immediates. Ran it against dji_sys (E1E 32-bit: 11 real call sites recovered, matching and reproducing this project's already-known mappings for 0x22/0x60, 0x00/0xa3, 0x06/0x3a, 0x04/0x69 exactly -- validating the method) and again, independently, in AArch64 against dji_sys (E2: 12 call sites, same four known mappings reproduced). Then ran the same scanner over every 32-bit ELF in e1e_extracted/system_files/{bin,lib,xbin} (all daemons and shared libs, not just dji_sys). No call site anywhere registers cmd_set 0 / cmd_id 0x10. (b) libduml_frwk.so's one built-in 6-entry dynamic-command data table (vaddr 0x1098fc in E1E, independently re-decoded by hand from readelf -x .data this round) does not contain 0x10 either (its 6 entries are cmd_id 0x00, 0x2f, 0x89, 0xfa, 0xaa, and cmd_set 0x51/0x05). (c) dji_flight, dji_navigation and dji_autoflight (the plausible owners of an SDK telemetry-frequency command) import only duss_mb_create_route_table/duss_event_create_client -- they do not import duss_event_register_dynamic_command at all, so if 0x10 lives there it is wired through the string/route-tag-keyed mechanism in note (d), not a literal cmd_id. (d) In dji_sys (E1E) I found a previously-undocumented local helper at vaddr 0x6fff4 that loops over an externally-supplied table of {cmd_set:u16, cmd_id:u16, pad:u32} rows (stride 12 bytes) and calls duss_event_register_dynamic_command once per row, all sharing one fixed handler descriptor -- this is a batch-registration mechanism this project had not previously documented, and it is architecturally capable of covering 0x10. However I could not find any caller of this helper (a full skipdata-enabled scan of dji_sys's .text for bl/blx targeting 0x6fff4/0x6fff5 found zero hits, and a raw byte search for its address as a relocated function-pointer-table entry also found zero hits), so its actual table contents -- and therefore whether 0x10 is one of its rows -- could not be recovered. This is a concrete lead for a future pass, not a resolved finding. Given all of the above, I did not invent a payload layout. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Per the task hint, checked whether 0x20-0x28 share the already-partially-known cmd_set 0x00/0x2A 'FileTrans General Trans' transport. Confirmed by direct disassembly (both E1E armv7 and E2 aarch64 libduml_frwk.so -- addresses match 1:1 across builds) that duss_file_trans_event (E1E vaddr 0x8f515) is a tiny dispatcher that reads ONE byte from the incoming message at the same struct offset (+0x14) that this project's existing Lua dissector already uses as payload offset 0 ('Transfer Phase') for cmd 0x2A, and branches: phase 1 -> bl duss_file_trans_req (0x8d970, the already-documented 'start transfer' path), phase 2 -> bl duss_file_trans_data (0x8e155, matches the already-documented partno+data path), phase 3 -> bl duss_file_trans_checksum (0x8ef79, matches the already-documented 16-byte 'after transfer' path), phase 4 -> bl duss_file_trans_data_lost_list (0x8e661, a 4th phase NOT in the existing 0x2A dissector at all -- a new finding, semantically a good match for 'File Segment Err'/0x25, but see below). This re-confirms and extends the shared-module architecture, but does NOT by itself tell us which literal cmd_id(s) besides 0x2A route into it. I then checked all 6 daemons previously identified as consumers of this module (dji_sys, dji_perception, dji_blackbox, dji_config_store, dji_sec, libupgrade_commu_demo.so): every one of them imports duss_file_trans_event only via an R_ARM_ABS32 relocation landing in a .data struct field (confirmed exact relocated offsets in dji_sys: 0xa5e24, and in dji_blackbox: 0x3de70) that is consumed by duss_mb_create_route_table/duss_event_create_client -- the route-tag/string-keyed mechanism, not a literal register_dynamic_command(cmd_set,cmd_id,...) call. I disassembled dji_blackbox's duss_event_create_client call site (vaddr 0x5ffa) and duss_mb_create_route_table call site (0x5e64) directly: the fields populated into the route-table/client-config structs there are pointer-sized (string/pointer) values and small integers that are NOT DUML cmd_id bytes (e.g. literal ints 7 and 0x32 at specific struct offsets, plus several relocated pointers I could not confirm as readable C-strings in the time available). Ran the same full literal-immediate scanner from 0x10's entry across every 32-bit daemon/lib in the firmware (bin+lib+xbin) specifically for cmd_set 0/cmd_id in {0x20,0x21,0x22,0x23,0x25,0x26,0x28}: zero hits anywhere. This reconfirms, independently, this project's own prior conclusion in 14_FOLLOWUP_DEEPDIVE_FINDINGS.md Track E ('Not determined: the exact cmd_id(s) bound to duss_file_trans_event per consuming daemon') -- I was not able to go further than that prior pass on the specific cmd_id binding, despite a fresh, independent attempt. I did not invent a payload layout for 0x20 specifically; its name ('File List') is also the one in this batch I'd trust LEAST to actually be this same chunked-transfer state machine (a directory listing is a plausible, semantically distinct, simpler request/response that could have an entirely different handler I did not find). See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — File Info

_Not decoded._ Same investigation and same negative result as 0x20 (File List) -- see that entry for the full method (shared duss_file_trans_event module confirmed and its phase-dispatch re-derived by direct disassembly; all 6 consumer daemons confirmed to wire it only through the route-table/string-keyed mechanism, not a literal cmd_id; full-tree literal-immediate scan across both architectures found zero register_dynamic_command call sites for cmd_set 0/cmd_id 0x21 anywhere). 'File Info' (get metadata for a single file) also reads to me as plausibly a distinct, simpler request/response pair rather than literally the same multi-phase transfer state machine, but I have no binary evidence either way -- reported honestly as unresolved rather than guessed. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — File Send

_Not decoded._ Same investigation and same negative result as 0x20 -- see that entry for the full method. 'File Send' is the one name in this sub-batch I'd call MOST likely to literally be an alias that starts the generic duss_file_trans_req (phase=1) path documented for cmd 0x2A, since the semantics line up well ('begin sending a file' matches the already-known phase=1 payload: 1-byte phase + 4-byte total length + 1-byte filename length + filename string). But I found no literal register_dynamic_command(0x00, 0x22, ...) call site anywhere in the firmware (both architectures checked), and the route-table mechanism that actually wires this module in every consumer daemon I checked is string/pointer-keyed, not something I could statically resolve to a numeric cmd_id in the time available. I am not reporting a decoded layout because I have no binary evidence tying cmd_id 0x22 specifically to this handler -- only a plausible, unconfirmed architectural guess, which the task instructions say not to present as a finding. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x23 — File Receive

_Not decoded._ Same investigation and same negative result as 0x20/0x22 -- see those entries for the full method. 'File Receive' is the natural counterpart to 'File Send' and, if the naming pattern holds, might be the direction-reversed read-side of the same generic transfer module (or simply the request that triggers the daemon to start sending phase=1/2/3 frames the other way), but again I found zero literal register_dynamic_command(0x00, 0x23, ...) call sites anywhere in either architecture, and the actual wiring for every consumer daemon goes through the unresolved string-keyed route-table mechanism. Not reporting a layout I can't back with disassembly evidence. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x24 — File Sending

Payload decoder: `general_file_sending_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `general_file_sending_index` (Index) | int32 |  |
  | 4 | 495 | `general_file_sending_data` (Data) | bytes |  |

## 0x25 — File Segment Err

_Not decoded._ Same investigation and same negative result as 0x20 -- see that entry for the full method. This is the strongest circumstantial (but still unconfirmed) semantic match in the whole batch: while disassembling duss_file_trans_event's dispatcher this round, I found a 4th phase value (payload byte0==4) that the existing Lua dissector for cmd 0x2A does NOT document at all, which calls duss_file_trans_data_lost_list (E1E vaddr 0x8e661) -- a function whose own name is an exact semantic match for 'reporting which segments of a transfer were lost/need retransmission', i.e. 'File Segment Err'. I partially disassembled duss_file_trans_data_lost_list itself looking for a clean field layout (it is a much larger function, 0x754 bytes in E1E, that builds a retransmit-request list) but ran out of budget to fully resolve its byte-level fields with confidence in this pass, and -- critically -- I still have no evidence that cmd_id 0x25 (as opposed to 0x2A with phase=4, or some other cmd_id) is what's actually wired to trigger it; the literal-immediate scan across both architectures found zero register_dynamic_command(0x00, 0x25, ...) sites. Flagging this as the single best lead for a focused follow-up pass (disassemble duss_file_trans_data_lost_list's body specifically, and separately try to resolve the route-table string keys in dji_sys/dji_blackbox to confirm which cmd_id maps to phase=4), rather than reporting a guessed layout now. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x26 — FileTrans App 2 Camera

_Not decoded._ Same investigation and same negative result as 0x20 -- see that entry for the full method. This name (and 0x27's) reads like an older/legacy direction-specific alias from before the generic 0x2A 'General Trans' mechanism existed, plausibly routed to the same shared module, but I have zero binary evidence of the actual cmd_id-to-handler binding (zero literal register_dynamic_command(0x00, 0x26, ...) sites found in either architecture; the real wiring for every consumer daemon goes through the unresolved route-table mechanism described under 0x20). See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x27 — FileTrans Camera 2 App

Payload decoder: `general_camera_file_dissector` (names a dissector function but extracts no real fields — boilerplate/raw dump only).

_Binary RE note:_ Same investigation and same negative result as `0x20` — zero literal `register_dynamic_command(0x00, 0x27, ...)` call sites found anywhere in either architecture; the real wiring for the shared file-trans module in every consumer daemon checked goes through an unresolved route-table/string-keyed mechanism rather than a literal cmd_id. See `DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md` for full search methodology.

## 0x28 — FileTrans Delete

_Not decoded._ Same investigation and same negative result as 0x20 -- see that entry for the full method. 'Delete' is semantically the simplest of this whole sub-batch (plausibly just a filename string, maybe with a short status/flags prefix) and is the one I'd expect to be EASIEST to confirm if its handler were found, but I located no distinct 'delete a file' function in libduml_frwk.so's file-trans module (duss_file_trans_init/_req/_data/_checksum/_data_lost_list/_ack_event/_destory/_get_current_file_info/_set_path/_set_recv_param/_set_callback/_set_high_speed_mode/_get_high_speed_mode/_register_stream_unsign_callback -- the full exported symbol list of that module in both architectures -- none of these names is an obvious file-delete operation), and zero literal register_dynamic_command(0x00, 0x28, ...) call sites anywhere. It's plausible the real delete handler lives in a daemon-specific function outside libduml_frwk.so entirely (e.g. inside dji_config_store or dji_sys's own code, reached from the route-table dispatch) that I did not have budget to locate by other means. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ The file-transfer subsystem inside a daemon that owns an active file-transfer session (e.g. dji_sys's blackbox/upgrade transfer path) pushes a short, ordinary diagnostic status note after successfully writing one segment of an in-progress transfer -- routine telemetry, not an error report. Handler correctly identified (duss_trans_diag_event), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Name-matched a local function `sys_event_security_comm` at vaddr 0x41310 (8 bytes: `mov w0,#-0x3f3; ret` — an unconditional-error stub that never reads its arguments at all). Its address is taken via an R_AARCH64_RELATIVE relocation at .data offset 0xf1050, sitting in the same irregularly-strided region of relocated function pointers that also holds sys_event_set_date/sys_event_rtc_get_date/sys_event_power_manage_req (i.e. it IS part of dji_sys's General-command handler-context blob, not random data) — but I could not find the code that actually WALKS this region by cmd_id: a full linear disassembly of dji_sys's .text (both E2/AArch64 and E1E/ARM32-Thumb, using capstone with skipdata to survive embedded literal pools) found only 11-12 literal-immediate `duss_event_register_dynamic_command(client,cmd_set,cmd_id,ctx)` call sites total in each binary, all of which match ALREADY-documented commands (0x00/0xa3, 0x22/0x60, 0x06/0x3a, 0x04/0x69) — none of them is 0x34. I also chased what I first thought was an adjacent sub-dispatcher at 0x41318 (reads a payload byte, checks range 0x40-0x44) hoping it was 0x34- or fw-update-related, but its 'in-range' branch target (vaddr 0x837e0) resolves to the unrelated, clearly-named `clear_log_all_process` — so that code is almost certainly part of a Log-Control command (0xF2/0xF3/0xFA), not Safe Communication or the fw-update range, and I'm flagging that red herring explicitly so a future pass doesn't re-walk it. Net result: a plausible but unproven handler candidate, which — even if correctly attributed — contains no payload fields to decode (it unconditionally rejects before touching the message). See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x40 — Fw Update Desc Push

_Not decoded._ Per this project's own `20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md` (Track BF) and `cmdset_00_General.md`'s binary-investigation note, 0x40 and 0x43 were the two of the original 7-command fw-update gap that remained fully unresolved even after that dedicated sweep (0x07/0x08/0x09/0x0A/0x41 were at least confirmed sender-side). Per this round's explicit instruction to look harder at dji_sys's FULL register table directly rather than trust the prior search radius: I did a complete linear disassembly of dji_sys's entire .text section on BOTH architectures (E2/AArch64 via capstone CS_ARCH_ARM64; E1E/ARM32 via capstone CS_ARCH_ARM+CS_MODE_THUMB with skipdata=True to survive literal-pool desync — the default thumb decode silently stopped after ~240 bytes without that flag, which I caught and fixed), located the real PLT stub address for `duss_event_register_dynamic_command` on each architecture (computed from the ARM32 PLT's two-ADD GOT-relative addressing by hand since no disassembler resolves it directly), and enumerated EVERY `bl`/`blx` call site to that stub in the whole binary. Result: 12 call sites in E2, 11 in E1E, and in both cases every single one resolves (via the literal `mov w1,#cmd_set; mov w2,#cmd_id` immediates I decoded alongside it) to an ALREADY-documented command (0x00/0xa3, 0x22/0x60, 0x06/0x3a, 0x04/0x69) — none is 0x40. This rules out the direct/literal-immediate registration mechanism for 0x40 in dji_sys on both chips, which is strictly more thorough than the prior pass's stated search. It does not rule out a loop/table-driven registration (dji_sys has at least two such loops, e.g. `sys_command_agent_config`, that pull cmd_set/cmd_id from a runtime array rather than a literal immediate, which my scan cannot resolve without walking that array's actual runtime contents) — that remains a genuine, acknowledged gap, not a disproof. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x41 — Fw Update Push Control

_Not decoded._ This project's `20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md` already confirmed 0x41 is sent live from DJI's own `test_upgrade` QA harness (`check_update_control`, literal cmd_id 0x41 to dji_sys module 0x0801) but could not find the receiver-side handler inside dji_sys. I repeated the deeper check this round's instructions asked for (same full-.text literal-immediate `duss_event_register_dynamic_command` scan described under 0x40, covering every call site on both E1E/ARM32-Thumb and E2/AArch64) and again found none of the 11-12 total call sites uses cmd_id 0x41 — so the receiver side remains unresolved even after exhaustively checking the direct-registration table on both architectures. Same caveat as 0x40: a loop/table-driven registration path (dji_sys has at least 2 such generic bulk-registration loops) was not fully resolved and could still hold it. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Same situation and same additional verification effort as 0x40 (see that entry for the full methodology: complete linear disassembly of dji_sys .text on both architectures, full enumeration of literal-immediate `duss_event_register_dynamic_command` call sites, none matching 0x43). This project's prior sweep (doc 20) also left 0x43 fully unresolved on both the sender and receiver side, unlike 0x41 which at least has a confirmed sender. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x45 — Sleep Control

_Not decoded._ Found a large (0xcdc=3292-byte) exported function `sys_event_power_manage_req` whose address is relocated into the same General-command handler-context data region as the confirmed commands, and which DOES genuinely read the raw incoming DUML message directly: `ldrsb w8,[msg,#0x14]!` loads payload byte 0 as a signed byte; bits[7:6] are split off as a 2-bit tag (w23, used only in a diagnostic log call); the low 6 bits (`w8 & 0x3f`, range 0-13) are used as an index into a genuine compiled jump table (`adrp/ldrsw/br`) with 14 distinct case targets — i.e. this one wire message multiplexes at least 14 different power-related sub-actions (plausibly spanning sleep, wake, shutdown, standby, reboot-adjacent states, etc. together). I could not, in this pass, disassemble all 14 jump-table targets to determine which one (if any) specifically implements 'sleep' as opposed to the other 13 actions, nor confirm via a literal register() call or any other proof that this function is bound to cmd_id 0x45 specifically rather than 0x46, some other/shared cmd_id, or a cmd_set other than 0x00. Reporting the one byte-offset fact I AM confident of (payload byte 0 = {2-bit tag, 6-bit action enum 0-13}) here rather than under 'fields', since I can't attribute it confidently enough to call it decoded for 0x45 specifically. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x46 — Shutdown Notification

_Not decoded._ Identical finding and identical caveats to 0x45 above — the same 14-action `sys_event_power_manage_req` dispatcher is the only plausible lead I found for power-state-transition commands in dji_sys, and 'shutdown' is numerically adjacent to 'sleep' in the catalog, but I have no evidence tying either specific cmd_id to a specific one of the 14 jump-table branches, or indeed confirming this function is reachable via 0x45/0x46 rather than some other cmd_id/cmd_set. Not disassembling all 14 branches to look for a shutdown-specific one was a time-boxing decision this pass, not a dead end — flagging it for a follow-up with a larger time budget. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x47 — Power State

Payload decoder: `general_power_state_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_power_state_a` (A) | uint8 | TODO values from enum P3.DataNotifyDisconnect |
  | 1 | 2 | `general_power_state_b` (B) | uint16 |  |

## 0x48 — LED Control

_Not decoded._ Found `led_control_thread` (0x44960, 376 bytes), a real worker that reads a small heap-allocated struct: byte0=flags (bit1 checked), byte1=action enum (0, 1, or 2 — three distinct code paths with distinct log strings), byte2/byte3=two more parameter bytes used differently per action. Traced its only address-taking reference (found by scanning every ADRP+ADD pair in .text for one producing 0x44960) to a call site at 0x42738 that `malloc(5)`s this exact struct and fills it from an incoming DUML message's payload bytes 0-4 (`msg+0x14`..`msg+0x18`) before handing it to a queue/thread-post primitive — so the 5-byte payload-to-struct mapping itself is solid. The problem: that call site's containing symbol, per the recovered local symbol table, is `sys_event_auto_test_info` (0x426d0-0x42858) — i.e. the code that triggers the LED appears to live inside the handler for cmd 0x60 'Auto Test Info' (plausibly 'blink the LED as part of a hardware self-test'), not inside any function named for LED control, and I found no second, LED-dedicated handler function anywhere in dji_sys or libduml_frwk.so (checked both for any other 'led'/'light'/'indicator'-named symbol). So either 0x48 genuinely has no separate implementation in this daemon's General-command table, or its real handler is one of the loop/table-driven registrations my literal-immediate scan can't see. I'm not reporting 'decoded' for 0x48 because I can't honestly attribute this struct layout to cmd_id 0x48 specifically rather than 0x60. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4A — Set Date/Time

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: sys_event_set_date (request handler, builds/validates a struct tm and calls mktime()); sys_event_set_date_ack (logs the 1-byte ack payload when dji_sys itself receives a response)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `year` (Year) | uint16 | Full calendar year, little-endian (e.g. 2024, not years-since-1900). Rejected with error 0xFF if <= 2018. Converted internally to struct tm's tm_year via -1900. |
  | 2 | 1 | `month` (Month) | uint8 | Month, 1-12 (1=January). Converted internally to tm_mon via -1. |
  | 3 | 1 | `day` (Day) | uint8 | Day of month, 1-31 (struct tm's tm_mday, used as-is). |
  | 4 | 1 | `hour` (Hour) | uint8 | Hour, 0-23 (tm_hour). |
  | 5 | 1 | `minute` (Minute) | uint8 | Minute, 0-59 (tm_min). |
  | 6 | 1 | `second` (Second) | uint8 | Second, 0-59 (tm_sec). Bytes 0-6 together are assembled into a struct tm and passed to mktime(). |
  | 7 | 2 | `tz_offset_min` (Timezone Offset (minutes)) | int16 | Signed UTC offset in minutes, little-endian. Validated to lie in [-720, +720] (i.e. within ±12 hours) before use. |

**Worked example:**

- Request payload: `E8 07 06 0F 0E 1E 00 E0 01`
  The ground-station App sets the aircraft's system clock to 2024-06-15 14:30:00 local time at UTC+8 (DJI's home timezone), the kind of one-shot time sync that happens after a cold boot or GPS time-lock. year=2024(0x07E8 LE), month=6, day=0x0F(15), hour=0x0E(14), minute=0x1E(30), second=0x00, tz_offset_min=+480(0x01E0 LE, UTC+8).
- Response payload: `00`
  A single status byte, 0 = accepted (non-zero would indicate the handler rejected the request, e.g. year too old). This is the only payload byte sys_event_set_date_ack reads when logging an incoming ack; the handler itself replies via the generic duss_event_resp_err/ok primitives when it is dji_sys answering the original request, rather than building a multi-field response.

## 0x4B — Get Date/Time

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: sys_event_rtc_get_date (builds and sends the response from the live system clock); sys_event_get_date_ack (logs the response if dji_sys itself is the one receiving an ack)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `hour` (Hour) | uint8 | Response payload offset 0: current hour (tm_hour), 0-23. |
  | 1 | 1 | `minute` (Minute) | uint8 | Current minute (tm_min), 0-59. |
  | 2 | 1 | `second` (Second) | uint8 | Current second (tm_sec), 0-59. |
  | 3 | 1 | `year_low` (Year (low byte)) | uint8 | Low byte of the current full year (year & 0xFF). Split into two separate bytes rather than one little-endian uint16, unlike the Set-Date request's year field. |
  | 4 | 1 | `year_high` (Year (high byte)) | uint8 | High byte of the current full year (year >> 8). |
  | 5 | 1 | `month` (Month) | uint8 | Current month, 1-12 (tm_mon+1, already converted back to 1-based). |
  | 6 | 1 | `day` (Day) | uint8 | Current day of month (tm_mday), 1-31. |

**Worked example:**

- Request payload: ``
  Bare query: the ground-station App asks the aircraft what time it currently thinks it is (e.g. to display/annotate a flight log). No request-payload-reading code was found for this command, consistent with an effectively empty/zero-length request payload; receipt alone triggers gettimeofday()+localtime().
- Response payload: `0E 23 0A E8 07 06 0F`
  The aircraft replies with its current onboard clock: 14:35:10 on 2024-06-15 — hour=0x0E(14), minute=0x23(35), second=0x0A(10), year_low=0xE8, year_high=0x07 (2024), month=6, day=0x0F(15).

## 0x4C — Get Module Sys Status

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: sys_event_report_status`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `module_id` (Module ID (high nibble)) | uint8 | High 4 bits (mask 0xF0) of the single request payload byte. Named from context (this is the field logged separately from query_index in the handler's own debug print) — the actual module-ID enum/table was not found, so treat the name as descriptive rather than a confirmed enum. |
  | 0 | 1 | `query_index` (Query Index (low nibble)) | uint8 | Low 4 bits (mask 0x0F) of the same byte. Echoed back verbatim as the first byte of the response. |

**Worked example:**

- Request payload: `31`
  The App/RC asks dji_sys for the status of a specific onboard module — module_id=3 (high nibble), query_index=1 (low nibble), packed as 0x31 — the kind of periodic or on-demand 'how's this component doing' diagnostic poll a ground station might send for a health/status display.
- Response payload: `31 01 00 00 00`
  dji_sys echoes the same request byte (0x31) back as byte 0, followed by a 4-byte little-endian word that is a hardcoded literal 1 in this code path (plausibly a fixed 'query acknowledged/ok' result code, though this pass could not confirm it ever varies).

## 0x4D — Set RT

_Not decoded._ Unresolved. 'RT' most plausibly abbreviates a 'Real-Time'/clock or legacy flight-record-time concept from an earlier DJI product generation, superseded on this airframe by the already-confirmed, adjacent 0x4A/0x4B 'Set/Get Date Time' pair (which IS registered in the same table, immediately before this one) -- but this is speculation about the name only, not a traced finding. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4E — Get RT

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4F — Get Cfg File

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x50 — Set Serial Number

_Not decoded._ Notably, this command's sibling 0x51 'Get Serial Number' IS registered and fully decoded (see that entry: handler sys_event_get_serial_number at dji_sys E2 vaddr 0x3fb00, found via table row 0xf0b70+0x51*0x18=0xf1308). The corresponding 0x50 row (0xf0b70+0x50*0x18=0xf12f0) is all-zero, i.e. dji_sys registers a getter for the hardware UUID/serial but no local setter. This is plausible on its face: sys_event_get_serial_number's type=5 branch reads the UUID from the '/dev/block/by-name/env' NVRAM partition's 'uuid' key and auto-generates+persists one via uuid_generate_random() if absent -- a self-provisioning scheme that would have no ordinary need for a runtime 'Set' command on production units (write access to that value, if it exists at all, would more likely live in a factory/manufacturing-only tool rather than the always-running dji_sys daemon). Checked and ruled out: libduml_frwk.so's built-in table, all 12 literal register_dynamic_command call sites in dji_sys E2, and an nm -D sweep for 'set_serial'/'serial' symbol names across every binary in both firmware trees (the only hits were unrelated: OpenSSL/mbedTLS X.509 certificate-serial-number APIs in libcrypto.so/libdji_crypto_lib.so, and ICU string-serialization functions -- none are DUML handlers). E1E/ARM32 dji_sys could not be reliably cross-checked for the reasons given under 0x4D. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x51 — Get Serial Number

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: sys_event_get_serial_number (vaddr 0x3fb00)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `serial_type` (Serial Type Selector) | uint8 (enum) | Selects which value the 'Get Serial Number' request wants back. Read directly from byte 0 of the request payload (struct offset 0x14 in dji_sys's internal message representation). |

**Worked example:**

- Request payload: `05`
  A ground-station/RC app asks the aircraft's core system daemon (dji_sys) for its persistent hardware serial number/UUID -- e.g. to display in an 'About this aircraft' screen or to associate the airframe with a user account. serial_type=5 requests the hardware-UUID branch.
- Response payload: `10 00 4A 3F 8C 12 7D 9E 4E 01 84 4B B6 7A 3C 05 E8 91`
  A successful reply to a type=5 request: a 2-byte little-endian length field (0x0010 = 16), followed by the 16 raw bytes of the aircraft's persistent UUID/serial identifier (an ordinary, representative placeholder value here -- the real one is read from, or generated once and stored into, the '/dev/block/by-name/env' NVRAM partition). Total response payload length 18 bytes.

## 0x52 — Set Gps Push Config

Payload decoder: `general_set_gps_push_config_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `general_set_gps_push_config_is_start` (Is Start) | uint8 |  |
  | 1 | 4 | `general_set_gps_push_config_get_push_interval` (Get Push Interval) | uint32 |  |

## 0x53 — Push Gps Info

_Not decoded._ dji_sys E2 dispatch-table row for cmd_id 0x53 (0xf0b70+0x53*0x18=0xf1338) is all-zero -- no local dji_sys handler for receiving this. This is expected for a command literally named 'Push': the task hint and the sibling 0x52 'Set Gps Push Config' (already decoded elsewhere in this project as general_set_gps_push_config_dissector, taking an is_start/push_interval pair) strongly suggest 0x53 is the resulting one-way PUSH *sent outward* by whichever daemon owns the GPS/positioning solution (most likely a flight-control daemon, not dji_sys), triggered by that config command -- i.e. dji_sys's absence from the inbound dispatch table is consistent with dji_sys not being the sender either. Searched for a plausible sender: nm -D sweep of both firmware trees for 'gps_info'/'gps' symbol names found no dedicated DUML-sending function; the one 'gps' hit (format_gps_information in libdcam_muxer.so, camera subsystem) formats GPS EXIF/metadata for recorded video, unrelated to the DUML bus. Did not have a specific flight-control daemon binary identified/available to search further within this batch's scope (this project's other docs point to a separate flight-control codebase for cmd_set 0x03 material, outside this General-cmd_set-focused pass). Ruled out libduml_frwk.so's built-in table and all 12 literal register_dynamic_command call sites in dji_sys E2 as the receiving mechanism. Could not determine the payload layout without locating the actual sender/handler. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x54 — Get Temperature Info

_Not decoded._ Found via the dispatch table (row 0x54 = 0xf0b70+0x54*0x18=0xf1350 -> fn=0x41e60). Confirmed by .gnu_debugdata symbol name sys_event_get_temp_info @ 0x41e60 and 5 embedded log/format strings: 'sys_event_get_temp_info' (0xa7aba), 'get_temp_info msg_len %d error' (0xa8938), 'get_temp_info not support this platform' (0xa8957), 'get_omc_handle failed' (0xa897f), and 'get_temp_info input msg error, %d should <= %d' (0xa8995). Disassembled the full body (vaddr 0x41e60-0x4209c): it first checks the incoming message's length field (struct offset 0x10) equals exactly 1, erroring otherwise ('get_temp_info msg_len %d error', resp code 0xff). It then requires the platform's power-module identity string (compared via strncmp against a constant read as 'PM430S AC') to match, erroring 'get_temp_info not support this platform' otherwise -- i.e. this handler only functions on hardware carrying that specific power module. It then calls sys_omc_get_this_board_handle() and sys_omc_get_temp() (both confirmed by symbol name) to obtain/refresh a per-channel sensor-data structure. It then reads the single payload byte at struct offset 0x14 (same payload-start convention validated for 0x51/0x5B) as a channel index, rejecting values >= 6 ('get_temp_info input msg error, %d should <= %d', resp code 0xff). For index 5 it reads one raw byte directly from the board-handle struct at offset 0x55; for indices 0-4 it reads a 32-bit float from the struct at offset (index*4)+0x40 and truncates it to a signed integer. Either way the resulting integer is multiplied by 10 (via add+shift: x+x*4, then <<1) and returned as a 16-bit value through duss_event_resp_data(), response length fixed at 2 bytes. Which physical sensor each index 0-4 corresponds to (battery/ESC/board/etc.) could not be determined from this function alone -- the surrounding 'temperature_group'/'omc' subsystem in this binary tracks many named channels (esc_temperature_group, bat_temperature_group, cb_temperature_group, and about a dozen more, per embedded JSON-config-key strings), but this specific 6-slot board-handle array was not traced to that naming scheme with confidence, so the index is reported generically rather than guessed. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x55 — Get Alive Time

_Not decoded._ dji_sys E2 dispatch-table row for cmd_id 0x55 (0xf0b70+0x55*0x18=0xf1368) is all-zero. Also specifically checked the one plausible same-sounding function found in dji_sys, get_boot_time_us (symbol-confirmed @ 0x8a440): it has exactly one caller in the whole binary, inside an unrelated periodic process-CPU-load-percentage computation (dividing an elapsed-boot-time delta to compute load%), with no connection traced to any duss_event_register_dynamic_command call or to the dispatch table -- so it was explicitly ruled OUT as this command's handler rather than assumed. Also ruled out: android::uptimeMillis() (present in libutils.so/libbinder.so/libhwbinder.so as a generic Android SDK symbol used system-wide, not DUML-specific), libduml_frwk.so's built-in table, and all 12 literal register_dynamic_command call sites in dji_sys E2. A broader nm -D sweep for 'alive'/'uptime'/'boot_time'/'run_time' across every binary in both firmware trees found nothing else plausibly tied to a DUML command. E1E/ARM32 dji_sys could not be reliably cross-checked for the reasons given under 0x4D. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x56 — Over Temperature

_Not decoded._ dji_sys E2 dispatch-table row for cmd_id 0x56 (0xf0b70+0x56*0x18=0xf1380) is all-zero -- no INBOUND handler in dji_sys. Given the name ('Over Temperature'), this is plausibly a one-way PUSH sent outward when a thermal threshold is exceeded, not a request dji_sys receives -- consistent with its absence from the inbound-dispatch table. dji_sys does contain an extensive, clearly-related 'temperature_group'/OMC subsystem (sys_omc_*, plus temperature_group_pack_status/pack_temperature/pack_status_version1/pack_temperature_version1, temperature_group_v1_send_status, temperature_group_v1_send_temperature, update_temperature_group_threshold, detect_temp_exception, temp_group_exception_log -- all symbol-confirmed) that builds and transmits multi-channel temperature/fan-state messages via duss_event_send()/duss_event_send_sync() (confirmed by embedded strings 'duss_event_send() send temperature error=%d' and 'duss_event_send_sync() temp_status error=%d'), and an exception-level/threshold-crossing code path (detect_temp_exception, 'exception temperature level:%d', 'current exception temp level=%d, then notify sysmode') that is a strong structural match for an 'Over Temperature' notification. However, disassembling temperature_group_v1_send_temperature showed it calls duss_event_send() through a generic internal message-envelope wrapper (a fixed internal message-type constant 0x44 was found at the call site, which is this wrapper's own internal tag, not a confirmed DUML cmd_set/cmd_id) -- tracing that wrapper far enough to recover the literal DUML cmd_set/cmd_id byte(s) it ultimately emits on the wire, and the exact byte layout of the temperature_group_pack_temperature/pack_status payload, was not completed within this pass's time budget. This is therefore a strong lead, not a confirmed decode: reporting insufficient_evidence rather than asserting a layout built on an unconfirmed cmd_id match. Also ruled out libduml_frwk.so's built-in table and all 12 literal register_dynamic_command call sites in dji_sys E2. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x57 — Send Network Info

_Not decoded._ dji_sys E2 dispatch-table row for cmd_id 0x57 (0xf0b70+0x57*0x18=0xf1398) is all-zero. Specifically checked the one binary in either firmware tree whose name directly suggests this theme -- bin/dji_network (present in both e1e_extracted and e2_extracted) -- including extracting its own .gnu_debugdata symbol table (250 symbols) and inspecting its DUML registration mechanism (it imports duss_mb_create_route_table + duss_event_create_client, i.e. route-tag addressing, not direct duss_event_register_dynamic_command). Its full exported-function list was reviewed; it is exclusively a WiFi/Bluetooth radio-link daemon (hostapd control, channel/country/SSID/passwd config, BT BSA test harness, acs_get_best_channel, etc.) with no symbol resembling 'network_info' or any DUML General-cmd_set handler -- ruled out as the handler for this command. Ruled out libduml_frwk.so's built-in table and all 12 literal register_dynamic_command call sites in dji_sys E2. A broader nm -D sweep for 'network_info'/'send_network'/'net_info' across every binary in both firmware trees found no match anywhere. E1E/ARM32 dji_sys could not be reliably cross-checked for the reasons given under 0x4D. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x58 — Time Sync

_Not decoded._ No handler for cmd_set 0x00/cmd_id 0x58 could be located by any of this project's four known registration mechanisms. Concretely: (1) exhaustively enumerated every literal-immediate duss_event_register_dynamic_command call site in dji_sys on BOTH architectures (11 call sites in e1e/ARM32 Thumb at vaddr range 0x2db80-0x70064, 12 in e2/aarch64 at 0x2db80-0x96f8c, cross-checked register-argument values programmatically) -- none registers cmd_set=0 with cmd_id=0x58; the only cmd_set=0 literal registration found anywhere is cmd_id 0xa3 (already-known USB State Report). (2) dji_sys (e2/aarch64) also contains a 256-slot array, directly indexed by single-byte cmd_id, of {primary_handler_fn, secondary/ack_fn, flag} 24-byte records for cmd_set 0x00 (confirmed real by independently re-deriving 3 already-documented cmd_ids from it: 0x54='Get Temperature Info' -> sys_event_get_temp_info, exact name match to this project's existing doc; 0x5B='FTP Control' -> sys_event_ftpd_control, matches this project's doc20 finding; 0x60='Auto Test Info' -> sys_event_auto_test_info, see that entry below). Array base resolved as vaddr 0xF0B70, stride 24 bytes (so slot(cmd_id) = 0xF0B70 + cmd_id*24). The slot for cmd_id 0x58 (vaddr 0xF13B0-0xF13C7) is entirely zero -- no handler of any kind registered there. (3) Separately, dji_sys DOES contain real, confirmed time-sync machinery (sys_event_set_sync_delta_time, sys_event_sync_time, sys_event_simple_sync_time), but these sit at cmd_ids 0x67, 0x68, and 0x73 respectively in the SAME indexed array -- not 0x58. This is corroborated by an adjacent log string literally reading 'ENTRY: send timesync msg(0x68): index = %d, global timeus = %llu'. This strongly suggests the dissector's 'Time Sync' label on cmd_id 0x58 does not correspond to dji_sys's real on-wire time-sync traffic, which runs on 0x68 instead; 0x58 may belong to a different/legacy mechanism or an as-yet-unexamined daemon. (4) Checked all 6 other binaries across both trees that even import duss_event_register_dynamic_command (libMipiHandshake.so, libWorkModeLiveview.so, dji_sdrs_agent, test_rtos_raw, libdcam_event_client_pool.so, duml_googletest) -- all are camera/MIPI-pipeline or test-harness code, none plausibly General-cmd_set time-sync owners, and none referenced 'time_sync'-style strings beyond dji_sys itself. (5) Also scanned dji_sys's 125 call sites to duss_event_send/duss_event_send_sync/duss_event_send_self (e2/aarch64) for a literal #0x58 cmd_id argument (in case 0x58 is a device->app PUSH rather than an app->device request) -- none found (the only literal hex values matching our target bytes that turned up, #0x5a and #0x62, were independently confirmed to be unrelated internal log-module tag constants, not cmd_ids, by inspecting their call context). Not pursued further in this pass: the e1e/ARM32 build's own copy of the same 256-slot array (not located/decoded this round), and any RTOS-side (flight controller) time-sync protocol that might be the true counterpart of wire cmd_id 0x58. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x59 — Test Mode

_Not decoded._ A ground-station/companion app (or a factory test fixture) attempting to toggle the aircraft's internal engineering/self-test-mode flag before a diagnostic sequence -- the kind of boring, routine toggle this cmd_id's name suggests. Confirmed no meaningful payload. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x5A — Play Sound

_Not decoded._ The DJI Fly app (or RC) telling the aircraft to play its 'entering/exiting packing mode' audio cue, e.g. as part of the guided power-down/gimbal-lock packing sequence the app walks a pilot through before storing the drone. Handler correctly identified (sys_event_play_sound), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Same exhaustive checks described for 0x58 were applied here: all literal duss_event_register_dynamic_command call sites in dji_sys on both architectures (11 e1e/ARM32, 12 e2/aarch64, fully enumerated) -- none registers cmd_set=0/cmd_id=0x5C. dji_sys's 256-slot cmd_id-indexed request-handler array (base vaddr 0xF0B70, stride 24, validated against 3 independently-confirmed cmd_ids as described under 0x58) has an entirely-zero slot at cmd_id 0x5C (vaddr 0xF1410-0xF1427). This is consistent with 'UAV Fly Info' being a device->app PUSH/notification rather than something the app sends in for the device to parse (the array only ever holds request-side handlers; already-known push-type cmd_ids like 0x53 'Push Gps Info' are similarly all-zero in it). Tried to find the corresponding PUSH/encoder side: found a plausibly-named function `sys_eagle_check_uav_fly_status` (dji_sys e2/aarch64, vaddr 0x1be68) with one real caller (vaddr 0x51970), but disassembling that caller showed it is one small piece of a much larger, unrelated OSD/flight-status aggregation routine -- it never builds anything resembling a standalone cmd_set-0/cmd_id-0x5C DUML frame in the portion traced, and tracing it further to its actual destination packet was not completed in this pass. Also found unrelated same-named-concept strings ('radar_flightctrl_push_fly_info', 'PayloadActionRadarFlightCtrlPushFlyInfo') in dji_perception, but these are a distinct, perception-subsystem-internal 'push fly info' feature with no evidence connecting it to this specific DUML cmd_id. Also scanned dji_sys's 125 call sites to duss_event_send/duss_event_send_sync/duss_event_send_self for a literal #0x5c cmd_id argument (sender-side PUSH construction) -- none found. Not conclusively resolved either way. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x60 — Auto Test Info

_Not decoded._ A factory/production test fixture (DJI's own 'auto test' QA tooling) commanding a freshly-assembled aircraft to light its red recording-status LED solid, so an automated optical test rig (or a line operator) can visually confirm the LED driver hardware is soldered and functioning before the unit ships. Handler correctly identified (sys_event_auto_test_info (forwards, when the length check passes, into a thread entry this project is calling led_control_thread at vaddr 0x44960)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x61 — Set Product Newest Ver

_Not decoded._ Same methodology as 0x58/0x5C: all literal duss_event_register_dynamic_command call sites in dji_sys (both architectures, 11+12 sites, fully enumerated) -- no match for cmd_set=0/cmd_id=0x61. dji_sys's 256-slot cmd_id-indexed request-handler array (base 0xF0B70, stride 24, independently validated against 3 already-known cmd_ids) has an entirely-zero slot at cmd_id 0x61 (vaddr 0xF1488-0xF149F) -- no handler registered there either. Also string-searched dji_sys, dji_perception (both architectures), dji_cht, dji_cst, ss_dsp_manager, and dji_rcam for version-metadata-sounding identifiers ('newest_ver', 'product_version', and similar case-insensitive variants) -- no hits in any of them. Checked the same 6 binaries (beyond dji_sys) that import duss_event_register_dynamic_command at all -- none are plausibly related to product/version metadata by name or by any string found in them. Did not check the firmware-upgrade daemon's own 4-library plugin chain (libupgrade_register.so -> libupgrade_communication.so -> libupgrade_commu_demo.so -> libupgrade_upgrade.so) in this pass, which is the most plausible remaining owner of 'product version' metadata and was flagged by a prior pass of this project (14_FOLLOWUP_DEEPDIVE_FINDINGS.md, Track E) as containing no cmd_id-literal dispatch logic that pass's own analysis could resolve either, for a related but different set of cmd_ids (0x40-0x43) -- worth revisiting specifically for 0x61/0x62 by someone with more time budget, but not attempted here. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x62 — Get Product Newest Ver

_Not decoded._ Identical methodology and identical negative result to 0x61 (its Set/Get pair): no literal register_dynamic_command call for cmd_set=0/cmd_id=0x62 in dji_sys on either architecture; dji_sys's 256-slot cmd_id-indexed array's slot for cmd_id 0x62 (vaddr 0xF14A0-0xF14B7) is entirely zero. One extra check specific to this cmd_id: scanned all 125 call sites in dji_sys (e2/aarch64) to duss_event_send/duss_event_send_sync/duss_event_send_self for a literal `#0x62` cmd_id argument, in case this is answered by a device-initiated send rather than a registered receive handler. Two call sites did show a literal `mov w0, #0x62`, but tracing that function (vaddr ~0x70c84) showed it is an unrelated generic 'build-and-forward a message' helper that uses 0x62 purely as its own internal log-module tag constant (passed to duss_log_gen_head/duss_log_print), with the real cmd-type value supplied dynamically by its caller via a register argument, not as a literal -- a false positive, not a real sighting of cmd_id 0x62. No genuine handler or sender found. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x83 — External Upgrade Request

_Not decoded._ Confirmed (carried over from this project's prior pass, independently re-observed here): the literal `mov w9, #0x83` at vaddr 0x7d38 in upgrade_test/e2, reached from the code path handling the 'external_upgrade' CLI subcommand. This pass went further and traced what happens to that value: the surrounding function builds a large (~1040-byte) LOCAL staging buffer on its own stack, storing the 0x83 literal into that buffer at a fixed offset (sp+1020) alongside a handful of other locally-computed fields (a u16 from a config-getter call at sp+1016, a double-precision value around sp+1024, and several memset/zeroed regions) -- consistent with building a 'negotiate upgrade parameters' request. This pass located the actual shared send routine (a distinct function at vaddr 0x3ab8, confirmed by it containing the only 2 real calls to duss_event_send_sync/duss_event_send in the whole binary) and confirmed IT follows the same request-struct convention seen elsewhere in this project (length field at caller-struct offset +0x10, payload copied in via memcpy from offset +0x14). However, this pass could not conclusively connect the ~1040-byte local staging buffer built at the 0x83 call site to that +0x14 payload-copy source within the available effort budget -- it's architecturally plausible but not confirmed that some sub-range of that staging buffer becomes the actual wire bytes, versus the staging buffer being purely-local bookkeeping for the CLI tool with only a small, not-yet-identified subset of fields actually reaching the wire. Per this task's instructions, reporting this as insufficient_evidence rather than guessing a layout. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Confirmed (carried over from this project's prior pass, independently re-observed here): the literal `mov w8, #0x85` at vaddr 0x8960 in upgrade_test/e2, in a function built from the exact same template as the 0x83 one above (same ~1040-byte local staging buffer, cmd literal stored at the same sp+1020 offset, same config-getter call feeding sp+1016). This pass additionally found, in the immediately surrounding code, a literal constant 0x4C4B40 (5,000,000) loaded into a log-call argument register (w5) just before/after the cmd literal is stored -- plausibly the 'timeout' value from this project's already-known log string 'up_center: send transfer complete message, len = %d, timeout = %d' (5,000,000 would read naturally as a 5-second timeout expressed in microseconds), which would mean this command's logical payload carries at least a length field and a timeout field. However, as with 0x83, this pass could not conclusively trace which specific bytes of the local staging buffer (if any) actually become the transmitted wire payload within the available effort budget, so the exact offsets/sizes of a 'len' field and a 'timeout' field cannot be confirmed. Reporting insufficient_evidence rather than guessing specific byte offsets. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ An engineer connected over the device's debug-reachable channel (e.g. the USB rndis0 link this project has separately confirmed is routed to this same message-bus listener) sending the built-in 'ping' diagnostic to check that the message-bus/shell-event plumbing on the device is alive and round-tripping -- an ordinary liveness check, not the kind of generic remote-exec primitive the command's DUML name might suggest (this project's own prior analysis found the 10 real sub-handlers are ping/heartbeat/log/route-table diagnostics, not an arbitrary system()/popen() call). Handler correctly identified (duss_event_shell), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ A firmware-update utility (e.g. the on-aircraft upgrade_test CLI, standing in for whatever orchestrates a module firmware push) asks the drone's upgrade center to begin a single-module upgrade cycle; in this call path the device replies with the list of modules it currently considers upgradeable, which the caller would use to pick a target before sending the actual firmware transfer commands (0x83/0x84/0x85 family, documented elsewhere in this project). Handler correctly identified (send_fn (local, stripped static helper inside upgrade_test, at file offset matching vaddr 0xa010/0xa240 in the E2 build) -> duss_event_send_sync (libduml_frwk.so, PLT import)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Before pushing a dual-partition (A/B) firmware image, the upgrade orchestrator sets an upgrade-mode flag on the device (e.g. 'apply to both A/B banks') and waits for the device to acknowledge the flag was accepted. Handler correctly identified (send_fn (local static helper inside upgrade_test, call site at vaddr ~0xa124-0xa158 in the E2 build) -> duss_event_send_sync (libduml_frwk.so)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Some part of the aircraft's Android-based system (e.g. a kernel uevent listener or USB-mode-switch helper) reports to dji_sys that the aircraft's USB-C port has entered a particular OTG state (for example, a storage/peripheral device being plugged in), so dji_sys can update its own cached state and wake any thread waiting on a USB-state change. Handler correctly identified (sys_wm260_usb_state_handle), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ A ground-station app or another internal DUML client wants to discover what devices/nodes are currently reachable on the aircraft's DUML bus (e.g. after plugging in a new payload/accessory), and sends an initial node-sniffer probe; hop_count and visited_entry_count both start at zero since no hop has occurred yet. Handler correctly identified (duss_event_node_sniffer_req), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF0 — Log Push

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF3 — Log Control Module

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF4 — Test Start

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF5 — Test Stop

_Not decoded._ No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF6 — Test Query Result

_Not decoded._ Not resolved -- no handler found, so no example payload is given. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF7 — Push Test Result

_Not decoded._ Not resolved -- no handler found, so no example payload is given. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF8 — Get Metadata

_Not decoded._ Not resolved -- no handler found, so no example payload is given. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFA — Log Control

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: duss_event_log_control`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `module` (Module) | uint8 | Selects which internal debug/log subsystem to control. The handler bounds-checks this to 0-9 inclusive via a 10-entry jump table (cmp w21,#9; b.hi -> reject); any other value short-circuits to status -1001 without ever calling the underlying duss_log_control(). I could not recover which named subsystem each small integer actually corresponds to (no nearby string/enum table was found), so the index values themselves are confirmed but their semantic names are not -- reported honestly as 'module index' rather than invented names. |
  | 1 | 1 | `level` (Level / Parameter) | uint8 (module 0) / uint16 little-endian (module 6, 2 bytes) / absent (modules 1,2,5,7,9) | Verbosity/level value passed to the internal duss_log_control(module, level, 0) API. Confirmed width is module-dependent: module 0 reads exactly 1 more byte here (offset 1); module 6 reads 2 more bytes (offset 1-2, little-endian uint16); modules 1, 2, 5, 7 and 9 read NO further payload bytes at all -- the handler instead passes the address of a zeroed stack slot, consistent with those modules being query-only / having no explicit 'set' value. Modules 3 and 4 have distinct extra code paths (module 3 reads 2 bytes; module 4 reads 1 byte plus a secondary pointer argument) whose exact purpose I could not fully disambiguate -- reported honestly as unresolved rather than guessed. |

**Worked example:**

- Request payload: `00 03`
  module = 0x00 (the default/global log channel), level = 0x03 -- a ground-support engineer raising the aircraft's default debug-log verbosity to level 3 to capture more detail while reproducing an intermittent field issue. This is the simplest, best-evidenced case (module 0, 1-byte level); it is an ordinary, representative diagnostic value, not an edge case.
- Response payload: `03 00 00 00`
  This command gets a distinct, data-bearing response, not a bare ack: on success the handler calls duss_event_resp_data() with a 4-byte little-endian payload containing the level value it just applied (0x00000003, echoed back as confirmation); on failure (duss_log_control returning non-zero) it instead calls duss_event_resp_err() with the error code in place of this payload.

## 0xFB — Selftest State

_Not decoded._ Not resolved -- no handler found, so no example payload is given. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFC — Selftest State Count

_Not decoded._ Not resolved -- no handler found, so no example payload is given. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFD — Dump Frame Buffer

_Not decoded._ Not resolved -- no handler found, so no example payload is given. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFE — Self Define

_Not decoded._ Not resolved -- no handler found, so no example payload is given. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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
