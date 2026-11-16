# DUML Command Set Index

| Cmd Set | Name | # Cmd IDs known | # with byte-level decoder |
|---|---|---|---|
| 0x00 | General | 84 | 15 |
| 0x01 | Special | 12 | 2 |
| 0x02 | Camera | 207 | 17 |
| 0x03 | Flight Control | 191 | 36 |
| 0x04 | Gimbal | 46 (45 pre-existing + `0x69`, newly rendered this pass — see `cmdset_04_Gimbal.md`, which also flags 9 pre-existing duplicate-heading cmd_ids) | 26 |
| 0x05 | Center Board | 18 | 1 |
| 0x06 | Remote Control | 84 | 2 |
| 0x07 | Wi-Fi | 64 | 5 |
| 0x08 | DM36x | 15 | 3 |
| 0x09 | HD Link | 69 | 24 |
| 0x0a | Mono/Binocular (Vision) | 48 | 14 |
| 0x0b | Simulator | 21 | 4 |
| 0x0c | ESC | 0 | 0 |
| 0x0d | Battery | 16 | 5 |
| 0x0e | Data Logger | 2 | 2 |
| 0x0f | RTK | 1 | 1 |
| 0x10 | Automation | 0 | 0 |
| 0x11 | ADSB | 11 | 0 |
| 0x22 | Demo Mode (not from the public dissector — found by this project's own binary RE; see `cmdset_22_Demo_Mode.md`) | 5 | 0 |
| 0x23 | Smart (not from the public dissector — found by this project's own binary RE, independently in 2 different binaries; see `cmdset_23_Smart.md`) | 3 | 0 |
| 0x51 | Route Switch (not from the public dissector — found by this project's own binary RE; see `cmdset_51_Route_Switch.md`) | 1 | 0 |

**Total: 898** known `(cmd_set, cmd_id)` pairs across 19 non-empty cmd_sets
(of the 21 cmd_sets catalogued at all, 2 — `0x0c` and `0x10` — are
confirmed-empty with an architectural explanation rather than unexamined;
see their own `.md` files). 157 have a full byte-level payload decode.
(This total adds 10 commands found via an exhaustive follow-up sweep of
24 previously-unexamined WM260 binaries/libraries, all independently
reverify-confirmed: 4 under `0x00` — `0x83`/`0x85`/`0x93`/`0x94` — 1 under
`0x02` — `0xEC` — 2 under `0x09` — `0xA9`/`0xAA` — and 3 under a brand-new
cmd_set, `0x23`. See `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.)

**Accuracy note (this pass):** the per-row "# with byte-level decoder"
column above was found to have drifted out of sync with the real
`commands.json` data for several rows (`0x00`, `0x03`, `0x04`, `0x08`,
`0x09`, `0x0a`, `0x0d`), and `0x02`/`0x04`/`0x06`'s "# Cmd IDs known"
values were likewise off by a small amount — all pre-existing drift,
unrelated to this pass's own additions. The aggregate totals in the
paragraph above (898 / 157) were independently recomputed directly from
`commands.json` and are accurate; every row in the table above has now
been recomputed the same way and the two now agree.

**For the status of the ongoing binary-by-binary sweep** (which
binaries/libraries have been checked for undiscovered DUML command
registrations, which haven't, and the reproducible methodology behind the
checks), see `BINARY_COVERAGE_TRACKER.md` — it tracks that independently
of this file's command-set totals, and should be updated whenever a new
sweep round changes a binary's disposition.
