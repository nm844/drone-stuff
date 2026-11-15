# E1E flight/navigation/camera-link daemons — `dji_flight`, `dji_navigation`, `dji_autoflight`, `dji_autotest`, `dji_rcam`, and `dji_sys`'s command-agent populator

Six targeted disassembly passes on the E1E image, chasing the two biggest
open questions from `04_WM260_DAEMON_FINDINGS.md`: where does cmd_set `0x03`
(Flight Control) actually get registered, and where does the still-
undocumented cmd_set `0x10` (Automation) live? Net result on both questions:
**still not found as a numeric registration site** — but each daemon's real
architecture is now mapped in detail, two concrete bugs turned up along the
way (in `dji_rcam`'s calibration-file loader), and one real, unauthenticated
network service turned up in `dji_autotest`. All six passes used the
project's established toolchain (capstone/pyelftools, `.gnu_debugdata`
extraction where present, the literal-immediate-before-`bl` convention as the
first thing checked and, in every case here, ruled out).

## Headline correction: none of these five daemons use the `duss_event_register_dynamic_command` convention

Every single one of `dji_flight`, `dji_navigation`, `dji_autoflight`,
`dji_autotest`, and `dji_rcam` was checked for the `duss_event_register_
dynamic_command`-family import that `dji_sys`/`libduml_frwk.so` use, and
**none of them have it** — confirmed absent from `.dynsym`/`.rel.plt` in
every case, not just "not found in the functions examined." Each instead
joins the internal message bus a different way:

| Daemon | How it joins the bus | cmd_set/cmd_id carried how |
|---|---|---|
| `dji_flight` | Generic `duss_event_create_client`/`_send`/`_send_sync` client | Internal struct fields at event+`0x41c` (cmd_set) / +`0x41d` (cmd_id) — architecturally confirmed, no numeric literal recoverable |
| `dji_navigation` | Named client (`navigation_service`/`navigation`/`navigation_eagle`) via `duss_mb_create_route_table` + `duss_event_create_client`, config from `/system/etc/dji.json` (**absent from this firmware extraction**) | Private 32-bit internal "event-type" field (~1000–1801 decimal), not the wire-level single-byte DUML space |
| `dji_autoflight` | `duss_ps_*` publish/subscribe (a *different* API from `duss_event_*`) | String topic names (`fs/rectify/down/left`, `fs/osd_func`) — not numeric at all |
| `dji_autotest` | Generic `duss_event_create_client` bus client, **plus** its own custom TCP service (see below) | N/A for DUML; the TCP service uses its own 16-bit "item type" field, unrelated to DUML cmd_set/cmd_id |
| `dji_rcam` | Two named endpoints (`rcam`, `rcam_tld`) on an internal bus called `camera_service`, via `duss_mb_create_route_table` + `duss_dsh_create_channel_handle`/`duss_dsh_register_callback` | Bitmask flags (AE/AWB/AF/lens-adjustment enable bits) carried in the message itself — not per-cmd_id |

This means the "literal `cmd_set` in w1, `cmd_id` in w2, before a `bl` to
`duss_event_register_dynamic_command`" recovery technique that worked for
`dji_sys` and the built-in `libduml_frwk.so` table (see
`04_WM260_DAEMON_FINDINGS.md`) is a real pattern, but it is **not universal**
— these five daemons are message-bus *clients*, not *registrars*, and three
different alternative wiring schemes (`duss_event_create_client` + a private
internal event-type space, `duss_ps_*` string-topic pub/sub, and
`duss_mb_*`/`duss_dsh_*` named-endpoint channels) now have confirmed,
disassembly-traced examples in this codebase. A future pass on any other
daemon that comes up empty on the registration convention should check for
these three next, in that order.

## `dji_flight` — the actual flight-control-adjacent daemon, finally located; still no numeric cmd_set `0x03` registration

