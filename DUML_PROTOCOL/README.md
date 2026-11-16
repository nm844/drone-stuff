# DUML Protocol Reference — WM260 firmware package

A complete byte-by-byte breakdown of the DJI DUML v1 wire protocol and every
known command/payload, built for the firmware in this project
(`V01.00.1000_wm260_dji_system.bin` and its 7 decrypted modules).

## Read order

1. **`00_FRAME_FORMAT.md`** — the 11-byte header + CRC16 trailer, every bit
   of every multi-field byte, both CRC algorithms with their tables,
   **independently confirmed by disassembling this firmware's own
   `libduml_frwk.so`** (not just quoted from documentation).
2. **`01_BINARY_ANALYSIS_FINDINGS.md`** — what was actually inspected in the
   firmware binaries: which modules could be decrypted, which implement the
   protocol natively, what the real camera-control daemon's parameters look
   like, and an honest list of what remains unverified (Battery/ESC firmware
   contents; per-daemon runtime command-registration tables).
3. **`INDEX.md`** — table of all 21 command sets with command counts.
4. **`cmdset_XX_Name.md`** — one file per command set (General, Camera,
   Flight Control, Gimbal, Center Board, Remote Control, Wi-Fi, DM36x,
   HD Link, Mono/Binocular, Simulator, ESC, Battery, Data Logger, RTK,
   Automation, ADSB, Special, plus `0x22` Demo Mode, `0x23` Smart, and
   `0x51` Route Switch — the latter three found by this project's own
   binary RE, not the public dissector). Each lists every known `cmd_id`,
   its name, and —
   where the source dissector decodes it, or this project's own binary
   disassembly established it — a byte-exact table of offset / size /
   field name / type / enum / bitmask / description, or a purpose /
   evidence / confidence writeup for binary-RE'd entries.
5. **`BINARY_COVERAGE_TRACKER.md`** — not a findings doc, a living status
   tracker: which of the 808 binaries/libraries across both firmware
   images have been checked for undiscovered DUML command registrations,
   which haven't, why, and the reproducible methodology/tooling gotchas
   behind the checks. Start here before launching a new sweep so you
   don't redo already-done work or repeat a known false-negative.

## Totals

