# `dji_flight`'s full `.data` command table — re-acquired, independently re-derived, and found to be larger than this project's own prior estimate

A follow-up pass on the `.data`-array lead `cmdset_22_Demo_Mode.md` and
`08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` both flagged as unfinished:
only 4 of the array's rows had ever been decoded. The two documents
disagreed with each other on the array's own boundaries, and that
disagreement had never been reconciled: `cmdset_22_Demo_Mode.md`'s own
"Known gap" note called the array "rooted at vaddr `0xae0f8`... continu[ing]
for at least 43 records total (vaddr `0xae0f8`–`0xae190`)" — a
self-contradictory claim on its own terms, since `0xae0f8`–`0xae190` is
only 20 rows of 8 bytes each, not 43. `14_FOLLOWUP_DEEPDIVE_FINDINGS.md`
(Track H), by contrast, already had the internally-consistent version of
this fact on record: the array "continues for at least 43 records
spanning vaddr `0xae040`–`0xae190`" — i.e. the correct starting address
was already published in this project, just never carried into
`cmdset_22_Demo_Mode.md`'s own gap note, and every one of those 39 extra
rows was explicitly left as "Not determined" there.

This pass re-derived the array's boundaries independently from raw bytes
and relocations (not by picking one prior document's claim over the
other) and confirms `14_FOLLOWUP_DEEPDIVE_FINDINGS.md`'s number: **43
rows, `0xae040`–`0xae190`**. This document's real new contribution is
everything that document's own "Not determined" left open: actually
decoding all 39 previously-unresolved rows' contents, resolving handler
names, and disassembling each one — none of which had been done before
this pass.

## Scope and what's new here

- Re-acquired and re-decrypted the WM260 firmware from scratch (nothing
  carried over from any prior session's extracted files — this project's
  containers don't persist extracted firmware between sessions; see
  `02_WM265_MAVIC3_NFZ_FINDINGS.md` §4c for why that's the expected
  pattern, not a problem).
- Independently re-walked every `R_ARM_RELATIVE` relocation in `dji_flight`'s
  `.data` section from raw bytes, rather than trusting any single prior
  document's claim about the array's boundaries — this is what settled
  the `cmdset_22_Demo_Mode.md`-vs-`14_FOLLOWUP_DEEPDIVE_FINDINGS.md`
  disagreement in the latter's favor.
- Resolved names for the table's handler functions using a **new
  technique for this project**: this binary has no `.gnu_debugdata`
  (unlike `dji_sys`, which is where that technique originates in
  `04_WM260_DAEMON_FINDINGS.md`) — only a `.gnu_debuglink` pointing at a
  companion debug file that doesn't exist anywhere in the firmware tree.
  Names were instead recovered by disassembling each handler's own
  `_LOGD("%s: ...", __FUNCTION__, ...)`-style self-identifying log call
  and resolving the PC-relative literal-pool string it loads — validated
  first against the 4 already-known handlers (all 4 resolved to their
  exact existing names, with no prompting, before trusting the method on
  anything new).
- Disassembled every new row's handler to characterize what it does with
  its payload, and traced the shared dispatcher every `api_wp2_*`-family
  trampoline tail-calls into, recovering a reusable byte-level anchor for
  this binary's generic inbound-command context struct.
- Confirmed `dji_flight` does not exist at all in the E2 (aarch64,
  camera/gimbal payload computer) firmware build — a clean negative, not
  an unexamined gap.

## 1. Acquisition and decryption (redone from scratch)

WM260 `V01.00.1000` (2022-12-09), pulled via `dankdronedownloader.com`.
The flow documented in `02_WM265_MAVIC3_NFZ_FINDINGS.md` §4c (GET-style
`download/preview`/`download/start` with query params) is stale; the live
site now serves everything under `/DDD2/app/` and both steps are POSTs:

```
POST https://www.dankdronedownloader.com/DDD2/app/download/preview
     brand=DJI&model=wm260&version=01.00.1000&category=Aircraft
  -> HTML page, hidden field dl_sha256=230EA6BA1A1D3D9E63048D0E541B1D54C57CFD32CE1A767AD771AA1D36E8443E
POST https://www.dankdronedownloader.com/DDD2/app/download/start
     dl_sha256=<that value>&client_id=
  -> 428,830,720-byte octet-stream, V01.00.1000_wm260_dji_system.bin
```

