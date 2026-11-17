# Cmd Set 0x23 — Smart

Total known command IDs: 3

**Not part of the public `dji-firmware-tools` Wireshark dissector** — this
cmd_set is entirely outside that project's documented `0x00`-`0x11` range,
and distinct from the other two project-found cmd_sets (`0x22` Demo Mode,
`0x51` Route Switch). Every entry below was found by direct disassembly of
this project's own WM260 (Mavic 3) firmware, independently confirmed in
**two** different binaries via **two** different registration mechanisms.
Full methodology and verification history:
`16_EXHAUSTIVE_SWEEP_FINDINGS.md` (Track Q).

The name "Smart" is taken directly from a literal DWARF enumerator found
in one of the two confirming binaries, `SS_MB_CMD_SET_SMART` (value `35` =
`0x23`) — not a project-invented label. Despite the name, this cmd_set has
nothing to do with "SmartCapture"/"ActiveTrack"-style subject tracking; it
is a lifecycle-arbitration protocol for a shared DSP/co-processor resource
contended by multiple camera-pipeline processes.

## Two independent confirmations of the same 3-command set

The same three `(cmd_set, cmd_id)` pairs — `0x20`/`0x21`/`0x22` — were
found registering real handlers in **both**:

1. **`ss_dsp_manager`** (ARM32/E1E build only — the AArch64/E2 build of
   the identically-named binary performs no DUML registration at all).
   Registers via a private, non-imported, two-level `[cmd_set 0..238][cmd_id
   0..255]` dispatch table that structurally mirrors
   `duss_event_register_dynamic_command` without ever calling it — a
   previously-uncatalogued, binary-local reimplementation of the standard
   registration mechanism. Strings in this binary (`ss_dsp_status_msgq`,
   `ss_dsp_status_ctrl_task`, `/system/etc/perception/json/
   ss_dsp_manager_storage.json`) identify it as the manager for a
   vision/perception-camera DSP coprocessor.
2. **`libhyperlapse_eis.so`** — registers via a *different*, HAL-level
   API, `ss_hal_mb_set_req_callback(cmd_set, cmd_id, req_callback, ...)`,
   itself reached only after this library joins the generic DUSS message
   bus (domain `ss_dsp_manager`, role `ss_dsp_manager_service`) using the
   project's mechanism #2 (`duss_mb_create_route_table` +
   `duss_event_create_client`). This binary is **not fully stripped** and
   carries real DWARF debug info and symtab names, giving the
   authoritative `SS_MB_CMD_SET_SMART` enum name and the handler function
   names used below.

Having two separate binaries, using two separate registration mechanisms,
independently land on the exact same `(cmd_set, cmd_id)` triplet is strong
corroborating evidence this is a real, shared wire-level convention — not
a coincidence or a mis-disassembly. It also means **the same three wire
commands can be driven by at least two different local processes**,
consistent with an arbitration protocol where only one participant should
hold "ownership" of the DSP resource at a time (see the per-command
entries below for how that maps onto register/claim/release semantics).

## 0x20 — Register As Smart Owner

- **Handler:** `register_as_dspN_owner_callback` (symtab name, in
  `libhyperlapse_eis.so`) — also independently registered in
  `ss_dsp_manager` (ARM32/E1E) under a stripped, unnamed handler at
  `.text+0x5770` that forwards to `duss_osal_msgq_send` into the
  `ss_dsp_status_ctrl_task` worker thread.
- **Purpose:** a peer process registers itself as the current/candidate
  owner of the shared DSP resource.
- **Evidence:** `libhyperlapse_eis.so`: `ss_dsp_status_ctrl_init` calls
  `ss_hal_mb_set_req_callback(cmd_set=0x23, cmd_id=0x20,
  register_as_dspN_owner_callback)`, with `cmd_set=0x23` matching the
  DWARF enumerator `SS_MB_CMD_SET_SMART`. `ss_dsp_manager`: literal
  `movs r0,#0x23` / `movs r1,#0x20` immediately before a `bl` to a local
  function that structurally matches `duss_event_register_dynamic_command`
  (bounds-checks cmd_set against `0xef`, lazily allocates a 256-slot
  per-cmd_set table, writes the handler pointer at `table[cmd_id]`),
  independently re-derived byte-for-byte on reverify.
- **Confidence:** high on both registration sites and the `(cmd_set,
  cmd_id)` pair. Medium on which binary's semantic label
  ("register-as-owner" vs. `ss_dsp_manager`'s own internal
  `ss_dsp_status_ctrl` naming) is the more complete description — treat
  both as describing the same wire command from two different
  participants' perspectives.
