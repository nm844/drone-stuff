# Cmd Set 0x02 — Camera

Total known command IDs: 207

## 0x01 — Do Capture Photo

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _cs_cam_duss_proxy_on_capture`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `trigger_flag` (Wake-before-capture flag) | uint8 (boolean-tested) | Only bit significance confirmed by disassembly is zero-vs-nonzero (the code does `cbz`, not a value compare). 0 = fire the capture trigger immediately, no power-state handling. Nonzero = first check/exit camera low-power mode and wait for the live-view pipeline to come back up, THEN fire the trigger. The two internal camdev trigger-mode constants used (0x1020008 for byte0==0, 0x1020007 for byte0!=0) differ by exactly 1, so they are adjacent entries in some internal enum this pass did not further resolve. Semantic label ("wake before capture") is inferred from the surrounding low-power-wake code path, not from an embedded string -- flagged as medium confidence on the exact end-user meaning, high confidence on the byte's existence, offset, and zero/nonzero branching behavior. |

**Worked example:**

- Request payload: `55 0E 04 66 02 01 01 00 20 02 01 00 26 E2`
  App(2) -> Camera(1), cmd_set=0x02, cmd_id=0x01, seq=1, ack_type requested, 1-byte payload 0x00 (immediate capture, camera already awake). Built and CRC-checked with this project's own duml_py Frame.encode().
- Response payload: `55 0E 04 66 01 02 01 00 80 02 01 00 A5 62`
  Camera(1) -> App(2), same cmd_set/cmd_id/seq, 1-byte payload 0x00 = ret_code OK. (The exact byte count of duss_event_resp_ok's own ACK payload was not independently re-disassembled in this pass -- it follows this project's established ack convention from earlier waves.)

## 0x02 — Do Record

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _cs_cam_duss_proxy_on_record`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `record_ctrl` (Record control byte (packed bitfield)) | uint8 (bitfield: bits[1:0]=action, bits[5:3]=range-checked submode, bits 2/6/7 unused by this logic) | Exact Start/Stop labeling for bits[1:0]==0 vs 1 is an inference from which branch does the wake+convergence-wait (consistent with "start recording should wait for exposure/focus to settle first"), not from an embedded string -- flagged medium confidence on the label, high confidence on the bit layout, valid-value set, and branching behavior itself. |

**Worked example:**

- Request payload: `55 0E 04 66 02 01 02 00 20 02 02 01 BA D5`
  App(2) -> Camera(1), cmd_set=0x02/cmd_id=0x02, seq=2, payload 0x01 (bits[1:0]=1, bits[5:3]=0): likely "start recording", triggers the low-power-wake + 3A-convergence-wait path before calling the record-start trigger.
- Response payload: `55 0E 04 66 01 02 02 00 80 02 02 00 B0 44`
  Camera(1) -> App(2), same cmd_set/cmd_id/seq, payload 0x00 = ret_code OK.

## 0x03 — HeartBeat

_Not decoded._ Confirmed, by direct disassembly, to be a one-way PUSH the camera itself emits (Camera -> App/RC) roughly once per second, not a request the app sends and the camera answers. No incoming-wire-request parser for cmd_id 0x03 was found anywhere in this .so. Confirmed no meaningful payload. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — Set Usb Switch

_Not decoded._ No handler could be bound to this specific cmd_id. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x05 — Virtual Key Send

_Not decoded._ No handler could be bound to this specific cmd_id. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x06 — Get Usb Switch

_Not decoded._ No handler could be bound to this specific cmd_id. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x10 — Camera Work Mode Set

_Not decoded._ A strong-looking candidate handler was found and then specifically disproven as exclusive to this cmd_id -- reported in detail because the disproof technique is reusable. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x11 — Camera Work Mode Get

_Not decoded._ Same investigation and same disproof as 0x10 (see that entry's handler_evidence for the full detail) -- the best-looking name match (camduss_proxy_get_camdev_status_workmode / camapp_proxy_get_camdev_status_workmode) is confirmed to be a shared composite-status-assembly helper called from 7 total sites across 2 other, differently-named status-builder functions, not a dedicated Get-Work-Mode dispatch target. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x12 — Photo Format Set

_Not decoded._ A plausible but unconfirmed lead was found and is reported as a lead, not a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x13 — Photo Format Get

_Not decoded._ Same lead as 0x12 (see that entry) -- _cs_cam_duss_proxy_on_get_p_size is the candidate, unconfirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x14 — Photo Quality Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: camdev_apply_p_quality`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `quality` (Photo Quality enum) | uint8 (enum) | Single enum byte for the internal 'p_quality' camera setting. Copied verbatim into the live capture-params block by camdev_apply_p_quality with no inline range check found in that function (validation, if any, happens upstream in a generic settings-registration layer this pass did not locate). The concrete legal value list was not recovered -- reported as a 1-byte field only, not a specific enum. |

**Worked example:**

- Request payload: `01`
  Set quality to raw code 1 (an ordinary representative value; the exact named meaning of code 1 was not independently confirmed).
- Response payload: `00`
  DUML Set commands in this family are ack-only: a short status/return-code response, not a copy of the field.

## 0x15 — Photo Quality Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: camdev_apply_p_quality (write side); no dedicated per-parameter read function was found -- reads of 'p_quality' appear to go through the generic camdev_get_user_setting primitive rather than a named per-parameter getter`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `quality` (Photo Quality enum) | uint8 (enum) | Same field as 0x14's Set payload, echoed in the Get response as the current value. Request itself carries no payload. |

**Worked example:**

- Request payload: `(empty -- Get requests in this family carry no payload)`
  A bare Get request with zero-length payload.
- Response payload: `01`
  Response payload = current quality raw code (1).

## 0x16 — Photo Storage Fmt Set

_Not decoded._ App/pilot changes which storage-format convention photo files are written in. Handler correctly identified (camdev_apply_p_storage_format), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x17 — Photo Storage Fmt Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: camdev_apply_p_storage_format (write side); Get served generically, same caveat as 0x15`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `storage_format` (Photo Storage Format enum) | uint8 (enum) | Same field/legal-value set as 0x16, echoed in the Get response. |

**Worked example:**

- Request payload: `(empty)`
  
- Response payload: `02`
  Current storage-format raw code (2).

## 0x18 — Video Format Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _camdev_set_v_format (top-level, full struct) and camdev_apply_v_format (sub-step validating just the fps sub-field)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `resolution_profile_id` (Resolution/Profile ID) | uint8 (enum) | Selects a product-specific video resolution/aspect profile. Validated by linear search against a 39-entry table; confirmed legal raw codes: {0,2,4,6,8,10,12,14,16,18,20,22,24,26,29,31,32,33,37,39,45,55,57,59,60,61,62,63,64,65,90,91,92,93,94,95,96,97}. |
  | 1 | 1 | `fps_id` (Frame-rate ID) | uint8 (enum) | Selects the frame rate for the chosen resolution profile. Confirmed legal raw codes: 0-30 except {12,17,18,21,23}. |
  | 2 | 1 | `unk_field_2` (unresolved field) | uint8 | Confirmed read by the handler (present in its debug-log call); specific meaning not resolved in this pass -- not a guessed name. |
  | 4 | 1 | `unk_field_4` (unresolved field) | uint8 | Confirmed read by the handler; meaning not resolved. |
  | 5 | 1 | `unk_field_5` (unresolved field) | uint8 | Confirmed read by the handler; meaning not resolved. |
  | 6 | 1 | `unk_field_6` (unresolved field) | uint8 | Confirmed read by the handler; meaning not resolved. |
  | 7 | 1 | `unk_field_7` (unresolved field) | uint8 | Confirmed read by the handler; meaning not resolved. |
  | 8 | 2 | `unk_field_8` (unresolved 16-bit field) | uint16 | Read with `ldrh` (so genuinely 2 bytes, not 2 separate u8 fields); meaning not resolved -- plausibly a bitrate or codec-parameter sub-field. |
  | 10 | 1 | `unk_field_10` (unresolved field) | uint8 | Confirmed read by the handler; meaning not resolved. Struct is at least 11 bytes (offset 0-10 inclusive). |

**Worked example:**

- Request payload: `3C 00 00 00 00 00 00 00 00 00 00`
  resolution_profile_id=0x3C(60, a confirmed-valid profile code), fps_id=0 (a confirmed-valid fps code), all remaining unresolved fields left at 0 as an ordinary/default-looking value -- illustrative only, not a confirmed real-world combination.
- Response payload: `00`
  Ack-only Set response (generic 1-byte return code).

## 0x19 — Video Format Get

_Not decoded._ App queries the aircraft for the video resolution+frame-rate profile currently in effect. Handler correctly identified (_camdev_set_v_format / camdev_apply_v_format (write side); Get served generically), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1A — Video Quality Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _camdev_apply_v_quality`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `quality` (Video Quality enum) | uint8 (enum, inferred) | Inferred-by-analogy single enum byte for the internal 'v_quality' setting; not directly observed being read in camdev_apply_v_quality itself (that function forwards the raw pointer to a generic publish/notify call instead of reading it in-line). Reported at medium-low confidence specifically because of this gap -- not invented beyond what the sibling functions support. |

**Worked example:**

- Request payload: `02`
  Set video quality to raw code 2 (illustrative, unconfirmed exact semantics).
- Response payload: `00`
  Ack-only Set response.

## 0x1B — Video Quality Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _camdev_apply_v_quality (write side); Get served generically`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `quality` (Video Quality enum) | uint8 (enum, inferred) | Same field as 0x1A, current value. |

**Worked example:**

- Request payload: `(empty)`
  
- Response payload: `02`
  Current video-quality raw code (2).

## 0x1C — Video Storage Fmt Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: camdev_apply_v_storage_format`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `storage_format` (Video Storage Format enum) | uint8 (enum) | Binary enum byte for the internal 'v_storage_format' setting. Directly-verified legal raw wire values: {0,1}; any other byte is rejected by camdev_apply_v_storage_format. The named meaning of 0 vs 1 (e.g. two different recording-container conventions) was not independently resolved. |

**Worked example:**

- Request payload: `00`
  Set video storage format to raw code 0, one of the two confirmed-legal codes.
- Response payload: `00`
  Ack-only Set response (generic 1-byte return code).

## 0x1D — Video Storage Fmt Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: camdev_apply_v_storage_format (write side); Get served generically`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `storage_format` (Video Storage Format enum) | uint8 (enum) | Same field/legal-value set as 0x1C, echoed in the Get response. |

**Worked example:**

- Request payload: `(empty)`
  
- Response payload: `00`
  Current video storage-format raw code (0).

## 0x1E — Exposure Mode Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: af_v1_camera_api_switch_exposure_mode (vaddr 0x0003017c in at_v1trigger.so); corroborated by gc_v1_camera_api_set_camera_expo_mode (vaddr 0x000157e4 in at_gimbalcali.so)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `exposure_mode` (Exposure Mode) | uint8 (enum) | Enum reused from this cmd_set's already-decoded 0x81 'Camera Shot Params' push field at its own offset 20 (enums.CAMERA_SHOT_PARAMS_EXPOSURE_MODE_ENUM from the imported public dissector): 0x01=Program, 0x02=ShutterPriority, 0x03=AperturePriority, 0x04=Manual, 0x07=Cine (0x00/0x05/0x06/0x64 unnamed in the public dissector). |
  | 1 | 1 | `exposure_mode_param2` (Secondary Byte (unresolved)) | uint8 | A genuine second field - confirmed real (not padding) because the AT-tool wrapper is compiled with 2 separate function arguments, AAPCS r0/r1, not one. Exact DJI semantics not recovered from available evidence; no caller of this specific wrapper was found in-binary to observe a typical literal value. Reported honestly as unresolved rather than guessed. |

**Worked example:**

- Request payload: `03 00`
  Set Exposure Mode = 0x03 (AperturePriority); second byte left at its most commonly-observed value in this family of calls, 0x00 (semantics unresolved, see field note).
- Response payload: `00`
  1-byte DUML ack/result code, 0x00 = success - confirmed by the AT-tool's own post-call check (it treats a non-zero byte at the response-buffer offset as failure, mirroring the proven convention for sibling command 0x24 below).

## 0x1F — Exposure Mode Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: No cmd-0x1f-specific function found. Pattern borrowed from two directly-disassembled sibling Get functions in this exact library: af_v1_camera_api_get_focus_mode (0x0002fe5c, binds cmd_id 0x25) and af_v1_camera_api_query_camera_mode (0x0002f97c, binds cmd_id 0x11) - both empty-request / [ret_code:u8][value:u8]-response.`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 0 | `(no request fields)` (Request) | none | Empty request payload, matching both directly-observed sibling Get commands (0x11, 0x25) in this family. |
  | 0 | 1 | `ret_code` (Result Code) | uint8 | 0 = success, matching the convention observed in all disassembled Set/Get wrappers in this family. |
  | 1 | 1 | `exposure_mode` (Exposure Mode) | uint8 (enum) | Inferred mirror of the Set command's byte 0 field (enums.CAMERA_SHOT_PARAMS_EXPOSURE_MODE_ENUM). |

**Worked example:**

- Request payload: `(empty)`
  No request payload sent.
- Response payload: `00 03`
  ret_code=0x00 (success), exposure_mode=0x03 (AperturePriority) - by analogy to the directly-disassembled 0x25/0x11 response shape.

## 0x20 — Scene Mode Set

_Not decoded._ Searched: (1) all 16 at_*.so factory-test plugins (nm -D export scan + full grep for 'scene'/'scn') on e1e - zero gc_v1_camera_api_*/af_v1_camera_api_* functions reference a scene mode setter; (2) dji_camera3's direct link graph (libdcam_cs_cbb.so - exactly one cam_event_client_pool_register call site, fully disassembled, used only for an HMS debug-tool client with value 0xef, not a scene-mode table); (3) dji_sys's recovered .gnu_debugdata minidebuginfo local symbol table (extracted this pass) - no camera-ISP-parameter functions at all, only camera power-state/subscribe glue; (4) dji_flight's fully-dumped relocated dispatch array (vaddr 0xae038-0xae190) - its only cmd_set=0x02 rows are 0x80/0x81/0x87, not 0x20. The real receiving-side parser most plausibly lives in the dynamically-loaded camera 'state' plugin (lib64/camera/plugins/state/libdcam_cs_camera_state.so on e2), which exports only 2 symbols (cs_camera_state_create, cs_camera_state_set_tap_zoom_target) - its actual per-command dispatch logic is entirely in unexported, file-local static functions that would need full address-by-address decompilation to recover, out of this pass's scope. CONCRETE LEAD for a future pass: libdcam_camdev.so (e2) exports camdev_apply_focus_mode-sibling setters camdev_get_aperture/camdev_set_ae_meter but NO 'scene_mode' setter by that name; the only scene_mode evidence found anywhere is a bare uint8 field (no enum, no cmd binding) inside the ALREADY-DECODED sibling push command '0x81 Camera Shot Params' at byte offset 21 (camera_camera_shot_params_scene_mode) - this gives a plausible TYPE lead (uint8, likely a small enum) but is not evidence of 0x20's own binding or byte count, so it is reported here as a lead, not a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — Scene Mode Get

_Not decoded._ Same search as 0x20 (Scene Mode Set) - no handler, no AT-tool wrapper, no literal cmd_id=0x21 found anywhere in either firmware image's DUML-registration-capable binaries. Same scene_mode-field type lead from the sibling '0x81 Camera Shot Params' push applies (uint8, offset 21, no enum recovered). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — AE Meter Set

_Not decoded._ Searched all 16 at_*.so plugins and the dji_camera3 link graph as for 0x20/0x21 - no handler or AT-tool wrapper found. Two genuine but explicitly-disambiguated false leads recorded rather than conflated: (1) librcam.so (e2) contains debug-CLI strings 'UsCtrlId_Set_AeMeterMode' / 'UsCtrlId_Set_AeMeterRegion' and 'Query_AeMeterRegionFunc', and libdcam_camdev.so exports _camdev_set_ae_meter/camdev_apply_ae_meter/camdev_get_user_setting(US_AE_METER) - but 'UsCtrlId_*'/'US_*' is this firmware's internal User-Setting-Manager (USM) property-ID namespace, a SEPARATE numbering space from DUML (cmd_set,cmd_id), per this project's own standing disambiguation rule (same caution the task brief raised for BLCOMM/CHANID and imss_link_register_sdk_callback) - not treated as a cmd_id binding. (2) the sibling, already-decoded '0x81 Camera Shot Params' push has a bare uint8 field named 'metering' at offset 22 (camera_camera_shot_params_metering, no enum) which is plausibly the same underlying parameter as 'AE Meter', offered only as a weak type lead, not a decode of 0x22 itself. No byte offsets recovered. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x23 — AE Meter Get

_Not decoded._ Same search and same result as 0x22 (AE Meter Set) - no handler or literal cmd_id=0x23 binding found anywhere. Same USM-namespace disambiguation and 'metering' field type-lead notes apply. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x24 — Focus Mode Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: gc_v1_camera_api_set_camera_focus_mode (vaddr 0x00015334, at_gimbalcali.so) and af_v1_camera_api_set_focus_mode (vaddr 0x0002ff74, at_v1trigger.so)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `focus_mode` (Focus Mode) | uint8 (enum) | Direct copy of the function's sole uint8 argument onto the wire - no internal remapping/lookup in either wrapper. No cmd-0x24-specific enum table was found disassembled; the enum values given are borrowed (with that caveat stated) from this cmd_set's sibling CAMERA_SHOT_INFO_FUSELAGE_FOCUS_MODE_ENUM (same semantic domain, already in the imported public dissector): 0=Manual, 1=OneAuto(AF-S), 2=ContinuousAuto(AF-C), 3=ManualFine. |

**Worked example:**

- Request payload: `02`
  focus_mode = 0x02 (ContinuousAuto / AF-C).
- Response payload: `00`
  1-byte ack, 0x00 = success - directly observed in both wrappers' post-call check logic (cbz/cbnz on the single response byte).

## 0x25 — Focus Mode Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: af_v1_camera_api_get_focus_mode (vaddr 0x0002fe5c)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 0 | `(no request fields)` (Request) | none | req_ptr=NULL, req_len=0 in the disassembled struct build - confirmed empty request. |
  | 0 | 1 | `ret_code` (Result Code) | uint8 | 0 = success. Directly observed: non-zero short-circuits to an error-logging path without reading byte 1. |
  | 1 | 1 | `focus_mode` (Focus Mode) | uint8 (enum) | The actual retrieved value, directly observed being copied out via 'ldrb r1,[r6,#1]; strb r1,[r7,#0]'. Same borrowed-enum caveat as cmd 0x24 applies (CAMERA_SHOT_INFO_FUSELAGE_FOCUS_MODE_ENUM): 0=Manual,1=OneAuto,2=ContinuousAuto,3=ManualFine. |

**Worked example:**

- Request payload: `(empty)`
  No request payload.
- Response payload: `00 02`
  ret_code=0x00 (success), focus_mode=0x02 (ContinuousAuto) - matches the Set-side worked example for 0x24, as a plausible read-back after that Set call.

## 0x26 — Aperture Size Set

_Not decoded._ Same exhaustive AT-tool/dji_camera3-link-graph/dji_sys-minidebuginfo/dji_flight-array search as 0x20-0x23 - no handler or literal cmd_id=0x26 binding found anywhere in either firmware image. Leads recorded, not asserted as a decode: (1) librcam.so (e2) debug-CLI strings show '8: set_aperture <aperture_value> <speed>' / 'Capture_SetAperture ApertureValue:%d speed:%d' / 'DjiLens_SetApertureOpen Speed:%d' - this is the LENS-DRIVER level API below any DUML parsing, not proof of the wire payload's own shape, but it does suggest a target-value-plus-adjustment-speed pattern is used somewhere in this stack for aperture changes. (2) libdcam_camdev.so exports _camdev_set_aperture/camdev_apply_aperture/camdev_get_aperture, confirming 'aperture' is a real internal parameter name, but gives no byte-level binding. (3) Strong, repeated TYPE evidence (not a cmd-0x26 decode) from the sibling already-decoded '0x81 Camera Shot Params' push: camera_camera_shot_params_aperture_size (offset 0, uint16), camera_camera_shot_params_real_aperture_size (offset 38, uint16), camera_camera_shot_params_cap_min_aperture / cap_max_aperture (offsets 62/64, uint16 each) - every other appearance of an 'aperture size' value in this cmd_set's already-decoded traffic is a uint16, which is the most defensible type lead for a future pass, but is reported here as a lead only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x27 — Aperture Size Get

_Not decoded._ Same search and result as 0x26 (Aperture Size Set) - no handler or literal cmd_id=0x27 binding found. Same uint16 aperture_size type lead (from the sibling 0x81 push) applies. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x28 — Shutter Speed Set

_Not decoded._ Exhaustive search for a cmd_id-keyed handler found none. Checked, in this order: (1) dji_camera3 and librcam.so (e2/aarch64) — neither imports duss_event_register_dynamic_command or any _with_user_data/_table variant at all (confirmed via a full .rela.plt/.dynsym walk with readelf -rW, not a sample), so mechanism #1 (including a dji_sys-style duss_register_cmd batch helper) is structurally impossible in both binaries. (2) librcam.so's two duss_mb_create_route_table+duss_event_create_client call sites (route table 'camera_service', vaddr 0x88508 and 0xb2e30ish) were fully traced: the dispatch-table argument they build (a 224-byte object populated at vaddr 0x57ed0 with 15 static function pointers, auto-constructed before main) feeds into a property-registration routine (vaddr 0x580a0) that validates each incoming row has 'exactly one bit set' among 4 flag bits at row-offset 8 of a 12-byte input descriptor — this is an AE/AWB/AF/lens-adjustment bitmask-category subsystem, not a per-cmd_id switch. This independently reconfirms, on the e2/aarch64 build, this project's existing doc08 finding for the sibling e1e daemon dji_rcam ('Bitmask flags...carried in the message itself — not per-cmd_id'). (3) dji_flight's relocated {fn_ptr,cmd_word} array (e1e only; no dji_flight binary exists in the e2 tree) was directly re-extracted byte-for-byte from vaddr 0xae038-0xae190 (44 rows confirmed) — its only 3 cmd_set 0x02 rows are cmd_id 0x80/0x81/0x87 (Camera State Info/Shot Params/Shot Info pushes); none is in this batch. (4) libdcam_cs_duss_proxy.so is confirmed (own imports: duss_mb_create_route_table + duss_event_create_client_with_attribution, separate from librcam.so's clients) to be the file-download/offload channel the task warned about, not the generic command channel. (5) A major architectural lead WAS found: dji_camera3 itself embeds a 105-entry internal named-parameter table (.data, base vaddr 0x20020, count field at 0x20010 = 0x69 = 105, confirmed self-consistent) mapping numeric IDs (category_byte<<24 | sequential_index) to literal name strings — entry #29, id 0x0200001d, is named exactly 'shutter_speed'. This table is passed (via a stack-built config struct) into service_init(), exported by libdcam_cs_cbb.so (the one other library, besides librcam.so, that imports duss_event_send — 'cs' plausibly = 'command set'). service_init spins up a generic message-loop ('looper_thread_create'/'looper_message_send') and calls dcam_dbg_init; I could not, within this pass's effort, disassemble the looper thread's message callback to recover the (cmd_set 0x02, cmd_id 0x28) -> param-id-0x1d translation or the exact wire encoding used by whatever reads/writes this specific parameter. See shared_infrastructure_found for the full table. Given no handler was independently disassembled, this is reported as insufficient_evidence per the task's own instruction, with the following as a clearly-flagged, lower-confidence candidate layout only: the already real, disassembled, cross-architecture-confirmed 'Camera Shot Params' push dissector (cmd_id 0x81, camera_camera_shot_params_dissector, independently cross-checked against the public dji-firmware-tools Wireshark dissector) has a directly-analogous 'User Shutter' field (uint16 @ offset 2, bit15/mask 0x8000 = 'Reciprocal') plus 'Shutter Speed Decimal' (uint8 @ offset 4) — i.e. the aircraft's camera firmware already represents a shutter speed exactly this way somewhere in its wire protocol. By structural analogy (not independent disassembly of this specific cmd_id's handler) a Shutter Speed Set payload most plausibly mirrors that same 3-byte encoding. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x29 — Shutter Speed Get

_Not decoded._ Same exhaustive search and same result as 0x28 (its Set counterpart) — see that entry's scenario_description for the full methodology (librcam.so/dji_camera3 rule out mechanism #1 entirely; librcam.so's bus clients lead only to the AE/AWB/AF bitmask-category subsystem, cross-confirming doc08; dji_flight's e1e array's only cmd_set 0x02 rows are 0x80/0x81/0x87; dji_camera3's internal 105-entry named-parameter table has a 'shutter_speed' entry (id 0x0200001d) whose real consumer (service_init/libdcam_cs_cbb.so's looper-thread callback) was located but not fully disassembled in the time available). No cmd_id-0x29-specific handler found. Candidate layout is the Get-direction mirror of 0x28's candidate, by the same analogy to the already-decoded cmd_id 0x81 'Camera Shot Params' push struct. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2A — ISO Set

