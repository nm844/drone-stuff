# DUML Command Set Index

| Cmd Set | Name | # Cmd IDs known | # with byte-level decoder |
|---|---|---|---|
| 0x00 | General | 80 | 21 |
| 0x01 | Special | 12 | 2 |
| 0x02 | Camera | 212 | 17 |
| 0x03 | Flight Control | 192 | 40 |
| 0x04 | Gimbal | 47 (46 pre-existing + `0x69`, newly rendered this pass — see `cmdset_04_Gimbal.md`, which also flags 9 pre-existing duplicate-heading cmd_ids) | 44 |
| 0x05 | Center Board | 18 | 1 |
| 0x06 | Remote Control | 85 | 2 |
| 0x07 | Wi-Fi | 64 | 5 |
| 0x08 | DM36x | 15 | 6 |
| 0x09 | HD Link | 67 | 26 |
| 0x0a | Mono/Binocular (Vision) | 48 | 15 |
| 0x0b | Simulator | 21 | 4 |
| 0x0c | ESC | 0 | 0 |
| 0x0d | Battery | 16 | 6 |
| 0x0e | Data Logger | 2 | 2 |
| 0x0f | RTK | 1 | 1 |
| 0x10 | Automation | 0 | 0 |
| 0x11 | ADSB | 11 | 0 |
| 0x22 | Demo Mode (not from the public dissector — found by this project's own binary RE; see `cmdset_22_Demo_Mode.md`) | 5 | 0 |
| 0x51 | Route Switch (not from the public dissector — found by this project's own binary RE; see `cmdset_51_Route_Switch.md`) | 1 | 0 |

**Total: 888** known `(cmd_set, cmd_id)` pairs across 18 non-empty cmd_sets
(of the 20 cmd_sets catalogued at all, 2 — `0x0c` and `0x10` — are
confirmed-empty with an architectural explanation rather than unexamined;
see their own `.md` files). 157 have a full byte-level payload decode.
