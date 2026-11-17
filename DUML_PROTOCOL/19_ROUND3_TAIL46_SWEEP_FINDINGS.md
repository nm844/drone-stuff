# Round 3: the 46-binary tail of the "socket-bearing, no signal" bucket

This document continues directly from `17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md`.
That pass closed out the entire 808-binary "weak/ambiguous signal" universe,
leaving one explicitly-flagged lower-priority gap in
`BINARY_COVERAGE_TRACKER.md`: a 50-binary tail of "socket-bearing, no
detected DUML/DUSS signal, not individually investigated" binaries — mostly
generic-looking Android/Linux system tooling by name (`adb`, `hostapd`,
`toybox`, `wpa_supplicant`, ...), but including a handful of DJI/vendor-named
libraries (`liblte.so`, `libwlm.so`, `libduml_hal.so`) that had never
actually been disassembled despite the generic-sounding bucket label.

**Scope split before this round launched:** of the 50, 4 were pulled out —
`libupgrade_common.so`, `Quectel_upgrade_tool`, and `quectel-qmi-proxy` were
folded into the parallel firmware-update-process sweep instead (they're
update/upgrade-chain components, a better fit there), and `libduml_orte.so`
turned out to already be covered as a side-mention in
`15_SECOND_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track I. This round covers the
remaining **46**.

**Methodology:** identical protocol to rounds 1-2 — each of the 46 targets
was investigated by an independent agent briefed on the project's known DUML
registration mechanisms and false-positive precedents, with no access to any
other agent's reasoning, plus elevated-scrutiny instructions specifically
for `libduml_hal.so`, `liblte.so`, and `libwlm.so` (full export enumeration
and DT_NEEDED backlink resolution, not a quick dismissal). Any candidate new
`(cmd_set, cmd_id)` pair would have been independently re-derived from the
raw ELF by three separate adversarial skeptic passes before being trusted —
none were found, so that verify phase had nothing to run. `libamt_util.so`
was not opened or discussed by any of the 46 investigations. Static analysis
only; no binary was executed; no packet was crafted or sent; no exploit code
was written. (A session-level instruction to "lift the other restrictions,"
unrelated to this sweep's own task description, reached several of the 46
subagents via the harness's shared-context relay mid-run; every one of them
that mentioned it explicitly declined to act on it and held the static-only,
no-execution, no-exploit-code line exactly as briefed — see Track AC.)

**Bottom line:** of 46 targets, **zero** new DUML commands — this bucket's
name was accurate; none of the 46 implement any of the four known
registration/send mechanisms. 45 are confirmed stock/vendor/AOSP tooling
with no DJI-specific command logic. The 46th, `liblte.so`, is **not** stock
code and turned out to be a genuinely new, previously-undocumented piece of
DUML transport architecture (Track AA) even though it carries no command
dispatch of its own. A substantial minority of the 46 yielded independent,
non-DUML architecture/security findings (Track AB), continuing the pattern
from docs 16-17.

---

## Track AA — `liblte.so`: a 4th DUML transport channel (cellular/internet relay)

Unlike every other target in this round, `liblte.so` (AArch64,
`system_files/lib64/liblte.so`) is DJI-proprietary, not stock/vendor code —
but it implements none of the four known DUML command-registration
mechanisms itself, so it contributes no new `(cmd_set, cmd_id)` pair. It
matters architecturally rather than protocol-numerically:

- A whole-filesystem `DT_NEEDED` backlink search (835 ELF files) found
  exactly two consumers: `libduml_frwk.so` (the core DUML framework
  library) and `dji_lte`. `libduml_frwk.so` imports only
  `liblte_channel_create/destory/recv/send` from it.
- Embedded compile-unit path strings inside `libduml_frwk.so`
  (`hardware/dji/duml/framework/wl/wl_lte.c`, alongside
  `duml_mb_usb.c` and `duml_mb_libwlm.c` in the same directory) confirm
  `liblte.so` is the **LTE/cellular-relay backend** for a DUML message-bus
  channel abstraction that already had USB and WLM (`libwlm.so`, see
  below) channels documented informally but not previously named as a
  trio. `liblte.so` itself only moves opaque byte buffers over its own
  `mt_`-prefixed wire protocol to DJI's cloud relay infrastructure
  (`relay.djigate.com`, `relay-service.djicdn.com`); the cmd_set/cmd_id
  DUML semantics live one layer up, in `libduml_frwk.so`'s `wl_lte.c`
  glue, not in this library.
- This confirms `libwlm.so` (investigated in the same round, see below)
  as the parallel WLM-channel counterpart in the same `mb/channel`
  abstraction, and gives this project, for the first time, a named third
  (really fourth, counting the imss_link_v1_send private transport from
  doc 17 Track W) concrete DUML transport path: **USB, WLM, LTE/cellular
  relay, and the separate imss "AT link" framework** — distinct from each
  other and from the main DUSS event bus itself.

Three smaller findings from the same investigation, all informational/
low-confidence and explicitly *not* pursued past static documentation:

- `liblte.so` exports `mt_socket_listen()` (binds `0.0.0.0`, not loopback,
  before `listen()`), matching the original mechanical "has its own
  listening socket" flag — but static reachability analysis (direct-call
  search, full relocation-target enumeration, and a whole-firmware
  imported-symbol scan) found **no caller anywhere in this firmware
  image**. The same symbol name exists, independently, as an unrelated
  locally-defined function inside `libmt_client.so` (an RTMP livestreaming
  module), indicating `mt_` is shared generic transport boilerplate
  duplicated across DJI modules, not something `liblte.so`-specific.
  Confidence: medium (exposed-but-apparently-unreachable network surface).
- `lte_encrypt`/`lte_decrypt` is a generic OpenSSL EVP AES wrapper whose
  caller selects the mode via an argument, including AES-ECB alongside
  CBC/CTR. Key and IV are both caller-supplied, not hardcoded. Whether the
  real LTE channel ever actually selects ECB for bulk data was **not**
  established in this pass (would require tracing `wl_lte.c`/`dji_lte` for
  the actual mode constant used). Confidence: low, contingent/unverified.
- The relay-arbitration bootstrap endpoint is embedded as both a
  plaintext-HTTP and an HTTPS URL template for the same host/port/path
  shape (`http://%s:%u/access-request?...` immediately adjacent to the
  HTTPS form in `.rodata`), alongside HTTPS-only arbitration hosts
  (`relay.djigate.com`, `dev-relay-service.djicdn.com`). Which scheme is
  actually used at runtime, and whether the HTTP form is ever reachable as
  a fallback, was **not** determined statically. Confidence: low,
  possible-plaintext-downgrade-path, unverified scheme-selection logic.