_Not decoded._ Same exhaustive search as 0x28/0x29 (dji_camera3/librcam.so rule out mechanism #1 entirely; librcam.so's bus clients lead only to the AE/AWB/AF bitmask-category subsystem; dji_flight e1e array's only cmd_set 0x02 rows are 0x80/0x81/0x87) found no cmd_id-0x2A-specific handler. Two independent pieces of REAL evidence converge on this field's identity and real value set, raising confidence above the other commands in this batch: (1) dji_camera3's own internal 105-entry named-parameter table has an entry named exactly 'iso' (id 0x0200001b, table index 27); (2) the already-decoded, cross-architecture-confirmed 'Camera Shot Params' push struct (cmd_id 0x81) has a 1-byte 'Iso' field at offset 5 with a REAL, non-placeholder enum table (CAMERA_SHOT_PARAMS_ISO_TYPE_ENUM, cross-checked against the public dji-firmware-tools Wireshark dissector): 0x00 AUTO, 0x01 AUTOHIGH, 0x02 ISO50, 0x03 ISO100, 0x04 ISO200, 0x05 ISO400, 0x06 ISO800, 0x07 ISO1600, 0x08 ISO3200, 0x09 ISO6400, 0x0A ISO12800, 0x0B ISO25600. No separate ISO enum/lookup table was found anywhere in dji_camera3/librcam.so itself (the only evidence for the enum values is the already-decoded sibling struct), so this remains a structural-analogy candidate, not an independently disassembled cmd_id-0x2A handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2B — ISO Get

_Not decoded._ Same methodology and same result as 0x2A (its Set counterpart) — see that entry. No cmd_id-0x2B-specific handler found; candidate layout is the Get-direction mirror, carrying the same 1-byte ISO enum in the response instead of the request. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2C — White Balance Env Set

_Not decoded._ Same exhaustive search as the rest of this batch (mechanism #1 structurally ruled out in dji_camera3/librcam.so; librcam.so's bus leads only to the AE/AWB/AF bitmask-category subsystem — note this subsystem IS 'AWB'-adjacent by name, but the task's own prior docs (08, 16) and this pass's independent re-trace both confirm it carries generic enable/category BITMASKS, not a specific white-balance preset VALUE, so it was not usable as this command's handler; dji_flight e1e array's only cmd_set 0x02 rows are 0x80/0x81/0x87) found no cmd_id-0x2C-specific handler. dji_camera3's internal 105-entry named-parameter table has an entry named 'wb' (id 0x02000028, table index 40) confirming this exact setting has its own first-class internal parameter slot, but (as with the rest of the batch) the translation from this cmd_id to that internal id, and the exact wire encoding, was not independently disassembled. The already-decoded 'Camera Shot Params' push struct (cmd_id 0x81) has two directly-relevant 1-byte fields: 'White Balance' (offset 23, raw uint8, no enum/lookup table found anywhere for its real values — unlike the ISO field, the public dissector does NOT give this field an enum) and 'Color Temp' (offset 24, raw uint8). No evidence was found for whether 'White Balance Env Set' sends one byte (preset only) or two (preset + an associated custom color-temperature byte); this is flagged as the least-confident part of this candidate. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2D — White Balance Env Get

_Not decoded._ Same methodology and same result as 0x2C (its Set counterpart) — see that entry. No cmd_id-0x2D-specific handler found; candidate layout is the Get-direction mirror. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2E — Exposition Bias Set

_Not decoded._ Same exhaustive search as the rest of this batch (mechanism #1 structurally ruled out in dji_camera3/librcam.so; librcam.so's bus leads only to the AE/AWB/AF bitmask-category subsystem; dji_flight e1e array's only cmd_set 0x02 rows are 0x80/0x81/0x87) found no cmd_id-0x2E-specific handler. dji_camera3's internal 105-entry named-parameter table has an entry named 'ev_bias' (id 0x0200001e, table index 30), directly confirming this exact setting ('exposition bias'/'EV bias' are the same concept) has its own first-class parameter slot, but the cmd_id-to-internal-id translation and exact wire encoding were not independently disassembled (same unresolved gap as the rest of the batch — the consumer is most likely libdcam_cs_cbb.so's service_init-spawned looper-thread message callback, which I located but did not fully disassemble). The already-decoded 'Camera Shot Params' push struct (cmd_id 0x81) has a directly-named 'Exposure Compensation' field: 1 byte, raw uint8, no enum/scale table found anywhere. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2F — Exposition Bias Get

_Not decoded._ Same methodology and same result as 0x2E (its Set counterpart) — see that entry. No cmd_id-0x2F-specific handler found; candidate layout is the Get-direction mirror. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x30 — Focus Region Set

_Not decoded._ Same exhaustive search as the rest of this batch found no cmd_id-0x30-specific handler (mechanism #1 structurally ruled out in dji_camera3/librcam.so; librcam.so's bus leads only to the AE/AWB/AF bitmask-category subsystem, whose 12-byte entries have no x/y coordinate fields; dji_flight e1e array's only cmd_set 0x02 rows are 0x80/0x81/0x87). dji_camera3's internal 105-entry named-parameter table has an entry named exactly 'focus_region' (id 0x02000019, table index 25) — directly confirming this exact setting has a first-class internal parameter slot — but, as with the rest of the batch, the cmd_id translation and wire encoding were not independently disassembled. This is the weakest-evidenced candidate in the batch: the closest BYTE-LEVEL analog found is in a *different* already-decoded push struct, 'Camera Shot Info' (cmd_id 0x87, camera_camera_shot_info_dissector), which has directly-named 'Spot Af Axis X' and 'Spot Af Axis Y' fields, both type float. No field named 'region' with x/y/width/height semantics was found in the already-decoded 'Camera Shot Params' struct (cmd_id 0x81) itself — the two generic 'Ctr Object For One/Two' uint8 fields there (offsets 7-8) were considered but explicitly NOT used as evidence, since they carry no name or context tying them to focus/region at all (the public dissector itself leaves them unlabeled) and using them would cross into inventing a layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x31 — Focus Region Get

_Not decoded._ Same methodology and same result as 0x30 (its Set counterpart) — see that entry. No cmd_id-0x31-specific handler found; candidate layout is the Get-direction mirror. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x32 — AE Meter Region Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _DjiAAA_CmdMgr_AE_AeMeterRegion @ 0x8c008 (376 bytes) — set/notify path. Cross-confirmed by the paired Query_AeMeterRegionFunc @ 0x7a5c8 (Get path: memcpy(out_buf, ctx+0x198, 0x88) — same 136-byte size).`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `region_type` (Region Type) | int32/enum | AE metering-region mode selector (e.g. spot/center/multi-point); real enum value set not recovered from this handler — no switch/lookup table enumerating it was found in this pass. |
  | 4 | 1 | `rect_index` (Rect Index) | uint8 | Index of the region entry this record pertains to (bounds-checked elsewhere in librcam against a per-type max-count table at vaddr 0x2b1b68 + type*16 + 4, confirmed in Query_AeMeterRegionFunc's disassembly). |
  | 5 | 1 | `reserved_1` (Reserved) | uint8 | Struct-alignment padding byte before the following uint16; never read by the disassembled code (inferred from alignment, not observed). |
  | 6 | 2 | `rect_count` (Rect Count) | uint16 | Number of currently-active metering regions (0-8, given the struct's 8-slot array). |
  | 8 | 4 | `region_0_x_label` (Region 0 X Label) | float32 | First region's normalized X center/label coordinate — directly confirmed via the debug-print's s0 load. |
  | 12 | 4 | `region_0_y_label` (Region 0 Y Label) | float32 | First region's normalized Y center/label coordinate — confirmed via s1. |
  | 16 | 4 | `region_0_x_len` (Region 0 X Len) | float32 | First region's normalized width — confirmed via s2. |
  | 20 | 4 | `region_0_y_len` (Region 0 Y Len) | float32 | First region's normalized height — confirmed via s3. |
  | 24 | 112 | `regions_1_to_7` (Regions 1-7) | array[7] of {float32 x_label; float32 y_label; float32 x_len; float32 y_len} | Remaining 7 region slots, same 16-byte shape as region 0 by direct size arithmetic (136 - 8 header - 16 region0 = 112 = 7*16) — NOT individually confirmed by disassembly (the one debug-print call only ever logs slot 0 regardless of rect_index), so field names/order for slots 1-7 are inferred, not directly observed. |

**Worked example:**

- Request payload: `00000000000001000000003f0000003fcdcc4c3ecdcc4c3e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000`
  136-byte Set payload: region_type=0 (first/default mode), rect_index=0, rect_count=1 (single active region), region[0] = {x_label=0.5, y_label=0.5, x_len=0.2, y_len=0.2} i.e. a single spot-metering box centered in frame, 20% of frame width/height; regions 1-7 zeroed/unused.
- Response: Set is expected to be ack-only (standard DUML ret_code ack, no distinct payload) per this project's convention for Set-family commands elsewhere in cmd_set 0x02 — not independently confirmed for this specific command_id.

## 0x33 — AE Meter Region Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: Query_AeMeterRegionFunc @ 0x7a5c8 (304 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `region_type` (Region Type) | int32/enum | Same semantics as the Set command's field (see 0x32). |
  | 4 | 1 | `rect_index` (Rect Index) | uint8 |  |
  | 5 | 1 | `reserved_1` (Reserved) | uint8 |  |
  | 6 | 2 | `rect_count` (Rect Count) | uint16 |  |
  | 8 | 4 | `region_0_x_label` (Region 0 X Label) | float32 |  |
  | 12 | 4 | `region_0_y_label` (Region 0 Y Label) | float32 |  |
  | 16 | 4 | `region_0_x_len` (Region 0 X Len) | float32 |  |
  | 20 | 4 | `region_0_y_len` (Region 0 Y Len) | float32 |  |
  | 24 | 112 | `regions_1_to_7` (Regions 1-7) | array[7] of {float32 x_label; float32 y_label; float32 x_len; float32 y_len} | Inferred by size arithmetic only, as for 0x32. |

**Worked example:**

- Request payload: ``
  Get request: conventionally an empty/zero-length payload for this DUML product line's simple parameter-Get commands (not independently disassembly-confirmed for 0x33 specifically).
- Response payload: `00000000000001000000003f0000003fcdcc4c3ecdcc4c3e00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000`
  Response mirrors the 0x32 worked example: single active spot-metering region, centered, 20% width/height.

## 0x34 — Zoom Param Set

_Not decoded._ Concrete, bounded lead for a future pass: total payload is very likely 24 bytes; the parameter almost certainly groups a zoom-operation-type selector with a target value and a speed (per the 5 CLI sub-commands and the dead debug string's variable names 'Zoom'/'speed'/'FL'), but exact byte offsets/types within those 24 bytes are not evidenced. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x35 — Zoom Param Get

_Not decoded._ Same open lead as 0x34: handler identified, total/field layout not resolved. A future pass tracing the caller(s) of Query_ZoomControlFunc to see what length constant they pass in would likely resolve the response size. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x36 — Flash Mode Set

_Not decoded._ Thorough, multi-angle negative search, consistent across every angle tried: (1) librcam.so's recovered .symtab (.gnu_debugdata) lists a complete 'UsCtrlId_Set_*' enumeration of ~95 settable parameters (every other command in this batch and most of cmd_set 0x02's 0x1E-0x45 range has an exact-name match in this list) — there is NO 'UsCtrlId_Set_FlashMode' or 'UsCtrlId_Set_Flash' entry anywhere in it. (2) The parallel '_DjiAAA_CmdMgr_{AE,AF,AWB}_*' per-parameter handler family (which covers 0x32-0x37's AE/AF siblings) has no '..._FlashMode' or '..._Flash' member in any of the three groups. (3) A direct string search of librcam.so for 'flash'/'Flash' turns up only unrelated hits: mechanical-shutter flash-SYNC terminals ('FlashSync', 'SetFlashSync <FlashSync>', 'Util_EnableFlashSync', 'DjiLens_OperateShutter FlashSync:%d') — an electrical sync-pulse-to-external-strobe feature on the lens/shutter assembly, not a camera-owned flash unit or mode enum — and unrelated image-sensor register names ('FLASH_STRB_*', likely strobe-timing registers reused from a sensor datasheet). (4) dji_camera3's own string table has no 'flash'-related string at all. This is consistent with the Mavic 3/WM260 camera gimbal simply having no onboard flash hardware, so this legacy-numbered DUML command, while present in the public dissector's command list, appears to have no live implementation on this airframe — architecturally analogous to this project's prior 'confirmed not implemented on this firmware generation' finding for the 12 DM36x commands (doc 21). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x37 — Flash Mode Get

_Not decoded._ Same exhaustive negative search as 0x36 (Query_* convention also checked — no 'Query_FlashMode*'/'Query_Flash*' exists in librcam.so's recovered symbol table either). See 0x36 for full detail. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x38 — Sharpeness Set

_Not decoded._ Lead for a future pass: check libdcam_iq_module.so's / libdcam_pp*.so's dcam_adj_* functions directly (this pass extracted but did not fully disassemble libdcam_iq_module.so, which has only a tiny recoverable debug symbol set of its own) for a sharpness setter; also worth checking whether the generic 'Param Name Set/Get' commands (0xC2/0xC3, flagged open in doc 04) are the real wire-level carrier for UsCtrlId_Set_Sharpness rather than a dedicated 0x38-specific parser. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x39 — Sharpeness Get

_Not decoded._ No 'Query_Sharpness*' function exists in librcam.so's recovered symbol table (only 'Query_ProresRawSharpness' and 'Query_DngBaselineSharpness' exist, both clearly scoped to ProRes RAW/DNG metadata export, not the live camera-ISP sharpness control). Same sibling-struct lead as 0x38 (cmd 0x81 offset 27, uint8). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3A — Contrast Set

_Not decoded._ Stronger negative than Sharpness: librcam.so's full recovered 'UsCtrlId_Set_*' list (~95 entries, exhaustively enumerated in this pass) has NO 'UsCtrlId_Set_Contrast' entry at all — unlike Sharpness, which at least has a live string confirming the setting exists somewhere in this product's control surface, Contrast has no trace whatsoever in librcam.so's or libaaa.so's live string/symbol tables (every 'contrast'-matching string found in both libraries is unrelated ISP tuning-curve calibration-table data, e.g. 'DjiCfg_iq_main_gtm_contrast_curve_r/g/b' — static gamma/tone-mapping curve *data*, not a settable user parameter — or AF-algorithm internal terms like 'af_scene_contrast'/'cdaf_check_contrast_info_enhance', which are autofocus-confidence-metric internals unrelated to image contrast styling). The only lead at all is, again, this project's pre-existing dissector-sourced cmd 0x81 'Camera Shot Params' push struct, which has a 'camera_camera_shot_params_contrast' uint8 field at offset 28 (immediately after the Sharpe field at offset 27) — but with zero corroborating evidence that this legacy numbered Set/Get command pair is actually wired to anything live on this firmware. Plausibly a legacy/vestigial DUML command (contrast may now be folded into the broader 'ColorMode'/'SceneCtrlMode' style-preset selection rather than exposed as its own independent slider on this camera generation) rather than a tooling gap — but this pass cannot assert that conclusively, so it is reported as insufficient_evidence, not as a confirmed negative. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3B — Contrast Get

_Not decoded._ Same exhaustive negative search as 0x3a — no 'Query_Contrast*' exists anywhere in librcam.so's recovered symbol table. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3C — Saturation Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: UsCtrl_Map_CmdId (vaddr 0x44330) -> 126-entry {internal_cmd_id, usctrl_index} table at vaddr 0x205698 (.rodata) -> usctrl_index 37 -> UsCtrl_Query_TagSize/UsCtrl_Query_TagType (vaddr 0x7b0b8 / 0x7b320) -> 82+-entry {type_tag, size, handler_ptr} table at vaddr 0x2b1b68 (.data), entry 37`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `saturation_level` (Saturation level) | int32 | Single int32 (little-endian) adjustment value, internal UsCtrl type_tag=5 ('adjustable level' class, shared with Sharpness/Denoising/ISO-gain-style params in the same table). Exact numeric range not independently confirmed from disassembly in this pass; DJI's other camera products conventionally use a small signed range (commonly -3..+3) for this style of ISP slider, shown here only as a plausible, non-attack-shaped example, not a confirmed enum table. |

**Worked example:**

- Request payload: `01 00 00 00`
  Set saturation to +1 (one notch above neutral), an ordinary user-adjustment value.
- Response: Request/response (not one-way): the exact ACK payload format for this specific cmd_id was not independently disassembled in this pass (unlike e.g. cmd_set 0x00/0x4A 'Set Date/Time', where this project previously found and disassembled a confirmed 1-byte status ack). By established DUML convention for 'Set' commands elsewhere in this project, expect a short status/ack frame (commonly a single 0=success byte) rather than an echoed value; not stated as a confirmed byte sequence here to avoid inventing evidence.

## 0x3D — Saturation Get

_Not decoded._ The ground-station app queries the camera's current saturation adjustment to populate the Color Settings panel UI on connect. Handler correctly identified (Same UsCtrl_Map_CmdId / UsCtrl_Query_TagSize / UsCtrl_Query_TagType chain as 0x3C, usctrl_index 37), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3E — Hue Set

_Not decoded._ Searched: (1) librcam.so's complete, ordered 82-entry 'UsCtrlId_Set_<Name>' debug-string table (.rodata vaddr 0x34dfe onward, the same table that resolved Saturation/Denoising below) -- NO entry named Hue, HueAdjust, or anything hue-related anywhere in the 82 names. (2) The same library's 126-row UsCtrl_Map_CmdId internal-id table (vaddr 0x205698) -- the ~82 resolvable rows' target names were cross-checked against the string list with the same negative result. (3) bin/dji_camera3's OWN, separate, disassembly-confirmed 105-entry generic-parameter registration table (passed into service_init() at startup, see 0x3C's evidence) DOES contain an exact-name entry 'hue' (param_id 0x2000027) -- so Hue is a real, implemented ISP parameter on this camera module, just evidently NOT reached through librcam.so's UsCtrl mechanism (unlike Saturation/Denoising, which appear in BOTH tables). This is consistent with Hue being handled purely within dji_camera3's own color-pipeline/libdcam_pp.so path rather than being forwarded to librcam's lens/sensor-centric UsCtrl dispatcher. (4) No literal duss_event_register_dynamic_command call carrying cmd_set=2/cmd_id=0x3E was found in dji_camera3, librcam.so, libdcam_cs_cbb.so, or the 120+ runtime camera plugins. Net result: Hue is confirmed real/live on this firmware (per dji_camera3's table), but no function that parses its byte-level Set/Get payload was located in this pass, and no field-width evidence (the thing UsCtrl's Query_TagSize table gave us for Saturation/Denoising) exists for it. Not guessed rather than reported with an invented layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3F — Hue Get

_Not decoded._ Same investigation and same result as 0x3E Hue Set (see that entry) -- Get and Set were searched together since they are the same parameter family. 'hue' is confirmed as a real registered parameter name in dji_camera3's generic param table (id 0x2000027) but has no corresponding entry in librcam.so's UsCtrl size/type table, so no byte-width evidence could be obtained for either direction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x40 — Face Detect Set

_Not decoded._ Exhaustively searched for any trace of a face-detection camera parameter across every binary this pass examined, and found none: (1) bin/dji_camera3's complete 105-entry generic-parameter table (the same disassembly-confirmed table that resolved saturation/hue/digital_effect/denoising) has no entry named face_detect, facedetect, face, or fd_* anywhere in its 105 rows. (2) librcam.so's complete 82-entry UsCtrlId_Set_<Name> table (same one that resolved Saturation/Denoising) has no Face-related entry either. (3) A raw case-insensitive 'face' string search across bin/dji_camera3, lib64/librcam.so, lib64/libdcam_cs_cbb.so, lib64/libdcam_base.so, lib64/libaaa.so (the AE/AWB/AF algorithm library -- the most likely place subject/face detection logic would live if present) and all lib64/camera/plugins/*.so returned zero genuine hits; the handful of raw grep matches in librcam.so/libaaa.so/etc. were confirmed to be false positives, all substring matches inside the unrelated word 'interface'. (4) No literal duss_event_register_dynamic_command call carrying cmd_set=2/cmd_id=0x40 was found anywhere. This is a clean, multi-source negative result, structurally identical to this project's own prior precedent of declaring a whole feature 'confirmed not implemented on this firmware generation' (see 21_PAYLOAD_DECODE_SWEEP_FINDINGS.md's cmd_set 0x08/DM36x section) -- consistent with real-world knowledge that the Mavic 3's camera module ('Seal', per dji_camera3's own boot-log string 'DJI Camera Service for Seal is starting...') does not expose a user-facing face-detection toggle, unlike some other DJI consumer products. Reported as insufficient_evidence (no handler located) rather than a stronger claim, since absence-of-evidence in a large-but-not-100%-exhaustive binary set is not proof of non-existence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x41 — Face Detect Get

_Not decoded._ Same exhaustive, multi-source negative search as 0x40 Face Detect Set (see that entry for full detail) -- Get and Set were investigated together. No trace of a face-detection parameter found in any of the checked tables, strings, or registration mechanisms across dji_camera3, librcam.so, or the full camera plugin set. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x42 — Digital Effect Set

_Not decoded._ Searched the same way as Hue (0x3E/0x3F): bin/dji_camera3's disassembly-confirmed 105-entry generic-parameter registration table (passed into service_init() at startup) DOES contain an exact-name entry 'digital_effect' (param_id 0x2000029), immediately adjacent to 'wb' (0x2000029-1) and 'codec_type' (0x200002a+1) in the table's ISP-pipeline-ordered layout -- confirming this is a real, live parameter on this camera module. However, librcam.so's complete 82-entry UsCtrlId_Set_<Name> table/Map_CmdId/Query_TagSize mechanism (the one that gave hard field-width evidence for Saturation and Denoising below) has no entry named Effect, DigitalEffect, Filter, or similar anywhere in its 82 rows. No literal duss_event_register_dynamic_command call carrying cmd_set=2/cmd_id=0x42 was found in any checked binary. As with Hue, this parameter is confirmed real but is evidently applied through dji_camera3's own internal path (likely directly into libdcam_pp.so's pixel-processing pipeline) rather than librcam's sized UsCtrl dispatcher, so no byte-width/type evidence could be obtained. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x43 — Digital Effect Get

_Not decoded._ Same investigation and same result as 0x42 Digital Effect Set (see that entry) -- 'digital_effect' is confirmed as a real registered parameter name in dji_camera3's generic param table (id 0x2000029) but has no corresponding entry in librcam.so's sized UsCtrl table, so no byte-width evidence could be obtained for either direction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x44 — Digital Denoise Set

_Not decoded._ The app enables a medium level of digital (ISP) noise reduction before a low-light video shoot. Handler correctly identified (UsCtrl_Map_CmdId (vaddr 0x44330) -> 126-entry internal-id table at vaddr 0x205698 -> usctrl_index 39 -> UsCtrl_Query_TagSize/UsCtrl_Query_TagType (vaddr 0x7b0b8/0x7b320) -> table at vaddr 0x2b1b68, entry 39), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x45 — Digital Denoise Get

_Not decoded._ The app queries the camera's current digital denoise level for display in the video settings panel. Handler correctly identified (Same UsCtrl_Map_CmdId / UsCtrl_Query_TagSize / UsCtrl_Query_TagType chain as 0x44, usctrl_index 39), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x46 — Anti Flicker Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_set_anti_flicker (vaddr 0x92fb0, 660 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `anti_flicker_mode` (Anti-Flicker Mode) | uint8 | Validated 0-3 (ldrb+cmp #4,b.hs reject); any value >=4 is rejected by the handler before being forwarded to the sensor/AE layer. |

**Worked example:**

- Request payload: `01`
  1-byte payload: anti_flicker_mode = 0x01.
- Response payload: `00`
  Inferred, not independently disassembled at the wire level: the handler returns a C int status (0 = success) from its own body; by this project's established convention for simple Set acks, the generic DUML wrapper most likely turns that into a 1-byte status/result code (00 = success) in the ack payload. Flagging this response byte as inferred-by-convention, not directly observed.

## 0x47 — Anti Flicker Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_get_anti_flicker (vaddr 0xa2c68, 556 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `anti_flicker_mode` (Anti-Flicker Mode) | uint8 | Current anti-flicker mode, same 1-byte enum as the Set command's payload (strb-widths match on both sides). |

**Worked example:**

- Request payload: ``
  No request payload -- the Get handler's second argument is write-only; nothing is read from it.
- Response payload: `02`
  1-byte response: anti_flicker_mode = 0x02 (the camera is currently set to mode 2 of the 4 valid values).

## 0x48 — Multi Cap Param Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_set_capture_multicap_param (vaddr 0x91bc8, 780 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `multicap_count` (Multi-Capture Count/Selector) | uint32 | Read as a 4-byte little-endian word on the wire (ldr, not ldrb) but range-checked to 0-255 and truncated to 1 byte before use internally -- almost certainly a burst-shot count/selector (DJI camera UIs commonly expose burst options like 3/5/7/10/14 photos). The exact enumerated value set was not recovered (no switch/table on the value was found in this handler; it is opaquely forwarded to the underlying sensor/capture-strategy layer). |

**Worked example:**

- Request payload: `05 00 00 00`
  4-byte little-endian uint32: multicap_count = 5.
- Response payload: `00`
  Inferred success-ack byte (see 0x46's note on this convention); not independently confirmed at the wire level.

## 0x49 — Multi Cap Param Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_get_capture_multicap_param (vaddr 0xa1e40, 672 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `multicap_count` (Multi-Capture Count/Selector) | uint32 | Mirrors the Set payload's field exactly (same property id, same internal 1-byte value zero-extended to a 4-byte wire field). |

**Worked example:**

- Request payload: ``
  No request payload.
- Response payload: `05 00 00 00`
  4-byte response mirroring the value set in the 0x48 example (multicap_count = 5).

## 0x4A — Conti Cap Param Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_set_capture_conticap_param (vaddr 0x91848, 892 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `conticap_type` (Continuous-Capture Type/Mode) | uint32 | Validated 0-3 by the handler (cmp #4,b.hs reject). Plausibly selects the sub-mode of legacy continuous/interval shooting (distinct from the separately-named timelapse_param/motionlapse_param/hyperlapse_param generic params found elsewhere in dji_camera3, which appear to be newer, separate features). |
  | 4 | 4 | `conticap_count` (Shot Count) | uint32 | Validated 0-255 by the handler (cmp #0x100,b.hs reject). Most plausibly the number of shots to take (0 may mean 'unlimited/continuous until stopped', consistent with common DJI UI semantics, but not confirmed by this disassembly). |
  | 8 | 2 | `conticap_interval` (Interval/Period) | uint16 | Read unconditionally in both code paths, no bounds check observed. Most plausibly the time interval between shots (units not determinable from this disassembly -- likely seconds or deciseconds by convention with similar DJI params). |
  | 10 | 2 | `conticap_param4` (Unknown/Reserved uint16) | uint16 | Read unconditionally alongside conticap_interval, no bounds check observed, no distinguishing name evidence found for its specific role. |

**Worked example:**

- Request payload: `01 00 00 00 0A 00 00 00 02 00 00 00`
  12-byte payload: conticap_type=1 (offset0,u32), conticap_count=10 (offset4,u32), conticap_interval=2 (offset8,u16), conticap_param4=0 (offset10,u16).
- Response payload: `00`
  Inferred success-ack byte; not independently confirmed at the wire level.

## 0x4B — Conti Cap Param Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_get_capture_conticap_param (vaddr 0xa1bb8, 648 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `conticap_type` (Continuous-Capture Type/Mode) | uint32 | Mirrors the Set field; 0-3. |
  | 4 | 4 | `conticap_count` (Shot Count) | uint32 | Mirrors the Set field; 0-255. |
  | 8 | 2 | `conticap_interval` (Interval/Period) | uint16 | Mirrors the Set field. |
  | 10 | 2 | `conticap_param4` (Unknown/Reserved uint16) | uint16 | Mirrors the Set field. |

**Worked example:**

- Request payload: ``
  No request payload.
- Response payload: `01 00 00 00 0A 00 00 00 02 00 00 00`
  12-byte response mirroring the 0x4A example exactly (general-path layout, not the type=0/count=1 fast path).

## 0x4C — Hdmi Output Param Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_set_hdmi_output_mode (0x9f6d0, 656B), cam_event_handler_set_hdmi_output_fmt (0x9f960, 1044B), cam_event_handler_set_hdmi_output_area (0x9fd78, 652B)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `hdmi_output_mode` (HDMI Output Mode) | uint32 | Confirmed valid range 0-2 from the setter's own bounds check; wire width of 4 bytes inferred from the GET handler's 'str w8' (full-word) response write, by symmetry with every other Set/Get pair in this batch. |
  | 4 | 4 | `hdmi_output_fmt_1` (HDMI Output Format field 1) | uint32 | Confirmed valid range 0-96 by the fmt setter; confirmed round-trip via the fmt getter. |
  | 8 | 4 | `hdmi_output_fmt_2` (HDMI Output Format field 2) | uint32 | Confirmed valid range 0-28. |
  | 12 | 4 | `hdmi_output_fmt_3` (HDMI Output Format field 3) | uint32 | Confirmed valid range 0-5. |
  | 16 | 4 | `hdmi_output_fmt_4` (HDMI Output Format field 4) | uint32 | Confirmed valid range 0-3. |
  | 20 | 4 | `hdmi_output_area` (HDMI Output Area (packed)) | uint32 | No bounds check observed; the handler's own debug log splits it into two uint16 halves for printing, suggesting an internal {u16,u16} pair (plausibly crop width/height or x/y offset), but this is not independently confirmed. |

**Worked example:**

- Request payload: `01 00 00 00 0A 00 00 00 05 00 00 00 02 00 00 00 01 00 00 00 00 00 00 00`
  Best-evidence 24-byte reconstruction (see caveat above): hdmi_output_mode=1 @0, fmt_1=10 @4, fmt_2=5 @8, fmt_3=2 @12, fmt_4=1 @16, area=0 @20.
- Response payload: `00`
  Inferred success-ack byte; not independently confirmed.

## 0x4D — Hdmi Output Param Get

_Not decoded._ The app queries the current HDMI output mode and format settings. Unlike 0x4C, there is no confirmed internal getter for the 'area' sub-property at all, so this response is reported as 20 bytes (mode+fmt only), not 24 -- a deliberately narrower, better-evidenced claim than 0x4C's Set-side reconstruction. Handler correctly identified (cam_event_handler_get_hdmi_output_mode (0xab5a0, 672B), cam_event_handler_get_hdmi_output_fmt (0xab840, 700B); NOTE: no cam_event_handler_get_hdmi_output_area function exists anywhere in this library (confirmed by a full symbol-table grep) -- only a 'set' exists for 'area'.), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4E — Quickview Param Set

_Not decoded._ Could not determine a payload layout -- no handler, no related string, and no generic-parameter-table entry was found anywhere in either firmware image for this command. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4F — Quickview Param Get

_Not decoded._ Could not determine a payload layout -- same findings as 0x4E. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x50 — OSD Param Set

_Not decoded._ No literal (cmd_set=2, cmd_id=0x50) registration exists anywhere in either firmware image. Exhaustively checked: (1) dji_camera3 (the e2/AArch64 daemon this project's own doc 01/04 names as the Camera owner) imports ZERO duss_event_*/duss_mb_*/duss_dsh_* DUML-registration symbols at all (full .dynsym dump) -- it is not a DUML registrar in its own right. (2) librcam.so (the shared lib dji_camera3-family binaries link) was fully recovered via its .gnu_debugdata minidebuginfo (5441 symbols) and does not import duss_event_register_dynamic_command/_table either; its one internal numeric dispatcher, rcam_cmd (vaddr 0x51968), switches on three 32-bit constants (0x44140018, 0x44150018, 0xc4130210) that do not decode as (cmd_set,cmd_id) under this project's established literal-immediate convention (verified against 4 independently-confirmed pairs elsewhere) -- these are internal DUSS event-type IDs, not wire cmd_ids. (3) Enumerated and checked ALL 15 of librcam.so's non-libc DT_NEEDED libraries (libduml_osal/util/frwk/hal, libdcam_base/container/fcali/iq_module, libcutils, lib_gdc_creategrid, libz, libaaa, libsensor_imx686, plus dji_camera3's own extra deps libdcam_cs_cbb/pp) for duss_event_register_dynamic_command(_table)/duss_register_cmd-equivalents: none import it except dji_sys (unrelated binary) and the googletest harness. (4) Personally disassembled all 12 of dji_sys's own duss_event_register_dynamic_command call sites (PLT at 0xffd0) in e2 dji_sys -- 9 use compile-time-literal (cmd_set,cmd_id) collapsing to exactly {0x22/0x60, 0x00/0xa3, 0x06/0x3a, 0x04/0x69}, none is cmd_set 0x02. (5) dji_flight's (e1e-only) fully re-dumped 44-row relocated dispatch array (vaddr 0xae038-0xae190) contains exactly 3 cmd_set-0x02 rows (0x80, 0x81, 0x87 -- all unrelated already-decoded push/state commands), not 0x50. Architecturally, found a strong but unconfirmed lead: libdcam_cs_cbb.so's local function cs_proxy_manager_uni_set (vaddr 0xd698) is a generic numeric-ID parameter setter that forwards to usm_set in libdcam_usm_v2.so, and this whole 'User Setting Manager' (USM v2) subsystem's actual ID<->name<->type table is proven (via usf_json_parse/_usm_check_usf_file/user_setting_filename strings) to be loaded at runtime from an external 'USF' JSON config file that is NOT present in this firmware extraction -- the same 'config file absent from extraction' gap this project already hit for dji_sys's Param Manager (doc 21) and command-agent JSON (doc 04). OSD overlay settings are an extremely plausible fit for a persisted 'user setting', but no code was found that ties DUML cmd_id 0x50 specifically to a us_id value, so this cannot be reported as a resolved layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x51 — OSD Param Get

_Not decoded._ Sibling of 0x50; same exhaustive negative search applies (no binary registers cmd_set 0x02/0x51 via any of this project's known mechanisms). If this command follows the same uni_get->usm_get->USM-v2 path hypothesized for its Set sibling, the same missing-USF-JSON-file gap blocks resolution. Separately noted for documentation purposes: by this protocol's own convention elsewhere in commands.json (e.g. the confirmed 0x00/0x4B 'Get Date/Time' sibling pair), a '...Get' request is typically an empty-payload query and the real field layout of interest lives in the ACK/response -- but since no handler was found at all, neither the request's triviality nor the response's layout can be confirmed here, only assumed by analogy, which this project's rules say not to report as a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x52 — Preview OSD Param Set

_Not decoded._ Same base negative result as 0x50 (no registrar anywhere for cmd_set 0x02/0x52). Additionally checked whether 'Preview' OSD (the live Wi-Fi/HDMI preview feed's overlay, architecturally distinct from the recorded-video OSD of 0x50/0x51) might be owned by a separate display/overlay-specific binary: checked libdcam_disp_wm260.so, libdcam_wm_multi.so (watermark plugin), libdcam_wm260_lcdc_link_node.so, and libOmxDispSink.so/libOmxCamDispEngSink.so via nm -D for any duss_event_*/duss_mb_*/duss_dsh_* import -- none of them import any DUML registration API, consistent with these being pure rendering backends invoked through whatever upper-layer command dispatch remains unresolved (the same uni_set/usm_set/USF-JSON gap noted for 0x50), rather than independent DUML registrars. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x53 — Preview OSD Param Get

_Not decoded._ Sibling of 0x52; same negative result and same reasoning (no registrar found; display-backend libraries checked and ruled out as independent registrars; likely routed through the same unresolved, USF-JSON-config-driven uni_get path as 0x51, if the USM-v2 hypothesis is even correct). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x54 — Camera Date/Time Set

_Not decoded._ No cmd_set-0x02/0x54 registration found by any mechanism. Specifically checked whether this is secretly handled by dji_sys's already-confirmed System Date/Time handler (sys_event_set_date, cmd_set 0x00/0x4A, byte-decoded struct-tm layout already in commands.json): personally re-enumerated and disassembled ALL 12 of dji_sys's duss_event_register_dynamic_command call sites in the e2 binary and confirmed cmd_set is never 0x02 at any of them (the 9 literal sites collapse to exactly {0x22/0x60, 0x00/0xa3, 0x06/0x3a, 0x04/0x69}; the 2 remaining data-driven sites pull from runtime-populated tables that doc 21 already ties to the cmd_set-0x00 Param Manager family, not Camera) -- so sys_event_set_date is confirmed System-clock-only, not shared with this camera-specific command. Also searched librcam.so's full 5441-symbol minidebuginfo and dji_camera3/libdcam_cs_cbb.so for date/time/RTC/clock-named functions: the only hits (DjiSys_Time_GetMS, DjiSys_Timer_Create/Start/Stop/Destroy in librcam.so) are generic millisecond-timer utility primitives, not a date-set handler. A dedicated camera-side RTC-sync command (for EXIF/video-timestamp sync, independent of the flight controller's system clock) is architecturally plausible and, if DJI reused their own date/time wire convention, would likely resemble the confirmed 0x00/0x4A layout (year uint16 LE / month u8 / day u8 / hour u8 / minute u8 / second u8, possibly + tz offset) -- but this is stated explicitly as an unconfirmed analogy from a sibling command in a different cmd_set, not a traced finding, and is not reported as a decode per this project's rules. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x55 — Camera Date/Time Get

_Not decoded._ Sibling of 0x54; same result. Also confirmed dji_sys's sys_event_rtc_get_date (the General cmd_set 0x00/0x4B handler) is not reachable from any cmd_set-0x02 registration, for the same reason given for 0x54 (complete re-verified enumeration of dji_sys's 12 registration call sites). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x56 — Language Param Set

_Not decoded._ No cmd_set-0x02/0x56 registration found anywhere. Searched specifically for 'language'/'lang'-named functions or strings across librcam.so's full recovered symbol table (5441 entries), libdcam_cs_cbb.so, libdcam_frwk.so, and dji_camera3 itself: zero hits in any of them. Language selection is a classic persisted-config 'user setting' (like OSD), so it most plausibly routes through the same unresolved cs_proxy_manager_uni_set -> usm_set -> USF-JSON-config pipeline documented under 0x50, but no code ties cmd_id 0x56 to a specific us_id, and the id<->name mapping table itself is proven to live in an external USF JSON file absent from this extraction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x57 — Language Param Get

_Not decoded._ Sibling of 0x56; identical negative result and identical reasoning (no handler, no 'language' string/symbol hit anywhere searched, likely-but-unconfirmed USM/USF routing). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x58 — Camera GPS Set

_Not decoded._ No cmd_set-0x02/0x58 registration found anywhere, and unlike the other 8 commands in this batch this one does not obviously fit the 'persisted user setting' (USM/USF) hypothesis at all, since GPS is externally-sourced live telemetry rather than a stored config value -- so that lead does not apply here. Searched specifically for GPS-related handlers: dji_camera3, librcam.so (full symbol recovery), libdcam_base.so, and libdcam_metadata_util.so all have zero GPS-named exported or local functions. The only GPS-named artifact found anywhere in the entire camera library set is GpsBasic_fields / _fill_metadata_gps_basic in libdcam_protobuf_metadata.so -- a nanopb-generated protobuf message schema (sitting alongside sibling schemas ISO_fields, Gyroscope_fields, GimbalMode_fields in the same library) used for the camera's internal metadata/telemetry logging track. Following this project's own established caution about superficially-similar internal schemas (doc 21's dji_perception/dji_flightsystem_msgs ROS-schema dead-end for RC cmd 0x50), this is explicitly NOT confirmed to be the DUML wire-payload format for cmd_id 0x58/0x59 -- a real DJI internal data model existing in a binary is not proof it is what travels over this specific wire command, and no cross-reference from this protobuf schema back to a DUML cmd_set/cmd_id was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x59 — Camera GPS Get

_Not decoded._ Sibling of 0x58; identical negative result and identical reasoning (no handler found; the GpsBasic protobuf schema in libdcam_protobuf_metadata.so is a plausible-looking but explicitly unconfirmed internal-telemetry lead, not evidence of this command's wire layout). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x5A — Discon State Set

_Not decoded._ Searched exhaustively across the e2 (aarch64) camera stack for any handler, config key, or debug-log field tied to a 'Discon'/'disconnect'/connection-state concept inside cmd_set 0x02 scope, and found none. Checked: (1) dji_camera3's full internal parameter-name table (105 'mode_profile' keys, vaddr 0x20028-0x206a8, dumped byte-for-byte via relocation-confirmed string pointers) -- no discon/connect-like key. (2) libdcam_camera_service_server.so's full demangled dynamic symbol list (~1444 names, including ~200 cam_event_handler_set_*/get_* pairs covering nearly every other ISP parameter in this cmd_set) -- no Discon/Connect-named handler. (3) libdcam_cs_duss_proxy.so's exhaustive 'CamPusherMonitor: CamParm.*' (50 fields) and 'CamPusherMonitor: CamStat.*' (31 fields) debug-label lists, which independently reproduce nearly the entire existing Camera State Info (cmd 0x80) push struct field-for-field (WifiCon, TimeSync, SdInserted, FileIndexMode, Histogram, etc.) -- the only connectivity-adjacent field present is 'WifiCon' (Wi-Fi connected), nothing named Discon. (4) libdcam_cs_cbb.so, libdcam_cs_cbb_storage.so, libdcam_cs_camera_state.so, libdcam_storage.so, libdcam_storage_dev.so, libdcam_cs_storage_mgr_server.so, libdcam_audiodev.so, libdcam_pbdev.so -- no 'discon' string in any. (5) dji_flight's (e1e, 32-bit) relocated {fn_ptr, cmd_word} dispatch array, fully re-parsed from raw bytes (44 rows at vaddr 0xae038-0xae190, row format confirmed as w0=relocated fn_ptr, w1 low byte=cmd_set, high byte=cmd_id -- independently reproduces every previously-documented row in this project's docs, e.g. 0x22/0x06,0x07,0x08,0x44): its only cmd_set-0x02 rows are cmd_id 0x80 (Camera State Info), 0x81 (Camera Shot Params), 0x87 -- none near 0x5a/0x5b. No candidate function or string tied this cmd_id to any real code path. Not invented; left unresolved. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x5B — Discon State Get

_Not decoded._ Same exhaustive search as 0x5a (Set); this is the paired Get command with identical negative result across the same binaries/mechanisms. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x5C — File Index Mode Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cs_storage_manager_set_file_index_mode (vaddr 0x1cb10, 24-byte thunk)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `file_index_mode` (File Index Mode) | uint8 | Whether new captured files restart numbering from 1 or keep a continuous running index. |

**Worked example:**

- Request payload: `550e04660201010140025c018002`
  App(sender type 2) -> Camera(receiver type 1), seq=0x0101, ack=After-Exec, cmd_set=0x02, cmd_id=0x5c, payload=[0x01] (set mode to Sequence).
- Response payload: `550e046601020101c0025c00d91c`
  Camera -> App, same seq, packet_type=Response, payload=[0x00] (ack/return-code OK; this cmd pair is ack-only on Set, the current mode is read back via 0x5d).

## 0x5D — File Index Mode Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cs_storage_manager_get_file_index_mode (vaddr 0x1cb28, 24-byte thunk)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `file_index_mode` (File Index Mode) | uint8 | Current file-numbering mode, request payload is empty. |

**Worked example:**

- Request payload: `550d04330201020140025de741`
  App -> Camera, seq=0x0102, cmd_id=0x5d, zero-length request payload (a plain Get).
- Response payload: `550e046601020201c0025d01f518`
  Camera -> App, payload=[0x01] (current mode is Sequence).

## 0x5E — AE bCap Param Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_set_capture_aeb_param (vaddr 0x91520, 804 bytes); internal type dji::CameraAEBParams / struct camera_aeb_param`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `expo_offset` (AEB EV Step) | uint8 | Exposure-bracketing EV step/mode selector; the real handler enforces this value is in [1,10] or [101,108] (two disjoint enum ranges, exact per-value EV meaning not separately enumerated in this binary). |
  | 1 | 1 | `count` (Bracket Shot Count) | uint8 | Number of frames in the AEB burst (e.g. 3/5/7/9 on typical DJI cameras); handler only confirms it is a single byte, not a specific enum set. |

**Worked example:**

- Request payload: `550f04a20201030140025e030550a4`
  App -> Camera, seq=0x0103, cmd_id=0x5e, payload=[0x03, 0x05]: expo_offset=3 (a representative EV-step enum value), count=5 (5-frame AEB burst).
- Response payload: `550e046601020301c0025e003f27`
  Camera -> App, payload=[0x00] (ack OK).

## 0x5F — AE bCap Param Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: cam_event_handler_get_capture_aeb_param (vaddr 0xa1988, 556 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `expo_offset` (AEB EV Step) | uint8 | See 0x5e. |
  | 1 | 1 | `count` (Bracket Shot Count) | uint8 | See 0x5e. |

**Worked example:**

- Request payload: `550d04330201040140025f6d59`
  App -> Camera, seq=0x0104, cmd_id=0x5f, zero-length request (plain Get).
- Response payload: `550f04a201020401c0025f030516ef`
  Camera -> App, payload=[0x03, 0x05]: current expo_offset=3, count=5.

## 0x60 — Histogram Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _histogram_set_histogram_op / _get_histogram_op (libdcam_histogram_filter.so); _cs_cam_duss_proxy_on_set_histogram_op / _on_get_histogram_op (libdcam_cs_duss_proxy.so)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `histogram_op` (Histogram Operation) | uint8 | Enable/disable (and possibly select a display mode for) the live-view histogram overlay. Confirmed single-byte scalar; confirmed meaning for value 0/1 (off/on) by analogy with the existing 'Histogram Enable' push-state bit; no further enum values located. |

**Worked example:**

- Request payload: `550e046602010501400260012e0d`
  App -> Camera, seq=0x0105, cmd_id=0x60, payload=[0x01] (turn histogram overlay on).
- Response payload: `550e046601020501c00260007713`
  Camera -> App, payload=[0x00] (ack OK).

## 0x61 — Histogram Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _get_histogram_op (libdcam_histogram_filter.so); _cs_cam_duss_proxy_on_get_histogram_op (libdcam_cs_duss_proxy.so)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `histogram_op` (Histogram Operation) | uint8 | Current histogram overlay state; request payload is empty. |

**Worked example:**

- Request payload: `550d0433020106014002611897`
  App -> Camera, seq=0x0106, cmd_id=0x61, zero-length request.
- Response payload: `550e046601020601c00261015b17`
  Camera -> App, payload=[0x01] (histogram currently on).

## 0x62 — Video Subtitles Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _cs_cam_duss_proxy_on_set_v_subtitles (tag string referenced from the proxy's generic per-key event dispatcher); underlying field consumed by cs_cam_pusher_monitor_push_msg's debug dump and by _camdev_apply_v_subtitles (libdcam_camdev.so)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `subtitle_src_camera` (Include Camera Telemetry) | bitfield | bit0: embed camera/ISP parameter telemetry (ISO, shutter, aperture, etc.) in the subtitle track. |
  | 0 | 1 | `subtitle_src_mc` (Include Flight-Controller Telemetry) | bitfield | bit1: embed flight-controller (MC) telemetry (GPS, attitude, speed, etc.). |
  | 0 | 1 | `subtitle_src_gimbal` (Include Gimbal Telemetry) | bitfield | bit2: embed gimbal attitude/mode telemetry. |
  | 0 | 1 | `subtitle_src_hdvt` (Include Video-Link Telemetry) | bitfield | bit3: embed HD video transmission (downlink) link-quality telemetry. |
  | 0 | 1 | `subtitle_src_dm368` (Include Legacy Encoder Telemetry) | bitfield | bit4: embed legacy DM368 video-encoder telemetry; vestigial on this product generation. |
  | 0 | 1 | `subtitle_reserved` (Reserved) | bitfield | bits5-6: reserved, 2 bits wide. |
  | 0 | 1 | `subtitle_op` (Subtitle Master Enable) | bitfield | bit7: master on/off switch for subtitle-track embedding as a whole. |

**Worked example:**

- Request payload: `550e04660201070140026287f6d7`
  App -> Camera, seq=0x0107, cmd_id=0x62, payload=[0x87] = 0b10000111: bit7(Op)=1, bit2(Gimbal)=1, bit1(MC)=1, bit0(Camera)=1, bit3(HDVT)=0, bit4(DM368)=0 -- enable subtitle embedding with camera+flight-controller+gimbal telemetry sources, downlink/legacy-encoder sources off.
- Response payload: `550e046601020701c00262009128`
  Camera -> App, payload=[0x00] (ack OK).

## 0x63 — Video Subtitles Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _cs_cam_duss_proxy_on_get_v_subtitles`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `subtitle_src_camera` (Include Camera Telemetry) | bitfield | bit0, see 0x62. |
  | 0 | 1 | `subtitle_src_mc` (Include Flight-Controller Telemetry) | bitfield | bit1, see 0x62. |
  | 0 | 1 | `subtitle_src_gimbal` (Include Gimbal Telemetry) | bitfield | bit2, see 0x62. |
  | 0 | 1 | `subtitle_src_hdvt` (Include Video-Link Telemetry) | bitfield | bit3, see 0x62. |
  | 0 | 1 | `subtitle_src_dm368` (Include Legacy Encoder Telemetry) | bitfield | bit4, see 0x62. |
  | 0 | 1 | `subtitle_reserved` (Reserved) | bitfield | bits5-6, see 0x62. |
  | 0 | 1 | `subtitle_op` (Subtitle Master Enable) | bitfield | bit7, see 0x62. |

**Worked example:**

- Request payload: `550d043302010801400263b2d5`
  App -> Camera, seq=0x0108, cmd_id=0x63, zero-length request.
- Response payload: `550e046601020801c002638777fc`
  Camera -> App, payload=[0x87] (same bitmask value as the 0x62 example: Op+Camera+MC+Gimbal enabled).

## 0x64 — Video Subtitles Log Set

_Not decoded._ Searched dji_camera3's own internal USM settings table (fully reverse-engineered, see shared_infrastructure_found): it has a 'v_subtitles' key (usm_id 0x2000016), but that corresponds to the already-catalogued, separate cmd_set 0x02 0x62/0x63 'Video Subtitles Set/Get' toggle, not this distinct '...Log' variant. Grepped the whole e2 firmware tree for subtitle+log/gps/osd combinations with no further hits. No handler reachable via any of the DUSS registration mechanisms exhaustively searched (see shared_infrastructure_found) references cmd_id 0x64. Architecturally, a 'subtitle log' push is more likely a variable-length streamed per-frame telemetry/OSD text blob (DJI's SRT-style burn-in data: GPS/alt/ISO/shutter/etc. per frame) than a small fixed struct, which would make it a poor fit even if a handler were found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x65 — Mgear Shutter Speed Set

_Not decoded._ No string containing 'mgear' (case-insensitive) exists anywhere in either the e1e (32-bit ARM) or e2 (AArch64) firmware extraction - confirmed by a full-tree grep. Checked dji_camera3's USM settings table (has plain 'shutter_speed', 'shutter_type', 'shutter_angle' keys but nothing gear-qualified) and librcam.so's full UsCtrlId_* enum string list (has UsCtrlId_Set_IrisStill/IrisVideo and others but no mechanical-gear-ring-specific shutter control). No handler for cmd_id 0x65 found by any searched mechanism. 'Mgear' most plausibly denotes a mechanical aperture/shutter control ring hardware feature (seen on some other DJI camera modules) that either isn't compiled into this WM260/Mavic 3 image, or is handled by code with no distinguishing strings this pass could locate. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x66 — Video Standard Set

_Not decoded._ Strongest lead in this batch, but still short of an actual wire-parser disassembly. dji_camera3's internal USM (user-setting-manager) settings-registration table - independently reverse-engineered row-by-row from .data, see shared_infrastructure_found - contains a row {key string "video_standard" at .rodata vaddr 0x501b, usm_key_id 0x2000017} at table row vaddr 0x20178. This confirms 'video_standard' is a real, individually-tracked, integer-valued persisted camera setting with a name matching this command exactly. However, the bridge code that would convert an incoming DUML cmd_set 0x02/cmd_id 0x66 payload into a write of this USM key was not located: it plausibly runs through libdcam_cs_cbb.so's exported but internally-opaque usm_register_apply_tbl/proxy_manager_user_setting_apply chain, which this pass confirmed exists but could not disassemble to the point of recovering a per-cmd_id mapping in the time available. Per instructions, not asserting a byte offset/size/enum mapping (e.g. NTSC=0/PAL=1) without having actually seen the wire-parsing code - that specific encoding was not found in this firmware. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x67 — Video Standard Get

_Not decoded._ Same USM-table evidence as 0x66 (Set) applies: the paired Get almost certainly reads the same 'video_standard' USM key back out. Same gap: the DUML-to-USM bridge code was not disassembled, so no byte offset/size can be asserted. See 0x66's entry for full detail - not duplicated here to avoid padding. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x68 — AE Lock Status Set

_Not decoded._ Second-strongest lead in the batch, from two independent binaries. (1) dji_camera3's USM table has a row {key string "ae_lock" at .rodata vaddr 0x5095, usm_key_id 0x2000023} at table row vaddr 0x20238 - same table and method as 0x66/0x67. (2) librcam.so (confirmed reachable from dji_camera3's full transitive dependency graph via libduml_hal_cam.so, though see shared_infrastructure_found for why librcam's *own* DUSS client registration is NOT reachable from dji_camera3 in practice) independently contains the strings 'UsCtrlId_Set_AeLock', '_DjiAAA_CmdMgr_AE_AeLock', and the log format '[rcam]: [%s][%s:%d][ch:%d]AeLock:%d' - the trailing %d confirms AE-lock state is handled as a plain scalar integer in that engine's own (differently-numbered) internal control-ID API. Neither binary's actual DUML-cmd_id-0x68-keyed wire parser was located/disassembled, so no byte offset, size, or 0/1 polarity convention is asserted as confirmed - only that the underlying concept is a real, simple, scalar setting. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x69 — AE Lock Status Get

_Not decoded._ Same corroborating evidence as 0x68 (Set) applies to the paired Get. See 0x68's entry for full detail - not duplicated here. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6A — Photo Capture Type Set

_Not decoded._ Found a real, firmware-verified 2-valued enum bound - CAPTURE_TYPE_MAX = 2, disassembled directly as `cmp w9, #0x2; b.cs <assert-fail>` guarding `aeb_param->to_capture_type` (loaded from offset 24 of an AEB-bracketing parameter struct) in libdcam_shooter_still_common.so / libdcam_shooter_still_general.so / libdcam_shooter_still_yuvraw_zsl.so - plus a related string 'DCF_ST_CAPTURE_TYPE' in libdcam_fnm_dcf.so (DCF file-naming module). Both are explicitly narrower, adjacent concepts: the AEB one is a 2-valued sub-field of the Multi/AEB-capture parameter struct already covered by this cmd_set's separate 0x48/0x49 ('Multi Cap Param') and 0x4a/0x4b ('Conti Cap Param') commands, not the general per-shot capture-type selector this command's name implies (which by general DJI SDK convention is a broader ~8-12-value enum: Single/HDR/Burst/Interval/Panorama/etc. - noted here only as background context, NOT firmware-verified, so not used as a basis for any field claim). No handler keyed to cmd_id 0x6a itself was found by any searched mechanism. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6B — Photo Capture Type Get

_Not decoded._ Same search and same adjacent-but-non-matching leads as 0x6a (Set) apply. See 0x6a's entry for full detail. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6C — Video Record Mode Set

_Not decoded._ Found a real internal 'record mode' state-machine function. libdcam_cs_topmode_common_video.so's exported cs_topmode_common_video_create contains an inlined static helper (logged under the literal name '_init_record_mode', located by string xref and fully disassembled) that loads a BYTE-sized field (`ldrb w22, [x21, #305]`) from a per-camera-session state struct and switches on it over the range 0-0x28 (0-40 decimal: `cmp w22,#0x28; b.hi <default>` feeding a 41-entry relocated jump table) into calls like camdev_set_rec_op / camdev_set_shoot_mode / camdev_set_lowlight_video_mode. This confirms the firmware's internal video record/shoot-mode concept is represented as a single byte with up to ~41 internal states - architecturally consistent with a compact DUML wire encoding, but NOT proof of one: no xref from any DUML-reachable code path into this specific struct field was found, and the externally-exposed DUML enum (if it even maps 1:1 to this internal byte, which covers many sub-modes like slomo/timelapse/hyperlapse/quickshot variants) was not recovered. Not asserting a decode without that link. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6D — Video Record Mode Get

_Not decoded._ Same internal-mechanism lead as 0x6c (Set) applies to the paired Get - the same per-session byte-sized record-mode field would presumably be read back. See 0x6c's entry for full detail. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6E — Panorama Mode Set

_Not decoded._ Searched for a handler/registration binding this literal cmd_id under cmd_set 0x02. Checked, in order: (1) dji_camera3 -- pure bootstrap, no command logic (confirmed by full disassembly). (2) librcam.so -- imports no DUML registration primitive at all (ruled out architecturally). (3) libdcam_topmode_comm.so exports real panorama-logic functions by name -- topmode_get_panomode_by_op, topmode_get_pano_op_by_submode, topmode_get_panotype_by_op, topmode_get_dussrlt_by_panorlt, topmode_get_dussphase_by_panophase -- consistent with a real panorama-mode state machine existing in this layer, but this library's only direct cam_event_client_pool_register call site registers an unrelated gimbal/external-module-control client, not these functions; and none of these function addresses appear in any relocated pointer array in the library (checked all 77 relocation targets). (4) dji_cht (camera hardware test tool) has an interactive menu entry "'5': pano-cap" and real pano_phase/pano-mode strings, but drives the camdev engine directly (bypassing DUML) for manual QA, so gives no cmd_id evidence. (5) dji_sys's 11-12 literal duss_event_register_dynamic_command call sites on both architectures: none under cmd_set 0x02 (only 0x00/0x04/0x06/0x22 found). (6) dji_flight's fully-decoded 44-row 0xae038 array: only 3 cmd_set-0x02 rows exist (cmd_id 0x80/0x81/0x87), none matching 0x6e. No numeric (0x02, 0x6e) binding recoverable by any traced mechanism; the plugin-to-cmd_id wiring is most likely config-file-driven and that config file is absent from this firmware extraction (same gap documented for dji_navigation in doc 08). Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6F — Panorama Mode Get

_Not decoded._ Identical investigation and identical result to 0x6e (Panorama Mode Set) -- the same candidate functions in libdcam_topmode_comm.so were checked, the same negative results for dji_camera3/librcam.so/dji_sys/dji_flight apply, and no numeric (0x02, 0x6f) binding was recoverable. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x70 — System State Get

_Not decoded._ Checked dji_camera3 (bootstrap only), librcam.so (no registration import), libdcam_cs_cbb.so's service_get_system_configuration (0x16c38) -- disassembled fully: it is a trivial getter returning an internal platform-capability-config pointer at struct offset 0x68, unrelated to DUML and with no cmd_id association. Checked dji_sys (both architectures, all literal call sites) and dji_flight's 44-row array: no cmd_set-0x02 entry near this value. Noted but NOT asserted as fact: the existing, already-decoded cmd_id 0x80 'Camera State Info' (camera_camera_state_info_dissector, ~38 fields covering connect/usb/sensor/SD-card/firmware-upgrade/hot/recording state) is a plausible semantic match for what a 'System State Get' request would retrieve as its response, given the DUML convention that many 'X Get' commands trigger a same-topic push/response. No binary evidence (handler disassembly, registration call, or request/response pairing metadata) was found to confirm this pairing, so it is flagged as an unconfirmed hypothesis only, not reported as a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x71 — SDcard Info Get

_Not decoded._ Checked libdcam_storage_dev.so (exports storage_dev_get_size_info, storage_dev_get_status, storage_dev_get_remain_shots, storage_dev_get_remain_time, string literal SD_CARD_INFO) and libdcam_cs_cbb.so (cs_storage_manager_get_storage_conf, cs_storage_manager_get_storage_dev, cs_storage_dev_eng_get_dev/_is_available) -- real, plausibly-relevant engine functions by name and by the literal SD_CARD_INFO string, but neither library imports duss_event_register_dynamic_command/cam_event_client_pool_register/any other DUML registration primitive (confirmed via readelf UND-symbol check), so no code path ties any of them to a specific cmd_id. Checked dji_camera3/librcam.so/dji_sys (both archs)/dji_flight's 44-row array: no cmd_set 0x02 registration anywhere near 0x71. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x72 — SDcard Do Format

_Not decoded._ libdcam_storage_dev.so exports a function literally named storage_dev_format -- a strong name match -- but, as with 0x71, this library imports no DUML registration primitive at all, so there is no traceable path from a wire-level cmd_id to this function. Checked the same set of candidate registrars (dji_camera3, librcam.so, dji_sys on both architectures, dji_flight's fully-decoded 44-row array) with the same negative result: no cmd_set-0x02 entry near 0x72 anywhere. The config file that would presumably drive the camera plugin framework's command routing (analogous to dji_navigation's /system/etc/dji.json, itself documented absent in doc 08) is likewise absent from this e2 extraction (confirmed via find, no /system/etc, no .json files anywhere). Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x73 — SDcard Format Progress Get

_Not decoded._ No function name anywhere in the camera library set matches 'format_progress' (checked via strings across every lib64/libdcam_*.so, lib64/librcam.so, and bin/dji_camera3). The closest related real functions are the same storage_dev_format/storage_dev_get_status candidates noted under 0x71/0x72, which could plausibly report an in-progress format's status via a generic status enum, but no function or string specifically names a 'progress' percentage/counter for formatting, and no registration call binds any candidate to this cmd_id. Checked the same registrar set (dji_camera3, librcam.so, dji_sys both archs, dji_flight array) with the same negative result. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x74 — Fw Upgrade Progress Get

_Not decoded._ Searched every camera-related binary (dji_camera3, librcam.so, all lib64/libdcam_*.so) for 'fw_upgrade'/'upgrade_progress' strings: zero hits. The only 'upgrade_progress' strings anywhere in the e2 firmware image belong to bin/dji_lte (LTE-dongle firmware update, an unrelated subsystem already covered under cmd_set 0x18/doc 21's LTE-Dongle-Diagnostic entry) -- confirmed not to be camera-related. Checked dji_sys (both architectures) and dji_flight's 44-row array for any cmd_set-0x02 registration near 0x74: none found. No handler of any kind located for this command. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x75 — Photo Sync Progress Get

_Not decoded._ Searched every camera-related binary for 'photo_sync'/'sync_progress' strings: zero hits anywhere in the e2 firmware image. No plausible candidate function name was found in libdcam_storage.so, libdcam_storage_dev.so, libdcam_cs_cbb.so, or libdcam_topmode_comm.so's exported symbol lists either. Checked dji_sys (both architectures) and dji_flight's fully-decoded 44-row array: no cmd_set-0x02 registration near 0x75. No handler located. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x76 — Camera Power Info Get

_Not decoded._ Searched every camera-related binary for 'power_info'/'camera_power' strings: zero hits. Checked libdcam_cs_cbb.so's cs_hms_manager_init/cs_hms_manager_register_listener/_cam_hms_send (Health Management System forwarding functions, the only call site to cam_event_client_pool_register in this library) on the theory that camera power/health telemetry might route through this HMS path -- but this registers a single client with no visible literal cmd_id tie to 0x76, and 'HMS' in this codebase forwards general health/diagnostic events rather than parsing camera-specific DUML commands. Checked dji_sys (both architectures) and dji_flight's 44-row array: no cmd_set-0x02 registration near 0x76. No handler located. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x77 — Settings Save

_Not decoded._ libdcam_cs_cbb.so exports real, plausibly on-topic functions -- cs_storage_manager_save_user_setting, proxy_manager_user_setting_save, storage_manager_user_setting_save (and matching ...load variants, presumably for the paired cmd_id 0x78 'Settings Load') -- a strong name match for a settings-persistence command. However, as with the storage candidates under 0x71/0x72, libdcam_cs_cbb.so imports no DUML registration primitive (duss_event_register_dynamic_command/cam_event_client_pool_register) that ties any of these functions to a specific cmd_id; its one actual registration call site (cs_cam_duss_hms_init) is the unrelated single-entry HMS client noted above. Checked dji_camera3, librcam.so, dji_sys (both architectures, all literal + loop-based call sites -- the loop sites are independently confirmed, matching the project's own doc 00, to be the unrelated Param-Manager/cross-chip-parameter-bus subsystem, cmd_set 0x00 family, not Camera), and dji_flight's fully-decoded 44-row array (only cmd_id 0x80/0x81/0x87 present under cmd_set 0x02): no binding found for 0x77 anywhere. Not guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x78 — Settings Load

_Not decoded._ Found and fully disassembled a real, single-purpose function pair: cs_storage_manager_load_user_setting(storage_mgr_self, index:w1) (libdcam_cs_cbb.so vaddr 0x1cb40) takes a lock then forwards the single integer `index` unchanged to storage_manager_user_setting_load([self+0x48], index) — i.e. the function's only external input is one integer selecting which storage device's saved settings to load. This is a strong name/semantic match for 'Settings Load' and has an exact structural counterpart for 0x77 'Settings Save' (cs_storage_manager_save_user_setting, same signature, not in this batch). HOWEVER: (1) no literal cmd_id==0x78 comparison or duss_event registration tying this function to DUML traffic was found anywhere in either image (consistent with the missing-plugins.conf architecture described in shared_infrastructure_found); (2) this function's single-int signature could equally be invoked internally on SD-card hot-plug (loading that card's own saved settings) rather than being driven by an explicit wire command at all — both are plausible given the function's placement in the storage-device manager rather than a camera-command-facing plugin. Could not resolve which, or confirm any additional wire fields beyond a single index byte, so this is reported as insufficient_evidence per the task's guidance rather than guessing the full payload. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x79 — File Delete

_Not decoded._ Disassembled cam_file_name_manager_remove_by_index(mgr, idx:w1, subidx:w2) (libdcam_fnm.so vaddr 0x2a50): builds a 3-word {op=2, idx, subidx} struct on the stack and calls a vtable slot at [mgr+0x40]. cam_file_name_manager_remove_all(mgr) (vaddr 0x2730) builds {op=0} and calls the SAME vtable slot — confirming a real, op-coded 'delete' dispatcher exists (op 0=all, 2=by-index; a 3rd op for remove_by_name, exported as a separate symbol, is inferred as op=1 by the same pattern but not individually disassembled). libdcam_fnm_dcf.so's DjiDCF_* functions are the underlying filesystem-level implementations these ops eventually reach. This is a real, multi-mode file-deletion API that plausibly backs cmd_id 0x79, but no literal cmd_id==0x79 registration/dispatch site was found tying a specific DUML wire-byte layout to a specific one of these three ops (same missing-plugins.conf gap as 0x78). Could not determine whether the wire payload carries a mode byte + index, a filename string, or an 'all' flag, so no layout is asserted. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x7A — Video Play Control

_Not decoded._ App/RC asks the aircraft's playback (picture-review) engine to resume video playback starting at the 5000 ms mark of the currently-open clip. Handler correctly identified (pbdev_ctrl (libdcam_pbdev.so, vaddr 0x4308) forwards byte@0/u32@1 of its 2nd-arg struct as a looper message (msg=0x36b3) to the playback engine; pb_eng_play_control (libdcam_pb.so, vaddr 0x6220) is the real state machine, dispatching on that byte via a 5-entry jump table at vaddr 0xef94), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x7B — Thumbnail 2 Single Ctrl

_Not decoded._ Checked: (1) string search for 'thumbnail' across every .so/executable in both e1e and e2 images — zero hits anywhere (not even as a non-DUML log string); (2) libdcam_fnm.so's DCF 'subfile' API family (cam_file_name_manager_get_subfile_by_no / get_subfile_no_by_name / gen_subfile / subfile_remove_*), since DCF 'subfile' conventionally means an embedded thumbnail/screennail — a plausible architectural home, but cam_file_name_manager_gen_subfile (vaddr 0x1d28) is a bare vtable-call wrapper with no extra arguments visible at this level (the real per-device implementation isn't in this library), so no field layout could be extracted; (3) libdcam_pb.so/libdcam_pbdev.so (playback engine, since '2' in the name may mean a secondary/large thumbnail shown during playback) — no thumbnail-named export found there either. No handler with an inspectable argument structure was located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x7C — Camera Shutter Cmd

Payload decoder: `camera_camera_shutter_cmd_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_shutter_cmd_shutter_type` (Shutter Type) | uint8 |  |

## 0x7D — PB Zoom Ctrl

_Not decoded._ Checked libdcam_pbdev.so and libdcam_pb.so's full exported symbol lists (no zoom-named export; pbdev_ctrl/pb_eng_play_control cover only the 1-5 play/pause/seek control codes documented under 0x7a, with no additional zoom-scale field observed in those functions), libdcam_cs_pb_state.so's full import list (fs_tree_param_*/pbdev_* only, nothing zoom-related), and libdcam_cs_camera_state.so's cs_camera_state_set_tap_zoom_target (vaddr 0x2368, disassembled: takes a pointer-to-{float x, float y} target pair) as the one zoom-adjacent function anywhere in the camera plugin tree — but this is in the live-shooting 'camera_state' plugin (tap-to-zoom/tap-to-focus during live view), not the 'pb_state' (playback) plugin, and no call chain from a playback context into it was found. No PB-specific zoom handler was located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x7E — PB Pic Drag Ctrl

_Not decoded._ Same search as 0x7d (libdcam_pbdev.so, libdcam_pb.so, libdcam_cs_pb_state.so, libdcam_cs_camera_state.so): no 'drag'/'pan'-named export or call found anywhere in the camera plugin tree on either image. No handler located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x80 — Camera State Info

Payload decoder: `camera_camera_state_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `camera_camera_state_info_masked00` (Masked00) | uint32 |  |
  | 0 | 4 | `camera_camera_state_info_connect_state` (Connect State) | uint32 | mask:`0x0001` |
  | 0 | 4 | `camera_camera_state_info_usb_state` (Usb State) | uint32 | mask:`0x0002` |
  | 0 | 4 | `camera_camera_state_info_time_sync_state` (Time Sync State) | uint32 | mask:`0x0004` |
  | 0 | 4 | `camera_camera_state_info_photo_state` (Photo State) | uint32 | enum:`enums.CAMERA_STATE_INFO_PHOTO_STATE_ENUM`; mask:`0x0038` |
  | 0 | 4 | `camera_camera_state_info_record_state` (Record State) | uint32 | mask:`0x00c0`; TODO values from enum P3.DataCameraGetPushStateInfo |
  | 0 | 4 | `camera_camera_state_info_sensor_state` (Sensor State) | uint32 | mask:`0x0100` |
  | 0 | 4 | `camera_camera_state_info_sd_card_insert_state` (Sd Card Insert State) | uint32 | mask:`0x0200` |
  | 0 | 4 | `camera_camera_state_info_sd_card_state` (Sd Card State) | uint32 | enum:`enums.CAMERA_STATE_INFO_SD_CARD_STATE_ENUM`; mask:`0x3c00` |
  | 0 | 4 | `camera_camera_state_info_firm_upgrade_state` (Firm Upgrade State) | uint32 | mask:`0x4000` |
  | 0 | 4 | `camera_camera_state_info_firm_upgrade_error_state` (Firm Upgrade Error State) | uint32 | enum:`enums.CAMERA_STATE_INFO_FIRM_UPGRADE_ERROR_STATE_FIRM_ERROR_TYPE_ENUM`; mask:`0x18000` |
  | 0 | 4 | `camera_camera_state_info_hot_state` (Hot State) | uint32 | mask:`0x020000` |
  | 0 | 4 | `camera_camera_state_info_not_enabled_photo` (Not Enabled Photo) | uint32 | mask:`0x040000` |
  | 0 | 4 | `camera_camera_state_info_is_storing` (Is Storing) | uint32 | mask:`0x080000` |
  | 0 | 4 | `camera_camera_state_info_is_time_photoing` (Is Time Photoing) | uint32 | mask:`0x100000` |
  | 0 | 4 | `camera_camera_state_info_encrypt_status` (Encrypt Status) | uint32 | mask:`0xc00000`; TODO values from enum P3.DataCameraGetPushStateInfo |
  | 0 | 4 | `camera_camera_state_info_is_gimbal_busy` (Is Gimbal Busy) | uint32 | mask:`0x08000000` |
  | 0 | 4 | `camera_camera_state_info_in_tracking_mode` (In Tracking Mode) | uint32 | mask:`0x10000000` |
  | 4 | 1 | `camera_camera_state_info_mode` (Camera Mode) | uint8 | enum:`enums.CAMERA_STATE_INFO_MODE_ENUM` |
  | 5 | 4 | `camera_camera_state_info_sd_card_total_size` (Sd Card Total Size) | uint32 |  |
  | 9 | 4 | `camera_camera_state_info_sd_card_free_size` (Sd Card Free Size) | uint32 |  |
  | 13 | 4 | `camera_camera_state_info_remained_shots` (Remained Shots) | uint32 |  |
  | 17 | 4 | `camera_camera_state_info_remained_time` (Remained Time) | uint32 |  |
  | 21 | 1 | `camera_camera_state_info_file_index_mode` (File Index Mode) | uint8 | enum:`enums.CAMERA_STATE_INFO_FILE_INDEX_MODE_ENUM` |
  | 22 | 1 | `camera_camera_state_info_fast_play_back_info` (Fast Play Back Info) | uint8 |  |
  | 22 | 1 | `camera_camera_state_info_fast_play_back_enabled` (Fast Play Back Enabled) | uint8 | mask:`0x80` |
  | 22 | 1 | `camera_camera_state_info_fast_play_back_time` (Fast Play Back Time) | uint8 | mask:`0x7f` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_info` (Photo Osd Info) | uint16 |  |
  | 23 | 2 | `camera_camera_state_info_photo_osd_aperture_is_show` (Photo Osd Aperture Is Show) | uint16 | mask:`0x02` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_shutter_is_show` (Photo Osd Shutter Is Show) | uint16 | mask:`0x04` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_iso_is_show` (Photo Osd Iso Is Show) | uint16 | mask:`0x08` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_exposure_is_show` (Photo Osd Exposure Is Show) | uint16 | mask:`0x10` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_sharpe_is_show` (Photo Osd Sharpe Is Show) | uint16 | mask:`0x20` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_contrast_is_show` (Photo Osd Contrast Is Show) | uint16 | mask:`0x40` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_saturation_is_show` (Photo Osd Saturation Is Show) | uint16 | mask:`0x80` |
  | 23 | 2 | `camera_camera_state_info_photo_osd_time_is_show` (Photo Osd Time Is Show) | uint16 | mask:`0x01` |
  | 25 | 2 | `camera_camera_state_info_unknown19` (Unknown19) | bytes |  |
  | 27 | 1 | `camera_camera_state_info_in_debug_mode` (In Debug Mode) | uint8 |  |
  | 28 | 1 | `camera_camera_state_info_unknown1c` (Unknown1C) | uint8 |  |
  | 29 | 2 | `camera_camera_state_info_video_record_time` (Video Record Time) | uint16 |  |
  | 31 | 1 | `camera_camera_state_info_max_photo_num` (Max Photo Num) | uint8 |  |
  | 32 | 1 | `camera_camera_state_info_masked20` (Masked20) | uint8 |  |
  | 32 | 1 | `camera_camera_state_info_histogram_enable` (Histogram Enable) | uint8 | mask:`0x01` |
  | 33 | 1 | `camera_camera_state_info_camera_type` (Camera Type) | uint8 | enum:`enums.CAMERA_STATE_INFO_CAMERA_TYPE_ENUM` |
  | 34 | 2 | `camera_camera_state_info_unknown22` (Unknown22) | bytes |  |
  | 36 | 1 | `camera_camera_state_info_version` (Version) | uint8 |  |

  *if (payload:len() >= offset + 2) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 37 | 2 | `camera_camera_state_info_padding` (Padding) | bytes |  |

## 0x81 — Camera Shot Params

Payload decoder: `camera_camera_shot_params_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `camera_camera_shot_params_aperture_size` (Aperture Size) | uint16 |  |
  | 2 | 2 | `camera_camera_shot_params_user_shutter` (User Shutter) | uint16 |  |
  | 2 | 2 | `camera_camera_shot_params_reciprocal` (Reciprocal) | uint16 | mask:`0x8000` |
  | 4 | 1 | `camera_camera_shot_params_shutter_speed_decimal` (Shutter Speed Decimal) | uint8 |  |
  | 5 | 1 | `camera_camera_shot_params_iso` (Iso) | uint8 | enum:`enums.CAMERA_SHOT_PARAMS_ISO_TYPE_ENUM` |
  | 6 | 1 | `camera_camera_shot_params_exposure_compensation` (Exposure Compensation) | uint8 |  |
  | 7 | 1 | `camera_camera_shot_params_ctr_object_for_one` (Ctr Object For One) | uint8 |  |
  | 8 | 1 | `camera_camera_shot_params_ctr_object_for_two` (Ctr Object For Two) | uint8 |  |
  | 9 | 1 | `camera_camera_shot_params_image_size` (Image Size) | uint8 | enum:`enums.CAMERA_SHOT_PARAMS_IMAGE_SIZE_SIZE_TYPE_ENUM` |
  | 10 | 1 | `camera_camera_shot_params_image_ratio` (Image Ratio) | uint8 | enum:`enums.CAMERA_SHOT_PARAMS_IMAGE_RATIO_TYPE_ENUM` |
  | 11 | 1 | `camera_camera_shot_params_image_quality` (Image Quality) | uint8 |  |
  | 12 | 1 | `camera_camera_shot_params_image_format` (Image Format) | uint8 |  |
  | 13 | 1 | `camera_camera_shot_params_video_format` (Video Format) | uint8 |  |
  | 14 | 1 | `camera_camera_shot_params_video_fps` (Video Fps) | uint8 |  |
  | 15 | 1 | `camera_camera_shot_params_video_fov` (Video Fov) | uint8 |  |
  | 16 | 1 | `camera_camera_shot_params_video_second_open` (Video Second Open) | uint8 |  |
  | 17 | 1 | `camera_camera_shot_params_video_second_ratio` (Video Second Ratio) | uint8 |  |
  | 18 | 1 | `camera_camera_shot_params_video_quality` (Video Quality) | uint8 |  |
  | 19 | 1 | `camera_camera_shot_params_video_store_format` (Video Store Format) | uint8 |  |
  | 20 | 1 | `camera_camera_shot_params_exposure_mode` (Exposure Mode) | uint8 | enum:`enums.CAMERA_SHOT_PARAMS_EXPOSURE_MODE_ENUM` |
  | 21 | 1 | `camera_camera_shot_params_scene_mode` (Scene Mode) | uint8 |  |
  | 22 | 1 | `camera_camera_shot_params_metering` (Metering) | uint8 |  |
  | 23 | 1 | `camera_camera_shot_params_white_balance` (White Balance) | uint8 |  |
  | 24 | 1 | `camera_camera_shot_params_color_temp` (Color Temp) | uint8 |  |
  | 25 | 1 | `camera_camera_shot_params_mctf_enable` (Mctf Enable) | uint8 |  |
  | 26 | 1 | `camera_camera_shot_params_mctf_strength` (Mctf Strength) | uint8 |  |
  | 27 | 1 | `camera_camera_shot_params_sharpe` (Sharpe) | uint8 |  |
  | 28 | 1 | `camera_camera_shot_params_contrast` (Contrast) | uint8 |  |
  | 29 | 1 | `camera_camera_shot_params_saturation` (Saturation) | uint8 |  |
  | 30 | 1 | `camera_camera_shot_params_tonal` (Tonal) | uint8 |  |
  | 31 | 1 | `camera_camera_shot_params_digital_filter` (Digital Filter) | uint8 |  |
  | 32 | 1 | `camera_camera_shot_params_anti_flicker` (Anti Flicker) | uint8 |  |
  | 33 | 1 | `camera_camera_shot_params_continuous` (Continuous) | uint8 |  |
  | 34 | 1 | `camera_camera_shot_params_time_params_type` (Time Params Type) | uint8 |  |
  | 35 | 1 | `camera_camera_shot_params_time_params_num` (Time Params Num) | uint8 |  |
  | 36 | 2 | `camera_camera_shot_params_time_params_period` (Time Params Period) | uint16 |  |
  | 38 | 2 | `camera_camera_shot_params_real_aperture_size` (Real Aperture Size) | uint16 |  |
  | 40 | 2 | `camera_camera_shot_params_real_shutter` (Real Shutter) | uint16 |  |
  | 40 | 2 | `camera_camera_shot_params_rel_reciprocal` (Rel Reciprocal) | uint16 | mask:`0x8000` |
  | 42 | 1 | `camera_camera_shot_params_rel_shutter_speed_decimal` (Real Shutter Speed Decimal) | uint8 |  |
  | 43 | 4 | `camera_camera_shot_params_rel_iso` (Real Iso) | uint32 |  |
  | 47 | 1 | `camera_camera_shot_params_rel_exposure_compensation` (Real Exposure Compensation) | uint8 |  |
  | 48 | 1 | `camera_camera_shot_params_time_countdown` (Time Countdown) | uint8 |  |
  | 49 | 2 | `camera_camera_shot_params_cap_min_shutter` (Cap Min Shutter) | uint16 |  |
  | 49 | 2 | `camera_camera_shot_params_cap_min_shutter_reciprocal` (Cap Min Shutter Reciprocal) | uint16 | mask:`0x8000` |
  | 51 | 1 | `camera_camera_shot_params_cap_min_shutter_decimal` (Cap Min Shutter Decimal) | uint8 |  |
  | 52 | 2 | `camera_camera_shot_params_cap_max_shutter` (Cap Max Shutter) | uint16 |  |
  | 52 | 2 | `camera_camera_shot_params_cap_max_shutter_reciprocal` (Cap Max Shutter Reciprocal) | uint16 | mask:`0x8000` |
  | 54 | 1 | `camera_camera_shot_params_cap_max_shutter_decimal` (Cap Max Shutter Decimal) | uint8 |  |
  | 55 | 1 | `camera_camera_shot_params_video_standard` (Video Standard) | uint8 |  |
  | 56 | 1 | `camera_camera_shot_params_ae_lock` (Ae Lock) | uint8 |  |
  | 57 | 1 | `camera_camera_shot_params_photo_type` (Photo Type) | uint8 | enum:`enums.CAMERA_SHOT_PARAMS_PHOTO_TYPE_ENUM` |
  | 58 | 1 | `camera_camera_shot_params_spot_area_bottom_right_pos` (Spot Area Bottom Right Pos) | uint8 |  |
  | 59 | 1 | `camera_camera_shot_params_unknown3b` (Unknown3B) | uint8 |  |
  | 60 | 1 | `camera_camera_shot_params_aeb_number` (Aeb Number) | uint8 |  |
  | 61 | 1 | `camera_camera_shot_params_pano_mode` (Pano Mode) | uint8 | TODO values from enum P3.DataCameraGetPushShotParams |
  | 62 | 2 | `camera_camera_shot_params_cap_min_aperture` (Cap Min Aperture) | uint16 |  |
  | 64 | 2 | `camera_camera_shot_params_cap_max_aperture` (Cap Max Aperture) | uint16 |  |
  | 66 | 1 | `camera_camera_shot_params_masked42` (Masked42) | uint8 |  |
  | 66 | 1 | `camera_camera_shot_params_auto_turn_off_fore_led` (Auto Turn Off Fore Led) | uint8 | mask:`0x01` |
  | 67 | 1 | `camera_camera_shot_params_exposure_status` (Exposure Status) | uint8 |  |
  | 68 | 1 | `camera_camera_shot_params_locked_gimbal_when_shot` (Locked Gimbal When Shot) | uint8 |  |
  | 69 | 1 | `camera_camera_shot_params_encode_types` (Video Encode Types) | uint8 |  |
  | 69 | 1 | `camera_camera_shot_params_primary_video_encode_type` (Primary Video Encode Type) | uint8 | enum:`enums.CAMERA_SHOT_PARAMS_VIDEO_ENCODE_TYPE_ENUM`; mask:`0x0f` |
  | 69 | 1 | `camera_camera_shot_params_secondary_video_encode_type` (Secondary Video Encode Type) | uint8 | enum:`enums.CAMERA_SHOT_PARAMS_VIDEO_ENCODE_TYPE_ENUM`; mask:`0xf0` |
  | 70 | 1 | `camera_camera_shot_params_not_auto_ae_unlock` (Not Auto Ae Unlock) | uint8 |  |
  | 71 | 1 | `camera_camera_shot_params_unknown47` (Unknown47) | uint8 |  |
  | 72 | 1 | `camera_camera_shot_params_constrast_ehance` (Constrast Ehance) | uint8 |  |
  | 73 | 1 | `camera_camera_shot_params_video_record_mode` (Video Record Mode) | uint8 |  |
  | 74 | 1 | `camera_camera_shot_params_timelapse_save_type` (Timelapse Save Type) | uint8 |  |
  | 75 | 2 | `camera_camera_shot_params_video_record_interval_time` (Video Record Interval Time) | uint16 |  |
  | 77 | 4 | `camera_camera_shot_params_timelapse_duration` (Timelapse Duration) | uint32 |  |
  | 81 | 2 | `camera_camera_shot_params_timelapse_time_count_down` (Timelapse Time Count Down) | uint16 |  |
  | 83 | 4 | `camera_camera_shot_params_timelapse_recorded_frame` (Timelapse Recorded Frame) | uint32 |  |
  | 87 | 2 | `camera_camera_shot_params_optics_scale` (Optics Scale) | uint16 |  |
  | 89 | 2 | `camera_camera_shot_params_digital_zoom_scale` (Digital Zoom Scale) | uint16 |  |

## 0x82 — Camera PlayBack Params

Payload decoder: `camera_camera_play_back_params_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_play_back_params_mode` (Mode) | uint8 | enum:`enums.CAMERA_PLAY_BACK_PARAMS_MODE_ENUM` |
  | 1 | 2 | `camera_camera_play_back_params_file_type` (File Type) | uint16 | enum:`enums.CAMERA_PLAY_BACK_PARAMS_FILE_TYPE_ENUM` |
  | 3 | 1 | `camera_camera_play_back_params_file_num` (File Num) | uint8 |  |
  | 4 | 2 | `camera_camera_play_back_params_total_num` (Total Num) | uint16 |  |
  | 6 | 2 | `camera_camera_play_back_params_index` (Index) | uint16 |  |
  | 8 | 1 | `camera_camera_play_back_params_progress` (Progress) | uint8 |  |
  | 9 | 2 | `camera_camera_play_back_params_total_time` (Total Time) | uint16 |  |
  | 11 | 2 | `camera_camera_play_back_params_current` (Current) | uint16 |  |
  | 13 | 2 | `camera_camera_play_back_params_delete_chioce_num` (Delete Chioce Num) | uint16 |  |
  | 15 | 2 | `camera_camera_play_back_params_zoom_size` (Zoom Size) | uint16 |  |
  | 17 | 2 | `camera_camera_play_back_params_total_photo_num` (Total Photo Num) | uint16 |  |
  | 19 | 2 | `camera_camera_play_back_params_total_video_num` (Total Video Num) | uint16 |  |
  | 21 | 4 | `camera_camera_play_back_params_photo_width` (Photo Width) | uint32 |  |
  | 25 | 4 | `camera_camera_play_back_params_photo_height` (Photo Height) | uint32 |  |
  | 29 | 4 | `camera_camera_play_back_params_center_x` (Center X) | uint32 |  |
  | 33 | 4 | `camera_camera_play_back_params_center_y` (Center Y) | uint32 |  |
  | 37 | 1 | `camera_camera_play_back_params_cur_page_selected` (Cur Page Selected) | uint8 |  |
  | 38 | 1 | `camera_camera_play_back_params_del_file_status` (Del File Status) | uint8 | enum:`enums.CAMERA_PLAY_BACK_PARAMS_DEL_FILE_STATUS_ENUM` |
  | 39 | 1 | `camera_camera_play_back_params_not_select_file_valid` (Not Select File Valid) | uint8 |  |
  | 40 | 1 | `camera_camera_play_back_params_single_downloaded` (Single Downloaded) | uint8 |  |

## 0x83 — Camera Chart Info

Payload decoder: `camera_camera_chart_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `camera_camera_chart_info_light_values` (Light Values) | bytes | // size not known |

## 0x84 — Camera Recording Name

Payload decoder: `camera_camera_recording_name_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_recording_name_file_type` (File Type) | uint8 | enum:`enums.CAMERA_RECORDING_FILE_TYPE_ENUM` |
  | 1 | 4 | `camera_camera_recording_name_index` (Index) | uint32 |  |
  | 5 | 8 | `camera_camera_recording_name_size` (Size) | uint64 |  |
  | 13 | 4 | `camera_camera_recording_name_time` (Time) | uint32 |  |

## 0x85 — Camera Raw Params

Payload decoder: `camera_camera_raw_params_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_raw_params_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `camera_camera_raw_params_disk_status` (Disk Status) | uint8 | enum:`enums.CAMERA_RAW_PARAMS_DISK_STATUS_ENUM`; mask:`0x0f` |
  | 0 | 1 | `camera_camera_raw_params_disk_connected` (Disk Connected) | uint8 | mask:`0x10` |
  | 0 | 1 | `camera_camera_raw_params_disk_capacity` (Disk Capacity) | uint8 | mask:`0x60` |
  | 1 | 2 | `camera_camera_raw_params_disk_available_time` (Disk Available Time) | uint16 |  |
  | 3 | 4 | `camera_camera_raw_params_available_capacity` (Available Capacity) | uint32 |  |
  | 7 | 1 | `camera_camera_raw_params_resolution` (Resolution) | uint8 |  |
  | 8 | 1 | `camera_camera_raw_params_fps` (Fps) | uint8 |  |
  | 9 | 1 | `camera_camera_raw_params_ahci_status` (Ahci Status) | uint8 |  |

## 0x86 — Camera Cur Pano Status

Payload decoder: `camera_camera_cur_pano_file_name_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `camera_camera_cur_pano_file_name_index` (Index) | uint32 |  |
  | 4 | 8 | `camera_camera_cur_pano_file_name_unknown04` (Unknown04) | bytes |  |
  | 12 | 4 | `camera_camera_cur_pano_file_name_pano_create_time` (Pano Create Time) | uint32 |  |
  | 16 | 1 | `camera_camera_cur_pano_file_name_cur_saved_number` (Cur Saved Number) | uint8 |  |
  | 17 | 1 | `camera_camera_cur_pano_file_name_cur_taken_number` (Cur Taken Number) | uint8 |  |
  | 18 | 1 | `camera_camera_cur_pano_file_name_total_number` (Total Number) | uint8 |  |
  | 19 | 1 | `camera_camera_cur_pano_file_name_unknown13` (Unknown13) | uint8 |  |
  | 20 | 8 | `camera_camera_cur_pano_file_name_file_size` (File Size) | uint64 |  |
  | 28 | 4 | `camera_camera_cur_pano_file_name_create_time` (Create Time) | uint32 |  |

## 0x87 — Camera Shot Info

Payload decoder: `camera_camera_shot_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_shot_info_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `camera_camera_shot_info_fuselage_focus_mode` (Fuselage Focus Mode) | uint8 | enum:`enums.CAMERA_SHOT_INFO_FUSELAGE_FOCUS_MODE_ENUM`; mask:`0x03` |
  | 0 | 1 | `camera_camera_shot_info_shot_focus_mode` (Shot Focus Mode) | uint8 | mask:`0x0c`; TODO values from enum P3.DataCameraGetPushShotInfo |
  | 0 | 1 | `camera_camera_shot_info_zoom_focus_type` (Zoom Focus Type) | uint8 | mask:`0x10` |
  | 0 | 1 | `camera_camera_shot_info_shot_type` (Shot Type) | uint8 | mask:`0x20`; TODO values from enum P3.DataCameraGetPushShotInfo |
  | 0 | 1 | `camera_camera_shot_info_shot_fd_type` (Shot Fd Type) | uint8 | mask:`0x40`; TODO values from enum P3.DataCameraGetPushShotInfo |
  | 0 | 1 | `camera_camera_shot_info_shot_connected` (Shot Connected) | uint8 | mask:`0x80` |
  | 1 | 2 | `camera_camera_shot_info_shot_focus_max_stroke` (Shot Focus Max Stroke) | uint16 |  |
  | 3 | 2 | `camera_camera_shot_info_shot_focus_cur_stroke` (Shot Focus Cur Stroke) | uint16 |  |
  | 5 | 4 | `camera_camera_shot_info_obj_distance` (Obj Distance) | float |  |
  | 9 | 2 | `camera_camera_shot_info_min_aperture` (Min Aperture) | uint16 |  |
  | 11 | 2 | `camera_camera_shot_info_max_aperture` (Max Aperture) | uint16 |  |
  | 13 | 4 | `camera_camera_shot_info_spot_af_axis_x` (Spot Af Axis X) | float |  |
  | 17 | 4 | `camera_camera_shot_info_spot_af_axis_y` (Spot Af Axis Y) | float |  |
  | 21 | 1 | `camera_camera_shot_info_masked15` (Masked15) | uint8 |  |
  | 21 | 1 | `camera_camera_shot_info_focus_status` (Focus Status) | uint8 | mask:`0x03` |
  | 22 | 1 | `camera_camera_shot_info_mf_focus_probability` (Mf Focus Probability) | uint8 |  |
  | 23 | 2 | `camera_camera_shot_info_min_focus_distance` (Min Focus Distance) | uint16 |  |
  | 25 | 2 | `camera_camera_shot_info_max_focus_distance` (Max Focus Distance) | uint16 |  |
  | 27 | 2 | `camera_camera_shot_info_cur_focus_distance` (Cur Focus Distance) | uint16 |  |
  | 29 | 2 | `camera_camera_shot_info_min_focus_distance_step` (Min Focus Distance Step) | uint16 |  |
  | 31 | 1 | `camera_camera_shot_info_masked1f` (Masked1F) | uint8 |  |
  | 31 | 1 | `camera_camera_shot_info_digital_focus_m_enable` (Digital Focus M Enable) | uint8 | mask:`0x01` |
  | 31 | 1 | `camera_camera_shot_info_digital_focus_a_enable` (Digital Focus A Enable) | uint8 | mask:`0x02` |
  | 32 | 1 | `camera_camera_shot_info_x_axis_focus_window_num` (X Axis Focus Window Num) | uint8 |  |
  | 33 | 1 | `camera_camera_shot_info_y_axis_focus_window_num` (Y Axis Focus Window Num) | uint8 |  |
  | 34 | 1 | `camera_camera_shot_info_mf_focus_status` (Mf Focus Status) | uint8 |  |
  | 35 | 1 | `camera_camera_shot_info_focus_window_start_x` (Focus Window Start X) | uint8 |  |
  | 36 | 1 | `camera_camera_shot_info_focus_window_real_num_x` (Focus Window Real Num X) | uint8 |  |
  | 37 | 1 | `camera_camera_shot_info_focus_window_start_y` (Focus Window Start Y) | uint8 |  |
  | 38 | 1 | `camera_camera_shot_info_focus_window_real_num_y` (Focus Window Real Num Y) | uint8 |  |
  | 39 | 1 | `camera_camera_shot_info_support_type` (Support Type) | uint8 |  |

## 0x88 — Camera Timelapse Parms

Payload decoder: `camera_camera_timelapse_parms_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_timelapse_parms_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `camera_camera_timelapse_parms_control_mode` (Control Mode) | uint8 | mask:`0x03` |
  | 0 | 1 | `camera_camera_timelapse_parms_gimbal_point_count` (Gimbal Point Count) | uint8 | mask:`0xfc` |
  | 1 | 2 | `camera_camera_timelapse_parms_interval` (Point Interval) | uint16 |  |
  | 3 | 4 | `camera_camera_timelapse_parms_duration` (Point Duration) | uint32 |  |
  | 7 | 2 | `camera_camera_timelapse_parms_yaw` (Point Yaw) | uint16 |  |
  | 9 | 2 | `camera_camera_timelapse_parms_roll` (Point Roll) | uint16 |  |
  | 11 | 2 | `camera_camera_timelapse_parms_pitch` (Point Pitch) | uint16 |  |

## 0x89 — Camera Tracking Status

Payload decoder: `camera_camera_tracking_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_tracking_status_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `camera_camera_tracking_status_status` () |  |  |
  | 1 | 2 | `camera_camera_tracking_status_x_coord` (X Coord) | uint16 |  |
  | 3 | 2 | `camera_camera_tracking_status_y_coord` (Y Coord) | uint16 |  |

## 0x8A — (name unknown)

Payload decoder: `camera_camera_fov_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `camera_camera_fov_param_image_width` (Image Width) | uint32 |  |
  | 4 | 4 | `camera_camera_fov_param_image_height` (Image Height) | uint32 |  |
  | 8 | 4 | `camera_camera_fov_param_image_ratio` (Image Ratio) | uint32 |  |
  | 12 | 4 | `camera_camera_fov_param_lens_focal_length` (Lens Focal Length) | uint32 |  |

## 0x8A — Camera FOV Param

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x8B — Racing Liveview Format Set

_Not decoded._ Exhaustive case-insensitive string search for 'racing' across every file in both e1e and e2 images found zero genuine hits (all apparent matches were substring false-positives on 'tracing', e.g. ftrace/atrace/kprobe strings in unrelated system binaries). Also searched for 'liveview_format'/'fpv'/'low_latency' — no hits. Found a DIFFERENT, confirmed cmd_set-0x08 liveview-codec-switch command (cmd_id 0x41, H.265<->H.264 toggle) exercised by e1e's h26x_liveview_switch_test.sh test script, and a cmd_set-0x02/cmd_id-0x4c resolution-switch command exercised by h264_resolution_switch_test.sh — both real, concretely evidenced, but neither is cmd_id 0x8b/0x8c and neither mentions 'racing'. No evidence ties any binary logic to a 'racing' liveview mode specifically. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x8C — Racing Liveview Format Get

_Not decoded._ Same exhaustive search as 0x8b (its Set counterpart) — no 'racing'/liveview-format-specific evidence found. See 0x8b's handler_evidence for the related-but-distinct cmd_set 0x08/0x41 and cmd_set 0x02/0x4c liveview commands that were found instead. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x90 — Sensor Calibrate Test

_Not decoded._ Checked libdcam_fcali.so (the factory-calibration library linked by librcam.so per the task's own DT_NEEDED hint): its exports are fcali_free_sensor_cali / fcali_load_sensor_calib_data / fcali_shading_sensor_lsc_convert — real calibration-data-file functions, but none named/shaped like a 'test' or 'complete' phase handshake. Checked bin/dji_fcali_test (the standalone factory calibration CLI test tool, invoked by test_dji_fcali_test.sh): it imports no duss_event_*/cam_event_client_pool* symbols at all — it is a self-contained offline test harness, not a DUML command source. Re-dumped and fully decoded dji_flight's relocated {fn_ptr,cmd_word} dispatch array (e1e, vaddr 0xae038, all 44 rows) per the task's hint: its only cmd_set-0x02 rows are cmd_id 0x80 ('Camera State Info'), 0x81 ('Camera Shot Params'), 0x87 ('Camera Shot Info') — 0x90/0x91 are not present, confirming dji_flight only forwards a few specific camera-adjacent commands and not these. No handler for 0x90 was located in either image. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x91 — Sensor Calibrate Complete

_Not decoded._ Same search as 0x90 (its paired command): libdcam_fcali.so's exports, dji_fcali_test's import list, and dji_flight's fully-decoded 44-row dispatch table (cmd_set 0x02 rows only 0x80/0x81/0x87) were all checked with no match. No handler for 0x91 was located in either image. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x92 — Video Clip Info Get

_Not decoded._ Likely a Get query for metadata (duration/size/timestamp/thumbnail-offset etc.) about one recorded video clip on the SD card, analogous to cmd 0x87 'Camera Shot Info' but for playback/clip browsing rather than live-shot status. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x93 — TransCode Control

_Not decoded._ Almost certainly a start/stop (and possibly pause) control for the aircraft-side background video transcode engine that converts raw clips to a delivery format before/while they are offloaded to the app; no byte-level field layout could be confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x94 — Focus Range Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: dji_af_get_output (libaaa.so, thin wrapper @0x2b738) called from librcam.so's debug_tool_app.c 'af get_ret' handler (disassembled at file vaddr ~0x9da30-0x9db80)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `reserved_or_status` (Reserved / Status (unprinted by debug dump)) | int32 | Not printed by the 'af get_ret' debug path; likely a sequence number or internal status/valid flag. Not confirmed. |
  | 4 | 4 | `cur_focusing_state` (CurFocusingState) | int32 | AF focusing-state code (e.g. idle/focusing/in-focus/failed); exact enum values not recovered. |
  | 8 | 4 | `focus_range` (FocusRange) | int32 | Current usable/total AF range in lens motor-step units. |
  | 12 | 4 | `cur_focus_pos` (CurFocusPos) | int32 | Current focus-motor position, same step units as FocusRange. |
  | 16 | 4 | `inf_pos` (InfPos) | int32 | Lens motor position corresponding to infinity focus. |
  | 20 | 4 | `mod_pos` (ModPos) | int32 | Lens motor position corresponding to macro/closest-focus (named 'ModPos' in firmware, likely 'minimum object distance' position). |
  | 24 | 8 | `unknown_gap` (Unknown / unprinted) | bytes | Two 32-bit words present in the struct between ModPos and Distance_mm that this specific debug path does not print; content not determined. |
  | 32 | 4 | `distance_mm` (Distance_mm) | int32 | Estimated absolute subject distance, in millimetres. |

**Worked example:**

- Request payload: `550d0433020134122002944216`
  App (sender_type=APP/2) asks the Camera (receiver_type=CAMERA/1) for the current AF result, empty payload, ack requested. Built and CRC-checked with this project's own duml_py Frame.encode().
- Response payload: `5531045301023412800294000000000100000078000000c2010000d40300000a0000000000000000000000dc0500000b0f`
  Camera ACKs with an illustrative 36-byte struct (offsets 0-35 as decoded above; the true total length beyond offset 32 is not fully confirmed -- see field notes): reserved=0, CurFocusingState=1 (focusing), FocusRange=120, CurFocusPos=450, InfPos=980, ModPos=10, two unknown words=0, Distance_mm=1500mm. This exact byte count/trailing padding is illustrative, not independently confirmed as the real wire-level total payload size.

## 0x95 — Focus Stroke Set

_Not decoded._ Likely commands the lens to move to (or sets a target/limit for) an absolute focus-motor 'stroke' position -- the same physical quantity already confirmed, by this project, as a real wire field in the cmd 0x87 'Camera Shot Info' push (fields 'Shot Focus Max Stroke' and 'Shot Focus Cur Stroke', both uint16, at offsets 1 and 3 of that payload). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x96 — Focus Stroke Get

_Not decoded._ Get counterpart of 0x95; most plausibly returns the lens's current focus-motor stroke position, the same uint16 'Shot Focus Cur Stroke' quantity already confirmed in the cmd 0x87 push payload. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x98 — FileSystem Info Get

_Not decoded._ Almost certainly returns summary filesystem/storage information (likely total/free capacity, filesystem type or mount state, possibly card health) for the active SD card, as a lower-level or higher-detail counterpart to the already-decoded cmd 0x71 'SDcard Info Get'. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x99 — Shot Info Get

_Not decoded._ Most plausibly a pull/query equivalent of the already-fully-decoded cmd 0x87 'Camera Shot Info' push notification (40-byte struct covering focus mode/state, focus stroke min/max/current, aperture range, AF spot coordinates, focus distance range, and focus-window layout) -- i.e. the app asking on-demand for the same (or a superset of the same) live shot-status data that the camera otherwise pushes unsolicited via 0x87. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9A — Focus Aid Set

_Not decoded._ Most likely toggles a manual-focus visual aid (e.g. focus peaking / edge highlighting on the live feed), by analogy with other camera UIs, but no firmware-side evidence of this feature's name or implementation was located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9B — Video Adaptive Gamma Set

_Not decoded._ Likely a simple enable/mode toggle for an adaptive (scene-dependent) gamma/tone curve applied to the video stream, as opposed to the fixed ISP gamma LUTs found elsewhere in the same binary. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9C — Video Adaptive Gamma Get

_Not decoded._ Get counterpart of 0x9B; same uncertainty applies. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9D — Awb Meter Region Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _DjiAAA_CmdMgr_AWB_SpotAwbRegion (vaddr 0x90a58) / Query_SpotAwbRegionFunc (vaddr 0x7ae48); internal id confirmed by .rodata string "UsCtrlId_Set_SpotAwbRegion" (also seen in a debug log string "[rcam]: ...DebugTool UserSetting, UsId:SpotAwbRegion, Num:%d")`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `awb_region_mode` (Mode/Enable) | uint8 | Inferred by analogy to the confirmed sibling AE Meter Region format; 0=auto/default region, nonzero=manual spot region active. Not directly disassembled for this cmd_id. |
  | 1 | 1 | `awb_region_type` (Region Type) | uint8 | Inferred; in the confirmed AE sibling, value 2 selects the explicit {x,y,w,h} list sub-format that follows. |
  | 2 | 2 | `awb_region_count` (Region Count) | uint16 | Inferred; number of region entries that follow (AE sibling validates <9/max 8; AWB 'spot' likely always sends 1). |
  | 4 | 4 | `awb_region_x` (Region X) | float32 | Inferred; normalized horizontal center/origin of the metering spot (0.0-1.0 of frame width), by analogy to the AE sibling's float32 region entries. |
  | 8 | 4 | `awb_region_y` (Region Y) | float32 | Inferred; normalized vertical center/origin of the metering spot. |
  | 12 | 4 | `awb_region_w` (Region Width) | float32 | Inferred; normalized spot width. |
  | 16 | 4 | `awb_region_h` (Region Height) | float32 | Inferred; normalized spot height. |

**Worked example:**

- Request payload: `01 02 01 00 00 00 00 3F 00 00 00 3F CD CC CC 3D CD CC CC 3D`
  20-byte payload: mode=1 (manual spot), type=2 (explicit list), count=1, region={x=0.5,y=0.5 (frame center, both float32 0x3F000000 LE), w=0.1,h=0.1 (float32 0x3DCCCCCD LE)}. Scenario: pilot taps the live-view center to set a small AWB sampling spot while shooting under mixed tungsten/daylight.
- Response: Set is expected to be ack/err-only (standard duss_event_resp_ok / duss_event_resp_err pattern seen on every sibling *_on_set_* handler in this daemon) — no structured response payload.

## 0x9E — Awb Meter Region Get

_Not decoded._ App queries the currently-configured AWB spot region to redraw the on-screen box after reconnecting to the aircraft mid-flight. Handler correctly identified (Query_SpotAwbRegionFunc (vaddr 0x7ae48) — generic 'query parameter table' accessor indexed by the SpotAwbRegion parameter-table slot, memcpy's taskbuf-cached region data into the caller's output buffer), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9F — Audio Param Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _cs_cam_duss_proxy_on_set_audio_params (vaddr 0x36660)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `audio_channel_config` (Channel/Source Config) | uint16 (bitfield) | Packed config word (mic source/enable bits); exact bit meanings not isolated — real offset/size confirmed by disassembly (ldrh at payload+0), semantics not fully resolved. |
  | 2 | 1 | `audio_channel_select` (Channel Select) | uint8 | Folded into bits 16-23 of the channel_config word by the handler (bfi); likely selects which mic/audio channel the rest of the message applies to. |
  | 3 | 5 | `audio_reserved` (Reserved/Unused) | bytes | Not read anywhere in the disassembled handler — either padding or fields this daemon build ignores. Generic placeholder name used deliberately since no evidence exists for real semantics here. |
  | 8 | 1 | `audio_gain_level` (Gain/Level) | uint8 (enum, masked 0x0E) | Read and masked with 0x0E (keeps a 3-bit value shifted left 1, i.e. one of 8 even values 0-14) — consistent with a small gain/level enum, exact value table not recovered. |
  | 9 | 4 | `audio_flags` (Flags/Reserved32) | uint32 | Copied through verbatim (ldur w10,[payload+9]); real offset confirmed, exact semantic bits not resolved. |
  | 13 | 1 | `audio_format_sub` (Format/Sub-type) | uint8 | Last valid byte of the 14-byte payload; read via a halfword load that only this byte is guaranteed in-bounds for. |

**Worked example:**

- Request payload: `44 00 01 00 00 00 00 00 04 00 00 00 00 01`
  14-byte payload: channel_config=0x0044 (LE), channel_select=1 (external mic), reserved bytes zero, gain_level raw byte=0x04 (masked value 4), flags=0, format_sub=1. Scenario: pilot plugs in an external microphone and raises its input level before starting a video with narration.
- Response: Ack/err only — the handler ends with duss_event_resp_ok() on success (no payload argument passed) after the internal cs_audiodev_uni_set() call succeeds.

## 0xA0 — Audio Param Get

_Not decoded._ DJI Fly app reads back current audio settings (external mic enabled, gain level) when the Audio settings panel is opened. Handler correctly identified (_cs_cam_duss_proxy_on_get_audio_params (vaddr 0x36a58)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA1 — Format Raw SSD

_Not decoded._ User-initiated low-level format of the camera's RAW/SSD storage target (distinct from the ordinary SD-card 'SDcard Do Format' 0x72), used before recording Apple ProRes RAW on the external SSD module. Handler correctly identified (_cs_cam_duss_proxy_on_format_storage (vaddr 0x2f978)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA2 — Focus Distance Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _DjiAAA_CmdMgr_AF_FocusObjDist (vaddr 0x8f300); internal id string "UsCtrlId_Set_FocusObjDist" (exact match for 'Focus [Object] Distance Set')`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `focus_obj_distance` (Focus Object Distance) | uint16 | Target manual-focus distance. Type/size inferred from the confirmed sibling telemetry field camera_camera_shot_info_cur_focus_distance (uint16); exact unit/scale (raw mm vs 0.1 m steps) not confirmed — handler itself not directly disassembled, only name-matched. |

**Worked example:**

- Request payload: `32 00`
  2-byte payload, value 0x0032 = 50 (LE). Scenario: app's manual-focus slider is dragged to a specific object distance (e.g. 5.0 m if the unit is 0.1 m steps) while framing a close-up macro shot.
- Response: No paired Get command exists for 0xA2 in the command list; Set is expected to be ack/err-only like other scalar Set commands in this daemon.

## 0xA3 — Calibration Control Set

_Not decoded._ Factory/service-tool command that triggers one of several internal camera calibration or production-test routines (lens, sensor, or similar), selected by a sub-opcode byte rather than exposing one DUML command per routine. Handler correctly identified (_cs_cam_duss_proxy_on_factory_production (vaddr 0x33cc0)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA4 — Focus Window Set

_Not decoded._ Tap-to-focus: user taps a point on the live preview, and the app converts that screen position into an AF-window-grid rectangle sent to the camera to drive autofocus toward that area. Handler correctly identified (none found directly — searched lib64/librcam.so, lib64/camera/plugins/proxy/libdcam_cs_duss_proxy.so (local symtab), and lib64/libdcam_cs_cbb.so for 'focus_win'/'focuswindow' symbols and found none; the closest named functions (_cs_cam_duss_proxy_on_focus_ctrl @0x46de0 and _cam_on_ctrl_focus @0x47e38) were disassembled and ruled out — they implement a TLV-encoded physical/virtual focus-RING rotation-to-lens-position curve (using pow()/calibration metadata), unrelated to a rectangular AF window.), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA5 — Tracking Region Get

_Not decoded._ Presumed: app queries the currently user-set ActiveTrack/tracking target box (distinct from the live tracking status telemetry already covered by cmd 0x89). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA6 — Tracking Region Set

_Not decoded._ Presumed: user draws an ActiveTrack-style bounding box on the live preview to designate a subject for the camera/gimbal to track, which is forwarded here as a region rectangle. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA7 — Iris Set

_Not decoded._ App/RC sets the still-camera lens aperture (iris). Handler found and fully disassembled (topmode_on_event_aperture_set, lib64/libdcam_topmode_comm.so, E2) with a plausible 2-byte uint16 field (camdev prop id 0x2000001F), but NOT promoted to a full decode: the investigating agent itself flagged medium confidence that this cmd_id binds to this exact DUML command rather than a sibling legacy command, and the claim was not run through adversarial reverify. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA8 — AE Unlock Mode Set

_Not decoded._ Searched for a handler named for 'unlock'/'auto_ae_unlock' across every .so in the e2 camera plugin tree (grep of every library's exported dynsym list for 'unlock'); the only real hits were generic mutex/rwlock-unlock library functions (duss_osal_mutex_unlock etc.), not a camera parameter. The one plausible-looking lead, `topmode_on_event_ae_lock_set` (libdcam_topmode_comm.so, vaddr 0xb350, camdev prop id 0x20000022, 1-byte value), is almost certainly the handler for this project's ALREADY-DOCUMENTED, differently-named cmd_id 0x68 'AE Lock Status Set' (/0x69 Get) instead -- 'AE Lock' (engage/disengage the exposure lock) and 'AE Unlock Mode' (configure whether/how the camera auto-unlocks AE) are different controls, and misattributing one to the other would repeat exactly the kind of cmd_id-conflation mistake this wave's own task brief warned against for BLCOMM. The best semantic analog actually found is the already-documented cmd 0x81 'Camera Shot Params' field `camera_camera_shot_params_not_auto_ae_unlock` (offset 70, uint8) -- but no dedicated Set/Get handler wiring a standalone command to that specific flag was located; it is only known as a sub-field of the big periodic status push. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA9 — AE Unlock Mode Get

_Not decoded._ Same search as 0xA8 (its Set counterpart) -- no dedicated Get handler found, and no generic 'batch read' call site in `libdcam_cs_camera_state.so`'s `cs_camera_state_on_get_usm_batch` (the closest candidate for a generic multi-property Get path found during this pass) was traced far enough to confirm it serves this specific property. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAA — Pano File Params Get

_Not decoded._ Checked the dedicated panorama-still-mode state-machine plugin `lib64/camera/plugins/state/libdcam_cs_topmode_pano_still.so` (has .gnu_debugdata, full local symtab recovered) in detail: it exports per-ISP-parameter getters in the pano context (`_cs_topmode_pano_still_get_iso/aperture/wb/...`) and panorama mode/submode conversion helpers (`topmode_get_panotype_by_op`, `topmode_get_pano_op_by_submode`, `topmode_get_dussrlt_by_panorlt`, `topmode_get_dussphase_by_panophase`, in libdcam_topmode_comm.so) -- none of these return per-file/stitch metadata (filenames, sub-image count, stitch progress) as this GET-only command's name implies. Also checked that this is NOT the same as this project's already-documented, textually similar `camera_camera_cur_pano_file_name_dissector` command (a different, already-known cmd_id for 'current pano file name') -- confirmed distinct, not a source of this command's layout. No handler found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAB — Video Encode Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: topmode_on_event_codec_type_set (vaddr 0x5978, 1036 bytes)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `primary_video_encode_type` (Primary Video Encode Type) | uint8 | Codec for the primary recording stream. Known enum values from this project's cross-referenced public dissector: 0x00, 0x01, 0x64 (likely H.264/H.265/ProRes respectively, labels not resolved by the public dissector either). This pass's own disassembly additionally shows the handler validates for values 2 and 3 (masked together) as an extra ProRes-variant case requiring a storage-media check -- so the real enum has at least 5 members, not just the 3 previously known. |
  | 1 | 1 | `secondary_video_encode_type` (Secondary Video Encode Type) | uint8 | Codec for a second, simultaneous recording stream. Same value space as primary_video_encode_type. |

**Worked example:**

- Request payload: `550f04a2020102004002ab01003aee`
  App -> Camera, seq=2, cmd_id=0xAB, payload = 01 00 (primary=1/H.265, secondary=0/H.264).
- Response payload: `550e046601020200c002ab00e02a`
  Camera -> App, ack-after-exec, 1-byte success return code 0x00.

## 0xAC — Video Encode Get

_Not decoded._ App queries the current primary/secondary recording codec configuration. The Set-side sibling (0xAB Video Encode Set) was independently decoded and verified; this Get was inferred by this project's Set/Get-symmetry convention rather than from a directly disassembled Get handler (no specific camdev_get_user_setting call site with this field's us_id was isolated), so it is not promoted to a full decode despite the underlying research being real. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAD — MCTF Set

_Not decoded._ Searched every .so across both images (e1e and e2) exporting any symbol containing 'mctf' (14 libraries matched: libsensor_imx686.so, libmctf_comm.so, librcam.so, libdcam_frwk.so, libdcam_pp.so, libduml_hal_cam.so, libdcam_cp_adj.so, libdcam_mctf.so, libdcam_async_mctf_stream_filter.so, libdcam_async_independent_mctf_stream_filter.so, libdcam_async_mee_motion_mask_stream_filter.so, lib_hal_mctf.so, and others) -- every hit is a low-level image-pipeline/stream-filter-engine function (cam_mctf_eng_create/config/process/..., mctf_hal_set_param, mctf_motion_*, dcam_adj_mctf_calc_*) operating on frame buffers inside the ISP pipeline, not a DUML-level command parser. None of libdcam_topmode_comm.so's ~90 recovered `topmode_on_event_X_set` camdev-property handlers (the mechanism confirmed for 0xA7/0xAB/0xAF) has an 'mctf'-named entry. The only concrete lead is this project's own already-documented cmd 0x81 'Camera Shot Params' struct, which has adjacent fields `camera_camera_shot_params_mctf_enable` (offset 25, uint8) and `camera_camera_shot_params_mctf_strength` (offset 26, uint8) -- a plausible analog for what a dedicated MCTF Set command's payload would look like, but this is a cross-reference to a different, already-known command's sub-fields, not evidence of a handler for 0xAD itself. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAE — MCTF Get

_Not decoded._ Same search as 0xAD; no Get-side handler found either. See 0xAD's handler_evidence for the full list of 'mctf' symbol hits checked and why each was ruled out as image-pipeline-internal rather than DUML-command-level. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAF — SSD Video Format Set

_Not decoded._ App formats the onboard SSD's video storage filesystem. Handler found and disassembled (topmode_on_event_v_storage_fmt_set, lib64/libdcam_topmode_comm.so, E2; literal camdev prop id 0x20000013, embedded debug name 'v_storage_fmt') with a plausible 1-byte field, but NOT promoted to a full decode: the investigating agent flagged a real cmd_id-binding ambiguity against this project's existing, near-identically-named 'Video Storage Fmt Set/Get' pair at a different cmd_id, and the claim was not run through adversarial reverify. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB0 — SSD Video Format Get

_Not decoded._ App queries the current SSD video storage format setting. Inferred by Set/Get symmetry from 0xAF's handler-backed (but unverified, see 0xAF's own note) 1-byte field; no specific Get-side call site was isolated. Same cmd_id-binding ambiguity caveat as 0xAF applies. Not promoted to a full decode. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB1 — Record Fan Set

_Not decoded._ Tried: full string/symbol sweep of librcam.so + dji_camera3 for 'fan'; disassembly of the 4 candidate functions above; direct check of the generic by-name parameter table (see shared_infrastructure_found) which does list a 'fan_value' entry (param_id 0x37/55) -- but that generic path forwards through libdcam_cs_cbb.so's _cs_proxy_manager_uni_set into libdcam_usm_v2.so's usm_set, which resolves the id via a runtime TREE lookup (_usm_find_descendant_node_by_us_id), not a static size/type table, so even if 'fan_value' is the right parameter its wire size/type can't be read statically; exhaustive registration-mechanism sweep across librcam.so/dji_camera3/libdcam_cs_cbb.so/libdcam_camdev.so/libdcam_topmode_comm.so/libdcam_event_client_pool.so found no literal (cmd_set,cmd_id) binding for 0xB1 in any of them; dji_flight's relocated array independently re-checked and ruled out. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB2 — Record Fan Get

_Not decoded._ Tried: same sweep as 0xB1. The DutyCycle/Percentage/MinDutyCycle/RotationSpeed/Temperature format string is flagged as a concrete, well-evidenced lead for a future pass with more time to trace its actual callers back to a response-builder function, rather than asserted as the decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB3 — Request IFrame

_Not decoded._ Genuinely request/trigger-shaped by name ('Request IFrame' = ask the encoder to emit a keyframe immediately, e.g. after a dropped/resynced video link) -- architecturally plausible as either a zero-payload one-way trigger or a 1-byte stream-selector (Mavic 3 has multiple concurrent video streams: main wide/tele/zoom camera outputs plus FPV), but no disassembled evidence supports either guess, so neither is reported as a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB4 — (name unknown)

Payload decoder: `camera_camera_prepare_open_fan_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_prepare_open_fan_left_seconds` (Left Seconds) | uint8 |  |

## 0xB4 — Camera Prepare Open Fan

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xB5 — Camera Sensor Id Get

_Not decoded._ Plausible by name that the response is either a small numeric sensor-module enum or a fixed-length ASCII module serial string, but neither could be confirmed from static evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB6 — Forearm Lamp Config Set

_Not decoded._ A real, newly-found by-name parameter table exists with 2 lamp-related entries, but no static evidence ties either to this specific dedicated cmd_id, and the underlying storage mechanism (a runtime-populated settings tree) makes the byte layout unrecoverable from static analysis even if the identification were confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB7 — Forearm Lamp Config Get

_Not decoded._ See 0xB6. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB8 — (name unknown)

Payload decoder: `camera_camera_optics_zoom_mode_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_optics_zoom_mode_optics_zomm_mode` (Optics Zomm Mode) | uint8 | enum:`enums.CAMERA_OPTICS_ZOOM_MODE_ZOOM_MODE_ENUM` |
  | 1 | 1 | `camera_camera_optics_zoom_mode_zoom_speed` (Zoom Speed) | uint8 | enum:`enums.CAMERA_OPTICS_ZOOM_MODE_ZOOM_SPEED_ENUM` |
  | 2 | 1 | `camera_camera_optics_zoom_mode_c` (C) | uint8 |  |
  | 3 | 1 | `camera_camera_optics_zoom_mode_d` (D) | uint8 |  |

## 0xB8 — Camera Optics Zoom Mode

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xB9 — Image Rotation Set

_Not decoded._ Genuinely a dead end this pass -- not even a weak candidate function was found, as distinct from the lamp/gimbal-lock/fan entries above which at least have a named parameter-table hit. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBA — Image Rotation Get

_Not decoded._ See 0xB9. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBB — Gimbal Lock Config Set

_Not decoded._ Best-evidenced of the three by-name-table candidates in this batch (direct literal string match, not just numeric-id inference), but still not tied to the dedicated cmd_id by any disassembled wire parser, and the backing store's byte layout is runtime-config-driven rather than statically recoverable. Given the task's own framing that commands of this shape are often a single enum/bool byte, a plausible (but UNCONFIRMED) guess would be a 1-byte lock-enable flag -- explicitly not reported as a decode since no disassembled evidence supports the specific size/offset. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBC — Gimbal Lock Config Get

_Not decoded._ See 0xBB. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBD — Old Cam LCD Format Set

_Not decoded._ Likely a legacy ('Old Cam' in the name suggests backward-compatibility with an older DJI product line) analog-video-format control (e.g. NTSC/PAL) for a camera-mounted or ground-station LCD monitor output. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBE — Old Cam LCD Format Get

_Not decoded._ Paired Get for 0xbd's LCD output format setting. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBF — File Star Flag Set

_Not decoded._ App stars (marks as favorite) one or more photo/video files, or applies star status to an entire storage volume at once, on a given storage device. Handler correctly identified (unnamed local function at file offset 0x39b38 (vaddr 0x3bb38); calls imported cam_file_name_manager_update_file_info_star (from libdcam_fnm.so)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC0 — MFDemarcate

_Not decoded._ Name suggests inserting a demarcation marker between segments of a continuously-written multi-frame capture (e.g. a video/burst file split point or a continuous-shoot boundary tag), but this is a guess from the name alone, not evidenced. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC1 — Log Mode Set

_Not decoded._ Could plausibly be either a picture/color-profile log-gamma mode (D-Log style) or a diagnostic/telemetry logging-mode toggle; name alone is ambiguous and no binary evidence resolves it either way. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC2 — Param Name Set

_Not decoded._ Likely a generic named-parameter interface (set an internal camera parameter by string name rather than a fixed per-parameter cmd_id), analogous in spirit to the already-documented dji_sys 'Param Manager' subsystem for cmd_set 0x00, but no binary evidence ties the two together or resolves this cmd_id's handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC3 — Param Name Get

_Not decoded._ Paired Get for 0xc2's named-parameter interface. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC4 — Camera Tap Zoom Set

_Not decoded._ User taps a subject on the live-view image in the app to trigger tap-to-zoom; the app sends this Set command to the aircraft. Handler found and fully read end-to-end (_cs_cam_duss_proxy_on_set_tap_zoom, lib64/camera/plugins/proxy/libdcam_cs_duss_proxy.so, E2 -- name confirmed via 4 internal debug-log string cross-references), but no byte-level field layout (coordinates, region size, etc.) was recovered from the function body within this pass's budget -- a real handler identification without a field decode, not a search failure. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC5 — Camera Tap Zoom Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _cs_cam_duss_proxy_on_get_tap_zoom (name string at file offset 0x8c582; code at file offset 0x3ab48 / vaddr 0x3cb48)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 0 | `request_payload` (Request Payload) | none | Confirmed no_payload request -- the handler never reads any request byte beyond the generic shared wrapper header. |
  | 0 | 1 | `byte0` (Response byte 0) | uint8 | CONFIRMED hardcoded constant 0x01 in this firmware build (not read from any live camera/engine state in this handler). Likely intended to mirror one of the 'tap_status'/'is_gimbal_moving' fields seen in this same file's periodic status-push struct (cs_cam_pusher_monitor_push_msg, which logs TapZoom.tap_status / TapZoom.is_gimbal_moving / TapZoom.single_magnification as 3 consecutive bytes of an internal status struct), but this specific GET handler returns a compile-time constant rather than a live value. |
  | 1 | 1 | `byte1` (Response byte 1) | uint8 | CONFIRMED hardcoded constant 0x01 (same single instruction, mov w8,#0x0101 then strh, produces both bytes at once). Same caveat as byte0. |

**Worked example:**

- Request payload: `550d0433020101104002c5f09b`
  App(2)->Camera(1), seq=0x1001, cmd_id=0xc5, zero-length payload (confirmed no_payload request).
- Response payload: `550f04a2010201108002c501019b17`
  Camera(1)->App(2), same seq, 2-byte payload 01 01 -- this exact pair of bytes is a hardcoded constant in this handler's code (not computed from live state), so every real-world Get response from this exact build will read back these same two bytes regardless of actual tap-zoom status.

## 0xC6 — Camera Tap Zoom Target Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: _cs_cam_duss_proxy_on_set_tap_zoom_target (name string at file offset 0x8c5a5; code at file offset 0x3ad10 / vaddr 0x3cd10)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `target_x` (Target X (inferred)) | float32 (inferred) | INFERRED, not confirmed by a resolved sub-field read: the handler treats the full 8 bytes as one opaque blob forwarded to an un-traced internal engine callback, so this specific 4/4 float split (normalized [0.0-1.0] screen-space X) is a plausible guess based on total size + DJI's common tap/AF-point convention, not a verified byte boundary. |
  | 4 | 4 | `target_y` (Target Y (inferred)) | float32 (inferred) | Same caveat as target_x -- inferred normalized [0.0-1.0] screen-space Y, not independently confirmed. |

**Worked example:**

- Request payload: `551504a9020102204002c60000003fcdcccc3e4832`
  App(2)->Camera(1), seq=0x2002, cmd_id=0xc6, 8-byte payload = float32(0.5) float32(0.4) little-endian (00 00 00 3F, CD CC CC 3E) under the inferred target_x/target_y split -- i.e. 'zoom target at the point 50% across, 40% down the frame'. The handler itself only verifiably cares that it's exactly 8 bytes; the x/y split is illustrative, not verified.
- Response payload: `550d0433010202208002c6dc56`
  Camera(1)->App(2), same seq, zero-length-payload ack (duss_event_resp_ok) on the success path (internal vtable call returned 0); a nonzero internal return is remapped through a small internal-error-code-to-DUML-error-code lookup table (same idiom shared with the Star Flag handler) and sent via duss_event_resp_err instead.

## 0xC7 — Camera Tap Zoom State Info

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xC7 — (name unknown)

Payload decoder: `camera_camera_tap_zoom_state_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_tap_zoom_state_info_working_state` (Working State) | uint8 | enum:`enums.CAMERA_TAP_ZOOM_STATE_INFO_WORKING_STATE_ENUM` |
  | 1 | 1 | `camera_camera_tap_zoom_state_info_gimbal_state` (Gimbal State) | uint8 |  |
  | 2 | 1 | `camera_camera_tap_zoom_state_info_multiplier` (Multiplier) | uint8 |  |

## 0xC8 — Defog Enabled Set

_Not decoded._ Searched for a 'defog'/'haze'/'dehaze'/'demist' semantic string or symbol anywhere in the e2 (aarch64) camera stack -- bin/dji_camera3, lib64/librcam.so, libdcam_base.so, libdcam_cs_cbb.so, libdcam_pp.so, libdcam_iq_module.so, libdcam_fcali.so, libaaa.so, libduml_hal_cam.so, all camera/plugins/{state,stream_filter,proxy}/*.so, and the e1e (32-bit) dji_rcam userspace binary and rcam_dji.ko kernel module. No match in any binary's string table (strings -a) or exported dynamic-symbol table (readelf -sW, UND and DEFAULT). librcam.so's confirmed internal 'UsCtrlId_Set_*' control-ID enum (~90 Set + ~35 Query entries, the real internal names behind this camera daemon's AE/AF/AWB parameter surface -- see shared_infrastructure_found) has no 'Defog' entry either, so this isn't simply using different internal terminology within that specific subsystem. Also checked dji_flight's small cross-cmd_set relocated dispatch array (vaddr 0xae038-0xae190 in the e1e dji_flight binary) directly by reading its raw 8-byte {fn_ptr,cmd_word} rows -- the only cmd_set 0x02 rows present are cmd_id 0x80/0x81/0x87, not 0xC8. No handler candidate found by any of this project's five known registration mechanisms within this pass's time budget. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC9 — Defog Enabled Get

_Not decoded._ Same exhaustive search as 0xC8 (its Set counterpart) across the same binary set, with the same negative result -- no 'defog'/'haze' semantic lead found anywhere, and not present in dji_flight's cross-cmd_set array or librcam.so's UsCtrlId enum. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xCA — Raw Equip Info Set

_Not decoded._ Searched for 'raw_equip'/'rawequip'/'equip_info'/'equipinfo' across the same e2 camera-stack binaries and e1e dji_rcam/rcam_dji.ko -- no match. The closest semantically-adjacent real entries found are librcam.so's 'UsCtrlId_Set_LensInfo', 'UsCtrlId_Query_LensSN', 'UsCtrlId_Query_LensSpecInfo', and 'UsCtrlId_Query_LensVersion' (all real, confirmed strings in the UsCtrlId enum -- see shared_infrastructure_found), but 'Equip' most likely maps to a different scope than 'Lens' specifically (DJI's public DUML naming distinguishes 'Equip' from 'Lens' elsewhere in the Camera cmd_set), so this is flagged as a weak, unconfirmed candidate for a future pass rather than asserted here. No disassembled handler or byte-level evidence either way. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xCC — SSD Raw Video Digital Filter Set

_Not decoded._ Searched for 'digital_filter'/'digitalfilter'/'raw_video'/'ssd_raw_video' across the e2 camera stack. Found 'STORAGE_MEDIA_SSD_RAW' as a real string in libdcam_cs_cbb.so, but it's one value of a storage-media-type enum (alongside STORAGE_MEDIA_CFCARD/EMMC0/SDCARD0/SDCARD1/SSD/LOCAL0, used by cs_storage_manager_get_prores_storage_media) -- i.e. it identifies *which storage device* holds raw video, not a 'digital filter' setting, so it's not treated as a match. Also checked librcam.so's UsCtrlId_Query_ProresRaw* family (NoiseReduction, Sharpness, Saturation, etc. -- real Query-only entries, no Set_ counterpart found) as a possible loose semantic fit for a ProRes RAW processing toggle, but there is no direct textual match to 'digital filter' and no Set_ entry exists for any of them, so this is not asserted as the handler. No byte-level evidence found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xCE — Calibration Control Get

_Not decoded._ Searched for a general calibration-mode/state toggle. Found extensive 'calib'-prefixed material, but all of it resolves to two different things that are NOT a generic 'Calibration Control' command: (1) libdcam_fcali.so ('factory calibration') exports ~25 fcali_load_*_cali/fcali_save_*_cali functions that load/save specific per-subsystem calibration DATA FILES (awb, sbpc, mtf, dsa, ds, qsc, lrc, dcc, pdaf_type3, intri/extri_param) from disk -- a file I/O layer, not a DUML command handler, and 'CS_CALIB_GOLDEN_LIGHT_ENABLE' is a config-file key it reads, not a wire field. (2) the e1e rcam_dji.ko kernel module has its own unrelated 'cam_ctrl_id_t' ioctl enum with a 'CTRL_CMD_CATEGORY_API_CALIBRATION' category and 'cam_ctrl_id_get_sensor_calib_data' -- a low-level sensor-driver ioctl for reading factory bad-pixel/AWB calibration blobs, not a DUML-level control/status toggle. librcam.so's UsCtrlId enum has calibration-PROCEDURE entries (_DjiAAA_CmdMgr_MTF_Calib, _PDAFType1_Calib, _PDAFType3_Calib) but no generic 'CalibControl'. None of these is a confident match for a Set/Get-style 'Calibration Control' DUML command. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xCF — Mechanical Shutter Set

_Not decoded._ Strongest lead found in this batch, but it falls short of a disassembly-confirmed handler, so it is reported as insufficient_evidence with the lead documented rather than as a decode. librcam.so contains a confirmed real string 'UsCtrlId_Set_ShutterType' (file offset 0x1d4eb9, runtime vaddr 0x1faeb9 in .rodata) as part of the project's newly-catalogued internal UsCtrlId_Set_*/Query_* control-ID enum (see shared_infrastructure_found) -- 'ShutterType' (mechanical vs. electronic vs. EFCS shutter) is the natural internal name for a public 'Mechanical Shutter' DUML command. However, an exhaustive adrp+add xref search for every instruction pair in librcam.so's full disassembly that could materialize this exact string address found zero references -- the string is evidently reached only through an indexed string-pointer table (used by a generic 'print any UsCtrlId name' debug helper), not through a literal per-case reference, so the specific case/handler body that implements the Set logic could not be isolated by this method within this pass's budget. (An earlier intermediate finding in this investigation that pointed to a specific function at vaddr ~0x52d3c-0x52dc8 doing a bounds-checked [0,3] read at struct-offset +72 was traced from what turned out to be a coincidental, unrelated string-offset match at a different page -- 0x1ce000+0xeb9 rather than the real 0x1fa000+0xeb9 -- and is explicitly retracted here rather than reported as if confirmed.) No dji_camera3-side DUML parser for this cmd_id was found either (dji_camera3 itself imports no duss_event_register_dynamic_command* symbol at all -- see shared_infrastructure_found). Flagged for a follow-up pass with budget to resolve the indexed string table and its enum-index-to-case mapping. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xD0 — Mechanical Shutter Get

_Not decoded._ Same lead and same limitation as 0xCF (its Set counterpart): 'UsCtrlId_Set_ShutterType' is confirmed present in librcam.so's internal enum, but no 'UsCtrlId_Query_ShutterType' or equivalent Get-side entry was found in the enum's Query_* list (which is populated almost entirely with DNG/Lens/ProRes-RAW metadata fields, not live AE state), and no disassembled handler could be isolated for either direction within this pass. The Get value is presumably read back from whatever internal state field the Set side writes, but that field's location was not confirmed (see note on 0xCF for the retracted intermediate finding). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xD1 — Cam DCF Abstract Push

_Not decoded._ Searched for 'dcf'/'abstract'/'thumbnail' (DCF = Design rule for Camera File system; an 'abstract' push plausibly means a lightweight metadata/thumbnail notification) across the e2 camera stack including libdcam_cs_storage_mgr_server.so (the storage/media-index subsystem, the most plausible owner of file-abstract pushes) and libdcam_container.so, plus dji_camera3, librcam.so, libaaa.so, and the e1e dji_rcam/rcam_dji.ko. Zero matches for either term as a whole word in any binary's string table. This is a one-way PUSH-style command per its name, consistent with other already-catalogued '*_Push' commands in this project's registry, but no candidate handler or subsystem owner was identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xD2 — Dust Reduction State Set

_Not decoded._ Searched for 'dust'/'dust_reduction'/'dustreduc' across the full e2 camera stack (dji_camera3, librcam.so, libdcam_base.so, libdcam_cs_cbb.so, libdcam_pp.so, libdcam_iq_module.so, libdcam_fcali.so, libaaa.so, libduml_hal_cam.so, all camera/plugins/*/*.so) and e1e dji_rcam/rcam_dji.ko. Zero matches anywhere. Not present in librcam.so's confirmed UsCtrlId enum either. 'Dust reduction' (sensor-shake-style dust removal, as seen on some other camera platforms) does not appear to have a textually-recoverable implementation in this firmware image, or uses internal terminology not guessed in this pass (e.g. a purely numeric/bitmask internal representation with no corresponding debug string). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xD3 — (name unknown)

Payload decoder: `camera_camera_unknownD3_dissector`

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 67 | `camera_camera_camera_unknownD3_field0` (Field0) | bytes |  |

## 0xD3 — Camera UnknownD3

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xDD — ND Filter Set

_Not decoded._ Second-strongest lead in this batch, same category of limitation as 0xCF/0xD0. librcam.so contains a confirmed real string 'UsCtrlId_Set_NDValue' in the same internal control-ID enum (see shared_infrastructure_found) -- an essentially exact semantic match for 'ND Filter Set' (NDValue = the ND filter's stop/density index). Separately, librcam.so also contains a distinct, independently-confirmed debug-console help-text block (reachable from a literal numbered test-command menu, via repeated calls to 'dcam_dbg_append_ack_info') listing usage lines '26: NdFilterControl <NDNumber>' and '27: GetNdFilterCurrentNDNumber', plus runtime log-format strings 'SetNdFilter NDNumber:%d', 'GetNdFilter Current ND NUMBER:fail(%d)', two 'BCPU NDFILTER ... INFORMATION' banner strings, a helper named '_mount_get_ndfilter', and an error string '[rcam]: ...the current mount don`t support ndfilter' -- all confirming ND-filter control is implemented in librcam.so, keyed by a single integer 'NDNumber' parameter, and that it is gated by whether the currently-mounted lens/gimbal module reports ND-filter support. However: (1) that debug-console path is a separate text-command shell (selected by a numeric menu index typed over a debug/test interface), not the production DUML wire parser, and (2) an exhaustive adrp+add xref search for the literal 'UsCtrlId_Set_NDValue' string address found no code reference (same indexed-table-only access pattern noted for ShutterType). So the real DUML cmd_id 0xDD payload-parsing code itself was not isolated. Given the strength of the naming/behavioral match, a single-byte or small-int 'NDNumber' field is a very plausible real layout for a future pass to confirm, but is not asserted here without a disassembled extraction site. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xDE — Raw New Param Set

_Not decoded._ Confirmed via DUML_PROTOCOL/cmdset_02_Camera.md, ALL_COMMANDS.csv and duml_py/duml/commands.json (cmd_id 222, decode_status currently 'none') that no prior decode exists. Traced the real E2/aarch64 camera daemon architecture: dji_camera3 (bin/dji_camera3) is a thin generic plugin host — its own .dynsym imports contain zero duss_event_*/duss_mb_*/cs_cam_* symbols, only generic service_init/plugins_init/plugins_get_* calls, and its strings show it loads its plugin list from '/system/etc/plugins.conf', which is ABSENT from this firmware extraction. The real per-parameter camera logic lives in lib64/camera/plugins/proxy/libdcam_cs_duss_proxy.so, recovered via its .gnu_debugdata minidebuginfo symbol table (~180 local functions, same technique as doc 04's dji_sys recovery). That library exports a matching Set/Get handler pair named _cs_cam_duss_proxy_on_expansion_set / _cs_cam_duss_proxy_on_expansion_get (vaddr range starting 0x3deb0 for the 'on_expansion' family) which is the best semantic name-match for a generic 'raw/expansion parameter passthrough' mechanism consistent with 'Raw New Param'. However I could NOT bind this candidate to the literal byte value 0xDE: (1) the shared per-cmd_id dispatch tables this library exposes via cs_cam_base_duss_proxy_get_default_cmd_tbls()/_override_cmd_tbls() are zero-filled in the .so file itself (populated only at runtime - see shared_infrastructure_found for the full trace); (2) no function anywhere in this library's own .text writes a literal cmd_id immediate for 0xDE via the standard adrp/add+str pattern (checked exhaustively — grep of the full disassembly for 'cmp w*, #0xde' and all 'adrp ...,0xc5000'-style page refs found only unrelated internal-dispatch tables); (3) no other .so/binary in the ~442-file E2 tree statically imports the getter/override functions (checked via nm -D grep across every .so), so the real (cmd_id -> handler) binding is assembled from a runtime config this extraction does not contain. Marking insufficient_evidence rather than inventing a byte layout for a function whose cmd_id binding is unconfirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xDF — Raw New Param Get

_Not decoded._ Same situation as 0xDE (its Set sibling): confirmed no prior decode in this project's own docs/CSV/JSON (cmd_id 223). Candidate handler _cs_cam_duss_proxy_on_expansion_get in libdcam_cs_duss_proxy.so is a plausible name-match (paired with the _set variant used for 0xDE) but the binding to the literal byte 0xDF is unconfirmed for the identical reasons given under 0xDE — the destination dispatch tables are runtime-populated and the data isn't present in this firmware extraction. Also checked: this project's EXISTING decoded command 'camera_camera_raw_params_dissector' (disk_status/disk_capacity/resolution/fps fields) is a confusingly-similarly-named but DIFFERENT, already-cataloged command (storage/disk status), not 0xDE/0xDF — flagging this explicitly so it isn't mistaken for evidence about 'Raw New Param'. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE0 — Capture Sound

_Not decoded._ Searched this project's own docs (no decoder), and exhaustively grepped for 'sound'/'capture_sound'/'beep'/'shutter_sound' in libdcam_cs_duss_proxy.so's full string table (which otherwise contains ~180 very specifically-named _cs_cam_duss_proxy_on_<param> handlers covering nearly every other standard ISP/camera parameter) — zero matches. Also checked librcam.so and dji_camera3 strings directly — no audio/sound-related symbol names at all in the 'camdev' plugin. This strongly suggests 'Capture Sound' (likely the shutter/record audio cue, a tiny feature) is handled by a different category entirely — possibly the audio subsystem reached via libdcam_cs_duss_proxy.so's separate _proxy_handle_audiodev_message dispatch path (a distinct 103-entry category table per shared_infrastructure_found), which I could not resolve to specific named functions since that table has no correspondingly-named exported handler strings either. No candidate handler found; marking insufficient_evidence rather than guessing a payload for an unlocated handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE1 — Capture Config Set

_Not decoded._ No prior decode in project docs/CSV/JSON (cmd_id 225). Weak candidate: _cs_cam_duss_proxy_on_param_option in libdcam_cs_duss_proxy.so (vaddr 0x32040, a notably large handler — 0x32040 to ~0x33cc0, ~7.3KB, consistent with a generic multi-field 'capture config' struct) is the closest semantic match for a generic capture-configuration command, but I found no way to confirm it is bound to cmd_id 0xE1 specifically (same runtime-population problem described in shared_infrastructure_found). Other considered-and-rejected candidates: _cs_cam_duss_proxy_on_set_multicap_param / _on_set_conticap_param (these are specifically continuous/multi-shot burst-count-and-interval parameters, a narrower concept than a general 'Capture Config', and this project's cmd list already has them as a less likely fit given 'Capture Config' sits in the 0xE1/0xE2 pair far from the burst-capture commands numerically). Did not disassemble on_param_option's body in enough depth to extract real field offsets without a confirmed cmd_id binding, per the task's 'never invent a layout without evidence' instruction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE2 — Capture Config Get

_Not decoded._ Get sibling of 0xE1; same situation and same weak/unconfirmed candidate (_cs_cam_duss_proxy_on_param_option, which appears to be a single combined Set+Get-style handler in some of this library's other pairs, but no Get-specific sibling function with a matching name was found for 'param_option' specifically, unlike the clean _set/_get pairs seen for ~80 other parameters in this same library). Marking insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xEC — Camera Subscribe Push

_Not decoded._ The (cmd_set=0x02, cmd_id=0xEC) HANDLER BINDING itself is high-confidence and I independently re-verified it by direct disassembly (this project's doc 16/cmdset_02_Camera.md already asserted it, but I re-derived it from scratch rather than taking that on faith): in the E1E/32-bit-ARM build, lib/libWorkModeLiveview.so, function dji::CamMsgSubscribe::initEventClientCallback() (Thumb-2, vaddr 0x9bb4), at instructions 0x9bc8-0x9bd4 does 'movs r1,#0x2' (cmd_set) / 'movs r2,#0xec' (cmd_id) immediately before 'blx 0x6318' which resolves (via .rel.plt / PLT-stub GOT-offset math, index 102 in .rel.plt, GOT offset 0xfeb8) to duss_event_register_dynamic_command_with_user_data. This is cross-confirmed by a matching teardown in deinitEventClientCallback. Went further than the existing docs by tracing the PAYLOAD: the registered callback is _ZN3dji31_on_event_camera_subscribe_pushEP17duss_event_clientP10duss_eventPv (vaddr 0x9a58), which (when its user_data arg is non-null) calls through to dji::CamMsgSubscribe::handleNewCamMessage(_DUSS_MSG_CAM_SUBSCRIBE_PUSH_t*) (vaddr 0x98f0 — note the parameter's own C-struct type name, recovered from the mangled C++ symbol, confirming a distinct payload struct type exists for this command). Inside handleNewCamMessage I found ONE confirmed real field: a byte at struct offset +0x1 is tested bit-0 only ('ldrb r0,[r4,#1]; lsls r3,r0,#31; ite pl; addpl r4,#4; addmi r4,#8') — bit 0 of this flags byte selects whether the embedded liveview-metadata sub-record begins at struct offset +0x4 (bit clear) or +0x8 (bit set), i.e. this is a format/version selector, and the function then operates starting at (that base)+0x1 as a nested record which is further decoded by dji::CamMsgSubscribe::transCamMsgToWlMetadata() into a duss_wl_liveview_metadata_t. I was not able to fully resolve the complete byte-by-byte layout of that nested metadata record or the meaning of struct offset +0x0 within my review scope, so per the task's 'never invent a layout without real evidence' instruction I am not presenting a full field table — only this one confirmed field, with the handler binding fully confirmed and the rest left open as a concrete, narrowed lead (continue from vaddr 0x98f0 in libWorkModeLiveview.so, specifically the calls at 0x9962/0x996a/0x999e onward which consume the +4-or-8-based sub-record) rather than the vague 'binary-confirmed live, no byte decode' this project's doc previously had. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

- **Handler:** `_ZN3dji31_on_event_camera_subscribe_pushEP17duss_event_clientP10duss_eventPv`
  (`dji::_on_event_camera_subscribe_push`), registered by
  `dji::CamMsgSubscribe::initEventClientCallback`.
- **Purpose:** pushes a subscribed live-view/camera-metadata feed to the
  registering client; the handler plausibly forwards into
  `handleNewCamMessage` → `transCamMsgToWlMetadata` (inferred from
  mangled C++ class/method naming, not a directly-observed call chain).
- **Evidence:** direct call to
  `duss_event_register_dynamic_command_with_user_data(client, cmd_set=0x02,
  cmd_id=0xEC, user_data)` in `libWorkModeLiveview.so` (ARM32/E1E),
  cross-confirmed by a matching teardown call to
  `duss_event_cancel_dynamic_command(client, 0x02, 0xEC)` in the same
  class's `deinitEventClientCallback`.
- **Confidence:** high on the `(cmd_set, cmd_id)` pair and registration
  mechanism; medium on the exact downstream dispatch chain (inferred from
  naming, not traced byte-for-byte). See
  `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.

## 0xF0 — Camera TBD F0

_Not decoded._ DJI's own tooling has no name for this command either (this project's own ALL_COMMANDS.csv/commands.json already record it as literally 'Camera TBD F0' — a placeholder name, not ours). Checked the dji_flight {function_pointer, cmd_word} relocated array at vaddr 0xae038 in dji_flight (E1E) per the task's specific hint: dumped and decoded all 44 rows (confirmed row format = {u32 fn_ptr, u8 cmd_id, u8 cmd_set, u16 reserved=0}); only three cmd_set=0x02 rows exist in that table at all (cmd_id 0x80, 0x81, 0x87) — none is 0xF0 (or any other id in this batch), so this specific lead is cleanly ruled out, not just unexamined. Also checked libdcam_cs_duss_proxy.so's ~180 named handlers and found no obviously-unassigned/'tbd'-style stray handler. No candidate found anywhere. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF1 — Camera Tau Param

_Not decoded._ 0xF1 has no decoder of its own, but its immediate numeric neighbor 0xF2 'Camera Tau Param Get' DOES already have a full, existing byte-level decode in this project (dissector camera_camera_tau_param_dissector; duml_c/generated/registry_data.cpp row {2, 242, 'Camera Tau Param Get', 'full', ...}; duml_py/duml/commands.json). Note: cmdset_02_Camera.md's markdown rendering of this is confusingly laid out (a stray '## 0xF2 — (name unknown)' heading appears before the real '## 0xF2 — Camera Tau Param Get' heading, both describing the SAME dissector/cmd_id 242 per the generated registry — this is a doc-formatting artifact, not two different commands; flagging it since it could mislead a future reader). Given (a) 0xF1's own name is literally 'Camera Tau Param' with no Set/Get suffix — the natural DJI naming convention in this exact cmd_set is '<Param> Set' immediately followed by '<Param> Get' (e.g. 0x1E/0x1F, 0x22/0x23, 0x26/0x27 etc.), so '0xF1 Camera Tau Param' + '0xF2 Camera Tau Param Get' is itself a Set/Get pair where 0xF1 is conventionally the Set half; and (b) hundreds of other Set/Get pairs in this exact cmd_set share one identical payload struct between the Set and Get commands (Set carries the new value, Get returns the current value, byte-for-byte the same layout) — I apply the EXISTING, already-verified 0xF2 struct to 0xF1 as well. This is a real, disclosed inference (not a disassembly of a cmd_id==0xF1-specific parser, which does not appear to exist as a separate code path) and is reported at medium confidence accordingly, exactly mirroring this project's own accepted precedent for 0x26. 'Tau Param' strongly suggests this cmd_set's commands are shared across this DJI chip/binary family with FLIR-Tau-based thermal cameras (e.g. Mavic 3T / M30T-class aircraft) even though this specific WM260/Mavic-3 image may not exercise a thermal sensor at runtime — same 'compiled in, not necessarily reached on this exact aircraft' pattern this project has already documented elsewhere (e.g. cmd_set 0x22 Demo Mode). Handler correctly identified (a handler), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF2 — (name unknown)

Payload decoder: `camera_camera_tau_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `camera_camera_tau_param_image_format` (Image Format) | uint8 |  |
  | 1 | 1 | `camera_camera_tau_param_video_format` (Video Format) | uint8 |  |
  | 2 | 1 | `camera_camera_tau_param_video_fps` (Video Fps) | uint8 |  |
  | 3 | 1 | `camera_camera_tau_param_zoom_mode` (Zoom Mode) | uint8 | enum:`enums.CAMERA_TAU_PARAM_ZOOM_MODE_ENUM` |
  | 4 | 2 | `camera_camera_tau_param_zoom_scale` (Zoom Scale) | uint16 |  |
  | 6 | 1 | `camera_camera_tau_param_digital_filter` (Digital Filter) | uint8 |  |
  | 7 | 1 | `camera_camera_tau_param_agc` (Agc) | uint8 | enum:`enums.CAMERA_TAU_PARAM_AGC_AGC_TYPE_ENUM` |
  | 8 | 2 | `camera_camera_tau_param_dde` (Dde) | uint16 |  |
  | 10 | 2 | `camera_camera_tau_param_ace` (Ace) | uint16 |  |
  | 12 | 2 | `camera_camera_tau_param_sso` (Sso) | uint16 |  |
  | 14 | 1 | `camera_camera_tau_param_contrast` (Contrast) | uint8 |  |
  | 15 | 2 | `camera_camera_tau_param_brightness` (Brightness) | uint16 |  |
  | 17 | 4 | `camera_camera_tau_param_thermometric_x_axis` (Thermometric X Axis) | float |  |
  | 21 | 4 | `camera_camera_tau_param_thermometric_y_axis` (Thermometric Y Axis) | float |  |
  | 25 | 4 | `camera_camera_tau_param_thermometric_temp` (Thermometric Temp) | float |  |
  | 29 | 1 | `camera_camera_tau_param_shot_count_down` (Shot Count Down) | uint8 |  |
  | 30 | 1 | `camera_camera_tau_param_roi_type` (Roi Type) | uint8 | enum:`enums.CAMERA_TAU_PARAM_ROI_TYPE_ENUM` |
  | 31 | 1 | `camera_camera_tau_param_masked1f` (Masked1F) | uint8 |  |
  | 31 | 1 | `camera_camera_tau_param_isotherm_enable` (Isotherm Enable) | uint8 | mask:`0x01` |
  | 32 | 1 | `camera_camera_tau_param_isotherm_unit` (Isotherm Unit) | uint8 |  |
  | 33 | 2 | `camera_camera_tau_param_isotherm_lower` (Isotherm Lower) | uint16 |  |
  | 35 | 2 | `camera_camera_tau_param_isotherm_middle` (Isotherm Middle) | uint16 |  |
  | 37 | 2 | `camera_camera_tau_param_isotherm_upper` (Isotherm Upper) | uint16 |  |
  | 39 | 1 | `camera_camera_tau_param_thermometric_type` (Thermometric Type) | uint8 | enum:`enums.CAMERA_TAU_PARAM_THERMOMETRIC_TYPE_ENUM` |
  | 40 | 1 | `camera_camera_tau_param_object_control` (Object Control) | uint8 |  |
  | 41 | 1 | `camera_camera_tau_param_gain_mode` (Gain Mode) | uint8 | enum:`enums.CAMERA_TAU_PARAM_GAIN_MODE_ENUM` |
  | 42 | 1 | `camera_camera_tau_param_video_resolution` (Video Resolution) | uint8 | enum:`enums.CAMERA_TAU_PARAM_VIDEO_RESOLUTION_ENUM` |
  | 43 | 1 | `camera_camera_tau_param_len_focus_length` (Len Focus Length) | uint8 | enum:`enums.CAMERA_TAU_PARAM_LEN_FOCUS_LENGTH_ENUM` |
  | 44 | 1 | `camera_camera_tau_param_len_fps` (Len Fps) | uint8 | enum:`enums.CAMERA_TAU_PARAM_LEN_FPS_ENUM` |
  | 45 | 1 | `camera_camera_tau_param_photo_interval` (Photo Interval) | uint8 |  |
  | 46 | 1 | `camera_camera_tau_param_unknown2e` (Unknown2E) | uint8 |  |
  | 47 | 1 | `camera_camera_tau_param_ffc_mode` (Ffc Mode) | uint8 | enum:`enums.CAMERA_TAU_PARAM_FFC_MODE_ENUM` |
  | 48 | 1 | `camera_camera_tau_param_masked30` (Masked30) | uint8 |  |
  | 48 | 1 | `camera_camera_tau_param_support_spot_thermometric` (Support Spot Thermometric) | uint8 | mask:`0x01` |
  | 48 | 1 | `camera_camera_tau_param_thermometric_valid` (Thermometric Valid) | uint8 | mask:`0x80` |
  | 49 | 1 | `camera_camera_tau_param_exter_param_type` (Exter Param Type) | uint8 | enum:`enums.CAMERA_TAU_PARAM_EXTER_PARAM_TYPE_ENUM` |
  | 50 | 2 | `camera_camera_tau_param_target_emissivity` (Target Emissivity) | uint16 |  |
  | 52 | 2 | `camera_camera_tau_param_atmosphere_transmission` (Atmosphere Transmission) | uint16 |  |
  | 54 | 2 | `camera_camera_tau_param_atmosphere_temperature` (Atmosphere Temperature) | uint16 |  |
  | 56 | 2 | `camera_camera_tau_param_background_temperature` (Background Temperature) | uint16 |  |
  | 58 | 2 | `camera_camera_tau_param_window_transmission` (Window Transmission) | uint16 |  |
  | 60 | 2 | `camera_camera_tau_param_window_temperature` (Window Temperature) | uint16 |  |
  | 62 | 2 | `camera_camera_tau_param_window_reflection` (Window Reflection) | uint16 |  |
  | 64 | 2 | `camera_camera_tau_param_window_reflected_temperature` (Window Reflected Temperature) | uint16 |  |
  | 66 | 2 | `camera_camera_tau_param_area_thermometric_left` (Area Thermometric Left) | uint16 |  |
  | 68 | 2 | `camera_camera_tau_param_area_thermometric_top` (Area Thermometric Top) | uint16 |  |
  | 70 | 2 | `camera_camera_tau_param_area_thermometric_right` (Area Thermometric Right) | uint16 |  |
  | 72 | 2 | `camera_camera_tau_param_area_thermometric_bottom` (Area Thermometric Bottom) | uint16 |  |
  | 74 | 4 | `camera_camera_tau_param_area_thermometric_average` (Area Thermometric Average) | float |  |
  | 78 | 4 | `camera_camera_tau_param_area_thermometric_min` (Area Thermometric Min) | float |  |
  | 82 | 4 | `camera_camera_tau_param_area_thermometric_max` (Area Thermometric Max) | float |  |
  | 86 | 2 | `camera_camera_tau_param_area_thermometric_min_x` (Area Thermometric Min X) | uint16 |  |
  | 88 | 2 | `camera_camera_tau_param_area_thermometric_min_y` (Area Thermometric Min Y) | uint16 |  |
  | 90 | 2 | `camera_camera_tau_param_area_thermometric_max_x` (Area Thermometric Max X) | uint16 |  |
  | 92 | 2 | `camera_camera_tau_param_area_thermometric_max_y` (Area Thermometric Max Y) | uint16 |  |

## 0xF2 — Camera Tau Param Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0xF9 — Focus Infinite Get

_Not decoded._ No existing decode (cmd_id 249). Candidate: _cs_cam_duss_proxy_on_focus_ctrl in libdcam_cs_duss_proxy.so (vaddr 0x46de0) is a generic focus-control handler name that could plausibly cover infinite-focus toggling alongside ordinary AF/MF control, but (a) its binding to the specific byte 0xF9 is unconfirmed for the same runtime-table reason given in shared_infrastructure_found, and (b) being a 'generic focus control' handler it may dispatch MULTIPLE distinct focus-related cmd_ids via an internal sub-type field I did not have evidence to resolve, so I cannot even be confident it's the right handler rather than one of several separate sibling handlers for ordinary focus mode/region (which already have their OWN confirmed-named handlers _cs_cam_duss_proxy_on_set/get_focus_mode and _on_set/get_focus_region elsewhere in the same library, suggesting 'on_focus_ctrl' is likely something else — e.g. a raw actuator nudge command — making it a weaker fit for 'Infinite' specifically than I initially assumed). Per the task's guidance that many such Get commands have a trivial/no payload, 'no_payload' is plausible for a simple boolean toggle-state readback, but I have no disassembly evidence either way and am not willing to guess between the two. Marking insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFA — Focus Infinite Set

_Not decoded._ Set sibling of 0xF9; same weak/unconfirmed candidate and same reasoning. If this handler is correct, a Set-style 'infinite focus' command would most plausibly be a single enable/disable enum byte (matching this project's own observed pattern that most simple camera-ISP Set commands in this cmd_set carry exactly one enum byte), but I have no disassembly evidence confirming either the handler binding or the byte count, so per instructions I am not asserting a specific layout. Marking insufficient_evidence rather than a low-confidence guessed single-byte layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
