# Cmd Set 0x0a — Mono/Binocular (Vision)

Total known command IDs: 48

## 0x01 — Eye Bino Info

Payload decoder: `mbino_bino_info_dissector`

## 0x02 — Eye Mono Info

_Not decoded._ Likely the monocular-sensor counterpart PUSH to 0x01's binocular info (single-camera vision-module status), following the same family naming pattern as the already-decoded 0x06-0x08/0x2f sensor-status pushes. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x03 — Eye Ultrasonic Info

_Not decoded._ Likely a PUSH of ultrasonic-rangefinder sensor status/readings, part of the same sensor-telemetry family as the already-decoded 0x2f 'Eye Sensor Status Push' (which itself only covers image/vision sensors, not ultrasonic specifically -- consistent with 0x03 being a separate, still-undecoded ultrasonic-specific push). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x04 — Eye Oa Info

_Not decoded._ 'Oa' most plausibly abbreviates Obstacle Avoidance -- likely a summary/aggregate obstacle-avoidance status PUSH, distinct from the already-decoded per-direction detail pushes at 0x06 ('Eye Avoidance Param'), 0x07 ('Eye Obstacle Info'), and 0x08 ('Eye TapGo Obst Avo Info'). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x05 — Eye Relitive Pos

_Not decoded._ Likely a PUSH of the vision system's relative-position estimate (e.g. relative to a tracked target, takeoff point, or precision-landing marker) -- an output of the vision daemon's pose-estimation pipeline. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Explicitly named as a PUSH -- a debug/diagnostic telemetry stream from the vision pipeline (likely feature counts, frame-processing stats, or algorithm internal state) sent outward for app-side diagnostics/logging, not a request-response command. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0B — Eye Push Control Debug Info

_Not decoded._ Explicitly named as a PUSH -- likely a diagnostic stream of the vision-driven control-loop internals (e.g. the obstacle-avoidance/tracking control outputs that feed into flight commands), paired conceptually with 0x0a's vision-side debug push. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Explicitly named as a PUSH -- plausibly the vision daemon forwarding/echoing an SDK-originated control command (e.g. a payload SDK gimbal/vision control instruction) outward for logging or app-side confirmation, analogous in spirit to the already-catalogued cmd_set 0x01 'SDK Ctrl' bridge commands (which this project's most recent sweep, 21_PAYLOAD_DECODE_SWEEP_FINDINGS.md, also could not resolve -- all 10 of that cmd_set's SDK-bridge commands came back insufficient_evidence after an equally thorough pass). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x10 — Eye Enable Tracking Taptogo

_Not decoded._ Unlike the rest of this batch, the name has no 'Push' qualifier -- this is most plausibly an INBOUND app/SDK-to-aircraft command (an app toggling TapFly/'tap-to-go' subject tracking on or off), conceptually adjacent to the already-decoded 0x08 'Eye TapGo Obst Avo Info' and 0x26 'Eye TapGo Status Push', both of which came from the public dissector source rather than binary RE. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x11 — Eye Push Target Speed Pos Info

_Not decoded._ Explicitly named as a PUSH -- likely a periodic report of a tracked target's estimated speed and position (from the tracking/TapFly pipeline), conceptually adjacent to the already-decoded 0x23 'Eye Tracking Status Push' and 0x26 'Eye TapGo Status Push' (both decoded from the public dissector, which already documents target_type/target_action/center_x/y/width/height-style fields for the sibling tracking-status command). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x12 — Eye Push Target Pos Info

