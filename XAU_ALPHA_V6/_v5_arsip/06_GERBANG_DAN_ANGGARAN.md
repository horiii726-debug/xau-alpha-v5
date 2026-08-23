# 06 — GERBANG KELULUSAN, ANGGARAN TRIAL & LEDGER

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


Semua ambang di file ini **dikunci sebelum melihat hasil**. Mengubahnya setelah melihat hasil
butuh **OVERRIDE V5 tertulis dari user** dan mengulang dari awal (§O8).

## Dua rezim seleksi yang berbeda

| | Divisi arah (X, E, M) | Divisi estimasi (V, Q, T) |
|---|---|---|
| Aturan seleksi | `threshold_only` | Model Confidence Set, alpha=0.10 |
| Boleh diperingkat? | **TIDAK.** `forbid_argmax: true` | Ya — targetnya terukur |
| Tie-break | tidak ada — lolos atau mati | paling sederhana |
| Jumlah centang | 17 | 3 |

## Anggaran bukan negosiasi

`screen_max = min(500, floor(50 * K_eff_terukur))`. K_eff 10 → 500 kandidat. K_eff 4 → 200.
**K_eff < 3 → BERHENTI, jangan jalankan apapun.** Ini dihitung otomatis dari pengukuran F0.

Kalau anggaran memaksa pemangkasan, urutannya sudah dikunci: **E tier-3 duluan, X paling terakhir** —
karena X adalah satu-satunya divisi yang belum pernah diuji sekalipun dan di situ peluang terbesar berada.

## Gerbang kelulusan

```yaml
gates:
  direction:      # divisi X, E, M — TIDAK ADA PERINGKAT
    selection_rule: threshold_only
    forbid_argmax: true
    checklist:
      - expectancy_net_bps_positif_pada_biaya_worst
      - t_stat_dengan_effective_n >= 3.0
      - lolos_BH_FDR_q_0.10
      - DSR >= 0.95
      - PBO <= 0.50
      - mengalahkan_B01_sampai_B08
      - CPCV_path_positif >= 80%
      - bootstrap_CI95_tidak_memuat_nol
      - permutasi_blok_di_atas_persentil_95
      - walkforward_konsistensi_tanda >= 80%
      - stabil_di_10_seed
      - sepertiga_terakhir_masih_signifikan
      - trades_per_tahun >= 300
      - MC2_P_breach_250_trade <= 5%
      - MC3_expectancy_positif_di_persentil_5
      - MC5_tidak_runtuh_pada_plus_minus_20pct
      - konsisten_di_minimal_60pct_instrumen_panel
  estimation:     # divisi V, Q, T — target terukur, boleh diperingkat
    selection_rule: model_confidence_set
    alpha: 0.10
    tie_break: paling_sederhana
    checklist:
      - masuk_model_confidence_set
      - mengalahkan_baseline_naif
      - stabil_lintas_sub_periode
  kalau_nol_lolos:
    wajib_ditulis: "Nol kandidat lolos. Ini temuan tentang pasarnya, bukan kegagalan proses."
    dilarang:
      - melonggarkan ambang
      - menambah kandidat
      - mengganti definisi statistik
      - mencari partisi data yang lebih ramah
    yang_boleh: lihat_protokol_nol_lolos
```

## Anggaran trial & tangga pemangkasan

Total maksimum **572 baris ledger**: 72 pilot horizon (F2b) + <=500 screening pada horizon terpilih.