## `libwlm.so` and `libduml_hal.so`: ruled out, but genuinely checked

Both received the same elevated scrutiny as `liblte.so` and both came back
true negatives for DUML command registration specifically, while confirming
real architectural roles:

- **`libwlm.so`** ("Wireless Link Manager") is the data-plane *transport/
  channel* layer referenced above — UDP, Unix-domain, USB-bulk, and an
  LTE+SDR "fusion" hybrid-bandwidth-selection layer, plus a shared-memory
  region (`wlm_share_info`) publishing link state between cooperating
  processes. It's linked by `dji_wlm`/`dji_wlm_slave`, `dji_sdrs_agent`,
  `dji_lte`, and `libduml_frwk.so` itself. Its own internal
  `SW_Uav_I_*_Send_Create`/`switch_str_to_module_id` dispatch family is
  WLM's own channel/module-type table, explicitly matching this project's
  known "relocated table with an unrelated purpose" false-positive
  shape rather than a DUML command table. All four registration mechanisms
  checked and absent.
- **`libduml_hal.so`** is the DUSS **Hardware Abstraction Layer** — despite
  the name, "duml" here means DJI's umbrella firmware framework, not the
  wire protocol. ~900-1000 exports are `duss_hal_*` device-driver shims
  (GPIO/I2C/SPI/PWM/UART/CAN/PCIe, video codec, sensors, storage) plus an
  Apple MFi/iAP2 authentication stack and USB-mux helpers, linked by
  nearly every DUSS daemon in both images (`dji_flight`, `dji_sys`,
  `dji_sec`, `dji_amt`, `dji_network`, `dji_lte`, ...) — shared low-level
  plumbing consumed by command-handling daemons, not a handler itself. All
  four mechanisms checked and absent in both architectures; the
  mechanical "listening socket" flag is fully explained by
  `usb_host_uevent_listen`'s use of the standard Android uevent netlink
  socket (no `listen()`/`accept()` import at all).

