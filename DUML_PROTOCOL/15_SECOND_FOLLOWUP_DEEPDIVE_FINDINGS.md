# Second follow-up deep-dive: 5 medium-priority binaries, 4 pushed open questions, and a low-priority re-sweep

This document continues directly from `14_FOLLOWUP_DEEPDIVE_FINDINGS.md`
(Tracks A-H) with a second, larger pass: a full disassembly-level deep-dive
of 5 previously triaged-but-not-escalated binaries/libraries
(`libduml_orte.so`, `dji_vtwo_sdk`, `dji_media_server`, the RTOS/Parameter-
Manager bus path, `dji_wlm_slave`), a push on 4 of that document's own
still-open questions (Fast-RTPS network scope, the cmd_set `0x00`
`0x07`-`0x0A` loader/update mystery, the `dji_flight` wp2-registration-loop
lead, and `duss_event_shell`'s `route_control`/message-bus delivery
semantics), and a real second-look sweep over 20 files this project had
previously triaged as "low priority, not escalated."

**Methodology**, unchanged from doc 14: every investigate pass was followed
by one independent adversarial-verify pass (a fresh agent, no access to the
first agent's reasoning, instructed to default to **refuted** unless it can
reproduce the claimed mechanism itself from raw bytes). This run again
caught a real, substantial number of errors — wrong struct-offset
attributions, a claimed table that was actually a different table, a
"missing auth check" that turned out to be two real checks one level
further down, a shell-command argument that turned out to be compile-time
hardcoded rather than attacker-reachable. **Every finding below is marked
confirmed or refuted; refuted claims are kept and corrected, never silently
dropped.** Two verify passes (flagged individually where they occur) were
stopped mid-run by an automated safety-filter false-positive on ordinary,
legitimate security-research text — not a finding about the content itself
— and so remain at their original, not-independently-re-derived confidence.
As with every other document in this project: static analysis only; no
binary was executed; no packet was crafted or sent; no exploit code was
written; `libamt_util.so` (the `e91c9402...` activation/secure-debug/
DJICare TA) was not touched in any track.

---

## Track I — `libduml_orte.so`: dead ORTE/RTPS middleware, superseded by Fast-DDS

Never previously documented beyond a one-line triage entry. `libduml_orte.so`
(E1E: ARM32; E2: aarch64) is a genuine, vendored, standalone C
implementation of the open-source **ORTE** (Open Real-Time Ethernet) RTPS
1.x pub-sub middleware — version string `orte 0.3.4, compiled: Dec 7 2022`
— completely independent of, and architecturally older than, the
`libduml_fastrtps.so` eProsima Fast-DDS stack doc 14 Track A already
documented. Unlike `fastrtps`'s `duss_ps_*` DJI-authored wrapper layer,
`dji_sys`'s imports call this library's native upstream API names
(`ORTEInit`, `ORTEDomainMgrCreate`, etc.) directly — no DJI wrapper exists
anywhere in the firmware for it. The library links only `libc`/`libc++`/
`libdl`/`libm` — no `duss_*`/DUML-bus dependency at all.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `dji_sys` is the only binary (on either E1E/ARM32 or E2/aarch64) with `libduml_orte.so` in its `DT_NEEDED`, and declares exactly 6 ORTE API symbols as dynamic imports (`ORTEInit`, `ORTEDomainPropDefaultGet`, `ORTEDomainInitEvents`, `ORTEDomainMgrCreate`, `ORTEDomainStart`, `ORTEDomainMgrDestroy`) — but **zero relocation entries anywhere in `dji_sys`** (`.rel.plt`+`.rel.dyn`, exhaustively enumerated against the exact `DT_PLTRELSZ`/`DT_RELSZ` byte counts; no packed/Android relocation format present) actually wire any call site to any of them, on either build | architecture_note | high | **confirmed on reverify**, independently, via pyelftools on both ISAs, with positive controls (`duss_event_register_dynamic_command`, `socket`, and all 7 of the sibling `libduml_fastrtps.so` `duss_ps_*` imports *do* show real relocations by the identical scan) |
| The contrast with `libduml_fastrtps.so` is itself the evidence, not an inference: the same `dji_sys` binary has its fastrtps `duss_ps_*` imports genuinely live (real `R_ARM_JUMP_SLOT`/`R_AARCH64_JUMP_SLOT` relocations, confirmed on both ISAs) while its ORTE imports are structurally orphaned — concretely confirming (not merely restating) this project's "superseded by fastrtps" triage hypothesis | architecture_note | high | **confirmed on reverify** |
| `ORTEAppRecvThread` implements a real, bounds-checked RTPS wire parser (checks cursor+declared-submessage-length against total bytes received before dispatch) feeding a 14-way jump table to per-submessage-type handlers — the overall framing is sound | architecture_note | high | **confirmed on reverify** |
| `RTPSIssue` (the DATA/ISSUE handler carrying the actual application payload) reads a 16-bit wire field with **no minimum-value check**, computes `len = field - 16`, and passes that same (potentially-underflowed, ~4GB) value both as `malloc()`'s size and as a raw `memcpy()`'s length, with no check of `malloc`'s return value before the copy | crash_dos (mechanism); real-world severity not established | medium-high on the mechanism; low-medium on real-world severity | **not independently reverified** — explicitly flagged as a caveated lead, not a live bug: nothing currently calls into this dead code path (Finding 1 above), so there is no live caller to exploit it today even if a future change revived this library |
| `ORTEDomainCreate` performs genuine BSD-socket networking — 5 UDP sockets per domain (multicast+unicast metatraffic/userdata/send), real interface enumeration via `ioctl(SIOCGIFCONF/SIOCGIFFLAGS)` filtered to UP+non-loopback+AF_INET, and a real multicast group join (`IP_ADD_MEMBERSHIP`) — it is not a local-IPC shim | architecture_note | high | **confirmed on reverify** |
| The library's only hardcoded address literal anywhere in the binary is `127.0.0.1` (loopback): both `ORTEDomainPropDefaultGet` and `ORTEDomainCreate`'s own fallback set the default peer/multicast-destination address to loopback rather than a LAN-multicast group, and no interface-name/IP allowlist string exists anywhere in this library — contrasting directly with `libduml_fastrtps.so`'s documented `rndis0`/`192.168.100.4` fallback pattern (doc 14 Track A) | architecture_note | medium-high | **confirmed on reverify** |

