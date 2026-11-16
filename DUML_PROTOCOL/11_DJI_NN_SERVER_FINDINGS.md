# `dji_nn_server` deep dive — E2 (aarch64) image

Full disassembly-based follow-up to the light triage pass on `bin/dji_nn_server`
(E2 `system_files`,
`/home/user/wm260_fw/decrypted/e2_extracted/system_files/bin/dji_nn_server`).
Tooling: `pyelftools` + `capstone` (`CS_ARCH_ARM64`), PT_LOAD-based
vaddr→file-offset mapping (this binary's single executable `LOAD` segment has
`p_offset == p_vaddr == 0`, so no translation is actually needed), `.rela.plt`
→ import-name resolution for every PLT stub, and a `.rela.dyn` walk to
recover the real C++ vtable for `FregService` (see §3) instead of guessing
method order from argument-count pattern-matching. No execution of the
binary; static analysis only.

**`.gnu_debugdata` confirmed present and useful**, exactly as the triage
flagged: `section.data()` + `xz -d` on the 0xa8c-byte compressed section
yields a 2,700-byte mini-ELF, `not stripped`, with a real `.symtab` (141
local+global function symbols) that names effectively every function
actually exercised in this analysis — every address below has a real name,
not a `sub_XXXXXX`, including the full C++-mangled method names that let the
Binder vtable be identified unambiguously.

## 1. Role/architecture — triage confirmed, with one real correction on how `service_id` is scoped

The triage's `purpose_guess` holds up under disassembly: this is the
`ml_proxy` NN-inference proxy daemon (source paths confirmed as literal
`__FILE__`-style strings: `hardware/dji/common/ml/ml_proxy/./src/server/
ml_binder_service.cpp`, `.../src/common/IBinder_service.cpp`,
`.../src/dspf/ml_dsp_hal_dspf.c`). Build fingerprint recovered from
`proxy_nn_service_constructor`'s own version-print call: version string
`"3.0.0"`, build date `"Dec  7 2022"` `"01:25:59"`.

**Startup sequence, confirmed from `main()` (`0xa350`) and
`proxy_nn_service_constructor` (`0x8970`):**

1. `main()` initializes ION (`osal_osa_ion_mem_dev_open`), log subsystems,
   then calls `resloveConfigParam("/vendor/model/nnf/etc/proxy_nn_cfg.json")`
   (`0x9dd8`, a `cJSON_Parse`-based reader) to populate a **global, fixed
   16-entry configuration table** (base vaddr `0x25d48`, stride `0x2f0` =
   752 bytes/entry — i.e. valid indices are `service_id` 0–15).
2. `duss_sketch_initialize()` is called against `/system/etc/dji.json` (the
   route-table file this project's `02_DEVICE_ADDRESSING_EXTENDED.md`
   already documents) — this binary participates in that generic
   sketch/bus-init step but, per §2, registers **no** DUML `cmd_set`/
   `cmd_id` commands of its own on top of it.
3. `ml_dspf_init()` (`0xa5f8`) sets up the DSP-core bitmask, local host ID,
   and the `/dev/icc_dev:apN-dspM-x.y` inter-chip-communication channel table
   the triage already found as literal strings (confirmed: 5 DSP cores,
   `dsp0`..`dsp4`, each with an AP↔DSP pair of channel names).
4. `proxy_nn_service_constructor()` then **loops `service_id` 0..15**,
   calling `getProxyNNConfig(service_id)` for each and, only where that
   slot's config was actually populated from the JSON file (non-zero "init
   output" field), calling `proxy_service_constructor(service_id)` →
   `FregService::instantiate(service_id)` (`0x8728`), which constructs a new
   `FregService` C++ object, stores `service_id` into the object itself at
   offset `0x28`, and registers it with
   `defaultServiceManager()->addService("my.IFregService", ...)`.

**The correction:** because step 4 is a loop that can call `addService()`
multiple times under the **same fixed name** `"my.IFregService"` (confirmed
as a single global `String16` built once by a static initializer,
`_GLOBAL__sub_I_IBinder_service.cpp` @ `0x5768` — there is no per-service-id
name suffixing anywhere in this binary), Android's service manager semantics
mean only the **last**-constructed enabled slot's `FregService` object stays
reachable under that name at any given time; earlier ones are superseded.
In practice this means: **exactly one `FregService` Binder object is ever
live on the IPC surface**, and *that* object's own `service_id` (the value
baked into it at construction, read back from `this+0x28` by its own
methods) is whichever slot happened to be constructed last — not something
a client chooses per call. The triage's framing ("clients supply a
service_id") is correct for the wire-level `deinit` transaction specifically
(see §4) but not for the four buffer/frame methods or `add_cfg`, which all
implicitly operate on the *object's own* `service_id`, not an
attacker-chosen one. All of these methods, however, share the **same
global 16-entry table** (`0x25d48`, stride `0x2f0`) regardless of which
object is currently "the" live Binder service — which is what makes §4
possible: `deinit` can target *any* of the 16 slots, not just the live
object's own.

