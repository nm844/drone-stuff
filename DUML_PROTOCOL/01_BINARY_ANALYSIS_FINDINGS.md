# Binary analysis findings — WM260 firmware package

This covers what was actually inspected in the firmware binaries (as opposed
to what is merely carried over from the public `dji-firmware-tools`
Wireshark dissector / `comm_mkdupc.py`, which is cross-referenced separately
in the per-cmd_set `.md` files). Tooling: `pyelftools` + `capstone` (Thumb/
ARM/AArch64) driven from Python, plus `nm`/`objdump`/`strings`/`7z` (the
last used to read directly from the ext4 `system.img` images without a full
mount/extract).

## 1. Package layout (what's actually in this firmware image)

`V01.00.1000_wm260_dji_system.bin` → `wm260.cfg.sig` + 7 module `.sig` files,
unpacked (`dji_imah_fwsig.py`-style AES+scramble removal) into
`extracted_decrypted/`:

| Module | Type | Role (inferred) | Plaintext after decrypt? |
|---|---|---|---|
| `00_cfg` | CNFG | Firmware package config/manifest | yes (small) |
| `0105_LCPU` | LCPU | A flight-side MCU ("Logic CPU") | **yes** — ARM/Thumb code, `0xAA55AA55` boot magic + build-date string visible |
| `0500_PD_MCU` | BAT2 | Power-distribution MCU | **yes** — clean Cortex-M vector table (`SP=0x20001200`) |
| `0802_WM260_E2` | — | Camera/gimbal payload computer, Android-derived Linux (aarch64) | yes (ext4 `system.img`/`vendor.img`, 512 MiB / 64 MiB) |
| `1100_Battery` | BAT1 | Smart battery MCU | **no** — entropy 7.45/8, no recognizable header; still encrypted or uses a differently-keyed container not handled by the open-source unsigner |
| `1200_ESC_0` / `1202_ESC_2` | ESC0/ESC2 | Motor ESC firmware (redundant pair) | **no** — entropy ≈7.998/8 (indistinguishable from random); still encrypted |
| `1502_WM260_E1E` | — | Main aircraft Linux computer (FC-adjacent, "E1E"), 32-bit ARM, Android-derived | yes (ext4 `system.img`/`vendor.img`, 268 MiB / 150 MiB) |

**Battery and ESC firmware could not be analyzed at the byte level** — they
remain high-entropy blobs after running the same decrypt step that worked for
`00_cfg`/`0105_LCPU`/`0500_PD_MCU`. This is consistent with those two module
*types* (`BAT1`, `ESC0`/`ESC2`) using per-type key material the open-source
`dji_imah_fwsig.py` doesn't have (vs. the generic `UFIE` key path that worked
for the others) — i.e. likely a genuine gap in available keys, not a
tooling bug. Their DUML-level command surface is therefore only documented
here via the **Center Board**'s translation layer (cmd_set 0x05, 0x0D) which
proxies these modules onto the DUML bus — see `cmdset_05_Center_Board.md` and
`cmdset_0d_Battery.md`. What's actually on the wire *between* Center Board
and the battery/ESC chips themselves (likely SMBus/SBS for the battery,
given `dji-firmware-tools/comm_sbs_bqctrl.py` + `comm_sbs_chips/BQ*.py`
target exactly this) was not reverse engineered here.

## 2. Frame format — fully confirmed (see `00_FRAME_FORMAT.md`)

`disasm/binding/deps/libduml_frwk.so` (ARM Thumb-2, EABI5, stripped but with
a full `.dynsym`) exports the actual frame codec:

| Symbol | vaddr | Role |
|---|---|---|
| `CalCrc8` | `0x2559c` | Table-driven CRC-8, confirmed algorithm (see frame doc) |
| `CalCrc16` | `0x255b8` | Table-driven CRC-16, confirmed algorithm |
| `DjiCrc8Table` | `0xfe800` (256 B) | Verified byte-identical to `comm_dat2pcap.py`'s `arr_2A103` |
| CRC16 table | file offset `0xd3100` (found by byte search, not a named symbol) | Verified byte-identical to `comm_dat2pcap.py`'s `crc[]` (standard reflected CRC-16/CCITT) |
| `DJI_Frame_Cap` | `0x25a9e` | The actual byte-stream state machine: finds `0x55`, validates header CRC8, extracts the 10-bit length, validates CRC16 over the whole frame, with seed **`0x3692`** as an inline literal |
| `Frame_Capture` / `Frame_CapByHeadAndLen` | `0x25740`/`0x257de` | Generic delimiter-pair framer (configurable start/end bytes) — a different, more generic framing helper also present in the library, used by other (non-DUML) link types; **not** the DUML v1 parser |

Disassembly of `DJI_Frame_Cap` reproduced in `00_FRAME_FORMAT.md` line by
line; this independently confirms, against actual compiled code rather than
documentation: the SOF byte, the 10-bit/6-bit split of the length/version
field, the header-CRC8-as-resync mechanism, and the CRC16 seed/range.

