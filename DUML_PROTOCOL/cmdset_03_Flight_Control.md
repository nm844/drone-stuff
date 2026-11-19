# Cmd Set 0x03 — Flight Control

Total known command IDs: 192

## 0x00 — FlyC Scan/Test

_Not decoded._ Checked all three mechanisms this project uses for dji_flight. (1) The relocated {fn_ptr,cmd_word} dispatch array at vaddr 0xae040-0xae190 (43 valid rows -- see shared_infrastructure_found for the full corrected dump) has 5 cmd_set-0x03 rows, at cmd_id 0xea/0x3f/0xc1/0xcd/0xdb; cmd_id 0x00 is not among them. (2) dji_flight's .dynsym imports (readelf -sW, UND symbols) contain no duss_event_register_dynamic_command at all -- confirmed by both grepping .dynsym directly and by the fact no '...@plt' stub for it exists in the disassembled .plt section, so the direct-literal-immediate registration mechanism this project used successfully in dji_sys does not apply to this binary. (3) dji_flight's only duss_mb_create_route_table + duss_event_create_client call pair (Thumb disasm, single call site at vaddr 0x22b96/0x22c1a) is JSON-config-driven: the route table is built by duss_mb_create_route_table(path="/system/etc/dji.json", service_name="flight_service", ...) and the client is tagged with a 3rd literal string "flight_srv_fmu" (all three strings resolved via PC-relative literal-pool cross-reference and read directly from .rodata at 0x9c958/0x9c970/0x9c980). That config file is not present anywhere in this firmware extraction (find across both e1e_extracted and e2_extracted found no dji.json), so the actual per-cmd_id switch inside whatever generic callback this registration installs could not be statically recovered -- the callback's own address is not visible as a literal argument to duss_event_create_client in the disassembly (its likely location, [ctx+4], is only ever referenced by address-of, never by value, in the one call site found). Grepped all ~10k dji_flight strings for 'scan'/'test'-adjacent terms; the only 'SCAN' hits are unrelated bundled-sqlite query-planner strings ('SCAN TABLE %s%s%s'). No cmd_id-0x00-specific function was identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x01 — FlyC Status Get

_Not decoded._ Same architectural dead-end as 0x00: not one of the 5 cmd_set-0x03 rows in the dispatch array (0xea/0x3f/0xc1/0xcd/0xdb), no duss_event_register_dynamic_command import to find a literal binding, and the one route+client registration is JSON-config-driven with the config file absent from this extraction. One loose, unconfirmed lead: the string 'is_status_pushed:%hu' exists at rodata 0x97a24, which is at least thematically close ('status'), but tracing its xref shows it belongs to a generic internal state-machine status print (no connection found to any incoming-payload parse, and no cmd_id comparison near it), so it is not asserted as this command's handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x02 — FlyC Params Get

_Not decoded._ A real false lead worth recording explicitly, since it name-matches so well: dji_flight contains a cluster of 'FC_PARAM:' debug strings ('FC_PARAM: rcv undefine cmd:%d' @0x95b40, 'FC_PARAM: invalid data len:%d' @0x95a40, 'FC_PARAM: %s, write fail, %d' @0x95afc) backing a real sub-command dispatcher at vaddr 0x1a5c0 that reads a 1-byte sub-cmd from ctx->data[0] (ctx+8=data ptr, ctx+12=u16 length -- the same {data_ptr@+8, len@+12} convention recurs across dji_flight's handlers) and switches on values 1/2/3 with a default 'undefined cmd' error. This is exactly the shape I was looking for cmd_id 0x02 ('Params Get'). However, I cross-checked it against the dispatch array rather than trusting the name match: the function's own Thumb-tagged address (0x1a5c1) appears as a raw relocated data word at file-offset 0xad0b0, which is precisely dispatch-array row 14 (vaddr 0xae0b0) -- and that row's cmd_word decodes to cmd_set=0x11 (ADSB), cmd_id=0x01, not cmd_set 0x03. So FC_PARAM is conclusively a cmd_set-0x11 (ADS-B parameter) sub-protocol, not cmd_set-0x03's 'FlyC Params Get' -- a good example of a name-based lead that the registration-table cross-check actually disproves rather than confirms. No other 'param'-named function was found specific to cmd_set 0x03. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x03 — Origin GPS Set

_Not decoded._ Strongest lead in this batch, but still short of a wire-level binding. Found a genuine, named GPS-origin subsystem: update_nfz_gps_origin (vaddr 0x16e80-0x17048ish) validates a live telemetry struct's lat/lon (float64 fields at that struct's +8/+16, range- and non-zero-checked via vcmpe.f64) before committing an NFZ origin record, logging '[%s]:update nfz origin[%f %f %f] elevation:%f' (rodata 0x95154). Nearby, fc_event_cb_nfz_dynamic_update (0x19860), fc_event_cb_nfz_fc_dynamic_update (0x19ad0), and fc_event_cb_nfz_enquery (0x1a07c-ish; all 3 names recovered via the same PC-relative literal-pool string xref technique used elsewhere in this project) read a sub-cmd byte from ctx->data[0] via the same {data@+8} convention. The '_cb' / '_enquery' naming is exactly DJI's convention for a registered event callback elsewhere in this project's docs, which is why this is flagged as the best lead, not a weak one. What's missing: none of these three functions' addresses appear in the 43-row dispatch array (ruling that mechanism in or out), dji_flight has no duss_event_register_dynamic_command import to find a literal (cmd_set,cmd_id) binding for them, and the one JSON-driven client registration's internal cmd_id dispatch could not be located (config file absent, see 0x00's note). I could not determine which of these functions, if any, is reached specifically via DUML cmd_id 0x03 vs. 0x04 vs. an internal (non-DUML) GPS-subsystem event, so no byte offsets are asserted. Flagged as a concrete, bounded lead for a future pass with better tooling (recovering dji_flight's generic client callback via a C++ vtable/RTTI-aware disassembler would likely resolve this). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — Origin GPS Get

_Not decoded._ Same lead and same gap as cmd_id 0x03 (Origin GPS Set) -- see that entry for the full update_nfz_gps_origin / fc_event_cb_nfz_* cluster. A 'Get' counterpart most plausibly corresponds to fc_event_cb_nfz_enquery ('enquery' = query) by name alone, but I found no registration-mechanism evidence (table row, literal immediate, or resolved JSON config) tying it to cmd_id 0x04 specifically, so this remains a named-but-unbound lead rather than a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x05 — GPS Coordinate Get

_Not decoded._ No function specific to a live/generic GPS coordinate query (distinct from the NFZ-origin cluster used for cmd_id 0x03/0x04) was found. Checked the dispatch array (not present, same 5 cmd_set-0x03 rows as every other entry in this batch), checked for a 'coordinate'/'gps_push'/'position' string cluster separate from the NFZ-origin one (none found beyond the single bare word 'origin' at rodata 0xa13f4, which traces to an unrelated SQL-grammar-table string from the bundled sqlite amalgamation, not flight code), and confirmed the same architectural blockers (no register_dynamic_command import; the one route+client registration is JSON-config-driven with the config absent from this extraction). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x06 — Fly Limit Param Set

_Not decoded._ Grepped all ~10k extracted strings in dji_flight for 'limit'/'fly_limit'/'flylimit'/'max_'-style terms; the only 'limit' hits are unrelated bundled-sqlite strings ('cannot limit WAL size: %s', 'LIMIT clause should come after %s not before'). Not one of the 5 cmd_set-0x03 dispatch-array rows (0xea/0x3f/0xc1/0xcd/0xdb). Same registration-mechanism blockers as every entry in this batch (no register_dynamic_command import; sole route+client registration is JSON-config-driven, config file not present in this extraction). No candidate handler found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x07 — Fly Limit Param Get

_Not decoded._ Identical research trail and identical result to cmd_id 0x06 (Fly Limit Param Set) -- see that entry. No fly-limit-specific strings or functions found; same architectural blockers apply. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x08 — Nofly Zone Set

_Not decoded._ Disassembled the NFZ-area-update function fc_event_cb_nfz_dynamic_update (vaddr 0x19860) in full: it reads a 1-byte sub-cmd from ctx->data[0] (same {data@+8} convention as elsewhere in dji_flight) and, for the sub-cmd-0/default path, runs a chunked-upload loop -- a growable, ~50-entry polygon/area table filled via repeated bounded memcpy of a per-chunk record whose size is itself taken from a payload length byte, with malloc/free bookkeeping of a running byte budget. This matches the task's own prediction that the Upload/Download-Nofly-Area-adjacent commands are chunked-blob-transfer shaped, not small fixed structs. However, on reflection this looks architecturally closer to the ALREADY-catalogued dispatch-array entry for cmd_set 0x03/cmd_id 0xcd ('Update Nofly Area', table row 12, fn_ptr 0x1144c) than to the lighter-weight single-record shape implied by this project's own description of cmd_id 0x08 ('Nofly Zone Set', 'ordinary geographic-data fields: lat/lon/radius/shape-type') -- except fc_event_cb_nfz_dynamic_update's own address (0x19861 tagged) is NOT the 0x1144d stored in that row, so it is not literally that table entry's target either. I could not find a simpler, single-circle-NFZ handler matching the expected cmd_id-0x08 shape, and could not establish fc_event_cb_nfz_dynamic_update's real (cmd_set,cmd_id) binding via any available mechanism (not in the dispatch array; no register_dynamic_command import; JSON-driven client registration's config absent). Reporting insufficient_evidence rather than asserting a field layout I can't tie to this specific cmd_id with confidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x09 — Nofly Status Get

Payload decoder: `flyc_flyc_forbid_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_forbid_status_flight_limit_area_state` (Flight Limit Area State) | uint8 | enum:`enums.FLYC_FORBID_STATUS_FLIGHT_LIMIT_AREA_STATE_DJI_FLIGHT_LIMIT_AREA_STATE_ENUM` |
  | 1 | 1 | `flyc_flyc_forbid_status_dji_flight_limit_action_event` (Dji Flight Limit Action Event) | uint8 | enum:`enums.FLYC_FORBID_STATUS_DJI_FLIGHT_LIMIT_ACTION_EVENT_ENUM` |
  | 2 | 1 | `flyc_flyc_forbid_status_limit_space_num` (Limit Space Num) | uint8 |  |
  | 3 | 4 | `flyc_flyc_forbid_status_unknown3` (Unknown3) | bytes |  |

## 0x0A — Battery Status Get

Payload decoder: `flyc_battery_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_battery_status_not_ready` (Not Ready) | uint8 |  |
  | 1 | 1 | `flyc_battery_status_comm_err` (Comm Err) | uint8 |  |
  | 2 | 1 | `flyc_battery_status_first_auth` (First Auth) | uint8 |  |
  | 3 | 1 | `flyc_battery_status_auth_fail` (Auth Fail) | uint8 |  |
  | 4 | 1 | `flyc_battery_status_need_re` (Need Re) | uint8 |  |
  | 5 | 1 | `flyc_battery_status_volverylow` (Voltage Very Low) | uint8 |  |
  | 6 | 1 | `flyc_battery_status_volnotsafe` (Voltage Not Safe) | uint8 |  |
  | 7 | 1 | `flyc_battery_status_vollevel1` (Voltage Level 1) | uint8 |  |
  | 8 | 1 | `flyc_battery_status_vollevel2` (Voltage Level 2) | uint8 |  |
  | 9 | 1 | `flyc_battery_status_caplevel1` (Capacity Level 1) | uint8 |  |
  | 10 | 1 | `flyc_battery_status_caplevel2` (Capacity Level 2) | uint8 |  |
  | 11 | 1 | `flyc_battery_status_smartcap1` (Smart Capacity 1) | uint8 |  |
  | 12 | 1 | `flyc_battery_status_smartcap2` (Smart Capacity 2) | uint8 |  |
  | 13 | 1 | `flyc_battery_status_d_flg` (D Flag) | uint8 |  |
  | 14 | 1 | `flyc_battery_status_ccsc` (CCSC) | uint8 |  |
  | 15 | 4 | `flyc_battery_status_all` (All Flags Combined) | uint32 |  |

## 0x0B — Motor Work Status Set