- **898** known `(cmd_set, cmd_id)` pairs documented by name across 19
  non-empty command sets (of 21 catalogued in total; the other 2,
  `0x0c`/ESC and `0x10`/Automation, are confirmed-empty with an
  architectural explanation rather than unexamined — see
  `cmdset_0c_ESC.md`/`cmdset_10_Automation.md`). (An earlier pass of
  this doc reported 884 for a different reason — a handful of hex-case
  duplicate keys, e.g. `0x0A` and `0x0a` both present in the source tables,
  inflating what was really 877 at the time; that was deduplicated by
  integer value. The 884 that followed was genuinely larger: 7 commands
  across 2 entirely new cmd_sets — `0x22` and `0x51`, both outside the
  public dissector's 0x00-0x11 range — found by binary disassembly of a
  WM260/Mavic 3 image rather than from any known capture; see
  `04_WM260_DAEMON_FINDINGS.md`. A later pass took this to **888**: 4 more
  cmd_ids under `0x22` specifically — `0x06`/`0x07`/`0x08`/`0x44`, all 4
  found inside `dji_flight` rather than `dji_sys` — recovered by an
  independently-verified follow-up pass (see
  `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track H and `cmdset_22_Demo_Mode.md`),
  plus 5 cmd_ids that were already present in `commands.json`/
  `ALL_COMMANDS.csv` but had never been rendered into their per-cmd_set
  `.md` file — `0x00`'s `0x2F`/`0x89`/`0xA3`/`0xAA` and `0x04`'s `0x69`.
  The current **898** adds 10 more commands found by an exhaustive
  follow-up sweep of 24 previously-unexamined WM260 binaries/libraries
  (16 with a strong relocation-based registration signal, 8 secondary
  candidates), every one independently reverify-confirmed by 3 skeptical
  passes each: 4 under `0x00` (`0x83`/`0x85`/`0x93`/`0x94`, all in the
  `upgrade_test` firmware-upgrade CLI), 1 under `0x02` (`0xEC`, in
  `libWorkModeLiveview.so`), 2 under `0x09` (`0xA9`/`0xAA`, split across
  `libWorkModeLiveview.so` and `libMipiHandshake.so`), and 3 under a
  brand-new cmd_set — `0x23` "Smart" (`0x20`/`0x21`/`0x22`, a DSP/
  co-processor ownership-arbitration bus independently confirmed in two
  different binaries via two different registration mechanisms). See
  `16_EXHAUSTIVE_SWEEP_FINDINGS.md` and `cmdset_23_Smart.md`. One further
  candidate (`0x00`/`0x84`) was investigated with equally solid
  mechanism-level evidence but did not clear the reverify bar — a
  majority of reviewers flagged the original write-up's file-scope claim
  as overstated — and was deliberately left uncatalogued rather than
  added on a technicality; see `16_EXHAUSTIVE_SWEEP_FINDINGS.md` for the
  full reasoning.)
- **157** of those have a full, *non-empty* byte-level payload decode
  (offset/size/type for every field). This is a stricter count than an
  earlier pass used: a command only counts here if its dissector function
  actually extracts at least one field — several dissector functions in the
  upstream Lua are stubs (a commented-out field, just an offset-sanity
  assertion) that an earlier, looser "has *a* dissector function" count
  mistakenly credited as decoded. Of the 157: 155 come straight from the
  Lua dissector, and **2 are new this pass** — reverse engineered by
  cross-referencing the DJI *flight-recorder* log-file dissectors
  (`dji-p3-flyrec-proto.lua`, `dji-mavic-flyrec-proto.lua`), which happen to
  log the exact same wire structs as some live push commands, and then
  **added to the actual Wireshark dissector** (`dji-dumlv1-proto.lua`'s
  `battery_push_common_info_dissector` for Battery/0x06, and
  `dji-dumlv1-flyc.lua`'s `flyc_battery_status_dissector` for Flight
  Control/0x0A). Both are marked `source: flyrec_crossref` wherever they
  appear and flagged as a *candidate* mapping (by cmd_id name match, not
  independently confirmed against live WM260 traffic) rather than
  ground-truth. None of the 4 newly-added `0x22` cmd_ids or the 5
  gap-fix entries above have a byte-level payload decode — all 9 are
  name/handler-confirmed only, so this 157 figure is unchanged.
- Frame header: **100% byte-level confirmed** against this exact firmware's
  compiled code (not inferred).
- A runnable Python implementation of all of the above — frame codec,
  command registry, payload encode/decode, and serial/TCP send+receive — is
  in [`../duml_py/`](../duml_py/README.md). Every one of the 898 commands is
  registered by name and sendable/receivable there; the other 741 (no known
  payload layout) send/receive as raw bytes.

## Methodology — "use dji-firmware-tools as a template, but verify against the binaries"

This was built in two passes, matching that brief:

**Pass 1 — extract the complete command/payload structure from the public
reference implementation**, rather than reading the ~43,000 lines of
Wireshark Lua dissector (`dji-firmware-tools/comm_dissector/wireshark/
dji-dumlv1-*.lua`) by hand. A small Python parser
(`parse_lua.py`/`render_docs.py`, included in this delivery as
`tools/` is not shipped here but the method is documented so it's
reproducible) walks the Lua source and:
  - extracts every `ProtoField` definition (name, Wireshark type, enum
    table, bitmask, free-text description),
  - extracts every per-command-set `*_CMD_TEXT` (ID → name) and
    `*_CMD_DISSECT` (ID → payload-decoder-function) table,
  - symbolically replays each decoder function's `offset = offset + N`
    arithmetic (handling `if pack_type == 0 / else` Request-vs-Response
    branches, and nested `if payload:len() >= N` optional-tail branches,
    each restarting its own offset count from the branch point) to
    reconstruct the exact byte layout each function describes.

  This is **more reliable than manual transcription** for a codebase this
  large and this mechanically regular, and it was cross-checked by hand
  against several dozen individual functions during development (three bugs
  found and fixed this way: a byte-doubling bug, a Request/Response branch
  offset leak, and a comment-stripping regex bug that dropped ~5 fields).
  Additional payload structs present only in `comm_mkdupc.py` (the project's
  ctypes-based DUML packet builder, which independently documents some
  payloads in more structured form, including the newer 2017-era flight-
  parameter protocol) were appended by hand as appendices to the General and
  Flight Control files.

**Pass 2 — verify against the actual firmware binaries**, per
`01_BINARY_ANALYSIS_FINDINGS.md`: disassembled the real CRC/frame-validation
functions out of `disasm/binding/deps/libduml_frwk.so` (ARM Thumb-2, via
`pyelftools` + `capstone`), confirmed both CRC tables byte-for-byte and the
CRC16 seed as an inline literal, located the same CRC tables inside two raw
MCU firmware dumps in this package, and pulled the camera-control daemon
(`bin/dji_camera3`) directly out of the 0802 module's ext4 `system.img`
(via `7z`, no mount needed) to cross-check its real parameter names against
the documented Camera command set.

## Known gaps (stated plainly, not glossed over)

- **Battery (`1100_Battery`) and ESC (`1200_ESC_0`/`1202_ESC_2`) firmware
  are still high-entropy/encrypted** after the same decrypt step that
  worked on the other modules — their internal command handling could not
  be inspected. Their DUML-bus-visible behavior is covered via the Center
  Board's proxy commands (cmd_set 0x05, 0x0D) in the relevant `.md` files,
  but what's on the wire *between* Center Board and these chips was not
  reverse engineered (likely SMBus/SBS for the battery; see
  `comm_sbs_bqctrl.py`/`comm_sbs_chips/` in `dji-firmware-tools` for that
  separate protocol).
- The exact runtime **per-daemon `cmd_id` registration tables** (which would
  let you say definitively "`dji_camera3` on this exact firmware answers
  these and only these camera commands") were not extracted — this would
  require full decompilation of several stripped PIE executables, which
  was out of scope for this pass. The command *names and payload layouts*
  documented here are accurate as a protocol reference; whether every one
  of the 898 is actually *reachable* on this specific airframe/firmware
  revision (vs. being a command another DJI product in the dissector's
  multi-product history supports) was not individually confirmed.
- Some payload fields are named `unknownN` / have no enum decode in the
  upstream dissector — that reflects the true state of community knowledge,
  not something this pass could resolve without live traffic capture or
  deeper per-field disassembly.