_Not decoded._ Checked this project's own docs first (21_PAYLOAD_DECODE_SWEEP_FINDINGS.md, 04/06/11/14_*.md) — no prior handler for this cmd_id. Independently re-dumped dji_flight's relocated dispatch table at vaddr 0xae038 byte-for-byte (confirmed 44 raw 8-byte rows through 0xae190, matching this project's prior count) and decoded its cmd_word packing (low byte of the 16-bit word = cmd_set, high byte = cmd_id; cross-validated against this project's own previously-confirmed cmd_set-0x22 rows 0x06/0x07/0x08/0x44, which decode correctly under this scheme). The table's only two cmd_set-0x0a rows are cmd_id 0xDD and 0xDE (vaddr 0xae188/0xae190) — 0x12 is not among them, ruling out dji_flight. Confirmed via `readelf -rW` on both dji_perception builds that neither imports any duss_event_register_dynamic_command-family symbol (re-confirms doc 04 independently). Resolved dji_perception E1E's real call sites to duss_mb_create_route_table/duss_event_create_client/duss_event_send/duss_event_send_sync via PLT-stub address arithmetic plus .ARM.exidx-anchored per-function disassembly (a naive linear Thumb sweep across this 20MB stripped binary desyncs after ~128KB and stops finding real calls — exidx-anchored per-function restart was needed for reliability). The real duss_event_send wrapper functions found (vaddr 0x63d0d8/0x63d268/0x63d428/0x63d728) build their packet entirely from a caller-supplied struct (a 16-bit cmd_word field at a fixed struct offset, plus payload ptr/len), so the literal cmd_id is set by a still-unidentified deeper caller. A literal-immediate scan for the packed cmd_word 0x120a found 2 hits in dji_perception E1E (vaddr 0x99e8da/0x99e8e4), but disassembling the surrounding code proved this is a rate-limited internal error/status-code logger (shared helper at vaddr 0x99e2cc, called identically from 3 unrelated functions elsewhere) whose internal module/error-tag namespace happens to also end in byte 0x0a — explicitly refuted as a DUML cmd_word, not a real handler. Searched the entire decrypted firmware tree (both E1E and E2 roots, every file, case-insensitive) for 'target_pos'/'push_target_pos'/'targetpos' — only hits are generic homing-planner/camera-tracking 'target_pos_x/y/z' fields (dji_flightsystem_msgs ROS-style schema strings), already characterized by doc 04 as perception-internal telemetry schema unrelated to DUML cmd_id dispatch (none of those string addresses is referenced by dispatch code). Reporting insufficient_evidence rather than a guessed layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x13 — Eye Push Trajectory

_Not decoded._ Same dji_flight dispatch-table check as 0x12 (see that entry / shared_infrastructure_found): cmd_id 0x13 is not among the table's only two cmd_set-0x0a rows (0xDD, 0xDE), ruling out dji_flight. Same import-table confirmation (readelf -rW, both architectures): dji_perception imports no duss_event_register_dynamic_command-family symbol. A literal-immediate scan for the packed cmd_word 0x130a found 3 hits in dji_perception E1E, all inside one function at vaddr 0x99d8f8 (movw at 0x99da10, 0x99dc20, 0x99dc26). Disassembling that function's surrounding code shows the same shared rate-limited log helper (bl to vaddr 0x99e2cc) seen for 0x12, inside what is structurally a generic circular-buffer/queue read routine (wraparound arithmetic, memcpy via an internal vtable pointer, a sibling 0x150a code path a few hundred bytes later in the same function — see 0x15 below) — this is the same internal ring-buffer/queue module error-code namespace (low byte 0x0a as a module tag), not a DUML cmd_word; explicitly refuted. Zero hits for the same literal in the E2 (aarch64) build. The project's existing docs (04_WM260_DAEMON_FINDINGS.md) already document that dji_perception's many embedded 'trajectory' strings (homing/MPC path-planning, hyperlapse waypoint logic) are a self-describing ROS-style telemetry schema used for black-box logging, not DUML cmd dispatch — re-confirmed here by a fresh full-tree string search turning up only the same category of hits (homing_local_planner, mpc_follower, HyperlapseWaypointBack, etc.), none of which resolve to a DUML wire parser for this specific cmd_id. Reporting insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x14 — Eye Push Expected Speed Angle

_Not decoded._ Same dji_flight dispatch-table check as 0x12: cmd_id 0x14 is not among the table's two cmd_set-0x0a rows (0xDD, 0xDE). Same import-table confirmation: dji_perception imports no duss_event_register_dynamic_command-family symbol on either architecture. A full-tree case-insensitive string search (both E1E and E2 roots, every file) for 'expected_speed', 'expectedspeed', and 'expected speed angle' produced zero hits anywhere in the firmware — not even an unrelated/generic false-positive, unlike several of the other commands in this batch. A literal-immediate scan for the packed cmd_word 0x140a across all 43,286 exidx-delimited functions in dji_perception E1E, and across the full linearly-disassembled .text of the E2 (aarch64) build, found zero matches in either architecture. No lead of any kind found; this is the cleanest 'nothing found' result in the batch, not a near-miss. Reporting insufficient_evidence, not a guessed layout. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x15 — Eye Receive Frame Info