Downloaded file sha256 matched the preview page's advertised hash exactly
(`230ea6ba1a1d3d9e63048d0e541b1d54c57cfd32ce1a767ad771aa1d36e8443e`). The
preview page also showed `Anti-Rollback 2`, `DJI Code wm260`, and release
notes mentioning "Added Waypoint Flight" — consistent with the genuine
package.

Decrypted with `o-gs/dji-firmware-tools`' `dji_imah_fwsig.py` (cloned fresh
for tooling, not redistributed here):

| Module | Key pair | Result |
|---|---|---|
| `1502` (E1E, main aircraft computer) | `PRAK-2020-01` / `UFIE-2020-04` | signature verified, decrypted-chunk checksum `0xEEDE3CAD` matched — clean, not forced |
| `0802` (E2, camera/gimbal computer) | `PRAK-2021-09` / `UFIE-2021-08` | signature verified, checksum `0xAD618E04` matched — clean, not forced |

Both decrypted payloads are Android OTA signed zips carrying block-OTA
SDAT images (`system.new.dat[.br]`/`vendor.new.dat[.br]`); rebuilt into
flat ext4 images with a from-scratch `sdat2img.py` (transfer-list v3) and
extracted directly with `7z x` (no mount needed — same no-mount technique
`01_BINARY_ANALYSIS_FINDINGS.md` used). Produced image sizes matched that
document's prior records exactly (268,419,072 / 150,994,944 bytes for E1E;
536,870,912 / 67,108,864 for E2 — the "256 MiB" vs "268 MiB" difference in
the old doc is just MiB-vs-rounded-decimal, same byte count).

## 2. Locating `dji_flight`

- **E1E:** `bin/dji_flight` (no `system_files/` prefix in the real image —
  that prefix was apparently just an ad hoc wrapper-directory name from
  however a prior session organized its own scratch extraction, not a
  real firmware path). `sha256`:
  `9367d43daccdeed15dfa3034edfd91d2cf1e0bdc0dc2e28f5183dc744637a8ad`.
  `file`: ELF32 LSB, ARM, EABI5, dynamically linked (`/system/bin/linker`
  interpreter), stripped. `readelf -h`: `Type: DYN`.
- **E2:** absent entirely. An exhaustive `find` over both fully-extracted
  `system.img` and `vendor.img` (554 files in `bin/` alone) found no file
  named `dji_flight` or matching `*flight*` anywhere. E2's `bin/` is
  dominated by camera/vision/ISP daemons (`dji_camera3`, `dji_perception`,
  `dji_dsp_load`, `dji_nn_server`, `dji_mb_ctrl`, ...) with no
  flight-control-family binary at all — architecturally consistent with
  E2's role as the camera/gimbal payload computer, not a search failure.
  Unlike the `libduml_frwk.so`/Route-Switch precedent in
  `04_WM260_DAEMON_FINDINGS.md` (same library, same table, present in both
  E1E and E2 builds at different addresses), there is no "same binary,
  different build" comparison to make here — `dji_flight` is E1E-only by
  design.

## 3. The table: corrected boundaries, 43 rows, fully decoded