```yaml
trial_budget:
  pilot_horizon_max: 72        # F2b: 12 formula murah x 6 horizon
  screen_max: 500              # F4-F7, HANYA pada horizon terpilih
  total_ledger_max: 572
  screen_max_ditentukan_oleh:
    formula: "screen_max = min(500, floor(50 * K_eff_terukur))"
    alasan: >
      Anggaran kandidat harus proporsional terhadap jumlah instrumen INDEPENDEN
      efektif yang benar-benar terukur di F0, bukan terhadap jumlah instrumen
      mentah. K_eff 10 -> 500 kandidat. K_eff 4 -> 200 kandidat.
      K_eff 3 -> 150 kandidat. Ini dihitung otomatis, bukan dinegosiasikan.
  confirm_max: 8
  confirm_max_locked: true
  holdout_shots: 1
  naikkan_butuh: "OVERRIDE V5 tertulis dari user"
  aturan_horizon: >
    Horizon adalah bagian dari HIPOTESIS (H20: horizon berbeda = eksperimen
    berbeda). Karena itu menjalankan registri penuh di 6 horizon = 6x jumlah
    trial. DILARANG. Horizon dipilih dulu di F2b dengan pilot kecil, lalu
    registri penuh dijalankan di 1-2 horizon terpilih saja.

  # DIPERBAIKI r5: registri berisi 507 varian tapi screen_max <= 500, dan tidak
  # ada aturan APA yang dipangkas. Divisi E (209) jauh lebih besar dari X (114)
  # padahal X prioritas tertinggi. Tanpa aturan ini, pemangkasan akan sembarang.
  tangga_pemangkasan:
    komposisi_registri: {X: 114, E: 209, M: 81, V: 41, Q: 35, T: 27, TOTAL: 507}
    prinsip: >
      Yang dipangkas DULUAN adalah yang prioritasnya PALING RENDAH dan
      biayanya PALING MAHAL. X tidak pernah dipangkas sampai langkah terakhir,
      karena X adalah satu-satunya divisi yang belum pernah diuji sekalipun
      dan tempat peluang terbesar berada.
    urutan_pangkas:
      1: "E tier-3 (E40-E45, E95-E97) — mahal + spekulatif. Potong -37 varian."
      2: "E tier-2 dengan grid besar: kecilkan grid ke maksimal 3 varian per formula (E33 9->3, E35 8->3, E80 6->3, E97 6->3, E02 6->3, E03 6->3, E22 6->3, E24 6->3). Potong -29."
      3: "M selain meta-labeling & baseline: buang M01-M05, M09, M10, M14, M15. SISAKAN M06, M07, M08 (baseline wajib aturan M6) dan M11 (meta-labeling, prioritas tertinggi divisi M). Potong -53."
      4: "E tier-1 dengan grid besar: kecilkan ke 2 varian per formula. Potong sesuai kebutuhan."
      5: "V/Q/T: sisakan 1 varian per formula (jendela tengah). Potong -60."
      6: "X — DIPANGKAS TERAKHIR, dan hanya varian, bukan formula."
    tidak_boleh_dipangkas_dalam_kondisi_apapun:
      - X01_TRIPLE_BARRIER_GRID     # gerbang payoff F2, bukan kandidat biasa
      - X06_VERTICAL_ONLY_BASELINE  # baseline pembanding wajib
      - X33_DRAWDOWN_CONSTRAINED_SIZING  # bentuk matematis aturan prop firm
      - V01_PARKINSON               # dipakai labeling & penskalaan barrier
      - V05_CLOSE_TO_CLOSE          # baseline pembanding wajib
      - M06_LASSO                   # baseline wajib aturan M6
      - M07_RIDGE                   # baseline wajib aturan M6
      - Q10_SPREAD_PERCENTILE_GATE  # gerbang biaya eksekusi
      - Q12_REALIZED_SPREAD_COST    # perhitungan biaya
    contoh_hasil_pemangkasan:
      K_eff_10_budget_500: "pangkas langkah 1 saja -> 470 varian. X utuh 114."
      K_eff_6_budget_300:  "pangkas langkah 1-3 -> 388, lalu langkah 4 -> ~300. X utuh 114."
      K_eff_4_budget_200:  "pangkas langkah 1-5 -> ~200. X utuh 114, estimasi 36, E ~40, M 10."
      K_eff_kurang_dari_3: "BERHENTI. Lihat stop_conditions.0. Jangan jalankan apapun."
```

## Ledger

Ledger dimulai **KOSONG**. Trial v3/v4 tidak diwarisi — instrumen, horizon, dan struktur label berbeda.

```yaml
ledger:
  file: ledger_trials.csv
  kolom: [trial_id, timestamp, candidate_id, formula_id, division, instrument_set,
          horizon, params_hash, partition, n_trades, eff_n, ic, t_stat, p_raw,
          p_effN, expectancy_bps, sharpe, max_dd, capture_ratio, status, notes]
  aturan:
    - "Sweep 42 kombinasi = 42 baris"
    - "Percobaan gagal/dibatalkan/error TETAP dicatat"
    - "Panel 1 hipotesis di 25 instrumen = 1 BARIS (satu hipotesis)"
    - "Grid hyperparameter ML 100 kombinasi = 100 baris"
    - "Ledger dimulai KOSONG. Trial v3/v4 tidak diwarisi — instrumen, horizon, dan struktur label berbeda."
```

## Protokol kalau nol lolos

Kerjakan **URUT dari atas**. Laporkan tiap langkah sebelum lanjut. Langkah 6 — *terima kalau memang nol* — adalah jawaban yang sah dan menghemat uang.

```yaml
protokol_nol_lolos:
  catatan: "Kerjakan URUT dari atas. Laporkan tiap langkah sebelum lanjut."
  langkah:
    1: "Cek horizon. Apakah membaik di horizon lebih panjang? Biaya menelan 7.9% di 24 menit vs 2.5% di 4 jam."
    2: "Cek biaya. Apakah ada sesi/jam dengan spread jauh lebih murah? Membatasi trading ke jendela biaya rendah kadang membalik expectancy tanpa mengubah sinyal."
    3: "Perbesar panel. eff N naik linear terhadap jumlah instrumen. Pengungkit terkuat yang tersisa."
    4: "Perpanjang riwayat. Dukascopy punya data lebih jauh dari 2020."
    5: "Cari di area yang belum disentuh: exit & sizing, ruin theory, optimal stopping. BUKAN menambah kandidat entry."
    6: "Terima kalau memang nol. Laporkan tanpa dilunakkan. Itu jawaban yang menghemat uang."

# =============================================================================
# 10. FORMULA — matematika eksplisit + grid parameter
# =============================================================================
# CARA BACA:
#   formula      = matematikanya, ditulis eksplisit supaya bisa dikodekan
#                  tanpa menebak. Notasi: H=high, L=low, C=close, O=open,
#                  r_t = ln(C_t/C_{t-1}), n = panjang jendela.
#   params       = grid parameter. Setiap kombinasi = 1 VARIAN = 1 baris ledger.
#   variants     = jumlah kombinasi grid (= jumlah kandidat dari formula ini)
#   n_parameters = parameter bebas yang harus dipilih dari data (anggaran §O4)
```
