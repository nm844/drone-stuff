# `/nfz/nfz.bin` — the on-aircraft No-Fly-Zone/restricted-area database, located and format-sketched

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
