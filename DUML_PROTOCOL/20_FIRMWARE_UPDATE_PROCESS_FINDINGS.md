# Firmware update/upgrade process: an end-to-end sweep

This document covers a dedicated investigation of the WM260/Mavic 3
firmware-update pipeline, requested alongside the activation-process
investigation (`18_ACTIVATION_TA_FINDINGS.md`) after the project owner
lifted the `libamt_util.so`/activation-TA exclusion — see
`BINARY_COVERAGE_TRACKER.md`'s "Authorization change" note. It also
closes out 3 of the 4 binaries pulled out of round 3's 50-binary tail
bucket (`libupgrade_common.so`, `Quectel_upgrade_tool`,
`quectel-qmi-proxy` — see `19_ROUND3_TAIL46_SWEEP_FINDINGS.md`).

**Methodology:** identical protocol to rounds 1-3 — 14 investigation
units (20 binaries/libraries total, counting both the E1E/32-bit-ARM
and E2/64-bit-aarch64 builds separately) each investigated by an
independent agent, briefed on the project's four known DUML
registration/send mechanisms and false-positive precedents, with no
access to any other agent's reasoning. Every candidate new
`(cmd_set, cmd_id)` pair that the pipeline actually routed to the verify
phase got 3 independent adversarial skeptic passes, default-refuting
unless the pair was independently re-derived from the raw ELF bytes.
Static analysis only: no binary was executed, no packet was crafted or
sent, no exploit/forgery code was written. Several of the 14 agents
noted a session-level "lift the other restrictions" instruction
reaching them mid-run via the harness's shared-context relay and
explicitly declined to act on it, holding the static-only/no-execution/
no-exploit-code line exactly as briefed — the same robustness pattern
already recorded in doc 19 Track AC. `libamt_util.so` itself was not
opened by this sweep (that is `18_ACTIVATION_TA_FINDINGS.md`'s target);
two incidental dependency-graph mentions of it are noted below for
whoever maps that TA's blast radius.

**Bottom line:** one new DUML command confirmed and added to the
registry (900th entry), 5 previously-"could not resolve dispatch"
command IDs independently confirmed live from the sender side, one
promising lead found but **not** adversarially verified (a pipeline
gap, flagged honestly rather than silently added), a second lead found
and explicitly refuted, the A/B-OTA architectural question definitively
answered ("genuinely wired up"), and a substantial set of
vulnerability-research-style architecture/security findings across the
verification chain, the orchestration layer, and the modem/PKCS7-signing
side-channels.

---

## Track BA — Firmware-package verification: two parallel mechanisms

**The primary path** (`dji_fw_verify` CLI → `libfw_util.so` →
`libfw_util_ca.so` → OP-TEE) was traced end-to-end and confirmed on both
architectures. `dji_fw_verify` is a pure CLI shim (`-n <module_name> -s
-c -o <path>`) that converts `-n`'s string into a 4-byte "module id" via
`str2id()` — an **unvalidated, truncated little-endian FourCC pack of up
to 4 characters, no allow-list, no length/charset check** — then calls
`dji_fw_verify_file()`, which chunks the file (≤32MB per chunk, or
operator-chosen `-s`) through `fw_util_verify_init/_update/_final`,
which are thin CA wrappers around `TEEC_InvokeCommand` into the
already-mapped Firmware-Verify TA (`09db16c0-873b-4fed-b87e-a5d2b86293a2`,
command IDs 3/4/5 per `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track F). None
of the project's four known DUML registration/send mechanisms appear
anywhere in this chain — it is a one-shot CLI tool invoked by shell
scripts, not a DUML-speaking daemon.

Two concrete defects were found in `dji_fw_verify_file()`, confirmed
byte-identically on both the ARM32 (e1e) and AArch64 (e2) builds:

- **A broken retry loop.** A 50-attempt retry counter is initialized,
  but on the *first* failure the code `unlink()`s the input file
  *before* checking whether retries remain — every subsequent "retry"
  then immediately fails to `fopen()` the now-deleted file. The final
  pass/fail exit code is still correct (callers aren't fooled), but this
  is a genuine reliability defect: the function never actually retries,
  and the verification target is always deleted as a side effect of the
  first failure.
- **A TOCTOU-shaped pattern.** Rather than pinning one fd/inode for the
  whole verify pass, the function re-opens the same pathname *by string*
  for every chunk (`open`→`lseek`→`read`→`close`, repeated), with no
  inode/mtime check tying one open to the next. Layered on top of the
  already-documented `ota.sh` flow (verify exits → shell branches on the
  exit code → a *separate* process, after a reboot into recovery,
  re-reads the "same" path to actually flash it), this is two distinct,
  concretely-observable TOCTOU windows. Documented as a structural gap
  only — no attempt was made to demonstrate or trigger a race, per this
  project's static-analysis-only scope.

**`libupgrade_upgrade.so`'s streaming variant** (`upgrade_stream_unsign_
package_init/_unsigning/_final`) independently calls the same
`dji_fw_verify_file_init/_update/_final` chain, confirmed correctly
ordered (verify-then-write: each chunk is only `fwrite()`n if the TA
call returns 0 — no write-before-verify TOCTOU here). This extends doc
14's "that library itself out of scope" note with concrete call-site
evidence, and confirms the ION `size_kb` argument (relevant to doc
12/14's pre-existing `size_kb=0` 32-bit-shift DoS finding) is
data-supplied at this call site, not a compile-time constant.

**A second, previously-undocumented verification path exists** for the
`mcu`/`eagle`/`rk3399` sec_types, inside `libupgrade_upgrade.so`:
`mcu_up_sec_verify`/`eagle_up_sec_verify`/`rk3399_up_sec_verify` are
byte-identical functions (both ISAs) that build and `popen()` a shell
command — the literal rodata string is `dji_fw_verify -n %s -c %s -o %s
'%s'` — read its stdout, and correctly decode the real process exit
status via `pclose()`. At least two of the four `%s` slots are filled
from the function's own runtime arguments, with **no visible
sanitization against shell metacharacters** before the string reaches
`popen()`. This is the same command-injection-shaped primitive category
already recorded for `libupgrade_product.so` in
`17_ROUND2_RESIDUAL_SWEEP_FINDINGS.md` (see the corrected attribution
there) — reachability of the untrusted-input question (can the
module/chip-name or path arguments ever carry attacker content) was not
traced further, out of scope for this pair of libraries.

| Finding | Impact category | Confidence |
|---|---|---|
| `dji_fw_verify_file()` retry loop deletes the file on first failure, never actually retries | reliability | high |
| `dji_fw_verify_file()` re-opens the same path by string per-chunk, no inode pinning (TOCTOU-shaped, layered on `ota.sh`'s own reboot-boundary gap) | integrity / TOCTOU (unconfirmed exploitability) | medium |
| `str2id()` accepts any string as an unvalidated truncated FourCC "module id" | architecture note | high |
| `mcu_up_sec_verify`/`eagle_up_sec_verify`/`rk3399_up_sec_verify` build a `popen()` shell command from partially caller-supplied strings with no visible escaping | command-injection-shaped (unconfirmed reachability) | medium |

## Track BB — The A/B OTA scheme: genuinely wired up, now fully traced

This resolves the open architectural question flagged in prior docs
("is the `[AB_OTA]`-prefixed code real or vestigial?") definitively:
**it is real, live production code**, traced through a concrete call
chain rather than inferred from string proximity:

1. `update_engine` (e1e) / `dji_update_engine` (e2) are **not** Google's
   real AOSP `update_engine` A/B-payload daemon — zero occurrences of its
   characteristic class names (`DeltaPerformer`, `PayloadConsumer`, ...).
   Both are DJI builds of the legacy Android `/sbin/recovery` "updater"
   binary (edify interpreter + its own independent whole-zip
   `verify_file()` signature check against `/res/keys`), repurposed to
   run standalone and renamed.
2. DJI added a custom `[AB_OTA]` layer on top, implementing A/B
   redundancy specifically for the raw eMMC `boot0`/`boot1` hardware boot
   partitions (not Android's generic dynamic-partition A/B scheme):
   toggling `force_ro`, storing slot-state tags via a custom `/dev/unrd`
   tool backed by a `/dev/block/by-name/env` partition, reading
   `androidboot.slot_suffix` from `/proc/cmdline`.
3. The real caller is `libeagle_md_up.so` (linked against
   `libupgrade_communication.so`/`libupgrade_status_push.so`/
   `libupgrade_upgrade.so`/`libupgrade_common.so` — the DUML-aware
   upgrade-orchestration layer). It parses a JSON manifest key
   `self_update_tool` with three values — `Recovery` → hand off to the
   existing `ota.sh`/recovery flow; `Android6_AB` → exec `update_engine
   --update_package=/cache/ota.zip`; `Android9_AB` → exec
   `dji_update_engine --update_package=/cache/ota.zip`.
4. The plugin's primary `upgrade()` path on E2 doesn't call
   `dji_update_engine` directly at all — it manually re-implements
   `ota.sh`'s own `/cache/recovery/command` hand-off. The direct
   `update_engine`/`dji_update_engine` exec is a *secondary*
   `continue_upgrade()`/`reboot()` step, per the plugin's own embedded
   comment ("we need to upgrade the other partition too!(A/B upgrade)") —
   i.e. the eMMC A/B step runs as a follow-up to, not a replacement for,
   the single-partition recovery flow.
5. `libupgrade_upgrade.so` and `libupgrade_product.so` themselves also
   carry real (non-stub) A/B-aware functions (`set_flag_upgrade_ab_both`,
   `upgrade_force_up_both_ab_part`, a `upgrade_both_ab_partition` JSON
   config key parsed identically in `libupgrade_init.so` on both
   architectures) — independent, corroborating evidence from the
   app-orchestration side that the A/B concept is wired into the live
   call graph, not confined to the `update_engine` binaries alone.

Three further findings from this track:

| Finding | Impact category | Confidence |
|---|---|---|
| Result-verification is inconsistent across the three `self_update_tool` modes — only `Android6_AB` has an implemented post-hoc success check (`grep`s `/cache/recovery/last_log`); `Recovery` and `Android9_AB` explicitly log "result check not support now!" and skip it | reliability / integrity-reporting gap | high (string evidence); untraced (downstream DUML-status effect) |
| Both physical eMMC boot copies' write-protection (`force_ro`) is lifted together, unconditionally, rather than one at a time during a slot switch | robustness/availability (power-loss resilience), not a confirmed corruption path | medium |
| Both binaries statically bundle a full `mmc-utils` CLI (including raw RPMB key read/write), BoringSSL's X.509 OID table, and AVB-version strings, inside a privileged, signature-gated OTA binary — reachability via any secondary entry point was not determined | attack-surface/code-bloat | medium |

## Track BC — Orchestration layer: `dji_upgrade` and the `libupgrade_*` chain

`dji_upgrade` itself is a pure cJSON-config-driven lifecycle shell (no
`dji_fw_verify`/ota/recovery/slot strings anywhere) that establishes a
DUML bus-client handle via one of two mutually-exclusive paths — one of
which is a **config-driven trust-switch**: when a config flag byte is
zero, a raw config-supplied handle value is written directly into the
live client-handle field with only a non-null check, bypassing the
normal registration path entirely (this independently re-confirms, with
exact cross-arch instruction-level evidence, a weakness doc 12 §7 had
already flagged but not verified this precisely). It then `dlopen()`s a
config-named `product_lib_name` plugin with **zero canonicalization,
allowlist, hash, or signature check**, and `dlsym()`s 5 lifecycle entry
points by literal name before invoking the first one immediately with
the (possibly-unvalidated) client handle. Both weaknesses are now
confirmed cross-arch with exact addresses, not just on the E1E build
doc 12 originally covered.

A debug/test-named library, `libupgrade_core_test.so`, is a **hard,
non-optional DT_NEEDED dependency** of the real production `dji_upgrade`
daemon (via `libupgrade_commu_demo.so`), on both architectures — not
dlopen-only/optional tooling. Its lifecycle hooks are genuinely called
on every daemon startup. Investigating it turned up a **5th, previously
uncatalogued DUML-adjacent dispatch shape**: its
`upgrade_core_test_event_callback` is a real, wire-reachable handler
(reached via the generic mechanism-#2 client registration) that, after a
correctly-implemented length bound-check, dispatches on one sentinel
"phase" value (`0x100`) into `upgrade_core_test_sync_entry`/
`_async_entry`, which perform an **indirect function-pointer call whose
target is looked up via `upgrade_common_cmd_get_cmd_func(module_id,
group, id)`** — a cross-library (`libupgrade_common.so`), process-global,
runtime-populated registry, **keyed by 3 raw bytes copied verbatim from
the incoming wire event with no validation of the triple itself**. This
is architecturally distinct from all four previously-catalogued
mechanisms: a generically-registered DUSS client whose payload bytes
become a lookup key into a *separate* library's live function-pointer
table, rather than a static `(cmd_set, cmd_id)` registration.

**Honest open gap, not glossed over:** which handler functions are
actually registered in that `upgrade_common_cmd_get_cmd_func` registry
could not be established in this pass. The one init-time registration
call site that could be cleanly disassembled only ties to a trivial
3-entry stub table; the call sites for the imported
`upgrade_common_cmd_save_cmd`/`_init_cmd_list` (which must exist
somewhere, since both are real PLT imports) fall in a region that
defeated both `objdump` and a capstone-based linear disassembler —
almost certainly an inline literal-pool/jump-table region with no
symbol boundary in this stripped binary. This is a genuine **tooling
gap**, flagged for a dedicated follow-up pass with a function-boundary-
aware disassembler, not a claimed absence of exposure. The larger,
functionally significant tables this registry might expose
(`up_package_mngr_test_set_antirollback_value`, the
`up_module_test_single/multi_module_upgrade` family) are not imported by
any *other* binary in the firmware tree, so if reachable at all from
outside this library, it's only via this same runtime registry.

Further confirmed-negative and confirmed-positive findings across the
orchestration chain:

| Finding | Impact category | Confidence |
|---|---|---|
| `libupgrade_module_mngr.so`'s `up_mm_set_state`/`up_mm_ready_reboot_uc`/`up_mm_request_reboot_uc` index fixed lookup tables directly with an unvalidated state integer (both ISAs); `up_mm_count_all_module_state` goes further and computes a 2-D offset from two unchecked fields to both read and *write* into the **caller's own** buffer | memory-safety / missing-bounds-check (OOB read + OOB write into caller memory); reachability depends on the only 2 callers, outside this round's scope | high (mechanism); medium-low (reachability) |
| `libupgrade_status_control.so`'s `do_upgrade_status_change_action()` indexes its 9-slot status-action table with an **unvalidated** caller-supplied id and performs an indirect call through a pointer read from that slot — in contrast to its sibling `add_upgrade_status_change_action()` in the same file, which validates the identical index before the identical computation | memory-safety / OOB-index-to-indirect-call; reachability from untrusted input not established (no network surface in this library itself) | high (mechanism, both ISAs); low (reachability) |
| `libupgrade_event.so`'s `upgrade_get_version_ack` reads a fixed-offset/fixed-size struct from an inbound message with no length parameter, unlike its sibling `upgrade_update_status` which explicitly carries a `msg_size` field | potential OOB read / info disclosure in DUML message parsing | plausible, unconfirmed (caller/dispatcher validation not analyzed) |
| `upgrade_device_register_interface` (`libupgrade_register.so`) correctly validates an exact-length check on a sync-ack response before trusting its payload — a negative/defensive finding, documented per the task's request to look for the absence of a bug too | negative result / sound validation | high |
| `libdji_sec_ds_whitelist_upgrade.so`'s sole export, `upgrade_check_version_whitelist`, is a 4-byte stub (`movs r0,#0; bx lr`) that unconditionally returns "pass" — its only caller treats a 0 return as "not blocked." Immediately after the stub, the same `.text` contains a large (~6KB), structurally coherent but completely unreachable ASN.1 BER-style TLV decoder. The check is additionally gated opt-in per-module by a manifest flag that defaults off. Importantly, the primary signature-verification call (`upgrade_package_verify_image`) runs unconditionally regardless of this check's outcome — this is a disabled/vestigial secondary policy gate, not a break of firmware signature verification | disabled/no-op security control + vestigial dead code | high |

## Track BD — PKCS7 signing (`p7_sign`) is live, and so is a weaker key path

Settling the open background question: `p7_sign` is **not** leftover
factory tooling. `dji_lte`'s `relay_service`/`pkcs7_util_sign` feature
builds the exact command line `p7_sign -t %d -c %s -i %s -p %s -v %d -b
%d -o %s 2>&1` at runtime and runs it via `popen()`, reading the result
back from `/data/sign.out`.

- **Command-injection-shaped primitive, incomplete denylist.** Before
  calling `popen()`, `dji_lte` checks the assembled command string for
  exactly two characters — `;` and `$` — and aborts (logging "potential
  command injection") if either is found. This denylist **does not
  cover backtick substitution, `|`, `&`, newline, quotes, or
  redirection**, any of which would still reach `popen()` (which execs
  via `/system/bin/sh -c`). One of the format string's `%s` slots (the
  device-certificate path, `-c`) is populated from a caller-supplied
  request structure; whether that field can ever carry untrusted content
  was not traced (would require analyzing `dji_lte`'s own request-parsing
  entry points, out of scope here).
- **Weak static key used instead of the device's TEE-backed signer.**
  `dji_lte` always supplies `/system/etc/fake.priv` — an unencrypted,
  literally-named "fake" private key file — for `p7_sign`'s `-p`
  argument, even though the same `dji_lte` binary separately imports and
  calls `libamt_util.so`'s `https_client_sign` (`rsa_sign`) elsewhere for
  what is presumably the device's real, TEE-backed per-device signing
  key. (This `libamt_util.so` dependency is noted here only as a
  cross-reference for whoever maps that TA's blast radius in
  `18_ACTIVATION_TA_FINDINGS.md` — it was not itself investigated.)
- **`p7_sign`'s own TEE-backed path is dead code.** The binary links
  `https_client_sign`/`https_check_private_key` and contains two small
  trampoline functions for them, reachable only via an otherwise-
  unreferenced 2-pointer table that no instruction in the binary ever
  dereferences. `main()`'s actual signing path exclusively uses the
  file-based "fake" key.
- `p7_sign` itself is a bare, unauthenticated CLI primitive with no
  verification counterpart and no caller-identity check — by design, it
  trusts whoever can exec it with arguments. The weak point is entirely
  in its one caller's argument construction (above), not in `p7_sign`'s
  own simple, faithful implementation of what its help text promises.

## Track BE — The LTE/modem update chain: a separate, weaker trust domain

`Quectel_upgrade_tool` is an unmodified build of Quectel's public
`QFirehose_Linux_Android_V1.4.10` reference tool (Sahara handshake +
Firehose XML flashing of the modem's own storage). `quectel-qmi-proxy`
is unrelated — a QMUX/QMI control-plane socket proxy for ordinary modem
AT/QMI traffic, with zero upgrade-related strings; it's dropped from
this investigation's scope as a non-finding. `dongle_upgrade_test.sh` is
a factory/QA stress-cycling harness.

The real orchestrator is `dji_lte` (not itself one of this round's
assigned targets, but the only binary anywhere in the firmware tree
referencing `Quectel_upgrade_tool`/`quectel-qmi-proxy`/QFirehose by
name). This directly answers the open question about whether the modem
chain reuses `dji_fw_verify`/the TA infrastructure: **it does not.**

- `dji_lte` spawns the flash via `popen("Quectel_upgrade_tool -n -f %s
  -l %s")` — explicitly passing QFirehose's own `-n` ("skip MD5 check")
  flag. The only application-layer integrity check anywhere in this
  chain is an **MD5 checksum** against a bundled `md5.txt` — not a
  cryptographic signature — and production invocation explicitly skips
  even that. All actual trust for the flashed modem image is delegated
  to the Qualcomm modem SoC's own on-chip Secure Boot (Sahara hash-table
  authentication, OEM public-key-hash and anti-rollback-version fuses) —
  a root of trust DJI's own PKI does not control, architecturally
  disjoint from `dji_fw_verify`/the OP-TEE Firmware-Verify TA used for
  the drone's own OS and recovery images.
- `dji_lte` also builds this `popen()` command by interpolating a
  package-directory path with **no visible escaping** in the format
  string itself — a second, lower-confidence (unconfirmed reachability)
  command-injection-shaped lead in the same binary as Track BD's.

| Finding | Impact category | Confidence |
|---|---|---|
| Modem-firmware trust is MD5-only at the DJI application layer, and that check is explicitly skipped (`-n`) at the point of actual flashing; real trust is entirely the Qualcomm modem's own secure boot, outside DJI's PKI | weak/absent application-layer authenticity check — supply-chain / firmware-integrity gap on a network-facing but non-flight-critical subsystem | high (absence of any DJI signature check); medium (practical exploitability — modem fuse config not independently verified) |
| `dji_lte` interpolates a path argument into a `popen()`-launched `Quectel_upgrade_tool` command with no visible escaping | potential command injection via unsanitized path interpolation | low-medium (plausible from the format string; upstream sanitization of the path not traced) |

## Track BF — DUML command findings

**Confirmed and added to the registry** (3/3 independent adversarial
re-derivation from raw ELF bytes, all three votes `refuted: false`):

| cmd_set | cmd_id | Name | Found in | Evidence |
|---|---|---|---|---|
| `0x00` | `0x5B` | FTP Control (Start/Stop) | `test_upgrade` (E1E/ARM32) `check_ftpd_start_control`/`check_ftpd_stop_control` | Both set the request struct's cmd field to literal `0x5B` immediately before `duss_event_send_sync`, targeting `dji_sys` (module `0x0801`); differ only in a flag byte (offset `0x14`: `1` for start, memset-default `0` for stop). `0x5B` is absent from cmd_set `0x00`'s catalog (`0x59`/`0x5A`/`0x5C` are catalogued, `0x5B` was a gap); the pre-existing `0x02`/`0x5B` "Discon State Get" is a different, non-conflicting namespace. |

This is the project's **900th** command. Added to `commands.json`,
`ALL_COMMANDS.csv`, `cmdset_00_General.md`, and regenerated into
`duml_c/generated/registry_data.cpp`.

**The same `test_upgrade` binary independently confirmed, from the
sender side, 5 of the 7 command IDs this project had explicitly flagged
as an unresolved dispatch gap** (`cmdset_00_General.md`'s binary
investigation note, originating in `14_FOLLOWUP_DEEPDIVE_FINDINGS.md`
Track E): `0x07` (Enter Loader) via `check_fw_entry`, `0x08` (Update
Confirm) via `check_fw_start`, `0x09` (Update Transmit) via
`check_fw_transmit` (a chunked send loop with per-chunk
`fseek`/`fread`), `0x0A` (Update Finish) via `check_fw_finish` (attaches
a 16-byte MD5 digest), and `0x41` (Fw Update Push Control) via
`check_update_control` — all sent to `dji_sys` (module `0x0801`) the
same way as `0x5B` above. These were already named/catalogued, so they
are not new registry entries (`already_known: true`, correctly excluded
from the verify phase), but they resolve half of the project's own
explicitly-documented gap: the dispatch logic is confirmed real and live
from the client/sender side, even though the *handler*-side dispatch
inside `dji_sys` that receives them still hasn't been found with
confidence. `0x40`/`Fw Update Desc Push` and `0x43`/`Fw Upgrade Finish`
remain fully unresolved on both sides. `cmdset_00_General.md`'s note was
updated accordingly. The same binary also reconfirmed `0x2A` (FileTrans
General Trans) phase-1/phase-2 usage for an unrelated `test.sig` file
transfer, matching the existing catalog dissector exactly.

**Found but explicitly refuted — not added, documented for the record:**

| cmd_set | cmd_id | Why it didn't survive |
|---|---|---|
| `0x01` | `0x78` | Found via a clean literal-immediate descriptor build in `libupgrade_upgrade.so` before an `upgrade_send_directly` call. 2 of 3 skeptics refuted: the claim mischaracterized the handler as an "unexported static helper" when it is in fact the exported symbol `upgrade_coldreboot_devices_and_notify` (a cold-reboot/notify routine, not a generic status push as originally proposed), and — more substantively — no skeptic could independently confirm that struct offsets `0x14`/`0x15` specifically represent a `cmd_set`/`cmd_id` pair rather than some other internal field (the one skeptic who traced one layer deeper, into `libupgrade_communication.so`'s packet-build routine, found the fields are copied into the outgoing bus-event structure but never named `cmd_set`/`cmd_id` by any log string — only "method"/"msg_id_index" are named). This is exactly the kind of struct-offset/DUML-cmd-id conflation this project's own doc 10 and docs 14/00 had already flagged as a known risk for this exact 4-library upgrade plugin chain. **Not added to the registry.** |

**Resolved by a targeted follow-up pass (2026-11-17):** `0x18`/`0x3D` was
re-derived from scratch rather than trusted from the original circumstantial
match, using the fixed pipeline (the `already_known` filter bug above is
corrected in the saved template). **Added to the registry** as the 901st
entry — `cmd_set 0x18` ("LTE/Dongle Diagnostic", a previously-uncatalogued
cmd_set — known sets had stopped at `0x11` before jumping to `0x22`) /
`cmd_id 0x3D` ("Upgrade/Downgrade Test Trigger") — but with its scope kept
deliberately narrow, reflecting a real 2-of-3 adversarial split rather than
a clean pass:

- **Independently reproduced, byte-exact, by all three reviewers:** the
  *sender* side. `dji_mb_ctrl`'s own `getopt` jump table was decoded
  straight from the raw ELF bytes (not trusted from its usage string) and
  confirmed to pack `-s`/`-c` into a literal `cmd_id | (cmd_set << 16)`
  word, handed to `duss_event_send_sync_v2`; `-g 08 -t 06` pack into
  destination word `0x0806` (device-type `8` / index `6`). Device-type `8`
  is this project's own already-catalogued `DeviceType.DM36X_AIR` /
  firmware string `"ve_air"` (`duml_py/duml/enums.py`,
  `02_DEVICE_ADDRESSING_EXTENDED.md`) — an independent cross-check the
  original lead never had. `/etc/dji.json`, extracted read-only from both
  images via `debugfs`, confirms `dji_lte` is the only service whose
  message-bus identity resolves to that exact `(type=8, idx=6)` pair, and
  its registered callback (resolved via its own `R_AARCH64_RELATIVE`
  relocation, not guessed) opens with `cmp w8,#0x806; b.ne <bail>` — an
  exact match to the sender's own destination packing.
- **Where the three reviewers actually split:** one of three independently
  and fully disassembled the function the claim named as `dji_lte`'s
  handler (vaddr `0xb108`) and found it contains **no branch on `cmd_set`
  or `cmd_id` anywhere** — it's a generic DUML-frame-field logger reused for
  every message addressed to that identity, not a command-specific
  handler, and therefore doesn't by itself support the proposed name
  "Upgrade/Downgrade Test Trigger" as a description of what `0x3D`
  *does*. The other two reviewers agreed this specific point was never
  pinned down (the candidate's own confidence field already said so) and
  weighed the claim's honest hedging plus independently-reproduced
  plumbing more heavily; one of them additionally found fresh,
  uncited corroboration — the literal `dji_mb_ctrl -c 3d 01616161...`
  ("start upgrade") / `-c 3d 03616161...` ("start downgrade") invocations
  inside `dongle_upgrade_test.sh` itself — which does support the *name*
  even though it doesn't resolve the *dispatch-site* question. Per this
  project's reverify rule (`refuted` only if ≥2 of 3 skeptics refute), the
  candidate survives 2-of-3.
- **What this means for the registry entry:** the `(cmd_set, cmd_id)` pair
  and its sender/addressing mechanism are confirmed to the same standard
  as every other entry in this catalog. The *name* describes the sender
  tool's own stated intent, not a confirmed receiver-side function — no
  reviewer, including the two who didn't refute, found where (or whether)
  `dji_lte` actually branches on `0x3D` specifically versus any other
  command addressed to the same identity. This is recorded here rather
  than silently smoothed over in the registry's own terse `name` field,
  which has no confidence column.
- A separate, previously-conflated lead is now resolved as unrelated:
  `dji_lte`'s `'test enable[%d]'` strings (what the original pass thought
  might be this command's handler) actually belong to the Android sysprop
  `lte.dev.update` (set by this same shell script's own
  `setprop lte.dev.update test` line) gating a distinct "skip firmware-list
  re-pull" bypass flag in `dji_lte`'s upgrade state machine — unrelated to
  the `0x18`/`0x3D` DUML send, and not itself re-examined for reachability
  here (out of scope, flagged for any future pass that wants it).

**One further open question, explicitly left unresolved rather than
asserted either way:** `test_upgrade`'s `check_get_device_version`
issues two additional literal-cmd sends, `0x0B` and `0x0C`, beyond its
primary `0x01` (Version Inquiry) query. These numerically coincide with
the already-catalogued General names "Reboot Chip" (`0x0B`) and "Get
Device State" (`0x0C`), but the printed response content (a loader
version string; a hardware-id + protocol-version pair) doesn't obviously
match either command's existing byte-level dissector fields. There may
be a per-target sub-selector this pass didn't decode, or the existing
catalog dissector (sourced from the community app-facing Lua dissector)
may simply not describe this internal `dji_sys`-targeted usage
correctly. Flagged for a future pass, not resolved here.

## Completeness statement

Of this round's 14 investigation units (20 binary/library files across
both architectures), plus a targeted follow-up pass on 2026-11-17: **2 new
DUML commands confirmed and added** (900th registry entry, `0x00`/`0x5B`;
901st, `0x18`/`0x3D`, added with its sender-side-only confirmation scope
explicitly documented above), **5 previously-unresolved command IDs
confirmed live from the sender side** (`0x07`/`0x08`/`0x09`/`0x0A`/
`0x41`), **1 candidate found and explicitly refuted** (`0x01`/`0x78`), and
**1 open semantic question left unresolved** (`0x0B`/`0x0C` in
`test_upgrade`). The A/B-OTA architectural
question is definitively resolved (genuinely wired up, fully traced).
Three of the four binaries pulled out of round 3's 50-binary tail
bucket are now closed (`libupgrade_common.so`, `Quectel_upgrade_tool`,
`quectel-qmi-proxy` — the last ruled unrelated to firmware update
entirely). A substantial set of independent architecture/security
findings were produced across the verification chain (Track BA), the
A/B mechanism (Track BB), the orchestration layer (Track BC), the
PKCS7-signing side-channel (Track BD), and the modem-update chain
(Track BE) — named weakness, impact category, and confidence throughout,
consistent with this project's vulnerability-research-only documentation
standard. No binary was executed, no packet was crafted or sent, and no
exploit, forgery, or cryptanalysis code was produced at any point in
this sweep, including when several agents noted a relayed instruction
suggesting otherwise was in scope — it was not, and they correctly
declined it. `libamt_util.so` was not opened by this sweep.
