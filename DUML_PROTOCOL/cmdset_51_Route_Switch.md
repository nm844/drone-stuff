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
- **Not determined (as of the original pass):** payload format/fields;
  whether this is ever reachable from outside the device.

### Payload fields (added 2026-11-17, direct disassembly of the handler itself)

Byte offsets below are relative to the DUML payload (the handler's own
internal struct offsets, quoted in the evidence, are 20 higher — e.g.
payload offset 0 is struct offset `0x14`). Confirmed identically on both
architecture builds (E1E/ARM32 Thumb and E2/AArch64) via the handler's own
embedded `printf`-style debug strings.

| Off | Size | Field | Type | Notes |
|---|---|---|---|---|
| 0 | 1 | `operation` | uint8 (enum) | `1`=Port Switch, `2`=Route Switch, `3`=Switch Done. Selects one of three structurally different sub-layouts for the rest of the payload — see below. Any other value logs `"RS: unsupport rs command :%#x"` and returns an internal error with no wire response. |
| 1 | 1 | `inverted` | uint8 (flag) | **Only meaningful when `operation`=2.** From debug string `"RS: route switch: inverted = %d, old link mode = %d, new link mode = %d, type = %d"`. |
| 2 | 1 | `old_link_mode` | uint8 | **`operation`=2 only.** Numeric encoding (e.g. wired vs. wireless) not recovered. |
| 3 | 1 | `new_link_mode` | uint8 | **`operation`=2 only.** Numeric encoding not recovered. |
| 4 | 1 | `type` | uint8 | **`operation`=2 only.** Route/link type; semantic enumeration not recovered. |
| 5 | 1 | `host_id_count` | uint8 | **`operation`=2 only.** Loop bound for `host_id_list` below. |
| 6 | 2×N | `host_id_list` | uint16[] (little-endian) | **`operation`=2 only.** `host_id_count` little-endian 16-bit host IDs; 2-byte stride confirmed identically on both architectures. |

For `operation`=1 ("Port Switch"), only a single `switch_mode` byte at
payload offset 1 is used, and the handler replies synchronously with a
2-byte `{return_command=1, return_code=0}` ack via
`duss_event_resp_data_without_retcode`. For `operation`=3 ("Switch Done"),
offset 1 is `link_mode` and offset 2 is `type`, replying synchronously
with `{return_command=3, return_code=0}`. **`operation`=2 is one-way at
the DUML-payload level** — it's forwarded internally to the framework's
own `"sendto_route_coutrol"` task via `duss_osal_msgq_send` and an
eventfd wake, with no DUML-payload response constructed on that path
(confirmed by tracing every branch out of the `operation=2` block); any
eventual completion signal most plausibly arrives later as a separate,
independent `operation=3` ("Switch Done") request, not traced in this
pass.

**Worked example** (`operation`=2, "Route Switch"): a DUSS message-bus
client daemon asks the framework's internal route-control task to move
one host's active link from mode 0 to mode 1, for a single host ID, not
inverted, link type 0 (representative values — the real-world meaning of
specific link-mode numbers was not recovered).

- Request payload: `02 00 00 01 00 01 01 00`
  (`operation`=2, `inverted`=0, `old_link_mode`=0, `new_link_mode`=1,
  `type`=0, `host_id_count`=1, `host_id_list`=[`0x0001`])
- Response: none at the DUML-payload level for `operation`=2 — see above.
