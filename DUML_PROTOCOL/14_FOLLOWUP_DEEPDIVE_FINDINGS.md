# Follow-up deep-dive: 8 flagged open leads from the exhaustive binary sweep

This document resolves (or honestly fails to resolve, with reasons) 8
specific open leads that `12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md` and
`09_DJI_AUTOTEST_EXPLOITABILITY_DEEPDIVE.md` flagged but didn't chase down:
`libduml_fastrtps.so`'s real network reachability, `librtos.so`/
`rtos_debug`'s authorization model, `libduml_shineIO.so`'s storage-parsing
surface, finally decoding `duss_event_shell`'s dispatch table (a
packed-Android-relocation tooling gap that had blocked this three times),
5 previously-undisassembled cmd_set `0x00` commands, the `TEEC_InvokeCommand`
command-ID tables for 3 of the 4 OP-TEE CA libraries, the newly-discovered
`/nfz_data/nfz_tfr.bin`, and `dji_flight`'s cmd_set `0x10` registrar
mystery.

**Methodology.** Each of the 8 tracks ran as an independent investigate
pass, followed by a second, independent adversarial-verify pass: a fresh
agent, with no access to the first agent's reasoning, re-derives each
non-trivial claim directly from the raw binary bytes and is instructed to
default to **refuted** unless it can reproduce the claimed mechanism itself.
This caught a real, substantial number of errors — wrong addresses, a
genuinely non-existent "dispatch table" that turned out to be misread C++
RTTI data, overstated categorical claims ("no file-write primitive
anywhere") contradicted by one level of call-graph the first pass didn't
walk. **Every finding below is marked confirmed or refuted; refuted claims
are kept and corrected, never silently dropped**, because the corrections
are often more informative than the original claim. As with every other
document in this project: static analysis only (disassembly, ELF/relocation
parsing, string/import enumeration); no binary was executed; no packet was
crafted or sent; no exploit code was written; the activation/AMT TA
(`libamt_util.so`, UUID `e91c9402...`) was not touched in any track, per
this project's standing exclusion — explicitly re-stated and independently
confirmed honored (see Track F below).

---

## Track A — `libduml_fastrtps.so`: a real, vendored eProsima Fast-DDS stack

`libduml_fastrtps.so` (E1E: ARM32, 3.45MB; E2: aarch64, 5.18MB) is DJI's
build of eProsima Fast-RTPS/Fast-DDS, vendored close to wholesale under
DJI's own path prefix (`hardware/dji/duml/dds/fast/rtps/...`, mirroring
eProsima's real upstream directory layout file-for-file). DJI wraps it with
a thin C API — `duss_ps_construct`/`duss_ps_publish`/`duss_ps_subscribe`/
`duss_ps_publisher_create`/`duss_ps_subscriber_create`/etc (20 exports),
source file `duss_ps_fastdds.cpp` — confirming the project's informal "DUSS
pub/sub" convention is concretely a real DDS participant, not a lightweight
custom protocol. Neither build strips its `.dynsym` (10,135 / 9,046
entries, including mangled C++ names), so almost the whole call graph is
name-recoverable. No eProsima version string was found; namespace evidence
(legacy `fastrtps::rtps` alongside the newer `fastdds::rtps`/`dds` split,
TCP transport + `RTCPMessageManager`) places it at Fast-DDS ~2.x.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `ParameterList::read_guid_from_cdr_msg` / `readInstanceHandleFromCDRMsg`, on RTPS parameter `PID_KEY_HASH` (0x70) or a caller-chosen target PID, unconditionally read a fixed 16 bytes (12-byte GuidPrefix + 4-byte EntityId) without ever checking the wire-supplied parameter's own declared length is actually ≥16 — confirmed on both the E1E (ARM32) and E2 (aarch64) builds, byte-for-byte | memory_corruption (bounded) / data-integrity | medium-high | **confirmed on reverify** |
| The same gap is wired into the ordinary per-DATA-submessage inline-QoS path (`ParameterList::updateCacheChangeFromInlineQos`), not only one-time discovery traffic — so it recurs on every received DATA submessage carrying inline QoS | architecture_note | medium | **confirmed on reverify** |
| The library performs genuine raw UDP/TCP socket networking itself (real `socket`/`bind`/`connect`/`listen`/`accept`, multicast-join code with its own `'UDPTransport Error binding '`/`'Error joining multicast group on '` strings) — it is not a pure local-IPC shim riding on another transport | architecture_note | high | **confirmed on reverify** |
| A small string cluster (`rndis0`, `192.168.100.4`, `192.0.2.0`, `getIPs failed`, `All whitelist interfaces where filtered out`) sits beside confirmed-live `UDPv4Transport.cpp` code, but no reachable function referencing any of the five strings could be found | architecture_note | low | **REFUTED on reverify** — all five strings ARE referenced, from a local (non-exported) function `get_ipv4s`, itself called from 4 exported `UDPv4Transport` methods **including the constructor**. `rndis0`/`192.168.100.4` is a hardcoded (interface, IP) fallback pair used when interface enumeration fails; `All whitelist interfaces where filtered out` and `192.0.2.0` are referenced directly inside the transport constructor. The original pass's exidx-based function-start recovery evidently missed these local functions. |
| DJI's vendored tree is essentially unmodified upstream eProsima source wrapped by DJI-authored glue, not a from-scratch reimplementation | architecture_note | medium-high | **confirmed on reverify** |

**Biggest open question, explicitly unresolved:** whether DJI's
`duss_ps_fastdds.cpp` wrapper restricts this transport to loopback or to
the already-documented internal `192.168.100.x` companion/debug network,
or leaves Fast-RTPS at its stock defaults — binding across *all* active
network interfaces with multicast SPDP discovery on `239.255.0.1`. This is
the single fact that would determine whether Finding 1's gap is reachable
only from a local/internal peer or from anything able to reach one of the
device's live interfaces (Wi-Fi, LTE, the RC link). Resolving it requires
tracing `duss_ps_construct`/`duss_ps_publisher_create`/
`duss_ps_subscriber_create`'s full call graph into the actual
`DomainParticipantQos`/transport-descriptor construction — not done in this
pass; `duss_ps_construct` itself turned out to be mostly a string-keyed
participant-handle cache plus logging boilerplate, not the QoS-configuration
step. Also undetermined: the exact eProsima release version; which other
DJI binaries besides `dji_blackbox` link against and use this bus; whether
any real DJI peer ever sends a non-16-byte-length `PID_KEY_HASH` (no attempt
was made to find or examine a peer encoder, per this project's no-exploit
scope).

---

## Track B — `librtos.so` / `rtos_debug`: flight-control RTOS core reboot/ramdump

`rtos_debug` (shipped internally as `test_rtos`) is a thin CLI over
`librtos.so`'s small, fully-named exported API. Every primitive —
`rtos_start_hb_monitor`/`do_ramdump`/`do_reboot`/`sgi_trigger`/
`timeout_set`/`dumpsize_set`/`do_recover`/`rsysrq_base_get` — is, at bottom,
a single `ioctl()` against `/dev/rtos` opened `O_RDWR`, using a consistent
custom ioctl ABI (type `'R'`, sequential `nr` 0–8).

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `-R`/`--reboot` and `-d`/`--dump` trigger a reboot or ramdump of the flight-control RTOS co-processor through a bare `ioctl()` with **no DUML-bus, authentication, or cryptographic gate of any kind** — neither `rtos_debug` nor `librtos.so` links any DUML-bus library at all. This extends `12_...FINDINGS.md`'s `duss_shell`/`dji_mb_ctrl` "local shell access is the only gate" pattern to the RTOS core's own reboot/ramdump primitives specifically | missing_authz | high | **confirmed on reverify** |
| `-r`/`--recover` does **not** itself trigger recovery — it only selects which of two local functions is installed as a `SIGIO` handler (via `signal(29,...)` + `fcntl(F_SETOWN)`/`O_ASYNC`); `rtos_do_recover()` is reached only asynchronously, if/when the kernel driver later raises `SIGIO` | architecture_note | medium-high | **confirmed on reverify** |
| `rtos_do_recover()`'s "custom image" branch loads an arbitrary caller-supplied filesystem path (from `-p`/`--imagepath`) as the RTOS recovery firmware via `dji_fw_load_file()`, with no signature/hash/allowlist check visible anywhere in `librtos.so` around that call | integrity | medium | **confirmed on reverify** — `rtos_imagepath_set` itself safely bounds the path copy (`strlen<=0x7f` gate + FORTIFY'd `__strcpy_chk`, so no overflow in path-setting), but nothing downstream checks the *image's* authenticity before `dji_fw_load_file()` hands it to the RTOS core |
| `rtos_do_recover()` issues an `ioctl` declaring a 128-byte kernel-to-user transfer (`_IOR('R',7,char[128])`) against what looked like a leftover 4-byte stack scratch buffer from an earlier call — a stack-smash via mismatched ioctl sizes | memory_corruption | high (as originally stated) | **REFUTED on reverify** — there is no bug. Between the two ioctl calls, two instructions reload the register to a correctly-sized 128-byte **global `.bss` buffer** (the same buffer `rtos_imagepath_set` populates via a FORTIFY-checked copy), not the stack. The original pass missed that intervening reload. No stack corruption occurs via this path. |
| Minor CLI robustness nits: an unrecognized `getopt` option re-enters the parse loop instead of exiting; `-S`'s post-processing wait is an unconditional CPU-spinning busy-wait (no `pause`/`nanosleep`) | crash_dos | low | **confirmed on reverify** (correctness nits, not security-relevant on their own) |