_Not decoded._ Found and fully disassembled a motor-error-reporting routine at vaddr 0x209d4, backing the strings 'regist motor error code, result %d' (0x9a21c) and 'fc give motor ext error code:%d' (0x9a258): it reads ctx->data[8] as a bool flag, then ctx->data+8's own +0/+1/+6 fields ({u8 motor_id?, u32 error_code, u8 ext_error_code}) and iterates printing them. On inspection this is a diagnostic DUMP of already-stored error state (pure formatted output, no incoming-payload field extraction, no write/'set' semantics), so it does not match 'Motor Work Status Set' -- which by name should be an incoming command that changes motor work-state, not a log dump. Ruled out as this command's handler rather than asserted. No other motor-work-state-specific function was found. Same architectural blockers as the rest of the batch apply (not in the dispatch array; no register_dynamic_command import; JSON-driven registration's config absent from this extraction). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0C — Motor Work Status Get

_Not decoded._ ALL_COMMANDS.csv lists typical_receiver as 'Flight Controller' for this command. dji_flight links against libduml_hal.so (Linux UART/SPI HAL: duss_hal_uart_read/write, duss_hal_attach_linux_tty, embedded source paths hardware/dji/duml/hal/linux/{uart/linux_tty.c,spi/linux_spi.c}) and, more precisely, libduml_frwk.so (the message-bus framework dji_flight actually calls into for route-table/client registration) directly imports duss_hal_uart_write/read, duss_hal_spi_write/read and duss_hal_attach_linux_tty/pcie. dji_flight's single duss_mb_create_route_table+duss_event_create_client call subscribes it to cmd_set 0x03 (among 9 others) as one generic bus client, but there is essentially no per-command parsing code of its own for the bulk of that range. This strongly indicates 'Flight Controller' in typical_receiver means the physical flight-controller MCU reached over UART/SPI through libduml_frwk.so/libduml_hal.so, with dji_flight acting mostly as a transparent bus-to-serial bridge for this command, not a command that dji_flight itself parses -- directly analogous to this project's existing cmd_set 0x06 (RC-MCU-local) and cmd_set 0x01 (RTOS-blob) findings. A 4.5MB non-ELF blob (e1e_extracted/rtos_dec_RTOS.bin, confirmed present, 'file' reports plain data) remains an unchased lead for where the real MCU-side firmware/parsing would live. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0D — Statistical Info Save

_Not decoded._ Same architectural conclusion as 0x0c (typical_receiver = Flight Controller; dji_flight is a thin UART/SPI bus bridge via libduml_frwk.so/libduml_hal.so for the bulk of cmd_set 0x03, with no local field-parsing code found for this command). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0E — Emergency Stop

_Not decoded._ Same architectural conclusion as 0x0c/0x0d. Emergency Stop, being a safety-critical, single-shot motor-kill command, is exactly the kind of low-level command that would plausibly be forwarded byte-for-byte to the flight-controller MCU rather than parsed in the Android daemon, though no direct evidence of its specific wire format was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x10 — A2 Push Commom

Payload decoder: `flyc_a2_commom_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_a2_commom_a` (A) | uint8 |  |
  | 1 | 1 | `flyc_a2_commom_b` (B) | uint8 |  |
  | 2 | 4 | `flyc_a2_commom_c` (C) | uint32 |  |
  | 6 | 4 | `flyc_a2_commom_d` (D) | uint32 |  |
  | 10 | 1 | `flyc_a2_commom_control_mode` (Control Mode) | uint8 | enum:`enums.FLYC_A2_COMMOM_E_DJIA2_CTRL_MODE_ENUM` |
  | 11 | 1 | `flyc_a2_commom_f` (F) | uint8 |  |

## 0x11 — Sim Rc

_Not decoded._ Same architectural conclusion as other batch commands. By name and by structural analogy with this project's already-decoded sibling commands (0x06/0x05 'RC Parameter Get/Push' and 0x06/0x26 'RC AETR Value Push', both int16 aileron/elevator/throttle/rudder at offsets 0/2/4/6), a plausible layout for 'Sim Rc' would be the same 4x int16 stick-value struct used to inject simulated RC input into the flight control loop -- but no disassembled handler or cross-referenced schema was found to support this for cmd_set 0x03/0x11 specifically, so it is flagged as a plausible lead only, not asserted as a real decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x16 — Sim Status

_Not decoded._ Same architectural conclusion as 0x11. Likely a simulator-mode-active status push/get paired with 0x11's simulated-RC-injection, but no handler evidence found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1C — Date and Time Set

_Not decoded._ Same architectural conclusion as other batch commands (typical_receiver = Flight Controller; no local dji_flight parsing code found). By name, a plausible layout would be a packed date/time struct (e.g. year/month/day/hour/min/sec, or a single uint32 Unix timestamp), matching common DUML time-sync conventions elsewhere in this project's docs -- but this is an unverified guess with zero binary evidence behind it for this specific command, so it is explicitly not asserted as a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1D — Initialize Onboard FChannel

_Not decoded._ Same architectural conclusion as other batch commands. 'FChannel' (likely 'Function Channel', DJI's term for configurable auxiliary PWM/servo output channels on the flight controller) is exactly the kind of raw hardware-I/O feature that would live on the physical MCU side rather than be parsed by the Android daemon; no handler evidence found to support a specific byte layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1E — Get Onboard FChannel Output

_Not decoded._ Same architectural conclusion as 0x1d (paired get for the FChannel I/O feature). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1F — Set Onboard FChannel Output

_Not decoded._ Same architectural conclusion as 0x1d/0x1e (paired set for the FChannel I/O feature). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x20 — Send GPS To Flyc

_Not decoded._ Same architectural conclusion as other batch commands. This command injects an external GPS fix into the flight controller (e.g. from an external GPS/RTK module) -- plausibly a lat/lon/alt/accuracy struct by analogy with cmd_set 0x03's already-documented 'Origin GPS'/'GPS Coordinate' family, but no disassembled handler was found to confirm specific offsets, so no layout is asserted. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — UAV Status Get

_Not decoded._ Likely a simple status-poll request (armed/flying-mode/GPS-health style aircraft status), by name and by its ALL_COMMANDS.csv typical_receiver='Flight Controller', typical_request_sender='APP/RC/PC'. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — Upload Air Route

_Not decoded._ By name, an app-to-aircraft upload of a full 'air route' (mission plan) -- plausibly a chunked blob transfer, as the task hint suggested by analogy to cmd_set 0x00/0x2A 'FileTrans General Trans' (phase byte + 4-byte length/part-no + filename/data payload, per duml_py/duml/commands.json's existing decoded entry for that command). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x23 — Download Air Route

_Not decoded._ The read counterpart to 0x22 -- app requests the aircraft's currently-stored air route back, plausibly chunked the same way. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x24 — Upload Waypoint

_Not decoded._ By name, uploads individual waypoint records (lat/lon/alt/action per point) into a previously-created air route. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x25 — Download Waypoint

_Not decoded._ Read counterpart to 0x24 -- app requests individual waypoint records back from the aircraft. (dji_flight's own strings include an exact-matching log line 'app req waypoint info' and 'size of download waypoint invalid, buf data len: %d' / 'download fail for not upload waypoint, waypoints num: %d', but these were traced to the confirmed-distinct 'Waypoint 2.0' api_wp2_download_waypoint function, not to this legacy cmd_set 0x03/0x25 command -- see handler_evidence.) No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x26 — Enable Waypoint

_Not decoded._ By name, likely toggles whether the uploaded waypoint mission is armed/active -- plausibly a tiny single-byte (bool, or route-ID + bool) payload, but this is pattern inference from the name only, not binary evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x27 — Exec Fly

_Not decoded._ By name, triggers execution/start of the previously-uploaded mission -- plausibly a trigger-only or near-trigger-only command (the public dissector's own source comment notes a newer-platform variant repurposes this same cmd_id as 'Suspend Resume Waypoint', suggesting a small mode/action-selector payload on some platforms). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x28 — One Key Back

_Not decoded._ By name, a 'return to home' (RTH) trigger command -- plausibly trigger-only or carrying a small mode selector. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x29 — Joystick

_Not decoded._ The real-time virtual-stick / manual flight-control-override command -- by strong architectural analogy to every public DJI Mobile SDK generation's 'Joystick'/'Virtual Stick' command, this is almost certainly a fixed-size, high-frequency struct of 4 signed control axes (roll/pitch/yaw/throttle, likely int16 or float32) plus a mode-flags byte. This analogy is NOT asserted as the decoded layout -- it is explicitly flagged as inference, not evidence, per the no-invented-layouts rule. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2A — (name unknown)

Payload decoder: `flyc_function_control_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_function_control_function_command` (Function/Command) | uint8 | New value of g_real.wm610_app_command.function_command |

## 0x2A — Function Control

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x2B — IOC Mode Type Set

_Not decoded._ Sets DJI's 'Intelligent Orientation Control' mode (the public dissector's own comment glosses this exact command as such) -- by name, plausibly a single mode-enum byte (e.g. Course Lock / Home Lock / Free), analogous in shape to this project's existing small-enum decodes elsewhere (e.g. cmd_set 0x22/0x60 'Demo Mode Handle'), but this is pattern inference only. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2C — IOC Mode Type Get

_Not decoded._ A query for the current IOC (Intelligent Orientation Control) mode/type. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2D — Limit Params Set

_Not decoded._ Sets flight limit parameters (e.g. max altitude/radius/velocity limits). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2E — Limit Params Get

_Not decoded._ Reads back the current flight limit parameters. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2F — Battery Voltage Alarm Set

_Not decoded._ Sets low-battery-voltage alarm threshold(s). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x30 — Battery Voltage Alarm Get

_Not decoded._ Reads back the current low-battery-voltage alarm threshold(s). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x31 — UAV Home Point Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: nav_v1_flight_api_set_homepoint (name recovered from its own embedded debug string, not a surviving symbol)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `set_homepoint_mode` (Set-home mode/operation byte) | uint8 | First packed field (original function argument #0, a byte). Likely a mode selector (e.g. 'use current GPS fix' vs 'use the explicit values below'), by analogy with DJI's known home-point-set semantics, but no comparison/switch against this byte was visible in the disassembled window, so the exact enum values are NOT confirmed -- reported honestly as unconfirmed. |
  | 1 | 4 | `set_homepoint_param_a_f32` (Parameter A (4-byte, position-related, unconfirmed exact role)) | float32 | Byte offset/size are HIGH confidence (independently reproduced in two separately-compiled sender implementations). The specific physical quantity is NOT confirmed: no string or comparison ties it to latitude specifically. Note this does not match the sibling already-decoded command 'OSD Home Point Get' (cmd_id 0x44, same cmd_set 0x03), which uses 8-byte doubles for lat/lon -- so this Set command most likely does NOT carry raw double-precision GPS coordinates, and the 4-byte size here is a genuine, confirmed structural fact, not a guess. |
  | 5 | 4 | `set_homepoint_param_b_f32` (Parameter B (4-byte, unconfirmed exact role)) | float32 | Same confidence profile as param_a. Natural positional guess (if param_a is a latitude-like value) would be a longitude-like value, but this is not independently confirmed. |
  | 9 | 4 | `set_homepoint_param_c_f32` (Parameter C (4-byte, unconfirmed exact role)) | float32 | Same confidence profile as param_a/param_b. Could plausibly be an altitude or a distance/radius limit, by analogy with other DJI home-point-adjacent telemetry, but not confirmed. |
  | 13 | 4 | `set_homepoint_param_d_f32` (Parameter D (4-byte, unconfirmed exact role)) | float32 | Same confidence profile as the other 4-byte fields. No distinguishing evidence found for its specific role (e.g. heading vs a secondary limit vs reserved). |
  | 17 | 1 | `set_homepoint_flag` (Trailing flag/validity byte) | uint8 | Final packed byte (original function argument from the 3rd stack slot). Position/size confirmed; semantic role (e.g. a 'coordinates valid' or 'GPS health' boolean) is an educated guess, not confirmed. |

**Worked example:**

- Request payload: `00 AF 94 B4 41 A3 E1 E3 42 00 00 20 41 00 00 00 00 01`
  18-byte payload. Byte0=0x00 (mode byte, guessed meaning 'use the explicit parameters below'); bytes1-4 = float32 0x41B494AF = 22.5726 (illustrative 'param_a', chosen to look like a plausible latitude value for documentation purposes only -- NOT a confirmed field identity); bytes5-8 = float32 0x42E3E1A3 = 113.9407 ('param_b', illustrative longitude-shaped value); bytes9-12 = float32 0x41200000 = 10.0 ('param_c', illustrative altitude-shaped value in meters); bytes13-16 = float32 0.0 ('param_d', illustrative/reserved); byte17 = 0x01 (flag byte, illustrative 'valid' value).
- Response payload: `00`
  A single-byte DUML ack/return-code payload (0x00 = success), inferred from the sender's own 'ack fail %d' / 'fail, reason: %d' debug strings, which imply a short numeric result code comes back rather than a data payload. The exact response byte count was not independently confirmed from a receiving-side parser (none was found in any extracted ELF binary), so this is a best-effort convention-based guess, disclosed as such.

## 0x32 — FlyC Deform Status Get

Payload decoder: `flyc_flyc_deform_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_deform_status_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `flyc_flyc_deform_status_deform_protected` (Deform Protected) | uint8 | mask:`0x01` |
  | 0 | 1 | `flyc_flyc_deform_status_deform_status` (Deform Status) | uint8 | enum:`enums.FLYC_DEFORM_STATUS_DEFORM_STATUS_TRIPOD_STATUS_ENUM`; mask:`0x0e` |
  | 0 | 1 | `flyc_flyc_deform_status_deform_mode` (Deform Mode) | uint8 | enum:`enums.FLYC_DEFORM_STATUS_DEFORM_MODE_ENUM`; mask:`0x30` |

## 0x33 — UAV User String Set

_Not decoded._ Sets a user-assignable aircraft name/label string. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x34 — UAV User String Get

_Not decoded._ Reads back the user-assignable aircraft name/label string. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x35 — Change Param Ping

_Not decoded._ Appears, by name, to be a lightweight liveness/ack-style ping tied to a parameter-change notification mechanism. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x36 — Request SN

_Not decoded._ Requests the aircraft's serial number. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x37 — Device Info Get

_Not decoded._ No handler located. dji_flight's own 43-row {fn_ptr,cmd_word} dispatch table (see shared_infrastructure_found) contains no cmd_set 0x03 row for 0x37, and dji_flight imports no duss_event_register_dynamic_command symbol at all, so there is no literal-immediate call site to find either. A plausible alternate owner was identified but not confirmed: dji_sys (NOT dji_flight) is the only WM260 binary that links libduml_dn.so, which exports dn_device_info_query/dn_device_info_parse -- a generic, multi-device-type 'device info' subsystem. dn_device_info_parse(buf,ctx) reads a uint16 at payload offset 0, masks it to its low 4 bits ('device_type', 0-15), and uses that as an index into a 16-entry, 8-byte-stride function-pointer table to pick a per-device-type parser before reading any further bytes -- so IF cmd_set 0x03's Device Info Get/Set routes through this generic mechanism, the wire format would start with a device_type selector, not FC-specific fields directly. I did not find where (or whether) this generic dispatcher is wired to cmd_set 0x03 specifically -- dji_sys's 11 duss_event_register_dynamic_command call sites (fully enumerated, see shared_infrastructure_found) never pass cmd_set=3, so if this path is used at all it must be through dji_sys's JSON-config-driven 'command agent' registration (already characterized in doc 04 as not statically recoverable -- the config file isn't in this extraction) rather than a literal immediate. No strings matching device_info/serial/hw_version/product_id/board_id were found anywhere in dji_flight's .rodata. Not resolved; this is a concrete lead (dn_device_info_parse's device-type dispatch table in libduml_dn.so) for a future pass, not a confirmed binding. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x38 — Device Info Set

_Not decoded._ Same search and same result as 0x37 (Device Info Get) -- not in dji_flight's dispatch table, dji_flight has no duss_event_register_dynamic_command import, and dji_sys's libduml_dn.so generic device-info subsystem (dn_device_info_query/dn_device_info_parse) is a plausible but unconfirmed owner. No cmd_set-0x03-specific evidence found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x39 — Enter Flight Data Mode

_Not decoded._ No cmd_id-specific handler located. dji_flight does contain a real, named internal flight-data/blackbox subsystem (debug strings FLIGHT_DATA_MUTEX, flight_data_size:%d, recorder_init, __recorder_reg_dev, bb recorder inited, recorder_monitor for %s, fc_recorder_cfg, recorder cfg send!, Error: recorder block cfg!), confirming this general subsystem is real and alive in this exact binary -- but the function I traced two of these strings to (vaddr ~0x21656-0x2173e, via direct xref of 'recorder cfg send!' and 'Error: recorder block cfg !') turned out to be a snprintf-based circular ring-buffer LOGGER (writing dji_flight's own diagnostic log lines into a rotating buffer), not a DUML wire-payload parser keyed on a specific cmd_id. I could not locate the xref site for 'fc_recorder_cfg' itself (it doesn't appear near any ldr+add-pc string-load pair reachable from Thumb code in a ~500 Thumb/ARM-mixed-mode scan of .text, suggesting it's referenced from ARM-mode code or via a different addressing idiom I didn't crack) so I can't confirm whether that specific string belongs to the same function or a distinct one. Neither 0x39 nor 0x3a could be tied to a specific duss_event_register_dynamic_command call site or dispatch-table row (0x03/0x39 and 0x03/0x3a are both absent from dji_flight's 43-row table and from all 11 of dji_sys's literal registration call sites). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3A — Ctrl Fly Data Recorder

_Not decoded._ Same subsystem and same result as 0x39 -- the 'recorder' debug strings found in dji_flight belong to an internal diagnostic ring-buffer logger, not a disassembled parser keyed on cmd_id 0x3a, and 0x03/0x3a is absent from both dji_flight's dispatch table and dji_sys's 11 literal registration call sites. 'fc_recorder_cfg' (the string whose name most directly suggests a configuration struct matching this command's 'Ctrl ... Recorder' naming) could not be xref'd to any specific function with the tooling used this session. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3B — RC Lost Action Set

_Not decoded._ No handler for cmd_id 0x3b itself was found (absent from dji_flight's dispatch table and from dji_sys's literal registration sites), but a concrete, strongly-named architectural lead was found and is reported here rather than withheld: dji_flight contains a real, live debug-dump function (vaddr 0x1bdb4, called from exactly one site, vaddr 0x1bab2, inside a larger function starting at vaddr 0x1b97c) that prints a 'Waypoint Mission Init Info' struct field-by-field via a literal printf-style format-string table. One of its fields, at struct offset 19, size 1 byte, is logged with the format string 'action_when_rc_lost : %d\n' -- i.e. this exact aircraft binary, on this exact firmware, has a real uint8 enum field literally named 'action_when_rc_lost'. This is NOT itself cmd 0x3b's payload (it's one field inside a different, larger waypoint-mission struct, most likely belonging to a mission-init command in the 0x80-0x9f range, not independently identified by cmd_id in this pass) -- but it is strong, real, disassembly-confirmed evidence that DJI's own internal naming for this exact behavioral concept is a 1-byte enum, which is architecturally very likely to be the same shape (and possibly the same enum constants) that cmd_set 0x03's standalone 'RC Lost Action Set/Get' pair reads and writes. Per this project's rule against inventing layouts without command-specific evidence, this is reported as insufficient_evidence (not decoded) for 0x3b itself, with the full related struct given in shared_infrastructure_found since it is independently useful to whoever is decoding the 0x80-0x9f mission range. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3C — RC Lost Action Get

_Not decoded._ Same search and same lead as 0x3b (RC Lost Action Set) -- the 'action_when_rc_lost' 1-byte-enum field found live in dji_flight's Waypoint Mission Init Info struct (offset 19) is the strongest related evidence found, but it belongs to a different (mission-init) command, not a disassembled parser for 0x3c itself. See 0x3b's scenario_description and shared_infrastructure_found for the full struct. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3D — Time Zone Set

_Not decoded._ No handler for cmd_set 0x03/0x3d was found in dji_flight (absent from its dispatch table; it has no duss_event_register_dynamic_command import) or in dji_sys's 11 literal registration call sites. A promising-looking lead turned out, on closer inspection, to most likely belong to a DIFFERENT, already-decoded command rather than to 0x3d: dji_sys's .rodata contains the Android property name 'persist.sys.timezone_minutes' and an adjacent format string '%s: utc min offset :%d', but these sit in the exact same small .rodata cluster as '%s: wrong 0x4A cmd len %d from 0x%x!' and 'Got %d %d sys_event_set_date message: ...' -- i.e. this string neighborhood belongs to dji_sys's sys_event_set_date function, which this project already has catalogued as the handler for cmd_set 0x00/cmd_id 0x4A ('Set Date/Time', doc 21). This strongly suggests the UTC-minute-offset/timezone-property side effect is a field INSIDE the already-decoded 0x00/0x4A payload (a combined date+time+UTC-offset sync message), not a separately wired cmd_set 0x03/0x3d handler -- i.e. 'Time Zone Set' under cmd_set 0x03 may simply not be implemented on this firmware generation, with 0x00/0x4A's existing decode potentially missing a utc_offset field it should have. I was not able to directly xref the exact instruction(s) loading these two particular strings (the literal-pool ldr+add-pc pattern that worked for every other string in this report did not resolve for 'persist.sys.timezone_minutes' specifically, suggesting a different addressing idiom in that part of dji_sys), so this remains a strings-proximity inference, not a fully confirmed function identity -- reported honestly as such. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3E — FlyC Request Limit Update

Payload decoder: `flyc_flyc_request_limit_update_dissector`

## 0x3F — Set NoFly Zone Data

Payload decoder: `flyc_set_nofly_zone_data_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_set_nofly_zone_data_num_entries` (Number of entries) | uint8 | Amount of entries transfeered it this packet; value of 0 means end of transfer. |
  | 1 | 1 | `flyc_set_nofly_zone_data_frag_num` (Transfer fragment index) | uint8 | Fragment index |
  | 2 | 3 | `flyc_set_nofly_zone_data_reserved2` (Reserved2) | uint8 | Should be zeros |
  | 5 | 4 | `flyc_nofly_zone_entry_latitude` (Latitude) | int32\* | angular value * 1000000 |
  | 9 | 4 | `flyc_nofly_zone_entry_longitude` (Longitude) | int32\* | angular value * 1000000 |
  | 13 | 2 | `flyc_nofly_zone_entry_radius` (Radius) | uint16\* | meters |
  | 15 | 2 | `flyc_nofly_zone_entry_contry_code` (Contry Code) | uint16\* |  |
  | 17 | 1 | `flyc_nofly_zone_entry_type` (Type) | uint8 |  |
  | 18 | 4 | `flyc_nofly_zone_entry_id` (Id) | uint32\* |  |

  \* The source dissector (`dji-dumlv1-flyc.lua` lines 380-385) declares all
  five of these as `ProtoField.uint8()` regardless of their actual
  `Size` above — harmless for Wireshark's hex display, but wrong for an
  encoder/decoder that needs the real numeric value. Corrected here in
  `commands.json`/`registry_data.cpp` (not in `duml_lua_db.json`, which stays
  a faithful mirror of the upstream source) and verified against the
  `FlycNoFlyZone` C struct (`c_int` lat/lon) that `dji_flyc_nofly_ed.py`
  reads from raw flight-controller firmware on earlier DJI generations —
  same field shapes, independently corroborated. See
  `02_WM265_MAVIC3_NFZ_FINDINGS.md` and the `test_set_nofly_zone_data_roundtrip`
  / `SetNoFlyZoneDataRoundTrip` regression tests.

## 0x41 — Upload Unlimit Areas

_Not decoded._ No handler found. Architecturally, 'Upload Unlimit Areas' sits in the same 0x3f/0x41/0x42/0x47 'fly-zone override' command family as the already-fully-decoded 0x3f ('Set NoFly Zone Data', 10 fields: num_entries/frag_num/reserved/lat/lon/radius/country_code/type/id, see cmdset_03_Flight_Control.md) -- by the task's own hint and by naming/domain analogy it is plausible 0x41 follows the same chunked-fragment-header + per-entry-struct convention, but I found zero command-specific disassembled evidence for it, so I am not proposing an offset table (that would be inventing a layout, which the project's rules explicitly forbid). I did examine the dji_flight dispatch-table row that DOES exist for cmd_set 0x03/cmd_id 0x3f (vaddr 0xae090, fn 0x10eb4) directly, since it's the closest real, disassembled sibling: its body memsets a buffer, calls a validation helper (0x172a8), and on a null-request short-circuits to copying a FIXED 60-byte canned buffer into the output with a hardcoded return code (0x3d) -- i.e. this looks like a test/stub placeholder rather than dji_flight's real production NoFly-Zone parser (the actual decoded 0x3f field layout in this project's registry traces to the Lua dissector / doc 02_WM265_MAVIC3_NFZ_FINDINGS.md, a different source, not this dji_flight function). This is a useful caution (flagged in shared_infrastructure_found) but doesn't help pin 0x41's layout. No 'unlimit'/'nlimit'/'limit_area' strings were found in dji_flight at all; dji_flight does contain real NFZ-database SQL strings ('SELECT ... FROM airmap_geofence_polygons WHERE area_id=... sub_area_id=...', columns area_id/points/country/lat/lng/radius/shape/sub_area_id/height/area_level/elevation) but these are the already-documented (docs 02/06) SQLite geofence-polygon DB schema, not evidence of cmd 0x41's wire format, and 'Unlimit Areas' (authorized-override zones) are conceptually distinct from the NFZ polygon DB in DJI's real product line. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x42 — FlyC Unlimit State / UAV Posture

Payload decoder: `flyc_flyc_unlimit_state_dissector`

  *if (payload:len() >= 35) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_uav_posture_param0` (Param0) | float | Sum of squares of params 0..3 must give 1.0 for the values to be accepted |
  | 4 | 4 | `flyc_uav_posture_param1` (Param1) | float |  |
  | 8 | 4 | `flyc_uav_posture_param2` (Param2) | float |  |
  | 12 | 4 | `flyc_uav_posture_param3` (Param3) | float |  |
  | 16 | 4 | `flyc_uav_posture_param4` (Param4) | float |  |
  | 20 | 4 | `flyc_uav_posture_param5` (Param5) | float |  |
  | 24 | 4 | `flyc_uav_posture_param6` (Param6) | float |  |
  | 28 | 4 | `flyc_uav_posture_param7` (Param7) | float |  |
  | 32 | 1 | `flyc_uav_posture_has8` (Has8-unknown) | uint8 |  |
  | 33 | 2 | `flyc_uav_posture_unkn21` (Unknown21) | uint16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_unlimit_state_is_in_unlimit_area` (Is In Unlimit Area) | uint8 |  |
  | 1 | 1 | `flyc_flyc_unlimit_state_unlimit_areas_action` (Unlimit Areas Action) | uint8 |  |
  | 2 | 1 | `flyc_flyc_unlimit_state_unlimit_areas_size` (Unlimit Areas Size) | uint8 |  |
  | 3 | 1 | `flyc_flyc_unlimit_state_unlimit_areas_enabled` (Unlimit Areas Enabled) | uint8 |  |

## 0x43 — OSD General Data Get

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

## 0x44 — OSD Home Point Get

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

## 0x45 — FlyC GPS SNR Get

Payload decoder: `flyc_flyc_gps_snr_dissector`

## 0x46 — FlyC GPS SNR Set

_Not decoded._ App/SDK would send this to set a GPS-SNR acceptance threshold; dji_flight receives it generically through the above path. No command-specific field boundary could be established within the generic handler's logic. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x47 — Enable Unlimit Areas

_Not decoded._ Likely a simple on/off toggle for the 'unlimit areas' (GPS no-fly override zones uploaded via 0x41) feature; routed through dji_flight's generic FlyC parameter-write path with no command-specific parsing found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x49 — Push Encrypted Package

_Not decoded._ An opaque encrypted blob forwarded through dji_flight's generic internal param/observer path to whichever subscribed consumer actually decrypts it; no architecture-level byte fields identified and none attempted for the encrypted content itself (out of scope per task boundaries). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4A — Push Att IMU Info

_Not decoded._ Telemetry push (attitude + IMU status) into dji_flight's internal state, generically dispatched; no command-specific struct fields identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4B — Push RC Stick Value

_Not decoded._ Likely RC stick-position telemetry pushed into dji_flight; a plausible analogy to the already-confirmed cmd_set 6/0x26 4x int16 AETR struct exists but was not independently confirmed for this specific cmd_id/cmd_set pairing. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x4C — Push Fussed Pos Speed Data

_Not decoded._ Fused position/speed estimate pushed into dji_flight's internal state; plausible analogy to already-decoded 0x57/0x43 position/speed fields, not independently confirmed for this cmd_id. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x50 — Imu Data Status

Payload decoder: `flyc_imu_data_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_imu_data_status_start_fan` (Start Fan) | uint8 | On P3 |
  | 1 | 1 | `flyc_imu_data_status_led_status` (Led Status) | uint8 | On P3 |

## 0x51 — FlyC Battery Status Get

Payload decoder: `flyc_flyc_battery_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_flyc_battery_status_useful_time` (Useful Time) | uint16 |  |
  | 2 | 2 | `flyc_flyc_battery_status_go_home_time` (Go Home Time) | uint16 |  |
  | 4 | 2 | `flyc_flyc_battery_status_land_time` (Land Time) | uint16 |  |
  | 6 | 2 | `flyc_flyc_battery_status_go_home_battery` (Go Home Battery) | uint16 |  |
  | 8 | 2 | `flyc_flyc_battery_status_land_battery` (Land Battery) | uint16 |  |
  | 10 | 4 | `flyc_flyc_battery_status_safe_fly_radius` (Safe Fly Radius) | float |  |
  | 14 | 4 | `flyc_flyc_battery_status_volume_comsume` (Volume Comsume) | float |  |
  | 18 | 4 | `flyc_flyc_battery_status_status` (Status) | uint32 |  |
  | 22 | 1 | `flyc_flyc_battery_status_go_home_status` (Go Home Status) | uint8 | enum:`enums.FLYC_SMART_BATTERY_GO_HOME_STATUS_SMART_GO_HOME_STATUS_ENUM` |
  | 23 | 1 | `flyc_flyc_battery_status_go_home_count_down` (Go Home Count Down) | uint8 |  |
  | 24 | 2 | `flyc_flyc_battery_status_voltage` (Voltage) | uint16 |  |
  | 26 | 1 | `flyc_flyc_battery_status_battery_percent` (Battery Percent) | uint8 |  |
  | 27 | 1 | `flyc_flyc_battery_status_masked1b` (Masked1B) | uint8 |  |
  | 27 | 1 | `flyc_flyc_battery_status_low_warning` (Low Warning) | uint8 | mask:`0x7f` |
  | 27 | 1 | `flyc_flyc_battery_status_low_warning_go_home` (Low Warning Go Home) | uint8 | mask:`0x80` |
  | 28 | 1 | `flyc_flyc_battery_status_masked1c` (Masked1C) | uint8 |  |
  | 28 | 1 | `flyc_flyc_battery_status_serious_low_warning` (Serious Low Warning) | uint8 | mask:`0x7f` |
  | 28 | 1 | `flyc_flyc_battery_status_serious_low_warning_landing` (Serious Low Warning Landing) | uint8 | mask:`0x80` |
  | 29 | 1 | `flyc_flyc_battery_status_voltage_percent` (Voltage Percent) | uint8 |  |

## 0x52 — Smart Low Battery Actn Set

_Not decoded._ Sets which automatic action (go-home vs. land) the FC takes on low/critically-low battery; plausibly a single enum byte matching the already-decoded FLYC_SMART_BATTERY_GO_HOME_STATUS enum from sibling command 0x51, but not independently confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x53 — FlyC Vis Avoidance Param Get

Payload decoder: `flyc_flyc_vis_avoid_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_flyc_vis_avoid_param_masked00` (Masked00) | uint16 |  |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_obstacle_enable` (Avoid Obstacle Enable) | uint16 | mask:`0x01` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_user_avoid_enable` (User Avoid Enable) | uint16 | mask:`0x02` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_get_avoid_obstacle_work_flag` (Get Avoid Obstacle Work Flag) | uint16 | mask:`0x04` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_get_emergency_brake_work_flag` (Get Emergency Brake Work Flag) | uint16 | mask:`0x08` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_gohome_avoid_enable` (Gohome Avoid Enable) | uint16 | mask:`0x10` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_ground_force_landing` (Avoid Ground Force Landing) | uint16 | mask:`0x20` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_radius_limit_working` (Radius Limit Working) | uint16 | mask:`0x40` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_airport_limit_working` (Airport Limit Working) | uint16 | mask:`0x80` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_obstacle_working` (Avoid Obstacle Working) | uint16 | mask:`0x100` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_horiz_near_boundary` (Horiz Near Boundary) | uint16 | mask:`0x200` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_avoid_overshot_act` (Avoid Overshot Act) | uint16 | mask:`0x400` |
  | 0 | 2 | `flyc_flyc_vis_avoid_param_vert_low_limit_work_flag` (Vert Low Limit Work Flag) | uint16 | mask:`0x800` |

## 0x55 — FlyC Limit State Get

Payload decoder: `flyc_flyc_limit_state_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `flyc_flyc_limit_state_latitude` (Latitude) | double |  |
  | 8 | 8 | `flyc_flyc_limit_state_longitude` (Longitude) | double |  |
  | 16 | 2 | `flyc_flyc_limit_state_inner_radius` (Inner Radius) | uint16 |  |
  | 18 | 2 | `flyc_flyc_limit_state_outer_radius` (Outer Radius) | uint16 |  |
  | 20 | 1 | `flyc_flyc_limit_state_type` (Type) | uint8 |  |
  | 21 | 1 | `flyc_flyc_limit_state_area_state` (Area State) | uint8 |  |
  | 22 | 1 | `flyc_flyc_limit_state_action_state` (Action State) | uint8 |  |
  | 23 | 1 | `flyc_flyc_limit_state_enable` (Enable) | uint8 |  |

## 0x56 — FlyC LED Status Get

Payload decoder: `flyc_flyc_led_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_led_status_led_reason` (Led Reason) | uint32 | enum:`enums.FLYC_LED_STATUS_LED_REASON_ENUM` |

## 0x57 — GPS GLNS Info

Payload decoder: `flyc_gps_glns_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_gps_glns_gps_lon` (Gps Lon) | int32 |  |
  | 4 | 4 | `flyc_gps_glns_gps_lat` (Gps Lat) | int32 |  |
  | 8 | 4 | `flyc_gps_glns_hmsl` (Hmsl) | int32 |  |
  | 12 | 4 | `flyc_gps_glns_vel_n` (Vel N) | float |  |
  | 16 | 4 | `flyc_gps_glns_vel_e` (Vel E) | float |  |
  | 20 | 4 | `flyc_gps_glns_vel_d` (Vel D) | float |  |
  | 24 | 4 | `flyc_gps_glns_hdop` (Hdop) | float |  |
  | 28 | 2 | `flyc_gps_glns_numsv` (NumSV) | uint16 | Number of Global Nav System positioning satellites |
  | 30 | 2 | `flyc_gps_glns_gpsglns_cnt` (Gps Glns Count) | uint16 | Sequence counter increased each time the packet of this type is prepared |
  | 32 | 1 | `flyc_gps_glns_unkn20` (Unknown 20) | uint8 |  |
  | 33 | 1 | `flyc_gps_glns_homepoint_set` (Homepoint Set) | uint8 |  |

## 0x58 — Push Att Stick Speed Pos Data

_Not decoded._ Likely a combined attitude/stick/speed/position snapshot; dji_flight's handler for the inbound command validates internal entity state and emits a status response without reading request payload bytes, consistent with a bare query/trigger rather than a value-carrying request -- the actual telemetry field layout remains unresolved. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x59 — Push Sdk Data

_Not decoded._ Opaque SDK-defined data channel; genuinely no fixed FlyC-side field layout to recover, consistent with the generic internal handling found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x5A — Push FC Data

_Not decoded._ Generic flight-controller data push; no command-specific field layout found, routed through the same generic internal param/observer mechanism as most of this batch. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x60 — SVO API Transfer

_Not decoded._ No handler located by any of this project's five documented DUML registration mechanisms. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x61 — FlyC Activation Info

Payload decoder: `flyc_flyc_active_request_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_active_request_app_id` (App Id) | uint32 |  |
  | 4 | 4 | `flyc_flyc_active_request_app_level` (App Level) | uint32 |  |
  | 8 | 4 | `flyc_flyc_active_request_app_version` (App Version) | uint32 |  |

## 0x62 — FlyC Activation Exec

_Not decoded._ Architecturally located in the activation subsystem's known-but-untraced 'outer command to inner forwarding hop' gap; stayed at architecture level per this task's boundary. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x63 — FlyC On Board Recv

Payload decoder: `flyc_flyc_board_recv_dissector`

## 0x64 — Send On Board Set

_Not decoded._ Same plausible 'Onboard SDK' family as 0x63, no dissector stub at all. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x67 — FlyC Power Param Get

Payload decoder: `flyc_flyc_power_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_power_param_esc_average_speed` (Esc Average Speed) | float |  |
  | 4 | 4 | `flyc_flyc_power_param_lift` (Lift) | float |  |

## 0x69 — RTK Switch

_Not decoded._ No RTK-specific daemon, library, or handler found anywhere in either firmware extraction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6A — FlyC Avoid

Payload decoder: `flyc_flyc_avoid_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_avoid_masked00` (Masked00) | uint8 |  |
  | 0 | 1 | `flyc_flyc_avoid_visual_sensor_enable` (Visual Sensor Enable) | uint8 | mask:`0x01` |
  | 0 | 1 | `flyc_flyc_avoid_visual_sensor_work` (Visual Sensor Work) | uint8 | mask:`0x02` |
  | 0 | 1 | `flyc_flyc_avoid_in_stop` (In Stop) | uint8 | mask:`0x04` |

## 0x6B — Recorder Data Cfg

_Not decoded._ No matching handler; nearby 'recorder' symbols found are unrelated SSD/video recording, not flight-data recording. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6C — FlyC RTK Location Data Get

Payload decoder: `flyc_flyc_rtk_location_data_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 8 | `flyc_flyc_rtk_location_data_longitude` (Longitude) | double |  |
  | 8 | 8 | `flyc_flyc_rtk_location_data_latitude` (Latitude) | double |  |
  | 16 | 4 | `flyc_flyc_rtk_location_data_height` (Height) | float |  |
  | 20 | 2 | `flyc_flyc_rtk_location_data_heading` (Heading) | uint16 |  |
  | 22 | 1 | `flyc_flyc_rtk_location_data_rtk_connected` (Rtk Connected) | uint8 |  |
  | 23 | 1 | `flyc_flyc_rtk_location_data_rtk_canbe_used` (Rtk Can be Used) | uint8 |  |

  *if (payload:len() >= offset + 8) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 24 | 4 | `flyc_flyc_rtk_location_data_unknown18` (Unknown18) | uint32 |  |
  | 28 | 4 | `flyc_flyc_rtk_location_data_unknown1C` (Unknown1C) | uint32 |  |

## 0x6D — Upload Hotpoint

_Not decoded._ Candidate mission daemons (dji_navigation, dji_autoflight) checked per task hint; both fully stripped with no usable lead, two lookalike tables found and explicitly ruled out. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x6E — Download Hotpoint

_Not decoded._ Same investigation and same result as 0x6d (its upload counterpart) -- see that entry for full detail. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x70 — Set Product SN

_Not decoded._ A concrete, newly-found storage-location lead (factory_data partition) could not be tied to a DUML handler in the time available. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x71 — Get Product SN

_Not decoded._ Same lead and same result as 0x70 (its Set counterpart) -- see that entry for full detail. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x72 — Reset Product SN

_Not decoded._ No daemon in the e1e (32-bit ARM) extraction registers a DUML handler for cmd_set 0x03/0x72 via any of the 5 known mechanisms. Checked: dji_flight (readelf -sW shows zero imports of any product_sn/board_sn/chip_sn/eeprom-named function, and `strings` has no product_sn/product_id/eeprom hit anywhere in the binary); dji_sys (same, clean); dji_amt and dji_sec (both import only a generic `dev_info_get_product_sn` wrapper, used for their own activation/account-binding purposes, with no DUML registration call site found tying it to cmd_id 0x72); dji_wlm and dji_sdrs_agent (both call `get_product_sn`, exported from libduml_util.so, again for their own internal purposes -- dji_wlm is the master/slave-RC role daemon, dji_sdrs_agent is the SDR/radio-link daemon, neither is cmd_set-0x03-adjacent by name); libduml_util.so itself (exports get_product_sn/get_board_sn/get_chip_sn as generic utility functions with no cmd_set/cmd_id binding of their own -- dji_flight does not even link against these); eeprom_rw (a factory-calibration CLI test tool for CAMERA lens EEPROM specifically -- source path `hardware/dji/common/camera/lib_fcali/eagle1/...`, not flight-controller EEPROM, and not a DUML daemon at all, no duss_event_* imports). Concrete unresolved lead, consistent with this project's prior finding for cmd_set 0x01's hardware-adjacent SDK-ctrl commands (doc 21): the 4.5MB opaque blob `rtos_dec_RTOS.bin` (confirmed present in this firmware extraction at /home/user/wm260_fw/decrypted/e1e_extracted/rtos_dec_RTOS.bin, alongside `rtos.img` and the Android-side bridge library `librtos.so` -- which dji_flight does NOT link against, ruling out that specific bridge) is the most likely place 'Reset Product SN' actually lives, i.e. on the flight-controller's own RTOS MCU firmware rather than any Android-side daemon this extraction covers. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x73 — Set Product Id

_Not decoded._ Same exhaustive negative check as 0x72 (dji_flight, dji_sys, dji_amt, dji_sec, dji_wlm, dji_sdrs_agent, libduml_util.so, eeprom_rw -- see 0x72's note). Additionally checked specifically for a 'product_id'-named handler: the only 'product_id' string anywhere in the extracted tree is inside dji_perception, and it is a field name of an embedded ROS-style self-describing message schema (`dji_flightsystem_msgs`) used by dji_perception's black-box telemetry logging subsystem -- doc 04 already established (and this pass re-confirmed by checking dji_perception imports no duss_event_register_dynamic_command-family symbol at all) that these schema strings are never referenced by any instruction in dji_perception's .text, i.e. dead/unused cruft, not live DUML code. Same RTOS-blob lead as 0x72 applies. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x74 — Get Product Id

_Not decoded._ Identical negative result and identical checks as 0x73 (this is the read-side counterpart of the same product-id mechanism; no separate handler or string distinguishing a 'get' path from the 'set' path was found anywhere either). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x75 — Write EEPROM FC0

_Not decoded._ No function or debug string anywhere in the e1e extraction names 'EEPROM' together with 'FC0' or any flight-controller-board context. Checked dji_flight and dji_sys directly (grep for 'eeprom'/'fc0', case-insensitive, both clean). Checked `eeprom_rw` and `dji_autotest` specifically since both are factory/production-line tools that plausibly write identity data at manufacturing time: `eeprom_rw`'s ~30 eeprom_fcali_* exported functions and strings (read/write serial_num, pcba_sn, intri_param, calib_date, calib_finished_flag, etc.) are all under the `lib_fcali/eagle1` camera-lens-calibration namespace, not a flight-controller board; `dji_autotest` has exactly one hit, the string 'eeprom_rw read intri_param %s' (a log line referencing the same camera-calib tool by name), nothing FC-board-specific. Given 'FC0' plausibly means 'Flight Controller board 0' and this is clearly a factory-programming command (writing a fresh board's EEPROM during manufacturing), the RTOS-blob lead from 0x72 applies with similar or greater plausibility here, since raw EEPROM read/write is exactly the kind of low-level hardware I/O that would live on the MCU side rather than the Android application processor. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x76 — Read EEPROM FC0

_Not decoded._ Identical negative result and identical checks as 0x75 (read-side counterpart of the same mechanism; no distinguishing read-specific string or function found either). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x80 — Navigation Mode Set

_Not decoded._ Checked dji_flight: no flight_mode/navi_mode/nav_mode/atti_mode/sport_mode/gps_mode/ctrl_mode string anywhere (grep clean); the only '[NAVI]'-prefixed strings present are an unrelated subsystem about 'accurate shot'/precision-landing heartbeat status (navi action parameters, accurate shot ack/timeout), not a flight-mode toggle. Checked dji_navigation directly: no navi_mode/navigation_mode/flight_mode string found either. Checked dji_autoflight: nothing. Both dji_navigation and dji_flight register generically via duss_mb_create_route_table + duss_event_create_client (mechanism #3, same opaque, non-literal binding described in the shared_infrastructure_found section) rather than literal duss_event_register_dynamic_command immediates, so the direct literal-immediate search method this task suggested cannot resolve this command on either candidate daemon. No table-driven dispatch array entry (the 43-row {fn_ptr,cmd_word} table in dji_flight, fully decoded -- see shared_infrastructure_found) contains cmd_id 0x80 under any cmd_set. No further candidate daemon identified. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x81 — Mission IOC: Set Lock Yaw

_Not decoded._ A real, specific, well-evidenced architectural lead was found but could not be converted into a confirmed byte-level decode within this pass. dji_navigation contains the live debug/log string 'PROTOCOL_V1: nav flight ioc %d enable %d send fail %d' (file offset/vaddr 0x1e0e80, confirmed present via `strings -a -t x`), which is direct proof dji_navigation implements IOC (Intelligent Orientation Control) logic and logs a 3-field event: an id/mode-type parameter, an enable flag, and a send-fail result code -- a strong semantic match for 'Mission IOC: Set Lock Yaw' (IOC lock-yaw is a specific IOC sub-mode: the aircraft's nose is locked to a fixed heading regardless of stick input). However: (1) the standard PC-relative ADR xref-scan technique (ldr rX,[pc,#N] followed by add rX,pc, resolved and cross-checked against every ldr-literal in the whole .text section, 696,335 Thumb instructions scanned) found zero instructions anywhere in dji_navigation's .text that resolve to this string's address, meaning it is referenced through some other addressing pattern (most likely a MOVW/MOVT absolute-address pair, or a pointer stored in a relocated .data table rather than inline PC-relative code) that this pass's scripted scan did not cover; (2) dji_navigation registers cmd_sets via the same opaque duss_mb_create_route_table + duss_event_create_client mechanism as dji_flight (two calls found, naming route tables 'navigation' and 'navigation_eagle' via literal PC-relative strings -- confirmed the 3rd argument to duss_mb_create_route_table is a name string, not a cmd_set array, correcting this investigation's own initial hypothesis), so even having found the log string's owning function would not by itself confirm a (cmd_set,cmd_id) binding the way a literal register_dynamic_command call site would. The lock_yaw enable/mode-id/result-code field shape implied by the format string is a genuine, concrete lead for whoever picks this up next, but byte offsets/sizes were not independently confirmed and are not reported. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x82 — Miss. WP: Upload Mission Info

_Not decoded._ dji_flight contains a real, fully disassembled 'WP2' (Waypoint Protocol v2) mission sub-architecture with semantically on-topic function names: api_wp2_waypoints_upload (vaddr 0x1acc6), api_wp2_waypoints_upload_handle (vaddr 0x1ab80, called directly from the former at 0x1ace6), and wp2_mission_init_flight (a function whose tail logs that name at vaddr ~0x1bac0, full entry not pinned). This looked initially like a strong match for 'Upload Mission Info'. However, cross-checking two OTHER WP2-family siblings against this investigation's own full, relocation-verified decode of dji_flight's 43-row {fn_ptr,cmd_word} dispatch table (see shared_infrastructure_found) proves, by exact stripped-Thumb-bit address match, that api_wp2_download_waypoint = cmd_set 0x22/cmd_id 0x0d and api_wp2_break_restore_waypoint_fly = cmd_set 0x22/cmd_id 0x44 -- i.e. the entire WP2 family is bound to cmd_set 0x22 ('Demo Mode'), not cmd_set 0x03. api_wp2_waypoints_upload itself is NOT one of the 43 table rows, and a whole-.text search found zero direct bl/blx callers of it anywhere -- it is reached only indirectly (most plausibly a C++ vtable slot, since dji_flight links libc++ and is dense with mangled STL symbols), which this pass could not resolve, so its own exact cmd_set/cmd_id binding is unconfirmed either way, but the pattern strongly suggests 0x22 rather than 0x03. A dedicated whole-binary relocation scan (all 1773 R_ARM_RELATIVE entries in dji_flight) for any {fn_ptr,cmd_word} pair encoding cmd_set=0x03 with cmd_id=0x82 found zero hits. No separate cmd_set-0x03-specific 'mission info upload' handler was found anywhere else. Important negative result to pass on: do not assume the WP2 api_wp2_* family answers cmd_set 0x03's 'Miss. WP' commands just because the names/purpose line up -- the evidence says they are two separate implementations under two different cmd_sets. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x83 — Miss. WP: Download Mission Info

_Not decoded._ Same WP2-family investigation as 0x82 applies. The closest name match, api_wp2_download_waypoint (vaddr 0x1ad24, debug strings 'app req waypoint info', 'download fail for not upload waypoint, waypoints num: %d', 'download fail for can't find start[%d]/end[%d]...'), is confirmed -- by exact address match against the relocation-backed 43-row dispatch table -- bound to cmd_set 0x22/cmd_id 0x0d, not cmd_set 0x03. Its request-handling code (traced one level up, in its caller) validates the incoming event struct's 16-bit length field equals exactly 4 bytes before proceeding, consistent with a 'download by range/index' request whose payload is a single small integer (plausibly a start index or 32-bit id) -- but since this function is cmd_set 0x22-bound, this field-shape observation cannot be reported as cmd_set 0x03/0x83's own layout. The same whole-binary relocation scan described in 0x82's note (targeting cmd_set=0x03/cmd_id=0x83 specifically) found zero hits. No separate cmd_set-0x03 download-mission-info handler was located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x84 — Upload Waypoint Info By Idx

_Not decoded._ Same WP2-family investigation as 0x82/0x83 applies. The closest semantic/behavioral match is api_wp2_waypoints_upload_handle (vaddr 0x1ab80, dji_flight): its disassembly shows it reads the event struct's data pointer and 16-bit length (struct offsets +0x8/+0xc) and feeds them to a generic field-parser helper that extracts a sequence of fixed-width sub-fields of sizes 0x10, 0x2, 0x5, and 0xc bytes in turn -- a shape generally consistent with a single structured waypoint record (header + small fields + a larger coordinate/parameter block) being uploaded by index, which is exactly what 'Upload Waypoint Info By Idx' sounds like. However this function is reached only via api_wp2_waypoints_upload (see 0x82's note), which itself could not be confirmed bound to cmd_set 0x03 rather than 0x22 -- and two of its direct siblings in the same WP2 family ARE confirmed bound to 0x22. Reporting the field-size sequence (0x10/0x2/0x5/0xc bytes) here would require first confirming the cmd_set binding, which this pass could not do, so no field layout is asserted. The same whole-binary relocation scan (cmd_set=0x03/cmd_id=0x84) found zero hits in the dispatch table. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x85 — Download Waypoint Info By Idx

_Not decoded._ dji_flight's ONLY DUML dispatch mechanism was re-derived and fully re-verified this pass: the relocated {u32 function_vaddr (R_ARM_RELATIVE); u8 cmd_set; u8 cmd_id; u16 reserved=0} array at vaddr 0xae038, 44 raw 8-byte rows through 0xae190 inclusive (ending exactly at the .data/.bss boundary 0xae198 - clean, not a scan artifact). Re-dumped byte-for-byte directly from the file (not via a disassembler) and cross-checked: cmd_sets present = {0x00,0x02,0x03,0x04,0x0a,0x11,0x1f,0x22}, matching this task's hint exactly. Of the 44 rows, only 5 have cmd_set=0x03: cmd_id 0x3f, 0xc1, 0xcd, 0xdb, 0xea - all NFZ/dynamic-update related (confirmed by disassembling the 0xea row's handler directly: it validates an action-item count against 0x10e and calls into the gs_mission_wp_action_* family, not a Download-Waypoint-Info type command). None is in the 0x80-0x9f range. I then name-matched three plausible candidates via their own embedded compiler debug-name strings and disassembled each: api_wp2_download_waypoint (vaddr 0x1ad24 - reads a 4-byte request {u16 start_wp_idx @0, u16 end_wp_idx @2}, length-checked via 'ldrh r5,[sb,0xc]; cmp r5,#4', validates start<=end and both within the recorded min/max index before building a ~0x10e-byte response of per-waypoint 0x2c-byte records), api_wp2_get_wp_index_in_list (0x1b44c), and api_wp2_download_wp_init_info (0x1b8c4). Checking each address against the 44-row table's own data shows all three are in fact registered there - but under cmd_set 0x22 ('Demo Mode'), not 0x03: api_wp2_download_waypoint = row 28 = (0x22,0x0d); api_wp2_get_wp_index_in_list = row 30 = (0x22,0x17); api_wp2_download_wp_init_info = row 27 = (0x22,0x09). This is a confirmed negative result, not a guess. dji_flight imports no duss_event_register_dynamic_command symbol at all (checked via nm -D; zero literal-immediate call sites are even possible), and there is exactly one call site to duss_mb_create_route_table in the whole binary (the function at 0x22b54, itself called once, from 0x23302), which registers precisely this one 44-row table. No other registration mechanism exists in dji_flight. dji_navigation and dji_autoflight were checked for the same import pattern (both import only duss_mb_create_route_table/duss_event_create_client, same as dji_flight, confirmed via nm -D) but neither has a recoverable static table of this kind (checked: no run of >=8 consecutive 8-byte-spaced R_ARM_RELATIVE relocations in either binary's full relocation list), so this method cannot locate a (0x03,0x85) binding there either within this pass's time budget. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x86 — Mission WP: Go/Stop

_Not decoded._ Same table check as 0x85: cmd_set 0x03 has only the 5 NFZ-related rows, none in 0x80-0x9f. The strongest name/behavior-matched candidate anywhere in dji_flight is api_wp2_go_cmd_handle (vaddr 0x1b664, reached through a thin wrapper at 0x1b830): its own embedded debug-name string is literally 'api_wp2_go_cmd_handle', and its log strings ('go_cmd not ack', 'go_cmd after solve is:%d', 'already running, ack_result 0x%x', 'already stopping, ack_result 0x%x', 'go_cmd fail for not initial 0x%x') explicitly describe Go/Stop semantics; it reads byte 0 of the event's payload pointer ([event+8]) as an action code, looks up/updates a state value, and branches on state==1 vs state==2 (consistent with 1=Go, 2=Stop), building a 4-byte ack buffer. This looked initially like a strong direct hit. However, cross-checking its wrapper's address (0x1b830, thumb-bit-set 0x1b831) against the same 44-row table used for 0x85 shows it is literally row 23 of that table, bound to (cmd_set=0x22, cmd_id=0x05) - not 0x03/0x86. (I initially mis-read this hit as a separate C++ RTTI/vtable reference because of nearby _ZTVN10__cxxabiv120__si_class_type_infoE relocations in the same page; re-checking showed that vtable-looking region ends at 0xad034, immediately before the table starts at 0xad038, and the two are unrelated - row 23 is simply part of the already-known table.) This is therefore a confirmed, refuted candidate, not an open lead: api_wp2_go_cmd_handle is real, live, wire-triggered code, but for a different wire command than the one in this batch. No function bound to (0x03,0x86) was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x87 — Mission WP: Pasue/Resume

_Not decoded._ Table check: no cmd_set-0x03 row in 0x80-0x9f (see 0x85/0x86 for the full table re-derivation). Exhaustive case-insensitive string search of dji_flight for 'pause'/'resume' turned up exactly three hits: api_wp2_pause_recovery (row 26 of the table, confirmed (cmd_set=0x22, cmd_id=0x08) - already known from this project's doc 04/21, independently re-confirmed this pass at the exact byte level), and two unrelated ESC/actuator diagnostic log lines ('[ACT] Handle Actuator %d Main Index %d Sub Index %d PAUSE/RESUME for Action %d') that are motor-actuator test logging, not a Mission-WP ack handler. No second, distinct 'pause/resume' function exists anywhere in dji_flight's .rodata/.text that could plausibly be bound to a different cmd_id. No candidate for (0x03,0x87) found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x88 — Push Navigation Status Info

Payload decoder: `flyc_flyc_way_point_mission_info_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_way_point_mission_info_mission_type` (Mission Type) | uint8 | enum:`enums.FLYC_WAY_POINT_MISSION_INFO_MISSION_TYPE_ENUM` |

  *if (mission_type == 0x01) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_target_way_point` (Target Way Point) | uint8 |  |
  | 2 | 2 | `flyc_flyc_way_point_mission_info_limited_height` (Limited Height) | uint16 |  |
  | 4 | 1 | `flyc_flyc_way_point_mission_info_running_status` (Way Point Running Status) | uint8 | enum:`enums.FLYC_WAY_POINT_MISSION_INFO_RUNNING_STATUS_ENUM` |
  | 5 | 1 | `flyc_flyc_way_point_mission_info_wp_unknown5` (Way Point Unknown5) | uint8 |  |

  *elseif (mission_type == 0x02) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_hot_point_mission_status` (Hot Point Mission Status) | uint8 |  |
  | 2 | 2 | `flyc_flyc_way_point_mission_info_hot_point_radius` (Hot Point Radius) | uint16 |  |
  | 4 | 1 | `flyc_flyc_way_point_mission_info_hot_point_reason` (Hot Point Reason) | uint8 |  |
  | 5 | 1 | `flyc_flyc_way_point_mission_info_hot_point_speed` (Hot Point Speed) | uint8 |  |

  *elseif (mission_type == 0x03) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_follow_me_flags` (Follow Me Flags) | uint8 |  |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_follow_me_status` (Follow Me Status) | uint8 | mask:`0x0f` |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_follow_me_gps_level` (Follow Me Gps Level) | uint8 | mask:`0xf0` |
  | 2 | 2 | `flyc_flyc_way_point_mission_info_follow_me_distance` (Follow Me Distance) | uint16 |  |
  | 4 | 1 | `flyc_flyc_way_point_mission_info_follow_me_reason` (Follow Me Reason) | uint8 |  |
  | 5 | 1 | `flyc_flyc_way_point_mission_info_follow_me_unknown6` (Follow Me Unknown6) | uint8 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_info_mission_flags` (Mission Flags) | uint8 |  |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_mission_status` (Mission Status) | uint8 | mask:`0x03` |
  | 1 | 1 | `flyc_flyc_way_point_mission_info_position_valid` (Position Valid) | uint8 | mask:`0x04` |
  | 2 | 1 | `flyc_flyc_way_point_mission_info_current_status` (Current Status) | uint8 |  |
  | 3 | 1 | `flyc_flyc_way_point_mission_info_error_notification` (Error Notification) | uint8 |  |
  | 4 | 2 | `flyc_flyc_way_point_mission_info_current_height` (Current Height) | uint16 |  |

## 0x89 — Push Navigation Event Info

Payload decoder: `flyc_flyc_way_point_mission_current_event_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_way_point_mission_current_event_event_type` (Event Type) | uint8 | enum:`enums.FLYC_WAY_POINT_MISSION_CURRENT_EVENT_EVENT_TYPE_ENUM` |

  *if (event_type == 0x02) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_current_event_reach_incident_way_point_index` (Reach Incident Way Point Index) | uint8 | mask:`0xff` |
  | 2 | 1 | `flyc_flyc_way_point_mission_current_event_reach_incident_current_status` (Reach Incident Current Status) | uint8 | mask:`0xff` |
  | 3 | 1 | `flyc_flyc_way_point_mission_current_event_reach_incident_reserved` (Reach Incident Reserved) | uint8 | mask:`0xff` |

  *elseif (event_type == 0x03) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_current_event_upload_incident_is_valid` (Upload Incident Is Valid) | uint8 | mask:`0xff` |
  | 2 | 2 | `flyc_flyc_way_point_mission_current_event_upload_incident_estimated_time` (Upload Incident Estimated Time) | uint16 | mask:`0xffff` |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 1 | `flyc_flyc_way_point_mission_current_event_finish_incident_is_repeat` (Finish Incident Is Repeat) | uint8 |  |
  | 2 | 2 | `flyc_flyc_way_point_mission_current_event_finish_incident_resrved` (Finish Incident Resrved) | uint16 |  |

## 0x8A — Miss. HotPoint: Start With Info

_Not decoded._ No string containing 'hotpoint', 'hot_point', 'hot point', or 'poi' (point-of-interest, DJI's internal term for HotPoint) exists anywhere in dji_flight's .rodata (exhaustive case-insensitive strings grep) - and dji_flight's one static dispatch table (see 0x85) has no row that could plausibly be it either. The functionality clearly exists, but in a different daemon: dji_navigation (2.2MB, far larger than dji_flight/dji_autoflight; e1e-only, no e2/64-bit build at all for any of these three daemons) contains a function poi_interface_set_gps_circle_hot_point and roughly 80 'poi_*' blackbox-telemetry field-name strings (poi_radius, poi_target_id, poi_cnt_px/py/pz, poi_app_init_box_time/cx/cy/w/h, poi_cmd_velo_x/y/z, ...) that describe exactly the center-point/radius/target-id/initial-box fields a 'HotPoint Start With Info' payload would plausibly carry - a strong architectural lead, not a byte-level decode. dji_navigation imports only duss_mb_create_route_table/duss_event_create_client (same convention as dji_flight, confirmed via nm -D; no duss_event_register_dynamic_command import at all), but unlike dji_flight it has no recoverable static {fn_ptr,cmd_word} table: its full relocation list contains no run of >=8 consecutive 8-byte-spaced R_ARM_RELATIVE entries anywhere. Its one located duss_mb_create_route_table call site (fcn @ 0x55080, two calls, at 0x550e2 and 0x550fe) passes what resolve (via PC-relative literal-pool decoding) to route/client NAME strings ('navigation', 'navigation_eagle', '/system/etc/dji.json') plus a zeroed on-stack buffer as arguments - not a static data array - meaning any real per-command table is assembled at runtime in a way this pass's static tools could not recover from a 2.2MB stripped binary in the time available. A concrete, bounded lead for a future pass focused specifically on dji_navigation, not a resolved finding. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x8B — Miss. HotPoint: Cancel

_Not decoded._ Same search and same result as 0x8a: no hotpoint/poi evidence in dji_flight at all; dji_navigation's poi_interface_set_gps_circle_hot_point and poi_* telemetry schema are the only architectural lead, and dji_navigation's registration mechanism could not be statically recovered within this pass (no static dispatch table found; see 0x8a for the full detail, which applies identically here since Start/Cancel/Pause-Resume would plausibly share the same POI module and registration path). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x8C — Miss. HotPoint: Pasue/Resume

_Not decoded._ Same search and same result as 0x8a/0x8b: no hotpoint/poi evidence in dji_flight; dji_navigation's poi_interface_set_gps_circle_hot_point module is the only lead, registration mechanism unresolved within this pass's time budget. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x8D — App Set API Sub Mode

_Not decoded._ Searched all three daemons' strings for 'api_sub_mode', 'sub_mode', 'sdk_mode', 'ctrl_mode', 'rc_mode', 'api_mode'. The only near-match is an identical diagnostic string present in BOTH dji_navigation and dji_autoflight: '[nav-test 0x94] sub_mode %d, count %d, index %d' - but the '0x94' embedded in that literal string is a different, unrelated nav-test harness command number (not this task's cmd_id 0x8d), and the '[nav-test]' prefix marks it as a self-test/diagnostic log line, not a wire-command handler identifying itself. dji_flight's two 'ctrl_data' related strings found (E_api_user_ctrl_data_health, E_api_app_ctrl_data_health) are OSD/telemetry status-bit expression labels for a generic flight-status decoder, not a request handler. No function bound to (0x03,0x8d) found in any of the three binaries, and dji_flight's 44-row table (the only one of the three with a statically recoverable dispatch table) has no row for it. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x8E — App Joystick Data

_Not decoded._ Searched all three daemons' strings for 'joystick', 'stick', 'virtual_rc', 'virtual_stick', 'ctrl_data', 'app_cmd'. No wire-handler string of any kind was found (the only 'ctrl_data'-adjacent hits, in dji_flight, are the two OSD status-bit labels noted under 0x8d, unrelated to a request parser). dji_flight's 44-row table has no cmd_set-0x03 row in range, and dji_flight imports no duss_event_register_dynamic_command symbol at all. This negative result is architecturally consistent with App Joystick Data being a very high-rate (tens-of-Hz) control stream, the same category as this project's prior-wave cmd_set 0x06 finding for '0x26 RC AETR Value Push', which also had zero discoverable debug/log strings at its actual wire parser (hot-path code compiled without the logging calls this project's string-based identification method relies on). No candidate function found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x8F — Noe Mission pasue/resume

_Not decoded._ Read as 'New Mission Pause/Resume' (matches this batch's other 'Pasue' typo in 0x87/0x8c, likely a source-CSV typo of 'Now'/'New'). No candidate function or distinguishing string found in dji_flight beyond the already-eliminated api_wp2_pause_recovery (confirmed bound to cmd_set 0x22/cmd_id 0x08, not 0x03 - see 0x87). dji_navigation and dji_autoflight were confirmed to import only duss_mb_create_route_table/duss_event_create_client (no duss_event_register_dynamic_command, no static dispatch table in either, per the relocation-run check described under 0x8a), but were not individually disassembled for a 'new mission pause/resume'-specific string within this pass's time budget beyond the general term searches performed for 0x87/0x8a/0x8d. No function bound to (0x03,0x8f) found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x90 — Miss. Follow: Start With Info

_Not decoded._ No 'follow'/'followme'/'follow_me' wire-handler string exists in dji_flight, and its 44-row table has no cmd_set-0x03 row in 0x80-0x9f. dji_navigation contains an extensive, clearly-related state machine: strings 'TK state transite to TRACKING_MISSION_INITING/_STANDBY/_WAIT_FOR_SELECT...' (target-pose/lost-timeout/user-interrupt transitions), 'reset_planning_and_waypoint_follow_info', and 'check_permission_before/during/for_exit_during_pano_shot' - architecturally exactly what a Follow-Me/ActiveTrack 'Start With Info' mission would drive (an initial target designation starting a tracking state machine). Same limitation as the HotPoint commands (0x8a-0x8c): dji_navigation's actual DUML registration mechanism could not be statically recovered within this pass's time budget - no static {fn_ptr,cmd_word} table was found in its relocations (unlike dji_flight), and its one located duss_mb_create_route_table call site passes name strings and a runtime stack buffer rather than a static array (full detail under 0x8a). A concrete, bounded lead, not a resolved finding. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x91 — Miss. Follow: Cancel

_Not decoded._ One-way-vs-request/response status unknown; architecture suggests this would be an ack-only aircraft-side state transition (cancel active follow mission) if it exists on this firmware build at all. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x92 — Miss. Follow: Pasue/Resume

_Not decoded._ Likely a single enum/boolean 'pause vs resume' selector byte if it follows the pattern of other DJI toggle commands, but this is an architectural guess, not evidence-backed -- not asserted as a layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x93 — Miss. Follow: Get Target Info

_Not decoded._ Request/response shape (query a current follow target's info) is plausible by name alone; no fields recoverable. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x94 — Mission Noe: Start

_Not decoded._ Plausibly a thin wrapper (mission-type enum + maybe an id) given the 'generic mission node' naming, but not evidenced at byte level. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x95 — Mission Noe: Stop

_Not decoded._ Likely ack-only stop of whatever generic mission-node state 0x94 started; not evidenced at byte level. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x96 — Mission HotPoint: Download

_Not decoded._ By name, likely a chunked/length-prefixed read-back of previously-set hotpoint parameters (lat/lon/radius/altitude/direction), by analogy to the project's already-decoded 'FileTrans General Trans' and wp2 waypoint-download shapes, but no byte evidence was found to support this -- flagged as an inference, not a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x97 — Mission IOC: Start

_Not decoded._ Likely request/ack with a small enable/mode byte if the wire command exists as a genuine toggle, but unconfirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x98 — Mission IOC: Stop

_Not decoded._ Likely ack-only stop/disable of whatever 0x97 started; unconfirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x99 — Miss. HotPoint: Set Params

_Not decoded._ Expected to carry hotpoint center lat/lon, radius, altitude and circling direction/speed by analogy with DJI's public HotPoint mission model, but this is an informed guess from the function name alone, not a byte-level decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9A — Miss. HotPoint: Set Radius

_Not decoded._ Expected to carry a single radius value (meters, likely float32 or uint16 by DJI's typical HotPoint radius range of tens to hundreds of meters), but unconfirmed at byte level. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9B — Miss. HotPoint: Set Head

_Not decoded._ Not resolved -- see handler_evidence for what was tried and the one concrete (but unconfirmed) lead. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9C — Miss. WP: Set Idle Veloc

_Not decoded._ Not resolved -- see handler_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9D — Miss. WP: Get Idle Veloc

_Not decoded._ Not resolved -- see handler_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9E — App Ctrl Mission Yaw Rate

_Not decoded._ Not resolved -- see handler_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x9F — Miss. HotPoint: Auto Radius Ctrl

_Not decoded._ Not resolved -- see handler_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA0 — Send AGPS Data

_Not decoded._ Not resolved -- see handler_evidence for the FileTrans analogy lead. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA1 — FlyC AGPS Status Get

Payload decoder: `flyc_flyc_agps_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_agps_status_time_stamp` (Time Stamp) | uint32 |  |
  | 4 | 4 | `flyc_flyc_agps_status_data_length` (Data Length) | uint32 |  |
  | 8 | 2 | `flyc_flyc_agps_status_crc16_hash` (Crc16 Hash) | uint16 |  |

## 0xA2 — Race Drone OSD Push

_Not decoded._ Not resolved -- see handler_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA3 — Miss. WP: Get BreakPoint Info

_Not decoded._ Not resolved -- see handler_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA4 — Miss. WP: Return To Cur Line

_Not decoded._ Not resolved -- see handler_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA5 — App Ctrl Fly Sweep Ctrl

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: nav_v1_afqt_sweep_req (internal symbol-like string, vaddr 0xc6328), at code address 0x463fc-0x46528 in dji_autoflight; invoked (via a tail-call thunk at 0x4dc84) from the 'case_afqt_sweep' AFQT (AutoFlight Quality Test / factory tuning test) state machine starting at 0x2fbd0, whose config is loaded from a cJSON object with keys start_freq/end_freq/duration/amp (floats, offsets 0/4/8/12 of an 18-byte config struct) and inj_point/inj_loop (bytes, offsets 16/17) -- function at 0x2fb28, xref-resolved from the 'sweep config %.2f' and case_afqt_sweep debug strings.`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `sweep_msg_tag_a` (Internal Envelope Tag A) | uint8 | Observed constant 0x02 across all call sites seen; appears to be dji_autoflight's own internal message-bus framing, not sweep-specific data. Named conservatively -- real higher-level meaning not determined. |
  | 1 | 1 | `sweep_msg_tag_b` (Internal Envelope Tag B) | uint8 | Observed constant 0x03 across all call sites seen; same internal-framing caveat as tag_a. |
  | 2 | 1 | `sweep_mode` (Sweep Mode/Opcode) | uint8 | Function's first (r0) argument, stored verbatim; printed with %d in the debug strings. Plausibly a start/stop/calibrate selector for the sweep test, by analogy with this project's other small mode-selector bytes (e.g. cmd 0x22/0x60 Demo Mode Handle). |
  | 3 | 2 | `sweep_param_a_x10` (Sweep Parameter A (x10 fixed-point)) | uint16 | = round(param*10.0) where param is the function's 2nd float argument (r1/s19). Order-correlated but not proven 1:1 against the AFQT JSON config key 'start_freq' (a swept test frequency, Hz, scaled x10 for a 0.1 Hz fixed-point wire representation). |
  | 5 | 2 | `sweep_param_b_x10` (Sweep Parameter B (x10 fixed-point)) | uint16 | = round(param*10.0) where param is the function's 3rd float argument (r2/s18). Plausibly corresponds to the config key 'end_freq' by the same reasoning as sweep_param_a_x10. |
  | 7 | 2 | `sweep_param_c_x10` (Sweep Parameter C (x10 fixed-point)) | uint16 | = round(param*10.0) where param is the function's 4th float argument (r3/s17). Plausibly corresponds to the config key 'duration' or 'amp' by the same reasoning. |
  | 9 | 1 | `sweep_param_d` (Sweep Parameter D (unscaled)) | uint8 | The function's 5th argument (passed on the caller's stack, a float s16), truncated straight to uint8 WITHOUT the x10 scale applied to the other 3 -- notably different treatment, suggesting a small integer/count/index rather than a continuous measurement. Plausibly 'inj_point' (injection point/axis selector) from the AFQT config. |
  | 10 | 1 | `sweep_flags_packed` (Packed Sweep Flags) | uint8 | Bitfield built via 3 bfi instructions from the function's remaining stack arguments: bits[0:5) = a 5-bit value (6th argument), bits[5:7) = a 2-bit value (7th argument), bit[7] = a 1-bit value (8th argument). Plausibly related to 'inj_loop' (which control loop to inject into) and adjacent small enum/boolean test-control flags; exact sub-field semantics not individually confirmed. |

**Worked example:**

- Request payload: `02 03 01 32 00 C8 00 1E 00 01 20`
  11-byte internal request payload for nav_v1_afqt_sweep_req, constructed for documentation purposes (ordinary representative test values, not attack-shaped): tag_a=0x02, tag_b=0x03, sweep_mode=0x01 ('start'), sweep_param_a_x10=0x0032 (50 -> 5.0 units, e.g. a 5.0 Hz sweep start frequency), sweep_param_b_x10=0x00C8 (200 -> 20.0 units, e.g. a 20.0 Hz sweep end frequency), sweep_param_c_x10=0x001E (30 -> 3.0 units), sweep_param_d=0x01 (injection point index 1), sweep_flags_packed=0x20 (bits[5:7)=1, all other sub-fields 0).
- Response payload: `(ack-only; no distinct response payload)`
  This is a one-shot control/request command: the surrounding code checks only a boolean-ish return code from the internal send call and logs either 'sweep msg success %d: ...' (echoing the same 8 input values) or 'Failed to send afqt sweep ctrl cmd to FC, ret=%d' on failure -- consistent with a plain DUML ACK/NACK round-trip carrying no separate response fields, by analogy with other simple FlyC control commands in this cmd_set.

## 0xA6 — Set RKT Homepoint

_Not decoded._ Checked every known DUML registration mechanism for dji_flight and found no match: (1) dji_flight's own relocated {fn_ptr,cmd_word} dispatch array (corrected root vaddr 0xae040, 43 valid rows -- full dump in shared_infrastructure_found) has 5 cmd_set=3 rows (cmd_id 0x3f,0xc1,0xcd,0xdb,0xea) and none is 0xa6; (2) dji_flight imports NO duss_event_register_dynamic_command symbol at all (verified via nm -D and a full .rel.plt dump -- it only imports duss_mb_create_route_table/duss_event_create_client, used exactly once each), so the literal-immediate mechanism the task hinted at does not exist in this binary; (3) dji_sys's 11 duss_event_register_dynamic_command call sites were fully enumerated by disassembling every blx to its PLT stub (0x9bd0) -- 9 are literal immediates (0x22/0x60 x4 platform variants, 0x00/0xa3 x2, 0x06/0x3a x2, 0x04/0x69 x1) and 2 are runtime/config-driven loops (one per-client, one JSON-config-driven, matching this project's prior doc04/doc08 findings) -- none touches cmd_set 3 at all. 'RKT' was resolved via string evidence to DJI's internal codename 'ROCKET': dji_perception embeds the source path '.../missions/source/quickshot/quickshot_submode/qs_rocket.cpp', C++ RTTI names 'N10MasterShot20RocketPathControllerE'/'...Rocket2PathControllerE', the function name 'path_transf_QuickShot_rocket', and log strings 'Rocket Path Generate Failure!!' -- i.e. 0xA6 almost certainly sets the reference/home point for the 'Rocket' QuickShot automated camera move, a mission-planning feature inside dji_perception's quickshot submodule. dji_perception also only imports duss_mb_create_route_table/duss_event_create_client (not literal register_dynamic_command); an exhaustive decode of all 18 candidate 8-byte-stride relocation runs in its .data/.data.rel.ro sections (the same {fn_ptr,cmd_word} pattern as dji_flight's) found no cmd_set=3/cmd_id=0xa6 row -- every run that decoded 'sensibly' turned out to be a C++ vtable or bitmask table, not a DUML dispatch array. Incidental finding while chasing a 'nav_v1_flight_api_set_homepoint' lead in dji_navigation: that function (vaddr ~0x57350) really does hardcode cmd_set=3 in r1 before its generic send call, but the adjacent literal byte proves its cmd_id is 0x31 ('UAV Home Point Set', a different, still-undecoded cmd_id not in this batch) -- a genuine lead worth flagging for whoever owns 0x31, but it rules out that function as 0xA6's sender. No further lead found for 0xA6 itself. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAA — Sbus Packet

_Not decoded._ Same exhaustive negative result across dji_flight's table (no 0x03/0xaa row among its 5 cmd_set=3 entries), dji_flight's total absence of any register_dynamic_command import, and dji_sys's fully-enumerated 11 call sites (none under cmd_set 3). A string search for 'sbus' across the ENTIRE e1e firmware tree (every binary and kernel module) found exactly one hit: the kernel module rcam_dji.ko. Inspection of context (apical_sbus_*, sbus_spi_init, source path '.../rcam_drv/dji/.../apical_sbus.c') shows this is the Apical image-sensor-processor's internal register/SPI control bus, which happens to also be abbreviated 'sbus' -- a camera-ISP detail, unrelated to the RC/Futaba-style SBUS serial protocol this DUML command name implies. No genuine RC-SBUS-protocol code exists in any Android-side binary on this firmware image. Given the command is a raw, presumably high-rate serial RC-frame payload, this is architecturally consistent with this project's already-established conclusion for cmd_set 0x06 (Remote Control) and cmd_set 0x01 (Special): this class of low-level real-time control data is most plausibly consumed directly by the flight-controller's own RTOS MCU firmware (the still-unanalyzed 4.5MB non-ELF blob rtos_dec_RTOS.bin flagged in doc21), not parsed by any Android daemon in this extraction. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAB — Ctrl Attitude Data Send

_Not decoded._ Same exhaustive negative across dji_flight's table/imports and dji_sys's 11 fully-enumerated call sites (none is cmd_set 3). The string 'attitude' does appear in dji_perception, dji_autoflight, and dji_navigation, but every occurrence is internal attitude-estimation/control-law telemetry (generic attitude-controller/EKF-state log strings) with no cmd_set/cmd_id association recoverable via xref tracing, and none of those three binaries' own dispatch tables (dji_perception's were exhaustively decoded for this task; dji_navigation/dji_autoflight import neither register_dynamic_command nor the route-table pair for a comparable static table) contain a cmd_set=3/cmd_id=0xab row. Given this command's naming groups it with 0xAA 'Sbus Packet' and 0xAC 'Ctrl Taillock Data Send' as a family of raw-control-data injection commands (likely a bench/simulator-style direct-setpoint path that bypasses normal stick processing), the same RTOS-MCU-local reasoning given for 0xAA applies here. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAC — Ctrl Taillock Data Send

_Not decoded._ Same exhaustive negative across dji_flight's table/imports and dji_sys's 11 call sites. Unlike 'attitude', the string 'taillock'/'tail_lock'/'tail-lock' was searched for and found NOWHERE in the entire e1e firmware tree (checked every binary and library, not just the primary daemon candidates) -- a completely clean negative, stronger than the other two in this sibling group. Grouped architecturally with 0xAA/0xAB as a raw real-time control-injection command; same RTOS-MCU-local reasoning applies. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAD — FlyC Install Error Get

Payload decoder: `flyc_flyc_flyc_install_error_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_flyc_flyc_install_error_masked00` (Masked00) | uint32 |  |
  | 0 | 4 | `flyc_flyc_flyc_install_error_yaw_install_error_level` (Yaw Install Error Level) | uint32 | mask:`0x03` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_roll_install_error_level` (Roll Install Error Level) | uint32 | mask:`0x0c` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_pitch_install_error_level` (Pitch Install Error Level) | uint32 | mask:`0x30` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_gyro_x_install_error_level` (Gyro X Install Error Level) | uint32 | mask:`0xc0` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_gyro_y_install_error_level` (Gyro Y Install Error Level) | uint32 | mask:`0x300` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_gyro_z_install_error_level` (Gyro Z Install Error Level) | uint32 | mask:`0xc00` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_acc_x_install_error_level` (Acc X Install Error Level) | uint32 | mask:`0x3000` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_acc_y_install_error_level` (Acc Y Install Error Level) | uint32 | mask:`0xc000` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_acc_z_install_error_level` (Acc Z Install Error Level) | uint32 | mask:`0x30000` |
  | 0 | 4 | `flyc_flyc_flyc_install_error_thrust_install_error_level` (Thrust Install Error Level) | uint32 | mask:`0xc0000` |

## 0xAE — Cmd Handler RC App Chl Handler

_Not decoded._ Same exhaustive negative across dji_flight's table/imports and dji_sys's 11 call sites. Searched the entire e1e firmware tree for 'app_chl', 'appchl', 'app_channel', and 'rc_app' -- zero hits anywhere. The command's own name (containing the doubled word 'Handler' -- 'Cmd Handler ... Chl Handler') suggests this label may be a dissector-side auto-generated name derived from an internal class/enum identifier rather than a clean DJI feature name, which is consistent with finding no independent string trace of it in this firmware image at all. No lead found; this is a clean, total negative rather than a partial one. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xAF — Product Config

_Not decoded._ Same exhaustive negative across dji_flight's table/imports and dji_sys's 11 call sites. The string 'product_config' was found in exactly one place in the whole firmware tree: dji_sec, as part of the function name 'sec_act_check_product_config'. dji_sec is this project's already-documented activation/security daemon (docs 05/13/18); 'sec_act_*' functions are activation-integrity checks, not a DUML payload parser, and no register_dynamic_command/dispatch-table evidence ties this string to cmd_set 3 / cmd_id 0xaf specifically -- the match is thematic only, not a registration binding. Per this wave's task boundary, activation-internal logic in dji_sec was not characterized further (that subsystem is separately documented and closed in doc 18). No other lead found for this command. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB0 — Get Battery Groups Single Info

_Not decoded._ Same exhaustive negative across dji_flight's table/imports and dji_sys's 11 call sites. Searched the entire e1e tree for 'battery_group'/'batt_group' (and variants) -- zero hits anywhere. Cross-checked against this project's existing cmd_set 0x05 (Center Board) battery decode (`sys_battery_get_dynamic_info` in dji_sys, documented in cmdset_05_Center_Board.md) as a possible related mechanism, but that command uses a completely different cmd_set/dispatch path (a per-board-model SBS/SMBus callback reached via dji_sys's own generic request dispatcher, not a cmd_set-3 registration) with no evident tie to this FlyC-side 'Groups' query. The plural 'Groups' plausibly refers to the Mavic 3's dual-intelligent-battery hardware, but no binary evidence was found to support any specific byte layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB5 — FlyC Fault Inject Set

_Not decoded._ Same exhaustive negative across dji_flight's table/imports and dji_sys's 11 call sites. Its sibling GET command, cmd_set 3/0xB6 'FlyC Fault Inject Get', already has a pre-existing (Wireshark-sourced, not binary_re) decoded dissector: a single `status` byte with `enum: FLYC_FAULT_INJECT_STATUS_ENUM`. Set/Get pairs in this registry are very frequently byte-identical, so 0xB5 is plausibly the same single-enum-byte shape by convention -- but no binary evidence was found to independently confirm this for 0xB5, so it is NOT asserted as a decode (would be inventing a layout from a naming convention alone). Separately, dji_perception contains a real, extensive 'dbus_fault_injection' family of AUTOTEST functions (init_autotest_for_dbus_fault_injection, fmu_dbus_fault_injection, gohome_takeoff_height_dbus_fault_injection, press_alti_data_dbus_fault_injection, horiz_vel_flag_data_dbus_fault_injection) that is thematically a strong match (factory/QA fault-simulation for FMU/go-home/altitude/velocity-flag conditions), but dji_perception's own dispatch tables (exhaustively decoded for this task across all 18 candidate relocation runs) contain no cmd_set=3/cmd_id=0xb5 row, so no registration binding could be confirmed to this cluster either. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB6 — FlyC Fault Inject Get

Payload decoder: `flyc_flyc_fault_inject_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_fault_inject_status` (Status) | uint8 | enum:`enums.FLYC_FAULT_INJECT_STATUS_ENUM` |

## 0xB7 — Redundancy IMU Index Set and Get

_Not decoded._ Same exhaustive negative across dji_flight's table/imports and dji_sys's 11 call sites. Searched the entire e1e firmware tree for 'redundanc' (covers redundancy/redundant/etc.) -- zero hits in any binary or library on this firmware image, a completely clean negative. The command's own name (one cmd_id serving both 'Set and Get') architecturally matches this registry's existing precedent for combined-operation commands dispatched on a leading operation byte (e.g. cmd_set 0x51/0x05 'Route Switch', already decoded in this project as a 3-sub-layout payload keyed on a leading operation byte) -- a plausible structural pattern, but with zero binary evidence specific to this command, asserting it would violate this pass's no-invented-layout rule. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB8 — Redundancy Status

_Not decoded._ Same exhaustive negative (no 'redundanc' string anywhere in the firmware tree, no table/import match in dji_flight, no match among dji_sys's 11 fully-enumerated call sites). Its sibling PUSH command, cmd_set 3/0xB9 'Push Redundancy Status', already has a pre-existing (Wireshark-sourced) decoded dissector: `cmd_type` (uint8, enum FLYC_REDUNDANCY_STATUS_CMD_TYPE_ENUM) + `unknown1` (uint8). 0xB8 is plausibly the query/request counterpart that triggers this 0xB9 push (a bare status-request commonly carries a tiny or empty body while the 'Push' side carries the data), but no binary evidence was found to confirm 0xB8's own request shape -- it could equally be no_payload or a 1-byte selector, and asserting either without evidence would violate this pass's own rules, so it is reported insufficient_evidence rather than guessed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xB9 — Push Redundancy Status

Payload decoder: `flyc_flyc_redundancy_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_flyc_redundancy_status_cmd_type` (Command Type) | uint8 | enum:`enums.FLYC_REDUNDANCY_STATUS_CMD_TYPE_ENUM` |
  | 1 | 1 | `flyc_flyc_redundancy_status_unknown1` (Unknown1) | uint8 |  |
  | 2 | 1 | `flyc_flyc_redundancy_status_unknown2` (Unknown2) | uint8 |  |
  | 3 | 1 | `flyc_flyc_redundancy_status_unknown3` (Unknown3) | uint8 |  |
  | 4 | 1 | `flyc_flyc_redundancy_status_unknown4` (Unknown4) | uint8 |  |
  | 5 | 1 | `flyc_flyc_redundancy_status_unknown5` (Unknown5) | uint8 |  |
  | 6 | 1 | `flyc_flyc_redundancy_status_unknown6` (Unknown6) | uint8 |  |
  | 7 | 1 | `flyc_flyc_redundancy_status_unknown7` (Unknown7) | uint8 |  |
  | 8 | 1 | `flyc_flyc_redundancy_status_unknown8` (Unknown8) | uint8 |  |
  | 9 | 1 | `flyc_flyc_redundancy_status_unknown9` (Unknown9) | uint8 |  |
  | 10 | 1 | `flyc_flyc_redundancy_status_unknownA` (UnknownA) | uint8 |  |
  | 11 | 1 | `flyc_flyc_redundancy_status_unknownB` (UnknownB) | uint8 |  |

## 0xBA — Forearm LED Status Set

_Not decoded._ No duss_event_register_dynamic_command call site (literal or packed-cmd-word) for cmd_set 0x03/cmd_id 0xba was found in dji_flight, dji_sys (E1E ARM32 or E2 AArch64), dji_navigation, or dji_autoflight. dji_flight's relocated {func_ptr,cmd_word} dispatch array at vaddr 0xae038 (fully decoded, see shared_infrastructure_found) has no 0x03/0xba row. dji_flight imports zero duss_event_register_dynamic_command-family symbols at all (confirmed via readelf -rW and --dyn-syms: no PLT/JUMP_SLOT, no dynsym entry), so this cmd cannot be registered there directly.

Concrete lead found, not confirmed: dji_sys (E2/AArch64 build only) has a real function `led_control_thread` (vaddr 0x44960, recovered by name from .gnu_debugdata minidebuginfo; decompiled/decompressed and cross-checked against the live binary's own bytes). Its single argument is read as a 4-byte struct: byte0 bit1 = a gate/enable flag (tbz w8,#1 branches to the no-op exit if clear); byte1 = a 3-valued mode enum (0,1,2 - any other nonzero value also falls to the no-op exit); byte2 and byte3 = per-zone boolean flags, each independently logged if nonzero (consistent with 'forearm'=multiple LED positions/arms). Mode 2's branch additionally builds the 32-bit constant 0x7a120 (500000) passed to a call at vaddr 0x10110 (plausibly a delay/sleep primitive), consistent with a timed blink pattern. This 4-byte shape (enable_flag_bit, mode_enum, zone2_flag, zone3_flag) is a very plausible candidate for this command's payload, but: (1) no caller of led_control_thread (static bl/blx xref, or any relocation pointing at 0x44960) was found anywhere in the binary -- it is presumably invoked only via a runtime function-pointer table populated from dji_sys's own local JSON startup-config file (the same non-statically-enumerable mechanism this project already documented in 04_WM260_DAEMON_FINDINGS.md for cmd_set 0x10), so the exact byte-for-byte binding to cmd_id 0xba (vs. some other LED-adjacent cmd_id, or no DUML binding at all) is NOT confirmed; (2) the function does not exist at all in the E1E/ARM32 dji_sys build (checked directly), so this lead is architecture-specific. Reported as a lead, not a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBB — Open LED Info Get

_Not decoded._ Same search performed as for 0xba/0xbc/0xbe (dji_flight's 44-row dispatch table, dji_flight's and dji_sys's duss_event_register_dynamic_command call sites in both architectures, raw {0x03,0xbb,0,0} byte-pattern scan across dji_flight/dji_sys/dji_navigation/dji_autoflight): no match. No dji_sys .gnu_debugdata symbol name plausibly matches an 'Info Get' LED function either (only led_control_thread, sys_fc_led_exit, sys_fc_logout_led_ctrl_action have real FUNC symtab entries in either dji_sys build; none reads as a getter). The literal immediate 0xbb (187) was found via `mov w6, #0xbb` inside sys_fc_logout_led_ctrl_action, but that is a false lead: w6 there is consumed only as a duss_log_gen_head __LINE__-style argument (a run of consecutive, clearly-line-number-shaped constants 0x94/0x99/0x9e/0xbb/0xca/0xd2 appear through the same function), not a cmd_id -- flagging this explicitly so a future pass doesn't re-chase it. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBC — Open Led Action Register

_Not decoded._ The plain-text string `sys_fc_register_led_ctrl_action` exists verbatim in dji_sys(E2/AArch64)'s .rodata at vaddr 0xa589e -- an extremely strong name match for this exact command -- but it is NOT in dji_sys(E1E/ARM32) at all (checked directly, absent), and in the E2 build it has no .gnu_debugdata symtab FUNC entry and is not referenced by any adrp+add page/offset pair anywhere in a full linear disassembly of dji_sys(E2)'s .text, nor by any R_AARCH64_RELATIVE/data relocation pointing at that address. In other words the string is a dead/unreferenced constant in the one build that has it at all -- most plausibly the compiler-generated __func__ literal for a function whose body was linked out for this product/firmware generation (the same 'confirmed not present on this firmware generation' pattern this project already documented for the DM36x commands), or reached only via an indirection (a runtime function-pointer loaded from dji_sys's local JSON startup config) that this pass's static tracing could not follow. No duss_event_register_dynamic_command site for cmd_set 0x03/0xbc was found anywhere, and the raw {0x03,0xbc,0,0} byte pattern was not found in dji_flight/dji_sys(either arch)/dji_navigation/dji_autoflight. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBD — Open Led Action Logout

_Not decoded._ Handler SUBSYSTEM is confirmed with high confidence; the exact REQUEST wire-payload layout is not. `sys_fc_logout_led_ctrl_action` (dji_sys, E2/AArch64, vaddr 0x37548, size 828, name from .gnu_debugdata symtab) directly constructs the literal 32-bit value 0x000300bd (bytes: cmd_id=0xbd, cmd_set=0x03 packed as cmd_set<<16|cmd_id, via `mov w8,#0xbd` + `movk w8,#0x3,lsl #16` at vaddr 0x37600/0x37608) as part of an OUTGOING confirmation message it builds on the stack and sends via a call to the generic send primitive at PLT slot 0xf5c0 (`duss_event_send_sync`). This is the ONLY place in the whole dji_sys(E2) binary (and the only one of the project's whole-binary mov+movk-0x3<<16 sweep's 7 hits, 6 of which are genuine cmd_set-0x03 constructions -- see shared_infrastructure_found) where cmd_id 0xbd appears bound to cmd_set 0x03 this concretely -- this is a strong, real, disassembly-confirmed binding, not a name guess.

However, `sys_fc_logout_led_ctrl_action`'s single input argument (x19) is NOT read as raw wire bytes in this function -- it is read at offset+4 (loaded, then stored into the outgoing message as a uint16) and offset+8/+9 (two individual bytes, read once early on purely for a debug-log argument) -- i.e. x19 looks like a small, already-parsed per-client 'LED action registration record' (populated earlier by the Register path, 0xbc), not a fresh copy of this request's own wire payload. The function's only confirmed caller is `sys_fc_led_exit` (vaddr 0x37888, an internal cleanup/teardown routine, itself with no found caller either) -- so whether x19 is populated directly from this specific 0xbd request's payload, or is looked up by some other key (a connection/client id) with 0xbd carrying little or no payload of its own, could not be determined from static analysis alone. Reporting the struct offsets found (+4: 2 bytes used as uint16; +8: 1 byte; +9: 1 byte, log-only) as a lead, not asserting them as the confirmed wire layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBE — Open Led Action Status Set

_Not decoded._ Same situation as 0xbc: the plain-text string `sys_fc_set_led_action` exists in dji_sys(E2/AArch64) .rodata (vaddr 0xa59e4) -- a strong name match -- and IS referenced by one `add x0, x0, #0x9e4` at vaddr 0x95e44, but that reference turned out to be inside a generic CLI/diagnostic-dump routine (prints a sequence of named option strings via `printf`/`puts`, alongside many unrelated-looking labels in the same block) rather than a dedicated LED-action-status-set handler -- i.e. this looks like the string being used as one line of a human-readable settings dump/help text, not as a function's own __func__ tag or a registration call site. No duss_event_register_dynamic_command site for cmd_set 0x03/0xbe was found (checked all 12 dji_sys(E2) call sites, dji_flight's full 44-row table, and the raw {0x03,0xbe,0,0} byte pattern across all four candidate binaries in both architectures). The string is entirely absent from dji_sys(E1E/ARM32). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xBF — Flight Push

_Not decoded._ No duss_event_register_dynamic_command call site (literal, in any of the 12 dji_sys(E2) sites enumerated -- see shared_infrastructure_found -- nor in dji_sys(E1E)) and no row in dji_flight's full 44-row {func_ptr,cmd_word} dispatch table (0xae038-0xae190, fully decoded) corresponds to cmd_set 0x03/0xbf. Raw {0x03,0xbf,0,0} byte pattern not found in dji_flight/dji_sys(either arch)/dji_navigation/dji_autoflight. No plausible named symbol ('flight_push', 'push_flight', etc.) found in any binary's .gnu_debugdata or .dynsym. Given the generic name ('Flight Push'), this is plausibly a periodic telemetry broadcast built by a generic/templated push-sender (the same kind of stack-built-message-plus-duss_event_send_sync pattern seen for 0xbd) at one of many call sites this pass did not individually walk -- a concrete but unbounded lead, not chased further in the time available for this batch. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xC6 — Shell Test

_Not decoded._ No duss_event_register_dynamic_command call site for cmd_set 0x03/0xc6 found in dji_sys(either arch) or dji_flight; no row in dji_flight's fully-decoded 44-row dispatch table. Raw {0x03,0xc6,0,0} byte pattern not found in any of the four candidate binaries (either architecture where applicable). The only literal 0xc6 hit found, `mov w24, #0xc6` at dji_sys(E2) vaddr 0x36108, was checked and is unrelated: w24 there is not passed to any register/send call in its immediate vicinity (a brief check of the surrounding ~10 instructions found no duss_event_* call consuming it), so it was not pursued further as a possible false positive rather than asserted as a match. Given the name's similarity to the already-fully-documented cmd_set 0x00/0x89 'Shell Command' (handler duss_event_shell, confirmed in 04_WM260_DAEMON_FINDINGS.md), this may be a cmd_set-0x03-scoped analogue reachable only through the same non-statically-enumerable JSON-config-driven registration path already documented for other dji_sys commands in this project (see shared_infrastructure_found) -- a plausible architecture note, not a confirmed finding. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xCD — Update Nofly Area

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: outer dispatcher @ vaddr 0x1144c; type-0 sub-handler @ vaddr 0x112b8 (type-1 @ 0x1115c, type-2 @ 0x11114, type-3 @ 0x11104)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `operation_type` (Operation Type) | uint8 | Sub-operation selector for this command, dispatched via a 4-row function-pointer table inside dji_flight. Only values 0-3 are populated; any other value is a no-op (function-pointer slot is null/zero). |
  | 1 | 4 | `area_id_lo` (Area/Zone ID (low 32 bits)) | uint32 | Only read/stored for operation_type=0. Passed through unscaled; paired with the next field, plausibly the low half of a 64-bit zone/area ID (not independently confirmed as 64-bit vs. two separate 32-bit IDs). |
  | 5 | 4 | `area_id_hi` (Area/Zone ID (high 32 bits)) | uint32 | Only read/stored for operation_type=0. Passed through unscaled; see area_id_lo. |
  | 9 | 4 | `secondary_id_lo` (Secondary ID field (low)) | uint32 | Only read/stored for operation_type=0. Passed through unscaled, same pattern as area_id_lo/hi one field later in the struct; semantic meaning not determined (reported with a cautious, explicitly-generic name per the task's own standard, since no stronger evidence was found). |
  | 13 | 4 | `secondary_id_hi` (Secondary ID field (high)) | uint32 | Only read/stored for operation_type=0. Passed through unscaled; see secondary_id_lo. |
  | 17 | 4 | `revision_or_level` (Revision/Level value) | uint32 | Only read/stored for operation_type=0. Single pass-through field, no scaling; exact semantics not determined. |
  | 21 | 1 | `zone_subtype_byte` (Zone sub-type byte) | uint8 | Only read/stored for operation_type=0. Single byte, no scaling; plausibly a secondary classification byte distinct from zone_class below, exact meaning not determined. |
  | 22 | 4 | `duration_component_a` (Duration/time component A) | uint32 | Only read/stored for operation_type=0. Passed together with duration_component_b as two arguments to a helper function that performs a 64-bit-style division by 100 (confirmed via the function's gcc-style magic-constant multiply-and-shift division idiom); the single 4-byte result is stored, not either raw input. Plausibly a duration or a sub-second timestamp component; not independently confirmed. |
  | 26 | 4 | `duration_component_b` (Duration/time component B) | uint32 | Only read/stored for operation_type=0. See duration_component_a. |
  | 30 | 4 | `latitude_raw` (Latitude (raw wire int)) | int32 | Only read/stored for operation_type=0. Degrees * 1e7 (standard DJI wire convention). Internally converted by the handler to radians via raw*1e-7*(pi/180) using literal-pool double constants read directly from the binary. Reported as 'latitude' by analogy with this project's own cmdset_03_Flight_Control.md 0x3F entry's field order (latitude before longitude); the disassembly itself cannot distinguish which of this field and longitude_raw is really latitude vs. longitude, since both use byte-for-byte identical conversion code -- flagged as an assumption. |
  | 34 | 4 | `longitude_raw` (Longitude (raw wire int)) | int32 | Only read/stored for operation_type=0. Same format and conversion as latitude_raw; see that field's note on the lat/lon ordering assumption. |
  | 38 | 4 | `radius_mm` (Radius (millimeters)) | int32 | Only read/stored for operation_type=0. Raw wire value in millimeters; the handler converts it to meters internally via vdiv by the literal double constant 1000.0, read directly from the binary's own literal pool -- the /1000 scaling is disassembly-certain, the millimeter unit and 'radius' semantic are inferred from the task's own domain context (a no-fly-zone horizontal radius) and this project's prior documentation of DJI NFZ fields, not separately proven by name/string evidence inside this specific function. |
  | 54 | 2 | `shape_or_zone_type` (Shape/Zone type) | uint16 | Only read/stored for operation_type=0. Read as a 16-bit value but only the low 8 bits are ever stored by the handler (strb of the loaded halfword) -- i.e. effectively a 1-byte enum zero-padded to 16 bits on the wire. Plausibly a zone shape-type (cylinder/polygon/etc., per the task's own domain hint); specific enum values not determined. |
  | 58 | 4 | `begin_time_unix` (Effective begin time (Unix seconds)) | uint32 | Only read/stored for operation_type=0. Passed through unscaled; paired with end_time_unix immediately after it in both the wire layout and the destination struct, consistent with an effectivity time window. Not independently confirmed as Unix-epoch seconds vs. some other raw counter. |
  | 62 | 4 | `end_time_unix` (Effective end time (Unix seconds)) | uint32 | Only read/stored for operation_type=0. See begin_time_unix. |
  | 66 | 4 | `aux_field_c` (Auxiliary raw field C) | uint32 | Only read/stored for operation_type=0. Passed through unscaled, paired with aux_field_d immediately after it; semantics not determined (reported with an explicitly generic name). |
  | 70 | 4 | `aux_field_d` (Auxiliary raw field D) | uint32 | Only read/stored for operation_type=0. See aux_field_c. |
  | 74 | 4 | `aux_field_e` (Auxiliary raw field E) | uint32 | Only read/stored for operation_type=0. Single pass-through field, no scaling; semantics not determined. |
  | 78 | 1 | `enabled_flag` (Enabled flag) | uint8 (bit0) | Only read/stored for operation_type=0. Only bit 0 of this byte is extracted (ubfx) and stored as a 1-bit value; plausibly a zone enabled/active flag. |
  | 82 | 1 | `zone_class` (Zone classification) | uint8 (enum) | Only read/stored for operation_type=0. Normalized by a small helper (also reused elsewhere in this same handler family) that maps input 1->1, input 2->2, and any other value (including 0) ->0 before storing -- i.e. a validated tri-state enum, not a raw pass-through byte. |
  | 83 | 4 | `trailing_field` (Trailing raw field) | uint32 | Only read/stored for operation_type=0. Final field read by the handler; passed through unscaled; semantics not determined. |

**Worked example:**

- Request payload: `00e903000000000000000000000000000001000000010000000000000000c0474418a094e3d320a107000000000000000000000000000200000000b71b6900000000000000000000000001000000010000000100000000`
  A ground-control app defines a new, active, class-1, cylindrical no-fly zone (operation_type=0): area_id=1001 (0xe9030000... low word; hi word 0), revision/level=1, zone_subtype_byte=1, duration fields left at 0, latitude_raw=407128000 (40.7128 deg * 1e7), longitude_raw=-740060000 (-74.0060 deg * 1e7), radius_mm=500000 (500 m), shape_or_zone_type=2, begin_time_unix=1763424000 (an example Unix timestamp), end_time_unix=0 (no expiry), aux fields C/D left at 0, aux_field_e=1, enabled_flag=1, zone_class=1, trailing_field=0. All non-coordinate/non-radius fields whose semantics were not independently confirmed are filled with plausible placeholder values (0 or 1) for illustration, per the task's own instructions, not asserted as realistic real-world magnitudes beyond the lat/lon/radius fields.
- Response payload: `00`
  The outer dispatcher's own code path (outside the 4 sub-handlers) unconditionally returns 0 after dispatching, with no response-payload construction visible in the function itself; this project's established convention for this class of 'Set'-style DUML command (see e.g. the already-documented 0x60 'Demo Mode Handle' entry) is a minimal single-byte status/ack response. This specific ack byte value was not independently traced through the generic DUML response-wrapper that must sit above this dispatcher, so it is reported as the PLAUSIBLE convention, not a disassembly-confirmed response payload.

## 0xCE — Push Forbid Data Infos

_Not decoded._ No duss_event_register_dynamic_command call site for cmd_set 0x03/0xce was found in dji_sys (either architecture) or dji_flight; no row in dji_flight's fully-decoded 44-row dispatch table (which does have 5 other cmd_set-0x03 rows: 0x3f, 0xc1, 0xcd, 0xdb, 0xea -- none is 0xce). No packed cmd-word construction (cmd_set=3<<16 | 0xce) found anywhere in dji_sys(E2)'s whole-binary mov+movk-0x3-lsl-16 sweep (7 total hits found project-wide; 6 are genuine cmd_set-0x03 bindings -- 0x0c, 0xea, 0xeb, 0xec, 0xaf, 0xbd -- none is 0xce). Raw {0x03,0xce,0,0} byte pattern not found in any of the four candidate binaries. No 'forbid'/'nofly'-adjacent string found anywhere outside dji_perception's unrelated vision/obstacle-avoidance 'nofly_heights' strings (confirmed unrelated to DUML dispatch, per this project's own prior 04_WM260_DAEMON_FINDINGS.md). Given the name's clear pairing with 0xcd (Update Nofly Area, decoded above) and 0xcf (New Nofly Area Get, below), this is very plausibly the PUSH/notify counterpart sent by dji_flight to inform a connected app of forbidden-zone data -- but no concrete handler or send site could be pinned down in the time available for this batch. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xCF — New Nofly Area Get

_Not decoded._ No duss_event_register_dynamic_command call site for cmd_set 0x03/0xcf found in dji_sys (either architecture) or dji_flight; no row in dji_flight's fully-decoded 44-row dispatch table. No packed cmd-word construction (cmd_set=3<<16 | 0xcf) found in dji_sys(E2)'s whole-binary sweep (same 7-hit set checked for 0xce above -- no 0xcf). Raw {0x03,0xcf,0,0} byte pattern not found in any of the four candidate binaries. The one literal 0xcf hit found, `mov w2, #0xcf` at dji_sys(E2) vaddr 0x24598, was checked and ruled out: it sits inside a cJSON-based startup-config parser (confirmed by nearby `cJSON_GetObjectItem`/`cJSON_Delete`/`free` calls and an adjacent, unambiguously-unrelated JSON key string, 'timesync_master_pps', read by the same function at a nearby offset) and is used as an error/status CODE argument to a generic error-reporting helper, not a DUML cmd_id -- flagged explicitly as a decimal-coincidence false positive (0xcf=207) rather than asserted as a match, the same way the analogous 0xba hit in the same function was ruled out. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xD4 — Additional Info Get

_Not decoded._ No request/response structure recovered; cannot construct a worked example without inventing an unverified layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xD7 — FlyC Flight Record Get

_Not decoded._ No request/response structure recovered; cannot construct a worked example without inventing an unverified layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xD9 — Process Sensor Api Data

_Not decoded._ No request/response structure recovered; cannot construct a worked example without inventing an unverified layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xDA — FlyC Detection

_Not decoded._ No request/response structure recovered; cannot construct a worked example without inventing an unverified layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xDF — Assistant Unlock Handler

Payload decoder: `flyc_assistant_unlock_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_assistant_unlock_lock_state` (Lock State) | uint32 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_assistant_unlock_status` (Status) | uint8 |  |

> **Real firmware implementation found (follow-up pass).** The whole
> "Config Table" family below (`0xE0`-`0xE4`, `0xF3`, `0xF7`-`0xFC`, plus
> their cmd_set `0x01` aliases `0x40`-`0x43`) was, until this pass, known
> only from the public dissector's name-level decode — no firmware
> implementation had been traced. `test_rtos_raw` (a `dji_perception`
> Parameter-Manager QA/test harness, despite its filename-coincidence with
> the unrelated flight-control-RTOS `rtos_debug` tool) registers exactly
> this set of 12 distinct cmd_set `0x03` handlers (the 4 cmd_set `0x01`
> entries are confirmed exact aliases of 4 of them) under its own bus
> identity, using synthetic test-fixture parameters rather than real
> flight-controller parameters — confirming this is a **generic, reusable
> RPC surface any Parameter-Manager-linked daemon can register**, not
> something exclusive to the flight controller. The write-capable entries
> (`0xE3`/`0xF9`/`0xFC` and their `0x01` aliases) are gated, in this
> registrant, by two real checks: a writable-vs-read-only flag bit and a
> per-item privilege-level enum (an earlier draft of this finding claimed
> no check existed at all; that claim was independently re-examined and
> found incorrect — see below). See
> `15_SECOND_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track L for the full
> byte-level trace, the on-device QA-script corroboration
> (`dji_mb_ctrl -s 03 -c f8/f9 ...` over the real bus), and the correction
> to the original "no auth check" claim.

## 0xE0 — Config Table: Get Tbl Attribute

Payload decoder: `flyc_config_table_get_tbl_attribute_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_tbl_attribute_table_no` (Table No) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_tbl_attribute_status` (Status) | uint16 |  |

  *if (payload:len() - offset >= 6) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 2 | `flyc_config_table_get_tbl_attribute_table_no` (Table No) | int16 |  |
  | 4 | 4 | `flyc_config_table_get_tbl_attribute_entries_crc` (Table Entries Checksum) | uint32 |  |
  | 8 | 4 | `flyc_config_table_get_tbl_attribute_entries_num` (Table Entries Number) | uint32 |  |

## 0xE1 — Config Table: Get Item Attribute

Payload decoder: `flyc_config_table_get_item_attribute_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_attribute_table_no` (Table No) | int16 |  |
  | 2 | 2 | `flyc_config_table_get_item_attribute_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_attribute_status` (Status) | uint16 |  |

  *if (payload:len() >= 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 2 | 2 | `flyc_config_table_get_item_attribute_table_no` (Table No) | int16 |  |
  | 4 | 2 | `flyc_config_table_get_item_attribute_index` (Param Index) | int16 |  |
  | 6 | 2 | `flyc_config_table_get_item_attribute_type_id` (TypeID) | uint16 |  |
  | 8 | 2 | `flyc_config_table_get_item_attribute_size` (Size) | int16 |  |

  *if (type_id <= 3) or (type_id == 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 10 | 4 | `flyc_config_table_get_item_attribute_limit_u_def` (LimitU defaultValue) | uint32 |  |
  | 14 | 4 | `flyc_config_table_get_item_attribute_limit_u_min` (LimitU minValue) | uint32 |  |
  | 18 | 4 | `flyc_config_table_get_item_attribute_limit_u_max` (LimitU maxValue) | uint32 |  |

  *elseif (type_id >= 4) and (type_id <= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 10 | 4 | `flyc_config_table_get_item_attribute_limit_i_def` (LimitI defaultValue) | int32 |  |
  | 14 | 4 | `flyc_config_table_get_item_attribute_limit_i_min` (LimitI minValue) | int32 |  |
  | 18 | 4 | `flyc_config_table_get_item_attribute_limit_i_max` (LimitI maxValue) | int32 |  |

  *elseif (type_id == 8) or (type_id == 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 10 | 4 | `flyc_config_table_get_item_attribute_limit_f_def` (LimitF defaultValue) | float |  |
  | 14 | 4 | `flyc_config_table_get_item_attribute_limit_f_min` (LimitF minValue) | float |  |
  | 18 | 4 | `flyc_config_table_get_item_attribute_limit_f_max` (LimitF maxValue) | float |  |

## 0xE2 — Config Table: Get Item Value

Payload decoder: `flyc_config_table_get_item_value_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_value_table_no` (Table No) | int16 |  |
  | 2 | 2 | `flyc_config_table_get_item_value_unknown1` (Unknown1) | int16 |  |
  | 4 | 2 | `flyc_config_table_get_item_value_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_item_value_status` (Status) | uint16 |  |
  | 2 | 2 | `flyc_config_table_get_item_value_unknown1` (Unknown1) | int16 |  |

  *if (payload:len() >= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 4 | 2 | `flyc_config_table_get_item_value_index` (Param Index) | int16 |  |

  *if (payload:len() - offset >= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 6 | ? | `flyc_config_table_get_item_value_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

## 0xE3 — Config Table: Set Item Value

Payload decoder: `flyc_config_table_set_item_value_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_set_item_value_table_no` (Table No) | int16 |  |
  | 2 | 2 | `flyc_config_table_set_item_value_unknown1` (Unknown1) | int16 |  |
  | 4 | 2 | `flyc_config_table_set_item_value_index` (Param Index) | int16 |  |

  *if (payload:len() - offset >= 1) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 6 | ? | `flyc_config_table_set_item_value_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

## 0xE4 — Config Table: Reset Def. Item Value

_Not decoded._ No request/response structure recovered; cannot construct a worked example without inventing an unverified layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE5 — Push Config Table: Get Tbl Attribute

_Not decoded._ Likely a one-way aircraft-to-ground push notification by naming convention (unconfirmed); no byte layout recovered. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE6 — Push Config Table: Get Item Attribute

_Not decoded._ Likely a one-way aircraft-to-ground push notification by naming convention (unconfirmed); no byte layout recovered. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE7 — Push Config Table: Set Item Param

_Not decoded._ Likely a one-way aircraft-to-ground push notification by naming convention (unconfirmed); no byte layout recovered. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE8 — Push Config Table: Clear

_Not decoded._ Likely a one-way control/notification message by naming convention (unconfirmed); no byte layout recovered. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xE9 — Config Command Table: Get or Exec

Payload decoder: `flyc_config_command_table_get_or_exec_dissector`

## 0xEA — Register Open Motor Error Action

_Not decoded._ A client requests a 32-byte chunk of the NFZ database file starting at file offset 256 (e.g. refreshing a locally-cached slice of the geofence database). This is a request/response command, not one-way. Handler correctly identified (unnamed static function at dji_flight+0x20e14 (Thumb; stripped binary, no symbol table, so no real name is recoverable -- reported as an address, not a placeholder guess)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xEB — Logout Open Motor Error Action

_Not decoded._ Not present in dji_flight's 43-row {fn_ptr,cmd_word} dispatch array (vaddr 0xae040-0xae190, fully enumerated -- see shared_infrastructure_found). dji_flight does not import duss_event_register_dynamic_command at all (confirmed absent from readelf -sW's dynsym listing), so that whole mechanism is unavailable to it. An exhaustive byte-pair scan of dji_flight's entire .data/.data.rel.ro/.data.rel.ro.local regions for the literal bytes {0x03, 0xeb} found zero occurrences, ruling out any other small static table for this id within dji_flight. dji_sys's complete duss_event_register_dynamic_command call-site surface was enumerated on both architectures (2 call sites in the e1e/32-bit build, 11 bl instructions in the e2/64-bit build, fully decoded -- see shared_infrastructure_found): zero cmd_set 0x03 entries of any kind. The only other binaries in either firmware tree that import duss_event_register_dynamic_command at all are dji_sdrs_agent and test_rtos_raw (e1e) and duml_googletest (e2) -- none are plausible Flight-Control owners. A secondary lead: the flight-controller MCU RTOS firmware blob (rtos_dec_RTOS.bin) has a clear sibling subsystem for 'motor external error' (vp_motor_ext_err_register / vp_motor_ext_error_set / s_motor_ext_err_registry -- see the 0xea entry and shared_infrastructure_found), which would be the natural home for a paired 'logout'/unregister operation, but no distinctly-named 'logout'/'unregister'/'deregister' symbol-like string was found for it in that blob's string table; it may be a parameterized code path inside vp_motor_ext_err_register rather than a separately-named function, which this pass's tooling (string/relocation parsing of a raw flat binary with no symbol table) cannot resolve further. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xEC — Set Open Motor Error Action Status

_Not decoded._ Same negative result as 0xeb across every mechanism checked: absent from dji_flight's 43-row dispatch array, absent from dji_flight's full .data-region byte-pair scan for {0x03,0xec}, and absent from dji_sys's complete duss_event_register_dynamic_command surface on both architectures (zero cmd_set 0x03 entries). Stronger-than-usual secondary lead, reported honestly as unresolved rather than forced into a byte layout: the RTOS MCU firmware blob (rtos_dec_RTOS.bin) contains a function-name-like string 'vp_motor_ext_error_set' (and its mangled-looking duplicate 'Mvp_motor_ext_error_set'), plus the log format string 'Set motor external error failed. Return code: %u' and 'vp_motor_ext_error_init'. This is a real, named subsystem that matches this command's catalog name closely in spirit. However: (1) this blob is a raw flat binary with no ELF section/symbol table, so recovering its real function boundaries, calling convention, or byte-level argument layout reliably was not possible with the static tools available in the time budget (I could only confirm the blob is genuine ARM32 code -- its stated entry point at file offset 0x8000 disassembles as a textbook ARM exception-vector table, 'B'/0xEA... then seven 'LDR PC,[PC,#N]'/0xE59FF0xx opcodes -- not that this specific function's fields are recoverable); (2) no relay/bridge mechanism was found anywhere in dji_flight or dji_sys that would carry DUML wire command 0x03/0xec's payload bytes to this MCU-side function, so I cannot confirm this RTOS function is even the real target of this specific DUML command versus an internal-only MCU API used for something else entirely. Flagged as a concrete, well-evidenced lead for a future pass with proper flat-binary/RTOS disassembly tooling, not asserted as a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xED — ESC Echo Set

_Not decoded._ Absent from dji_flight's 43-row dispatch array and from the full .data-region byte-pair scan for {0x03,0xed}. Absent from dji_sys's complete duss_event_register_dynamic_command surface (both architectures). dji_flight does not import duss_event_register_dynamic_command. Checked the RTOS MCU firmware blob's extracted string table (31,120 printable strings) for 'esc_echo', 'echo_set', and bare 'ESC' -- the only 'ESC' hit was an unrelated JSON-escaping error message ('control character U+001B (ESC) must be escaped'), not an electronic-speed-controller reference. No candidate handler found in any binary or mechanism checked for this batch. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xEE — GoHome CountDown Get

_Not decoded._ Absent from dji_flight's 43-row dispatch array and from the full .data-region byte-pair scan for {0x03,0xee}. Absent from dji_sys's complete duss_event_register_dynamic_command surface (both architectures). Checked the RTOS MCU blob's strings for 'countdown'/'count_down'/'gohome'/'go_home' -- found a real 'go_home_takeoff_height' family of strings and functions (gohome_takeoff_height_dbus_fault_injection, go_home_takeoff_height_data, etc.), but these are about the RTH *altitude* parameter, not a *countdown timer*, and no distinct countdown-named symbol was found alongside them. One dead end worth recording so it isn't re-chased: dji_flight's own duss_event_create_client registration setup (at dji_flight+0x22bf0) contains a byte compare 'cmp r5,#238' (0xEE) while walking a libc++ list of dispatch-table entries -- this looked promising at first glance (0xEE is this command's own cmd_id) but on closer reading it is a generic low/high partitioning threshold applied uniformly to every entry's id byte during route-table setup, not a check specific to cmd_id 0xEE; recorded to save a future pass from re-investigating the same false lead. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF0 — Config Table: Get Param Info by Index

Payload decoder: `flyc_config_table_get_param_info_by_index_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_get_param_info_by_index_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_get_param_info_by_index_status` (Status) | uint8 |  |

  *if (payload:len() >= 8) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 2 | `flyc_config_table_get_param_info_by_index_type_id` (TypeID) | uint16 |  |
  | 3 | 2 | `flyc_config_table_get_param_info_by_index_size` (Size) | int16 |  |
  | 5 | 2 | `flyc_config_table_get_param_info_by_index_attribute` (Attribute) | uint16 |  |

  *if (type_id <= 3) or (type_id == 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_index_limit_u_min` (LimitU minValue) | uint32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_index_limit_u_max` (LimitU maxValue) | uint32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_index_limit_u_def` (LimitU defaultValue) | uint32 |  |

  *elseif (type_id >= 4) and (type_id <= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_index_limit_i_min` (LimitI minValue) | int32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_index_limit_i_max` (LimitI maxValue) | int32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_index_limit_i_def` (LimitI defaultValue) | int32 |  |

  *elseif (type_id == 8) or (type_id == 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_index_limit_f_min` (LimitF minValue) | float |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_index_limit_f_max` (LimitF maxValue) | float |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_index_limit_f_def` (LimitF defaultValue) | float |  |

## 0xF1 — Config Table: Read Params By Index

Payload decoder: `flyc_config_table_read_param_by_index_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_read_param_by_index_index` (Param Index) | int16 |  |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `flyc_config_table_read_param_by_index_index` (Param Index) | int16 |  |

## 0xF2 — Config Table: Write Params By Index

_Not decoded._ Absent from dji_flight's 43-row dispatch array and from the full .data-region byte-pair scan for {0x03,0xf2}. Absent from dji_sys's complete duss_event_register_dynamic_command surface (both architectures) -- note this includes the two data-driven/table-driven registration loops in dji_sys (the 'Param Manager'-adjacent mechanism from doc 21); neither loop's own cmd_set/cmd_id values are statically recoverable (they come from a runtime-populated registry, not a fixed .data table), so a live binding specifically to cmd_set 0x03 cannot be ruled out with full certainty for those two sites alone, but every *statically resolvable* mechanism checked is negative. The RTOS MCU blob's string table does contain many 'config_table' strings (get_config_table, Mchnl_config_table, Mopt3101_config_table_old/new, Mgpio_config_table, Muart_config_table, cfg_table_info, V_SENSOR_GET_CONFIG_TABLE_ERROR), but every one of these is tied to an internal driver/subsystem config table (vision sensor, GPIO, UART, an opt3101 ToF sensor, a flight-data recorder) rather than anything that looks like a generic DUML-wire-facing 'write/reset/set item by index' command family -- a real, specific, individually-checked negative rather than a guess. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF3 — Config Table: Reset Default Param Val

_Not decoded._ Same search and same result as 0xf2 (these three 'Config Table' commands were checked together): absent from dji_flight's dispatch array and full .data-region scan for {0x03,0xf3}; absent from dji_sys's complete duss_event_register_dynamic_command surface; the RTOS blob's many 'config_table'-named strings all belong to unrelated internal driver subsystems (vision sensor / GPIO / UART / ToF / recorder), not a DUML-command-facing generic config-table reset. See the 0xf2 entry for the full list of config_table strings checked and ruled out. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF4 — Config Table: Set Item By Index

_Not decoded._ Same search and same result as 0xf2/0xf3: absent from dji_flight's dispatch array and full .data-region scan for {0x03,0xf4}; absent from dji_sys's complete duss_event_register_dynamic_command surface; RTOS blob's config_table strings all tied to unrelated internal subsystems. See the 0xf2 entry for detail. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF5 — Ver Phone Set

_Not decoded._ Absent from dji_flight's 43-row dispatch array and from the full .data-region byte-pair scan for {0x03,0xf5}. Absent from dji_sys's complete duss_event_register_dynamic_command surface (both architectures). Checked the RTOS MCU blob's full string table for 'phone' and 'ver_phone' in any casing/separator form -- zero matches of any kind. No candidate handler found anywhere. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF6 — Push Param PC Log

_Not decoded._ Absent from dji_flight's 43-row dispatch array and from the full .data-region byte-pair scan for {0x03,0xf6}. Absent from dji_sys's complete duss_event_register_dynamic_command surface (both architectures). One weak, unconfirmed lead recorded rather than discarded silently: the RTOS MCU blob's string table contains 'pc_log_save_dir', which is at least thematically adjacent ('PC log'), but I found no format string, companion symbol, or any other corroborating evidence tying that specific string to a DUML-command-facing push operation rather than, e.g., a generic internal logging-directory configuration knob -- not promoted beyond a flagged lead. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xF7 — Config Table: Get Param Info By Hash

Payload decoder: `flyc_config_table_get_param_info_by_hash_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_config_table_get_param_info_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_get_param_info_by_hash_status` (Status) | uint8 |  |

  *if (payload:len() >= 8) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 2 | `flyc_config_table_get_param_info_by_hash_type_id` (TypeID) | uint16 |  |
  | 3 | 2 | `flyc_config_table_get_param_info_by_hash_size` (Size) | int16 |  |
  | 5 | 2 | `flyc_config_table_get_param_info_by_hash_attribute` (Attribute) | uint16 |  |

  *if (type_id <= 3) or (type_id == 10) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_hash_limit_u_min` (LimitU minValue) | uint32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_hash_limit_u_max` (LimitU maxValue) | uint32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_hash_limit_u_def` (LimitU defaultValue) | uint32 |  |

  *elseif (type_id >= 4) and (type_id <= 7) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_hash_limit_i_min` (LimitI minValue) | int32 |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_hash_limit_i_max` (LimitI maxValue) | int32 |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_hash_limit_i_def` (LimitI defaultValue) | int32 |  |

  *elseif (type_id == 8) or (type_id == 9) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 7 | 4 | `flyc_config_table_get_param_info_by_hash_limit_f_min` (LimitF minValue) | float |  |
  | 11 | 4 | `flyc_config_table_get_param_info_by_hash_limit_f_max` (LimitF maxValue) | float |  |
  | 15 | 4 | `flyc_config_table_get_param_info_by_hash_limit_f_def` (LimitF defaultValue) | float |  |

## 0xF8 — Config Table: Read Param By Hash

Payload decoder: `flyc_config_table_read_param_by_hash_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | ? | `flyc_config_table_read_param_by_hash_rq_num` (Request Number) | uint8 | // Add request number detached, without related byte within packet (it is just index of the value) |
  | 0 | 4 | `flyc_config_table_read_param_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |

## 0xF9 — Config Table: Write Param By Hash

Payload decoder: `flyc_config_table_write_param_by_hash_dissector`

  *if pack_type == 0 then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `flyc_config_table_write_param_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |
  | 4 | ? | `flyc_config_table_write_param_by_hash_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

  *else*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_write_param_by_hash_status` (Status) | uint8 |  |

  *if (payload:len() - offset >= 5) then*

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 1 | 4 | `flyc_config_table_write_param_by_hash_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |
  | 5 | ? | `flyc_config_table_write_param_by_hash_value` (Param Value) | bytes | Flight controller parameter value; size and type depends on parameter |

## 0xFA — Config Table: Reset Params By Hash

_Not decoded._ No confirmed handler binding; semantic name-match only, flagged honestly rather than asserted. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFB — Config Table: Read Params By Hash

Payload decoder: `flyc_config_table_read_params_by_hash_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `flyc_config_table_read_params_by_hash_unknown00` (Unknown00) | uint8 |  |
  | 1 | 4 | `flyc_config_table_read_params_by_hash_first_name_hash` (Param Name Hash) | uint32 | enum:`enums.FLYC_PARAMETER_BY_HASH_ENUM`; Hash of a flight controller parameter name string |

## 0xFC — Config Table: Write Params By Hash

_Not decoded._ No confirmed handler binding; semantic name-match only, flagged honestly rather than asserted. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFD — Product Type Get

_Not decoded._ Handler not located; one plausible-looking lead (dji_flight's Gimbal product-type-report handler) was traced and confirmed to be a different command under a different cmd_set, not this one. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFE — Motor Force Disable Set

_Not decoded._ No confirmed handler; flagged both as a possible dji_sys lead and as a possible MCU-firmware-resident command, neither confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xFF — Motor Force Disable Get

_Not decoded._ No confirmed handler; same unresolved candidates as the Set counterpart (0xfe), no independent distinguishing evidence found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

---

## Appendix: newer (2015/2017-era) parameter-table protocol structs
(from `comm_mkdupc.py`; these are the generic flight-parameter read/write
commands used by DJI Assistant 2 / the SDK to enumerate and tune hundreds of
named flight-controller parameters — "FlyC Param" style. All offsets
relative to the start of the DUML payload.)

### 0xDF — Assistant Unlock
**Request** (`DJIPayload_FlyController_AssistantUnlockRq`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 4 | lock_state | uint32 |

**Response** (`DJIPayload_FlyController_AssistantUnlockRe`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 1 | status | uint8 |

### 0xE0 — Get Table Attribute (2017 protocol)
**Request**: `table_no` (uint16, off 0).
**Response**: `status`(u16,0) `table_no`(u16,2) `entries_crc`(u32,4) `entries_num`(u32,8)
— or the shorter EOL form: `status`(u16,0) only.

### 0xE1 — Get Param Info By Index (2017 protocol)
**Request**: `table_no`(u16,0) `param_index`(u16,2).
**Response** (`U`=unsigned/`I`=signed/`F`=float variants, selected by `type_id`):
| Off | Size | Field | Type |
|---|---|---|---|
| 0 | 2 | status | uint16 |
| 2 | 2 | table_no | uint16 |
| 4 | 2 | param_index | uint16 |
| 6 | 2 | type_id | uint16 (see DJIPayload_FlyController_ParamType below) |
| 8 | 2 | size | uint16 |
| 10 | 4 | limit_def | uint32 / int32 / float |
| 14 | 4 | limit_min | uint32 / int32 / float |
| 18 | 4 | limit_max | uint32 / int32 / float |
| 22 | 160 | name | char[160] |
EOL short form: `status`(u16,0) only.

`DJIPayload_FlyController_ParamType` enum (`type_id` field above):
`0x0`=ubyte `0x1`=ushort `0x2`=ulong `0x3`=ulonglong `0x4`=byte(i8)
`0x5`=short(i16) `0x6`=long(i32) `0x7`=longlong(i64) `0x8`=float `0x9`=double
`0xA`=array `0xB`=bool. Values 0x4-0x7 are signed → response decodes with the
`I` struct variant (`limit_*` as signed int); 0x8/0x9 → `F` variant (float).

### 0xE2 — Read Param Value By Index (2017 protocol)
**Request**: `table_no`(u16,0) `unknown1`(u16,2) `param_index`(u16,4).
**Response**: `status`(u16,0) `unknown1`(u16,2) `param_index`(u16,4)
`param_value`(u8[160],6) — actual value occupies the first `size` bytes per
the param's type_id, rest is padding to the fixed 160-byte max.

### 0xE3 — Write Param Value By Index (2017 protocol)
**Request**, size varies by value width — `table_no`(u16,0) `unknown1`(u16,2)
`param_index`(u16,4) `param_value`(u8/u16/u32/u64/u8[16]/u8[160] at off 6,
width selected by how many bytes the caller sends: 1/2/4/8/16/≤160).
**Response**: `status`(u16,0) `table_no`(u16,2) `param_index`(u16,4)
`param_value`(u8[160],6).

### 0xF0 — Get Param Info By Index (2015 protocol, legacy — superseded by 0xE1)
**Request** (`DJIPayload_FlyController_GetParamInfoByIndex2015Rq`): `param_index`(u16,0).
**Response** (`U`/`I`/`F` variants by `type_id`, same enum as above):
| Off | Size | Field |
|---|---|---|
| 0 | 1 | status (uint8, not uint16 — legacy protocol) |
| 1 | 2 | type_id |
| 3 | 2 | size |
| 5 | 2 | attribute |
| 7 | 4 | limit_min |
| 11 | 4 | limit_max |
| 15 | 4 | limit_def |
| 19 | 160 | name |
EOL short form: `status`(u8,0) only. (cmd_id 0xF7 shares this same response shape.)

### 0xF8 — Read Param Value By Hash (2015 protocol — params addressed by name-hash, not index)
**Request** (`DJIPayload_FlyController_ReadParamValByHash2015Rq`): `param_hash`(u32,0).
**Response**: `status`(u8,0) `param_hash`(u32,1) `param_value`(u8[160],5).

Parameter name → hash function (`flyc_parameter_compute_hash` in
`comm_mkdupc.py`), confirmed matching DJI Assistant 2 behavior:
```python
def flyc_parameter_compute_hash(parname):
    parhash = 0
    parbt = parname.encode('gbk')
    for ncode in parbt:
        parhash = ((parhash & 0xffffffff) << 8) + ncode
        parhash %= 0xfffffffb   # note: NOT 0xffffffff - a prime-ish modulus just below 2^32
    return parhash
```

### 0xF9 — Write Param Value By Hash (2015 protocol)
**Request**: `param_hash`(u32,0) `param_value`(variable width 1/2/4/8/16/≤160, off 4).
**Response**: `status`(u8,0) `param_hash`(u32,1) `param_value`(u8[160],5).

These hash/index parameter-table commands are how DJI Assistant 2 and the
mobile SDK enumerate and tune the hundreds of named flight parameters (PID
gains, limits, feature toggles, etc.) without a fixed per-parameter `cmd_id`
— the parameter *name* (hashed) or a *table index* (looked up via 0xE0/0xE1)
is the real addressing scheme, layered on top of a handful of generic DUML
commands.
