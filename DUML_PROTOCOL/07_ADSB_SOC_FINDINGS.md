# `/adsb/adsb_soc.img` — ADS-B receiver SoC/MCU firmware blob, located and container-identified

Found on the E1E module's `vendor.img` (the same partition documented in
`01_BINARY_ANALYSIS_FINDINGS.md` and `06_NFZ_DATABASE_FINDINGS.md`) at
`/adsb/adsb_soc.img`, 98,592 bytes. This is **separate hardware** from the
DUML-level ADS-B command surface already catalogued in
`cmdset_11_ADSB.md` (cmd_set `0x11`, 11 command IDs: whitelist push,
license/unlock, push-warning, etc.) — that cmd_set is how the *main* DUML
bus talks *about* ADS-B (warnings, licensing, whitelist push) to whatever
daemon owns the feature; `adsb_soc.img` is the actual **firmware image for
a distinct ADS-B receiver chip** (the image name and its location alongside
other discrete peripheral blobs on this partition both point to a separate
SoC/MCU, not a Linux computer). Extracted via:

```
cd /home/user/wm260_fw/decrypted/e1e_extracted
debugfs -R "dump /adsb/adsb_soc.img /tmp/claude/adsb_work/adsb_soc.img" vendor.img
```

(`debugfs stat` confirmed the inode size, 98,592 bytes, matches exactly —
clean single-extent dump, no truncation.)

## Container-level finding: encrypted/signed, same `IM*H` family as the rest of this package — but a different key family

This is **not a plaintext MCU image**. Byte-level findings:

- **No ELF header, no ARM Cortex-M vector table at offset 0.** The first
  two little-endian 32-bit words are `0x00000040` / `0xe3b676af` — not a
  plausible initial-SP (`0x2000xxxx`-range) + reset-handler (odd/Thumb)
  pair, and no `\x7fELF` anywhere in the file.
- **`IM*H` magic (`49 4d 2a 48`) found at file offset `0x400`** — this
  project's already-documented firmware-signing/encryption wrapper (see
  `01_BINARY_ANALYSIS_FINDINGS.md` §1, `02_WM265_MAVIC3_NFZ_FINDINGS.md`,
  `06_NFZ_DATABASE_FINDINGS.md`). Unlike the top-level `.sig` modules where
  this magic sits at offset 0, here it's preceded by a 1024-byte region
  (offset `0x000`–`0x3ff`) that is non-zero but only moderately
  high-entropy (4.95 bits/byte over that span, all 1024 bytes examined;
  the last non-zero byte is at `0x21c`, rest is zero padding) — consistent
  with an outer signature/hash block (a 64-byte length field `0x40` at
  offset 0, then ~536 bytes of signature-shaped data, then padding to the
  512-byte boundary before the `0x400` header) rather than ADS-B payload
  data. This same two-tier layout (outer signature region, then `IM*H`
  header, then payload) is consistent with the general `dji_imah_fwsig`
  container family already used elsewhere in this project; the exact
  signature-field semantics were not reverse engineered (out of scope —
  see Scope note below).
- **Parsed header fields at `0x400`** (all little-endian):

  | Offset | Bytes | Value | Likely meaning |
  |---|---|---|---|
  | `0x400` | `49 4d 2a 48` | `"IM*H"` | magic |
  | `0x404` | `02 00 00 00` | `2` | format/version |
  | `0x408` | `20 7d 01 00` | `0x17d20` = 97,568 | payload size — **exactly** `98592 − 1024`, i.e. "everything after this 1024-byte region," cross-foots with the real file length |
  | `0x418` | `20 7b 01 00` | `0x17b20` = 97,312 | a second size field, `0x200` (512) smaller than the above |
  | `0x41c` | `20 7d 01 00` | `0x17d20` = 97,568 | repeats the `0x408` field |
  | `0x428` | `50 52 41 4b` | `"PRAK"` | key-family tag (public/package RSA-auth-key identifier, per this project's existing `PRAK-20xx`/`UFIE-20xx` key-pair naming — see `02_WM265_MAVIC3_NFZ_FINDINGS.md` §"Model-code correction" area and `01_BINARY_ANALYSIS_FINDINGS.md` §1) |
  | `0x42c` | `54 42 49 45` | `"TBIE"` | **symmetric-key-family tag — `TBIE`, not `UFIE`** |
  | `0x430`–`0x43f` | (16 bytes, high-entropy) | — | signature/hash fragment for the header itself |
  | `0x440` | `"bootloader\0..."` | — | an embedded ASCII component name, null-padded to a 32-byte field |
  | `0x460` | `"TBLD"` + `04 03 22 20` | tag `TBLD`, then bytes decoding as date `0x20220304` | a sub-component tag ("TBLD" = plausibly "table/bootloader descriptor") carrying what reads as a 2022-03-04 build-date-shaped field, plus a 4-byte value afterward not decoded |
  | `0x4c0` | `"BLLK"` + `98 7a 01 00` | tag `BLLK`, size `0x17a98` = 97,432 | another sub-block descriptor, size again close to the overall payload size |
  | `0x4e0` | `"BLFA"` + `a0 7a 01 00`, `73 00 00 00` | tag `BLFA`, two small fields (`0x17aa0`, `0x73`) | a third sub-block descriptor |

  Three internal 4-byte tags (`TBLD`, `BLLK`, `BLFA`) sit between the main
  `IM*H` header and the start of the uniformly-encrypted region — this
  looks like the same general "named sub-image" container convention used
  elsewhere in this product line's bootloader-class images (a named
  component — here literally the string `"bootloader"` — described by a
  handful of 4-letter-tagged descriptor records with size/hash fields),
  **not** unique to ADS-B. None of these tags, sizes or the embedded date
  were pursued further than listing them, per the scope boundary below.

