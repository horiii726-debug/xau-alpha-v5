# 05 — VALIDASI STATISTIK, NULL BENCHMARK & MONTE CARLO

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


Alat ukurnya dibangun **sebelum** kandidat pertama dijalankan (fase F1). Jangan mengukur
pakai alat yang belum diuji.

## Tiga hal yang paling sering salah dan sudah diperbaiki di sini

1. **Null benchmark harus berupa KODE, bukan aturan di dokumen.** Kalau cuma tertulis, dia tidak pernah menyaring apapun.
2. **B09 `PERFECT_FORESIGHT` DILARANG masuk `must_beat_all`.** Gerbang yang mustahil dilewati membunuh semua kandidat tanpa membedakan mutu — informasinya nol. Dia dipakai menghitung `capture_ratio` saja.
3. **P-value tanpa bobot keunikan = halusinasi.** Metode naif melaporkan 16 dari 112 kandidat signifikan; setelah dikoreksi tersisa 0–1.

## Monte Carlo — yang paling penting untuk uang nyata adalah MC2

MC1 menjawab *"apakah edge-nya nyata?"*. **MC2 menjawab *"apakah AKUNNYA SELAMAT?"***
Sistem dengan expectancy positif tapi `P(breach) = 40%` adalah sistem yang menghancurkan akun
sebelum sempat menghasilkan. Gate: `P(breach dalam 250 trade) <= 5%`.

## Null benchmark

Wajib ada **sebagai kode** sebelum kandidat pertama. Dua uji sanity wajib: sinyal acak tidak boleh menang, sinyal lookahead harus menang.

```yaml
null_benchmarks:
  module: src/stats/nulls.py
  wajib_ada_sebelum_kandidat_pertama: true
  must_beat_all: [B01, B02, B03, B04, B05, B06, B07, B08]
  reference_only: [B09]
  daftar:
    B01: {nama: BUY_AND_HOLD}
    B02: {nama: RANDOM_MATCHED, catatan: "entry acak, holding-time & biaya dicocokkan — PALING PENTING"}
    B03: {nama: BLOCK_PERMUTED, catatan: "autokorelasi dipertahankan"}
    B04: {nama: TSMOM_12M}
    B05: {nama: COIN_FLIP, catatan: "arah acak, timing sama"}
    B06: {nama: ALWAYS_LONG}
    B07: {nama: ALWAYS_SHORT}
    B08: {nama: RANDOM_FREQ_MATCHED}
    B09: {nama: PERFECT_FORESIGHT, catatan: "MUSTAHIL dikalahkan by definition — REFERENSI SAJA"}
  b09_aturan: >
    B09 DILARANG masuk must_beat_all. Gerbang yang mustahil dilewati membunuh
    semua kandidat tanpa membedakan mutu — informasinya nol.
    Dipakai menghitung capture_ratio = PnL_kandidat / PnL_B09.
  wajib_dilaporkan:
    - matriks korelasi antar null
    - jumlah null independen efektif (eigenvalue matriks korelasi)
  uji_sanity_wajib:
    - "Sinyal acak murni TIDAK boleh mengalahkan null manapun"
    - "Sinyal lookahead sengaja HARUS mengalahkan semuanya (kalau tidak, bug di null)"
```

## Ambang statistik

```yaml
statistics:
  t_stat_hurdle: 3.0
  effective_n:
    method: lopez_de_prado_uniqueness
    mandatory_for_all_pvalues: true
    assertion_reject_without_weight: true
  hac: newey_west
  fdr: {method: benjamini_hochberg, q: 0.10, n_source: ledger_executed_rows}
  dsr: {threshold: 0.95, n_source: ledger_cumulative}
  pbo: {threshold: 0.50}
  spa: {method: hansen_spa, plus: white_reality_check}
  cpcv: {n_paths_min: 66, purged: true, embargo: true, min_positive_pct: 80}
  bootstrap: {n: 2000, method: block, ci: 0.95, must_exclude_zero: true}
  permutation: {n: 1000, method: block, min_percentile: 95}
  walkforward: {n_windows_min: 24, sign_consistency_pct: 80}
  seed_stability: {n_seeds: 10, must_not_flip: true}
  last_third_significant: true
  min_trades_per_fold: 200
  min_trades_per_year: 300
  max_ic_gross_plausible: 0.15
```

## Deduplikasi kandidat

Korelasi >= 0.90 terhadap divisi sendiri → alias, tidak masuk registry. Terhadap graveyard → auto-kill, tidak dijalankan sama sekali.

