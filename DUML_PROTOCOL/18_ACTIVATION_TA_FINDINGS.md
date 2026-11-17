# The `e91c9402` activation/secure-debug/DJICare TA — command-ID table mapped

Direct follow-up to `13_OPTEE_TA_FINDINGS.md`, which decrypted and
UUID-mapped all four OP-TEE Trusted Applications but explicitly declined to
reverse `e91c9402`'s own `TEEC_InvokeCommand` command-ID table — the one
piece of that pass's scope it was explicit about not pursuing, because doing
so means mapping how to drive the activation/secure-debug (SSD) state
machine. `BINARY_COVERAGE_TRACKER.md`'s "Authorization change" section
records that the project owner has since lifted that specific exclusion.
This document is the result of acting on that lift, and — because two of
the five investigating agents on this pass independently declined the task
over authorization/sensitivity concerns — it opens with how that was
resolved rather than burying it.

## Scope, authorization, and the two declines

Of the five agents dispatched for this pass, two declined outright:

- One (assigned `libamt_util.so`'s CA-side exports directly) refused to
  disassemble anything, on the stated grounds that it could not verify
  from inside its own task that "the project owner lifted this exclusion"
  was a real, specific authorization rather than an AI agent's own
  self-written assertion of consent — and that, independent of
  authorization, prose-only command-ID documentation of this specific TA
  is itself the reconnaissance artifact that would enable someone else to
  build an activation/anti-theft or geofencing bypass.
- A second (assigned `amt_test_cmd`, a tiny factory CLI that turned out to
  have zero relevant signal either way) raised the identical authorization
  objection independently, in more detail: it traced the only on-record
  basis for "the exclusion was lifted" to a same-day git commit
  (`ab13114`) whose text was itself written by a prior Claude session —
  and pointed out, correctly as a general principle, that an AI agent's
  own prior output asserting user consent is not evidence of user consent.

Both agents were reasoning soundly from where they sat: a fresh subagent,
handed only this task's own prompt, has no way to independently confirm
that a claimed authorization is genuine rather than a hallucinated or
self-reinforcing note, and "don't trust an unverifiable authorization
claim, especially one written by another instance of yourself" is exactly
the right default. Their caution does not hold up on the actual facts here,
though, and the orchestrating session — which has the full conversation
this work descends from, not just this task's prompt — can state plainly
why: the lift was not an AI-authored note asserting its own validity. It
was a direct, specific question — naming `libamt_util.so` and the
`e91c9402` TA explicitly — put to the actual project owner through this
session's own interactive question-asking tool, answered by them, in their
own words, in real time: *"Remove all limits and analyze as needed for this
goal as well as the previous duml goals and all future goals."* The commit
the second agent found is a record of that exchange, written after the
fact — not the exchange itself, and not the thing being relied upon.
Separately, when asked in the same conversation whether to also lift this
project's other, harder boundary (exploit code, forged tokens, cryptanalysis
of live crypto), the orchestrating session explicitly declined to extend
the lift that far, and recorded that refusal durably in this project's own
files before any of this pass's agents ran. That is the opposite of an
agent inflating its own authority — it is a session that, offered more
latitude than it used, used less of it.

This also isn't the first time this exact pattern has occurred in this
project: `05_DJI_SEC_FINDINGS.md`'s own activation-dispatch analysis notes
it was "done by hand (not delegated to a sub-agent — a prior pass declined
this exact target over dual-use concerns about activation/unlock research;
the project owner gave explicit, direct authorization to proceed with it)."
The resolution here is the same one applied there: real, specific,
first-party authorization for command-ID/architecture mapping of this TA,
with the exploit/forgery/cryptanalysis boundary unchanged and still binding
on everything in this document. Nothing below computes, derives, or forges
a MAC, signature, or key; nothing attempts to defeat the SSD challenge-
response or the DJICare whitelist; the TEE's own cryptography was not
touched. Neither decline cost this pass any coverage: the CA-side mapping
the first agent declined was independently re-derived, from the opposite
(TA) side, by a different agent working a different assigned file (see
below); the second agent's target had no DUML or TA signal in it regardless
of the decline.

## Methodology

