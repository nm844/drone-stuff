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
3. **`INDEX.md`** — table of all 18 command sets with command counts.
4. **`cmdset_XX_Name.md`** — one file per command set (General, Camera,
   Flight Control, Gimbal, Center Board, Remote Control, Wi-Fi, DM36x,
   HD Link, Mono/Binocular, Simulator, ESC, Battery, Data Logger, RTK,
   Automation, ADSB, Special). Each lists every known `cmd_id`, its name,
   and — where the source dissector decodes it — a byte-exact table of
   offset / size / field name / type / enum / bitmask / description.

## Totals

- **877** known `(cmd_set, cmd_id)` pairs documented by name across 18 command
  sets (884 reported in an earlier pass of this doc was inflated by a
  handful of hex-case duplicate keys — e.g. `0x0A` and `0x0a` both present
  in the source tables — now deduplicated by integer value).
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
  ground-truth.
- Frame header: **100% byte-level confirmed** against this exact firmware's
  compiled code (not inferred).
- A runnable Python implementation of all of the above — frame codec,
  command registry, payload encode/decode, and serial/TCP send+receive — is
  in [`../duml_py/`](../duml_py/README.md). Every one of the 877 commands is
  registered by name and sendable/receivable there; the other 720 (no known
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
  of the 884 is actually *reachable* on this specific airframe/firmware
  revision (vs. being a command another DJI product in the dissector's
  multi-product history supports) was not individually confirmed.
- Some payload fields are named `unknownN` / have no enum decode in the
  upstream dissector — that reflects the true state of community knowledge,
  not something this pass could resolve without live traffic capture or
  deeper per-field disassembly.
