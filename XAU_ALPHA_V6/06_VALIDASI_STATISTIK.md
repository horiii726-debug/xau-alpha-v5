# 06 — VALIDASI STATISTIK, NULL BENCHMARK & MONTE CARLO

> Alat ukur dibangun **sebelum** kandidat pertama (F1). Jangan mengukur pakai alat
> yang belum diuji.

---

## Bagian A — Null benchmark

Wajib ada **sebagai KODE**, bukan aturan di dokumen. Kalau cuma tertulis, dia tidak
pernah menyaring apapun.

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
    B09: {nama: PERFECT_FORESIGHT, catatan: "MUSTAHIL dikalahkan — REFERENSI SAJA"}

  b09_aturan: >
    B09 DILARANG masuk must_beat_all. Gerbang yang mustahil dilewati membunuh semua
    kandidat tanpa membedakan mutu — informasinya nol.
    Dipakai menghitung capture_ratio = PnL_kandidat / PnL_B09.
```

### 🔄 Null baru untuk multi-strategi

```yaml
  null_router:
    # WAJIB dikalahkan oleh router §09. Tanpa ini, router tidak bisa dibedakan dari derau.
    N1_EQUAL_WEIGHT_STATIC:
      definisi: "tiga keluarga bobot sama, TANPA informasi rezim sama sekali"
      arti_kalau_kalah: "router tidak menambah nilai. Pakai bobot sama, catat, selesai."

    N2_BEST_SINGLE_FAMILY:
      definisi: "keluarga tunggal terbaik, dipilih lewat Model Confidence Set (BUKAN argmax)"
      arti_kalau_kalah: "diversifikasi keluarga tidak terbayar. Jalankan satu keluarga."

    N3_REGIME_SHUFFLE:
      definisi: >
        Label rezim DIACAK sambil MEMPERTAHANKAN distribusi durasi rezim
        (block shuffle pada deret label, bukan per-bar shuffle).
      n: 1000
      arti_kalau_kalah: >
        PALING PENTING. Router yang tidak mengalahkan label rezim acak berarti
        keunggulannya berasal dari struktur alokasi, BUKAN dari deteksi rezim.
        Kalau ini kalah -> buang routernya, pakai N1.
      gate: "router di atas persentil 95 dari distribusi N3"
```

### Uji sanity wajib

| # | Uji | Kalau gagal |
|---|---|---|
| 1 | Sinyal acak murni TIDAK boleh mengalahkan null manapun | bug di null |
| 2 | Sinyal lookahead sengaja HARUS mengalahkan semuanya (§L10) | bug di null |
| 3 | 🔄 Sinyal sintetis IC 0.05 HARUS lolos corong ≥50% (§L11) | **gerbangnya yang rusak** |
| 4 | 🔄 Versi lintas-seksi yang sengaja bocor HARUS menang telak (§L12e) | penyelarasan sesi bermasalah |

**Wajib dilaporkan:** matriks korelasi antar null + jumlah null independen efektif
(eigenvalue matriks korelasi).

---

## Bagian B — Ambang statistik

```yaml
statistics:
  # Ambang CONFIRM TIDAK BERUBAH dari v5.
  t_stat_hurdle_confirm: 3.0

  # 🔄 Ambang bertahap — diturunkan DARI daya partisinya, bukan dipilih (lihat §07)
  t_stat_hurdle_screening:  1.5
  t_stat_hurdle_robustness: 2.0

  effective_n:
    method: lopez_de_prado_uniqueness
    mandatory_for_all_pvalues: true
    assertion_reject_without_weight: true

  hac: newey_west
  clustering: per_instrumen        # untuk pooled t di panel

  fdr: {method: benjamini_hochberg, q: 0.10, n_source: ledger_arah_executed_rows}
  dsr: {threshold: 0.95, n_source: ledger_arah_cumulative}
  pbo: {threshold: 0.50}
  spa: {method: hansen_spa, plus: white_reality_check}
  cpcv: {n_paths_min: 66, purged: true, embargo: true, min_positive_pct: 80}
  bootstrap: {n: 2000, method: block, ci: 0.95, must_exclude_zero: true}
  permutation: {n: 1000, method: block, min_percentile: 95}
  walkforward: {n_windows_min: 24, sign_consistency_pct: 80}
  seed_stability: {n_seeds: 10, must_not_flip: true}
  last_third_significant: true

  # 🔄 diganti (§04 Bagian D)
  min_br_eff_per_year: 100         # menggantikan min_trades_per_year: 300
  min_trades_per_fold: 200

  max_ic_gross_plausible: 0.15

  # 🔄 WAJIB DIUKUR di F0 — menentukan anggaran (§01 B5)
  sd_sharpe_across_trials: WAJIB_DIUKUR
  skew_empiris: WAJIB_DIUKUR
  kurt_empiris: WAJIB_DIUKUR
