# The 4 OP-TEE Trusted Applications (`/ta/*.ta`) — decrypted, UUID-mapped, and tied into `dji_sec`/NFZ

One of the 39 agents in the "keep going deeper" sweep (see
`12_WM260_EXHAUSTIVE_BINARY_SWEEP_FINDINGS.md` for the sweep as a whole) was
pointed at the four previously-unopened files on the E1E `vendor.img` at
`/ta/*.ta`. This is the single most architecturally significant new result
from that sweep: it decrypts DJI's outer distribution wrapper around all
four files, confirms the inner payload is a standard OP-TEE signed
Trusted-Application image, and — without touching the TEE's own
cryptography — maps each TA's UUID to a concrete purpose by finding it
hard-coded in a small, single-purpose "Client Application" (CA) library
that links `libteec.so` and is itself linked by `dji_sec`'s dependency
chain. This closes several open loops in `05_DJI_SEC_FINDINGS.md` and
`06_NFZ_DATABASE_FINDINGS.md` and adds one previously-undocumented file
(`/nfz_data/nfz_tfr.bin`).

**Scope boundary, stated up front and preserved exactly throughout this
document:** this pass did **not** attempt to verify or break the OP-TEE
image's own RSA-2048 signature; did **not** attempt any key extraction or
cryptanalysis against the RPMB-backed secrets these TAs manage (activation
MACs, secure-debug/SSD keys, DJICare keys, the device's PKCS#12 identity
certificate, ADS-B AES-CCM keys); and did **not** reverse the
`TEEC_InvokeCommand` command-ID dispatch tables inside the CA libraries for
the activation/AMT TA specifically (doing so would mean mapping exactly how
to drive the activation/SSD state machine, which is the one piece of this
investigation the task was explicit about not pursuing further). Everything
below comes from exported symbol names and literal log/panic/error strings
the binaries print about themselves, not from exercising or reversing any
protected operation.

## Extraction and container format

All four files were pulled off the E1E `vendor.img` with the same
`debugfs`-based technique used throughout this project
(`debugfs -R "dump /ta/<file> ..." vendor.img`); all four extracted sizes
matched the inode size exactly.

**Layer 1 — DJI's standard `IM*H` distribution wrapper.** Each raw `.ta`
file opens with the same `"IM*H"` magic this project has already documented
on every other firmware module (`01_BINARY_ANALYSIS_FINDINGS.md`): header
version 2, a 224-byte header, auth-key fourcc `"PRAK"`, enc-key fourcc
`"TBIE"`, container type `"TZTA"`, module name `"djita"`. The whole file
measures ~7.9–8.0 bits/byte entropy at this layer — genuinely encrypted, no
ELF magic visible in the raw dump.

This is **not** the TEE/RPMB-backed secret this project's scope boundary
protects — it is DJI's generic firmware-distribution wrapper, the same one
this project has already decrypted for other modules (the `00_cfg`, `0105`
LCPU, and `0500` PD_MCU modules) using the already-published, community
`dji_imah_fwsig` un-signing tool (found on this machine at
`/home/user/nimrasol_wm260/tools/dji_imah_fwsig_latest.py`, a separate
open-source "dji-firmware-tools"-derived checkout — not something written
for this task). This pass used the **same tool** on these four files,
continuing that established precedent rather than opening new territory:
brute-forcing only the small set of same-fourcc keys the tool already
ships (not deriving or guessing any new secret), the already-known working
pair **auth=`PRAK-2020-01` / enc=`TBIE-2020-02`** decrypted all four files
cleanly. Correctness was confirmed independently of the tool's own
pass/fail flag two ways: the RSA header-signature check inside the tool
passed, and — more convincingly — the decrypted body starts with OP-TEE's
own standard `"HSTO"` shdr magic, and each embedded TA's internal UUID field
matches its own filename exactly.

**Layer 2 — standard OP-TEE signed-TA image**, exactly as expected for a
genuine OP-TEE deployment: a 20-byte `shdr` (magic `"HSTO"`, `img_type=0`,
`img_size`, `algo=0x70004830` = `TEE_ALG_RSASSA_PKCS1_V1_5_SHA256`,
`hash_size=32`, `sig_size=256`), then a 32-byte SHA-256 hash, then a
256-byte RSA-2048 signature (DJI's own TA-signing key — left untouched, not
verified or attacked), then the ELF payload starting at a fixed file offset
of 308 bytes in all four files. Each extracted ELF's own `.ta_head` section
(`TEE_UUID` + `stack_size` + `flags`) was decoded and its UUID matches the
containing file's UUID byte-for-byte in all four cases — a strong
self-consistency check that the un-signing tool's output is correct.