**Update, see `12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md` §1 addenda
for a direct follow-up:** a later pass fully disassembled this binary and
traced all six `system()`/`popen()` call sites to their actual arguments,
resolving the open "worth checking whether any `%s` is externally
influenced, inconclusive" question below about
`dji_verify -n geofense -H %s %s` and
`dji_fw_verify -n 1105 -c 1105 -o %s %s`. **Resolution: no** — every
argument at every one of the six call sites is a compile-time string
literal or a securely `mkstemp()`-generated temp path; none is built from
DUML/network-received data, through any call site that pass could locate.
See `12_...` for the full trace (including a latent, not-currently-
exploitable missing-defense-in-depth note about the command-building
wrapper's own lack of shell-metacharacter sanitization).

Confirms the device-type identity (`enums.py`'s `DeviceType.FLIGHT_
CONTROLLER=3`, firmware string `"flight"`) but is architecturally a generic
bus client, not a registrar — see table above. Two things worth separating
from that negative result:

- **Update, see `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track H for the direct
  follow-up on this exact lead.** The indirection blocking the scan below
  turned out to be a PIC addressing quirk specific to this binary (local
  addresses are stored as a relative delta plus a separate `add rX, pc`
  completion instruction, not as a bare pointer anywhere in the file) —
  once corrected for, the real entry addresses of 13 named `api_wp2_*`
  functions, including the three below, were recovered. But cmd_set `0x10`
  itself was then confirmed **not present anywhere** in this binary — not
  in any table, string, or literal immediate — ruling it out directly. A
  specific 19-entry dispatch table that follow-up pass initially thought
  it had found at this binary's `0xad0b0`-`0xad168` turned out, on
  independent re-verification, to be misread C++ RTTI/vtable data, not a
  real DUML table — don't trust that specific claim if it resurfaces. A
  separate, genuinely-evidenced `.data` array elsewhere in the binary
  (rooted at vaddr `0xae0f8`, confirmed `R_ARM_RELATIVE`-backed, and shown
  by a later independent pass to continue for 43+ records total, not just
  these 4) tags `api_wp2_set_global_cruise_vel`→cmd_id `0x06`,
  `api_wp2_get_global_cruise_vel`→cmd_id `0x07`,
  `api_wp2_pause_recovery`→cmd_id `0x08`, and
  `api_wp2_break_restore_waypoint_fly`→cmd_id `0x44`, all under cmd_set
  `0x22` — i.e. these specific WP2 functions belong to cmd_set `0x22`
  ("Demo Mode," see this document's own entry above), not `0x10` at all.
  This mapping, including the exact per-function ordering above, is now
  **independently confirmed** by a dedicated third pass done entirely
  from scratch (the first correction had the three-function order
  transposed — `pause_recovery` is last, `0x08`, not first).
- **A plausible, but statically unconfirmed, lead on cmd_set `0x10`
  (Automation), as originally found (see the Update above for the
  follow-up):** four fully-spelled internal API strings —
  `api_wp2_waypoints_upload_handle`, `api_wp2_waypoints_upload`,
  `api_wp2_download_waypoint`, `api_wp2_break_restore_waypoint_fly`
  ("WP2" = Waypoint-Mission-2.0) — sit inside real handler functions with
  real logic (a per-waypoint validator, an upload-loop driver, a dispatcher
  checking a sub-field against small constants and logging DJI-style error
  codes). None of `commands.json`'s existing cmd_set `0x03` waypoint/hotpoint
  entries (`0x22`/`0x24`/`0x25`/`0x6d`/`0x6e`) use "wp2" naming, so this is
  plausibly the Automation surface `04_WM260_DAEMON_FINDINGS.md` located
  architecturally (in `dji_sys`'s command-agent framework) but couldn't
  enumerate — found here, fully named, for the first time. However: an
  exhaustive direct-call-site scan, PC-relative-literal-pool resolution, and
  raw pointer byte-search of the whole binary found **no call site and no
  stored pointer referencing any of these three handler addresses anywhere**
  — they're reached through an indirection (vtable slot or computed jump)
  this pass couldn't resolve. No numeric cmd_id recoverable. Flagged
  low-confidence, not asserted.
- **Debug/upgrade-debugger code compiled into the production binary:** an
  embedded source path (`hardware/dji/service/flight/src/applications/
  nfz_data_upgrade/upgrade_debugger/src/upgrade_debugger.cpp`) and its
  `nfz_debug_init` log string confirm this exact code is compiled into the
  shipping binary and runs unconditionally at some init point — it just
  `fopen()`s an unresolved config path and fails safe (logs, continues) if
  absent. Given the name directly touches NFZ (see
  `06_NFZ_DATABASE_FINDINGS.md`), this was deliberately *not* pursued further
  (no file path, trigger condition, or format was investigated) — flagged as
  existing, not characterized.

## `dji_navigation` — OpenCV-heavy waypoint/vision-tracking service, not a cmd_set endpoint

**Update, see `12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md` §1 addenda
for a direct follow-up:** a later pass fully disassembled the NFZ-height-
limit backstop handler this section describes architecturally and
confirmed it concretely, down to the exact vaddr (`0x5c89c` for the
handler, `0x16b408` for the setter it calls): it reads a 16-bit field
directly from the incoming message-bus event payload (`[event+6]`) and
passes it straight into the height-limit setter with no additional
cryptographic or application-layer integrity check performed at this
layer. This confirms, rather than changes, the framing already below —
whether the underlying route-table/event-client layer authenticates the
sender before delivery remains unresolved either way.

2.25 MB, stripped, no `.gnu_debugdata`. Imports dozens of OpenCV symbols
(`solvePnPRansac`, `undistortPoints`, `Rodrigues`, `perspectiveTransform`) —
this is the visual waypoint-follow/tracking/panorama logic, not a protocol
dispatcher. Its real command surface is a ~30-branch internal dispatcher at
one address handling a private 32-bit "event-type" ID space (confirmed via
`ldr`, not `ldrb` — i.e. genuinely 32-bit, not a disguised byte field), fed
by two named bus clients whose actual routing configuration lives in
`/system/etc/dji.json` — a file confirmed **absent from this firmware
extraction** (`find` across the whole decrypted tree returns nothing), so
whether cmd_set `0x10`/`0x0f` frames get translated into this internal
event-ID space by that missing config file is a real, open question, not
resolved here. One file-parsing loop examined (`/data/waypoints.txt`) has an
explicit, correct 100-entry bound check — no bug there.

## `dji_autoflight` — confirmed ruled out for cmd_set `0x10`, with a specific reason

Supersedes the brief "ruled out" note in `04_WM260_DAEMON_FINDINGS.md`: this
isn't just "no evidence found," it's **structurally disqualified**. The four
`duss_event_*` symbols it imports (`create_client`/`start_client`/`send`/
`send_sync`) are dead code — a full dual cross-reference (manual Thumb
disassembly plus an independent `llvm-objdump` PLT-target grep) found zero
call sites to any of them. The only live inbound-message path is a
completely different API, `duss_ps_subscriber_create`, subscribing to two
string-named topics (`fs/rectify/down/left`, `fs/osd_func`) — internal
vision/OSD data topics, architecturally a different namespace from DUML's
numeric cmd_set/cmd_id space entirely. A possibly-dead validator function
elsewhere in the binary references `"cmdset too large"`/`"illegal cmdset
used"` strings, but its presumed caller chain is itself dead code in this
binary, so it couldn't even be confirmed reachable.

## `dji_autotest` — the factory/engineering daemon, and a real, concrete finding

**Update, see `09_DJI_AUTOTEST_EXPLOITABILITY_DEEPDIVE.md` for a much more
precise follow-up:** that pass found a second, previously-missed dispatch
layer (`router_thread` → `common_process`) reached over this same TCP
service, with a real, directly-confirmed `system()` command-injection
primitive and an ungated arbitrary-path directory-listing bug — but also
found the most dangerous capability (`system()`, and unrestricted file read)
is gated behind the device's own kernel boot command line already carrying
an engineering/factory/secure-debug flag, which meaningfully narrows the
threat model from "any Mavic 3 with `autotest_on` touched." The directory-
listing bug, by contrast, has no such gate and works on stock production
firmware. Read that document for the full precondition tree; the summary
below is the original, less precise pass.

This one has a genuine, confirmed security finding, not just an
architectural correction. `dji_autotest` is the WM260 factory calibration
daemon (confirmed via embedded source paths under `hardware/dji/service/
autotest/`). It imports no `duss_event_register_dynamic_command` and
contributes no new cmd_set/cmd_id entries — it's a bus client subscribing to
flight/IMU telemetry at several rates. The actual finding is in how it gets
turned on and what it does once it is:

- **Enablement is a bare file-existence check, no authentication at all.**
  `start_dji_system.sh`'s boot logic is: `if [ -f /data/dji/autotest_on ];
  then /system/bin/dji_autotest & fi`. `dji_autotest_on.sh` just does
  `touch`/`rm -f` on that path — no signature, credential, or production/
  engineering-mode distinction anywhere in the path. (A separate script,
  `dji_eng_happy.sh`, does check `/proc/cmdline` for a production flag, but
  tracing confirmed it is **never invoked** by anything in this file set and
  is architecturally unrelated to the `autotest_on` gate — correcting an
  initial hypothesis rather than forcing a connection that isn't there.)
- **Once running, it opens a plaintext custom-protocol TCP listener on port
  10000, bound to all interfaces (`INADDR_ANY`), with no authentication at
  all.** Disassembly of the bind call (`libv2_sdk.so`'s `my_tcp_bind`)
  confirms the socket address is explicitly zeroed (not `127.0.0.1` —
  checked and ruled out a loopback-only string found elsewhere in the same
  library, which turns out to be unused in this particular bind path). No
  password/auth/token/secret/crypto string of any kind exists in either
  `dji_autotest` or `libv2_sdk.so`. Per the daemon's own strings
  (`send_rgb_to_pc`, `maincamcali`/`monocamcali`, "subscribe main camera
  image"), this service streams raw/RGB camera frames and calibration/IMU
  data to whatever TCP client connects. The packet-type dispatcher that
  handles incoming requests on this socket *is* properly bounds-checked
  (rejects out-of-range type values before using them as a dispatch index) —
  checked specifically for an unchecked-index parser bug and didn't find one.
- **What's genuinely unresolved:** whether port 10000 is reachable only over
  a factory USB/debug interface or is exposed on the same network path as
  the normal companion-app/RC link. Static analysis alone can't answer that,
  and it's stated as an open question rather than assumed either way.

## `dji_rcam` — not a cmd_set `0x02` registrar either; two real, confirmed crash bugs

Corrects a hypothesis in `02_DEVICE_ADDRESSING_EXTENDED.md`'s reading of
`dji_rcam`'s `lens_ctrl_cmd_*` strings: those strings exist, but `dji_rcam`
itself never performs DUML-style cmd_set/cmd_id dispatch — it registers two
named endpoints (`rcam`, publish-only; `rcam_tld`, full duplex) on an
internal `camera_service` bus, and its real dispatcher fans incoming
messages out by an **AE/AWB/AF/lens-adjustment enable-bitmask**, not a
cmd_id switch. The likely explanation (synthesis, not disassembly-confirmed):
numeric DUML dispatch for camera/lens control terminates one layer up in
`dji_camera3`, and `dji_rcam` is the Linux-side translator down to the
already-documented LCPU "BLComm" lens-bus protocol (`01_BINARY_ANALYSIS_
FINDINGS.md`'s correction on module `0105`).

Two concrete bugs were found and confirmed at the raw-byte level in
`load_json_file` (the calibration-data JSON loader, recovered by name from
an embedded `__FILE__` string: `hardware/dji/service/camera/rcam_user/src/
testcmd/JSON_processor.c`):

1. `cJSON_GetObjectItem(root, "IQ")`'s return value is dereferenced at
   offset `+0x8` with **no NULL check** before the dereference — a
   malformed/truncated calibration file missing the top-level `"IQ"` key
   causes a NULL-pointer-read crash.
2. Two back-to-back loops each call `cJSON_GetArrayItem(array, i)` for a
   **hard-coded** `i = 0..3071` (not derived from the array's actual size)
   and immediately dereference the result's `->type` field with no NULL
   check — any calibration file whose numeric array has fewer than 3072
   elements crashes the daemon partway through loading.

Both are genuine, disassembly-confirmed defects, reported here exactly as
what they are — crash/DoS bugs in a file-format parser, not exploit
payloads, and not attempted to turn into anything more than that.

## `dji_sys`'s command-agent framework — corrected: not Binder-exposed, populated from a local config file

Direct follow-up and **correction** to `04_WM260_DAEMON_FINDINGS.md`'s
"Binder-exposed command agent" framing. A full `nm -D` sweep of every binary
on both images plus full-`.text` disassembly of `dji_sys` (recovered by name
from the E2 build's `.gnu_debugdata`) shows:

- None of `sys_command_agent_init/_add/_config/_request/_init_table/
  _deinit_table`, `command_agent_task`, or `sys_command_operation` appear in
  `dji_sys`'s `.dynsym` at all — **no other process can call them**, Binder
  or otherwise. Every call site resolves inside `dji_sys`'s own `.text`.
- There *is* a real cross-process Binder service hosted by `dji_sys`
  (`ISysModeManager`/`BnSysModeManager`, with `libsysmode_util.so` as the
  real client proxy linked by `dji_perception`/`sysmode_client`/
  `sysmode_test`) — but it's CPU/DDR-performance and wakelock/scene-switch
  arbitration (`doAcquireWakelock`, `doSetSystemPowerLevel`,
  `doRequestServiceCPUPerformance`, etc.), an entirely different subsystem
  that only superficially matches on the word "Manager."
- The real numeric `cmd_set`/`cmd_id` values are populated by
  `sys_load_config_from_json`, called exactly once from `dji_sys`'s own
  `main()`, parsing a local JSON file (fields literally named `"cmd_set"`
  and `"message_list"`) whose path comes from the process's own argv/env
  (`duss_sketch_get_config_file_name`/`duss_get_json_name_from_cmdline`) —
  **not** injected by another daemon over IPC as previously framed. That
  JSON file's path is not captured in this extraction (no `init.rc`/service
  definition was available to pin down the actual argv `dji_sys` is started
  with), so the literal values still can't be enumerated — but the honest,
  corrected statement is "a local config file this extraction doesn't
  capture," not "a runtime Binder registration this extraction can't trace."
- The full agent-record struct layout was recovered while in there (useful
  reference if that JSON file ever surfaces): `u8` cmd_id-count @`+0`,
  `u32` cmd_set @`+4`, `u16` @`+8`/`+0xa` (a destination-device-id field per
  log strings), `u64` cmd_id-array pointer @`+0x10`, `u64` second array
  pointer @`+0x18`. One minor config-robustness defect was noted (an array
  size read from the JSON gets silently truncated to a byte before being
  used consistently as both the malloc size and the loop bound — degenerate
  only at exactly 256+ entries, and only reachable by `dji_sys`'s own trusted
  startup parsing of a local file, not a network/Binder surface) — flagged
  as context, not listed as a security finding, since it doesn't fit any of
  the applicable impact categories on its own.

## Findings

| Function/component | Weakness | Impact category | Confidence |
|---|---|---|---|
| `dji_autotest`'s enablement (`start_dji_system.sh` boot gate + `dji_autotest_on.sh`) | The factory/engineering daemon — which opens a network-reachable camera/telemetry streaming service — is enabled solely by the presence of a plain flag file, checked with a bare `[ -f ... ]` test; no signature, credential, or production/engineering-mode distinction anywhere in the path | missing_authz | **high** |
| `dji_autotest`'s TCP/SDK service (`libv2_sdk.so`'s `my_tcp_bind` → `start_sdk` → packet dispatch) | Once enabled, opens a plaintext custom-protocol TCP listener on port 10000 bound to all interfaces, with no authentication, handshake, or peer allowlist anywhere in the traced path; streams raw/RGB camera frames and calibration/IMU data to any connecting client | info_disclosure | medium |
| `dji_rcam`'s `load_json_file` — missing NULL check on `cJSON_GetObjectItem(root,"IQ")` | A malformed/short calibration JSON file missing the `"IQ"` key causes a NULL-pointer-dereference crash | crash_dos | **high** |
| `dji_rcam`'s `load_json_file` — missing NULL check on `cJSON_GetArrayItem()` inside two fixed 3072-iteration loops | A calibration JSON file with a shorter-than-expected numeric array crashes the daemon via NULL dereference partway through loading | crash_dos | **high** |
| `dji_flight`'s generic authorization gate (called from 36 sites) | Fail-open by design: allows unconditionally when either of two bypass flags is set or when no authorizer callback is registered at all, and does not force-deny on an authorizer returning an out-of-range result code | missing_authz | medium |
| `dji_navigation`'s main event dispatcher (~30 branches) | No caller-identity/credential check found before acting on and responding to a received internal event — architectural, consistent with (not unique to) every other daemon examined in this project so far | missing_authz | low (explicitly: the upstream transport/pairing layer that would hold this answer, `dji_sec`/`dji_amt`, was examined separately in `05_DJI_SEC_FINDINGS.md` and found to use real cryptographic gating at *that* layer — this is only an observation about this one function) |

**What wasn't done, stated plainly:** the `api_wp2_*` cmd_set `0x10` lead in
`dji_flight` was not pushed past "handlers exist, no call site found" — that
would need a different technique (vtable/jump-table recovery) this pass
didn't attempt. `/system/etc/dji.json` (which would resolve `dji_navigation`'s
internal event-ID space back to wire-level cmd_set/cmd_id) and `dji_sys`'s
command-agent JSON config (same question for the rest of this cmd_set) are
both missing from this firmware extraction — neither was reconstructed or
guessed at. Real-world network reachability of `dji_autotest`'s port 10000
(factory/debug-only vs. reachable over the normal link) was not determined
and is stated as open, not assumed.