**Not determined:** the actual UNIX permission bits on `/dev/rtos` (no
`ueventd.rc`/`file_contexts` entry for it found in this extraction — the
real-world severity of the "no DUML/auth gate" finding rests entirely on
whatever those permissions are); whether the kernel driver genuinely
performs the full 128-byte transfer its ioctl code implies, and whether
that data is attacker-influenceable (the kernel module backing `/dev/rtos`
isn't present in this userspace-only firmware image); whether
`dji_fw_load_file()` or the kernel driver itself verifies the recovery
image's signature elsewhere; the callers of `rtos_sgi_trigger`/
`rtos_rsysrq_base_get` (not found in `rtos_debug` or `librtos.so` — likely
a different, unexamined RTOS-adjacent daemon).

---

## Track C — `libduml_shineIO.so`: storage I/O engine (NVMe/exFAT/SD)

A DUML-dispatch-free storage-engine library (no `duss_event_*`/`duss_mb_*`
import at all) abstracting three backends behind one API: NVMe (internal
SSD, or USB-attached SSD via a Realtek RTL9210 bridge), `mmcblk`
(SD-card/eMMC), and generic USB mass storage.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `nvme_get_vendor_sn`/`nvme_get_vendor_mn` `strncpy()` the raw NVMe Identify-Controller Serial-/Model-Number fields — both spec-defined as ASCII, space-padded, **not required to be NUL-terminated** — straight from whatever physical device answers Identify into a caller buffer, with no termination/length-capping beyond the fixed `strncpy` count | info_disclosure | medium-high | **confirmed on reverify** (whether any real caller then treats the result as a NUL-terminated C string without independently bounding it was not traced beyond this library) |
| `exfat_get_sb()` accepts any `read()` that returns exactly 512 bytes as a valid exFAT superblock — **no boot-sector signature/magic check anywhere in the function** | integrity | medium-high | **confirmed on reverify** (whether a caller elsewhere validates the signature before/after was not confirmed) |
| The DJI-proprietary "DJI partition" attribute block (cached sector/cluster size, write-tracking state; auto-reset when "abnormal") is integrity-checked only by a trivial additive rotate-hash seeded with the fixed constant `0xBEEF` — not CRC16-CCITT, not a cryptographic MAC. Mirrors the project's existing `dji_sdrs_agent` CRC16-only-NVRAM finding | weak_crypto | high | **confirmed on reverify** |
| A non-exported exFAT directory-entry-set parser has two length bound-checks whose own real max "could not be shown to ever actually fail" | architecture_note | medium | **REFUTED (corrected toward more exposed, not less)** — both checks are in fact live: one trivially fires for any byte whose nibble-sum exceeds 15; the other's true max is 46 (not the claimed 30) once a conditional OR'd bit from the same cited dispatch table is accounted for, exceeding its 0x1f bound on a path the original evidence itself feeds into. The function's real caller (reached only by indirect/function-pointer dispatch, not a direct branch) and the true origin of its outer entry-count bound remain genuinely unresolved. |
| `shine_disk_get_type_by_name`'s NVMe/`mmcblk`/USB dispatch is "generic across backing-store types, explicitly including removable/external media" | architecture_note | high | **REFUTED on reverify** — in the two gated operations actually traced (`shine_disk_do_format`, `sh_disk_flash_plate`), `mmcblk` (SD-card) is **explicitly rejected** (`return -EINVAL`); only NVMe (and partially the generic `"sd"` class) proceeds. Also corrected: the two "`scsi_nvme_*_RTL9210`" names cited as exported symbols are not in `.dynsym` at all — the real exports are `scsi_nvme_get_identify`/`scsi_nvme_smart_get_log`; the `_RTL9210` strings are internal debug-log tags, not symbol names. No call chain from this dispatcher to the NVMe-Identify parsing functions was found either. |

**Not determined:** which upstream daemon(s) actually invoke this library
with a user-facing SD-card path vs. an internal-SSD-only path (would need a
cross-binary consumer survey, out of this single-library pass); whether the
"DJI partition" lives on the same removable medium as the user exFAT
volume or a separate internal-only area; whether the RTL9210 USB-bridge
path is actually exercised on this airframe in practice.

---

## Track D — `duss_event_shell` dispatch table: the APS2 tooling gap, finally closed

This closes a tooling gap `09_DJI_AUTOTEST_EXPLOITABILITY_DEEPDIVE.md` and
two earlier passes had flagged: `libduml_frwk.so`'s Android "packed"
relocation section (`SHT_ANDROID_REL`/`DT_ANDROID_REL`, `"APS2"` magic,
sleb128-encoded delta groups) couldn't be decoded by this project's
standard tooling (`pyelftools`/`readelf`), which blocked reading
`duss_event_shell`'s real dispatch table. A working, independently
validated sleb128/group decoder for this format was built this pass (three
cross-checks: byte accounting, `R_ARM_RELATIVE` count matching
`DT_RELCOUNT` exactly, and three decoded `GLOB_DAT`/relocation targets
matching known `.dynsym` addresses) and is reusable for any future ARM32
Android binary in this firmware that carries this section.

**The real, independently re-derived dispatch table** (vaddr `0x107ee8`,
`.data.rel.ro.local`, 10×8-byte `{key string, handler fn}` entries, every
slot carrying a real `R_ARM_RELATIVE` relocation):

| key | handler vaddr |
|---|---|
| `dump` | `0x87d60` |
| `ping` | `0x89cc0` |
| `log` | `0x882b4` |
| `stat` | `0x89a68` |
| `capture` | `0x87ee8` |
| `asym_ping` | `0x89810` |
| `trans_heartbeat` | `0x895b8` |
| `async_ping` | `0x89360` |
| `route_control` | `0x8acf4` |
| `msg_send` | `0x89108` |

(The first pass's own claimed "dispatch table" — three GOT slots it said
*were* the table — was **refuted**: those slots are ordinary per-reference
GOT entries used when the `asym_ping`/`trans_heartbeat`/`async_ping`
handlers spawn their worker threads, not the dispatch table itself. The
table above was independently located and confirmed by a second pass.)

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| The `dump` sub-handler contains a length-check-then-`exit(-1)` path: on a length mismatch it logs a backtrace and **unconditionally terminates the whole host process**, rather than returning an error | crash_dos | medium-high | **confirmed on reverify** (the exact wire fields that drive the length past the bound were deliberately not traced, per this project's no-attack-recipe scope — only the internal control-flow-to-`exit()` is confirmed) |
| The `route_control` sub-handler can enable/disable an **arbitrary named internal message-bus route item** with no authentication beyond what `duss_event_shell` already lacks entirely — a capability well beyond ping/heartbeat diagnostics | missing_authz | medium-high | **confirmed on reverify** |
| The `log` sub-handler exposes unauthenticated enable/disable/get/set of internal logging-module state | missing_authz | medium-high | **confirmed on reverify** (minor severity — log-tampering/anti-forensics only, not data or control-plane) |
| **No file-write, file-create, or process-exec primitive exists anywhere in `duss_event_shell`'s reachable code** — directly resolving `09_...DEEPDIVE.md` §1's open question about setting `/data/dji/autotest_on` through this path | architecture_note | high | **REFUTED** — a real, reachable file-create+write primitive *does* exist: `route_control` → `duss_mb_control_route_item` → `mb_dump_rt` → `fopen("/data/dji/dump/host_0x%x","a")` + `fprintf`×2 + `fputc`+`fclose`. **However, this does not hand the original question an exploitable answer**: the path is a fixed, generic debug-dump location (`/data/dji/dump/host_0x<route-item-id>`), not `/data/dji/autotest_on`, and `<route-item-id>` is not raw attacker-controlled bytes — it comes from the targeted route item, not a free-form string. The categorical "no file I/O at all" claim was simply wrong; the specific "can this set `autotest_on`" question is still answered **no** via this path. |
| `capture` is a shared/tail-merged code block with `dump`/`log`, not its own distinct function | architecture_note | medium | **REFUTED** — `capture` is a genuinely separate function with its own 428-byte stack frame and its own clean epilogue; `dump` ends cleanly well before `capture`'s address with an unrelated helper in between. The three handlers share a similar *shape* (parse a flag via `argoat_graze`, log it) because they look hand-duplicated from a common source pattern, not because of compiler code-folding — and their boundaries are fully resolvable from static analysis, contrary to the original claim. |
| `msg_send`'s send path calls into "the same message-bus-adjacent function family used for `route_control`", suggesting (not confirmed) a message-injection primitive | integrity | medium | **REFUTED** — the shared call target (`0x3d988`) is the trivial, 4-instruction, exported `duss_mb_get_current_machine_id` (a cached-global-halfword getter), not a route/forwarding function; it is called from many mundane, unrelated contexts. The specific evidentiary claim doesn't hold, though the surrounding facts (handler addresses, task-spawn chain, a length-capacity check) are accurate. |
| `asym_ping`/`trans_heartbeat`/`async_ping` are confirmed pure parameter-parsing-and-logging diagnostics with no file/exec/socket calls anywhere in their bodies | architecture_note | high | **REFUTED (partially)** — the core mechanism (dispatch → task-spawn with the correct entry pointer, no *direct* exec/socket primitive) is real, but the "no file calls anywhere" claim is incomplete: one level deeper, all three bodies call `duss_event_send`/`_v2`/`_sync_v2`, which themselves reach `duss_mb_send_v2` → `fopen`/`fclose`/`fprintf` — a generic message-bus debug-dump feature, not ping/heartbeat-specific logic, but real file I/O is reachable from the call graph these handlers kick off. Cited call-counts for `duss_shell_parse_value_for_key` were also found inaccurate on recount (claimed 9–11×, actual 9/11/18×). |

**Net resolution of the original question:** `duss_event_shell` genuinely
cannot set `/data/dji/autotest_on` or write to any attacker-chosen path —
but it is not file-I/O-free either; it reaches a generic, fixed-location
debug-dump file-write primitive via two different sub-handlers. Two new,
real, unauthenticated capabilities (`route_control`'s arbitrary route
toggle, `dump`'s remote process-abort) were found that neither doc 09 nor
doc 12 previously knew existed.

**Not determined:** whether disabling an arbitrary route item via
`route_control` can itself crash or disrupt another subsystem (would
elevate that finding to `crash_dos`); the full semantics of `0x3d988`'s
sibling function family and of the message-bus packet `msg_send`
constructs (delivery scope — local vs. cross-component — unresolved); the
exact wire-level fields that drive `dump`'s length check past its bound.

---

## Track E — cmd_set `0x00` (General): the remaining unresolved commands

**Loader/update (`0x07`–`0x0A`) and fw-update-push (`0x40`/`0x41`/`0x43`)
remain genuinely unresolved** — reported honestly, not guessed. Neither
`libduml_frwk.so`'s one built-in 6-entry dynamic-command table nor
`dji_sys`'s 11 direct `duss_event_register_dynamic_command` calls cover any
of these 15 target cmd_ids, and a full disassembly of the firmware-upgrade
daemon's entire 4-library plugin chain (`libupgrade_register.so` →
`libupgrade_communication.so` → `libupgrade_commu_demo.so` →
`libupgrade_upgrade.so`) found no cmd_id-matching dispatch logic with
confidence either — its event callback parses fixed struct-offset fields
that don't look like a raw DUML cmd_id switch. Concrete architectural
reasons this may be unresolvable from this image: the handler may live in
a `dlopen()`'d per-product plugin not present in this extraction (no
`/system/etc/upgrade.json`/`dji.json` found), or this may be dead/legacy
protocol surface the upgrade subsystem has moved away from (even the
upstream community Lua dissector's `0x07`-`0x0A`/`0x40`-`0x43` stubs are
empty `TODO` placeholders with no payload-format knowledge to borrow).

**File-transfer (`0x20`–`0x28`) is resolved**: a shared
`duss_file_trans_event`/`_req`/`_data`/`_checksum`/`_data_lost_list` module
inside `libduml_frwk.so`, reused by 6 consumers (`dji_sys`,
`dji_perception`, `dji_blackbox`, `dji_config_store`, `dji_sec`,
`libupgrade_commu_demo.so`), dispatched by an internal payload "phase"
byte rather than by cmd_id — so which exact cmd_id(s) in `0x20`–`0x28`
route into it per daemon couldn't be read off a literal register table
(none exists for it; it's wired via a bus-client callback-struct field, an
`R_ARM_ABS32` relocation, not the usual literal-immediate pattern). The
already-known `0x24`/`0x2A` aliases are independently confirmed by a
field-for-field match.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `duss_file_trans_req` (the "start transfer" handler, phase=1) builds its destination path from a per-daemon fixed base directory plus a wire-supplied filename via `strncpy`+`strncat`, with **no authentication/authorization check of any kind** — any client able to deliver a cmd_set `0x00` message into a daemon's file-trans session reaches this, unauthenticated | missing_authz | high | **confirmed on reverify** |
| A strict `[A-Za-z0-9._-]` filename allow-list (rejects `/`) fully blocks traversal, confining the primitive "strictly inside" the daemon's fixed base directory | integrity | high | **REFUTED** — the allow-list has no whole-string check: a filename of exactly `".."` passes (each byte individually legal), and gets concatenated with **no separator logic** onto the base directory (confirmed default for `dji_sys`: `/blackbox/upgrade/`), producing the literal path `/blackbox/upgrade/..`, handed straight to `open(O_CREAT\|O_RDWR)` with no `realpath()`/canonicalization anywhere in the chain (confirmed: `realpath` is imported only by `dji_ftpd`/`dji_perception`, not by this code path). Because `/` itself is still rejected, a single filename value can only move **exactly one directory level up** — multi-component `"../../.."` traversal within one field is still blocked, so this is a confined, single-hop weakness, not arbitrary-path traversal. In the one concrete case checked (`dji_sys`'s `/blackbox/upgrade/..` → `/blackbox`, an existing directory), `open(O_CREAT\|O_RDWR)` on an existing directory fails with `EISDIR`, limiting the practical write impact of *that specific* instance — but that's incidental to the one target happening to be a directory, not a protection the validator or call chain provides, and the categorical "cannot escape via `..`" claim is false as stated. |
| `dji_sys`'s accepted-filename path flows into `open()`+`fallocate()` with an attacker-controlled, unbounded wire-supplied `datalen` — a remote disk-exhaustion DoS primitive | crash_dos | medium-high (as originally stated) | **REFUTED** — the low-level primitive (`duss_mmap_file_open`'s mode-2 branch really does `open()`+`fallocate()` with an unbounded caller-supplied size) is real, but the specific citation tying `duss_file_trans_req`'s wire `datalen` field to that call does not exist in the real function (the cited address resolves to `.rodata`, not code, in every candidate binary checked). No confirmed wire-reachable path to the unbounded `fallocate()` was established in this pass — remains an open question, not a demonstrated DoS. |