**Not determined:** the actual bind address for the 4 "Recv" sockets inside
`ORTEDomainCreate` (read from a caller-supplied struct field, not written
there — the ORTE-side analogue of doc 14 Track A's unresolved fastrtps
question); whether the sibling `RTPSVar`/`RTPSVarApp` submessage handler has
the same unchecked-length pattern as `RTPSIssue` (not exhaustively
disassembled); the real-world runtime outcome of the `RTPSIssue`
underflow (whether `malloc()` of a ~4GB request reliably returns NULL on
this bionic/kernel build, turning it into a clean crash vs. an
out-of-bounds read via overcommit) — not something static analysis can
settle, and nothing was executed to check.

---

## Track J — `dji_vtwo_sdk`: a second, independent SDK consumer that reopens dji_autotest's attack surface

`12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md`'s one-line triage of
`dji_vtwo_sdk` ("thin wrapper service around libv2_sdk.so's file-pull
protocol") undersells the binary's real role and is corrected here: it is a
**second, fully independent consumer** of `libv2_sdk.so` — the same SDK
`dji_autotest` uses, already deep-dived in
`09_DJI_AUTOTEST_EXPLOITABILITY_DEEPDIVE.md` — that performs its own
complete bring-up (`set_my_agent_id` → `init_sdk` → `set_eagle_sm_info` →
`init_tcp_manager` → `init_usb_bulk_transfer` → `set_process_handler` →
`start_sdk`), independently reopening the already-documented attack surface
and adding at least one previously-undocumented primitive of its own.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `dji_vtwo_sdk` performs its own full `libv2_sdk.so` bring-up rather than passively riding on another process's session — confirmed by direct disassembly of the literal call sequence, matching `start_sdk`'s own unconditional two-thread spawn (`process_thread`+`router_thread`) regardless of which binary calls it | architecture_note (attack-surface duplication) | high | **confirmed on reverify** |
| `dji_vtwo_sdk` opens its own, independent, unauthenticated **TCP listener on port 10000** — the exact same port already documented for `dji_autotest` — plus its own USB bulk-transfer channel; it does not depend on or reuse another process's socket | unauthenticated_network_listener | high | **confirmed on reverify** |
| Because `dji_vtwo_sdk` independently spawns `libv2_sdk.so`'s `router_thread`, the already-documented `router_thread`→`common_process` primitives — `process_cmd` command injection (type `0x52`, gated by `get_eagle_mode()!=2`) and `process_get_file_list` unguarded directory listing (type `0x11`, no gate at all) — are architecturally reachable **a second time**, through this binary's own channel, under the same preconditions doc 09 already established | command_injection / info_disclosure (reachability duplication) | high (architectural reachability); preconditions unchanged from doc 09 | **confirmed on reverify** |
| `dji_vtwo_sdk` installs its own custom packet handler that forwards types `0x0c`/`0x0d` (`process_pull_file`/`process_push_file`) **directly into `common_process`, bypassing `router_thread`'s allow-list entirely** — making `process_push_file` (client-supplied file write) reachable through this binary even though doc 09 explicitly concluded it was "not reachable any way" via `dji_autotest` | unrestricted/whitelisted file write — newly-confirmed reachability | high (dispatch-path reachability); gate behavior (the `is_file_accessable()`/`eagle_mode` whitelist doc 09 already characterized) inherited, not re-derived | **confirmed on reverify** |
| `dji_vtwo_sdk` implements its own, separate, **completely ungated arbitrary-file-read primitive** — the `RETR` command of a hand-rolled packet-type-`0x55` file-pull state machine that does **not** call `is_file_accessable()` or `get_eagle_mode()` at all; the only checks before streaming a client-named file's full contents back are `access(path,F_OK)` and a directory exclusion. Broader than the already-documented, whitelist-bounded `process_pull_file`: no boot-flag precondition, no filename whitelist, reachable on stock retail firmware | info_disclosure (unrestricted arbitrary file read/exfiltration) | high as originally stated | **not independently reverified** — this is one of the two safety-filtered verify passes; the adversarial reverify step was interrupted by an automated safety-filter false-positive on legitimate security-research text, not a finding about the content itself |
| The same type-`0x55` dispatcher performs a fixed-size, FORTIFY-checked (`__memcpy_chk`) copy of a client-supplied, length-prefixed payload into an 0x8c-byte stack buffer; an oversized length aborts the process rather than corrupting memory — a plausible remote crash, not memory corruption | denial_of_service | medium (the abort-on-overflow mechanism is directly confirmed; full attacker-control of the length field was not traced upstream of this function) | **not independently reverified** |
| Packet type `0x80` frees a shared-memory handle (`sm_free`) taken directly from a client-supplied field, with no visible ownership/validation check in the dispatcher itself | potential use-after-free / handle confusion (unconfirmed lead) | low | **not independently reverified** |

**Not determined:** whether `dji_autotest` and `dji_vtwo_sdk` are ever
started concurrently on a real unit (no service-launch script for either
binary exists in this extraction, so their identical `init_tcp_manager(.,
10000)` calls' bind-conflict behavior is unresolved); the full internal
logic of `process_push_file` beyond its `is_file_accessable(mode=1)` gate
call (doc 09 never disassembled this function's body either); whether the
type-`0x55` length field is fully attacker-controlled all the way from the
raw receive call; `sm_free`'s own internal handle-ownership validation.

---

## Track K — `dji_media_server`: new daemon, two confirmed memory-safety bugs

Never previously deep-dived beyond triage. `dji_media_server` imports zero
`duss_event_register_dynamic_command`-family symbols; it registers its
DUML/message-bus identity via `duss_mb_create_route_table("media_service",
"media_server",...)` + `duss_event_create_client`/`duss_event_start_client`
— the same alternate client-construction idiom this project has already
documented for `dji_navigation`/`dji_rcam`/`dji_cht`. A single init routine
wires multiple camera/media `_on_event_*` handler functions into **at least
3** separate static dispatch structs in `.bss` (an initial pass claimed
exactly 13 handlers across exactly 2 structs; reverify found this
undercounts both the struct count and, on the 2 originally-claimed structs
themselves, mis-attributes several handlers to the wrong struct and
collapses 2 pairs of genuinely separate, separately self-logged functions
into false "merged" entries — the real handler-to-struct-to-offset mapping
needs a dedicated re-pass and should not be cited as "13 handlers across 2
structs").

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `dji_media_server` imports no `duss_event_register_dynamic_command`-family symbol anywhere in its full 256-row dynsym/137-entry `.rel.plt` import table — the project's "literal cmd_set/cmd_id before `bl register_dynamic_command`" pattern does not apply to this binary | architecture_note | high | **confirmed on reverify** |
| It registers via `duss_mb_create_route_table("media_service","media_server",...)` + `duss_event_create_client`/`duss_event_start_client` — the same alternate client idiom already documented on other daemons, wiring handler functions into fixed field offsets of **multiple** static dispatch structs in `.bss` rather than a flat cmd-id table | architecture_note | high | **confirmed on reverify as to the registration mechanism**; the specific "13 handlers across exactly 2 structs" headline count is **REFUTED** — reverify found a 3rd (and likely a 4th) struct built by the same init routine, 4 handlers mis-attributed to the wrong struct in the original count, and 2 of the originally-claimed "merged" dual-named entries were actually 2 pairs of distinct, separately self-logged functions the exidx-based validation method couldn't tell apart; treat the exact handler count/table layout as unresolved pending a dedicated re-pass, not as "13" |
| `_on_event_camera_tlv` and a `dm368`-live-streaming handler both `calloc()`+`memcpy()` a buffer sized directly from an **attacker-controlled 32-bit field** in the incoming message, with zero validating instruction against the message's real received length before either call — contrasted directly, in the same binary, with 4 *other* handlers that do reference the project's "msg_len < requested, invalid input parameters" validation-log string before acting | memory corruption / out-of-bounds read | high for the missing-validation-before-use claim; medium for the practical reachability of the integer-overflow sub-case specifically | **confirmed on reverify as a lead** — missing-validation mechanism is high confidence; whether the allocated/copied buffer is ever echoed back to the sender (converting this into a demonstrated info-disclosure outcome, not just an OOB-read mechanism) was **not independently reverified** |
| A second, independent out-of-bounds-read-capable parsing path in the same `_on_event_camera_tlv` handler: a TLV-entry scan walks up to an attacker-controlled count byte (0-255) using an 8-bit-wraparound running offset, never compared against the message's actual length | out-of-bounds read / parser confusion | high for the unbounded-read mechanics; medium for real-world reach | **not independently reverified** |
| No `system`/`popen`/`exec*` primitive anywhere in `dji_media_server`'s import table; the only code-loading primitive is `dlopen()` against a small set of compile-time-fixed library paths, selectable (which of 3 "WorkMode" libraries loads) via an attacker-reachable mode-switch path, but the path strings themselves are compile-time constants | negative finding — reduces command-injection-style attack surface | high | **confirmed on reverify** |
| By contrast, `_on_event_dm368_set_codec_param` *does* explicitly range-check both of its input fields before acting — this daemon is not uniformly unsafe | negative/control finding | high | **confirmed on reverify** |
| `dji_media_server` parses two local JSON config files (`/system/etc/dji_media_service.json`, `/system/etc/dji.json`) via a vendored `nlohmann::json` parser for feature-flags/workmode selection — local filesystem trust boundary, not remote wire input | informational | high for the mechanism; not determined whether any remote path can influence these files' contents | **confirmed on reverify** |

**Not determined:** the literal wire-level DUML `cmd_set`/`cmd_id` byte
pairs for any of these handlers (the mapping from an incoming cmd_id to a
dispatch-struct field offset almost certainly lives in a shared library
this binary links, not examined in this pass — their names are strongly
semantically consistent with Camera/DM368-ISP functionality, but that is
inference from naming, not a confirmed numeric mapping); whether the
calloc/memcpy buffers are ever echoed back to the sender; whether the
32-bit-field integer-overflow sub-case of the calloc call is reachable in
practice (depends on whether an outer transport layer caps the field
first, not examined).

---

## Track L — The RTOS/Parameter-Manager bus path: cmd_set `0x03`'s "Config Table" family, tied to a real implementation for the first time

Direct follow-up to doc 14 Track B, which left open whether `test_rtos_raw`
(initially suspected, by filename alone, to be a sibling of the RTOS
co-processor's `rtos_debug`/`librtos.so` reboot/ramdump tool) was a second,
DUML-bus-reachable route into that RTOS core. **It is not.** `rtos_debug`
self-identifies in its own `--help` text as `test_rtos` — a different
string from `test_rtos_raw` entirely — and `test_rtos_raw` is independently,
conclusively identified (via its own QA driver script, `test_pm.sh`) as a
**`dji_perception`** (camera/vision daemon) Parameter-Manager test harness,
architecturally unrelated to the flight-control RTOS co-processor. This
closes doc 14 Track B's open question in the negative, but the deep-dive
into *what* `test_rtos_raw` actually does produced this project's first
real firmware implementation of the generic "Config Table" command family
already catalogued (name-only) in `cmdset_03_Flight_Control.md` — see the
pointer added there.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `test_rtos_raw` registers exactly 16 `(cmd_set, cmd_id)` pairs on the DUML bus: cmd_set `0x03` cmd_ids `{0xE0,0xE1,0xE2,0xE3,0xE4,0xF3,0xF7,0xF8,0xF9,0xFA,0xFB,0xFC}` (12 distinct handlers) plus cmd_set `0x01` cmd_ids `{0x40,0x41,0x42,0x43}` (4 slots that are exact aliases — sharing the identical handler/ack-helper function pointers — of 4 of the cmd_set-`0x03` entries). **None of the 12 distinct handlers reach any RTOS reboot/ramdump/recover-equivalent operation**, directly or indirectly: the binary imports no `ioctl` symbol at all, and no `/dev` substring exists anywhere in it | architecture_note | high | **confirmed on reverify** |
| The 12 distinct cmd_set-`0x03` handlers match, slot-for-slot, this project's own already-documented generic "Config Table" command family (`cmdset_03_Flight_Control.md`: `0xE0`-`0xE4`/`0xF3`/`0xF7`-`0xFC`, "Get/Set/Reset Tbl/Item Attribute/Value", "Read/Write/Reset Param(s) By Hash") — the first time this project has traced that family's wire-level dispatch down to an actual, named firmware implementation. It reveals the family is a **generic, reusable RPC surface any Parameter-Manager-linked daemon can register under its own bus identity**, not an implementation exclusive to the flight controller, despite `ALL_COMMANDS.csv`'s "Flight Controller" typical-receiver label for that row (that label remains accurate for the *flight-controller's own* registration of this same generic family; it is not the only registrant) | architecture_note | high | **confirmed on reverify**, independently (the real-world confirmation is unusually strong here: the on-device QA script `test_pm.sh` drives `test_rtos_raw` over the **real DUML bus** via `dji_mb_ctrl -s 03 -c f8/f9 ...`, using the exact cmd_set/cmd_id numbering this pass derived from pure static disassembly) |
| A methodology correction for future passes on this or similarly-built binaries: the project's established "literal cmd_set/cmd_id immediate before a direct `bl` to `duss_event_register_dynamic_command`" recovery technique can miss registrations reached only through a function-pointer vtable | architecture_note | — | **REFUTED on reverify** — an independent brute-force scan (validated first against `dji_sys`'s known baseline) found the real registration call site (`blx #0x1794` at vaddr `0x924c`) is in fact directly discoverable by plain branch-target scanning; the vtable-dispatch mechanism described is real (it coexists, reached via `pm_create_agent`) but does not demonstrate the claimed "silently misses it" failure mode — a direct scan already finds this binary's registration site |
| The write-capable commands in this family (`0xE3`/`0xF9`/`0xFC` and their cmd_set-`0x01` aliases) write into live in-memory parameter blocks with **"no authentication/authorization check visible anywhere in that path"** | missing_authz | — | **REFUTED on reverify** — two real, distinct checks sit between the generic parse helper and any write: (1) a writable-vs-read-only flag-bit gate (function at vaddr `0x5f08`/`0x60cc`), and (2) a per-item, per-sender **privilege-level check** (`0x5c1c`, masking an item's flags against a caller-supplied privilege value threaded in from the request), backed by an on-disk per-parameter `auth` attribute parsed into an 8-value `AUTH_NONE_ACCESSIBLE`..`AUTH_SDK_L2` enum. Corroborated black-box by the genuine on-device QA driver (`test_pm.py`, re-extracted and byte-diffed), which explicitly asserts a write to a lower-privilege parameter over this exact cmd path **fails**. The finding's categorical "no check anywhere" claim is false for this registrant; whether `dji_perception`'s own production binary (not examined in this pass) implements the identical gate for its *real*, non-test parameters under the same cmd_set is not determined |

**Not determined:** whether `test_rtos_raw`/`test_pm.sh` are wired into any
boot-time service (no matching `.rc` entry found; their own content — stop
the real `dji_perception`, substitute this test harness, restore
afterward — strongly suggests a manually-invoked factory/QA tool, not
something that runs during normal flight); whether `dji_perception`'s own
production binary has the same (confirmed-present, in `test_rtos_raw`) or a
weaker authorization gate for its real runtime parameters under this same
command family; whether the three host-id "channel" entries in
`param_manager.json` (`djigo`/`assistant`/`dcs`, host ids 2/10/23) are
enforced as an actual sender-identity allowlist anywhere in the dispatch
path, or are purely descriptive metadata.

---

## Track M — `dji_wlm_slave`: E2's wireless-link-manager slave, and its unauthenticated inter-processor sync channel

Refines `12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md` §6's open question:
`dji_wlm` (E1E, 32-bit ARM) and `dji_wlm_slave` (E2, aarch64) are two
**separately-compiled binaries for two different CPUs**, sharing one
source tree, with role selected purely by a JSON config key
(`common.role`: `"master"` on E1E's `/etc/wlm_cfg.json` vs. `"slave"` on
E2's) — not "the same ELF under a different role" as previously
speculated. `dji_wlm_slave` never joins the DUML message bus itself (zero
`duss_event_*`/`duss_mb_*` imports); it is a `ds_slave` receiver that
terminates an inter-processor "`ds_comm`" sync protocol pushed to it by
`dji_wlm` (E1E) — the binary that *is* a DUML bus client per §6 — so
externally/RC-influenced DUML content can reach `dji_wlm_slave`'s parser
indirectly through that pipe even though it never parses a DUML frame
itself. (This analysis was possible byte-exact, not from guesswork: the
binary carries a full `.gnu_debugdata` AOSP MiniDebugInfo blob that
decompresses cleanly and restores every local symbol/address — a technique
likely reusable on other E2/aarch64 binaries in this firmware.)

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| The `ds_comm` inter-processor message format `dji_wlm_slave` accepts from `dji_wlm` (E1E) is authenticated by nothing but a fixed, public 16-bit magic constant (`0xBEEF`) and a 1-byte msg-id range check; the header's own sender/receiver identity nibbles are read and logged but **never compared against the expected peer** before the message is acted on — no sequence number or cryptographic check exists at all | missing authentication / spoofable inter-processor control channel | high for the mechanism; medium for real-world severity, since the underlying transport's own reachability scope was not fully resolved | **confirmed on reverify** |
| The one wired-up `ds_comm` handler (msg-id 0) passes an untrusted offset/len pair, read directly from the inbound buffer, into `libwlm.so`'s `wlm_share_info_write_byte` with no clamp in `dji_wlm_slave` itself against the real size of the shared-memory region | unchecked length/offset field reaching a shared-memory write primitive | high for the missing check at this layer | **REFUTED on reverify, with a resolved "not determined"** — tracing one hop further into `libwlm.so` itself (not examined in the original pass) finds a real, complete bounds check (range-checks len to `[1,1024]`, checks offset non-negative, checks for signed-overflow, and compares the sum against the shared-memory region's own real size field) before the actual `memcpy` — the untrusted offset/len **cannot** drive a write outside the mapped region through this path; the clamp exists, just one library hop further than originally traced |
| The second `ds_comm` msg-id slot (msg-id 1) has "a reserved handler-table entry" that resolves to a NULL function pointer — a documented, compile-time dormant slot | architecture note — dormant message-id slot, not a vulnerability | high (as originally framed) | **REFUTED on mechanism, true on outcome** — there is no second compile-time table row for msg-id 1 anywhere in static data; the real per-instance handler table lives at a *heap* offset (`instance+0x50`) that is simply never initialized anywhere in the binary and stays at its `calloc`-zero value — an uninitialized field, not a documented reserved slot. The dispatcher does null-check the handler pointer before calling through it, so msg-id 1 genuinely is a safe, logged no-op in this build — that conclusion survives, just for the right reason |
| A failed message parse inside `wlm_parse_internal_msg` is logged internally, but the only caller (`wlm_recv_msg_sync`) collapses the parse-failed and parse-succeeded paths onto the same return code — parse failure and success are externally indistinguishable from the return value alone | error-handling / observability weakness | high | **confirmed on reverify** |
| The data-forward/liveview direction is the mirror image of the ds_slave finding: here `dji_wlm_slave` is the data **source** (locally-produced E2 camera/liveview buffers, forwarded outward toward E1E), with its own explicit frame/slice-index continuity checks rather than blind forwarding — lower attacker-reachability | architecture note | medium | **not independently reverified** |

**Not determined:** the exact underlying transport bound to the `ds_comm`
channel's logical slot name (`"selfdefine3"` resolves inside `libwlm.so`'s
own link-abstraction layer to one of several candidate transports —
USB bulk, a local FIFO, or a fixed-IP UDP pair at `192.168.100.3↔
192.168.100.4:50000` — which one was not traced through `libwlm.so`'s
internal link-resolution code); whether the share-info fields that travel
this channel are themselves reachable end-to-end from RC/app-originated
DUML traffic through `dji_wlm`'s (E1E) send side (not examined in this
pass).

---

## Track N — `duss_mb_control_route_item`/`duss_event_shell`'s message-bus delivery scope

Direct follow-up to doc 14 Track D's `route_control` finding and its one
open "not determined" item (the real delivery scope of
`duss_mb_send_v2`/`msg_send` — local-only vs. genuinely cross-process).

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `duss_mb_control_route_item`'s internal enable/disable sub-handlers each contain hard process-abort gates (`exit(-1)`/`abort()`) on internal-consistency-check failure — elevating "`route_control` disable/enable" from pure missing-authz to a **directly reachable crash-DoS within the same call** | crash_dos | high | **confirmed on reverify** |
| Disabling a route item zeroes the item's channel-reference field (`item+0x134`), but neither the fast-path router (`duss_mb_router_forward`) nor the generic send path (`duss_mb_send_v2`) ever null-checks that field before dereferencing it when later, *unrelated* bus traffic matches that item by destination device-id — making disable a genuine crash-DoS primitive against subsequent traffic, not merely a benign state toggle | crash_dos | high for `duss_mb_send_v2` (direct, unconditional call chain); medium-high for `duss_mb_router_forward` (mechanism fully disassembled; only the exact runtime wiring that selects this specific forward path was not independently confirmed) | **not independently reverified** — this is the second of the two safety-filtered verify passes; the adversarial reverify step was interrupted by an automated safety-filter false-positive on legitimate security-research text, not a finding about the content itself |
| `duss_event_send_v2`→`duss_mb_send_v2`→`duss_mb_send_in_block_mode`/`no_block_mode` genuinely dispatches, via an indirect per-channel-type function-pointer table, to real OS-level transport functions performing actual `socket()`/`send()`/`sendto()`/`libusb_bulk_transfer` I/O — refuting a purely local, in-process-only delivery model for this path | integrity / architecture_note (message-bus delivery scope) | high for the mechanism; medium for generalizing to every specific named route item | **REFUTED, with a corrected mechanism that still supports the broader point** — the specific named transport functions cited (`tcp_send`, `usbsocket_send`, `adb_send`, etc.) are **not** what the dispatch table actually reaches; a full linear sweep of the library found zero call sites to 6 of the 9, and the other 3 have only orphaned, unused GOT slots. The real mechanism is a **two-level dispatch** — a packet-format table (keyed by `"Logic"`/`"NAL"`/`"MAVLink"`/etc.) that selects a second, 16-entry **channel-type** table (`Local_Channel`, `IP_channel`, `UART_Channel`, `USB_Channel`, `LIBWLM_Channel`, etc. — distinct, unexported functions) — and disassembling `IP_channel`'s own `open`/`send`/`recv` vtable slots directly confirms real `socket()`/`sendto()`/`select()`/`recvfrom()` calls, so the underlying architectural conclusion (block-mode delivery is not purely local/in-process) **is** independently reproducible, just through a different, previously-unidentified mechanism. Separately, `duss_mb_send_in_no_block_mode` — the other half of the originally-claimed mechanism — uses **no** transport dispatch of any kind: it is unambiguously local-only (`calloc`+`memcpy`+an OSAL message-queue enqueue), the opposite of what was claimed for that function specifically |
| `duss_mb_router_forward_directly` shows the same `item+0x134`-after-disable hazard a third, independent time, passing the (possibly-NULL) value into a second, separately-indexed indirect call whose exact target was not resolved | crash_dos (unconfirmed downstream effect) | low-medium | **not independently reverified** |

**Net resolution of doc 14 Track D's open delivery-scope question:**
message-bus delivery is confirmed non-local for at least the block-mode
send path (real socket/USB I/O is genuinely reached, via a two-level
format-then-channel dispatch distinct from the specific functions
originally guessed), but the no-block-mode send path is confirmed
local-only — the honest answer is "it depends which of the two send modes
a given caller uses," not a single project-wide answer either way.

---

## Track O — Low-priority re-sweep: 20 previously-triaged files re-checked

A systematic second look at files `12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md`
had triaged as low-priority/not-escalated, specifically checking for
anything the one-line triage characterization might have missed. 18 of 20
files held up exactly as triaged (confirmed inert/low-risk at the import
level: `dji_mb_parser`, `dji_kmsg`, `dji_top`, `libduml_f2d.so`,
`libduml_fb.so`, `libduml_async_remux.so` — confirmed **dead, unused** code,
referenced nowhere else in the firmware — `libduml_vcodec.so`,
`libduml_watermark.so`, `dji_pbt`, `libduml_audio.so`, `libDjiMediaPlayer.so`,
`lib_hal_dji_ycc.so`, plus `dji_bb_spliter`/`dji_mb_parser`/`dji_fw_load`
below). Two files (`dji_ml_gtest`, `dji_ppt`) had an initial escalation
claim that did **not** survive adversarial reverify, and are corrected
below rather than silently dropped.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `dji_ml_gtest` is a genuine, stock Google Test harness that also fully imports the real client-side DUML event-bus/DSH API (`duss_event_create_client`, `duss_dsh_initialize`, etc.) — an initial pass concluded that running it with no arguments therefore "establishes a live, unauthenticated DUML-bus client connection and issues real 'link v1' commands" | missing_authz / attack-surface (local-shell-gated bus client) | medium-high (as originally stated) | **REFUTED, with a narrower surviving fact** — a combined constructor dispatched automatically via gtest's own virtual-method setup *does* unconditionally open a real HAL device and a real DSH channel/callback registration on a bare run (that narrower, genuine local-code-execution-gated action is confirmed and worth noting on its own). But `duss_event_create_client`/`duss_event_start_client` and 4 sibling bus-client symbols are imported yet **never called from anywhere in the binary** (zero call sites found via an alignment-independent brute-force branch scan) — they are dead imports. The one place that would send a bus command (`gtest_link_v1_send`) first checks a global client-handle pointer that is never populated, and deterministically takes the "handle not initialized" error branch instead of transmitting. **This binary does not establish a live DUML event-bus client connection or send a bus command on a bare run** — it does unconditionally touch a real HAL device and DSH channel, which is the corrected, narrower finding |
| `dji_ppt` (an aarch64 post-processing image-pipeline test CLI) builds and runs `system("cat <dir>/bdaf_raw.json")` via its `-c bdaf` test option, with `<dir>` taken from a struct field whose ultimate origin (CLI arg vs. config value vs. fixed constant) was not traced in the original pass | command-injection-shaped code pattern (CWE-78), reachability unconfirmed | plausible, as originally stated | **REFUTED** — tracing the field to its origin (hand-disassembled back through the harness's shared test-dispatch plumbing) shows `<dir>` is a fixed, compile-time string baked into `.rodata` and copied into the struct during static initialization, before argument parsing even runs; none of `dji_ppt`'s 19 `getopt` option handlers, and no config-file parser (none exists in this binary), ever write to that struct field. `<dir>` is **not attacker-influenceable through any discovered code path** — the `system()` call is real, but this is a non-finding as a security issue: an engineering test binary that happens to contain a `system()` call with a hardcoded, non-functional-looking argument |
| `dji_bb_spliter`'s own code is confirmed inert (no DUML/network imports at all), but it is not purely a manually-invoked tool as "offline .bb-log-file splitter" implies: `gimbal_log.sh` invokes it **automatically**, building its input path via unquoted command substitution (`log_bb_file=$(cat $log_bb_num_file).bb`) and interpolating it **unquoted** into the command line | unsafe shell-variable quoting / potential path-traversal-or-argument-injection pattern | high for the shell-script fact itself; low/unknown for real-world exploitability | **confirmed on reverify** — whether `/blackbox/dji_blackbox/latest`'s content (the ultimate source of the unquoted value) can ever be influenced by anything other than the trusted blackbox-logging daemon was not traced in this pass |
| `dji_fw_load` is structurally and behaviorally identical to the already-escalated `dji_fw_verify` (`12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md` §8, HIGH priority): both are thin CLI wrappers that forward CLI-supplied name/chunk/offset values across a library call boundary into `libfw_util.so` with zero local validation (no `strtol`/`atoi` imported at all) | architecture_note / triage-process inconsistency | high for the structural-identity claim; medium on real-world severity (no automated/remote invocation path for this CLI itself was found, same local-shell-only gate as `dji_fw_verify`) | **confirmed on reverify** |
| `dji_sw_uav` is confirmed to be a genuine, live DUML-bus participant (imports `duss_event_create_client`/`_send`/`_start_client`, `duss_mb_create_route_table`) despite having no CLI parsing and no "Usage" string — a sender/reporter only (`duss_event_register_dynamic_command` absent, so it cannot be addressed as a command target), consistent with (not contradicting) its "sliding-window reliability monitor" role | architecture_note (clarification) | high | **confirmed on reverify** |
| `libduml_osal.so`'s cgroup CPU-quota functions (used by "nearly everything" in this firmware) implement their writes by `sprintf`-building an unescaped shell command (`"echo %d > %s"`) and running it via `system()`, then reading the result back via a second `popen()` — rather than writing the already-known sysfs path directly — with **no escaping or validation of the path argument** inside this shared helper | architectural/defense-in-depth weakness (latent OS command-injection primitive) | medium — the shell-out pattern is directly confirmed; exploitability is not confirmed because every caller examined supplies only integers, and this pass covered only this one library file, not every other binary that calls into this exported API | **confirmed on reverify** |
| `libduml_ffremux.so`'s FFmpeg demux/recovery path (`avformat_open_input`/`av_read_frame`/etc.) is live, untrusted-container-parsing code, not dead code and not limited to remuxing the device's own trusted recordings as the one-line triage implies — but every call site in this firmware that feeds it an externally-chosen file path is an engineering CLI (`test_imgtec_vdec`) requiring pre-existing local shell/ADB access, not a DUML-bus or network path | memory_corruption / denial_of_service via malformed MP4/MOV parsing (FFmpeg demuxer historical CVE class), gated by a local-access precondition | medium | **confirmed on reverify** |
| `libduml_dsocket.so`'s `SCM_RIGHTS` Unix-domain-socket file-descriptor-passing primitive (`duss_util_send_fd`/`duss_util_recieve_fd`, fixed path `/tmp/UNIX.domain`) performs **no peer-identity verification whatsoever** (no `SO_PEERCRED`, no `getpeereid`, no `SCM_CREDENTIALS` check) before handing a connecting local peer a file descriptor | missing authentication on a local IPC mechanism (CWE-306-style) | confirmed at the code level; plausible/unconfirmed for real-world impact | **confirmed on reverify** — caveat, reported honestly rather than omitted: a reverse-dependency scan of every binary/library already unpacked on either image found **zero other references** to this library by name, `NEEDED` linkage, or either exported symbol — nothing in the already-extracted firmware tree is confirmed to actually load or call it, so live reachability on this image is unconfirmed, not disproven |

**Not determined (Track O as a whole):** `<dir>`'s non-finding status for
`dji_ppt` was traced only for the `-c bdaf` test case specifically, not
every one of its ~28 other test handlers; `libduml_dsocket.so`'s real-world
reachability on a shipped device; whether `/blackbox/dji_blackbox/latest`'s
content can ever be externally influenced.

---

## Track P — Corrections to 3 pushed-on open questions

### P.1 — Fast-RTPS network scope (doc 14 Track A's biggest open question): still **UNRESOLVED**

A dedicated push on doc 14 Track A's single biggest open question —
whether DJI's `duss_ps_fastdds.cpp` wrapper restricts the Fast-RTPS
transport to loopback/`192.168.100.x`, or leaves it at stock,
unrestricted-across-all-interfaces defaults — produced an initial pass
with 6 sub-findings, of which 4 did **not** survive independent reverify:
a "zero `interfaceWhiteList`-population instantiations exist anywhere"
claim (refuted: such instantiations do exist, including a live, fully
functional XML-driven `interfaceWhiteList` parser compiled into both
builds — though DJI's own traced runtime call path does not appear to
route through it); a "DJI explicitly constructs exactly 4 transport
descriptors and never constructs `UDPv4TransportDescriptor`" claim
(refuted: the real function is a 7-way runtime switch, not a single linear
builder, and at least one selector path can leave eProsima's stock
`UDPv4TransportDescriptor` — with its own default IPv4 multicast
discovery — registered via a conditional `useBuiltinTransports` gate);
the resulting "not restricted to loopback/`192.168.100.x`, but also not
stock IPv4-multicast defaults" net-resolution claim (refuted on
reverify — a UDPv4 transport, via the `useBuiltinTransports` path, is
*not* reliably absent, directly contradicting this framing); and an
Android-system-property-poll sequencing claim (refuted — the two things
described are mutually exclusive switch arms, never sequential). 2
sub-findings did survive independent reverify: the TCP transports (v4/v6)
really do come up with an empty `listening_ports` list via this specific
builder path (confirmed medium-high), and no
`DEFAULT_FASTRTPS_PROFILES.xml` exists anywhere in this firmware package
to override any of this at runtime (confirmed high).

**This question remains open, not answered.** Do not treat any "definitive
answer" framing from an earlier pass as settled. The honest state after
two passes: DJI's own confirmed participant-construction call path does
not appear to populate `interfaceWhiteList` and does not open a TCP
listening socket via this one builder function, but whether a genuine,
unrestricted default UDPv4 transport (with stock multicast discovery) ends
up registered depends on a runtime selector byte and an Android property
("`dds_prop`"/"`dds_init_ready`") whose actual value in a running system
was not determined from static analysis alone — a materially more
complicated picture than either pass's own headline claim, in either
direction.

### P.2 — `dji_flight`'s wp2-registration-loop (doc 14 Track H): the specific claim was wrong

> **Erratum (added this pass):** see this section for a correction to
> Track H's `api_wp2_get_wp_index_in_list`/19-entry-table lead — the
> specific follow-up claim about its `ctx+0x28` indirect-call target was
> independently re-examined and found incorrect. Track H's own text above
> is left as originally written; this note and the fuller correction below
> are the only changes.

A dedicated push on doc 14 Track H's remaining open thread (the identity
of the function reached via `api_wp2_get_wp_index_in_list`'s `ctx+0x28`
indirect call) confirmed the prior pass's **specific claimed call site was
wrong**: of the two addresses it cited, one (`~0x78a90`) is a large,
unrelated object-constructor function containing no such call pattern at
all; the real function (`~0x481a0`) does contain the `ctx+0x28` pattern,
with exactly one real caller. Tracing that caller's `ctx+0x30` sibling call
(not `ctx+0x28`) does lead to a concrete, address-level link to
`api_wp2_get_wp_index_in_list` — but the ultimate call target (the return
value of the `ctx+0x30` call) could not be resolved without disassembling
a different shared library, and no generic "loop over the wp2 table" was
found anywhere in the binary even searching by indirect/computed base
address. A real, unrelated 12-entry "broadcast to vector of listeners"
thunk family does exist in `dji_flight`, but no tie to wp2 was found for
it either. **Net: the wp2-registration-loop question stays open** — the
one concrete, actionable correction is that Track H's specific `0x78a90`
citation and its "`ctx+0x28`" framing should not be reused or cited as
established in any future pass; see Track H's methodology note (the
ldr-delta+add-pc PIC-addressing gotcha) for why a plain address-search can
mislocate functions like this.