- **The payload past this header is high-entropy throughout**, consistent
  with AES-encrypted (or equivalently scrambled) content, not plaintext
  firmware: a byte-for-byte Shannon entropy scan in 2 KiB windows across the
  whole 98,592-byte file gives ≈7.90–7.93 bits/byte for every window from
  offset `0x800` to end-of-file, and `0x18120`(EOF) − `0x800` covers 97% of
  the file. (Whole-file entropy: 7.994/8; header region `0x400`–`0x500`
  alone: 3.97/8, reflecting its real structure; `0x500`-to-EOF alone:
  7.998/8 — indistinguishable from random.) This matches exactly the
  pattern `01_BINARY_ANALYSIS_FINDINGS.md` §1 already documented for the
  Battery (`1100`) and ESC (`1200`/`1202`) modules: still-encrypted,
  high-entropy throughout, no recoverable structure beyond the outer
  container header.
- **`strings -n 6`** over the whole file returns 171 hits, and inspection
  shows only two are real fixed fields from the header already listed above
  (`"PRAKTBIE"`, `"bootloader`); the remaining ~169 are short, non-repeating,
  non-meaningful fragments — the statistically-expected number of
  printable-looking runs inside ~97 KB of high-entropy ciphertext, not
  genuine strings.
- **Byte-pattern search for this project's confirmed `DjiCrc8Table` leading
  16 bytes** (`00 5E BC E2 61 3F DD 83 C2 9C 7E 20 A3 FD 1F 41`, taken from
  the verified table in `duml_py/duml/frame.py` / `00_FRAME_FORMAT.md`,
  itself confirmed byte-identical against `libduml_frwk.so` at file offset
  `0xfe800`) — **not found anywhere in the file.** This is the expected
  result for an encrypted blob (same "no hit" result `01_BINARY_ANALYSIS_
  FINDINGS.md` §2 reports for the still-encrypted Battery/ESC dumps) and
  means **this file, as stored on the vendor partition, cannot be shown
  (and is not expected) to speak native DUML v1 framing** — unlike the
  LCPU (`0105`) and PD_MCU (`0500`) raw dumps, which are plaintext and do
  contain the table. Whether the *decrypted* ADS-B SoC firmware would
  contain it (i.e. whether this receiver also natively frames DUML, like
  the other confirmed MCU-class modules) is **not determined** — the data
  needed to check that is exactly the data this container is still hiding.

## Scope note — stopping at "it's encrypted, with this container, under this key family"

Per this project's established boundary (see `04_WM260_DAEMON_FINDINGS.md`
/`05_DJI_SEC_FINDINGS.md`/`06_NFZ_DATABASE_FINDINGS.md`), this pass
**stopped at identifying and describing the wrapper** — confirming the
`IM*H` magic, parsing its plainly-readable header fields (sizes, tags, the
`PRAK`/`TBIE` key-family identifiers, the embedded date), and measuring
entropy to confirm the payload is still encrypted. **No decryption was
attempted.** The task notes (consistent with `02_WM265_MAVIC3_NFZ_
FINDINGS.md`, where every encrypted WM265e module was tried against all 6
published `UFIE` keys and failed) that this project's available key
material targets the `UFIE` module-type family used by the Linux computers
and some MCUs (`0105`/`0500`/`0802`/`1502`); this file's header explicitly
tags itself `TBIE`, a **different** symmetric-key family, so even the keys
already in hand for other modules in this package would not be expected to
apply here, and no attempt was made to find or guess `TBIE` key material.

## Findings

| Observation | Weakness/property | Impact category | Confidence |
|---|---|---|---|
| `adsb_soc.img` carries the project's already-documented `IM*H` signing/encryption wrapper, with payload entropy (7.90–7.998 bits/byte throughout) indistinguishable from random | ADS-B receiver SoC firmware is encrypted at rest on the vendor partition, same protection level as the other first-party firmware modules in this package | confidentiality of firmware IP / anti-tamper for this specific peripheral — not a weakness relative to the rest of the product, just confirmation it is **not** an easier target than the already-examined modules | high-confidence (directly measured: magic offset, header fields, entropy scan, CRC8-table byte search all point the same way) |
| The container's header explicitly identifies a `TBIE` key family, distinct from the `UFIE` family this project has working keys for | This module sits behind key material this project does not currently possess, in addition to being encrypted | no new exploitable weakness — this is a "wall," not a finding of weak protection; recorded so a future pass doesn't re-attempt the same known-wrong `UFIE` keys against this file | high-confidence as observed (the tag string is read directly); whether `TBIE` denotes a genuinely different key or just a different label for key material this project already has under another name was not checked |
| No evidence either way on whether the *decrypted* firmware would speak native DUML v1 framing like the LCPU/PD_MCU MCUs do | Unknown — the CRC8-table byte-search that would answer this requires plaintext this project does not have | N/A (absence of information, not a vulnerability) | n/a — explicitly inconclusive, stated as such rather than guessed |

**What wasn't done, stated plainly:** no attempt to decrypt or find `TBIE`
key material; no attempt to decode the outer ~536-byte signature-shaped
region at offset `0x0`–`0x21c` beyond noting its presence, size, and
entropy; no attempt to decode the `TBLD`/`BLLK`/`BLFA` sub-block size/hash
fields beyond listing their tags and the plainly-readable integer fields
next to them; no attempt to identify the receiver chip's actual silicon
vendor/part number (impossible without the plaintext payload, since the
only readable strings in the file are the two header fields already
quoted). Each of these would require either the missing key material or a
different source for this image (e.g. an unencrypted engineering/debug
build, if one surfaces) — reasonable next steps for a future pass, not
pursued here because this pass's only unblocked next step was decryption
itself, which is out of scope.