**Model-loading pipeline, confirmed by full disassembly of `add_cfg` →
`cnn_proxy_service_common_init` → `encrypt_file_size`/`encrypt_file_read`:**
a client's `nn_client_cfg_t` (passed raw into `add_cfg`, see §3) carries a
NUL-terminated `model_path` string at struct offset `+8` (length-checked,
`strlen(model_path)+1 < 0x100`, i.e. ≤254 chars, logged and rejected with
result code `5` otherwise — this one check is real and present). That path
is then handed to `encrypt_file_size`/`encrypt_file_read` (`0xaaa0`/
`0xac78`), which `fopen()`s **two** candidate files —
`"<model_path>.eng.enc"` and the bare `"<model_path>"` — and uses whichever
one actually exists. The loaded bytes are then passed to
`NNFInitFromMem`/`NNFImagePreprocessInit` (`libnn_framework.so`) and from
there into the DSP pipeline (`ss_dsp_framework_init`, ION-backed shared
memory via `duss_hal_mem_alloc`/`duss_hal_attach_ion_mem`, over the
`/dev/icc_dev` channels from §1). See §6 for how `dji_fw_verify_load2mem`
fits into this — only part of it, not all of it.

## 2. `duss_event_register_dynamic_command` family / DUML `(cmd_set, cmd_id)` pairs: confirmed ABSENT — zero pairs to report

Checked the same three independent ways this project's prior `dji_cht`
deep dive (`10_DJI_CHT_CAMHAL_TEST_FINDINGS.md`) established as a
completeness check, all negative here too:

- `nm -D dji_nn_server | grep register_dynamic_command` → **no output** (the
  full dynamic symbol table — 150 imports, listed in full during this pass
  — contains no symbol from that family at all).
- `strings -n 6` over both the main binary and the decompressed
  `.gnu_debugdata` → **no output** (not referenced even as a `dlsym()`-style
  string; there is no `dlopen`/`dlsym` import either).
- The binary links `libduml_frwk.so` and `libduml_hal.so` (both `NEEDED`
  entries are present), but a full walk of `.rela.plt` shows those two
  libraries are used here **only** for `duss_sketch_initialize`,
  `duss_hal_*` (ION/device-open primitives) and `duss_osal_*`/`duss_log_*` —
  none of the three documented `duss_event_register_dynamic_command`
  variants are imported.

**Finding: `dji_nn_server` imports zero `duss_event_register_dynamic_command`-
family symbols, so there are zero `(cmd_set, cmd_id)` pairs of that specific
form to report.** (Confidence: high — completeness check over the whole
dynamic symbol table, not a sampling.) Architecturally this confirms the
triage's instinct that the real attack surface here is the Binder IPC
interface, not the DUML bus: `dji_nn_server` is a **local Android Binder
(AIDL-style) service**, full stop — it does not dispatch DUML wire commands
at all, in either direction documented elsewhere in this project.

## 3. The real Binder transaction table — `BnFregService::onTransact` fully disassembled and cross-checked against the actual C++ vtable

