# duml_c — DUML v1 protocol library (C++17)

An original C++ implementation of DJI's DUML v1 wire protocol, built from
the protocol reverse engineering in [`../DUML_PROTOCOL/`](../DUML_PROTOCOL/)
and sharing its data with the Python port in [`../duml_py/`](../duml_py/).
No external dependencies; builds with a plain `make`.

This is a representation of the protocol and command set, written from
scratch with its own architecture and naming. It is not a decompilation or
port of DJI's `libduml_*.so` libraries, and it does not include their
message bus, USB/IAP2/UDT networking, security, or any flight-control, ESC,
or battery firmware logic.

## Build

```bash
make            # build/libduml.a and build/duml_cli
make test       # 30 unit tests
make examples   # build/examples/*
```

## What's in it

| File | Role |
|---|---|
| `include/duml/crc.hpp`, `src/crc.cpp` | CRC8 (seed 0x77) and CRC16 (seed 0x3692) with the tables and algorithm confirmed against the firmware's `CalCrc8`/`CalCrc16` |
| `include/duml/frame.hpp`, `src/frame.cpp` | `Frame` encode/decode, header bit layout, `FrameError`, `IterFrames` |
| `include/duml/enums.hpp` | `DeviceType`, `CmdSet`, `AckType`, `EncryptType`, `PacketType` |
| `include/duml/codecs.hpp`, `src/codecs.cpp` | `EncodePayload`/`DecodePayload`: scalars, bitfields, and Request/Response or length-gated branches |
| `include/duml/registry.hpp`, `src/registry.cpp` | `LookupCommand`, `RequireCommand`, `CommandsInSet`, `FindByName` |
| `generated/registry_data.cpp` | All 877 commands and 1370 fields as static data (generated) |
| `include/duml/commands.hpp` | One named constant per command, e.g. `cmd::gimbal::kGimbalControl` (generated) |
| `include/duml/transport.hpp` | `Transport`, `StreamFramer` (resync like the firmware's frame scanner), `FrameListener`, `SerialTransport`, `TcpTransport`, `TcpServerTransport` |
| `include/duml/client.hpp`, `src/client.cpp` | `DumlClient`: build, send, `SendAndWait`, `Listen`, background listener |
| `tools/duml_cli.cpp` | `list`, `show`, `decode`, `send`, `listen` |

## Usage

```cpp
#include "duml/client.hpp"
#include "duml/commands.hpp"
using namespace duml;

SerialTransport port("/dev/ttyUSB0", 115200);
DumlClient client(port, static_cast<uint8_t>(DeviceType::kApp));

BuildOptions opts;
opts.receiver_type = static_cast<uint8_t>(DeviceType::kGimbal);
opts.fields["gimbal_control_unkn0"] = Value(int64_t(1024));
opts.fields["gimbal_control_unkn1"] = Value(int64_t(1024));
opts.fields["gimbal_control_unkn2"] = Value(int64_t(1024));
client.SendCommand(cmd::gimbal::kCmdSet, cmd::gimbal::kGimbalControl, opts);

// Any command, even with no known layout, via raw bytes:
BuildOptions raw; raw.raw_payload = Bytes{0x00};
client.SendCommand(cmd::camera::kCmdSet, 0x01, raw);
```

```bash
build/duml_cli list --cmd-set 4
build/duml_cli show --cmd-set 3 --cmd-id 0x0a
build/duml_cli decode 55 0d 04 33 0a 03 34 12 00 00 00 de 22
build/duml_cli send --transport serial --port /dev/ttyUSB0 --cmd-set 4 --cmd-id 1 \
    --receiver-type 4 --field gimbal_control_unkn0=1024 --field gimbal_control_unkn1=1024 \
    --field gimbal_control_unkn2=1024
build/duml_cli listen --transport tcp --host 127.0.0.1 --port 9000 --duration-ms 10000
```

## Coverage

All 877 known commands are registered and sendable. 157 have named,
field-level payload layouts; the other 720 send and receive as raw bytes
(`{"raw": bytes}`). The two layouts added from flight-recorder
cross-references (Battery/0x06, Flight Control/0x0A) are candidate
mappings, flagged `source: flyrec_crossref` in the registry.

## Regenerating the data

`generated/registry_data.cpp` and `include/duml/commands.hpp` come from
`../duml_py/duml/commands.json`:

```bash
python3 tools/gen_cpp_registry.py  ../duml_py/duml/commands.json generated/registry_data.cpp
python3 tools/gen_cpp_constants.py ../duml_py/duml/commands.json include/duml/commands.hpp
```

## Limitations

- `Frame::Encode` refuses `encrypt_type != kNone`: no key material or
  algorithm parameters are known for AES/DES/self-defined on this product.
- `uint64` fields decode into `int64_t`, so values above 2^63 wrap.
- Serial uses POSIX termios (macOS/Linux). Build with `DUML_NO_SERIAL=1` elsewhere.
- Branch choice for value-selected variants (such as the General Encrypt
  sub-commands) falls back to the largest layout that fits; pass
  `BuildOptions::variant` to force one.