```

### 🔄 Catatan wajib soal DSR

```yaml
  dsr_catatan_kritis: >
    DSR membandingkan Sharpe kandidat terhadap SR_0 = Sharpe maksimum yang muncul
    dari N trial karena kebetulan. Kalau SR_hat < SR_0, DSR negatif dan
    MEMPERBESAR SAMPEL TIDAK MENOLONG — malah memperburuk (sqrt(T-1) mengalikan
    selisih negatif).

    Satu-satunya pengungkit: (a) turunkan N, (b) turunkan sd_SR antar trial,
    (c) naikkan Sharpe kandidat lewat BR_eff panel.

    v5 gagal di ketiganya sekaligus: N=507, sd_SR tidak pernah diukur,
    K_eff=1 sehingga Sharpe portofolio = Sharpe single.

    Formula SR_0 (Bailey & Lopez de Prado):
      SR_0 = sqrt(Var_SR) * [ (1-gamma)*Phi^-1(1-1/N) + gamma*Phi^-1(1-1/(N*e)) ]
      gamma = 0.5772156649
```

---

## Bagian C — Deduplikasi

```yaml
dedup:
  corr_threshold: 0.90
  vs_same_division: "korelasi PnL >= 0.90 -> alias, TIDAK masuk registry"
  vs_graveyard:     "korelasi PnL >= 0.90 -> auto-kill, TIDAK dijalankan"
  computed_on: partisi_screen
  metrik: "korelasi PnL per-trade, bukan korelasi nilai sinyal"

  # 🔄 baru
  vs_cross_family: >
    Kandidat dari keluarga BERBEDA dengan korelasi PnL >= 0.90 adalah tanda bahwa
    taksonomi keluarganya salah. WAJIB dilaporkan dan salah satu dipindah keluarga
    atau dibuang. Keluarga yang tidak benar-benar berbeda merusak seluruh premis
    multi-strategi (§09).

  prioritas_dedup: >
    Dedup dijalankan SEBELUM kandidat dieksekusi, di partisi screen, dengan
    anggaran diagnostik (ledger_diagnostik). Membuang duplikat SEBELUM dijalankan
    adalah cara termurah menurunkan N — dan N adalah pengungkit terkuat pada DSR.