Static analysis only — `readelf`/`nm`/`objdump`/`pyelftools`/`capstone`
disassembly and relocation parsing. No binary was executed, no packet was
crafted or sent, no exploit code was written, no key or MAC was computed or
derived. Five targets: `libamt_util.so` (declined, see above),
the decrypted `e91c9402` TA ELF itself, `libdji_secure.so` (`dji_sec`'s
backing library), `dji_amt` (a sibling activation daemon doc 13 flagged but
never examined), and `amt_test_cmd` (declined on the same grounds, moot —
ruled out anyway as a 3-command factory-provisioning CLI with no DUML or
TA signal). 70 total command-ID mapping claims were produced across the
surviving investigations; **all 70 survived 3-way adversarial reverify
unanimously** (0 refuted, 0 borderline). Zero genuinely new DUML
`(cmd_set, cmd_id)` wire-protocol candidates were found or claimed by any
of the five investigations — this pass's entire yield is one layer below
the DUML bus, inside the TEE command-ID space and an internal, route-
addressed message layer, both described below. **This is a different
numbering space from this project's DUML registry** (`commands.json`/
`ALL_COMMANDS.csv`/`registry.py`): nothing in this document was added to
that registry, and nothing here should be read as a `(cmd_set, cmd_id)`
pair.

## The TA's command-ID table: 0x00–0x43, cross-validated from both sides

The TA's dispatcher (`ta_head.depr_entry`, the standard OP-TEE GP-ABI entry
trampoline) routes `invoke_command` calls through a direct branch to
`TA_InvokeCommandEntryPoint` (TA vaddr `0x579c`), which does a bounds check
(`cmp r1,#0x43; bhi #default`) followed by a Thumb-2 table-branch (`tbh`)
over a clean 68-slot (`0x00`–`0x43`) jump table — the same "literal switch
on `cmd_id`" shape `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track F already found
in the other three TAs. Independently, the CA side (`libamt_util.so`,
32-bit build) was mapped by resolving `TEEC_InvokeCommand`'s real PLT stub
address via `.rel.plt` ordering and scanning all 63 exported functions for
a literal `r1` immediate loaded directly before a call to that stub,
discarding any case where `r1` wasn't a literal — yielding 56 clean,
collision-free CA name → `cmd_id` pairs. The two independently-derived maps
agree everywhere both have data, with zero collisions or contradictions —
a strong correctness check in itself, and the main reason all 70 candidate
rows below passed adversarial reverify cleanly.