`BnFregService::onTransact` (`0x5d58`) dispatches on `code = w1` through a
compiler-generated jump table (at `0xb530`, 7 entries, one per
`code` 1–7) to 7 blocks, each of which reads some fixed amount of data out
of the inbound `Parcel` and then calls through the **object's own vtable**
(loaded from `this` at `[x19]`, the standard Itanium-ABI virtual-call
pattern) at a specific byte offset. Rather than inferring which method each
offset corresponds to, the actual `FregService` vtable contents were
recovered directly from `.rela.dyn` (the `R_AARCH64_RELATIVE` fixups for the
vtable's own entries, at vaddr `0x1ef00`), giving an unambiguous,
disassembly-and-relocation-confirmed mapping:

| Code | vtable+off | Real method (from `.gnu_debugdata` symtab) | What `onTransact` reads from the `Parcel` before calling it |
|---|---|---|---|
| 1 | `+0x28` | `FregService::add_cfg(nn_client_cfg_t const*, nn_info_t*)` | `Parcel::read()` **exactly 0x208 raw bytes** into a stack buffer → passed as `cfg`; a second stack buffer (0x198 bytes) is passed as the output `info`, then `Parcel::write()`'s it back to the reply whole |
| 2 | `+0x30` | `FregService::deinit(nn_service_id_e)` | `Parcel::readInt32()` — **one raw client-controlled 32-bit value**, passed straight through as the `service_id` argument |
| 3 | `+0x38` | `FregService::send_buffer_sync(void*, int)` | `Parcel::readInt32()` (compared against a hardcoded `0x468` and only *logged*, not enforced, on mismatch — see §5) then `Parcel::read()` of a fixed `0x468` bytes |
| 4 | `+0x40` | `FregService::send_buffer_async(void*, int)` | same pattern as code 3, fixed `0x468` bytes |
| 5 | `+0x58` | `FregService::reverse_comm(sp<ICallback> const&)` | `Parcel::readStrongBinder()` → `ICallback::asInterface()` |
| 6 | `+0x48` | `FregService::send_frame_sync(void*, int)` | same pattern as code 3/4 but fixed `0x240` bytes |
| 7 | `+0x50` | `FregService::send_frame_async(void*, int)` | same pattern as code 6, fixed `0x240` bytes |

`FregService::set_reverse_comm_cb(sp<ICallback> const&)` (seen in the
`.gnu_debugdata` symtab at `0x9708`) is **not** one of the 7 transaction
codes — it is called only from native code inside this process (confirmed:
no `blr` into it from `onTransact`'s dispatch region), so it is not part of
the remotely-reachable Binder surface.

This table is the complete, confirmed list of everything another local
process can ask `dji_nn_server` to do over `my.IFregService`. §4–§6 report
genuine issues found while tracing these seven paths all the way into their
real handlers.

## 4. Finding: unchecked, attacker-controlled array index in `deinit` → out-of-bounds read/write

**Weakness.** `FregService::deinit(nn_service_id_e service_id)` (`0x8f40`)
takes the raw `int32` read straight off the wire (transaction code 2, §3,
*zero validation anywhere between the Parcel and here*) and passes it
unchanged to `cnn_proxy_service_common_deinit(service_id)` (`0x7168`), which
computes the target slot as:

```
x24 = (uint64_t)(uint32_t)service_id * 0x2f0 + 0x25d48      ; umaddl x24, w19, w8, x25
...
ldr  w8, [x24]           ; OOB READ if service_id is out of [0,16)
...
str  xzr, [x20]          ; OOB WRITE a few lines later, same unchecked index
...
str  xzr, [x24]          ; another OOB WRITE
```

**There is no `cmp`/range check anywhere in `cnn_proxy_service_common_deinit`
before this arithmetic is used.** This is directly contrastable, inside the
very same binary, with the sibling function `getProxyNNConfig(int)`
(`0x7128`), which performs the *identical* slot-address computation
(`service_id * 0x2f0 + 0x25d48`, just offset by an extra `+0x30` for its
particular return convention) but is preceded by `cmp w0, #0x10; b.lt
<proceed>` — i.e. a real bound check, logging `"getProxyNNConfig service_id
exceed max limit."` and returning `NULL` when it fails. **The bound check
exists in exactly one of the three functions that perform this same
pointer arithmetic** (`getProxyNNConfig`, `cnn_proxy_service_common_init`,
`cnn_proxy_service_common_deinit`); `cnn_proxy_service_common_init` is safe
only because every call site happens to pass the object's own already-valid
`service_id` field (never a raw wire value, confirmed by walking all call
sites of `0x7308`), and `cnn_proxy_service_common_deinit` has no such luck —
its only caller, `FregService::deinit`, is wired directly to transaction
code 2's raw `Parcel::readInt32()`.

(Secondary, lower-severity note: even `getProxyNNConfig`'s check uses a
*signed* less-than comparison — `cmp w0,#0x10; b.lt` — so a negative
`service_id` would itself satisfy `< 16` and slip past that check too; this
was not found to be reachable with attacker-controlled data anywhere in
this binary, since every call site into `getProxyNNConfig` either passes a
compile-time constant 0–15, `0` or `1`, or the object's own non-negative
field — it is recorded here only because it is a second instance of the
same root-cause class of bug, dormant rather than exploitable in this
binary as built.)

**Impact category:** out-of-bounds memory read and write, reachable by any
local process able to obtain a Binder reference to `my.IFregService` and
send one `deinit` transaction with an out-of-range `service_id` (e.g.
`0x7FFFFFFF`, or a negative value, which `umaddl`'s unsigned 64-bit widening
turns into an index on the order of `service_id * 752` bytes past the
16-entry table). **Confidence: high** that the missing-bounds-check /
unsafe-index primitive itself is real — this is a direct disassembly
finding, not an inference. **Confidence is lower (medium) on the practical
ceiling of impact**: because the multiplier is a full unsigned 32-bit value
times 752, almost every out-of-range `service_id` produces an address far
outside any mapped region of the process (a crash/DoS is the straightforward
outcome), and this analysis did not go further to search for a small range
of `service_id` values that would land the read/write inside some other
*mapped, reachable, and useful-to-corrupt* structure — doing so would start
to shade into building an exploitation recipe, which is out of this
project's stated scope. Recorded here as: **a confirmed, concrete OOB
read/write primitive with a clear crash/DoS impact; corruption-of-adjacent-
heap/global-data beyond that was not demonstrated and was intentionally not
pursued.**

## 5. Finding: `Parcel::read()`/`readStrongBinder()` return status is discarded on every data-carrying transaction

Across **all five** of the data-carrying `onTransact` cases (codes 1, 3, 4,
6, 7 — i.e. `add_cfg`, `send_buffer_sync`, `send_buffer_async`,
`send_frame_sync`, `send_frame_async`), the pattern disassembled is
identical and was checked instruction-by-instruction for each of the five:

```
bl   Parcel::read      ; (or readStrongBinder for code 5, which is separate)
                        ; <-- return value in w0/x0 is NEVER inspected
ldr  x8, [x19]          ; load vtable pointer from `this`
ldr  x8, [x8, #0x28]     ; (etc. — the real handler's slot)
blr  x8                  ; call the real handler with the stack buffer,
                          ;   regardless of whether Parcel::read() actually
                          ;   succeeded in filling it
```

`android::Parcel::read(void*, size_t)` returns a negative status (and does
**not** guarantee the destination buffer was fully written) when the
`Parcel` does not actually contain as many bytes as requested — e.g. a
malformed or truncated transaction sent by a buggy or hostile local client.
Because the return value is never checked here, a short transaction causes
`add_cfg` (and the other four) to be invoked with a stack buffer that is
**partially left as whatever was already on the stack** from a prior call
in that Binder thread, rather than genuinely client-supplied data for the
unfilled tail — this includes the `model_path` field of `nn_client_cfg_t`
(struct offset `+8`, see §1), which is then `strlen()`'d, length-checked,
and potentially handed to `fopen()`/`snprintf()` as if it were trusted
input.

**Impact category:** missing input-length validation / use of
partially-uninitialized stack memory as trusted data. The most concrete,
confirmed consequence is that a short/malformed transaction is **not
rejected** the way a correctly-implemented Binder service would reject it;
whatever downstream effect that has (most plausibly a crash from passing
garbage to `fopen()`/`strlen()` on an unterminated or wild pointer-shaped
byte sequence, or — more speculatively — operating on stale data left over
from a previous Binder call that happened to reuse the same stack slot) was
not traced further than confirming the missing check itself. **Confidence:
high** for the code pattern (five independent, identically-shaped
confirmations); **confidence: low/not-determined** on what the realistic
worst-case consequence actually is, which was not pursued further per this
project's scope boundary.

## 6. Finding: `dji_fw_verify_load2mem` load-verification is applied to only one of the two file-path variants `encrypt_file_read` will accept

This directly extends the triage's flagged keyword hit. Full disassembly of
`encrypt_file_read` (`0xac78`) shows it tries **two** candidate files for a
given client-supplied `model_path`, in a fixed order baked into the
function itself:

1. The bare path, `fopen(model_path, "rb")`.
2. `model_path` with a literal `".eng.enc"` suffix appended (built via an
   internal `snprintf(buf, 0x100, "%s%s", model_path, ".eng.enc")` helper),
   `fopen(<that>, "rb")`.

Whichever one of the two actually exists on disk is the one used (confirmed
via an `fopen`-success `xor` check immediately after both attempts — exactly
one of the two is expected to exist). **The two branches are not
symmetric**: tracing both all the way to their end —

- The **bare-path branch** (reached when only the plain `model_path` file
  exists): `fseek`/`ftell` to get size, size-checked against a caller-
  supplied maximum, `fread()` into the output buffer, `fclose()`, and
  **returns success immediately — `dji_fw_verify_load2mem` is never called
  on this branch.**
- The **`.eng.enc`-suffixed branch** (reached when that sibling file
  exists): the same `fseek`/`ftell`/size-check/`fread()`/`fclose()`
  sequence, but is followed by exactly one call,
  `dji_fw_verify_load2mem(buf, size, ctx, &result)` (`0xae40`), whose
  nonzero-result path logs an error and fails the load; its zero-result
  path is what lets the read bytes actually reach the caller
  (`cnn_proxy_service_common_init`) as a validated model image.

So **the firmware/model-load verification step the triage flagged exists and
is real, but it is reached only through the filename convention
`<model_path>.eng.enc`.** A request whose `model_path` resolves to a file
that exists only under its bare name (no `.eng.enc` sibling present) is
read and handed to `NNFInitFromMem`/the DSP pipeline (§1) with **no call to
`dji_fw_verify_load2mem` at all** — confirmed by exhaustively tracing both
control-flow paths of the function to their respective `ret`s.

**Impact category:** load-integrity-gate bypass by file-naming choice,
*if* the bare-path branch is reachable with an attacker/client-influenced
`model_path` in a real deployment. **Confidence: high** on the control-flow
fact itself (both branches were fully disassembled to their returns).
**Not determined, and intentionally not pursued:** whether this bare-path
branch is actually reachable in this image's real-world configuration (e.g.
whether every model this device's `/vendor/model/nnf/etc/proxy_nn_cfg.json`
and filesystem actually ship always have a paired `.eng.enc` file such that
the bare-path branch is dead in practice; whether `model_path` can be
pointed somewhere outside the expected `/vendor/model/nnf/...` tree at all —
no path-prefix allow-list was found anywhere in this binary, but this
analysis stopped at that observation rather than trying to characterize or
defeat filesystem/SELinux-level restrictions that may sit outside this one
file). Per this project's scope boundary (as applied already to `dji_sec`
and the NFZ database), this finding **stops at identifying that the
verification gate is conditional and describing exactly which code path
skips it** — no attempt was made to determine whether the gate, where it
does run, could itself be defeated (that would mean touching
`dji_fw_verify_load2mem`'s actual cryptographic/signature logic, which lives
in a different library and is explicitly out of scope).

