# Cmd Set 0x51 — Route Switch

Total known command IDs: 1

**Not part of the public `dji-firmware-tools` Wireshark dissector** — this
cmd_set is entirely outside that project's documented `0x00`-`0x11` range.
Found by direct disassembly of this project's own WM260 (Mavic 3) firmware,
not borrowed from any existing capture, community reference, or public
dissector source. Full write-up: `04_WM260_DAEMON_FINDINGS.md`.

Unlike cmd_set `0x22`, this cmd_id is **framework-level, not daemon-level**:
it lives inside `libduml_frwk.so` itself (the shared DUML bus-client
library every daemon on the system links against), not inside one specific
daemon's own code — so it is registered automatically for *every*
message-bus client on the system, not opted into individually.

## 0x05 — Route Switch

- **Handler:** `duss_event_route_switch` (exported symbol, matched exactly
  against the callback pointer — not just a name guess)
- **Purpose:** controls the DUML bus's "route switch" — most plausibly an
  internal link-mode selector (e.g. switching which physical/logical
  transport a message route uses, such as wired vs. wireless) rather than
  anything directly app/RC-facing. This reading is supported by this
  function's own embedded debug strings:
  `"RS: route switch configuration error!"` and
  `"RS: route switch host id = %#x"` — both consistent with an internal
  routing-configuration operation, referencing a "host id," not a
  user-facing flight or camera control.
- **Evidence:** found in `libduml_frwk.so`'s built-in dynamic-command
  table (`duss_event_create_dynamic_cmd_tbl`), a literal data table at
  vaddr `0x190ff8` (E2/aarch64 build) / `0x1098fc` (E1E/32-bit-ARM build —
  independently re-decoded, identical content at the different address
  expected for a different architecture's build). This same built-in table
  also supplies 3 of cmd_set `0x00`'s commands (`0x2f`, `0x89`, `0xaa` —
  see `cmdset_00_General.md`).
- **Confidence:** high on the `(cmd_set, cmd_id)` → handler mapping
  (symbol-matched, not just string-matched; confirmed on 2 independent
  CPU-architecture builds of the same library). Low/speculative on the
  precise operational semantics of "route switch" itself — the handler
  body's full logic was not disassembled, only its registration and debug
  strings.
- **Not determined:** payload format/fields; whether this is ever
  reachable from outside the device (vs. purely an internal/intra-chip
  configuration path); the handler's full logic.
