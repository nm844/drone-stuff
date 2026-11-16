# `dji_cht` (camhal_test) deep dive — E2 (aarch64) image

Full disassembly-based follow-up to the light triage pass on `bin/dji_cht`
(E2 `system_files`, `/home/user/wm260_fw/decrypted/e2_extracted/system_files/bin/dji_cht`).
Tooling: `pyelftools` + `capstone` (`CS_ARCH_ARM64`) driven from Python, PT_LOAD-based
vaddr→file-offset mapping, `.rela.plt`-based PLT-stub→import-name resolution, and
`.rela.dyn`-addend search to locate function-pointer tables in `.data`. No
execution of the binary; static analysis only.

**`.gnu_debugdata` confirmed present and useful.** Extracted via
`section.data()` + `xz -d`: a 58 KB mini-ELF, `not stripped`, with a real
`.symtab` (975 symbols, 968 of them functions) covering effectively the whole
binary — this is why every address below has a real name instead of
`sub_XXXXXX`.

## 1. Role/architecture — triage confirmed, with one real correction

The triage's `purpose_guess` holds up under disassembly: this is the
`camhal_test` ("cht") manual/interactive engineering CLI for the Eagle2/E2
camera stack, built from (now 4 confirmed, embedded as literal `__FILE__`-
style strings) source paths under
`hardware/dji/common/camera/dcam_frwk/camhal_test/`:
`base/cht_entry.c`, `base/cht_exp_consistency_test.c`,
**`base/cht_camdev.c`** (new — not in the original triage), and
`eagle2/cht_camdev_platform.c`. `main()`/`_show_usage()` confirm the `-i`
interactive-test-mode flag and a large (~230-entry, per `.rela.dyn` pointer
density in that table's region) array of `{name, pad, test_fn, description}`
structs driving a named test-case menu (`liveview_still`, `liveview_video`,
`still_j_4x3`, `still_jandr_4x3_middle_debug`, …) — exactly matching the
`-i: enable interactive test...` usage string the triage already flagged.

**The correction:** the triage's framing ("creates an event client, creates
a route table... a genuine DUML/message-bus client") is directionally right
but the specific mechanism it implied — registering individual commands via
`duss_event_register_dynamic_command`-family calls, the pattern this project
confirmed for `libduml_frwk.so`'s own exports — **does not apply to this
binary.** See §2.

## 2. `duss_event_register_dynamic_command` family: confirmed ABSENT

Checked three independent ways, all negative:

- `nm -D dji_cht | grep register_dynamic_command` → **no output** (the
  symbol family is not in `.dynsym` at all — not imported).
- `strings -n 6 dji_cht | grep -i register_dynamic_command` → **no output**
  (not referenced even as a `dlsym()`-style string; there is no `dlopen`/
  `dlsym` import either).
- Full `.rela.plt` walk for the three documented variants
  (`duss_event_register_dynamic_command`, `_table`, `_with_user_data`) →
  **zero PLT entries resolve to any of them.**

**Finding: `dji_cht` imports zero `duss_event_register_dynamic_command`-family
symbols, so there are zero `(cmd_set, cmd_id)` pairs of that specific form to
report from this binary.** (Confidence: high — this is a completeness check
over the whole dynamic symbol table, not a sampling.)

## 3. What `dji_cht` actually does instead: a flat function-pointer table passed directly to `duss_event_create_client`

`dji_cht` links two independent `duss_event` bus clients, both built with the
same primitive sequence (`duss_sketch_get_config_file_name` →
`duss_mb_create_route_table` → `duss_event_create_client` →
`duss_event_start_client`, with `duss_mb_destroy_route_table`/
`duss_event_destroy_client` on every exit path):

| Client (owning function) | Called from | Dispatch table arg (`x2`) | Table size arg (`x3`) | Inbound handler? |
|---|---|---|---|---|
| `_create_cht_event_client` (0x744a8) / `_destroy_cht_event_client` (0x749c0) | `_test_f2f_raw_reprocess` (0x8c1d0) — **one call site, one specific test case** | `0x1101f8` (global `.data` array, literal pointer, pre-populated) | `0x71` = **113** (literal immediate) | **Yes — see §4** |
| Local client inside `_f2f_capture` (0x5bb78) | `_test_f2f_bit_true` (0x5e810) — another specific test case | on-stack buffer, `memset()`-zeroed, never written before the call | on-stack buffer, `memset()`-zeroed, never written before the call | No — all-zero table, send-only client |

Both clients pass `x4 = self` (an instance/context struct pointer threaded
through the whole binary) as a generic context argument, and `x5 = &self-\>field_0x2a28` for the library to write the resulting client handle into
— that stored handle (`self + 0x2a28`) is read back later by
`_on_notify_dsp_resources` (0x99ce8) to call `duss_event_send`, confirming
it really is "the" live client handle slot and that `_on_notify_dsp_resources`
belongs to the same client object as `_create_cht_event_client`.

**This is the real registration idiom here: a fixed-size array of function
pointers is built at compile time in `.data` and handed to
`duss_event_create_client()` wholesale as one argument (`x2`) plus a count
(`x3`), instead of one `duss_event_register_dynamic_command()` call per
command.** `duss_event_register_dynamic_command` genuinely isn't needed by
this binary because this older/simpler client-construction path already
takes a full table. (This also means a binary can be a legitimate
DUML/message-bus command-table owner — in the same architectural sense the
task's criterion was after — without ever importing
`duss_event_register_dynamic_command`; worth remembering for future triage
passes over other binaries in this image set.)

## 4. The one real entry: index 112 → `_on_event_debug_tool_cmd`

Walked all 113 slots of the table at `0x1101f8` (stride `0x18`, confirmed by
locating the one `.rela.dyn` `R_AARCH64_RELATIVE` relocation whose addend
equals the table's own base, `0x110c90`+... — actually the table base
itself, `0x1101f8`, is pointed to from a separate global at file offset
`0x10f488`, which is how the table was confirmed as *the* argument passed at
`0x74524`/`0x74560`):

- **78 / 113 slots: `NULL`** (unused)
- **34 / 113 slots: `not_implemented`** (a shared stub function, confirmed
  by name in `.gnu_debugdata`'s symtab, at `0x9d940`)
- **1 / 113 slots (index 112, the last slot, at `0x110c78`): `_on_event_debug_tool_cmd`** (`0x9d950`)

This is the **only** inbound command handler anywhere in `dji_cht`. Its
own source file is confirmed by the literal string it passes to
`duss_log_gen_head` as the log tag: `"hardware/dji/.../cht_camdev.c"` /
`"_on_event_debug_tool_cmd"` (the function's own name, logged verbatim —
i.e. this isn't a guess, the binary names itself).

**Note on numbering:** index `112` is a position in `dji_cht`'s own private,
compile-time-fixed table, handed directly to `duss_event_create_client` for
*this specific client instance* — it is **not** a DUML v1 wire-level
`cmd_set`/`cmd_id` byte pair (those are a different, 1-byte-each space
documented in `00_FRAME_FORMAT.md`). This matches the already-documented
distinction for `dji_navigation`/`dji_flight`'s "private internal event-type
field" in `08_E1E_FLIGHT_AUTOMATION_DAEMONS_FINDINGS.md` — same architectural
pattern, different binary. Whether `112` maps to any *globally* meaningful
value elsewhere in the bus (e.g. something another process references by
the same number) was not determined from this file alone.

### What `_on_event_debug_tool_cmd` does (fully disassembled, `0x9d950`–`0x9da98`)

Signature (inferred from use): `(void *client_handle /*x0*/, duss_event_t *ev /*x1*/)`.

1. Reads a 16-bit-ish length field at `ev+0x10` (`ldr w24, [x19, #0x10]`,
   `x19 = x1 = ev`) — **caller/sender-controlled**, i.e. this value comes
   from whatever sent the event over the bus, not from `dji_cht` itself.
2. Clamps it: `cmp w24, #0x400; mov w8, #0x3ff; csel w8, w8, w24, gt` — i.e.
   `w8 = (w24 > 0x400) ? 0x3ff : w24`. **This clamp has a boundary bug**: it
   only fires when the field is *strictly greater than* `0x400` (1024); any
   value from `0x3fd` to `0x400` (1021–1024) passes through unclamped. See
   §5 for why that matters.
3. Builds a local buffer at `sp+0x90` (size `0x400`, `memset()`-zeroed) by
   writing the clamped length as a 4-byte int at the buffer's start, then
   `__memcpy_chk`-ing `w8` bytes of the event's payload (`ev+0x14` onward)
   starting **4 bytes into that same buffer** (`x22 = (sp+0x90)|4`), with the
   FORTIFY bound (`x3` to `__memcpy_chk`) hard-coded to `0x400` — i.e. the
   buffer's *total* size, not its *remaining* size from the write pointer.
4. **Calls `dcam_dbg_cmd(buf)`** — an imported function, confirmed present
   as a real exported symbol (`dcam_dbg_cmd`, vaddr `0x133e0`) in
   `libdcam_base.so` on this same image. This is the actual command
   interpreter; `dji_cht` itself does no parsing beyond the length-prefixed
   copy above.
5. Logs the result with `duss_log_print`, format string **`"FIX_ME: EXE
   cmd=%s! OK rlt=%d"`** (literal string recovered from `.rodata`, at the
   `cht_camdev.c` source location) — the `FIX_ME` prefix is DJI's own, not
   an artifact of this analysis; it independently confirms the semantic
   ("execute command") without any guessing on my part.
6. Replies via `duss_event_resp_data(client_handle, ev, &"OK", 0x20)` — the
   reply payload is the literal fixed string `"OK"` regardless of
   `dcam_dbg_cmd`'s actual return code (the numeric result only goes to the
   local log, not back to the sender).
7. Returns `dcam_dbg_cmd`'s own return value.

### Reachability (binary-confirmed, not assumed)

- `_create_cht_event_client` has exactly **one** call site in the whole
  binary: `_test_f2f_raw_reprocess` (one specific named interactive test
  case). The client — and therefore this handler's registration — only
  exists for the duration of that one test case being manually run by an
  operator with physical/engineering access to this tool; it is **not**
  created on normal startup or by any other test case.
- Within that window, the handler is reachable by anything that can send a
  bus event landing on local event-type index `112` of this client's route
  table — which other process(es), if any, can address that specific
  client/route-table/index combination was **not determined** from this
  file alone (would need the sender side, e.g. whatever engineering/factory
  tool is meant to drive `camhal_test` interactively, which is out of scope
  for a single-file pass).

## 5. Findings (weakness / impact category / confidence)

| # | Weakness | Impact category | Confidence |
|---|---|---|---|
| 1 | `duss_event_register_dynamic_command`-family is entirely absent from `dji_cht` (not imported, not referenced); its DUML command surface instead comes from a compile-time flat array passed directly to `duss_event_create_client` | N/A — architectural correction to the triage, not a vulnerability | High (verified via `.dynsym`, `strings`, and full `.rela.plt` walk — a completeness check, not a sample) |
| 2 | `_on_event_debug_tool_cmd`'s length clamp (`cmp w24,#0x400; csel ...,gt`) only rejects values *strictly greater than* `0x400`, but the actual copy destination starts 4 bytes into a `0x400`-byte buffer and `__memcpy_chk`'s own FORTIFY bound is hard-coded to the buffer's *total* size (`0x400`) rather than its remaining room from the write pointer (`0x3fc`) — an attacker/sender-controlled length field of `0x3fd`–`0x400` (1021–1024) overflows the destination stack buffer by 1–4 bytes, and FORTIFY's own runtime check cannot catch it because the bound it was told is itself wrong by the same 4 bytes | memory_corruption (stack buffer overflow, bounded to ≤4 bytes) | Medium — the off-by-boundary mechanism itself is directly visible in the disassembly (high confidence it exists as described); practical impact is assessed as low, because the 4-byte spill lands in what this pass's stack-frame reconstruction identifies as alignment padding between this buffer and the next local (a separate 32-byte scratch buffer at a higher offset, with a 4-byte gap to spare) rather than a named variable, the saved-register/return-address area (far below, near the opposite end of the frame), or the stack canary (also far below and on the other side); a full compiler-accurate frame layout to rule out every remaining byte was not attempted, consistent with the scope boundary against building exploit-shaped artifacts |
| 3 | `_on_event_debug_tool_cmd` forwards a caller-supplied, only length-bounded (not content-validated) byte string essentially unmodified into `dcam_dbg_cmd()`, an engineering "debug command" interpreter exported by `libdcam_base.so` — `dji_cht`'s own handler performs no authentication, permission check, or allow-listing before this call (no equivalent of `dji_flight`'s generic authorization gate, or even the key=value sub-handler table `dji_autotest`'s `duss_event_shell` used, was found anywhere in this handler) | Unclear without `dcam_dbg_cmd` itself — see "not determined" below. Reporting the forwarding primitive and its lack of any gate in `dji_cht`'s own code as the finding; **not** claiming what `dcam_dbg_cmd` does with it | High confidence for what's stated (no gate in `dji_cht`); explicitly not extended to `dcam_dbg_cmd`'s own behavior |
| 4 | The reply to every `debug_tool_cmd` invocation is the fixed literal string `"OK"`, independent of `dcam_dbg_cmd`'s real return code (which only reaches the local log, tagged `FIX_ME`) | Minor — information/observability gap, not a security boundary | High |

**On finding #3 and the scope boundary:** `dcam_dbg_cmd` is a real, nameable
export of `libdcam_base.so` (vaddr `0x133e0`) — present on this same disk
image at `/home/user/wm260_fw/decrypted/e2_extracted/system_files/lib64/libdcam_base.so`.
A one-line check of that library's own import list shows it links
`system@LIBC` *somewhere* in the library. **This is explicitly flagged and
stopped at that description, not pursued further**: this pass's assigned
file is `dji_cht` alone, disassembling `dcam_dbg_cmd` itself (to determine
whether that `system@LIBC` import is actually reachable from the command
string `dji_cht` forwards to it, or is used by something unrelated
elsewhere in the library) is a different file's full deep-dive and is left
as a named, concrete follow-up rather than guessed at here.

## 6. `not_determined`

- Whether local dispatch-table index `112` corresponds to any value another
  process on the bus actually sends (i.e. who, if anyone, can reach this
  handler at all) — the sender side wasn't examined.
- Whether `dcam_dbg_cmd()` (in `libdcam_base.so`) actually reaches the
  `system@LIBC` import that library links, or whether that import belongs to
  an unrelated code path — not disassembled in this pass (out of scope: a
  different file).
- Exact byte-for-byte contents of the remaining ~111 unused table slots
  beyond "NULL vs. `not_implemented` vs. real handler" (i.e. whether the
  split between `NULL` and `not_implemented` encodes anything semantically,
  such as "reserved for future use" vs. "deliberately stubbed") — classified
  by pointer value only, not further investigated, since neither value is
  reachable without a registered handler either way.
- The internal-event-type value used by `_on_notify_dsp_resources`'s single
  `duss_event_send` call site — traced the call's argument construction
  (a per-client sequence counter at `self+0x2a1a`/`+0x2a1c`, not a literal
  immediate) but did not find a recoverable literal numeric identifier;
  the `0x51` immediate visible near that call site is `dji_cht`'s own
  internal log-module tag (confirmed reused identically across unrelated
  logging call sites throughout the binary, e.g. in `_create_cht_event_client`),
  **not** a `cmd_set`/`cmd_id` or event-type value — flagging this
  explicitly since it would be an easy false-positive pattern-match for a
  future pass to make.