```

---

## Bagian D — Monte Carlo

```yaml
montecarlo:

  MC1_permutasi:
    tujuan: "Apakah edge-nya nyata atau kebetulan?"
    method: block_permutation
    n: 1000
    catatan: >
      Permutasi acak biasa TIDAK cukup — merusak autokorelasi, null jadi terlalu lemah.
      BUG v5 YANG SUDAH DIPERBAIKI: objek yang dipermutasi salah (permutasi hampa).
      Uji regresi wajib: permutasi harus mengubah hasil. Kalau hasil identik -> bug.
    gate: "hasil kandidat di atas persentil 95"

  MC2_jalur_survival:
    tujuan: "Apakah AKUNNYA SELAMAT? — paling penting untuk uang nyata"
    method: bootstrap_resample_urutan_trade
    n_paths: 10000
    # 🔄 SEKARANG BISA DIJALANKAN — angka aturan akun sudah terisi (§03 B3)
    terapkan_aturan_prop_firm:
      sumber: "§03 B3 — FundedNext Stellar 1-Step (TERKETAT)"
      max_daily_loss_pct: 3.0
      max_total_drawdown_pct: 6.0
      drawdown_type: statis
      profit_target_pct: 10.0
      wajib_juga_dilaporkan: "FTMO 2-Step: daily 5%, maxDD 10% statis"
    hitung:
      - "P(breach) dalam 100 / 250 / 500 trade"
      - "distribusi drawdown maksimum (bukan nilai tunggal)"
      - "waktu ekspektasi sampai target profit"
      - "P(ruin) sebelum target tercapai"
      - "FRONTIER: P(capai target) vs P(breach) per ukuran posisi"
    gate: "P(breach dalam 250 trade) <= 5% pada ukuran posisi yang diusulkan"
    kalau_gagal: >
      Kecilkan ukuran posisi, hitung ulang. Kalau pada ukuran terkecil pun masih gagal
      -> kandidat DITOLAK untuk akun prop firm.

  MC3_eksekusi:
    tujuan: "Apakah tahan slippage?"
    method: "sampel acak dari grid slippage (alpha, beta, latensi) per trade"
    n_paths: 1000
    gate: "expectancy tetap positif di persentil ke-5 dari distribusi hasil"

  MC4_deflated_sharpe:
    tujuan: "Kalahkan Sharpe maksimum yang muncul dari N trial karena kebetulan"
    method: "simulasi expected_max_sharpe di bawah null, N dari ledger_arah"
    gate: "DSR >= 0.95"

  MC5_gangguan_parameter:
    tujuan: "Apakah edge-nya rapuh terhadap setelan?"
    method: "goyang tiap parameter +/-10% dan +/-20%"
    n_combos: 500
    gate: "Tanda expectancy TIDAK boleh berubah. Berubah karena lookback 20->22 = overfit."

  # 🔄 BARU
  MC6_transmitansi_gerbang:
    tujuan: "Apakah gerbang saya sanggup meloloskan edge yang MEMANG ADA? (§L11)"
    method: >
      Suntikkan sinyal sintetis ber-IC terkontrol ke data harga NYATA,
      jalankan lewat seluruh tumpukan gerbang, hitung proporsi lolos.
    ic_grid: [0.03, 0.05, 0.08]
    n_seeds: 500
    gate:
      screening:   ">= 0.80 pada IC 0.05"
      robustness:  ">= 0.70 pada IC 0.05"
      rantai_penuh: ">= 0.50 pada IC 0.05"
    kalau_gagal: >
      BERHENTI. Perbaiki DESAIN gerbang (urutan, tahapan, KILL vs FLAG).
      DILARANG menurunkan ambang CONFIRM.
    kapan: "F1, SEBELUM kandidat pertama. Diulang di F8 setelah registry final."