_Not decoded._ Same dji_flight dispatch-table check as 0x12: cmd_id 0x15 is not among the table's two cmd_set-0x0a rows. Same import-table confirmation (no duss_event_register_dynamic_command on either architecture). A literal-immediate scan for the packed cmd_word 0x150a found 2 hits, both in the SAME function as the 0x13 hits above (dji_perception E1E, vaddr 0x99d8f8; movw at 0x99dbd6 and 0x99dbdc). Disassembly confirms this is the identical ring-buffer/queue-module error-code path (same shared log helper at vaddr 0x99e2cc) described for 0x13 — explicitly refuted as a DUML cmd_word. A full-tree string search for 'frame_info'/'frameinfo' does hit many files on both images, but every hit traces to generic OMX/video-codec struct naming (libOmxCamCapEngSource.so, libOmxVideoPyramidGen.so, libduml_hal.so, etc.) — a 'VFrameInfo'/frame-metadata struct used throughout the camera/video pipeline, unrelated to the DUML wire protocol by name collision only. No evidence connects any of these string hits to a cmd_set-0x0a/cmd_id-0x15 dispatcher. Reporting insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x19 — Eye Flat Check

Payload decoder: `mbino_flat_check_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_flat_check_tink_count` (Tink Count) | uint8 |  |

## 0x1D — Eye Fixed Wing Ctrl

_Not decoded._ Same dji_flight dispatch-table check as 0x12: cmd_id 0x1D is not among the table's two cmd_set-0x0a rows. Same import-table confirmation on both dji_perception architectures. A full-tree case-insensitive string search (both E1E and E2 roots, every file on both images) for 'fixed_wing', 'fixedwing', and 'FixedWing' found ZERO hits anywhere in the entire decrypted firmware — the strongest negative result in this batch. A literal-immediate scan for the packed cmd_word 0x1d0a found zero matches in either architecture build of dji_perception. Given the Mavic 3 is a quadcopter, not a fixed-wing aircraft, this is consistent with (though not proof of) this being a fixed-wing-product-specific DUML command with no live code path compiled into this product's firmware image at all — the same category of finding this project previously made for DM36x-specific commands ('confirmed not implemented on this firmware generation'), though that prior case had direct device-type-string evidence of hardware retirement and this one does not, so it is reported here as insufficient_evidence with the zero-string-hit result called out explicitly rather than upgraded to a 'confirmed not implemented' verdict. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1E — Eye Fixed Wing Status Push

_Not decoded._ Same checks and same result as 0x1D immediately above: not in dji_flight's dispatch table (not among its two cmd_set-0x0a rows, 0xDD/0xDE); dji_perception imports no duss_event_register_dynamic_command on either architecture; zero string hits anywhere in either firmware tree for fixed_wing/fixedwing/FixedWing; zero literal-immediate hits for the packed cmd_word 0x1e0a in either architecture build. As with 0x1D, this is consistent with a fixed-wing-aircraft-specific command with no live code path on this quadcopter product, but that is not independently confirmed (no device-type string evidence as in the DM36x precedent), so reported as insufficient_evidence rather than 'confirmed not implemented'. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x20 — Eye Marquee Push

_Not decoded._ Same dji_flight dispatch-table check as 0x12: cmd_id 0x20 is not among the table's two cmd_set-0x0a rows. Same import-table confirmation (no duss_event_register_dynamic_command on either architecture). A full-tree string search for 'marquee' (both E1E and E2 roots, every file) found zero hits anywhere in the firmware. A literal-immediate scan for the packed cmd_word 0x200a found zero hits in dji_perception E1E but 2 hits in the E2 (aarch64) build (vaddr 0x180218 and 0x1802e0, both inside the same function). Disassembling that AArch64 code (`mov w9, #0x200a` immediately followed by `movk w9, #0x2020, lsl #16`, forming the full 32-bit word 0x2020200a, stored via `str w9, [x3]`) shows this is not a 16-bit cmd_word at all — 0x2020200a decodes byte-by-byte (little-endian) as the ASCII bytes `0a 20 20 20`, i.e. a newline followed by three spaces, built inside what is structurally a string-tokenizing/field-splitting routine (adjacent code compares extracted substrings of length 6 and 9 against literal pool strings via a memcmp-like call). This is an explicitly refuted false positive: the apparent 'cmd_word' match is a coincidental collision between the DUML cmd_set byte (0x0a) and the ASCII newline byte, not a real DUML cmd_word construction site. Reporting insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — Eye Tracking Cnf Cancel

