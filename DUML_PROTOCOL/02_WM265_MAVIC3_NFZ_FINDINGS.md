# WM265 (Mavic 3 Enterprise series) — NFZ / unlock-certificate findings

Session notes from an attempt to extend this repo's firmware analysis from
WM260 to WM265. Written up here (not committed automatically — review and
commit if useful) because the working files it references live outside the
repo and won't survive this container.

## 1. Model-code correction

The existing `01_BINARY_ANALYSIS_FINDINGS.md` firmware package
(`V01.00.1000_wm260_dji_system.bin`) is **Mavic 3 (base/Pro)**, not Mavic 2.
Confirmed from `o-gs/dji-firmware-tools`' own test fixtures
(`tests/test_dji_imah_fwsig_rebin1.py`, `tests/test_bin_archives_extract1.py`):

| WM code | Product |
|---|---|
| wm240/245/246/247 | Mavic 2 / Enterprise / Enterprise Dual / Enterprise RTK |
| **wm260** | **Mavic 3 / Mavic 3 Pro** (this repo's existing firmware) |
| wm2605 | Mavic 3 Classic |
| wm265e | Mavic 3 Enterprise |
| wm265m | Mavic 3 Multispectral |
| wm265t | Mavic 3 Thermal |

There is no bare "WM265" SKU in any source checked. A real aircraft reporting
"265" is one of the three Enterprise-series suffixed variants above (DDD's
own "Unknown" model list independently lists `WM265EA`, reinforcing this).
Confirm the exact code via DJI Assistant 2 / the label under the battery
bay before trusting any further analysis here.

## 2. Infra set up this session

- New cloud environment **`drone-stuff`** (personal, `env_01VS13tAuJ9DrgsovS7kSZ82`)
  with network access to `terra-1-g.djicdn.com` (DJI's own firmware CDN) and
  `archive.org` + `dn721904.ca.archive.org` (an Internet Archive mirror of a
  leaked Aloft/Anzu "Raptor" (DJI M3E/M3T-rebadged) CDN dump). This session
  switched onto it; it will be available to future sessions on this repo too.
- Cloned (not committed) for tooling only, no firmware redistributed here:
  - `o-gs/dji-firmware-tools` — `dji_imah_fwsig.py` unsigner + key database.
  - `Nimrasol/DJI-Mavic-3-WM260...USB-Recovery` — WM260 E2 recovery writeup
    and a newer `dji_imah_fwsig_latest.py`.
  - `mathewrtaylor/DJI_Resources` — curated link list (`Geofence_NFZ.md`,
    `Mods_Unlocks.md`).
  - `kenhuyang/dji_system.bin` — pre-Mavic2 era firmware archive + `NFZ.md`,
    documenting the **original Mavic (WM220, 2017)** NFZ mechanism: a
    separate IM*H-signed, AES-encrypted SQLite database (magic `GFDB`,
    tables `airmap_geofence_polygons`, `geofence_version`) pushed as its own
    module, abused at the time via an FTP-directory-traversal root exploit
    ("RedHerring") rather than a crypto break.
- Internet Archive item `anzu-quick-analysis` (metadata fetched) contains a
  full per-module `.sig` breakdown for **both wm265e and wm265t**, two
  firmware vintages each (`v20.00.0005` / `v09.00.0505`), plus two already
  Android-OTA-packaged `*_system.bin` files. Downloaded into
  `/home/user/wm265_fw/raw/` (cfg.sig, 0105, 0500, 1006, 1100, 1200, 1202,
  2607, 0802, 1502 for wm265e; 0105/0106/0103 for wm265t) — **ephemeral,
  outside the repo, will not survive this container.**
- Also fetched a real, non-leaked DJI Mavic 3 Enterprise firmware zip
  directly off `terra-1-g.djicdn.com` (verified live, HTTP 200) as a
  provenance cross-check: `/home/user/m3e_official/M3T_UAV_09.00.05.05_pro.zip`.
- `MAVProxyUser/BizarreActorPoutsOn` (an unrelated security-disclosure repo
  about the Aloft/Anzu "Raptor" white-label of the Mavic 3 Enterprise/Thermal)
  is where the two CDN URLs and the leaked-dump pointer came from, plus a
  useful wm265e/wm265t module/date/version table.

## 3. Firmware decryption attempts — result: blocked by unpublished keys

`wm265e.cfg.sig` (package manifest) decrypts cleanly — it's signed but
**not** encrypted. Full module list with real hashes:

```
0802 WM265E_E2  (Android/Linux camera+gimbal computer, "eagle" board)
1502 WM265_E1E  (Android/Linux main aircraft computer, sec_type="secure")
0105 LCPU       (flight-controller MCU)
0500 PD_MCU, 1006 SPEAKER_MCU, 1100 Battery, 1200/1202 ESC, 2607 RTK982
```

Every **encrypted** first-level module was tried against all 6 UFIE keys
currently published in `dji_imah_fwsig.py` (`UFIE-2021-08/-06`, `-2020-04`,
`-2019-11`, `-2018-07`, `-2018-01`), each paired with `PRAK-2021-09`:

| Module | Result |
|---|---|
| 0105 (LCPU) | all 6 keys fail — decrypted-chunk checksum mismatch, output entropy ≈7.999/8 (still effectively random) |
| 0802 (E2) | same, all 6 keys fail |
| 1502 (E1E) | same, 4 combos tried, all fail |
| 0500/1006/1100/1200/1202/2607 | same pattern, not pursued exhaustively (low NFZ relevance) |

This matches `dji-firmware-tools`' own test suite, which marks wm265e's
*production*-dated modules with placeholder keys commented "not published"
— only a specific internal/engineering version string (`V00.01.0101`,
`V90.00.0001`) is mapped to the real `PRAK-2021-09`/`UFIE-2021-08` pair.

Notably, that **same** key pair **does** decrypt the base **WM260**'s 0802
module (per Nimrasol's verified WM260 recovery writeup) — so WM260 and
WM265e, despite being the same airframe generation, use different
production encryption keys per SKU. The three modules most likely to hold
NFZ/unlock logic (LCPU, E2, E1E) are **not currently decryptable** with any
publicly known key for the Enterprise-series firmware. This is a real
cryptographic wall, not a tooling gap — confirmed empirically here, not
just asserted from reading the test suite.

## 4. The actionable path that doesn't need decryption

This repo's own `cmdset_03_Flight_Control.md` (cross-referenced from the
public Lua dissector, independent of any of the above) already catalogs the
**live DUML commands** for exactly this:

| cmd_id | Name | duml_py decode status |
|---|---|---|
| 0x08 | Nofly Zone Set | name-only |
| **0x09** | **Nofly Status Get** (`flight_limit_area_state`, `dji_flight_limit_action_event`) | **full** |
| **0x3F** | **Set NoFly Zone Data** (lat/lon/radius/country_code/type/id, fragmented) | **full** |
| 0x41 | Upload Unlimit Areas | name-only |
| 0x42 | FlyC Unlimit State (`is_in_unlimit_area`, `unlimit_areas_enabled`) | full |
| 0x47 | Enable Unlimit Areas | name-only |
| **0x61** | **FlyC Activation Info** (app_id/app_level/app_version) | **full** |
| 0x62 | FlyC Activation Exec | name-only |
| 0xCD | Update Nofly Area | name-only |
| 0xCF | New Nofly Area Get | name-only |
| **0xDF** | **Assistant Unlock Handler** (request: `lock_state`; response: `status`) | **full** |

Verified in this session: `duml_py`'s registry + generic field codec
already decode 0x09 / 0x3F / 0x61 / 0xDF correctly right now (tested
`reg.require(3, 0xDF)` + `codecs.decode_payload(...)` round-trip on a
synthetic response byte — works).

**This means the unlock-certificate handshake (0xDF) and the live NFZ table
(0x09/0x3F) can be observed directly off the wire against a real WM265,
fully decoded, using the existing `duml_py/examples/listen_and_decode.py`
— no firmware decryption needed, since the aircraft decrypts its own
firmware into RAM and the DUML bus carries plaintext structured commands.**

```
python examples/listen_and_decode.py --transport serial --port /dev/ttyUSB0
```
run while triggering an unlock / entering a restricted-zone boundary in
DJI Fly, is the direct contination of this repo's own methodology and
needs no further crypto work.

## 4b. Codec bug fixed, and a ready-to-run capture tool added

While building on §4: `0x3F`'s `latitude`/`longitude`/`radius`/`contry_code`/
`id` fields were declared `uint8` in the source Lua dissector
(`dji-dumlv1-flyc.lua` lines 380-385) despite their real sizes being
4/4/2/2/4 bytes — a pre-existing upstream mislabeling (harmless for
Wireshark's hex display, but it silently truncated every one of those
fields to its first byte through this repo's generic codec). Confirmed with
a synthetic payload, fixed in `duml_py/duml/commands.json` and regenerated
into `duml_c/generated/registry_data.cpp` (`int32`/`uint16`/`uint32` as
appropriate — cross-checked against the historical `FlycNoFlyZone` C struct
in `dji_flyc_nofly_ed.py`, which uses `c_int` for lat/lon), with a regression
test added to both suites (`test_set_nofly_zone_data_roundtrip` /
`SetNoFlyZoneDataRoundTrip`). 29/29 Python, 31/31 C++ tests pass.
`duml_lua_db.json` itself was left untouched — it's a faithful mirror of
the upstream dissector, not something to silently "fix".

Added `duml_py/examples/watch_nfz_unlock.py`: filters a live DUML capture
down to cmd_set 0x03's NFZ/Unlock-relevant commands, decodes `0x3F`'s
fragmented zone-table transfer into one accumulated list (lat/lon in
degrees), and optionally logs every watched frame as JSON lines. Tested
offline against synthetic frames (fragment accumulation, end-of-transfer,
0xDF/0x09 decode, raw fallback for the still-undocumented commands) —
not yet run against a real aircraft.

## 4c. WM260 fallback: real firmware obtained and decrypted (success)

Per the "same chipset as WM265, if known" fallback: WM260 is confirmed to
be exactly that. A plaintext file already in hand (the Android build
fingerprint inside a WM260 OTA payload) names the device
`eagle2_wm260_native` — same board family referenced by WM265e's own
recovery-mode fastboot identity (`product: eagle-fpga`).

Obtained a real WM260 firmware package (`wm260` V01.00.1000, dated
2022-12-09) via the DankDroneDownloader web app
(`dankdronedownloader.com`) — a plain HTML form (`brand=DJI&model=wm260&
version=01.00.1000&category=Aircraft` → `download/preview` →
`download/start`), no auth needed, streamed the real 429 MB package
directly. All three target modules decrypted **cleanly, with both RSA
signature verification and decrypted-content checksum passing** (not
forced/bypassed):

| Module | Key pair that worked |
|---|---|
| 0105 (LCPU, flight-controller MCU) | `PRAK-2020-01` / `UFIE-2020-04` |
| 0802 (E2, camera/gimbal Android computer) | `PRAK-2021-09` / `UFIE-2021-08` |
| 1502 (E1E, main aircraft Android computer) | `PRAK-2020-01` / `UFIE-2020-04` |

This independently confirms (not just secondhand) that WM260 uses
different, *published* keys than WM265e/t's unknown production keys —
same airframe generation and board family, different per-SKU key
material, exactly as suspected.

E2's `system.new.dat.br`/`vendor.new.dat.br` (Brotli-compressed Android
block-OTA data) were decompressed and reassembled into flat raw ext4
images (`DUML_PROTOCOL` doesn't carry this helper — ad hoc script, see
`/home/user/wm260_fw/build_raw_image.py` in this session's scratch area)
and read with `debugfs` (no mount/root privileges needed). This exposed
**the full Android `/system` and `/vendor` filesystem**, including a much
larger DUML library family than the prior pass examined:
`libduml_frwk/hal/util/rpc/payload/dn/fb/dsocket/osal/audio/vcodec/
f2d/fastrtps/hal_cam/ffremux/watermark/async_remux/dev_hb/shineIO/
orte/databuffer.so`, plus the daemons `dji_sec`, `dji_camera3`,
`dji_mb_ctrl`, `dji_mb_parser`, `dji_sys`, `dji_dcs`, `dji_hms`,
`dji_amt`, `dji_perception`, and many more (838 files total under
`lib`/`lib64`/`bin`/`xbin`) — none of which were extracted in the
original `01_BINARY_ANALYSIS_FINDINGS.md` pass (that pass only confirmed
the frame codec in `libduml_frwk.so`, explicitly leaving "the per-daemon
runtime registration tables" as future work). A mining pass across this
material is in progress; results to follow.

## 5. Not yet pursued: the DJI Fly app / FlySafe side

The *account-gated* "unlock certificate" layer (as opposed to the local
geofence-zone table) is, per DJI's current (2025 US policy change) FlySafe
architecture, substantially implemented app-side / server-side now, not
only in aircraft firmware. That's DJI Fly APK territory (`dji.go.v5`,
~650-715MB, APKMirror) — a separate research track (decompile with jadx,
look at how it talks to FlySafe's unlock endpoint) not attempted this
session.