All four embedded ELFs are ELF32/`EM_ARM`, EABI5, ARMv7-A ("Cortex-A7" build
tag), Thumb-2, `ET_DYN` (PIE), with **zero** `NEEDED` libraries — standard
statically-linked OP-TEE user-mode TAs. None carry `.gnu_debugdata` or
`.symtab` (genuinely stripped down to a small `.dynsym`), but all four carry
a rich set of self-documenting panic/log/assert strings in `.rodata` that
did almost all of the identification work below.

## UUID-to-purpose mapping method

The primary deliverable of this pass: for each of the four UUIDs, a search
across every file under `e1e_extracted/system_files` (in five forms —
dashed ASCII, no-dash ASCII, bare-filename ASCII, the little/mixed-endian
16-byte `TEEC_UUID` binary form actually used in memory, and the
big-endian 16-byte form as a fallback) found **exactly one hit per UUID**,
each in a distinct, small CA (TEE Client Application) library under
`system_files/lib`. Each library embeds the UUID as a literal 16-byte
struct and links directly against `libteec.so` — the standard
GlobalPlatform TEE Client API (`TEEC_OpenSession`/`TEEC_InvokeCommand`/etc.).

**Architecture finding in its own right:** none of the four UUID literals
appear directly inside `libdji_secure.so`, `dji_sec`, `dji_amt`, or
`tee-supplicant` — the higher daemons and libraries this project has
already examined call through these four thin, single-purpose CA wrapper
libraries rather than opening TEE sessions themselves. This adds a concrete
layer to `05_DJI_SEC_FINDINGS.md`'s picture:

```
dji_sec -> libdji_secure.so -> libamt_util.so -> TEEC_OpenSession/InvokeCommand -> TA (in TrustZone)
```

not `dji_sec -> TEE` directly. Each CA library's exported function names
line up almost 1:1 with its matching TA's internal log strings/symbols,
giving high confidence in all four mappings.

Two of the four TAs' build-time `gp.ta.description` property is the literal
placeholder string `"EKCST TA"` on **both** `ad09a153` (ADS-B) and
`e91c9402` (activation/AMT) — identical text on two functionally unrelated
TAs, so this reads as an un-customized SDK/template default rather than a
meaningful name. The other two (`"FW UTIL TA"`, `"NFZ UTIL TA"`) have
distinct, apparently real descriptive names.

## The four TAs

### `09db16c0-873b-4fed-b87e-a5d2b86293a2` — Firmware-verify TA (`"FW UTIL TA"`)

153,472 bytes. Maps to `/lib/libfw_util_ca.so` (sole UUID hit), whose
exports (`fw_util_load`, `fw_util_verify`,
`fw_util_verify_init/update/final`, `fw_util_verify_load2ion`) appear
almost verbatim as the TA's own internal function-name strings
(`fw_util_verify`, `dji_fw_verify_init/update/final`, `fw_image_verify`,
`fw_image_load`, `fw_image_verify_load2ion`), plus detail strings
(`image_verify_header/digest/checksum/payload`, `image_decrypt_payload`,
`antirollback`, `keyrepo_read_pack_version`, `'header auth_alg(%d) and the
signature size(%d) are not matching'`) that match the exact field names of
the `IM*H` container header already documented in
`01_BINARY_ANALYSIS_FINDINGS.md`.

**Purpose, high confidence:** the in-TEE half of DJI's firmware-update
authenticity check — validates an incoming module's header/digest/checksum
and signature, enforces anti-rollback via an RPMB-backed "key repo anti
version", and decrypts/loads the verified payload (including an
ION-buffer path) for the normal world to flash. This is the hardware-anchored
trust root behind the `IM*H` container format used on every module in this
firmware package, and is the TA that `libdji_fw_verify_util.so`/
`libfw_util_ca.so` (deep-dived in `12_...FINDINGS.md`) ultimately talks to.

### `789463d1-d97d-4e90-a2f6-039376e92644` — NFZ/FlySafe TA (`"NFZ UTIL TA"`)