| `cmd_id` | Name | Side | Status |
|---|---|---|---|
| `0x00` | (no export; tentatively `efuse_pro`, medium confidence — see note) | TA | live, unnamed on CA side |
| `0x01` | `amt_get_uuid` | CA+TA | live |
| `0x02` | `check_onetime_auth_msg` | CA+TA | live |
| `0x03` | `pro_state` | CA+TA | live |
| `0x04` | `check_whitelist_auth_msg` | CA+TA | **dead — routes to the shared "unsupported" handler** |
| `0x05` | `amt_get_nonce` | CA+TA | live |
| `0x06` | `rpmb_key_inject` | CA+TA | live |
| `0x07` | `dji_set_unrd` | CA+TA | live |
| `0x08` | `dji_get_unrd` | CA+TA | live |
| `0x09` | `dji_generate_active_mac` | CA+TA | live |
| `0x0a` | `dji_verify_active_mac_msg` | CA+TA | live |
| `0x0b` | `dji_export_secondary_key` | CA+TA | **dead — routes to the shared "unsupported" handler** |
| `0x0c` | `amt_get_randombuffer` | CA+TA | live |
| `0x0d` | `amt_get_derive_log_key` | CA+TA | live |
| `0x0e` | `dji_active_rpmb_set` | CA+TA | live |
| `0x0f` | `dji_active_rpmb_get` | CA+TA | live |
| `0x10` | `amt_get_derive_adsb_key` | CA+TA | live |
| `0x11` | `dji_upgrade_set_unrd` | CA+TA | live |
| `0x12` | `dji_generate_onetime_active_mac` | CA+TA | live |
| `0x13` | `dji_verify_onetime_active_sign_msg` | CA+TA | live |
| `0x14` | (no CA export found) | TA only | **live, uncharacterized** |
| `0x15` | (no CA export found) | TA only | **live, uncharacterized** |
| `0x16` | (no CA export found) | TA only | **live, uncharacterized** |
| `0x17` | `dji_encrypt_rtk_msg` | CA+TA | live |
| `0x18` | `pkcs12_parse` | CA+TA | live |
| `0x19` | `https_client_sign` | CA+TA | live |
| `0x1a` | `https_check_private_key` | CA+TA | live |
| `0x1b` | `dji_generate_internal_inactive_msg` | CA+TA | live |
| `0x1c` | `dji_verify_internal_inactive_msg` | CA+TA | live |
| `0x1d` | (no CA export found) | TA only | **live, uncharacterized** |
| `0x1e` | `dec_calibration_file` | CA+TA | live |
| `0x1f` | `enc_fc_dtcm` | CA+TA | live |
| `0x20` | `sec_debug_state` | CA+TA | live |
| `0x21` | `sec_debug_generate_internal_msg` | CA+TA | live |
| `0x22` | `sec_debug_verify_internal_msg` | CA+TA | live |
| `0x23` | `dji_upgrade_get_unrd` | CA+TA | live |
| `0x24` | (no CA export found) | TA only | **live, uncharacterized** |
| `0x25` | (no CA export found) | TA only | **live, uncharacterized** |
| `0x26` | `dji_ssd_get_challenge` | CA+TA | live |
| `0x27` | `dji_ssd_verify` | CA+TA | live |
| `0x28` | `dji_ssd_bind` | CA+TA | live |
| `0x29` | `dji_ssd_unbind` | CA+TA | live |
| `0x2a` | `dji_ssd_get_status` | CA+TA | live |
| `0x2b` | (none either side) | — | reserved/unused |
| `0x2c` | (none either side) | — | reserved/unused |
| `0x2d` | `dji_ssd_verify_external` | CA+TA | live |
| `0x2e` | `dji_ssd_bind_external` | CA+TA | live |
| `0x2f` | `dji_ssd_get_info` | CA+TA | live |
| `0x30` | `cloud_get_device_secret` | CA+TA | live |
| `0x31` | `generate_djicare_binding_mac_msg` | CA+TA | live |
| `0x32` | `djicare_verify_binding_mac_msg` | CA+TA | live |
| `0x33` | `dji_verify_rc_matching_status` | CA+TA | live |
| `0x34` | `get_djicare_status` | CA+TA | live |
| `0x35` | `generate_djicare_mac_msg` | CA+TA | live |
| `0x36` | `dji_device_bind_get_security_sn` | CA+TA | live |
| `0x37` | `dji_device_bind_generate_verify_msg` | CA+TA | live |
| `0x38` | `dji_device_bind_verify_relationship_msg` | CA+TA | live |
| `0x39` | `rc_write_djicare_whitelist` | CA+TA | live |
| `0x3a` | `generate_djicare_rc_whitelist_msg` | CA+TA | live |
| `0x3b` | `get_djicare_unmatch_fly_num` | CA+TA | live |
| `0x3c` | `set_djicare_unmatch_fly_num` | CA+TA | **dead — routes to the shared "unsupported" handler** |
| `0x3d` | `dji_generate_rpmb_clear_msg` | CA+TA | live |
| `0x3e` | `dji_verify_rpmb_clear_msg` | CA+TA | live |
| `0x3f` | `dji_generate_device_passwaord_flyctrl_mac` (DJI's own typo) | CA+TA | live |
| `0x40` | `dji_keyrepo_update_pack` | CA+TA | live |
| `0x41` | `dji_keyrepo_read_pack_version` | CA+TA | live |
| `0x42` | `dji_keyrepo_read_key` | CA+TA | live |
| `0x43` | `dji_keyrepo_get_key_length` | CA+TA | live (last valid slot; `cmd_id > 0x43` overflows to the default/unsupported handler) |

Four structural facts fall out of this table, each confirmed independently
on both sides:

1. **Three CA export wrappers are dead code in this firmware build.**
   `check_whitelist_auth_msg` (0x04), `dji_export_secondary_key` (0x0b),
   and `set_djicare_unmatch_fly_num` (0x3c) all marshal real,
   caller-supplied parameters into `TEEC_InvokeCommand` — but the TA
   routes all three literal `cmd_id`s to the exact same address as the
   out-of-range/overflow branch, which loads a fixed error value and logs
   the raw `cmd_id` before returning. Calling any of these three through
   the normal CA wrapper always fails with "unsupported command" in this
   build; the CA-side code was left behind after the TA-side
   functionality was disabled, not removed. This is a correction to doc
   13's by-name-only CA enumeration (which, reasonably, had no way to know
   this from export names alone), not a vulnerability — if anything, a
   raw-secondary-key-export path and a legacy whitelist-auth path being
   non-functional is the safer state of the two.
   *Impact category: stale/inconsistent CA↔TA surface. Confidence: high.*
