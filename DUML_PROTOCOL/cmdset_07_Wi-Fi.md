# Cmd Set 0x07 — Wi-Fi

Total known command IDs: 64

## 0x00 — WiFi Reserved

_Not decoded._ Reserved/unused cmd_id; not expected to appear on the wire with a real payload. Confirmed no meaningful payload. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x01 — WiFi Ap Scan Results Push

_Not decoded._ Searched the complete enumerated function-name list of dji_network/E2 (~60 wms_evt_*/v1_proc_* names, extracted via `strings` and cross-checked against the binary's own __func__ self-logging) - no scan_result/scan_push-named function exists. The only related artifact found is a literal path string '/tmp/scan_res' (vaddr 0x18913) surrounded by 'iw scan'-style parsing fragments (' freq: %d', ' signal: %d', ' * station count: %d', ' * channel utilisation:'), i.e. real evidence that dji_network/E2 DOES run and parse a Wi-Fi scan and stage results in a temp file, but no DUML payload-encoding function for that result set could be located or disassembled - the string reference itself could not be resolved to a specific function body within budget. dji_network/E1E's net_wifi*.c also contains generic 'ath_scan'-prefixed strings but nothing naming a push/result-encode function either. Given this is a device->app PUSH (one-way), it would plausibly be built by whatever function assembles the scan-result list into the wire frame, which I was not able to isolate. Reporting insufficient_evidence rather than guessing a layout for a variable-length, multi-record structure with no observed encoder. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x02 — WiFi Ap Channel SNR Get

_Not decoded._ dji_network/E1E (the net_wifi*.c codebase, NOT the E2 'wms' codebase) contains a full SNR/noise subsystem by name: net_evt_req_channel_noise (0x1eea0), net_push_snr (0x1f138), get_single_chan_noise (0x1f5e0), net_start_snr_timer (0x1ef78), net_suspend_snr_timer (0x1efe8), plus loose strings 'starting snr pushing thread as request', 'w_ctrl snr push cmd: %s', 'w_ctrl: pushing SNR to APP: %u bytes', 'w_ctrl_ch: freq %d, noise %d' - net_evt_req_channel_noise in particular is an extremely strong name match for an inbound 'request channel noise/SNR' handler. However, I could NOT resolve these strings' containing function bodies: ARM32/Thumb2 -fpic string references use a 'ldr rD,[pc,#imm]; add rD,pc' PC-relative idiom with no R_ARM_RELATIVE relocation on the literal (same as the aarch64 adrp+add idiom, but harder to scan correctly), and both (a) a custom capstone-based simulator I wrote for that idiom and (b) a direct `arm-linux-gnueabi-objdump -d` disassembly (which annotates literal-pool PC-relative loads with their resolved target in a comment, as verified against known-good PLT entries in the same binary) found zero references to any of these 5 string addresses anywhere in .text - the same 'orphaned string' phenomenon documented for the E2 wms_evt_*/v1_proc_* functions in shared_infrastructure_found, but here I additionally could not even get as far as identifying which bytes constitute the function body (unlike the E2 cases, where I did fully disassemble the handler bodies via other, successfully-resolved xrefs). Given the task's explicit instruction not to invent a layout without real evidence, and genuinely not having located the function body (only its name), this is reported as insufficient_evidence rather than a guessed single-byte-enum SNR-get payload. This is a concrete, named lead for a future pass with more ARM32-PIC tooling budget. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x03 — WiFi Ap Channel Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: inner handler at vaddr 0xfae8 (self-logs as __func__ 'v1_proc_set_chan' at 0xfb14/0xfb8c), called via direct `bl` from a per-command wrapper at vaddr 0x7010`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 2 | `wifi_ap_set_channel_channel` (Channel) | uint16 | Target Wi-Fi channel number, little-endian. Handler only checks value < 256 (0x100) at this layer; a deeper call (vaddr 0xb080, not further traced) presumably validates against the real regulatory/band channel list. |

**Worked example:**

- Request payload: `2400`
  Pilot selects 5 GHz channel 36 for the aircraft's Wi-Fi AP in the app's network settings. Payload = uint16 LE 36 (0x0024) -> bytes 24 00. (cmd_set=0x07, cmd_id=0x03 would precede this in the full DUML frame.)
- Response payload: `00`
  1-byte ack payload: result code 0x00 = success. (A rejected length or channel value instead yields 0xFF.)

## 0x04 — WiFi Ap Channel Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: inner handler at vaddr 0xfc10 (self-logs as __func__ 'v1_proc_get_chan' at 0xfc60/0xfc98), called via direct `bl` from a per-command wrapper at vaddr 0x71f8`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_get_channel_status` (Status) | uint8 | Always 0x00 on this code path; no error branch was observed in the disassembled handler. |
  | 1 | 1 | `wifi_ap_get_channel_channel` (Channel) | uint8 | Current configured Wi-Fi channel number. |

**Worked example:**

- Request payload: ``
  Empty payload (pure GET, no input fields read by the handler).
- Response payload: `0024`
  status=0x00 (success), channel=0x24 (36) - the app querying the channel it was told was set in the 0x03 example above.

## 0x05 — WiFi Ap Tx Pwr Set

_Not decoded._ Checked the complete enumerated v1_proc_*/wms_evt_* function-name list in dji_network/E2 (the module that cleanly implements set_chan/get_chan/set_ssid/get_ssid/get_rssi/set_band/set_country/etc. for this cmd_set) - no tx-power/txpwr/tx_pwr/power-level-named set function exists anywhere in that list. Also grepped dji_network/E1E (net_wifi*.c codebase) for 'txpwr'/'tx_pwr'/'tx_power'/'get_power'/'set_power' - no match. Not ruling out that the aircraft's actual Wi-Fi tx-power control lives in a third binary not yet identified for this cmd_set (e.g. a radio-calibration-specific daemon), but within this pass's scope (dji_network, the only binary found exposing a Wi-Fi-AP-management-shaped DUML-adjacent API for this cmd_set) nothing matched. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x06 — WiFi Ap Tx Pwr Get

_Not decoded._ Same exhaustive name-list check as 0x05 (Tx Pwr Set) - no tx-power-get-named function found in either dji_network build. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x07 — WiFi Ap SSID Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: inner handler at vaddr 0xf148 (self-logged by its own wrapper chain as 'wms_evt_get_ssid'), called via direct `bl` from a per-command wrapper starting at vaddr 0x56e0-ish (confirmed call site 0x573c -> bl #0xf148)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_get_ssid_status` (Status) | uint8 | Always 0x00 on this code path (no error branch observed). |
  | 1 | 1 | `wifi_ap_get_ssid_len` (SSID Length) | uint8 | Length N of the SSID string that follows. |
  | 2 | -1 | `wifi_ap_get_ssid_ssid` (SSID) | string | N raw ASCII bytes (length given by the preceding field), not separately null-terminated on the wire. |

**Worked example:**

- Request payload: ``
  Empty payload (pure GET).
- Response payload: `000d4d61766963332d413142324333`
  status=0x00, len=0x0D (13), SSID='Mavic3-A1B2C3' (ASCII 4D 61 76 69 63 33 2D 41 31 42 32 43 33) - app refreshing the network-info panel after connecting.

## 0x08 — WiFi Ap SSID Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: inner handler at vaddr 0xf1f8 (self-logs as __func__ 'v1_proc_set_ssid' at 0xf22c/0xf288/0xf300/0xf368), called via direct `bl` from a per-command wrapper starting at vaddr 0x59cc (confirmed call site 0x5a90 -> bl #0xf1f8)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_set_ssid_len` (SSID Length) | uint8 | Length N of the SSID that follows; must satisfy 1<=N<=32, and total payload length must equal N+1 or the request is rejected. |
  | 1 | -1 | `wifi_ap_set_ssid_ssid` (SSID) | string | N raw ASCII bytes of the new SSID (length given by the preceding field). |

**Worked example:**

- Request payload: `0d4d61766963332d413142324333`
  User renames the aircraft's Wi-Fi AP SSID to 'Mavic3-A1B2C3' from the app's network settings page. len=0x0D (13) + ASCII 'Mavic3-A1B2C3' (4D 61 76 69 63 33 2D 41 31 42 32 43 33), total payload 14 bytes.
- Response payload: `00`
  1-byte ack: 0x00 = success (0xFF on a length/validation/apply failure).

## 0x09 — WiFi Ap RSSI Push

Payload decoder: `wifi_ap_push_rssi_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_push_rssi_signal` (Signal) | uint8 |  |

## 0x0A — WiFi Ap Ant RSSI Get

_Not decoded._ Directly disassembled. The handler calls bl #0xa470(&local_u16) to fetch a 16-bit value, then unconditionally writes resp_buf[0]=0x00 (status), resp_buf[1..2]=the FIXED constant 0x0200 (little-endian, written via a hardcoded `mov w8,#0x200; sturh w8,[x21,#1]` - not derived from any input or measurement), and resp_buf[3..4]=the fetched 16-bit value (little-endian). Response length is computed as fixed = 5 bytes. The function name 'wms_evt_get_rssi' (no 'bt_' prefix, unlike the explicitly Bluetooth-scoped 'v1_proc_bt_*' functions in the same binary, and distinct from the separately-logged 'wms: get bt test: rx pakects %d, rssi %d' BT-test string) is why I attribute this to the Wi-Fi-side antenna RSSI command rather than the BT RSSI test path, but I could not confirm this split any further, and I could NOT determine what the fixed 0x0200 field actually represents (a type/capability tag seems most likely given it never varies, but this is not confirmed), nor the real unit/scale of the fetched value at vaddr 0xa470 (not traced further within budget) - both are flagged below as unresolved rather than asserted. Handler correctly identified (inner handler at vaddr 0x11010 (self-logged by its own wrapper chain as 'wms_evt_get_rssi'), called via direct `bl` from a per-command wrapper starting at vaddr ~0x5bf8 (confirmed call site 0x5c6c -> bl #0x11010)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0B — WiFi Ap Mac Addr Set

_Not decoded._ App/RC sets the AP's hardware MAC address. Handler correctly identified (wms_evt_set_mac @0x5df0 -> v1_proc_set_macaddr @0xf3f0 -> wifi_mgmt_set_mac @0xaf08), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0C — WiFi Ap Mac Addr Get

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: wms_evt_get_mac @0x5fc8 -> v1_proc_get_macaddr @0xf558 -> wifi_mgmt_get_mac @0xaf18`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 6 | `wifi_ap_mac_addr_get_mac` (MAC Address) | ether | Response-only field; request payload is empty/unparsed. Current AP MAC address, raw 6 bytes. |

**Worked example:**

- Request payload: `(empty)`
  Get requests carry no payload; any bytes sent would be ignored by v1_proc_get_macaddr.
- Response payload: `60 60 1F AA BB CC`
  Bare 6-byte MAC address, straight from wifi_mgmt_get_mac, with the internal 1-byte status code stripped before transmission.

## 0x0D — WiFi Ap Passphrase Set

_Not decoded._ App/RC sets the AP's WPA2-PSK passphrase. Handler correctly identified (wms_evt_set_psk @0x6240 -> v1_proc_set_passwd @0xf7f0 (v1_interface/v1_proc.c) -> check_input_validity @0xc0f0, then wifi_mgmt_set_passwd @0xafe0), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0E — WiFi Ap Passphrase Get

_Not decoded._ App/RC reads back the AP's current WPA2-PSK passphrase. Handler correctly identified (wms_evt_get_psk @0x6418 -> v1_proc_get_passwd @0xf750 -> wifi_mgmt_get_passwd @0xafd8), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x0F — WiFi Ap Factory Reset

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: wms_evt_restore_default @0x6690 -> v1_proc_restore_default @0xf998 (v1_interface/v1_proc.c) -> either wifi_mgmt_restore_default @0xb078 or _run_sys_cmd @0xb718`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_factory_reset_sub_id` (Sub ID) | uint8 | Optional; if the payload is empty, treated as 0. |

**Worked example:**

- Request payload: `00`
  sub_id=0: full factory reset of the Wi-Fi AP config. (An empty/0-byte payload would behave identically.)
- Response payload: `00`
  1-byte status, always observed as 0x00 for every sub_id value including the 'do nothing' fallback.

## 0x10 — WiFi Ap Band Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: wms_evt_set_band @0x6790 -> v1_proc_set_band @0xffd0 (validation only) -> wifi_mgmt_set_band @0xb178 -> set_band_config @0xd638 / device_set_band @0x160c0`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_band_set_band` (Band) | uint8 | Wi-Fi band selector. |

**Worked example:**

- Request payload: `00`
  Requests band=0 (inferred: 2.4GHz).
- Response payload: `00`
  1-byte status: 0x00 = value <=2 (accepted); 0xFF = value >2 (flagged invalid in the ack) -- note the firmware still calls wifi_mgmt_set_band with the raw byte afterward regardless of this status, so an out-of-range byte's ultimate effect depends entirely on wifi_mgmt_set_band's own handling, which was not traced further.

## 0x11 — WiFi Ap Sta MAC Push

Payload decoder: `wifi_ap_push_sta_mac_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 6 | `wifi_ap_push_sta_mac_mac` (Mac) | ether |  |

## 0x12 — WiFi Ap Phy Param Get

Payload decoder: `wifi_ap_get_phy_param_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_ap_get_phy_param_signal_status` (Signal Status) | uint8 | enum:`enums.WIFI_ELEC_SIGNAL_SIGNAL_STATUS_ENUM` |

## 0x13 — WiFi Ap Power Mode Set

_Not decoded._ Presumed: sets some Wi-Fi power-related mode (RF transmit power profile, or CE/FCC/SRRC-style regulatory power mode, by analogy with cmd_set 0x06's documented-but-undecoded 'RC Power Mode CE/FCC Set/Get' commands) -- not confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x14 — WiFi Ap Calibrate

_Not decoded._ Presumed: triggers some RF/antenna calibration routine for the Wi-Fi radio -- not confirmed. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x15 — WiFi Ap Wifi Restart

_Not decoded._ App/RC requests the aircraft restart its Wi-Fi (hostapd/supplicant) stack, e.g. to apply a changed SSID/passphrase/channel/band without a full reboot. Confirmed no meaningful payload. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x16 — WiFi Ap Selection Mode Set

_Not decoded._ Presumed: sets how the AP selects something (channel/band auto-selection mode, or master/slave Wi-Fi-vs-SDR link selection, by loose analogy with the already-documented cmd 0x17 'WiFi Ap Selection Mode Get' and the 'load_acs_selection_info'/'save_acs_selection_info' strings seen in dji_network) -- not confirmed to be the same subsystem. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x17 — WiFi Ap Selection Mode Get

_Not decoded._ Public dissector name only; no payload semantics known going in. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x18 — WiFi Ap 18

_Not decoded._ A genuinely new finding, not just a byte layout for an already-named command: cmd_id 0x18 is a real, implemented command whose actual purpose is setting the aircraft's Wi-Fi regulatory country/region using a plain 2-character ISO-3166-1 alpha-2 code -- distinct from the already-documented cmd_id 0x30 ('WiFi Ap Set Country Code'), which this same binary implements separately via wms_evt_set_country_ext/v1_proc_set_country_ext using a different payload shape (two 4-byte region strings + a uint16, per the existing cmdset_07_Wi-Fi.md decode). 0x18 is the simpler, non-'ext' sibling. Typical use: ground-station app sets the drone's operating region to 'US' before first flight in a new country, which constrains legal channel/power limits. Handler correctly identified (wms_evt_set_country (vaddr 0x6be0, the per-cmd_id event-table entry for cmd_id 0x18) -> v1_proc_set_country (vaddr 0x100f8) -> check_country_alpha2 (vaddr 0xbe98) / wifi_mgmt_get_country (vaddr 0xb2e8) on the fallback path), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x19 — WiFi Ap 19

_Not decoded._ The read counterpart to 0x18: queries the aircraft's currently-configured Wi-Fi regulatory country as a plain 2-character code. A genuinely new command purpose, not previously named anywhere in the public dissector (there is no existing 'country get' of any kind in the cmd_set 0x07 catalog prior to this finding). Typical use: app reads back the current region setting to display it in a settings screen, with no input needed. Handler correctly identified (wms_evt_get_country (vaddr 0x6e28, the per-cmd_id event-table entry for cmd_id 0x19) -> v1_proc_get_country (vaddr 0x104f0) -> wifi_mgmt_get_country (vaddr 0xb2e8)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1A — WiFi Ap 1A

_Not decoded._ No name or payload semantics known. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1B — WiFi Ap 1B

_Not decoded._ No name or payload semantics known. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1C — WiFi Ap 1C

_Not decoded._ No name or payload semantics known. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1D — WiFi Ap 1D

_Not decoded._ No name or payload semantics known. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1E — WiFi SSID Get

_Not decoded._ Public dissector name suggests this duplicates/overlaps already-decoded cmd_id 0x07 'WiFi Ap SSID Get' (which dji_network's table DOES implement, via v1_proc_get_ssid at vaddr 0xf148). No separate implementation of 0x1E itself was found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x1F — WiFi Ap 1F

_Not decoded._ No name or payload semantics known. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x20 — WiFi Ap Wifi Frequency Get

_Not decoded._ Public dissector name implies a 2.4/5GHz band or exact-frequency query, plausibly overlapping already-decoded cmd_id 0x10 'Band Set' (which the table DOES implement, handler wms_evt_set_band / v1_proc_set_band) or the unimplemented 0x2C/0x2D code-rate pair -- but no separate implementation of 0x20 itself was found in the one confirmed handler. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x21 — WiFi Ap Set Bw

_Not decoded._ Operator app requests a specific Wi-Fi AP channel-bandwidth mode. Handler reads device-ready state (device_ctx+0x314==1 required, else immediate error ack), then reads 1 payload byte. Value 3 is accepted and acked without reconfiguration (acts like a recognized sentinel, plausibly 'unchanged'/'auto-managed'); value 0 is accepted, acked, AND triggers an actual reconfiguration (builds a shell command string via __sprintf_chk using the AP's current channel and executes it via a run-command helper, i.e. a real hostapd/driver bandwidth reconfig). Values 1 and 2 are not individually checked by this function and fall through a branch that neither acks nor errors (silently dropped) - a real, evidenced finding, not a guess. Handler correctly identified (net_evt_set_bw, entry at file/vaddr 0x000089a0 (self-logs its own name "net_evt_set_bw" at entry via duss_log_gen_head)), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x22 — WiFi Ap 22

_Not decoded._ Unknown - no live handler located on either firmware image via any of the four documented mechanisms plus the newly-confirmed dense dispatch-table variant. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x23 — WiFi Ap 23

_Not decoded._ Unknown - no live handler located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x24 — WiFi Ap 24

_Not decoded._ Unknown - no live handler located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x25 — WiFi Ap 25

_Not decoded._ Unknown - no live handler located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x26 — WiFi Ap Realtime Acs

_Not decoded._ Unknown wire payload - the real ACS engine was located and named with high confidence as a subsystem, but no evidence ties it to this specific cmd_id's wire format. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x27 — WiFi Ap Manual Switch SDR

_Not decoded._ Unknown wire payload for cmd_id 0x27 itself; a plausible but unconfirmed internal relative (net_ack_do_wifi_mode_switch) was found and is documented as a lead, not a decode. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x28 — WiFi Ap Channel List Get/Push

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: net_evt_push_channel_list, entry at file/vaddr 0x00008608`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `total_len` (Total payload length) | uint32 | Computed as (end_of_buffer - start_of_buffer); i.e. self-describing total byte length of this Push payload. |
  | 4 | 1 | `current_channel` (Current operating channel) | uint8 | Read from device_ctx+0x298. |
  | 5 | 4 | `band_mode` (Band mode flag) | uint32 | 1 if device_ctx+0x548==0 (single-band/2.4GHz-only), else 2 (dual-band). Stored as a 4-byte int (`str.w`), not a byte. |
  | 9 | 4 | `reserved_9_c` (Reserved/flag bytes) | bytes | Four individually-written bytes: offset 9 is always 1, offsets 0xa/0xb/0xc are always 0 in the disassembled construction path. Exact per-byte semantics beyond their constant values were not resolved - flagged explicitly as unconfirmed, not invented. |
  | 13 | 1 | `count_2g` (2.4GHz channel count) | uint8 | Read from device_ctx+0x425; number of entries in the channel_2g array that follows. |
  | 14 | 3 | `reserved_e_10` (Reserved/padding) | bytes | Not observed being explicitly written in the traced construction path between the count field and the array; best-effort assumption of 3 reserved/pad bytes based on the array's observed start offset (0x11) - flagged as unconfirmed. |
  | 17 | -1 | `channel_2g` (2.4GHz channel list) | uint16[count_2g] | count_2g little-endian uint16 channel numbers, each copied from a per-record source table at device_ctx+0x399 (stride 10 bytes/record). |
  | -1 | -1 | `band5_block` (5GHz block (conditional)) | struct (conditional) | Present only when device_ctx+0x548 != 0: a second small header (count/flags, including a byte sourced from device_ctx+0x548 again and state checks against device_ctx+0x314/0x324) immediately followed by its own uint16 channel array sourced from a table near device_ctx+0x426. Confirmed present in disassembly (two nested loops, mirrored structure to the 2.4GHz block) but exact header-byte semantics were not individually resolved to the same confidence as the 2.4GHz block - reported as a confirmed-to-exist, partially-resolved structure rather than invented detail. |

**Worked example:**

- Request payload: ``
  Get direction: zero-length DUML payload (the handler never reads any request-payload byte) - a bare query, 'give me the channel list'.
- Response payload: `17 00 00 00 06 01 00 00 00 01 00 00 00 03 00 00 00 01 00 06 00 0B 00`
  Push/response, single-band case (band_mode=1, no 5GHz block): total_len=0x17(23), current_channel=6, band_mode=1, reserved bytes 1/0/0/0, count_2g=3, 3 reserved/pad bytes, then channel_2g=[1,6,11] (classic non-overlapping 2.4GHz channel set) as 3 little-endian uint16s - 23 bytes total, matching the length field.

## 0x29 — WiFi Ap Channel Noise/SNR Req

_Not decoded._ App asks the aircraft to start or stop its periodic per-channel noise/SNR measurement (whose results are reported asynchronously via the already-documented sibling Push command 0x2A 'WiFi Ap Channel Noise/SNR Push', which this starts/feeds). Handler reads 1 payload byte, always immediately ACKs, then starts the SNR measurement timer if the byte is 0, or suspends it for any other value. Handler correctly identified (net_evt_req_channel_noise, entry at file/vaddr 0x000087c0), but the proposed field-layout (offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, not just unfound. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2A — WiFi Ap Channel Noise/SNR Push

Payload decoder: `wifi_ap_push_chan_noise_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `wifi_ap_push_chan_noise_total` (Total) | uint32 |  |

## 0x2B — WiFi Ap Set Hw Mode

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: net_evt_set_hw_mode, entry at file/vaddr 0x000092f8`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `reserved_or_unused_0` (Unresolved byte 0) | bytes | Not observed being read anywhere in the disassembled code path for this handler. Explicitly flagged as unconfirmed rather than guessed - may be a reserved/padding byte, or consumed only by a separate branch (vaddr 0x966c) not disassembled in this pass. |
  | 1 | 2 | `hw_mode` (New HW/PHY mode) | uint16 | Read via unaligned `ldrh.w r1,[msg,0x15]`. Compared against the current value cached at device_ctx+0x33c (skip-if-unchanged fast path) and, when different, gated by a region/capability byte-pair check at device_ctx+0x291/0x292 before being applied. No enum table for its numeric values was recovered in this pass - reporting the field's existence, size and role, not invented value names. |

**Worked example:**

- Request payload: `00 01 00`
  Unresolved byte=0x00 (placeholder, per the caveat above - not confirmed meaningful), hw_mode=0x0001 (uint16 LE): request a change to HW/PHY mode value 1.
- Response: One-way-ish SET pattern consistent with every other confirmed handler in this table (resp_ok/resp_err, no data payload); the exact terminal ack call for this specific handler's success path was not individually re-confirmed in this pass, so no response hex is asserted beyond noting it is ack-only by the project's established convention for this command family.

## 0x2C — Wifi Ap Code Rate Set

_Not decoded._ No dedicated handler found. Method: exhaustively enumerated dji_network's (E1E) complete net_evt_* debug-log function-name inventory via the __FUNCTION__-string-xref technique (17 names total, listed in shared_infrastructure_found) — none named code_rate/coderate/set_rate. grep for 'code_rate'/'coderate' across every file in both firmware roots: zero matches. The closest related real code is dji_network's MCS/rate-adaptation subsystem (/cali/wifi/mcs.conf, debug strings 'fixed_mcs=', 'mcs_mode=%d', functions load_mcs_config/mcs_set_grade/adjust_mcs_grade), but that subsystem is driven internally by live RSSI (string 'MCS_Adjust rssi %d, prev_mcs %d, curr_mcs %d'), not by an external DUML setter, and none of its functions carry a net_evt_* wrapper or any other literal-immediate cmd_set/cmd_id registration evidence. Also checked: all 12 of dji_sys's (E2) and all 11 of dji_sys's (E1E) literal duss_event_register_dynamic_command call sites (fully disassembled) — none register cmd_set 7. No other Wi-Fi-AP-management binary found in either firmware root (bin/lib listings of both e1e_extracted and e2_extracted fully enumerated; only generic hostapd/wpa_supplicant/iw and dji_network/dji_wlm found). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2D — Wifi Ap Cur Code Rate Get

_Not decoded._ Counterpart getter to 0x2c; same negative result for the same reasons (no net_evt_get_code_rate/cur_code_rate name in dji_network's exhaustive function-name inventory, no 'code_rate' string anywhere in either firmware root, no dji_sys literal registration for cmd_set 7). The MCS-adaptation internals (mcs_set_grade/adjust_mcs_grade, driven by RSSI) are the closest related real code but are not wired to any external get-style DUML command we could find. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x2E — WiFi Ap Set Usr Pref

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: net_evt_set_user_pref`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_user_pref` (User Preference) | uint8 | New Wi-Fi rate/MCS preference value, written into the network-context 'user_pref' field. Confirmed behavior: 1 = apply the secondary stored MCS-table snapshot as the active one; any other value = reset both the active and stored MCS-table fields to 0 (effectively 'auto/default'). No-op (ack with no state change) if it equals the value already stored. |

**Worked example:**

- Request payload: `550e04660207341240072e015fda`
  App (sender_type=2) sends WiFi Ap Set Usr Pref to the WiFi-air module (receiver_type=7) requesting ack-before-exec, setting the preference byte to 1 (apply stored MCS table). Built and round-tripped with this project's own duml_py codec.
- Response payload: `550d04330702341280072e2281`
  Ack-only response (packet_type=RESPONSE, no payload) — duss_event_resp_ok with no data, matching the disassembled handler which never calls duss_event_resp_data on the set path.

## 0x2F — WiFi Ap Get Usr Pref

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: net_evt_get_user_pref`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `wifi_user_pref` (User Preference) | uint8 | Current Wi-Fi rate/MCS preference value (response payload), read directly from the same network-context field (struct+0x32c) that WiFi Ap Set Usr Pref (0x2e) writes. See 0x2e for the confirmed value-1-vs-other branch semantics. |

**Worked example:**

- Request payload: `550d04330207351240072f5175`
  App requests the current Wi-Fi user preference; no payload. Built and round-tripped with this project's own duml_py codec.
- Response payload: `550e04660702351280072f01b79b`
  WiFi-air module responds with the current 1-byte preference value (1 = apply-stored-MCS-table), matching the disassembled handler's duss_event_resp_data(handle, ctx, &byte, 1) call.

## 0x30 — WiFi Ap Set Country Code

Payload decoder: `wifi_ap_set_country_code_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 4 | `wifi_set_country_code_str1` (Region Str1) | string |  |
  | 4 | 4 | `wifi_set_country_code_str2` (Region Str2) | string |  |
  | 8 | 2 | `wifi_set_country_code_unkn8` (Unknown8) | uint16 |  |

## 0x31 — WiFi Ap Reset Freq

_Not decoded._ No dedicated handler found. Full net_evt_* name inventory of dji_network (E1E) has no reset_freq/freq_reset entry; grep for 'reset.?freq'/'freq.?reset' across the whole binary and both firmware roots: zero matches. The closest related real code examined was inside net_evt_set_country_code (cmd 0x30, already documented) itself: when that command's own 3rd payload byte (a mode/flag field at event-ctx+28) is >=2, the handler force-writes a literal 'K3' country code and stores the raw flag value into struct+0x298 (the same field 0x2e/0x2f's MCS-snapshot logic reads from) — a sub-behavior of 0x30, not a separate 0x31 wire command. No distinct standalone 'reset frequency/channel' handler was found. Also checked: dji_sys's literal duss_event_register_dynamic_command call sites (all 23 across E1E+E2 builds) — none for cmd_set 7. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x32 — WiFi Ap Del Country Code

_Not decoded._ No dedicated handler found. The country-code-related real functions recovered from dji_network's __FUNCTION__-string inventory are exactly three: net_evt_set_country_code (cmd 0x30, already documented), net_get_country_code, and net_alpha2_to_country_code — all fully disassembled; none implement a delete/clear operation distinct from the existing set path. grep for 'del_country'/'delete_cc'/'clear_country'/'rm_country' and generic 'del'+'country' co-occurrence across dji_network and the whole firmware tree: no matching function-name evidence beyond the shell helper set_country_code.sh (E2 bin/, a factory/production script, not a DUML handler) and the /factory_data/wifi/country.txt config file reader already covered by net_get_country_code. No separate 0x32 handler located. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x33 — WiFi Ap Verify Cc

_Not decoded._ No dedicated handler found. grep for 'verify' anywhere in dji_network: zero matches. The three real country-code functions (net_evt_set_country_code, net_get_country_code, net_alpha2_to_country_code — all disassembled for the 0x30/0x31/0x32 investigation above) contain validation-adjacent logic (e.g. net_evt_set_country_code's memcmp against a stored 2-byte reference at struct+0x291/+0x292 to detect a no-op 'unchanged' set), but no distinct 'verify/validate country code without applying it' entry point or function name was found. No other candidate binary found in either firmware root. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x39 — WiFi Get Work Mode

_Not decoded._ No dedicated handler found. Full net_evt_* inventory of dji_network has no get_work_mode/get_mode entry. grep for 'work_mode'/'workmode' across dji_network and the whole firmware tree: zero matches. dji_network does have a real AP-vs-STA operating-mode concept (source files states/wifi_ap_states.c and states/wifi_sta_states.c, and debug strings 'Wifi Connected (AP)'/'Wifi Connected (STA)'/'rc info gathered, switch to station mode'/'w_ctrl:switch to app mode'), but it is implemented as an internal state machine with no net_evt_*-named external getter found; could not establish that this cmd_id reads that state machine's current mode. No other candidate binary found. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3A — WiFi Set Work Mode

_Not decoded._ Counterpart setter to 0x39; same negative result (no net_evt_set_work_mode/set_mode name, no 'work_mode' string anywhere in either firmware root). Note: dji_sys's (E1E) literal duss_event_register_dynamic_command call site at vaddr 0x503a8 registers cmd_set=6/cmd_id=0x3a ('RC 2014 Usb Mode Set', already flagged elsewhere in this project as board-specific/dead on this image per 21_PAYLOAD_DECODE_SWEEP_FINDINGS.md) — a numerically coincidental but confirmed-unrelated different cmd_set (6, not 7); re-verified this is not a mismatch in our own transcription. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x3B — WiFi Config By Qrcode

_Not decoded._ No handler found anywhere, and no Wi-Fi-provisioning-relevant QR-code code at all in either firmware root. A content grep (via strings, not filename) for 'qrcode'/'qr_code' across every file in both bin/ and lib/ (and lib64/) of both e1e_extracted and e2_extracted turned up exactly: bin/dji_autoflight, bin/dji_ml, and a cluster of unrelated 'at_*.so' manufacturing/calibration self-test shared libraries (at_imubias.so, at_compass.so, at_sdr.so, at_imucali.so, at_vision_sensor_test.so, at_gimbal_yaw.so, at_gimbalcali.so, at_v1trigger.so, at_cleardata.so, at_barotest.so, at_systimer.so, at_checkcb.so, at_qrcode.so, at_imubiastemp.so) plus libimss.so (E1E) and libopencv_java3.so (E2, dji_ml only). This is itself a notable finding: these AT ('Aging Test') modules all share a common literal table of manufacturing self-test module names — at_qrcode.so is a physical QR-sticker scanner used during production hardware calibration (unrelated to end-user Wi-Fi provisioning), and its name only coincidentally overlaps with this command's name. No net_evt_*-named handler, no dji_network string, and no dji_sys/dji_sdrs_agent literal or table-driven registration evidence ties any code to this cmd_id. Genuinely plausible that 'WiFi Config By Qrcode' on this product is implemented entirely app/phone-side (the app decodes the QR code into an SSID+passphrase pair and simply issues the ordinary SSID/passphrase Set commands), with cmd_id 0x3b itself unimplemented/reserved on this aircraft firmware build. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x80 — WiFi Push Mac Stat

_Not decoded._ Aircraft -> App/RC periodic push of Wi-Fi link MAC-layer statistics (retry rate, byte/packet counters, signal metrics) while a Wi-Fi link (AP or STA) is active. No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x82 — WiFi Master/Slave Status Get/Push

_Not decoded._ Likely: status push/query of the aircraft's or RC's role (master/slave) in a dual-link-role or dual-RC pairing scenario (DJI's proprietary 802.11p ad-hoc link master/slave roles, or dji_wlm's dual-remote-controller flight-control-handoff arbitration -- both real, named subsystems found in these binaries, neither confirmed as this cmd_id's actual handler). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x83 — WiFi Master/Slave AuthCode Set

_Not decoded._ Likely: sets the shared pairing/authentication code used by DJI's proprietary 802.11p ad-hoc master/slave Wi-Fi link (candidate subsystem only, not a confirmed handler). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x84 — WiFi Scan Master List

_Not decoded._ Likely: returns/pushes the list of nearby 802.11p-ad-hoc 'master' broadcasters (or candidate master remote controllers) discovered during a scan, for subsequent pairing via cmd_id 0x85 (candidate subsystem only, not a confirmed handler). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x85 — WiFi Connect Master With Id AuthCode

_Not decoded._ Likely: instructs the device to join a specific, previously-scanned 802.11p-ad-hoc 'master' identified by an id, authenticating with the pairing auth code (candidate subsystem only, not a confirmed handler). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x89 — WiFi AuthCode Get

_Not decoded._ Likely: returns the current pairing/authentication code for the 802.11p ad-hoc master/slave Wi-Fi link (candidate subsystem only, not a confirmed handler). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x8B — WiFi MS Error Info Get/Push

_Not decoded._ Likely: pushes or returns an error/failure code for the master/slave pairing subsystem (candidate subsystem only, not a confirmed handler). No aircraft-side decoder found despite exhaustive search. See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology.

## 0x91 — WiFi Rc Info Set

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: net_evt_set_rc_info @ 0x7ad0`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `reserved_or_subtype` (Reserved / Sub-type (unresolved)) | uint8 | Present in the payload by struct-offset arithmetic (raw struct offset 0x14, one byte before the first byte this handler actually reads at raw 0x15), but never read anywhere in the traced net_evt_set_rc_info body. Could be a reserved/padding byte, or a sub-type/role selector consumed by an outer dispatch layer before reaching this specific sub-handler. Reported honestly as unresolved rather than guessed. |
  | 1 | 1 | `ssid_len` (RC Wi-Fi SSID Length) | uint8 | Length in bytes of the following rc_wifi_ssid field. Read via ldrb at raw struct offset 0x15 (= wire offset 1). Destination buffer is 0x40 (64) bytes, so the practical maximum is 63 (the memset pre-zeroes the full buffer, so a shorter string is implicitly NUL-padded). |
  | 2 | 12 | `rc_wifi_ssid` (RC Wi-Fi SSID) | ascii_string | ssid_len bytes of ASCII, memcpy'd into a 64-byte buffer in the Wi-Fi context struct (ctx+0xa6c -> +0x2c1). Named by inferred purpose/ordering (see handler_evidence) -- not an explicit string match in the binary. Size shown (12) is the example value below, not a fixed field size; the field is length-prefixed and variable (0-63 bytes). |
  | 14 | 1 | `password_len` (RC Wi-Fi Password Length) | uint8 | Length in bytes of the following rc_wifi_password field, located immediately after rc_wifi_ssid's data (raw offset = r5+0x16+ssid_len). Destination buffer is 0x21 (33) bytes, so the practical maximum is 32 -- the canonical size for a WPA/WPA2-PSK ASCII passphrase. |
  | 15 | 11 | `rc_wifi_password` (RC Wi-Fi Password) | ascii_string | password_len bytes of ASCII, memcpy'd into a 33-byte buffer (ctx+0xa6c -> +0x2a0, which sits immediately before the SSID buffer in the struct, i.e. struct field order is {password[33], ssid[64]} even though the SSID arrives first on the wire). Named by inferred purpose/ordering, not an explicit string match. Size shown (11) is the example value below; the field is length-prefixed and variable (0-32 bytes). |

**Worked example:**

- Request payload: `000c52435f4d61766963335f35470b536b794c696e6b32303234`
  26-byte payload for an RC telling the aircraft to join a Wi-Fi network: reserved/unresolved byte 0x00; ssid_len=0x0C (12); SSID 'RC_Mavic3_5G' (12 ASCII bytes); password_len=0x0B (11); password 'SkyLink2024' (11 ASCII bytes). Ordinary representative values, not attack-shaped.
- Response: Request/response exchange (not one-way): the handler calls duss_event_resp_ok(ctx, payload) directly, which in this codebase sends a bare success acknowledgement with no additional application-level payload bytes (this project's established convention for simple Set-type command acks, as opposed to duss_event_resp_data_v2-style acks that carry real response data).

## 0x92 — WiFi Update Sw State

Payload decoder (binary RE, this project's own disassembly — not from the public dissector): `binary RE: net_evt_update_sw_state @ 0x9dfe (ARM32/e1e); wms_evt_update_sw_state @ 0x8f1c (AArch64/e2)`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `sw_state` (Wi-Fi Switch State) | uint8 | Read via ldrb at raw struct offset 0x14 (= wire offset 0) in both independently-analyzed implementations. The value is compared for equality against 1 to pick the enable vs. disable code path; only 0 and 1 are meaningfully exercised in the disassembly (anything else falls through to the 'disable' branch, so is not a distinct state in practice). |

**Worked example:**

- Request payload: `01`
  1-byte payload: sw_state=0x01, enabling the Wi-Fi subsystem (e.g. the app turning on the aircraft's Wi-Fi direct-connect/image-transmission service). An all-zero/0x00 payload would be the disable case.
- Response: Request/response exchange: the handler computes a success/failure result and returns it as an integer status (0=success observed in the AArch64 build); the generic DUSS event-dispatch wrapper that invoked the handler sends the actual DUML ACK frame based on that return value. Expected ACK has no additional application-level payload bytes, consistent with 0x91's duss_event_resp_ok convention.