185,056 bytes. Maps to `/lib/libnfz_util_ca.so` (sole UUID hit), whose
exports (`nfz_unlock_api_handle`, `get_nfz_data_for_goggles_from_ta`,
`nfz_goggles_comm_ta`, `read_nfzdb`, `trigger_ta_*`, `sec_icc_cmd`/
`open_sec_icc`/`close_sec_icc`) match this TA's own internal strings/symbols
(`fs_api_push_goggles_nfz_data/status`, `fs_api_req_license_list`,
`fs_api_update_unlock_license`, `dji_flysafe_v3_License*_fields` nanopb
protobuf tables, `nfz_bin_init`/`fs_nfzbin_read`,
`flysafe_icc_dev_open/close`) almost one-to-one.

**Purpose, high confidence:** a TEE-backed No-Fly-Zone/geofence-unlock
TA that reads/manages the aircraft's NFZ database files, tracks per-license
unlock state (`SELF_UNLOCK`, `UNLOCK_IN_WL`, `UNLOCK_SIM_IN_WL`,
`FS_UNLOCK_NO_WL`), does country-based restriction logic
(`fs_country_task`, `'cloud ctrl country id/limit'`), and pushes signed
NFZ status/data to DJI FPV goggles over a dedicated secure channel
(`flysafe_icc_dev_open/close`, and — notably — a literal
`'goggles sign result is nooooot correct'` [DJI's own typo] string implying
a signature check on data sent to the goggles).

**Extends `06_NFZ_DATABASE_FINDINGS.md`:** the strings confirm the exact
path `/nfz_data/NFZ/nfz.bin` that document already profiled, **and** a
second file, `/nfz_data/nfz_tfr.bin`, not previously noted anywhere in this
project. Its contents were not examined in this pass (reading the raw
`nfz.bin` format is already documented as deliberately not pushed to a
byte-exact parser in `06_...`; `nfz_tfr.bin`'s format was not touched at
all — flagged as a lead, not a finding).

### `ad09a153-f7b6-4dea-8d30-34d070d0dc73` — ADS-B crypto TA (`"EKCST TA"`)

79,616 bytes, smallest of the four. Maps to `/lib/libadsb_util.so` (sole
UUID hit), whose exports (`dji_aes_ccm_auth_decypt` [sic],
`dji_aes_ccm_auth_multi_package_dec`, `dji_aes_ccm_encrypt_and_tag`,
`dji_aes_ccm_init`, `dji_aes_ccm_setkey`) correspond directly to this TA's
own exports (`adsb_ae_encrypt`, `adsb_ae_decrypt`, `adsb_ae_decrypt_multi`,
`aes_ccm_decrypt`, `generate_cmac`).

**Purpose, medium confidence:** a small, dedicated AES-CCM
authenticated-encryption/decryption + CMAC service for the ADS-B subsystem
(this project's own DUML `cmd_set 0x11`, currently 11 known cmd_ids and 0
decoded — see `cmdset_11_ADSB.md`). No ADS-B *protocol* logic is visible in
its strings, only generic bigint/crypto runtime plus these named crypto
entry points and a `TEE_CryptoCell_KeyDerivation` reference (suggesting use
of an ARM TrustZone CryptoCell hardware crypto IP key-derivation path) — so
this most plausibly authenticates/decrypts ADS-B feed data (or protects
outgoing broadcast data) rather than implementing ADS-B parsing itself.
Exactly which DUML `cmd_set 0x11` cmd_id(s) route to which of this TA's
functions was **not determined** — that would need disassembling the CA
library's `TEEC_InvokeCommand` call sites, not attempted (see scope
boundary).

Note: this is a **different**, separate ADS-B crypto path from the one
documented in `07_ADSB_SOC_FINDINGS.md` (the `/adsb/adsb_soc.img` MCU
firmware image, encrypted under a different `TBIE` key-family tag). The two
findings are architecturally related (both ADS-B, both DJI's `IM*H`-family
encryption heritage) but are not shown to be the same mechanism — this TA
services whatever reaches it via normal-world `TEEC_InvokeCommand` calls;
`adsb_soc.img` is a standalone encrypted MCU image on the vendor partition.

### `e91c9402-64a0-470f-88e7-bf5d3c606b6a` — Activation/AMT/secure-debug TA (`"EKCST TA"`)