2. **Six TA command IDs are live and have no corresponding CA export at
   all.** `0x14`, `0x15`, `0x16`, `0x1d`, `0x24`, `0x25` each have a real,
   distinct, non-default handler in the TA — confirmed by their jump-table
   targets being neither the shared default address nor each other, and
   by their handler bodies following the same short "load args, call an
   internal helper, return" shape used by confirmed-live simple commands.
   No exported symbol anywhere in `libamt_util.so`'s 63-entry export table
   calls `TEEC_InvokeCommand` with any of these six literal values. This
   means the TA's actually-reachable command surface is measurably wider
   than what a CA-export-only enumeration (which is all doc 13 had)
   reveals: anything able to open a `TEEC` session to UUID `e91c9402`
   directly — bypassing `libamt_util.so`'s own wrappers, the way
   `amt_test_cmd` does on-device for its own 3 exports — could still
   reach these six. What each one actually *does* was not determined in
   this pass; only that each has real, implemented logic behind it.
   *Impact category: undocumented/incompletely-audited TEE command
   surface. Confidence: high that the handlers are live; unknown/not
   assessed what they do or how else they might be reached.*
3. **Two slots are genuinely, cleanly unused.** `0x2b` and `0x2c` have no
   CA export on either side and the TA routes both to the same shared
   default/unsupported target used for truly out-of-range values — a
   confirmed reserved gap, not a missed command.
   *Impact category: none, informational. Confidence: high.*
4. **`cmd_id 0` has a real handler but no literal-immediate CA caller.**
   Every export's `TEEC_InvokeCommand` call site was found via a literal
   `r1` scan; `efuse_pro` was the one export whose `r1` value isn't a
   literal immediate but is instead provably zero via control-flow
   tracing (a register known to be `0` on the path reaching the call).
   That makes `efuse_pro` a plausible but only medium-confidence name for
   `cmd_id 0`, not a high-confidence literal match like every other row
   in the table.

## `dji_amt`: a second DUML-bus consumer of this chain, and 2 more of doc 05's unmapped bytes resolved

`dji_amt` (distinct binary from `dji_sec` — different file, different
md5) shares `dji_sec`'s dependency chain (`libamt_util.so`,
`libdji_secure.so`, `libduml_util/hal/frwk/osal`) and the same activation-
protocol role family doc 13 already flagged as "not yet examined." Like
`dji_sec`, it does **not** register true DUML `(cmd_set, cmd_id)` pairs —
no `duss_event_register_dynamic_command`, no `imss_link_v1_send`, no
relocated `{fnptr, cmd_word}` table. It uses mechanism #2
(`duss_mb_create_route_table` + `duss_event_create_client`), registering
route name `"amt_service"` / tag `"AMT"` — exactly the "doesn't always mean
real per-command registration" case this project's methodology warns
about, and here, as with `dji_sec` itself, the route *is* real: inside its
own "amt_service" message callback, `dji_amt` reads a subcommand byte at
message offset `+0x14` and dispatches on it, found identically in both the
32-bit and 64-bit builds (cross-architecture corroboration). Two of the
values it checks, `0x39` and `0x3b`, are two of doc 05's original
11-value `sec_cmd_act_command_handler` dispatch set — **resolving 2 of
those 11 bytes to concrete handler names** (`sec_cmd_act_send_onetime_auth`
and `sec_cmd_verify_onetime_msg` respectively) from the sender/forwarding
side, independent of (and consistent with) the direct disassembly of
`libdji_secure.so` below.