## 7. Observation: no caller-identity check anywhere in this binary

`BnFregService::onTransact` performs no `IPCThreadState::getCallingUid()`/
`getCallingPid()`-style check before dispatching any of the 7 transactions
(confirmed: neither symbol is imported by this binary at all — see the full
`.dynsym` import list gathered for this pass). Whatever restricts which
local processes may actually obtain a Binder handle to `my.IFregService`
(SELinux `service_manager` contexts, Android permission labels, etc.) is
therefore enforced entirely **outside** this file, by the platform/`init`/
SEPolicy configuration on the device — this was not located or evaluated as
part of this pass (it is not contained in this ELF). Recorded as an
architectural note rather than a scored finding: every one of §4–§6's issues
is reachable by *whatever* process set the platform policy allows to bind
this service, and that allowed set was not determined here.

## Scope note

Consistent with this project's established boundary for `dji_sec`
(`05_DJI_SEC_FINDINGS.md`) and the NFZ database (`06_NFZ_DATABASE_FINDINGS.md`):
this pass identified and fully traced the `dji_fw_verify_load2mem` call site
and the conditions under which it is and is not invoked (§6), but made **no
attempt** to characterize, weaken, or bypass the verification function's own
cryptographic logic (that function is exported from a different library, not
disassembled here). Likewise, §4's out-of-bounds primitive is reported as
"a confirmed OOB read/write exists, crash/DoS is the demonstrated ceiling" —
no attempt was made to search for a `service_id` value that would turn it
into a targeted corruption of a specific, useful structure, which would
start to constitute an exploitation recipe. No crafted Binder transactions
were actually sent to this (or any) binary; everything above is a static
disassembly finding.

## `not_determined`

- Whether `encrypt_file_read`'s bare-path (no-`.eng.enc`, no-verification)
  branch is reachable with any real `model_path` value in this device's
  actual shipped configuration — this binary alone does not show what files
  really exist on a live unit's `/vendor/model/nnf/` tree.
- The realistic worst-case impact of the `deinit` OOB read/write beyond
  "crash is clearly achievable, controlled corruption of a specific target
  was not demonstrated and not pursued" (§4).
- What SELinux/`service_manager` policy, if any, restricts which local
  processes may bind `my.IFregService` — not contained in this file (§7).
- The complete field-by-field layout of `nn_client_cfg_t` (0x208 bytes) and
  `nn_info_t` (0x198 bytes) beyond the fields actually exercised in the
  disassembled paths (`model_path` at `+8`, a length field at `+4`, a byte
  flag at `+0x108`); the remaining ~500 bytes of `nn_client_cfg_t` were not
  individually mapped.
- Whether any other local daemon on this image (outside `dji_nn_server`
  itself) is the actual client that normally calls `my.IFregService` — this
  pass covered only the server side.