171,200 bytes. Maps to `/lib/libamt_util.so` (sole UUID hit) — the same
library `05_DJI_SEC_FINDINGS.md` already names as `dji_sec`'s backend.
`libamt_util.so`'s ~45 exports (`dji_active_rpmb_get/set`,
`dji_ssd_bind/verify/get_challenge/get_status/unbind`,
`dji_generate_active_mac`, `dji_generate_onetime_active_mac`,
`dji_verify_onetime_active_sign_msg`, `dji_device_bind_*`, `djicare_*`,
`dji_keyrepo_*`, `dec_calibration_file`, `enc_fc_dtcm`, `https_client_sign`,
`https_check_private_key`, `pkcs12_parse`, `cloud_get_device_secret`,
`amt_get_derive_adsb_key`, `amt_get_derive_log_key`) match this TA's
internal strings/symbols virtually one-to-one — the same function names
appear as literal strings inside the TA binary itself (e.g.
`dji_generate_active_mac_msg`, `ssd_bind`, `ssd_verify`,
`decrypt_ssd_root_key`, `djicare_write_whitelist`,
`PKCS12_get_key_and_certs`, `d2i_PKCS12`, and BoringSSL-derived
`pkcs8/bytestring/cbs.c`/`pkcs8/pkcs8.c` source-path strings). This is also
the **only** one of the four UUIDs that appears alongside explicit
`TEE_RPMB_*` API usage (`TEE_RPMB_Get_EMMC_Size`/`Read`/`Write`/
`KeyInject`), tying it directly to the RPMB-area functions
`05_DJI_SEC_FINDINGS.md` already named from the normal-world side.

**Purpose, high confidence — by far the broadest and most security-critical
of the four:** this is the central activation / secure-debug /
device-binding / key-repository TA behind DJI's "AMT" (Active Management
Tool) subsystem, backing inside the TEE/RPMB hardware root of trust:

1. **Device activation** — `dji_generate/verify_active_mac_msg`,
   `dji_generate_onetime_active_mac_msg`, `check_onetime_auth_msg`/
   `check_whitelist_auth_msg`.
2. **"SSD" secure software/system debug unlock** — `ssd_bind`/`ssd_verify`/
   `ssd_get_challenge`/`ssd_derive_key`/`decrypt_ssd_root_key`. This is the
   TEE-side implementation of the ECC challenge-response secure-debug
   mechanism `05_DJI_SEC_FINDINGS.md` already documented from the
   normal-world (`libdji_secure.so`) side — now confirmed to actually
   execute here, with RPMB as its persistent store (`sec_tee_act_get_rpmb_
   area`/`set` map directly onto this TA's `active_rpmb_get`/`active_rpmb_set`).
3. **DJICare insurance account binding/whitelist/blacklist** —
   `djicare_write_whitelist`, `djicare_verify_msg`,
   `djicare_handle_uav_in_blacklist`, `dji_get_djicare_whitelist`/
   `unmatch_fly_num` — matching `05_...`'s findings exactly.
4. **An RPMB-backed "key repository" with anti-rollback versioning** —
   `dji_keyrepo_read_key`/`update_pack`/`read_pack_version`, `'antirollback'`.
5. **Calibration-file and flight-controller-DTCM encryption/decryption** —
   `dec_calibration_file`, `enc_fc_dtcm` — i.e. this TA also gates access
   to sensor-calibration data and flight-controller working memory.
6. **Mutual-TLS client authentication to DJI's cloud** using a per-device
   PKCS#12 certificate bundle parsed inside the TEE (`pkcs12_parse`/
   `PKCS12_get_key_and_certs`/`https_client_sign`/`https_check_private_key`,
   with `'pkcs12_parse couldn't find BoardSN'` tying the certificate to a
   specific board serial number) plus `cloud_get_device_secret`.

This is the single TA that most directly matches and extends
`05_DJI_SEC_FINDINGS.md`'s description of `dji_sec`/`libdji_secure.so`'s
TEE/RPMB-backed activation and secure-debug crypto — it closes that
document's open question of whether the ECC challenge-response/MAC schemes
are "genuine cryptographic checks backed by TEE-held keys" (yes, confirmed:
this is where they actually execute).

## What this does and does not resolve