### P.3 — cmd_set `0x00` `0x07`-`0x0A`/`0x40`-`0x43` (doc 14 Track E): two false negatives corrected, mystery still open

A dedicated push on doc 14 Track E's loader/update command mystery
corrected two of this project's own prior conclusions. First,
**`/system/etc/upgrade.json` and `/system/etc/dji.json` do exist** — on
both E1E's and E2's raw `system.img` (found via `debugfs`-level inspection
of the raw filesystem, not the pre-extracted `system_files/` tree the
original pass searched, which has no `/etc` directory at all for E1E).
Second, **the plugin libraries `upgrade.json` names are also present**,
with an exactly matching 15-function ABI (`check_online`/`init`/
`prepare`/`negotiate`/`transfer`/`upgrade`/`get_version`/etc.):
`libeagle_md_up.so`, `libstandard_v2_md_up.so`, `libstandard_md_up.so` (all
named in the config) plus a 4th, `libsubdev_md_up.so`, hardcoded as a
`dlopen()` default path independent of the JSON config entirely. None of
the 4 upgrade-chain libraries (`libupgrade_register.so`,
`libupgrade_communication.so`, `libupgrade_commu_demo.so`,
`libupgrade_upgrade.so`) use the classic per-cmd_id bus-registration
pattern; the one that does touch the DUML bus
(`libupgrade_commu_demo.so`) registers as a generic client whose channel
selector is computed at runtime, not a static literal — meaning a literal
byte-search for `0x07`-`0x0A` was structurally incapable of finding it in
this code even if it is real and live there.

