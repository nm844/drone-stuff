# Cmd Set 0x11 — ADSB

Total known command IDs: 14 (11 pre-existing + `0x01`/`0x05`/`0x20`, found
this pass via `dji_flight`'s relocated command array — see
`21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md`)

## 0x01 — (name unknown)

**Not from the public dissector — genuinely new, found by this project's
own binary RE.** Confirmed absent from this file before this pass.

- **Handler:** unresolved, inside `dji_flight`, func at `0x1a5c0`
  (**~1800B — likely multiple functions; only the entry region is
  attributable**).
- **Purpose:** no self-name was found, but rich `FC_PARAM`-prefixed
  logging near entry (`"FC_PARAM: rcv undefine cmd:%d"`, `"FC_PARAM:
  invalid data len:%d"`, `"fc_param_write_cfg %d"`) suggests a generic
  flight-controller-parameter get/set/ack dispatcher that itself
  multiplexes on a sub-opcode inside its own payload — a payload-shape
  clue even without a recovered name.
- **Evidence:** `dji_flight`'s confirmed `R_ARM_RELATIVE`-relocated
  `.data` command array, vaddr `0xae0b0`; cmd word decodes to cmd_set
  `0x11` / cmd_id `0x01`. See
  `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §6.
- **Confidence:** medium on the `(cmd_set, cmd_id)` mapping and the
  dispatcher inference; no name recovered.

## 0x02 — Push Data Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

**`dji_flight` handler confirmed:** `.data` array row at vaddr `0xae0b8`,
func at `0xd5c0` (352B). No clean self-name; the one solid log line,
`"[ADSB_TIMESTAMP]adsb time sync %d %d %d"`, is consistent with "Push
Data Get" (a pushed ADS-B timestamp-sync triple). See
`21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §6.

## 0x05 — FC Event Cb NFZ Enquiry

**Not from the public dissector — genuinely new, found by this project's
own binary RE.** Confirmed absent from this file before this pass.

- **Handler:** `fc_event_cb_nfz_enquery` (high confidence, clean), inside
  `dji_flight`, func at `0x1a054` (1388B).
- **Purpose:** an NFZ (no-fly-zone) "enquiry" event callback — part of the
  same NFZ family documented under cmd_set `0x00`
  (`cmdset_00_General.md`) and cmd_set `0x1f`
  (`cmdset_1f_Unclassified.md`), filed here under ADSB. A semantic-mismatch
  note, not a rename: this cmd_id's recipient does NFZ work, not ADS-B
  work.
- **Evidence:** `.data` array row at vaddr `0xae0d0`; cmd word decodes to
  cmd_set `0x11` / cmd_id `0x05`. See
  `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §6.
- **Confidence:** high on mapping and name; reachability unresolved;
  payload format not decoded.

## 0x08 — Push Warning Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x09 — Push Original Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x10 — Send Whitelist

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x11 — Request License

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x12 — License Enabled Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x13 — License Id Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x14 — Push Unlock Info Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

**`dji_flight` handler confirmed — this is the clearest look yet at this
binary's core ADS-B traffic-tracking engine, semantic mismatch flagged:**
`.data` array row at vaddr `0xae0c0`, func at `0xd720` (**~10,520B — by
far the largest single span in the table; almost certainly dozens of
adjacent functions, only the entry region is attributable to this
cmd_id**). No clean self-name near entry, but the log strings make the
subsystem unambiguous: `"get adsb push data err real:%d need:%d"`, `"lock
flight data failed when in adsb_update_data"`, `"Add a new
flight:%s/%s!"`, `"only %d frame_data for flight(%s/%s) so ignore it!"`,
`"flight_data_size:%d"` — i.e. it maintains a locked, in-memory table of
tracked ADS-B "flights" (keyed by some string pair, plausibly
ICAO/callsign), adding new ones and appending frame data to existing
ones. Filed under "Push Unlock Info Get" rather than a traffic-push name
— a semantic-mismatch note, not a rename. See
`21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §6.

## 0x15 — User Id Set

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x16 — Key Version Get

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x17 — Push Avoidance Action Get 

_No byte-level payload decoder in source dissector (name-only / unparsed payload)._

## 0x20 — (name unknown)

**Not from the public dissector — genuinely new, found by this project's
own binary RE.** Confirmed absent from this file before this pass.

- **Handler:** unresolved, inside `dji_flight`, func at `0x19d24` (816B).
- **Purpose:** no string references at all (no logging in this
  function). Raw disassembly: reads a count at `[r0]`/`[r0+8]`, iterates
  a 4-byte-stride array, and on growth calls a helper (`0x19dc8`) that
  uses the libc++/libstdc++ `0xAAAAAAAB` reciprocal-multiply constant
  characteristic of `std::vector`-style capacity growth — i.e. a
  dynamically-growing list builder, plausibly an ADS-B whitelist or
  tracked-aircraft list. No name recovered.
- **Evidence:** `dji_flight`'s confirmed `R_ARM_RELATIVE`-relocated
  `.data` command array, vaddr `0xae0c8`; cmd word decodes to cmd_set
  `0x11` / cmd_id `0x20`. See
  `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` §6.
- **Confidence:** high on the `(cmd_set, cmd_id)` mapping and the
  described list-builder shape; no name recovered.