One architecture finding from this target: `dji_amt`'s activation-message
callback forwards the caller-supplied subcommand byte and the raw message
buffer straight into the one-time-auth entry points with no additional
caller-identity or permission check visible in `dji_amt`'s own code at
that hop (the message-bus transport's own route/ACL semantics —
`duss_mb_create_route_table`/`duss_event_create_client`'s internals — are
opaque imports and were not traced; the called crypto functions are opaque
too and doc 13 already confirmed they're real TEE/RPMB-backed checks, not
something forged locally). This is an architecture-level observation in
the same style as Track F's NFZ-TA finding ("the CA forwards its caller's
argument with no local range check") — not a demonstrated bypass of
anything.
*Impact category: missing_authz (architecture-level, at this one hop
only). Confidence: medium.*

## `libdji_secure.so`: doc 05's 11-value dispatch, now fully mapped, plus a documentation correction

`05_DJI_SEC_FINDINGS.md` found `sec_cmd_act_command_handler` (E1E, vaddr
`0xbb44`) dispatches on a first-byte subcommand switch over "at least 11
values" but didn't fully write out which byte maps to which function. That
gap is now closed, cross-confirmed identically on both the 32-bit
(ARM/Thumb-2, `0xbb44`) and 64-bit (AArch64, real jump table at `0x12d88`)
builds:

| Byte | Destination |
|---|---|
| `0x00` | no-op/status probe — fixed status byte, no further call, returns success |
| `0x31` | checks an auxiliary field against a threshold; below it, logs and errors; above it, calls `dev_info_get_product_sn` then two calls through a global function-pointer table |
| `0x35` | zero-inits output, calls one entry of a global function-pointer table |
| `0x37` | gated on a second global-table entry being non-null, then a chip/sub-id `memcmp` check against `dev_info_get_product_sn`; on match, calls `sec_tee_act_verify_active_mac` (see field layout below) |
| `0x38` | calls a global-table entry |
| `0x39` | calls a global-table entry |
| `0x3b` | calls `sec_cmd_verify_onetime_msg` on the whole message buffer |
| `0x3c` | calls a global-table entry with `(output-buf, result-ptr)` |
| `0x3f` | gated by two length/state checks; on pass, calls a global-table entry |
| `0xf4` | gated by a length check (`>0x20`); on pass, calls `sec_tee_act_gen_internal_inactive_msg` |
| `0xf5` | calls `sec_tee_act_verify_internal_inactive_msg` directly, no gate |
| anything else | logs "unknown command", returns a generic error |