- **2026-11-17 re-confirmation:** a payload-decode pass independently
  re-disassembled `ss_dsp_manager`'s registration call site at
  `.text+0x685a` byte-for-byte (`movs r0,#0x23; movs r1,#0x20;` then
  `bl .text+0xe448`) and confirmed `.text+0xe448` structurally mirrors
  `duss_event_register_dynamic_command` exactly (bounds-checks `cmd_set
  <= 0xef`, lazily `malloc`s a 256-slot/8-byte-stride table per cmd_set,
  logs-but-doesn't-reject on overwrite). **Payload format/fields were
  not resolved** — `ss_dsp_manager`'s handler copies a fixed `0x1c`-byte
  struct from the incoming event and forwards it unparsed via
  `duss_osal_msgq_send`; the actual field meanings live in the worker
  thread that processes it, which was not traced.

## 0x21 — Calling For Smart Owner

- **Handler:** `calling_for_dspN_callback` (symtab name, in
  `libhyperlapse_eis.so`) — also independently registered in
  `ss_dsp_manager` (ARM32/E1E) under a second stripped handler at a
  distinct address, same forwarding-to-worker-thread pattern as `0x20`.
- **Purpose:** a peer process "calls" or claims active use of the DSP
  resource from whichever process currently owns it (per the
  register/claim/release naming pattern across all three commands in
  this cmd_set).
- **Evidence:** same call site/function (`ss_dsp_status_ctrl_init`) as
  `0x20` immediately above, registering `cmd_id=0x21` right after it;
  same `ss_dsp_manager` registration mechanism as `0x20`, confirmed at a
  different handler address.
- **Confidence:** high on both registration sites and the `(cmd_set,
  cmd_id)` pair; same semantic-label caveat as `0x20`.
- **2026-11-17 re-confirmation:** same `ss_dsp_manager` registrar
  (`.text+0xe448`), called at `.text+0x686e`, confirmed byte-for-byte;
  handler at `.text+0x56b4` confirmed to be the same 28-byte
  forward-to-msgq shape as `0x20`'s, with an injected discriminator
  constant of `1` (`movs r6,#1; str r6,[sp,#48]`) distinguishing it from
  `0x20`'s constant `0` — internal-consistency evidence the three
  handlers share one template. Payload format/fields not resolved, same
  basis as `0x20`.

## 0x22 — Finish Working On Smart

- **Handler:** `finish_working_on_dspN_callback` (symtab name, in
  `libhyperlapse_eis.so`) — also independently registered in
  `ss_dsp_manager` (ARM32/E1E) under a third stripped handler, same
  forwarding pattern as `0x20`/`0x21`.
- **Purpose:** releases/finishes the calling process's use of the DSP
  resource, completing the register → claim → release lifecycle.
- **Evidence:** same call site as `0x20`/`0x21`, registering `cmd_id=0x22`;
  same `ss_dsp_manager` mechanism, confirmed at a third distinct handler
  address. `libhyperlapse_eis.so` additionally exports sender-side APIs
  `register_as_dspN_owner` and `remove_dspN_owner_with_cmd_info`,
  consistent with this being a genuine peer-to-peer ownership-arbitration
  protocol rather than a one-directional push.
- **Confidence:** high on both registration sites and the `(cmd_set,
  cmd_id)` pair; same semantic-label caveat as `0x20`/`0x21`.
- **2026-11-17 re-confirmation:** same registrar (`.text+0xe448`), called
  at `.text+0x6884`; handler at `.text+0x55f8` confirmed same 28-byte
  shape with discriminator constant `2`, completing the `0`/`1`/`2`
  pattern across all three commands. `nm` additionally confirms an
  un-stripped symbol `finish_working_on_dspN_callback` at
  `.text+0x66040` in `libhyperlapse_eis.so`, DWARF-typed as
  `status_code_t finish_working_on_dspN_callback(...)`. Payload
  format/fields not resolved, same basis as `0x20`/`0x21`.

## Architecture notes (not separate commands)

- **Unchecked inner index (`libhyperlapse_eis.so`):**
  `ss_hal_mb_set_req_callback` bounds-checks the outer `cmd_set` index
  (`<= 0x4E`) but performs **no bounds check at all** on the inner
  `cmd_id` index before using it (sign-extended to 16 bits) as an
  8-byte-stride offset into a fixed 2048-byte (`0x800`, 256-row) heap
  allocation — a potential out-of-bounds heap read/write if this exported
  symbol is ever called with an attacker-influenced `cmd_id` from outside
  this library. High confidence on the code fact (verified in
  disassembly); medium on real-world reachability, since no out-of-range
  literal was found among this binary's own 3 internal call sites — the
  only way to exercise it with an untrusted value would be via an
  external caller of this exported symbol, which was not traced.
- **Silent handler overwrite:** re-registering the same `(cmd_set,
  cmd_id)` pair in `ss_hal_mb_set_req_callback` only logs a warning; the
  existing handler is silently overwritten, not rejected — a weak
  invariant that could let a second, lower-privilege registrant on the
  same cmd_set quietly displace a legitimate handler, if such a second
  registrant process existed and were reachable (not confirmed either
  way here).
- **No visible input validation in `ss_dsp_manager`'s handlers:** the
  three `0x20`/`0x21`/`0x22` handlers in `ss_dsp_manager` copy a fixed
  `0x1c`-byte struct from the incoming event payload and forward it via
  `duss_osal_msgq_send` with no visible length/range check before the
  copy; whether the worker thread that actually processes it validates
  anything further was not traced (out of scope for this pass).

## Known gap: this cmd_set may have more unmapped commands

Only the three commands above (`0x20`-`0x22`) were found registering real
handlers. `ss_hal_mb_set_req_callback`'s own bounds check (`cmd_set <=
0x4E`) implies this general mechanism could carry many more cmd_sets than
just `0x23`, and nothing rules out this specific cmd_set having additional
cmd_ids beyond `0x22` registered elsewhere in the firmware that this pass's
24-binary sweep did not happen to cover. Treat this as a bounded, not
exhaustive, result for this one cmd_set.