**Resolved / newly confirmed:** the existence and real execution location
of the activation/secure-debug/DJICare mechanisms `05_DJI_SEC_FINDINGS.md`
inferred from `libdji_secure.so`'s imports; the concrete `dji_sec ->
libdji_secure.so -> libamt_util.so -> TEEC_* -> TA` call chain; a TEE-backed
NFZ/FlySafe TA and a previously-unknown second NFZ-adjacent file
(`nfz_tfr.bin`); a plausible (medium-confidence) TEE-backed crypto service
for ADS-B.

**Explicitly not resolved, by design:** whether any of these mechanisms can
be defeated. No attempt was made to verify or break the OP-TEE RSA-2048
image signature; no key extraction or cryptanalysis was attempted against
any RPMB-backed secret (activation MACs, SSD/secure-debug keys, DJICare
keys, the PKCS#12 device certificate, ADS-B AES-CCM keys); and the
`TEEC_InvokeCommand` command-ID dispatch tables inside the four CA
libraries — which would map exactly which numeric command drives which TA
operation, and in particular how the activation/AMT TA's SSD state machine
is driven — were **not** disassembled. That last piece in particular was
judged to cross from "document the architecture" into "map how to drive
the activation/unlock state machine," which this project continues to
treat as out of scope absent explicit, separate authorization (consistent
with how `dji_sec` itself was handled in `05_DJI_SEC_FINDINGS.md`).

## Update: 3 of the 4 CA libraries' command-ID tables now mapped, see `14_FOLLOWUP_DEEPDIVE_FINDINGS.md` Track F

A follow-up pass disassembled `libfw_util_ca.so`, `libnfz_util_ca.so`, and
`libadsb_util.so`'s own `TEEC_InvokeCommand` call sites and recovered the
literal command-ID each exported wrapper function passes to its TA — a
clean sequential `0`-`5` map for the Firmware-Verify TA, a clean sequential
`0x11`-`0x14` map for the ADS-B crypto TA, and (for the NFZ TA) confirmation
that its two generic exported dispatcher functions forward their own
caller's first argument directly into `TEEC_InvokeCommand` with no local
range check (an architecture/missing-local-authz observation, not a
demonstrated bypass — whether the TA itself validates server-side wasn't
examined). **`libamt_util.so` (this document's `e91c9402...` activation/
secure-debug/DJICare TA) was explicitly excluded from that follow-up pass
and was never opened, disassembled, or searched for command IDs** — the
exclusion stated below remains fully in force and was independently
confirmed honored.

## Findings

| Observation | Weakness/property | Impact category | Confidence |
|---|---|---|---|
| All four `/ta/*.ta` files decrypt cleanly under the already-published `dji_imah_fwsig` tool and this project's already-known `PRAK-2020-01`/`TBIE-2020-02` key pair, revealing standard OP-TEE `HSTO`-signed TA images | The outer DJI distribution wrapper around these TEE binaries uses the same key family as other already-decrypted modules in this package — not a new weakness, just confirmation this layer offers no additional protection beyond what's already documented | N/A — container-format confirmation, not a vulnerability (the inner OP-TEE RSA-2048 TA signature is the real protection layer and was not touched) | high |
| None of the 4 TA UUIDs appear directly in `dji_sec`/`libdji_secure.so`/`dji_amt`/`tee-supplicant`; each is reached only through a small, dedicated CA library | Confirms a concrete `dji_sec -> libdji_secure.so -> libamt_util.so -> TEEC_* -> TA` architecture, extending `05_DJI_SEC_FINDINGS.md` | N/A — architecture documentation | high |
| `e91c9402`'s TA backs activation, SSD/secure-debug unlock, DJICare binding, an RPMB key repository, calibration/DTCM encryption, and cloud mTLS — all inside the TEE, all RPMB-anchored | Confirms (does not weaken) that these are genuine hardware-rooted cryptographic checks, closing `05_...`'s open question about whether the crypto is "real" | N/A — confirms existing protection is real, not a new weakness | high |
| `789463d1`'s TA manages a second, previously-undocumented file `/nfz_data/nfz_tfr.bin` alongside the already-profiled `nfz.bin` | New file surface identified; its format/contents were not examined | N/A — scope/documentation note for a future pass | high confidence the file reference exists in the TA's strings; format entirely unexamined |
| `ad09a153`'s and `e91c9402`'s TAs share the identical placeholder `gp.ta.description` string `"EKCST TA"` | Build/packaging hygiene observation (uncustomized SDK template default on two unrelated TAs) — not a security weakness | N/A | medium (plausible explanation, not confirmed against DJI's own build tooling) |

**What wasn't pursued, stated plainly:** OP-TEE image-signature
verification/bypass; any key extraction or cryptanalysis against
RPMB-backed secrets; disassembly of the `TEEC_InvokeCommand` command-ID
tables inside any of the four CA libraries (`libfw_util_ca.so`,
`libnfz_util_ca.so`, `libadsb_util.so`, `libamt_util.so`); and, in
particular, mapping the activation/AMT TA's SSD/secure-debug state-machine
command IDs. Each would be a reasonable, separately-scoped next step for a
future pass with explicit authorization, mirroring how this project has
already handled `dji_sec` itself.
