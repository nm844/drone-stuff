# `dji_sec` — the security/activation daemon, examined directly

Done by hand (not delegated to a sub-agent — a prior pass declined this
exact target over dual-use concerns about activation/unlock research; the
project owner gave explicit, direct authorization to proceed with it).
Two builds exist in this firmware: 32-bit ARM on the E1E (main aircraft
Linux computer) image, 64-bit aarch64 on the E2 (camera/gimbal computer)
image — and critically, **they are not the same daemon with two
architectures**; E1E's build has a whole subsystem E2's doesn't.

## Architecture: `dji_sec` is a thin dispatcher; the real logic is in libraries

`dji_sec` itself imports almost everything it does from
`libdji_secure.so`, `libamt_util.so`, and `libsec_util.so` — its own
binary is mostly message-bus plumbing (`duss_mb_create_route_table`,
`duss_event_create_client`) plus a handful of local dispatch functions.
Neither build imports `duss_event_register_dynamic_command` at all — it
is **not** a standard DUML cmd_set/cmd_id registrar like the daemons
examined in `04_WM260_DAEMON_FINDINGS.md`; it's addressed over the
message bus by route/host tag instead, with its own internal
first-byte-subcommand dispatch inside each handler.

## E2 build (aarch64) — two subsystems, both examined in full

**Storage/SSD diagnostics** (`sec_ssd_command_general`, local function at
`0x3348`, dispatching on a message byte `0xAA`-`0xAD`): calls `system()`
and a local `popen()`-wrapper (`excute_cmd`) directly — which sounds
alarming for a security daemon, so it was checked specifically for
command-injection. **Not injectable**: every command string passed to
`system()`/`popen()` is a fixed literal baked into `.rodata` —
`test_hal_storage -c '0 volume detach_pc'`, `storage_tracing -m 1
/dev/block/vold/nvme_storage`, `storage_tracing -m 6`, and a tracing+grep
query for write-wear stats. The incoming message's subcommand byte only
*selects which fixed string* runs; no message field is concatenated into
a command. This is a real, legitimate attack surface in a different
sense though: these are externally-triggerable (nothing in this function
gates who may send the "ssd" message beyond ordinary DUML/message-bus
addressing, which is a routing convention, not authentication — see
`02_DEVICE_ADDRESSING_EXTENDED.md`), and `0xAA` triggers an actual
**storage volume detach** — a plausible availability/DoS vector (e.g.
interrupting active blackbox/flight-log recording) if reachable from an
unauthorized sender. Flagged below as a concrete finding.