Byte-pattern search (`DjiCrc8Table`'s 16 leading bytes, then the CRC16
table's leading 16 bytes) was additionally run against the two plaintext raw
MCU dumps:

| File | CRC8 table found at | CRC16 table found at |
|---|---|---|
| `0105_LCPU/module_0105.bin` | `0x47e20` | `0x47f20` |
| `0500_PD_MCU/module_0500.bin` | `0x14c88` | `0x14d88` |

Both tables sit at the same +0x100 relative spacing as in `libduml_frwk.so`,
strongly suggesting a shared source file (`dji_frame.c`/equivalent) compiled
into every target in this product line, Linux and bare-metal MCU alike. This
means the flight-side MCU (LCPU) and the power-distribution MCU both speak
native DUML v1 framing directly on their wire, not just the Linux computers.

The same table search found **no hit** in `1100_Battery`/`1200_ESC_0`/
`1202_ESC_2` — consistent with §1 (still-encrypted) rather than "these don't
speak DUML", since the data is high-entropy throughout.

## 3. Higher-level message bus ("DUSS") layer — found, not fully mapped

Beyond the raw-byte DUML v1 codec, `libduml_frwk.so`/`libduml_hal.so`/
`libduml_util.so` export a large (`duss_*`, `mb_*`) API surface implementing
an internal pub/sub **message bus** over many transports (`mb_uart_channel_recv`,
`mb_usb_channel_recv`, `mb_i2c_channel_recv`, `mb_can_channel_recv`,
`mb_spi_channel_recv`, `mb_wl_channel_recv`, `mb_ip_channel_recv`, ...) with
dynamic command registration (`duss_event_register_dynamic_command_table`,
`duss_event_register_dynamic_command`). This is the plumbing that application
daemons (`dji_sec`, `dji_camera3`, `dji_sys`, `dji_dcs`, `dji_hms`, `dji_mb_ctrl`,
...) use internally; raw DUML-v1-framed bytes coming off a physical link are
decoded once (by `DJI_Frame_Cap` or equivalent) and then redistributed as
message-bus events to whichever daemon subscribed to that `cmd_set`. The
per-daemon runtime registration tables (which would give an exact, binary-
verified enumeration of exactly which `cmd_id`s each daemon on *this specific
aircraft* responds to) were not extracted — the daemons (`dji_camera3` etc.)
are small, stripped, position-independent executables with no exported
symbols for this, and resolving the registration-table contents would
require full control-flow decompilation per daemon, which was out of scope
for this pass. Flagged as the main place a deeper follow-up would add value.

## 4. Camera payload computer (`0802_WM260_E2`) cross-check

Extracted directly from `unzipped/system.img` (a genuine ext4 filesystem,
read via `7z x` without mounting) for inspection:

- `lib64/libduml_frwk.so` — same framework library as the aircraft computer,
  aarch64 build this time (1.5 MB vs 1.0 MB on the 32-bit side — more
  features compiled in, consistent with this being the newer/larger image).
- `lib64/libduml_hal_cam.so` — a **camera hardware-abstraction layer**
  (`cam_manager_*`, `camdev_*`, `dcam_*`: sensor/stream/exposure/metadata
  pipeline control). This is the layer *above* raw sensor I/O and *below*
  the DUML-facing daemon; it is not itself a DUML command parser.
- `bin/dji_camera3` — the actual camera-control daemon (aarch64 PIE, fully
  stripped, only 9 dynamic symbols — no exported command table to read
  without full decompilation). Strings extraction found literal parameter
  identifiers consistent with the public Camera command set's semantics:
  `aperture`, `shutter_speed`, `shutter_angle`, `shutter_type`, `focus_mode`,
  `iso_auto_max`, `recording_streams` — independent confirmation that the
  real camera control surface on this exact aircraft matches the kind of
  settings the community `dji-dumlv1-camera.lua` dissector documents for
  cmd_set 0x02, even though the exact numeric `cmd_id` mapping inside
  `dji_camera3` wasn't extracted.
- `bin/dji_sec`, `bin/dji_amt` are also present on this image (64-bit builds
  of the same binding/security daemons analyzed earlier in
  `disasm/binding/ANALYSIS.md`, which covers the 32-bit E1E versions).

## 5. What this means for the per-cmd_set documentation

The per-`cmd_set` `.md` files in this directory are generated from the public
`dji-firmware-tools` Lua dissector + `comm_mkdupc.py` definitions (see
`README.md` for the extraction method) — i.e. they are the best available
**documentation of the command *names*, numeric IDs, and payload byte
layouts** across the whole DJI product line's history, which the WM260 wire
format (confirmed above) is 100% compatible with. What this binary analysis
pass adds on top:

- Hard confirmation that the wire format itself is unchanged in this
  firmware generation (§2).
- Confirmation that the flight-side MCU and power-distribution MCU firmware
  genuinely implement this exact codec (§2).
- Confirmation that the real camera-control daemon on this exact airframe
  uses parameter semantics consistent with the documented Camera command set
  (§4).
- An honest accounting of what remains unverified: the literal per-daemon
  `cmd_id` registration tables (§3), and the Battery/ESC firmware contents
  (§1), neither of which could be pulled out of this specific package with
  the tooling/keys available in this session.
