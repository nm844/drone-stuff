# `/nfz/nfz.bin` — the on-aircraft No-Fly-Zone/restricted-area database, located and format-sketched

**Update, see `13_OPTEE_TA_FINDINGS.md` for a direct follow-up:** a later
pass decrypted the four `/ta/*.ta` OP-TEE Trusted Applications on this
same vendor partition and found one (UUID `789463d1-...`, mapped via
`/lib/libnfz_util_ca.so`) is a TEE-backed "NFZ UTIL TA" — it reads/manages
this exact database file (confirmed by the literal string
`/nfz_data/NFZ/nfz.bin`), tracks per-license unlock state, does
country-based restriction logic, and pushes signed NFZ status/data to DJI
FPV goggles over a dedicated secure channel. It also references a
**second, previously-undocumented file**, `/nfz_data/nfz_tfr.bin`, whose
format was not examined in that pass or this one. None of this changes
the container-level finding below (`nfz.bin` itself is unencrypted on the
vendor partition) — it adds a TEE-backed consumer/licensing layer on top
of the same plaintext file. See `13_...` for the full mapping and its
scope boundary (no attempt to verify/break the TA's own signature or
extract any RPMB-backed key material).

Found while walking the E1E module's `vendor.img` (the same partition that holds
the `ta/` TEE Trusted Applications referenced in `05_DJI_SEC_FINDINGS.md`) — a
previously-undocumented-in-this-repo file at `/nfz/nfz.bin`, 14,266,972 bytes.
Extracted via `debugfs -R "dump /nfz/nfz.bin system_files/nfz.bin" vendor.img`
(no mount/root needed, same technique used throughout this project).

This is examined here purely as a **data file whose format is worth
documenting**, in the same vulnerability-research framing as the rest of this
directory: identify what the file is and roughly how it's laid out, note
anything that's a genuine security-relevant property (e.g. "is it encrypted at
rest"), and stop short of producing a byte-exact, edit-ready record parser —
that crosses from "document the architecture" into "build the specific tool
needed to tamper with flight restrictions," which is out of scope here the
same way working exploit payloads are (see `04_WM260_DAEMON_FINDINGS.md` /
`05_DJI_SEC_FINDINGS.md` for the same stated boundary).

## What it is

High confidence this is the aircraft's local copy of DJI's global
restricted-airspace/no-fly-zone geofence database, current for this firmware
generation:

- `strings -n 8` extraction found **94,918** distinct readable strings, the
  overwhelming majority of which are real-world facility/airspace names:
  airports and airspace-classification labels (`"ABILENE REGIONAL CLASS E3"`,
  `"AABERDEEN CLASS D"`), prisons/jails/detention centers
  (`"ACADIA PARISH DETENTION CENTER"`, `"ADA CITY JAIL"`), hospitals
  (`"AALEN OSTALB-KLINIKUM"`), military installations/units (including
  non-US, e.g. a named Polish mechanized brigade), and a small number of
  explicitly flagged high-sensitivity sites (White House/Capitol/embassy-type
  names — **17** matches).
- Rough category tally from the full string list (keyword-matched, not
  deduplicated — a single zone name can match more than one category):
  airport/airspace-class terms **25,210**; prison/jail/detention/correctional
  **4,770**; hospital/medical **2,615**; power/nuclear plant **76**;
  military/air-force-base/naval **4,192**; White House/Capitol/embassy **17**.
  These categories line up exactly with the zone types DJI has always
  publicly stated its FlySafe/GEO system covers — this is consistent with
  "same database, current generation," not a new or different scheme.
- This supersedes, for this generation, the older SQLite-based `GFDB`/
  `airmap_geofence_polygons` format this project's existing `NFZ.md`
  documents from ~2017-era firmware: neither the `SQLite format` magic nor
  the `GFDB` magic bytes appear anywhere in this file. DJI has moved to a
  custom binary format for this aircraft generation, not a repackaged
  SQLite DB.

## Container-level finding: not encrypted, not wrapped

Unlike every firmware module examined in `01_BINARY_ANALYSIS_FINDINGS.md`
(all `IM*H`-signed/encrypted), `nfz.bin` has **no IM*H header** (first bytes
are `00 01 04 00 00...`, nothing resembling the `49 4d 2a 48` magic) and is
**not uniformly high-entropy** — a 4 MB sample measured **7.40 bits/byte**,
well below the ~8.0 expected of encrypted/compressed data, consistent with a
file that mixes plaintext string data with packed (but not encrypted) binary
fields. In other words: this specific database file sits on the vendor
partition in the clear, readable by anything with filesystem access to that
partition — a different exposure profile than the signed/encrypted firmware
modules it ships alongside. Noted as a finding below; **not** itself
demonstrated to be writable/tamperable at runtime (that would require
examining whichever daemon loads and validates this file, which was not
located in this pass — see "What wasn't done").