**The meaning of cmd_set `0x00`'s `0x07`-`0x0A` (and `0x40`/`0x41`/`0x43`)
remains unresolved** — no literal, traced wire-level construction of any
of these cmd_ids was found anywhere in the 4 upgrade libraries or their
dlopen'd plugins. The best surviving hypothesis (medium confidence,
circumstantial — supported by a `loader_needed` config flag present only
for one peripheral MCU module, and by that module's own distinct peer-ID
addressing, but not by a single traced outgoing byte construction) is that
these specific cmd_ids are DUML-v1 commands `dji_upgrade` **sends**, as bus
master, toward subordinate peripheral MCUs' own firmware during their
updates — meaning the handling/dispatch code for them, if this hypothesis
is correct, was never going to be found in this E1E/E2 Linux image at all,
because it runs on the peripheral's own, separate, non-Linux firmware.

---

## What wasn't pursued (scope boundary, restated)

Same boundary as every other document in this project, held throughout
every track above: no exploit code, crafted packet, or attack recipe was
written anywhere in this pass; every finding stops at "function X does/
doesn't check Y, impact category Z, confidence W." The activation/AMT TA
(`libamt_util.so`/`e91c9402...`) was not touched in any track. Several
real, exact wire-level trigger conditions were deliberately left untraced
(the exact byte origin of `dji_vtwo_sdk`'s `__memcpy_chk`-gated length
field; the exact runtime frequency of the fastrtps `useBuiltinTransports`
selector path) — the mechanism is documented, the recipe to pull the
trigger is not. Two of 78 adversarial-verify sub-agents (`dji_vtwo_sdk`'s
RETR primitive, and the `item+0x134` null-deref-after-route-disable
hazard in Track N) were stopped mid-run by an automated safety-filter
false-positive on ordinary, legitimate security-research text — not a
finding about the content itself — and remain at their original,
not-independently-re-derived confidence rather than being silently
promoted to "confirmed" or dropped.
