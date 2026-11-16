# Cmd Set 0x0c — ESC

Total known command IDs: 0

This cmd_set is empty in the public `dji-firmware-tools` Wireshark
dissector itself (`ESC_UART_CMD_TEXT` exists as a table name in the
dissector source but is literally `{}` — zero commands defined anywhere
upstream), and this project's own direct binary disassembly of the WM260
(Mavic 3) firmware found no concrete, enumerable commands either. This is
a real, acknowledged gap in community knowledge, not a search failure.

## What was found, short of a concrete cmd_id

- **Plausible explanation for why ESC traffic isn't first-class on the
  main DUML bus:** ESC (motor-controller) modules are likely addressed
  indirectly through the Center Board's translation layer (cmd_set `0x05`,
  `0x0D`) rather than with their own first-class cmd_set `0x0c` traffic —
  see `01_BINARY_ANALYSIS_FINDINGS.md` §1.
- **A second, distinct, non-DUML-style dispatch mechanism exists in
  `libdsp_frwk.so`:** `ss_hal_mb_set_req_callback`, operating over a
  runtime `.bss` table rather than the `duss_event_register_dynamic_command`
  convention used everywhere else in this firmware. One of its own log
  strings literally names `"cmd_set 0x%02x"`, suggesting it may be a
  motor/ESC-mailbox cousin of the main DUML dispatch mechanism. However:
  it has **zero found callers** within that binary, and no static table
  content was recoverable — so it is a plausible lead, not an enumerable
  command set. See `04_WM260_DAEMON_FINDINGS.md`, "ESC (`cmd_set 0x0c`) —
  no conclusive finding."
- **Battery/ESC firmware images themselves remain high-entropy/encrypted**
  in this firmware package, after the same decrypt step that worked on the
  other modules — their internal command handling could not be inspected
  at all. See `01_BINARY_ANALYSIS_FINDINGS.md` §1.
- A separate, independent firmware package for a different airframe
  (Matrice 600 Pro, a hexacopter) yielded 6 near-identical small modules
  (`m1100`-`m1106`) very plausibly its 6 rotor ESCs — flagged in
  `03_MASTER_COMMAND_LIST_FINDINGS.md` §3 as the single most promising
  concrete target for this gap, not yet pursued to completion.

**Bottom line:** no `(cmd_set 0x0c, cmd_id)` pair is known for this
firmware. This is reported as a genuine, architecturally-explained gap.
