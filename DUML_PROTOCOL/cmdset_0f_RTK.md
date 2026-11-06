# Cmd Set 0x0f — RTK

Total known command IDs: 1

## 0x09 — Rtk Status

Payload decoder: `rtk_rtk_status_dissector`

  | Off | Size | Field | Type | Notes |
  |---|---|---|---|---|
  | 0 | 1 | `rtk_rtk_status_a` (A) | uint8 |  |
  | 1 | 1 | `rtk_rtk_status_b` (B) | uint8 |  |
  | 2 | 1 | `rtk_rtk_status_c` (C) | uint8 |  |
  | 3 | 1 | `rtk_rtk_status_d` (D) | uint8 |  |
  | 4 | 1 | `rtk_rtk_status_e` (E) | uint8 |  |
  | 5 | 1 | `rtk_rtk_status_f` (F) | uint8 |  |
  | 6 | 1 | `rtk_rtk_status_g` (G) | uint8 |  |
  | 7 | 1 | `rtk_rtk_status_h` (H) | uint8 |  |
  | 8 | 1 | `rtk_rtk_status_i` (I) | uint8 |  |
  | 9 | 1 | `rtk_rtk_status_j` (J) | uint8 |  |
  | 10 | 1 | `rtk_rtk_status_k` (K) | uint8 |  |
  | 11 | 8 | `rtk_rtk_status_l` (L) | double |  |
  | 19 | 8 | `rtk_rtk_status_m` (M) | double |  |
  | 27 | 4 | `rtk_rtk_status_n` (N) | float |  |
  | 31 | 8 | `rtk_rtk_status_o` (O) | double |  |
  | 39 | 8 | `rtk_rtk_status_p` (P) | double |  |
  | 47 | 4 | `rtk_rtk_status_q` (Q) | float |  |
  | 51 | 4 | `rtk_rtk_status_r` (R) | float |  |
  | 55 | 1 | `rtk_rtk_status_s` (S) | uint8 |  |
  | 56 | 1 | `rtk_rtk_status_t` (T) | uint8 |  |