```yaml
dedup:
  corr_threshold: 0.90
  vs_same_division: "korelasi >= 0.90 -> alias, tidak masuk registry"
  vs_graveyard: "korelasi >= 0.90 -> auto-kill, tidak dijalankan"
  computed_on: partisi_screen
```

## Monte Carlo — 5 jenis, semuanya wajib

```yaml
montecarlo:

  MC1_permutasi:
    tujuan: "Apakah edge-nya nyata atau kebetulan?"
    method: block_permutation
    n: 1000
    catatan: "Permutasi acak biasa TIDAK cukup — merusak autokorelasi, null jadi terlalu lemah."
    gate: "hasil kandidat di atas persentil 95"

  MC2_jalur_survival:
    tujuan: "Apakah AKUNNYA SELAMAT? — paling penting untuk uang nyata"
    method: bootstrap_resample_urutan_trade
    n_paths: 10000
    terapkan_aturan_prop_firm:
      max_daily_loss_pct: LOOKUP        # cari di spesifikasi FTMO/FundedNext
      max_total_drawdown_pct: LOOKUP
      profit_target_pct: LOOKUP
    hitung:
      - "P(breach) dalam 100 / 250 / 500 trade"
      - "distribusi drawdown maksimum (bukan nilai tunggal)"
      - "waktu ekspektasi sampai target profit"
      - "P(ruin) sebelum target tercapai"
    gate: "P(breach dalam 250 trade) <= 5% pada ukuran posisi yang diusulkan"
    kalau_gagal: >
      Kecilkan ukuran posisi, hitung ulang. Kalau pada ukuran terkecil pun masih
      gagal -> kandidat DITOLAK untuk akun prop firm.
      Sistem dengan expectancy positif tapi P(breach) 40% adalah sistem yang
      menghancurkan akun sebelum sempat menghasilkan.

  MC3_eksekusi:
    tujuan: "Apakah tahan slippage?"
    method: "sampel acak dari grid slippage (alpha, beta) per trade"
    n_paths: 1000
    gate: "expectancy tetap positif di persentil ke-5 dari distribusi hasil"

  MC4_deflated_sharpe:
    tujuan: "Kalahkan Sharpe maksimum yang muncul dari N trial karena kebetulan"
    method: "simulasi expected_max_sharpe di bawah null, N dari ledger"
    gate: "DSR >= 0.95"

  MC5_gangguan_parameter:
    tujuan: "Apakah edge-nya rapuh terhadap setelan?"
    method: "goyang tiap parameter +/-10% dan +/-20%"
    n_combos: 500
    gate: >
      Tanda expectancy TIDAK boleh berubah. Kalau berubah karena lookback
      digeser 20 -> 22, itu overfit, bukan edge.
```

## Aturan machine learning

Meta-labeling **duluan**, bukan model arah baru. Meta-labeling menaikkan presisi tanpa menambah trial di ruang arah.

```yaml
machine_learning:
  diizinkan:
    - CatBoost
    - XGBoost
    - LightGBM
    - RandomForest
    - ExtraTrees
    - Lasso
    - Ridge
    - ElasticNet
    - SVM_RBF
    - KernelRidge
    - KalmanFilter          # estimator keadaan laten, BUKAN anchor mean-reversion
    - MetaLabeling
  dilarang_sampai_eff_n_5000:
    - LSTM
    - Transformer
    - CNN
    - deep learning apapun
  alasan_larangan: "jumlah parameter melampaui anggaran secara ekstrem"
  aturan:
    M1: "Validasi HANYA CPCV purged + embargo. K-fold biasa DILARANG (bocor lewat label tumpang tindih)."
    M2: "Bobot sampel = keunikan label."
    M3: "Feature importance pakai MDA (out-of-sample), BUKAN MDI (in-sample)."
    M4: "Hyperparameter tuning di inner loop nested CV."
    M5: "Setiap kombinasi hyperparameter = 1 baris ledger. Grid 100 = 100 trial."
    M6: "WAJIB mengalahkan baseline linear teregularisasi. Kalau tidak, kompleksitasnya tidak dibenarkan."
    M7: "WAJIB lolos MC5 gangguan parameter."
    M8: "Fitur wajib punya mekanisme. Fitur kotak hitam tanpa hipotesis DILARANG."
    M9: "DILARANG melatih ulang pada holdout, apapun alasannya."
  prioritas: >
    Meta-labeling DULUAN, bukan model arah baru. Meta-labeling memakai sinyal
    yang sudah ada dan hanya memutuskan taruh/tidak — menaikkan presisi tanpa
    menambah trial di ruang arah.
```
