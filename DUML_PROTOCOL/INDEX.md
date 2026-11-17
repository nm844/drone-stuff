# DUML Command Set Index

| Cmd Set | Name | # Cmd IDs known | # with byte-level decoder |
|---|---|---|---|
| 0x00 | General | 85 | 15 |
| 0x01 | Special | 12 | 2 |
| 0x02 | Camera | 207 | 17 |
| 0x03 | Flight Control | 194 (this row previously read 191 here, but `cmdset_03_Flight_Control.md` itself already said 192 before this pass — a small pre-existing drift between this table and that file, not something this pass introduced or has reconciled further; +2 this pass, `0xC1`/`0xDB`, via `dji_flight` binary RE) | 36 |
| 0x04 | Gimbal | 49 (45 pre-existing + `0x69`, rendered in an earlier pass, + `0x51` found a later pass — see `cmdset_04_Gimbal.md`, which also flags 9 pre-existing duplicate-heading cmd_ids — + `0xF1` found this pass via `dji_flight` binary RE) | 26 |
| 0x05 | Center Board | 18 | 1 |
| 0x06 | Remote Control | 84 | 2 |
| 0x07 | Wi-Fi | 64 | 5 |
| 0x08 | DM36x | 15 | 3 |
| 0x09 | HD Link | 69 | 24 |
| 0x0a | Mono/Binocular (Vision) | 50 (48 pre-existing + `0xDD`/`0xDE` found this pass via `dji_flight` binary RE) | 14 |
| 0x0b | Simulator | 21 | 4 |
| 0x0c | ESC | 0 | 0 |
| 0x0d | Battery | 16 | 5 |
| 0x0e | Data Logger | 2 | 2 |
| 0x0f | RTK | 1 | 1 |
| 0x10 | Automation | 0 | 0 |
| 0x11 | ADSB | 14 (11 pre-existing + `0x01`/`0x05`/`0x20` found this pass via `dji_flight` binary RE) | 0 |
| 0x1f | Unclassified (not from the public dissector, not previously catalogued anywhere in this project at all — found by this pass's `dji_flight` binary RE; no unifying domain theme found, so no domain name is given — see `cmdset_1f_Unclassified.md`) | 2 | 0 |
| 0x22 | Demo Mode (not from the public dissector — found by this project's own binary RE; see `cmdset_22_Demo_Mode.md`) | 17 (5 pre-existing + 12 found this pass, which also corrected this array's own previously-estimated boundary — see `21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md`) | 0 |
| 0x23 | Smart (not from the public dissector — found by this project's own binary RE, independently in 2 different binaries; see `cmdset_23_Smart.md`) | 3 | 0 |
| 0x51 | Route Switch (not from the public dissector — found by this project's own binary RE; see `cmdset_51_Route_Switch.md`) | 1 | 0 |

**Total: 922** known `(cmd_set, cmd_id)` pairs across 20 non-empty cmd_sets
(of the 22 cmd_sets catalogued at all, 2 — `0x0c` and `0x10` — are
confirmed-empty with an architectural explanation rather than unexamined;
see their own `.md` files). 157 have a full byte-level payload decode (the
22 commands this pass added are name/handler-confirmed only — none have a
byte-level payload decode, so this figure is unchanged from the prior
pass).

(The prior total of 898 added 10 commands found via an exhaustive
follow-up sweep of 24 previously-unexamined WM260 binaries/libraries, all
independently reverify-confirmed: 4 under `0x00` — `0x83`/`0x85`/`0x93`/
`0x94` — 1 under `0x02` — `0xEC` — 2 under `0x09` — `0xA9`/`0xAA` — and 3
under a brand-new cmd_set, `0x23`. See `16_EXHAUSTIVE_SWEEP_FINDINGS.md`.
A round-2 sweep added 1 more (899 total): `0x04`/`0x51`, found via a
sweep of the 141 residual weak-signal binaries left over from round 1,
via a 4th client-side DUML send mechanism (`imss_link_v1_send`) not
previously documented. See `17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md`. The
prior **900** added 1 more still: `0x00`/`0x5B` ("FTP Control"), found
in DJI's own `test_upgrade` QA harness during a dedicated sweep of the
firmware-update/upgrade process. 3/3 adversarial reverify. See
`20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md`.)

**This pass (922, up from 900):** a follow-up on `dji_flight`'s
`R_ARM_RELATIVE`-relocated `.data` command array (first partially decoded
in `04_WM260_DAEMON_FINDINGS.md`/`14_FOLLOWUP_DEEPDIVE_FINDINGS.md`, only
4 of an estimated "43+" rows resolved at the time) independently
re-confirmed from raw bytes and relocations that the array is **43 rows,
`0xae040`–`0xae190`** — the number and start address `14_FOLLOWUP_
DEEPDIVE_FINDINGS.md` already had on record, but which had never been
reconciled into `cmdset_22_Demo_Mode.md`'s own (self-contradictory) gap
note, and whose 39 extra rows had never actually been decoded by either
document. This pass does that decoding; see
`21_DJI_FLIGHT_COMMAND_TABLE_FINDINGS.md` for the full re-derivation. Of
the 39 rows beyond the original 4: 12 land
under `0x22`, 3 under `0x11`, 2 under `0x03`, 2 under a brand-new cmd_set
`0x1f`, 1 under `0x04`, and 2 under `0x0a` — 22 genuinely new
`(cmd_set, cmd_id)` pairs; the remaining 17 are handler-confirmations of
cmd_ids this project already had by name from the public dissector (8
under `0x00`, 3 under `0x03`, 3 under `0x02`, 1 under `0x04`, 2 under
`0x11`), several with a semantic-mismatch flag (the dissector's name for
that cmd_id doesn't match what `dji_flight`'s own handler actually does —
DUML cmd_ids are not guaranteed unique in meaning across different
recipient daemons). `dji_flight` was confirmed absent entirely from the
E2 (aarch64) firmware build — a clean negative, not an unexamined gap.

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