_Not decoded._ Same dji_flight dispatch-table check as 0x12: cmd_id 0x21 is not among the table's two cmd_set-0x0a rows. Same import-table confirmation on both dji_perception architectures. A full-tree string search for 'tracking_cnf', 'trackingcnf', and 'cancel_tracking' found zero hits anywhere in either firmware tree. A literal-immediate scan for the packed cmd_word 0x210a found 1 hit in dji_perception E1E (vaddr 0x99cffe, `movw r0, #0x210a`), inside a function (vaddr 0x99cedc) that is structurally the same kind of circular-buffer peek/consume routine seen for 0x12/0x13/0x15 (wraparound pointer arithmetic, a memcpy call, an internal read-like syscall wrapper at vaddr 0x89e08, and the same family of sibling return/error constants 0x10a/0x20a/0x30a/0x60a appearing a few dozen bytes away in the same function) — all sharing the low byte 0x0a as what is evidently this ring-buffer module's own error/status-code tag, not the DUML cmd_set byte. Explicitly refuted as a DUML cmd_word for the same reason as 0x12/0x13/0x15. Zero hits for the same literal in the E2 build. Reporting insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — Eye Move Marquee Push

_Not decoded._ Same dji_flight dispatch-table check as 0x12: cmd_id 0x22 is not among the table's two cmd_set-0x0a rows. Same import-table confirmation on both dji_perception architectures. A full-tree string search for 'move_marquee' and 'moveMarquee' found zero hits anywhere (consistent with the zero hits for plain 'marquee' under 0x20 above — the whole Marquee feature name is entirely absent from both firmware images' strings). A literal-immediate scan for the packed cmd_word 0x220a found zero matches in either dji_perception architecture build. No lead of any kind found. Reporting insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Same dji_flight dispatch-table check as 0x12: cmd_id 0x24 is not among the table's two cmd_set-0x0a rows. Same import-table confirmation on both dji_perception architectures. A full-tree string search for 'position_push' and 'eye_position' found zero hits anywhere in either firmware tree. A literal-immediate scan for the packed cmd_word 0x240a found zero matches in either architecture build. Note on adjacency: the immediately preceding cmd_id, 0x23 ('Eye Tracking Status Push'), already has a full public-dissector-sourced decode in this project's cmdset_0a doc, and the immediately following cmd_id, 0x25 ('Eye Fly Ctl Push'), is itself undecoded — no structural or textual link was found connecting 0x24 specifically to either neighbor's handling. Reporting insufficient_evidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x25 — Eye Fly Ctl Push

