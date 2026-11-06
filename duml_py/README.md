# duml — a DUML v1 protocol library

A from-scratch Python implementation of DJI's DUML v1 wire protocol: frame
codec (header/CRC8/CRC16), a registry covering all 877 known
`(cmd_set, cmd_id)` pairs, field-level payload encode/decode wherever the
byte layout is known, and transports for actually sending/receiving over
serial or TCP.

This sits on top of the reverse-engineering work in
[`../DUML_PROTOCOL/`](../DUML_PROTOCOL/) — read that directory first for the
full byte-by-byte protocol writeup and the firmware-binary verification
behind it. This package is the "make it actually usable" half of that work.

## What's really decoded, and what isn't

**Every one of the 877 known `(cmd_set, cmd_id)` pairs is registered by
name** (`duml list`) and **every one is sendable/receivable** — `send_command`
accepts a `raw_payload=` for anything, and `decode_incoming` always succeeds
(falling back to `{'raw': <bytes>}` for commands with no known field layout).

**157 of those 877 have a real, field-level byte decode** — offset, size,
type, bitmask, enum for every field — pulled mechanically from the public
`dji-firmware-tools` Wireshark dissector, plus 2 commands newly
reverse-engineered this round by cross-referencing the DJI flight-recorder
log-file dissectors (which happen to log some of the exact same wire
structs as live push commands) and added to the actual Lua dissector
(`dji-dumlv1-proto.lua`'s Battery Push Common Info, `dji-dumlv1-flyc.lua`'s
new Battery Status Get):

```
duml.registry.default_registry().stats()
# {'total': 877, 'full': 157, 'none': 720}
```