## Record format: length-prefixed name strings confirmed; surrounding fields not decoded

Checked the exact bytes immediately preceding three different zone names
(`"SOUTH POLE STATION"`, `"ACADIA PARISH DETENTION CENTER"`,
`"AALEN OSTALB-KLINIKUM"`) — in all three cases, the single byte immediately
before the name is a **length prefix that exactly matches the string's byte
length** (18, 30, 21 respectively). This confirms the name field itself is a
simple Pascal-style length-prefixed string, not null-terminated and not
fixed-width (ruling out an earlier guess that trailing characters like the
`"DTU"` seen stuck to one `strings` hit were part of the name — they're the
start of whatever field follows, not a suffix).

The bytes *preceding* that length byte are structured, not random — e.g. two
of the three samples share a repeated trailing pattern (`f1 d8 ff ff 01`
immediately before the length byte), suggesting a shared sentinel/default
value in some preceding field across different zone records — but the exact
field boundaries, count, and semantics (which bytes are latitude, longitude,
radius/shape data, a numeric zone ID, or an area/category code) were **not**
determined in this pass. Deliberately not pursued further: doing so to the
point of a confident, editable byte-offset table is the specific step this
project is treating as out of scope (it's the difference between "DJI stores
a readable zone-name database in file X" — architecture documentation — and
"here's exactly which bytes to change to delete/relocate a restriction" —
which is not being produced here).

## Update: `nfz_tfr.bin` and the `nfz.bin` relationship, see `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track G

A later pass resolved the `/nfz_data/nfz_tfr.bin` file `13_OPTEE_TA_
FINDINGS.md` surfaced as previously-unknown: it genuinely does not exist
on the E1E `vendor.img` (exhaustively confirmed, not a search miss) —
`/nfz_data` is its own SELinux-declared mount, separate from `/vendor`,
and this firmware extraction has no `userdata`-class image to back it.
Separately, that pass confirmed `/vendor/nfz/nfz.bin` (this document's
file) and `/nfz_data/NFZ/nfz.bin` are two physically distinct files kept
in sync by a version-gated, MD5-checked copy/upgrade routine in
`dji_perception` — not the same file via alias — and that `nfz_tfr.bin`
is architecturally Temporary-Flight-Restriction data pushed at runtime
from the DJI Fly app, never shipped as a firmware file, which independently
explains its absence. Also found: two apparent anti-rollback-disable
sentinel files (`disable_ota_anti_rollback`, `disable_anti_rollback`)
named next to that upgrade logic, not further characterized. See that
document for the full detail, including a correction that `dji_perception`
links `libnfz_util_ca.so` on the E1E build only — the E2 (aarch64) build
does not, and that library doesn't even exist under the E2 extraction.

## Findings

| Observation | Weakness/property | Impact category | Confidence |
|---|---|---|---|
| `nfz.bin` has no `IM*H` signature/encryption wrapper, unlike every other firmware module in this package | NFZ/restricted-zone database is stored unencrypted, unsigned (at the container level) on the vendor partition | confidentiality/integrity of a data-at-rest file — readable and (pending runtime validation, not examined) potentially editable by anyone with filesystem access, unlike the cryptographically-protected firmware modules | high-confidence-as-observed (the absence of the wrapper is directly checked); whether the loading daemon separately validates/signs the contents at load time is unknown — not examined |
| Zone names are stored as plaintext, length-prefixed strings | No obfuscation of the human-readable zone catalog itself | low-severity — this is place-name data with public real-world equivalents (aviation charts, OpenStreetMap); its sensitivity is about *tamper surface*, not secrecy | high-confidence |

**What wasn't done, stated plainly:** the exact per-record binary layout
(field boundaries/types beyond the confirmed length-prefixed name), any
coordinate/geometry decoding, and identifying which daemon on the aircraft
actually loads/parses/validates this file at runtime (so whether an edited
copy would even be accepted) were all left unexamined — each is a reasonable
next step for someone continuing pure format documentation, but the last one
in particular starts to shade toward "how would a modified file get
accepted," which is the point at which this pass stopped by design.