**Not determined:** the exact cmd_id(s) bound to `duss_file_trans_event`
per consuming daemon; the firmware-upgrade subsystem's own base directory
(populated from a runtime struct field, not a static string — unresolved
by this pass's static technique); whether cmd_set `0x00`'s `0x20`-`0x28`/
`0x40`-`0x43`/`0x07`-`0x0A` range is reachable from outside the device over
any interface other than the already-confirmed USB `rndis0` path (not
re-checked here; `09_...DEEPDIVE.md`'s general reachability analysis
applies); `duss_mmap_file_open`'s non-create (`mode!=2`, presumably
read/send) branch was not disassembled.

---

## Track F — OP-TEE CA-library `TEEC_InvokeCommand` command-ID mapping

Scope, honored throughout and independently re-confirmed: only
`libfw_util_ca.so`, `libnfz_util_ca.so`, and `libadsb_util.so` were
examined. **`libamt_util.so` (the `e91c9402...` activation/secure-debug/
DJICare TA) was never opened, disassembled, or searched for command IDs at
any point in this track** — the explicit exclusion from
`13_OPTEE_TA_FINDINGS.md` was maintained and is noted again in that
document's own findings, not relaxed here.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `libfw_util_ca.so`'s 6 `TEEC_InvokeCommand` call sites each pass a fixed, unconditional literal command ID per exported wrapper — a clean sequential `0`–`5` map to the `09db16c0` Firmware-Verify TA (`fw_util_verify`→0, `fw_util_load`→1, `fw_util_verify_load2ion`→2, `fw_util_verify_init`→3, `fw_util_verify_update`→4, `fw_util_verify_final`→5) | architecture_note | high | **confirmed on reverify** |
| `libadsb_util.so`'s 4 real call sites each pass a fixed, sequential literal command ID (`0x11`–`0x14`) to the `ad09a153` ADS-B crypto TA for its 4 AES-CCM wrappers; the 5th exported symbol (`dji_aes_ccm_init`) is a dead 2-byte `bx lr` stub that never touches the TEE | architecture_note | high | **confirmed on reverify** |
| `libnfz_util_ca.so` funnels everything through exactly two generic, exported dispatcher functions (`sec_icc_cmd`, `exchange_info_between_ca_ta`) that forward their **own caller-supplied first argument directly and unconditionally** into `TEEC_InvokeCommand`'s command ID, with no local range check — the library's own named convenience wrappers only ever use command IDs `{0,2,3,4,6,7,8,9,0xa,0xb}`, but nothing in this CA library stops a caller invoking the two dispatchers directly with `1`, `5`, or anything `>0xb` | missing_authz | medium | **confirmed on reverify** — whether the TA itself validates/rejects out-of-range command IDs server-side is unexamined (would require disassembling the TA image, out of this track's CA-library-only scope), so this is an architecture/missing-local-authz observation, not a demonstrated bypass |
| No code-level link found between `libadsb_util.so`'s recovered command IDs (`0x11`-`0x14`) and DUML cmd_set `0x11`'s (ADS-B) cmd_ids, despite the numeric digits coinciding | architecture_note | low | not independently reverified (low-confidence finding) — the overlap looks coincidental; confirming either way would require disassembling `dji_sys`'s own cmd_set `0x11` dispatch handlers, out of scope here |

---

## Track G — `/nfz_data/nfz_tfr.bin` and the `nfz.bin` relationship

`/nfz_data/nfz_tfr.bin` **does not exist anywhere on the E1E `vendor.img`**
— exhaustively confirmed (full `debugfs` directory walk of every directory
in the image; a raw byte-level search of the entire ~151MB image for both
`nfz_tfr` and `nfz_data` ASCII, finding zero and exactly-one [a policy-file
text match] hits respectively). This is architectural, not a search miss:

- `vendor.img`'s own `/etc/file_contexts` (SELinux policy) declares
  `/nfz_data` as its **own top-level mount point** (`system_data_file`),
  structurally distinct from `/vendor` (`system_file` — the mount this
  image itself backs) — so `/nfz_data` is never reachable by walking
  `vendor.img`'s own directory tree at all.
- This firmware extraction contains no `userdata`-class partition image
  anywhere (only `bootarea.img`/`normal.img`/`rtos.img`/`system.img`/
  `vendor.img`) to back that mount, so `/nfz_data`'s live contents simply
  aren't present in the package, full stop.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| `/vendor/nfz/nfz.bin` (`06_NFZ_DATABASE_FINDINGS.md`'s file, mounted from `vendor.img`'s `/nfz/nfz.bin`) and `/nfz_data/NFZ/nfz.bin` are **two physically distinct files**, not the same file via symlink/bind-mount alias — related by a version-gated copy/upgrade routine in `dji_perception`: the vendor copy is the read-only "golden" source; the `/nfz_data` copy is a separate writable runtime working copy, refreshed from the vendor copy only when its own stored version is older, validated by MD5 + an embedded `tz_sec_header` check, with a maintained backup file | integrity | high | **confirmed on reverify** |
| Two apparent anti-rollback-disable sentinel files are named directly adjacent to that upgrade logic: `/nfz_data/NFZ/disable_ota_anti_rollback`, `/nfz_data/NFZ/disable_anti_rollback` — naming strongly suggests presence-checked flags that would suppress the version-gate's anti-rollback check | integrity | medium-high | **confirmed present** (not disassembled further — which function reads them, what privilege creating them requires, and whether they're reachable without root/debug access are flagged as leads only, not resolved, per this project's no-attack-recipe scope) |
| `/nfz_data/nfz_tfr.bin` is architecturally TFR (Temporary Flight Restriction) data pushed at **runtime from the DJI Fly companion app** via a sequence-numbered packet-transfer protocol, MD5-validated against an app-supplied hash — never shipped as a firmware file at all, independently explaining its absence from `vendor.img` | architecture_note | high | **confirmed on reverify** |
| A separate code module's symbol/log names (`parseTfrFileHead`/`readTfrItemCircle`/`getTfrItemPolygonBuf`/`parseTfrItemData`/`parseTfrFileTail`) imply `nfz_tfr.bin`'s record format is a HEAD / typed-ITEM(circle or polygon) / TAIL layout | architecture_note | low | not independently reverified — explicitly inferred only from the *consuming* C++ code's naming, since the file itself could not be located to inspect its actual bytes |
| `dji_perception` links all four OP-TEE CA client libraries (including `libnfz_util_ca.so`) and imports two of its functions by name | architecture_note | medium-high | **REFUTED as a general statement, confirmed for one build** — this firmware package contains *two* distinct ELF files both named `dji_perception` (E1E 32-bit ARM, E2 aarch64). The claim is true, and independently re-confirmed down to the relocation table, for the **E1E build only**. The **E2 (aarch64) `dji_perception` does not link `libnfz_util_ca.so`** — and that library doesn't exist anywhere under the E2 extraction tree at all, so the E2 binary cannot call into it by any mechanism. Any future reference to "`dji_perception`" in this project should state which chip/build, the same convention `11_DJI_NN_SERVER_FINDINGS.md` already uses. |

**Not determined:** `/nfz_data/nfz_tfr.bin`'s or `/nfz_data/NFZ/nfz.bin`'s
state on an actual running device's writable partition (no userdata-class
image exists in this extraction to check); the byte-level container
format of `nfz_tfr.bin` (impossible without the file itself); whether
`dji_perception`'s `TEEC_InvokeCommand` calls into `libnfz_util_ca.so` pass
attacker-reachable input (not disassembled, consistent with this project's
TA-command-dispatch scope boundary — separate from, and not overlapping
with, the explicitly-excluded activation TA).

