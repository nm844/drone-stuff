# Cmd Set 0x18 — LTE/Dongle Diagnostic

Total known command IDs: 1

**Not part of the public `dji-firmware-tools` Wireshark dissector** — this
cmd_set is entirely outside that project's documented `0x00`-`0x11` range
(previously, no cmd_set in this project's catalog existed between `0x11`
and `0x22` at all). Found by direct disassembly of this project's own
WM260 (Mavic 3) firmware. Full write-up:
`20_FIRMWARE_UPDATE_PROCESS_FINDINGS.md`'s "Resolved by a targeted
follow-up pass" section and `21_PAYLOAD_DECODE_SWEEP_FINDINGS.md`.

The name "LTE/Dongle Diagnostic" is a project-assigned label — this is a
factory/QA test harness command, not an end-user feature, and the only
known sender (`dongle_upgrade_test.sh` via `dji_mb_ctrl`) addresses it to
`dji_lte` (the LTE/cellular-modem daemon).

## 0x3D — Upgrade/Downgrade Test Trigger

- **Handler (sender side, confirmed):** `dji_mb_ctrl` — a generic DUML
  message-bus CLI tool invoked as
  `dji_mb_ctrl -S test -R diag -g 08 -t 06 -s 18 -c 3d <payload>` by
  `dongle_upgrade_test.sh`, looping 1000 times (alternating "start
  upgrade"/"start downgrade", 360 seconds apart) to stress-test the LTE
  dongle's firmware-upgrade path.
- **Handler (receiver side):** `dji_lte`'s registered callback for bus
  identity device-type `8` ("ve_air" — a retired-chip legacy slot
  reassigned to the LTE/cellular daemon this generation; see
  `19_ROUND3_TAIL46_SWEEP_FINDINGS.md` Track AA) index `6`, at vaddr
  `0xb5f0`, dispatching into a generic DUML-frame decoder at vaddr
  `0xb108`. **Neither function branches on `cmd_set`/`cmd_id` anywhere in
  its body** — independently re-confirmed by a full disassembly of both
  functions, twice now (doc 20's original pass and this payload-decode
  pass). This means the *address* (device-type 8 / index 6) is
  confirmed, but what — if anything — distinguishes an "upgrade" trigger
  from a "downgrade" trigger once the frame arrives at `dji_lte` was not
  located in either pass.

### Payload fields

| Off | Size | Field | Type | Notes |
|---|---|---|---|---|
| 0 | 1 | `operation` | uint8 (enum) | `1` = Start Upgrade, `3` = Start Downgrade. Only these two literal values are ever observed anywhere in the firmware, both read directly from `dongle_upgrade_test.sh`'s own labelled invocation lines. No receiver-side code reads or branches on this byte specifically — its meaning comes from the sender's own intent, not from observed receiver logic. |
| 1 | 15 | `filler` | uint8[15] | The literal ASCII byte `0x61` (`'a'`) repeated, identical in both real invocations found anywhere in the firmware tree. No validation, length check, or parsing of these bytes was found in any traced receiver-side code path. Reported honestly as filler of unconfirmed purpose — it may be arbitrary padding chosen by the test script's author, or consumed by logic this pass could not locate. |

(Total payload: 16 bytes. An earlier pass's hint described a 17-byte
payload — 1 + 16 filler; direct reading of the shell script corrects this
to 16 bytes total, 1 + 15 filler.)

**Worked example** ("start upgrade"): the factory/QA harness's exact
real invocation.

- Request payload: `01 61 61 61 61 61 61 61 61 61 61 61 61 61 61 61`
  Copied verbatim from `dongle_upgrade_test.sh`'s `dji_mb_ctrl ... -c 3d
  01616161616161616161616161616161` line. The "start downgrade" line two
  lines below is byte-identical except the first byte is `0x03`.
- Response: none found. Neither `dji_lte` function in the traced call
  chain calls any of its imported response-construction routines
  (`duss_event_resp_data`, `duss_event_resp_data_without_retcode`,
  `duss_event_resp_ok`, `duss_event_resp_err`) — confirmed by checking
  every PLT call site of all four symbols across the full function
  range. This command is one-way at the DUML-payload level (the
  underlying DUSS message bus may still produce a generic
  transport-level ack independent of any command-specific payload; that
  was out of scope for this pass).

**Confidence:** high on the sender mechanism, the addressing, and both
functions' lack of command-specific branching (independently reproduced
twice). Low on what (if anything) actually distinguishes upgrade from
downgrade once the frame arrives — this remains a genuinely open
question, not glossed over.