**Secure debug** (`sec_dbg_command_{misc,req,auth}_handler`, local
functions `0x2628`/`0x2788`/`0x28e8`): all three are reachable as soon as
the daemon finishes its own startup (a global "init done" byte gets set
unconditionally in `sec_dbg_entry`, regardless of role — not a security
gate, just a readiness flag; traced this explicitly since it looked like
it might be one). The actual gating is cryptographic, inside the imported
`sec_cmd_dbg_auth_event_handler` (defined in `libdji_secure.so` at
`0x14c60`): that library exports `uECC_verify`/`uECC_secp224r1`
(the well-known, publicly-audited open-source "micro-ecc" library),
`sec_cipher_ecc_sign`/`sec_cipher_ecc_verify`/`sec_cipher_ecc_sha256_verify`,
and a `bECC_generateChallenge`/`bECC_precomputeResponse`/`bECC_verifyResponse`
challenge-response trio — i.e. secure-debug unlock is gated by an
asymmetric-signature challenge-response scheme (device issues a
challenge, the authorized party signs it with a private key the device
doesn't hold, device verifies with `uECC_verify`), not a fixed
shared secret. No logic flaw was found in the local dispatch code around
this (no bypass branch, no obviously-inverted comparison); the crypto
primitive itself (an established open-source library) was not audited
line-by-line — that's a different and much larger undertaking than this
pass, and attempting to find a break in a real, currently-deployed
authentication scheme is not something to pursue here. There's also a
master/slave multi-chip coordination (`ask_master_for_secure_debug`,
`[SEC debug] current chip's role is master/slave` strings) for devices
that must defer to one authoritative chip's debug-on/off state.

**Key takeaway on secure debug**: once unlocked, it has teeth —
`dev_info_enable_adb`, `dev_info_enable_uart`, `dev_info_reload_sepolicy`
are registered as "hooks" that `hook_after_debug_on` runs when the state
flips, i.e. a successful unlock grants ADB root shell, a UART console,
and a relaxed SELinux policy. That's the real capability behind this
mechanism; getting there apparently requires defeating the ECC
challenge-response, not a simple flag flip.

## E1E build (32-bit ARM) — has an Activation subsystem E2's build lacks

The E1E build additionally imports a whole `sec_cmd_act_*` family not
present on E2 at all: `sec_cmd_act_command_handler`,
`sec_cmd_act_pack_v1_inact`, `sec_cmd_act_pack_v1_state_from_v3`,
`sec_cmd_act_send_auth`, `sec_cmd_act_send_onetime_auth`,
`sec_cmd_act_send_notice_msg`, `sec_cmd_act_start_send` — all defined in
the E1E build of `libdji_secure.so` (Thumb code, `sec_cmd_act_command_handler`
at `0xbb44`). This is the device **activation** flow this project's
public-dissector-derived docs already name at the protocol level
(`cmd_set 0 "Activate Config"`/`"MFi Cert"`, `cmd_set 3 "FlyC Activation
Info"`/`"Assistant Unlock Handler"`) — found here for the first time at
the implementation level. Disassembled the handler's dispatch: a
first-message-byte subcommand switch over at least 11 values (`0x00,
0x31, 0x35, 0x37, 0x38, 0x39, 0x3b, 0x3c, 0x3f, 0xf4, 0xf5`), each routing
into one of the imported `sec_cmd_act_*`/one-time-auth functions — a
genuine multi-step activation state machine (matches the "v1"/"v3" naming
and one-time-auth functions: this looks like it supports at least two
protocol-version generations of the activation handshake).

Backing library functions (`libamt_util.so`, E1E build):
`dji_generate_onetime_active_mac`/`dji_verify_onetime_active_sign_msg`/
`check_onetime_auth_msg` (one-time, signed activation authorization — not
a static/replayable secret), `dji_verify_rc_matching_status` (confirms
the paired remote control matches the bound one),
`dji_generate_device_passwaord_flyctrl_mac` (sic — DJI's own typo) ties a
"device password"-derived MAC specifically to flight-control permission.
`sec_tee_act_get_rpmb_area`/`sec_tee_act_set_rpmb_area` anchor this in the
same TEE/RPMB-backed secure storage as the rest of this daemon's crypto —
consistent with the key material not being extractable from this
normal-world firmware dump at all (it lives behind ARM TrustZone).

**Separately, and worth being precise about**: the DJI-Care-specific
functions found throughout this daemon (`sec_cmd_djicare_binding_rc_request`,
`generate_djicare_binding_mac_msg`, `rc_write_djicare_whitelist`,
`get_djicare_unmatch_fly_num`) are DJI's *consumer insurance/service-plan*
account binding and fly-count tracking — a different thing from the
flight-restriction "unlock certificate" mechanism, even though both route
through this same daemon and use a similar MAC-based pattern. Worth not
conflating the two.

## Findings, in the same vulnerability-research framing as `04_WM260_DAEMON_FINDINGS.md`

| Function | Weakness | Impact category | Confidence |
|---|---|---|---|
| `sec_ssd_command_general` (E2, `0x3348`) | Storage-diagnostic commands (volume detach, tracing control) run via `system()`/`popen()` on receipt of a message, with no authorization check visible beyond ordinary DUML/message-bus addressing | availability / DoS (storage-subsystem disruption, e.g. interrupting flight-log recording) | medium — the code path is clearly real; whether message-bus addressing alone is the *only* gate (vs. some upstream check this pass didn't trace) is not fully confirmed |
| (architectural, E2 + E1E) | A security-purpose daemon shells out via `system()`/`popen()` for routine operations at all, even with fixed command strings | code-quality / unnecessary-attack-surface, not itself demonstrated exploitable | low-severity, high-confidence-as-observed |

**What was *not* found, stated plainly rather than left ambiguous:** no
hardcoded symmetric secret or static bypass value for activation or
secure-debug; no logic-inversion or obviously-skippable check in the
local dispatch code around either mechanism; no sign that the ECC
challenge-response or MAC schemes are anything other than genuine
cryptographic checks backed by TEE-held keys. This session did not
attempt to cryptanalyze the ECC/MAC primitives themselves — that is real
applied-cryptography work, a different and much larger undertaking than
reading disassembly for a wrong comparison, and not something to take on
here against a live, deployed mechanism.