---

## Track H — `dji_flight` cmd_set `0x10` (Automation) / `api_wp2_*` wiring

**Methodology finding worth keeping regardless of the rest of this
track:** `dji_flight`'s PIC code splits every local address computation
into a relative-delta literal-pool load (`ldr rX,[pc,#imm]`) *plus* a
separate `add rX, pc` completion instruction — the file stores the delta,
never the absolute address. This is why `08_...FINDINGS.md`'s original
pass, searching for bare absolute addresses/raw pointers, found nothing for
`api_wp2_*`. Sanity-checked against a string the project's own docs
already confirm is referenced (`dji_verify -n geofense -H %s %s`): a naive
literal-pool/raw-address scan reproduces the same false-negative; tracking
the `ldr`-delta+`add`-pc pair finds it immediately. This corrected
technique recovered real entry addresses for 13 named `api_wp2_*`
functions and should be used for any future pass on this binary.

| Finding | Impact category | Confidence | Status |
|---|---|---|---|
| Cmd_set `0x10` ("Automation") itself was **not located anywhere** in `dji_flight` — not in any recovered table's tag bytes, not in any string, not as a literal immediate before any registration-style call | architecture_note | medium | **confirmed on reverify** — genuinely not found, resolving the question in the negative rather than leaving it open on a technicality |
| A specific 19-entry static dispatch table at file offset `0xad0b0`–`0xad168`, cleanly mapping 9 of the named `api_wp2_*` functions to tag bytes (including a plausible `0x22` cluster) | architecture_note | high (as originally stated) | **REFUTED, substantially** — independently re-reading the actual relocations and raw bytes at the cited offsets does not reproduce the claim at all: 3 of the 19 cited slots carry no relocation whatsoever, and the "decoded" function-pointer values don't match any address in the file (one supposedly-distinct pair of entries decodes to the identical, unrelated word `0x0000ee7d`). The region is actually a mix of real `R_ARM_RELATIVE` relocations and `R_ARM_ABS32` relocations to C++ `_ZTVN10__cxxabiv1` typeinfo — consistent with RTTI/vtable data, not a hand-built DUML dispatch table. **This specific table and its claimed wp2-to-tag mapping should not be treated as established and should not be copied into other documents.** |
| `api_wp2_waypoints_upload_handle` is called once externally (from `api_wp2_waypoints_upload`) and recurses into itself once | architecture_note | high | **REFUTED on one sub-claim** — the single external caller is real and confirmed (`bl #0x1ab80` at `0x1ace6`), but the claimed "recursive self-call" at `0x1ac26` is not a branch instruction at all (it decodes as `strb r7,[r4]`, a store, whose opcode bits don't even match the Thumb-2 BL/BLX prefix). An exhaustive scan of every `bl`/`blx` target in the whole binary finds exactly **one** call to this function, not two. |
| `api_wp2_break_restore_waypoint_fly`/`set_global_cruise_vel`/`get_global_cruise_vel` are not in any table and are never called or address-taken from anywhere else in the binary; two of their shared GOT slots hold literal zero | architecture_note | medium (as originally stated) | **REFUTED** — the cited GOT-slot values are wrong (the real values are 4 distinct non-null `.bss` pointers, none matching the claimed `0x20010000`/`0`/`0`/`0x35925`), and — more importantly — all four stub addresses ARE address-taken, each exactly once, inside a **different**, genuinely real `.data` array (`R_ARM_RELATIVE`-backed 8-byte `{function pointer, cmd word}` rows starting around file offset `0xae0f8`). In that array, `pause_recovery`/`set_global_cruise_vel`/`get_global_cruise_vel` appear as three consecutive rows tagged cmd_set `0x22`/cmd_id `0x06`/`0x07`/`0x08`, and `break_restore_waypoint_fly` appears later in the same array tagged cmd_set `0x22`/cmd_id `0x44`. |

**On that last correction:** this `0x22`/`0x06`-`0x08`/`0x44` mapping
surfaced as a byproduct of refuting a different, narrower claim — it was
not itself put through a second, independent adversarial-verify pass the
way the rest of this project's findings are. It is evidenced directly
(`readelf -r` + a raw hex dump at the cited file offset), so it's a
genuinely promising lead, but it should be treated as **an unconfirmed
lead for a future pass to re-verify independently**, not as settled fact
on the level of the other findings in this document. If it holds up, the
practical implication is notable: `dji_flight`'s `api_wp2_*` waypoint-
mission handlers would be registered under cmd_set `0x22` ("Demo Mode",
per `04_WM260_DAEMON_FINDINGS.md`'s existing name for that cmd_set), not
cmd_set `0x10` — meaning the long-standing "who registers cmd_set `0x10`"
mystery may not have an answer in `dji_flight` at all, consistent with
this track's direct, confirmed negative finding that `0x10` doesn't appear
anywhere in this binary.

Also re-verified and confirmed: `dji_flight` has no `.gnu_debugdata`
section (31 section headers enumerated, none so named); its
`.gnu_debuglink` section names a split-debug file (literally `dji_flight`,
no path) that doesn't exist anywhere else in this firmware extraction —
a dead end, not a lead.

**Not determined:** whether the recovered table's tag byte really encodes
a DUML wire-level cmd_set/cmd_id pair at all, as opposed to some other
internal pair of small values (inferred by analogy only); who/what calls
or otherwise reaches the `break_restore`/`cruise_vel` stub cluster or its
sibling cluster at `0x1b040`-`0x1b140` (exhaustive scans found no
reference to either from anywhere else in the binary); what writes the
four GOT slots at runtime, if anything; the identity of the function
reached via the generic indirect call that consumes
`api_wp2_get_wp_index_in_list`'s table-record address (the one table entry
with a confirmed concrete consumer) — whether it ultimately resolves to
`duss_event_register_dynamic_command` or something else was not confirmed.

---

## What wasn't pursued (scope boundary, restated)

Same boundary as every other document in this project, held throughout all
8 tracks: no exploit code, crafted packet, or attack recipe was written
anywhere above; every finding stops at "function X does/doesn't check Y,
impact category Z, confidence W." The activation/AMT TA
(`libamt_util.so`/`e91c9402...`) was not touched in Track F or anywhere
else in this pass. Several real, exact wire-level trigger conditions were
deliberately left untraced (the `dump` sub-handler's exact length-overflow
fields in Track D; the exact bytes needed to drive Track C's exFAT parser
past its nibble-sum bound) — the mechanism is documented, the recipe to
pull the trigger is not. Two tracks (E, H) report genuine, honestly-stated
non-findings rather than a guess dressed up as an answer.