`readelf -S` shows `dji_flight` has a `.gnu_debuglink` (literal string
`"dji_flight"` + a CRC), **not** a `.gnu_debugdata` — a different, weaker
mechanism than `dji_sys`'s minidebuginfo. No companion unstripped file by
that name was found anywhere in the firmware tree, so minidebuginfo-based
name resolution (this project's usual first move on a stripped binary)
was not available at all for this specific binary; see §5 for what was
used instead.

Restricting `readelf -r`'s `R_ARM_RELATIVE` output to the `.data` section
(`Addr=0xae000`/`Off=0xad000`, i.e. `file_offset = vaddr - 0x1000`
throughout) and sorting by address: a relocated word sits at **every
multiple of 8 from `0xae040` through `0xae190` inclusive**, with the
intervening (odd-multiple-of-4) word at each row never relocated —
exactly the `{func_ptr(reloc), cmd_word(plain)}` 8-byte-row shape this
project already established for the 4 known rows. At `0xae198` the stride
breaks to 4 (every word relocated) — a structurally different plain
pointer array, not this table. That upper boundary (`0xae190` being the
last row, `0xae198` being something else) is confirmed correct.

**The lower boundary is not `0xae0f8` — it's `0xae040`, 23 rows earlier.**
Full raw-byte decode of every row, `0xae040`–`0xae190` (43 rows):

```
vaddr     raw bytes(LE)        func_ptr    cmd_word    set   id
0xae040   2110020000070000     0x00021021  0x00000700  0x00  0x07
0xae048   790d020000080000     0x00020d79  0x00000800  0x00  0x08
0xae050   d508020000090000     0x000208d5  0x00000900  0x00  0x09
0xae058   a90b0200000a0000     0x00020ba9  0x00000a00  0x00  0x0a
0xae060   35060200000b0000     0x00020635  0x00000b00  0x00  0x0b
0xae068   b1080200000c0000     0x000208b1  0x00000c00  0x00  0x0c
0xae070   3d0d02001f110000     0x00020d3d  0x0000111f  0x1f  0x11
0xae078   150e020003ea0000     0x00020e15  0x0000ea03  0x03  0xea
0xae080   d509020000000000     0x000209d5  0x00000000  0x00  0x00
0xae088   750f010000010000     0x00010f75  0x00000100  0x00  0x01
0xae090   b50e0100033f0000     0x00010eb5  0x00003f03  0x03  0x3f
0xae098   cd9a010003c10000     0x00019acd  0x0000c103  0x03  0xc1
0xae0a0   4d14010003cd0000     0x0001144d  0x0000cd03  0x03  0xcd
0xae0a8   5d98010003db0000     0x0001985d  0x0000db03  0x03  0xdb
0xae0b0   c1a5010011010000     0x0001a5c1  0x00000111  0x11  0x01
0xae0b8   c1d5000011020000     0x0000d5c1  0x00000211  0x11  0x02
0xae0c0   21d7000011140000     0x0000d721  0x00001411  0x11  0x14
0xae0c8   259d010011200000     0x00019d25  0x00002011  0x11  0x20
0xae0d0   55a0010011050000     0x0001a055  0x00000511  0x11  0x05
0xae0d8   3902010022010000     0x00010239  0x00000122  0x22  0x01
0xae0e0   ddba010022020000     0x0001badd  0x00000222  0x22  0x02
0xae0e8   c5ac010022030000     0x0001acc5  0x00000322  0x22  0x03
0xae0f0   31b8010022050000     0x0001b831  0x00000522  0x22  0x05
0xae0f8   79b1010022060000     0x0001b179  0x00000622  0x22  0x06   <- pre-existing (Set Global Cruise Vel)
0xae100   b1b1010022070000     0x0001b1b1  0x00000722  0x22  0x07   <- pre-existing (Get Global Cruise Vel)
0xae108   41b1010022080000     0x0001b141  0x00000822  0x22  0x08   <- pre-existing (Pause Recovery)
0xae110   c5b8010022090000     0x0001b8c5  0x00000922  0x22  0x09
0xae118   25ad0100220d0000     0x0001ad25  0x00000d22  0x22  0x0d
0xae120   1db40100220e0000     0x0001b41d  0x00000e22  0x22  0x0e
0xae128   4db4010022170000     0x0001b44d  0x00001722  0x22  0x17
0xae130   e9b1010022440000     0x0001b1e9  0x00004422  0x22  0x44   <- pre-existing (Break Restore Waypoint Fly)
0xae138   21b2010022180000     0x0001b221  0x00001822  0x22  0x18
0xae140   a9e2010022190000     0x0001e2a9  0x00001922  0x22  0x19
0xae148   fde20100221a0000     0x0001e2fd  0x00001a22  0x22  0x1a
0xae150   fde30100221e0000     0x0001e3fd  0x00001e22  0x22  0x1e
0xae158   49e301001f050000     0x0001e349  0x0000051f  0x1f  0x05
0xae160   61b80100041c0000     0x0001b861  0x00001c04  0x04  0x1c
0xae168   75d8010004f10000     0x0001d875  0x0000f104  0x04  0xf1
0xae170   c5d8010002800000     0x0001d8c5  0x00008002  0x02  0x80
0xae178   15d9010002810000     0x0001d915  0x00008102  0x02  0x81
0xae180   65d9010002870000     0x0001d965  0x00008702  0x02  0x87
0xae188   b5d901000add0000     0x0001d9b5  0x0000dd0a  0x0a  0xdd
0xae190   05da01000ade0000     0x0001da05  0x0000de0a  0x0a  0xde
0xae198   55da0100b4390900     0x0001da55  0x000939b4  <- pattern breaks (nonsense cmd_set, AND relocation stride changes to 4): confirmed not part of the table.
```

Rows `0xae0f8`–`0xae190` match the prior pass's 20-row list exactly — that
part was accurate. The error was treating `0xae0f8` as the table's start.
**Real extent: `0xae040`–`0xae190`, 43 rows.** Of these, 4 were already
documented (`0x22`/`0x06`, `0x07`, `0x08`, `0x44`); **39 are new or
newly-attributed**, listed by cmd_set in §6. This independently confirms
— rather than refutes — `cmdset_22_Demo_Mode.md`'s original "at least 43
records total" estimate and `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md`'s
own passing mention that a later pass had "shown [the array] to continue
for 43+ records total."

### Which rows are genuinely new vs. handler-confirmations of existing cmd_ids

Checked against both `ALL_COMMANDS.csv` and the actual `cmdset_*.md` files,
not just the CSV:

| cmd_set | Already-documented ids in this table (handler confirmation only) | Genuinely new ids |
|---|---|---|
| `0x00` General | `0x00,0x01,0x07,0x08,0x09,0x0a,0x0b,0x0c` (all 8) | — |
| `0x02` Camera | `0x80,0x81,0x87` (all 3) | — |
| `0x03` Flight Control | `0x3f,0xcd,0xea` (3) | `0xc1,0xdb` (2) |
| `0x04` Gimbal | `0x1c` (1, already doubly-ambiguous — see below) | `0xf1` (1) |
| `0x0a` Vision | — | `0xdd,0xde` (2) |
| `0x11` ADSB | `0x02,0x14` (2) | `0x01,0x05,0x20` (3) |
| `0x22` Demo Mode | `0x06,0x07,0x08,0x44` (4) | `0x01,0x02,0x03,0x05,0x09,0x0d,0x0e,0x17,0x18,0x19,0x1a,0x1e` (12) |
| `0x1f` (brand new cmd_set) | — | `0x05,0x11` (2) |

`0x1f` does not exist anywhere in `ALL_COMMANDS.csv` or `INDEX.md` as a
cmd_set number (`cut -d',' -f1 ALL_COMMANDS.csv | sort -u` confirms) — it
is a genuinely new cmd_set, and carries 2 unrelated cmd_ids, not 1 (see
§6). `0x04`'s `0x1c` was already flagged in `cmdset_04_Gimbal.md` as
having two pre-existing duplicate headings from the public dissector; this
row is a third, independent data point on that same already-ambiguous
cmd_id, not a resolution of the ambiguity.

Net new `(cmd_set, cmd_id)` pairs added to the project total: **22** (12
under `0x22`, 3 under `0x11`, 2 under `0x03`, 2 under `0x1f`, 1 under
`0x04`, 2 under `0x0a`).

## 4. Name resolution method

No `.gnu_debugdata`/symtab available (see §3). Instead: essentially every
function in this table is compiled with a `_LOGD("%s: ...", __FUNCTION__,
...)`-style macro whose arguments are PC-relative literal-pool strings
(the classic PIC `ldr rX,[pc,#n]` then `add rX,pc` idiom — the literal
itself carries no relocation, so it has to be recovered by disassembling
and replaying that instruction pair, not read directly off the relocation
table). A Capstone (`CS_ARCH_ARM`,`CS_MODE_THUMB`)-based script walked each
function tracking per-register literal loads and resolving the absolute
string address on the matching `add`.

**Validated first against all 4 already-known handlers** before trusting
it on anything new:

| known func | resolved name | matches existing doc? |
|---|---|---|
| `0x1b179` | `api_wp2_set_global_cruise_vel` | yes, exact |
| `0x1b1b1` | `api_wp2_get_global_cruise_vel` | yes, exact |
| `0x1b141` | `api_wp2_pause_recovery` | yes, exact |
| `0x1b1e9` | `api_wp2_break_restore_waypoint_fly` | yes, exact |

All 4 resolved to the exact pre-existing name, unprompted — the basis for
trusting this method on the 39 new rows.

**Two error modes found and corrected during the pass, not swept past:**

1. A few computed string addresses landed 1-3 bytes into `.rodata`
   alignment padding next to the real string, truncating it to garbage —
   caught and fixed by hand-checking raw bytes around every miss.
2. For the larger rows, bounding a disassembly window by "next known
   table address" repeatedly over-ran into **other, unregistered
   functions** that happen to sit between two table entries in memory —
   one row's naively-bounded window spanned ~8.7KB and actually contained
   one small real function plus a dense cluster of unrelated helper
   functions. **Only the first ~20-40 instructions at each row's own entry
   point are reported as pertaining to that row** in §6; anything found
   further into an over-long window, especially after an obvious topic
   shift, is called out explicitly as likely belonging to a different,
   unregistered neighbor — not claimed as that row's own behavior. A
   rigorous pass would trace real `pop`/`bx lr`/tail-branch exits to find
   each function's true end instead of relying on row spacing; that was
   not done here for all 39 rows.

## 5. Common calling convention for the `api_wp2_*` trampoline family

Every verified `api_wp2_*`-style row (push 3 incoming args into
`r5`/`r6`/`r7`, load 2 PC-relative strings + 1 GOT-indirect descriptor
pointer, `bl` a shared logger at `0x21110`, tail-`b.w` into a shared
dispatcher at `0x1b3ac`) funnels through that one shared dispatcher, which
was disassembled directly: it null-checks its 2nd argument and returns `0`
if null; otherwise reads a **pointer field at `arg0+0x8`** and a **uint16
length field at `arg0+0xc`** from that argument, plus 2 bytes from the
per-command descriptor (almost certainly the registered `cmd_set`/`cmd_id`
bytes themselves) for a generic registration/telemetry call, then
`blx`-dispatches through a vtable-like slot on the descriptor to the
actual per-command implementation, forwarding the original arguments
unchanged.

**Net effect:** every function reachable through this array is invoked as
`handler(descriptor_ptr, request_ctx_ptr, arg2, arg3)`, where
`request_ctx_ptr` exposes a **payload pointer at offset `+0x8`** and a
**16-bit payload length at offset `+0xc`** — a reusable byte-level anchor
for this binary's generic inbound-command context struct, at least for
everything reachable through this specific array. How `request_ctx_ptr`
itself gets built from a raw wire frame was not traced (out of scope here).

## 6. Per-row findings, by cmd_set (39 new/newly-attributed rows)

Confidence key: **high** = clean, repeated, unambiguous self-name string
at entry; **medium** = name found once, or some attribution uncertainty;
**low** = no name string, purpose inferred from nearby log text or raw
control flow only.

### `0x00` General — all 8 ids already documented; dji_flight routes them all into NFZ-database-upgrade internals

- **`0x00` Ping** — func `0x209d4` (~468B). Internal name
  `check_version_need_update` (high, repeats 4×). Reads a `[%d.%d.%d.%d]`
  version struct from a "database" file and compares it.
- **`0x01` Version Inquiry** — func `0x10f74` (~1240B, largest of this
  group). Internal name `fc_db_init` (high, "fc_db_init start"/"fc_db_init
  success"), plus `check_print_db`. Unrelated-looking strings
  (`"APP:[%d](%f,%f)"`, `"drone_takeoff_alti:%f"`) appear late in the
  disassembly window — per the §4 caveat, likely a separate neighboring
  function, not claimed as part of this row.
- **`0x07` Enter Loader** — func `0x21020` (~400B). `nfz_upgrade_get_version`
  (medium).
- **`0x08` Update Confirm** — func `0x20d78`. `nfz_upgrade_entry` (medium).
- **`0x09` Update Transmit** — func `0x208d4`. `nfz_upgrade_start` (high,
  clean, repeats).
- **`0x0a` Update Finish** — func `0x20ba8`. `nfz_upgrade_data` (medium).
  Log context: `"it is first packet, need to check revertable of databse"`
  (sic).
- **`0x0b` Reboot Chip** — func `0x20634` (~636B). `nfz_upgrade_end` (high,
  repeats twice) — also directly reads/writes `/nfz_data/NFZ/nfz.bin` and
  `/nfz_data/NFZ/nfz_backup.bin`, with explicit MD5 comparison
  (`check_file_data_md5_final`, `"the md5 code calculate from the file"`
  vs `"the md5 code received from the api"`).
- **`0x0c` Get Device State** — func `0x208b0` (36B, tiny). No clean
  self-name (shares a generic `"ack_result, ret_code %d, ack_buf_len %d\n"`
  format string with the next function) — low confidence on the name, but
  that format string is itself a solid payload-shape clue: an ack result
  code (int) plus an ack buffer length (int).

**Cross-cutting finding, corroborated by an existing doc:** every `0x00`
command here is wired to the aircraft's **NFZ (no-fly-zone) database
update machinery** — `/nfz_data/NFZ/nfz.bin` /
`/nfz_data/NFZ/nfz_backup.bin`, MD5-verified, version-compared against a
"database" header. This matches, exactly, the embedded source path
`08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` already found compiled into
this same binary — `hardware/dji/service/flight/src/applications/
nfz_data_upgrade/upgrade_debugger/src/upgrade_debugger.cpp` — i.e. DUML's
**generic firmware-update protocol (cmd_set `0x00`) is being reused by
`dji_flight` specifically to push geofence-database updates**, not device
firmware. Purely descriptive of a shipped update mechanism, not an exploit
or bypass. See `06_NFZ_DATABASE_FINDINGS.md` for the database file itself.

### `0x1f` — brand-new cmd_set, two unrelated cmd_ids, no unifying theme

- **`0x11`** — func `0x20d3c` (60B). `nfz_upgrade_get_device_state` (high,
  clean) — same NFZ-upgrade family as the `0x00` group above, under a
  different cmd_set.
- **`0x05`** — func `0x1e348` (180B). `gs_api_get_min_max_action_id` (high,
  clean, repeats) — part of the unrelated `gs_act_*`/WP2-mission-action
  family (see `0x22` below).

Recommend documenting `0x1f` as a thin cmd_set with no domain theme —
inventing a unifying name for it would overstate what's actually known.

### `0x03` Flight Control — 3 handler confirmations (1 with a semantic mismatch), 2 new ids

- **`0x3f` Set NoFly Zone Data** — func `0x10eb4` (192B). No clean name;
  log-only: `"ack the version check"`. Low confidence; a second apparent
  semantic mismatch (dji_flight's handler here reads like a version-check
  ack, not NFZ zone-table data) — flagged, not resolved.
- **`0xcd` Update Nofly Area** — func `0x1144c` (**~5648B — almost
  certainly several unrelated functions packed together**; only the entry
  region is attributable). Usage-string clue near entry: `"useage[1]:itdb
  -> disable tdb"`, `"useage[2]:itdb <tdbPath> -> enable tdb"`,
  `"sucess/fail to create nfz timer"` — a debug/test command processor for
  an "itdb" (NFZ timer/test database) feature. No single clean identifier;
  low confidence, but thematically consistent with the existing name
  (both NFZ-area-related).
- **`0xea` Register Open Motor Error Action** — func `0x20e14` (~524B).
  `nfz_upgrade_profile` (high, clean). **Semantic mismatch, flagged
  plainly**: this function's actual logic is NFZ-profile file read/seek
  against `/nfz_data/NFZ/nfz.bin` (`"file type:0x%x, address:0x%x,
  len:0x%x"`, `"seeK_result:%d"`, `"ack read_addr 0x%x"`) — nothing to do
  with motor-error registration. `dji_flight` reuses this wire cmd_id for
  a different purpose than its documented name; DUML cmd_ids are not
  guaranteed unique in meaning across different recipient daemons, so this
  is not a correction to the existing name, just a note that this
  particular recipient does something else with it.
- **`0xc1`** (new) — func `0x19acc` (600B). No name strings at all
  (operates purely on `.bss` pointers, no logging calls). Low confidence;
  behavior not characterized beyond that.
- **`0xdb`** (new) — func `0x1985c` (624B). `process_ddb_update_process`
  (high, repeats 3×), with `process_ddb_update_verify`,
  `process_ddb_update_request`, `fc_event_cb_nfz_dynamic_update` as related
  sub-steps once each. "ddb" = NFZ **dynamic database** update state
  machine — another member of the same NFZ-upgrade family, this time
  under Flight Control.

### `0x11` ADSB — 2 handler confirmations, 3 new ids, core traffic engine exposed

- **`0x02` Push Data Get** (existing) — func `0xd5c0` (352B). No clean
  self-name; one solid log line, `"[ADSB_TIMESTAMP]adsb time sync %d %d
  %d"` — consistent with "Push Data Get" (a pushed ADS-B timestamp-sync
  triple).
- **`0x14` Push Unlock Info Get** (existing) — func `0xd720` (**~10,520B —
  by far the largest span in the table; almost certainly dozens of
  adjacent functions, only the entry region is attributable**). No clean
  self-name near entry. This is the clearest look yet at `dji_flight`'s
  **core ADS-B traffic-ingestion/flight-tracking engine**: `"get adsb push
  data err real:%d need:%d"`, `"lock flight data failed when in
  adsb_update_data"`, `"Add a new flight:%s/%s!"`, `"only %d frame_data
  for flight(%s/%s) so ignore it!"`, `"flight_data_size:%d"` — i.e. it
  maintains a locked, in-memory table of tracked ADS-B "flights" (keyed by
  some string pair, plausibly ICAO/callsign), adding new ones and
  appending frame data to existing ones. Filed under "Push Unlock Info
  Get" rather than a traffic-push name — semantic-mismatch note for
  `cmdset_11_ADSB.md`, not a rename.
- **`0x01`** (new) — func `0x1a5c0` (**~1800B, likely multiple
  functions**). No self-name found. Rich `FC_PARAM`-prefixed logging near
  entry (`"FC_PARAM: rcv undefine cmd:%d"`, `"FC_PARAM: invalid data
  len:%d"`, `"fc_param_write_cfg %d"`) suggests a generic
  flight-controller-parameter get/set/ack dispatcher multiplexing on a
  sub-opcode inside its own payload. Low/medium confidence; no name.
- **`0x05`** (new) — func `0x1a054` (1388B). `fc_event_cb_nfz_enquery`
  (high, clean) — yet another NFZ-family function, an "enquiry" event
  callback, filed under ADSB.
- **`0x20`** (new) — func `0x19d24` (816B). No string references at all
  (no logging in this function). Raw disassembly: reads a count at
  `[r0]`/`[r0+8]`, iterates a 4-byte-stride array, and on growth calls a
  helper (`0x19dc8`) using the libc++/libstdc++ `0xAAAAAAAB`
  reciprocal-multiply constant characteristic of `std::vector`-style
  capacity growth — a dynamically-growing list builder (plausibly an
  ADS-B whitelist or tracked-aircraft list). No name recovered.

### `0x22` Demo Mode / WP2 — 12 new ids, `api_wp2_*` family filled in

All rows below use the same templated trampoline shape verified against
the 4 known handlers (see §5), except where noted.

- **`0x01`** — func `0x10238` (~1660B). No name found near entry; the
  content is thematically **ADS-B** (`"set adsb receiver successfully!"`,
  `"creat adsb directory successfully!"`, `/blackbox/adsb/
  adsb_log_wm231_%0d.txt`, CSV headers `center_lon`/`heading`/`air_groud`/
  `time`) despite being registered under `0x22` here — ADS-B
  logging/directory-setup code bound to a Demo-Mode/WP2 cmd_id, a
  cross-subsystem reuse worth noting, not a contradiction.
- **`0x02`** — func `0x1badc`. `upload_wp_ack_rec_handler` (medium, one
  clean hit ~330B in; per §4's caveat, later strings in this window —
  `add_node_to_list_tail`, `get_node_by_index`, `autotest_config`, then an
  abrupt shift into GIMBAL/CAMERA receive-handler strings — almost
  certainly belong to separate, unregistered neighbors, not this row).
  Purpose: receives/processes the ack for a waypoint upload.
- **`0x03`** — func `0x1acc4`. `api_wp2_waypoints_upload` (medium) — fits
  the existing `api_wp2_*` family exactly, and **independently resolves
  the open lead in `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md`**, which
  had found this exact string with "no call site... found anywhere" and
  "no numeric cmd_id recoverable" — it's `0x22`/`0x03`.
- **`0x05`** — func `0x1b830` (48B, tiny). No logging/name. Raw
  disassembly: null-checks `r0` (returns via `bx lr` if null); otherwise
  calls `0x1b664` with a local 4-byte output slot, and if that reports a
  non-zero count, loads one 4-byte value and stores it through the
  caller's `r1` pointer, returning `4` (else `0`). A clean, if anonymous,
  **"get one 4-byte value, return byte-count-or-zero"** accessor shape.
- **`0x09`** — func `0x1b8c4`. `api_wp2_download_wp_init_info` (high,
  clean) — fits neatly between `pause_recovery` (`0x08`) and
  `download_waypoint` (`0x0d`) in the existing numbering.
- **`0x0d`** — func `0x1ad24`. `api_wp2_download_waypoint` (high, clean,
  repeats 3×) — **independent confirmation of a name this project already
  had** from a different source
  (`08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md`); the two sources agree
  exactly on the name and this pass supplies the cmd_id it was missing.
- **`0x0e`** — func `0x1b41c` (48B). No identifier-shaped self-name; the
  function's only identifying text is the descriptive (and apparently
  source-level-typo'd) log phrase `"flight reveice get_max_point_num"`,
  reported verbatim as a log-string description, not a confirmed C
  identifier.
- **`0x17`** — func `0x1b44c`. `api_wp2_get_wp_index_in_list` (high, clean,
  early). The same ~1000B window also contains `go_stop_wp_ack_rec_handler`
  and `api_wp2_go_cmd_handle` — thematically consistent (WP2 "go/stop
  waypoint" logic), so this may be one genuine larger function cluster
  rather than a boundary-crossing artifact, but that wasn't confirmed by
  tracing control flow; reported with that caveat.
- **`0x18`** — func `0x1b220`. `api_wp2_info_to_flight` (high, clean,
  early).
- **`0x19`** — func `0x1e2a8` (84B). No clean name; log line `"flight
  receive action upload cmd, data len = %d, buf[3] = %d"` — WP2
  mission-action upload; payload-shape hint: a length field and byte
  offset 3 of the payload are both referenced directly.
- **`0x1a`** — func `0x1e2fc` (76B). `gs_api_action_download` (high,
  clean) — download-direction counterpart to `0x19`'s upload.
- **`0x1e`** — func `0x1e3fc`. `gs_api_get_action_memory_info` (high,
  clean, right at entry). **Bounding note:** this row's "next table
  address" is ~8700B away; that is **not** one function — it's the start
  of a dense cluster of small `gs_act_*`/`gs_mission_wp_action_*`
  (WP2 mission-action-list) and `upgrade_*`/`read_nfz_data_file`
  (NFZ-upgrade) helpers with no other table row pointing into them. Only
  `gs_api_get_action_memory_info` itself is attributed to this row.

### `0x04` Gimbal — 1 handler confirmation on an already-ambiguous id, 1 new id

- **`0x1c`** (existing, already doubly-ambiguous — see
  `cmdset_04_Gimbal.md`) — func `0x1b860` (100B). No clean name; one log
  line, `"into api_wp2_autotest\n"` — part of the `api_wp2_autotest`/
  `autotest_config` test-mode subsystem referenced elsewhere in the `0x22`
  region above. A third, unrelated-looking data point on this cmd_id —
  not a resolution of the existing ambiguity.
- **`0xf1`** (new) — func `0x1d874` (80B). `recv_gimbal_product_type_handler`
  (high, clean, repeats). Confirms this is a real, intentional cmd_id, not
  an alignment artifact — the relocation is solid and the name resolves
  cleanly.

### `0x02` Camera — 3 handler confirmations, 1 naming cross-wire

- **`0x80` Camera State Info** — func `0x1d8c4` (80B).
  `recv_gimbal_self_status_handler` (high, clean, repeats). **Note the
  mismatch**: a *gimbal*-named handler under a *Camera* cmd_id — either
  "Camera State Info" also carries gimbal self-status in this binary, or
  it's a generic device-status-push id shared by both subsystems. Flagged,
  not resolved.
- **`0x81` Camera Shot Params** — func `0x1d914` (80B).
  `recv_camera_status_handler` (high, clean, repeats) — consistent with
  the existing name.
- **`0x87` Camera Shot Info** — func `0x1d964` (80B).
  `recv_camera_capture_para_handler` (high, clean, repeats) — consistent
  ("capture para" ≈ shot info).

### `0x0a` Vision — both new

- **`0xdd`** — func `0x1d9b4` (80B). `recv_camera_len_param_handler` (high,
  clean, repeats) — "len" reads as "lens" in context (camera lens
  parameters feeding the stereo/vision pipeline).
- **`0xde`** — func `0x1da04` (**~2180B, likely several functions**).
  `recv_navi_accu_shot_finish_handler` (high, clean, right at entry — an
  "accurate shot finish" / precision-landing-adjacent feature). The same
  window also contains `recv_navi_heartbeat_handler` and
  `gs_mission_wp_actions_download`, which per §4's caveat are very likely
  separate, unregistered neighbors, not part of this row.

## 7. What this doesn't establish

- Byte-level payload *field* layouts (beyond the generic ptr+uint16-length
  context-struct shape in §5) were not derived for most of the 39 rows —
  most evidence here is self-identifying name strings and purpose-level
  log text, not a field-by-field decode of each payload buffer. The real
  exceptions are `0x22`/`0x05`'s get-4-bytes-or-zero shape and `0x00`/
  `0x0c`'s ack-result+ack-buf-len format string.
- Several larger rows' true function boundaries were not confirmed by
  tracing real control flow (branches/returns) — only approximated by
  "next known table address," which this pass caught over-running into
  unregistered neighbor functions more than once (§4). A rigorous pass
  would trace real exits per function instead.
- Runtime reachability (whether a live DUML frame actually reaches any of
  this) was not attempted — consistent with every existing entry in
  `cmdset_22_Demo_Mode.md` already being marked unresolved on that exact
  point.
- Single firmware version only (`V01.00.1000`, 2022-12-09) — not
  cross-checked against any other wm260 firmware version.