_Not decoded._ Checked cmdset_0a_Mono-Binocular_(Vision).md and commands.json (decode_status none, note null) -- confirmed fresh. dji_flight's relocated {fnptr,cmd_word} dispatch table at vaddr 0xae038 (E1E/32-bit ARM only; no E2 dji_flight exists) was dumped byte-for-byte (44 rows, 0xae038-0xae190 inclusive, cross-checked against R_ARM_RELATIVE relocations at every 8-byte boundary) -- it contains exactly 2 cmd_set 0x0a rows (cmd_id 0xdd, 0xde), neither matching 0x25. dji_perception (both E1E 32-bit ARM and E2 aarch64 builds) imports zero duss_event_register_dynamic_command-family symbols (readelf --wide --dyn-syms, both builds), ruling out the project's primary literal-immediate registration mechanism for this daemon directly. Strings search for 'fly_ctl'/'flyctl'/'FlyCtl' (case-insensitive) across both dji_perception builds and dji_flight returned nothing. A literal-immediate (r1=cmd_set/r2=cmd_id per doc 04's w1/w2 convention) scan of dji_sys (E1E) for cmd_set=0x0a + this cmd_id found no hits, but this method could not be validated against a known-positive control case (0x00/0xa3) either -- the control's real registration path turned out to be a struct-descriptor table filled by sys_platform_e2_wm260_init, not a literal-immediate-before-bl in that function -- so this specific negative result is not fully trustworthy and is reported as a lead tried, not a confirmed exclusion. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Same baseline checks as 0x25 (doc/commands.json confirmed fresh; dji_flight's 0xae038 table checked and ruled out -- its only cmd_set 0x0a rows are 0xdd/0xde; dji_perception's absent duss_event_register_dynamic_command import confirmed on both builds). Strings search for 'common_ctl'/'CommonCtl' across both dji_perception builds and dji_flight returned nothing. Given the generic name ('Common Ctl Cmd' mirrors the generic-control-command naming pattern seen in other cmd_sets, e.g. cmd_set 0x03's many '*_ctl' commands), this is plausibly a catch-all vision-subsystem control opcode multiplexed by an internal sub-type byte, but no disassembled evidence of such a sub-dispatch was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x28 — Eye Get Para Cmd

_Not decoded._ Baseline checks (doc/commands.json, dji_flight 0xae038 table, dji_perception register_dynamic_command import) as for 0x25/0x27, all negative/ruled-out the same way. A concrete lead was chased: E2 dji_perception's recovered .gnu_debugdata local symbol table has 'api_usr_get_param_by_index_handler' (vaddr 0x100388) and 'api_usr_get_param_by_index_func' (0xffc5c), names that plausibly match 'Get Para Cmd'. Disassembled both (AArch64, capstone) -- api_usr_get_param_by_index_func is itself never reached by any direct BL in .text (zero callers found), but IS referenced by an R_AARCH64_RELATIVE relocation inside a 24-byte-stride table at vaddr 0x390a98 (handler_ptr, a shared secondary ptr 0xff5e4, and a per-row id word). Dumping that table's id words (0xe00003, 0xe10003, 0xe20003, 0xe30003, 0xe40003, 0x400001, 0x410001, 0x420001, ...) shows sequential internal parameter-index values with no byte equal to the DUML cmd_set byte 0x0a anywhere in the pattern -- this looks like DJI's generic internal 'app_get_param'/'ss_get_param' parameter-store API (also attested by plaintext strings 'api_usr_get_param', '/device/terminal/0/request/app_get_param', 'TerminalRequestAppGetParam' in these binaries), not a binding keyed on DUML (cmd_set,cmd_id). Per this project's own established caution (doc 21: dji_perception's embedded message-schema strings have previously been a false lead for an unrelated 'waypoint' case), this lead is recorded but NOT asserted as the real handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x29 — Eye Set Para Cmd

_Not decoded._ Mirror of 0x28's investigation: E2 dji_perception's 'api_usr_set_param_by_index_handler' (0x10040c) / 'api_usr_set_param_by_index_func' (0xffd18) were disassembled and found referenced from the same 24-byte-stride relocated table (row at vaddr 0x390ab0, id word 0xe30003, directly adjacent to the get-param row). Same conclusion as 0x28: this is DJI's generic internal parameter-store API (also attested by 'api_usr_set_param', '/device/terminal/0/request/app_set_param', 'TerminalRequestAppSetParam' strings), with no byte 0x0a anywhere in its sequential internal id scheme -- plausible but unconfirmed, not asserted as the DUML handler for this cmd_id. Baseline dji_flight-table / dji_perception-import checks as in 0x25/0x27/0x28 all ruled out the same way. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Baseline checks (doc/commands.json fresh; dji_flight 0xae038 table's only cmd_set 0x0a rows are 0xdd/0xde, not 0x2c; dji_perception imports no duss_event_register_dynamic_command-family symbol on either build) all negative. 'Ta' most plausibly abbreviates 'Target' (cf. already-decoded sibling 0x23 'Eye Tracking Status Push' which has target_type/target_action enum fields) -- a byte-pattern scan for a {fnptr; cmd_set=0x0a; cmd_id=0x2c; pad} 8-byte table row (mirroring dji_flight's confirmed table format) across dji_perception (both builds), dji_flight, and dji_sys (both builds) surfaced a few raw coincidental byte matches (e.g. in dji_perception's large OpenCV/data-heavy text/data regions) but none corresponded to an ELF relocation at that offset, i.e. none are confirmed real pointer table rows -- discarded as noise, not evidence. Strings search for 'ta_lock'/'TaLock' across both dji_perception builds and dji_flight returned nothing. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2D — Eye Smart Landing

_Not decoded._ Baseline checks (doc/commands.json fresh; dji_flight 0xae038 table ruled out for 0x2d; dji_perception register_dynamic_command import absent on both builds) all negative. Strings search for 'smart_land'/'SmartLand'/'SmartLanding' across both dji_perception builds and dji_flight returned nothing -- notably different from 'Eye Self Calibration' (0x30) and 'Eye Precise Landing Energy' (0x3a, already decoded), where real plaintext leads exist; no comparable lead surfaced for this cmd_id specifically. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Baseline checks (doc/commands.json fresh; dji_flight 0xae038 table ruled out for 0x30; dji_perception register_dynamic_command import absent on both builds) all negative. A real, substantive lead exists in E1E dji_perception: a 'PnpSelfcaliBase' C++ class and numerous debug strings ('CALI_SELFCALE_FAIL', 'CALI_UPDATE_SELFCALI_ERR', '[%d] pnp selfcali finish fail...', '[%d] save result, all selfcali update num is [%d]'), and E2 dji_perception embeds a ROS-style self-describing message schema named 'dji_flightsystem_msgs/CalibrationSelfcaliInput'. However, per this project's own established finding (21_PAYLOAD_DECODE_SWEEP_FINDINGS.md), dji_perception's embedded dji_flightsystem_msgs schema strings are confirmed (for an unrelated waypoint case, by exhaustive capstone/relocation/hex-operand cross-check) to be field names of an internal black-box/bag telemetry-logging schema, not DUML wire-command field names -- the same caution applies here: no instruction anywhere in either binary was found to reference 'CalibrationSelfcaliInput' or treat it as an incoming DUML payload, so this is a real architectural lead (self-calibration genuinely exists and is logged) but not evidence of the wire-level byte layout, and is not asserted as a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x32 — Eye Easy Self Calib State

Payload decoder: `mbino_easy_self_calib_state_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `mbino_easy_self_calib_state_tink_count` (Tink Count) | uint8 |  |
  | 1 | 1 | `mbino_easy_self_calib_state_unknown01` (Unknown01) | uint8 |  |
  | 2 | 1 | `mbino_easy_self_calib_state_sensor_type` (Sensor Type) | uint8 | enum:`enums.MBINO_EASY_SELF_CALIB_STATE_VISION_SENSOR_TYPE_ENUM` |

## 0x37 — Eye QRCode Mode

_Not decoded._ Baseline checks (doc/commands.json fresh; dji_flight 0xae038 table ruled out for 0x37; dji_perception register_dynamic_command import absent on both builds) all negative. Strings search for 'qrcode'/'QRCode'/'qr_code' (case-insensitive) across both dji_perception builds and dji_flight returned nothing -- no plaintext trace of QR-code precision-landing functionality in either binary. A byte-pattern scan for an {fnptr; cmd_set=0x0a; cmd_id=0x37; pad} table row produced many hits in E2 dji_perception, but all were a single recurring coincidental byte sequence scattered through large binary/data regions (no corresponding ELF relocation at any hit offset), confirmed as noise rather than a real table. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

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

_Not decoded._ Baseline checks (doc/commands.json fresh; dji_flight 0xae038 table ruled out for 0x46; dji_perception register_dynamic_command import absent on both builds) all negative. Strings search for 'rc_packet'/'RcPacket' across both dji_perception builds and dji_flight returned nothing. Given this project's prior finding that cmd_set 0x06 (Remote Control) traffic is almost entirely opaque to this firmware extraction (handled in the physical RC's own MCU or relayed byte-blind), and that the already-decoded sibling cmd_id 0x26 ('RC AETR Value Push', aileron/elevator/throttle/rudder int16 struct) was only inferable by analogy via dji_perception's embedded message schema rather than a disassembled parser, 'Eye RC Packet' is plausibly a similar RC-stick-relay structure consumed by the vision/avoidance pipeline, but no disassembled command-specific parser or matching embedded struct definition was found for cmd_id 0x46 specifically. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x47 — Eye Set Buffer Config

_Not decoded._ Baseline checks (doc/commands.json fresh; dji_flight 0xae038 table ruled out for 0x47; dji_perception register_dynamic_command import absent on both builds) all negative. Strings search for 'buffer_config'/'BufferConfig'/'buf_config' across both dji_perception builds and dji_flight returned nothing. E2 dji_perception does contain a distinct, generic byte-ring-buffer API (ss_byte_buffer_init/_get_head/_get_tail/_commit_read/_commit_write/_get_read_block/_get_write_block) used by its internal ss_dbus/duml_pcie transport layer, but no evidence ties any of those functions to a DUML-facing (cmd_set 0x0a, cmd_id 0x47) entry point specifically -- the name correspondence ('buffer config') is suggestive but not disassembly-confirmed, so not asserted as a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x48 — Eye Get Buffer Config

_Not decoded._ Checked every known DUML registration mechanism on BOTH architectures and found no handler. (1) dji_flight's relocated .data dispatch table: re-derived it directly from raw bytes using the actual R_ARM_RELATIVE relocation offsets (44 relocations, stride 8, vaddr 0xae040..0xae198) rather than trusting the prior doc's byte alignment -- this corrects the row format to {cmd_word:u16 at row-4, cmd_set=byte0, cmd_id=byte1; fn_ptr:u32 reloc'd at row+0}. Decoded all 44 rows; exactly 2 are cmd_set 0x0a (cmd_id 0xDD, fn 0x1da05; cmd_id 0xDE, fn 0x1da55) -- neither is 0x48. Note dji_flight exists ONLY in the E1E (32-bit ARM) image; it is entirely absent from the E2 (aarch64) bin/ directory, so this check is necessarily E1E-only. (2) dji_sys literal duss_event_register_dynamic_command call sites: found via a capstone-based scanner that locates the PLT/import stub address and then brute-force decodes every 2-byte-aligned Thumb/A64 instruction in .text looking for bl/blx targeting it (not a text grep, which is unreliable on stripped ARM32). Found 11 call sites on E1E (vaddrs 0x2db80, 0x498ae, 0x4a23e, 0x4ac16, 0x4ac5c, 0x4be12, 0x4be58, 0x503a8, 0x504a8, 0x51ba2, 0x70064) and 12 on E2 (0x3ebd0, 0x62c00, 0x63790, 0x643a8, 0x6440c, 0x65690, 0x656f4, 0x68dd4, 0x68f70, 0x6cf9c, 0x96f58, 0x96f8c), decoded the preceding literal r1/r2 (cmd_set/cmd_id) operands at each: the full set resolves to cmd_set/cmd_id {0x22/0x60 x4, 0x00/0xa3 x2, 0x06/0x3a x2, 0x04/0x69 x1} plus 2-3 data-driven ('Param Manager') sites with no literal cmd_set/cmd_id -- identical on both architectures, confirming completeness. None is cmd_set 0x0a. (3) dji_perception: imports exactly ONE per-cmd registration primitive in either build -- duss_event_create_client -- and calls it from exactly ONE call site in its entire .text (E1E vaddr 0x63d98c, E2 vaddr 0xe2e3c), confirmed by the same brute-force BL/BLX-target scan. That single call site is reached only for JSON-config route entries whose 16-bit cmd_word passes two hard bound checks, confirmed instruction-identical on both architectures: high byte (cmd_set) < 0x20 (`cmp w1,#0x2000;b.hs reject` / `ldrh.w r1...;cmp.w r1,#0x2000;bhs reject`) AND low byte (cmd_id) < 0x42 (`and w8,w1,#0xfe;cmp w8,#0x42;b.hs reject` / `uxtb r0,r1;cmp r0,#0x42;bhs reject`), backing a compiled-in handler table only 66 slots wide per cmd_set (confirmed by the table stride, 0x210 bytes = 66*8). cmd_id 0x48 (72) exceeds this bound -- dji_perception's build cannot dispatch it via its own primary DUML entry point, regardless of JSON config content. (4) dji_sys also exports a batch-registration helper, duss_register_cmd (E2 vaddr 0x96ef0; this independently reproduces, exactly, a vaddr 0x6fff4 helper already flagged in this project's own commands.json note for an unrelated cmd_set-0x00 command on E1E) that walks an externally-supplied {cmd_set:u16,cmd_id:u16,...,handler:u64} array calling register_dynamic_command per row -- but a full .text BL/BLX-target scan of dji_sys found ZERO internal callers of it on either architecture, and no other binary in either firmware tree imports it either: it is dead code in this build, so it cannot be the actual route for 0x0a. (5) Every other binary across both e1e_extracted and e2_extracted trees that imports any register_dynamic_command/create_client-family symbol was enumerated and checked: dji_sdrs_agent (E1E, 1 data-driven call site, 'SDRS'-prefixed log/USB-diagnostic strings, unrelated to vision), test_rtos_raw (a dji_perception Parameter-Manager QA harness already documented by this project as covering only cmd_set 0x03/0x01), libMipiHandshake.so and libWorkModeLiveview.so (register literal cmd_set 0x09/cmd_id 0xaa, cmd_set 0x09/cmd_id 0xa9, cmd_set 0x02/cmd_id 0xec -- camera/MIPI pipeline, not vision), duml_googletest (E2 test harness, not inspected further as a production registrant). No handler for 0x48 found anywhere. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA3 — Eye Enable SDK Func

_Not decoded._ Identical exhaustive search as cmd_id 0x48 (see that entry for full method/addresses -- same dji_flight table re-derivation, same dji_sys 11/12-call-site literal-immediate enumeration, same dji_perception single-call-site bound-check analysis, same duss_register_cmd dead-code check, same sweep of the 6 other register_dynamic_command/create_client-importing binaries). cmd_id 0xA3 (163) is additionally far outside dji_perception's compiled 0x00-0x41 handler-table range (confirmed on both architectures by the identical `cmp r0/w8,#0x42;bhs reject` bound), and does not match any of dji_sys's literal cmd_ids (0x60, 0xa3-under-cmd_set-0x00-not-0x0a, 0x3a, 0x69) or dji_flight's two cmd_set-0x0a rows (0xDD, 0xDE). One specific false-lead ruled out: cmd_set 0x00 ALSO has a cmd_id 0xA3 ('USB State Report', handler sys_wm260_usb_state_handle, already fully documented in this project) -- confirmed by direct argument decoding (r1/w1=0 for that registration) that this is cmd_set 0x00, not cmd_set 0x0a; the two are a real naming/numbering coincidence, not the same wire command. No handler for cmd_set 0x0a/cmd_id 0xA3 found anywhere. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA4 — Eye Detection Msg Push

_Not decoded._ Same exhaustive registration-mechanism search as 0x48/0xA3 (dji_flight table, dji_sys's 11/12 literal register_dynamic_command call sites, dji_perception's single bound-limited duss_event_create_client call site on each architecture, duss_register_cmd's zero-callers dead-code status, and the 6 other binaries importing any register/create_client symbol) -- no receive-side handler found, and 0xA4 (164) exceeds dji_perception's compiled 0x00-0x41 table range on both architectures exactly like the other three commands. Because the name ('... Msg Push') marks this as a one-way device-to-app PUSH rather than an app-to-device request, also specifically checked the SENDER side, following this project's own established method for push-type commands (as used for cmd_set 0x00's 0x5C/0x58/0x62): grepped the E2 disassembly of dji_perception for the combined 16-bit cmd_word patterns a push would plausibly embed as a literal (0x0aa4 / 0xa40a, in either byte order) near any instruction, and found zero occurrences anywhere in .text. Did not exhaustively trace dji_perception's or dji_sys's dozens of duss_event_send/duss_event_send_sync call sites' argument-construction paths (each push's cmd_set/cmd_id is typically written into a locally-built request struct by pointer, not passed as a literal register argument to the send call itself, per this project's own prior experience on cmd_set 0x00/0x58 and 0x5C, where that same search path was tried at length and still came back inconclusive) -- that remains a concrete, bounded lead for a future pass with more time budget, not something this pass completed. No handler or sender found with confidence. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0xA5 — Eye Get SDK Func

_Not decoded._ Identical exhaustive search as cmd_id 0x48/0xA3 (see those entries for full method/addresses). cmd_id 0xA5 (165) is, like its siblings, far outside dji_perception's compiled 0x00-0x41 handler-table range on both architectures (same `cmp r0/w8,#0x42;bhs reject` bound), does not match any of dji_sys's 11/12 literal register_dynamic_command call sites on either architecture, and does not match either of dji_flight's two cmd_set-0x0a rows (0xDD, 0xDE; dji_flight is E1E-only, absent from the E2 image). duss_register_cmd (the 5th, batch-table registration mechanism) remains confirmed dead code (zero callers, both architectures) and so cannot be the real route either. No handler found for cmd_set 0x0a/cmd_id 0xA5 by any mechanism on either architecture. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.