The other 720 are real DJI commands (used by at least one product across
DJI's history that the community dissector covers) whose payload byte
layout has never been published or reverse engineered by anyone, as far as
this project found. **Decoding all 720 of those would need live traffic
capture against a real aircraft, or full decompilation of the stripped
daemon binaries this project could pull out of the firmware's own filesystem
images** (see `../DUML_PROTOCOL/01_BINARY_ANALYSIS_FINDINGS.md` §3) — neither
was achievable from static analysis alone in this pass. This package is
built so that filling in more decodes later is a matter of adding entries
to `duml/commands.json` (or re-running the generator against an updated
Lua dissector) — nothing else needs to change.

## Install

```bash
cd duml_py
pip install -e .            # core library, no deps
pip install -e .[serial]    # + pyserial, for real UART/USB links
```

## Quick tour

```python
from duml import DumlClient, DeviceType
from duml.transport import SerialTransport

transport = SerialTransport('/dev/ttyUSB0', baudrate=115200)
client = DumlClient(transport, sender_type=int(DeviceType.APP))

# Send a fully-decoded command with named fields:
client.send_command(0x04, 0x01, receiver_type=int(DeviceType.GIMBAL),
                     fields={'gimbal_control_unkn0': 1024,
                             'gimbal_control_unkn1': 1024,
                             'gimbal_control_unkn2': 1024})

# Send *any* command, even one with no known payload layout, via raw bytes:
client.send_command(0x02, 0x01, receiver_type=int(DeviceType.CAMERA),
                     raw_payload=b'\x00')   # "Do Capture Photo"

# Listen and get back named fields wherever known, raw bytes otherwise:
for decoded in client.listen(duration=10):
    print(decoded)
```

Or from the command line:

```bash
duml list --cmd-set 4                      # every Gimbal command
duml show --cmd-set 4 --cmd-id 1            # byte layout detail
duml decode 55 0d 04 33 0a 03 34 12 00 00 00 de 22   # decode a captured frame
duml send --transport serial --port /dev/ttyUSB0 \
    --cmd-set 4 --cmd-id 1 --receiver-type GIMBAL \
    --field gimbal_control_unkn0=1024 --field gimbal_control_unkn1=1024 \
    --field gimbal_control_unkn2=1024
duml listen --transport tcp --host 127.0.0.1 --port-num 9000 --duration 10
```

## Package layout

| Module | What |
|---|---|
| `duml/frame.py` | `Frame.encode()`/`Frame.decode()`, CRC8/CRC16, firmware-confirmed (see `DUML_PROTOCOL/00_FRAME_FORMAT.md`) |
| `duml/enums.py` | DeviceType, CmdSet, AckType, EncryptType, PacketType |
| `duml/registry.py` | `CommandRegistry` — loads `commands.json`, lookup by id or name |
| `duml/commands.json` | The generated data: all 877 commands, 157 with field specs |
| `duml/codecs.py` | `encode_payload()`/`decode_payload()` — turns a field spec + bytes into a dict and back, including bitfields and conditional/optional branches (Request-vs-Response, optional tails, value-selected variants) |
| `duml/client.py` | `DumlClient` — the high-level send/receive/listen API |
| `duml/transport/` | `SerialTransport` (pyserial), `TcpTransport`/`TcpServerTransport` (stdlib), `StreamFramer` (byte-stream resynchronization, same algorithm as the firmware's own frame scanner), `FrameListener` (background-thread listener) |
| `duml/cli.py` | `duml` command-line tool |

## How `commands.json` was generated (so you can extend it)

A small parser (not shipped here, but fully described in
`../DUML_PROTOCOL/README.md`) walks the Wireshark Lua dissector source,
extracts every `ProtoField` definition and every per-command dissector
function's `subtree:add(f.x, payload(offset,size))` / `offset = offset + N`
sequence, and reconstructs the byte layout mechanically. Branches
(`if pack_type == 0 then ... else ... end`, `if payload:len() >= N then`)
are preserved as labeled alternative field groups, which is exactly what
`codecs.select_branch()` consumes at runtime.

To add a newly-discovered decode:
1. Add the real dissector function + `ProtoField`s to the appropriate
   `dji-firmware-tools/comm_dissector/wireshark/dji-dumlv1-*.lua` file (as
   was done for the 2 new finds this round — see the git diff on that repo),
   wire it into that file's `*_CMD_DISSECT` table.
2. Add the equivalent `fields` list by hand (or re-run the generator) to the
   matching entry in `duml/commands.json`: list of
   `{name, label, offset, size, type, enum, mask, desc, branch}` dicts, one
   per `subtree:add()` call, in source order — exactly the shape already
   there for the 157 existing entries.
3. Set `decode_status` to `'full'`.

## Testing

```bash
pip install -e .
python -m unittest discover -s tests -v    # 28 tests: CRC vectors, frame
                                             # round-trips, codec round-trips
                                             # (including bitfields and
                                             # branches), registry integrity
```

## Known limitations

- **Encryption is not implemented.** The wire format's `encrypt_type` field
  (AES/DES/self-defined/XOR) is decoded, but `Frame.encode()` refuses to
  build a frame with `encrypt_type != NONE` — there is no publicly known key
  material or algorithm parameters for any of these on this product, so this
  package cannot encrypt a payload for you. If you have your own key
  material, encrypt the payload yourself and pass the ciphertext as
  `raw_payload` with `encrypt_type` set on the `Frame` directly.
- **720 of 877 commands have no known payload layout** (see above) — they
  send/receive fine as raw bytes, but you won't get named fields.
- **`StreamFramer`'s resync is byte-at-a-time** (matches the firmware's own
  approach exactly, but it's O(n) per candidate SOF on pathological noisy
  input — fine for real serial/USB traffic, not optimized for adversarial
  fuzzing input).
- Branch selection for *value-selected* variants (e.g. the General Encrypt
  command's 4 sub-commands, each with a different payload shape chosen by
  an earlier byte's value, not by length or direction) falls back to
  "biggest declared layout that fits the given length" — pass `variant=`
  explicitly if you need a specific one and the auto-selection picks wrong.