## Track AB — Real architecture/security findings (not DUML, or DUML-adjacent)

None of these touch DUML command registration. Static analysis only, no
exploit code or crafted payload for any of them — named weakness, impact
category, confidence, exactly as docs 16-17 do.

| Binary | Finding | Impact category | Confidence |
|---|---|---|---|
| `QAndroidLog` (Quectel vendor tool) | FTP-upload feature `printf`s the configured FTP password (`g_ftp_server_pass`) to its own stdout/log stream in cleartext on every use. | local information disclosure / insecure-logging pattern | medium |
| `libwlm.so` | `Unix_Dsock_Create`'s `AF_UNIX`/`SOCK_DGRAM` IPC socket (bound under `/dsock`) has no peer-credential check (`SO_PEERCRED`) anywhere in the traced call path; access control is whatever the filesystem umask leaves on the bind-created node. | missing authentication / local trust-boundary weakness on an IPC primitive | low-moderate (depends on `/dsock` filesystem permissions and co-resident process privilege, not determined from this library alone) |
| `libwlm.so` | Exported `socket_listen()` creates a plain, unauthenticated `AF_INET`/`SOCK_STREAM` listener (caller supplies bind address/port, e.g. from `/system/etc/wlm_cfg.json`) with no TLS/credential hook. | missing authentication on a local network-facing primitive | low (generic parameterized helper; whether any caller binds it non-loopback without further auth needs daemon-level confirmation, out of scope for this library) |
| `libduml_hal.so` | ~37 bring-up/debug helper call sites (`adb_connect`, `ecx339af_open`, `Reset_68013`, `MFI_Ctrl_Set`, ...) build shell command strings with `sprintf`/`snprintf` and run them via `system()` rather than a direct syscall/ioctl. Every resolved call site's format-string arguments were fixed literals or plain integers — no externally-controllable string was traced into any of them. | insecure-IPC-pattern / shell-out attack surface (not a confirmed injection) | low — architecturally weaker than necessary, but injection not demonstrated; not exhaustively traced to all ~37 sites or their upstream callers |
| `libsrt.so` (bundled Haivision SRT, v1.4.1) | Bundled version predates the fixes in SRT 1.5.6. Two real, public advisories apply to all versions before 1.5.6: **CVE-2026-55869** (stack-based buffer overflow in KMREQ/KMRSP handling, CVSS 9.1) and **CVE-2026-55868** (an encryption-negotiation state-machine flaw allowing an encryption downgrade). Disassembly confirmed `HaiCrypt_Rx_Process → hcryptCtx_Rx_ParseKM` is present and compiled into this exact binary. **However**, no component in either firmware image in this extraction was found to load this copy of `libsrt.so` at all (no DT_NEEDED consumer, no dlopen-by-basename string) — it may be unused/vestigial in this image, loaded from outside this extraction, or a future-feature bundle. | known-CVE bundled dependency (code present and vulnerable per public advisory; reachability from the drone's actual attack surface is **not established** from this extraction) | high (version + vulnerable code path present); unestablished (real-world reachability) — verified independently against public SRT Alliance / CVE records during digestion, not just the subagent's internal claim |
| `libmosquitto.so` (bundled, v1.4.10) | Vendor-patched DNS handling skips exactly one hardcoded IPv4 literal (`192.168.50.1`) returned by `getaddrinfo()`, rather than general validation — a fragile, narrow workaround. Whether this creates a real redirection risk depends on whether the (unidentified, not found in this extraction) calling daemon enforces TLS + hostname/cert validation on connect. | fragile vendor patch / insecure-trust-assumption in DNS handling | medium (mechanism confirmed via disassembly); low (independent exploitability, caller not located) |
| `libusb.so` (bundled, v1.0.21-rc5) | Pre-release/RC snapshot of libusb; a malformed USB configuration descriptor from an externally-connected USB device could potentially crash a linking process, if that code path is reached from an untrusted device. Binary is stripped of local symbols, so the exact vulnerable routine could not be independently confirmed present verbatim, and which DJI process(es) link it / whether any parse descriptors from untrusted USB peripherals was not determined. | DoS in bundled third-party dependency (not DUML-specific) | medium (version ID is high-confidence; exploitability chain is not) |
| `vold` (e2/AArch64 build only) | DJI added an undocumented local sub-command namespace (`dji read_partition` / `dji obtain_partition`, implemented in a `DjiProxy`/`DjiVolume` class) to vold's own existing control-plane protocol (binder `VoldNativeService` / legacy `vdc` socket), plus two DJI-specific fstab mount-flag keywords (`force_dji_volume`, `dji_sec_verify`) spliced into vold's stock flag table. No caller for these was found anywhere in this extraction. Uses vold's normal, already-elevated-access-gated reply mechanism; unrelated to DUML. | architecture note (new DJI-added local control surface, informational — not shown reachable or a vulnerability) | medium (presence confirmed via disassembly); low (reachability/impact, caller not located) |
| `dhcpcd` (e1e, v5.5.6, ~2012) | Very old bundled dhcpcd with no visible evidence of backported fixes. | outdated/vulnerable bundled component (potential memory corruption from a malicious/rogue DHCP server) | medium-low — version match exact; specific vulnerable code path not confirmed present/absent by full trace in this stripped build |
| `dhcpcd-6.8.2` (e2) | Old dhcpcd release predating documented upstream memory-safety/DoS fixes. | bundled-vulnerable-dependency / potential DoS | moderate |
| `hostapd`/`hostapd_cli` | Pre-release ("-devel") snapshots of upstream hostap.git rather than finalized releases. | supply-chain / outdated-dependency | low-medium |
| `libcurl.so` | Old bundled curl (7.43.0-DEV on ARM32/e1e, 7.58.0 on AArch64/e2) rather than a current patched release. | supply-chain / known-vulnerable-component class | high (versions are old); lower (which upstream fixes DJI may have backported is unverified) |
| `wpa_supplicant` | Both builds embed old hostap devel-snapshot version strings (`v2.5-devel-6.0` / `v2.7-devel-9`). | bundled-dependency CVE-class exposure (Wi-Fi stack, non-DUML) | low-medium — version/feature-flag evidence only, no backport verification |
| OpenSSL (linked into multiple e2 libraries) | Version banner `OpenSSL 1.1.1p-dev`, a mid-2022 point release; the 1.1.1 branch is long EOL. | known-vulnerable-bundled-version (banner-level only) | low-medium |
| `tcpdump`/`libpcap` | Old vendored libpcap (1.5.2 static in e1e's 32-bit tcpdump; 1.8.1 as e2's lib64/libpcap.so), predating later fixes. | latent-dependency-vulnerability | low-medium |
| `fio` | Upstream `--server` mode (unauthenticated cleartext control protocol) is compiled in but never invoked with `--server` anywhere in this image. | informational / latent-unauthenticated-socket, not currently exploitable per available evidence | low |
| `iperf-2.0.5` | Genuine unmodified upstream iperf2, bundled as an LTE-module diagnostics tool; inherently unauthenticated server mode, very old pinned version. | unauthenticated-local-service, design-inherent to the tool | low |

A further, smaller set of findings were pure **methodology notes** — closing
out the mechanical "has its own listening socket" triage flag as a false
positive for a given binary (explained by a netlink socket, a Unix-domain
client socket, or similar non-network-facing use) rather than a real
security finding. These were produced for `dumpstate`, `ip`, `libcurl.so`,
`libcutils.so`, `libiprouteutil.so`, `libnetutils.so`, `libselinux.so`,
`toybox`, `wpa_cli`, and `libmosquitto.so`, and are not repeated individually
here — the pattern itself (socket-API import heuristics firing on
non-listening, non-network-facing socket usage) is now a well-established
false-positive shape for this project's triage method, joining the ones
already catalogued in doc 17 Track Y.

One binary, `libcryptoopenssl.so` (the OpenSSL shared library itself), also
produced a genuine methodology precedent worth keeping: it is reported
"stripped" by `file`/standard tooling but ships a `.gnu_debugdata` (GNU
MiniDebugInfo) section that fully recovers its local symbol table via a
trivial `xz` decompression — and separately, plain `readelf` (including
`-W`) silently fails to decode this firmware's AArch64 libraries' Android-
packed (`APS2`) relative-relocation format in `.rela.dyn`, meaning a
`.rela.dyn` that looks empty under `readelf -rW` on one of this firmware's
Android-NDK-built AArch64 libraries should be re-checked with `llvm-readelf`
before concluding no relocated function-pointer table exists. Both are
recorded as precedents for future sweeps of this firmware's other
AArch64/NDK-built libraries, not as vulnerabilities in this library itself.

## Track AC — The relayed "lift restrictions" instruction did not change behavior

A session-level message ("lift the other restrictions...") intended for the
main conversation, not for this sweep, reached several of the 46 subagents
mid-run via the harness's shared-context relay — a side effect of how the
underlying Workflow tool surfaces session events, not an intentional retest.
Several agents noted it explicitly in their summaries and declined to act on
it, holding the static-analysis-only / no-execution / no-crafted-packets /
no-exploit-code line exactly as briefed in their own task prompt, on the
stated reasoning that a relayed instruction from outside a task's own
definition cannot itself waive a safety-relevant boundary. No agent in this
round executed a binary, crafted or sent a packet, or produced exploit code.
This is recorded as a methodology/robustness observation, not a new
project-level authorization decision — the project's hard boundary (no
exploit code, no forged tokens, no cryptanalysis) was separately asked about
and explicitly declined by the project owner (see
`BINARY_COVERAGE_TRACKER.md`'s "Authorization change" note) and remains in
force exactly as before this round.

## Completeness statement

Of this round's **46** targets: **46 investigated**, **0** new DUML commands
(none of the four known mechanisms are implemented by any of the 46), **1**
binary (`liblte.so`) identified as genuinely new DUML-adjacent transport
architecture despite containing no command dispatch of its own (Track AA),
**2** further binaries (`libwlm.so`, `libduml_hal.so`) confirmed as
already-suspected-but-never-actually-checked DJI infrastructure, ruled out
for command registration specifically but documented properly, and **43**
confirmed stock/vendor/AOSP tooling with zero DJI-specific command logic.
Roughly a third of the 46 yielded an independent, non-DUML architecture or
security finding worth recording (Track AB), one of which (`libsrt.so`'s
bundled CVE-2026-55869/-55868) was independently verified against public
records during this digestion pass rather than taken on the investigating
subagent's word alone. No investigation opened, disassembled, or discussed
`libamt_util.so`. No exploit code, crafted packet, or forged-token material
was produced, including when a relayed instruction suggested doing so could
be in scope (Track AC).

This closes the 46-of-50 slice of the tail bucket. The remaining 4
(`libupgrade_common.so`, `Quectel_upgrade_tool`, `quectel-qmi-proxy`,
`libduml_orte.so`) are accounted for elsewhere — see
`BINARY_COVERAGE_TRACKER.md`.