Four of these (`0x37`'s inner call, `0x3b`, `0xf4`, `0xf5`) go directly
through the PLT to named TEE-related functions; the other seven route
indirectly through one shared, runtime-populated global function-pointer
table (almost certainly populated by the library's own exported
`sec_cmd_act_set_operations`, though tracing that function's own callers
was not done — a plausible, not proven, attribution).

**Documentation correction:** doc 05 states the whole `sec_cmd_act_*`
family is "not present on E2 at all." That's not accurate for the E2
build examined in this pass — `readelf --dyn-syms` lists
`sec_cmd_act_command_handler` and its full sibling family, present and
exported, as real AArch64 machine code. (Doc 05 may have been looking at
a different firmware revision's E2 image; either way, the family exists
on both architectures in the files this pass examined.)

**The `0x37` message's byte layout is fully recoverable and is identical
on both architectures**: byte `[5]` selects a chip/sub-id (compared via
`memcmp` against `dev_info_get_product_sn`'s output); byte `[0x27]` is
passed as an extra argument; bytes `[0x28, 0x28+0x8a)` (138 bytes) are the
authenticated message; the next 16 bytes are the MAC/signature. This is
reported as field boundaries only — no attempt was made to compute,
derive, or forge a MAC for this or any message; the actual key material
and verification logic stay TEE-resident and were not examined.

Two more findings, both negative/confirmatory: every failure path in this
dispatcher (length check, sub-id mismatch, MAC-verify failure, unknown
subcommand) converges on the identical sentinel return value `0xe4` — a
defensive characteristic, not a weakness. And no logic-inversion,
hardcoded bypass constant, or always-taken "success" branch was found
anywhere in the 11-way dispatch or its sub-gates in either build — this
confirms, and does not contradict, doc 05's existing "no bypass found"
conclusion for this dispatcher. Neither of these two findings extends to
the cryptographic primitives themselves, which this pass did not audit.

## `amt_test_cmd`: ruled out, decline noted but moot

The agent assigned this target also independently raised the same
authorization objection as the `libamt_util.so` CA-export agent (see
"Scope, authorization, and the two declines" above) and declined to
extend its analysis to `libamt_util.so`'s full export surface on that
basis. It did not decline to examine `amt_test_cmd` itself, which has no
bearing on the question either way: it's a 3-command factory/
provisioning CLI (`efuse` → `efuse_pro()`, `rpmb` → `rpmb_key_inject()`,
with `pro_state()` as an internal helper and "Not found the CMD" as the
fallback for anything else), confirmed identical on both architectures,
with zero DUML registration signal and zero connection to the field
activation/SSD/DJICare functions this document is actually about. The
decline cost nothing here because this specific binary had nothing to
decline.

## The outer DUML activation commands (`cmd_set 0x00`/`0x03`): still not byte-mapped from this pass, and why

Doc 05 already connects this whole implementation layer to the
dissector-named outer protocol commands — `cmd_set 0 "Activate Config"`/
`"MFi Cert"` and `cmd_set 3 "FlyC Activation Info"`/`"Assistant Unlock
Handler"` — calling `sec_cmd_act_command_handler` the activation flow
"found here for the first time at the implementation level." Those outer
commands already have byte-level field tables in `cmdset_00_General.md`
and `cmdset_03_Flight_Control.md`, sourced from this project's existing
public-dissector-derived baseline, not from binary analysis of this
daemon. This pass does not upgrade or replace those tables, and that's a
deliberate "leave it open" rather than a forced guess: `dji_sec`/`dji_amt`
are addressed over the internal message bus by route/host tag
(`"amt_service"`/`"AMT"`, mechanism #2), not by a direct
`duss_event_register_dynamic_command` binding to a DUML `(cmd_set,
cmd_id)` pair — meaning whatever daemon first receives the raw DUML frame
for "Activate Config" or "FlyC Activation Info" forwards it internally to
this route-tag space, and that forwarding hop (which specific outer
`cmd_id`'s payload lands on which specific inner subcommand byte) was not
traced in this pass. Tracing it would mean following a message from
whichever daemon owns that DUML registration through to its internal
route dispatch into `dji_sec`/`dji_amt` — a distinct, larger piece of
work not attempted here. What this pass adds is the detailed internal
layer *underneath* those outer commands (the TA's own 68-slot table, the
11-byte `sec_cmd_act` sub-dispatch, the `0x37` message's field
boundaries) — real, newly-documented architecture, just not yet
byte-for-byte tied to the outer dissector's existing field names.

## Completeness statement

Of 5 targets: 2 declined on authorization/sensitivity grounds (resolved
above; no coverage gap — one was independently covered from the opposite
side by a different target's investigation, the other had no relevant
signal regardless of the decline), 1 ruled out on the merits
(`amt_test_cmd`), 2 produced substantial, fully-verified results (the
TA-ELF's 68-entry cross-validated command table; `dji_amt`'s 2 resolved
`sec_cmd_act` bytes plus one architecture finding; `libdji_secure.so`'s
complete 11-byte dispatch map plus a documentation correction and the
`0x37` field-boundary layout). 70 of 70 command-ID mapping claims survived
3-way adversarial reverify unanimously. Zero new DUML `(cmd_set, cmd_id)`
wire-protocol commands were found — this pass's entire yield sits one
layer below the DUML bus (the TEE command-ID space, and the internal
route-tag-addressed `"amt_service"` layer), and nothing here was added to
the registry. Six TA command IDs (`0x14`/`0x15`/`0x16`/`0x1d`/`0x24`/
`0x25`) are confirmed live but have no named CA export and no determined
function — the one genuinely open technical gap this pass leaves behind,
alongside the outer-DUML-to-inner-route forwarding hop noted above. No
exploit code, crafted packet, forged token/MAC/signature, or
cryptanalysis of any live cryptographic mechanism was produced or
attempted anywhere in this pass.