```

### 🔄 Angka acuan MC2 yang sudah dihitung

Simulasi 30.000 jalur, Sharpe 1.15, 250 trade, ~1.5 trade/hari:

**FundedNext Stellar 1-Step (daily 3%, maxDD 6% statis):**

| risk/trade | P(breach 250) | DD median | DD p95 | vonis |
|---:|---:|---:|---:|---|
| 0.15% | 0.04% | 1.76% | 3.41% | LOLOS |
| **0.25%** | **3.58%** | 2.91% | 5.67% | **LOLOS** |
| 0.50% | 45.42% | 5.73% | 6.57% | GAGAL |
| 1.00% | 98.78% | 6.19% | 7.31% | GAGAL |

**FTMO 2-Step (daily 5%, maxDD 10% statis):**

| risk/trade | P(breach 250) | vonis |
|---:|---:|---|
| 0.25% | 0.07% | LOLOS |
| 0.50% | 8.19% | GAGAL |
| 1.00% | 63.85% | GAGAL |

**Frontier keputusan (FTMO 2-Step, target +10%):**

| risk | Sharpe | P(capai target) | P(breach) | median trade s/d target |
|---:|---:|---:|---:|---:|
| 0.25% | 1.15 | 97.8% | 1.1% | 452 |
| 0.50% | 1.15 | 88.0% | 12.0% | 185 |
| 1.00% | 1.15 | 70.2% | 29.8% | 60 |
| 0.25% | 1.60 | 99.7% | 0.2% | 344 |
| 0.50% | 1.60 | 95.2% | 4.8% | 154 |

> Angka-angka ini **perencanaan**, dihitung dari Sharpe asumsi. MC2 yang mengikat
> WAJIB dijalankan dari distribusi trade NYATA kandidat, bukan dari Gaussian.

---

## Bagian E — Aturan machine learning

```yaml
machine_learning:
  diizinkan:
    [CatBoost, XGBoost, LightGBM, RandomForest, ExtraTrees, Lasso, Ridge,
     ElasticNet, SVM_RBF, KernelRidge, KalmanFilter, MetaLabeling]

  dilarang_sampai_eff_n_5000: [LSTM, Transformer, CNN, deep learning apapun]
  alasan_larangan: "jumlah parameter melampaui anggaran secara ekstrem"

  aturan:
    M1: "Validasi HANYA CPCV purged + embargo. K-fold biasa DILARANG (bocor lewat label tumpang tindih)."
    M2: "Bobot sampel = keunikan label."
    M3: "Feature importance pakai MDA (out-of-sample), BUKAN MDI (in-sample)."
    M4: "Hyperparameter tuning di inner loop nested CV."
    M5: "Setiap kombinasi hyperparameter = 1 baris ledger_arah. Grid 100 = 100 trial."
    M6: "WAJIB mengalahkan baseline linear teregularisasi. Kalau tidak, kompleksitasnya tidak dibenarkan."
    M7: "WAJIB lolos MC5 gangguan parameter."
    M8: "Fitur wajib punya mekanisme. Fitur kotak hitam tanpa hipotesis DILARANG."
    M9: "DILARANG melatih ulang pada holdout, apapun alasannya."

  prioritas: >
    Meta-labeling DULUAN, bukan model arah baru. Meta-labeling memakai sinyal yang
    sudah ada dan hanya memutuskan taruh/tidak — menaikkan presisi TANPA menambah
    trial di ruang arah. Itu properti yang sangat berharga di v6, karena tiap trial
    arah tambahan menaikkan SR_0 untuk semua kandidat lain.

  catatan_v5: >
    Meta-labeling TERBUKTI menaikkan sinyal mentah di run v5. Mekanismenya hidup.
    Yang belum ketemu itu sinyal primernya. Prioritaskan M11.

  # 🔄 peringatan anggaran
  peringatan_grid: >
    M5 berarti grid hyperparameter 100 kombinasi = 100 baris ledger_arah = hampir
    seluruh anggaran v6. Grid ML WAJIB <= 8 kombinasi per model, dan model non-baseline
    hanya dijalankan setelah ada sinyal primer yang lolos tahap 2.
```

---

## Bagian F — Bug yang sudah diperbaiki (jangan terulang)

| bug | dampak kalau tidak ketahuan | uji regresi wajib |
|---|---|---|
| QLIKE meledak ke 10⁸⁰ (floor pembagi) | seluruh peringkat F4 salah | assert QLIKE finite & < 1e6 |
| Permutasi MC1 hampa — objek salah dipermutasi | null terlalu lemah, kandidat sampah menang | assert hasil permutasi ≠ hasil asli |
| Tie-break SL/TP salah di bar M5/M15 | backtest optimis (~350 sinyal terkoreksi) | assert SL menang saat keduanya tersentuh |
| Shape mismatch array | hasil diam-diam salah, tidak crash | assert shape di tiap batas modul |

**Semua hasil F4 ke atas baru valid setelah perbaikan ini.** Uji regresi wajib masuk
`tests/` dan hijau sebelum F2.

---

**Lanjut ke `07_GERBANG_CORONG.md`.**
