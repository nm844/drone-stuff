# drone-stuff — DUML v1 protocol reverse engineering

Documentation and from-scratch client implementations for the DJI DUML v1
wire protocol, reverse-engineered from a WM260-series aircraft firmware
package and cross-checked against the public `dji-firmware-tools`
Wireshark dissector.

**No DJI firmware is included in this repository.** Everything here is
original documentation and code produced from studying that firmware;
the proprietary binaries themselves are not redistributed.

## Contents

- [`DUML_PROTOCOL/`](DUML_PROTOCOL/README.md) — the protocol reference:
  byte-by-byte frame format (confirmed against the firmware's own compiled
  CRC/frame-validation code), device addressing, and a byte-level payload
  breakdown for every command whose structure is known, across all 18
  command sets (877 commands catalogued, 157 with full field layouts).
- [`duml_py/`](duml_py/README.md) — a Python implementation: frame codec,
  command registry, payload encode/decode, serial/TCP transports, and a
  CLI.
- [`duml_c/`](duml_c/README.md) — a dependency-free C++17 port of the same,
  sharing its generated command-registry data with the Python library.

## Status

- Frame format: fully confirmed against the firmware's own disassembled code.
- 157 of 877 known commands have a complete byte-level payload decode;
  the rest are registered by name and sendable/receivable as raw bytes.
- Both libraries pass their test suites (28 Python, 30 C++) and have been
  checked against each other over a live TCP socket.

See each subdirectory's own README for details, methodology, and known
limitations.
