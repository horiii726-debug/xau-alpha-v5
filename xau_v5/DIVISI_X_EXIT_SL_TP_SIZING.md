# DIVISI X — EXIT, SL/TP & SIZING

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML di file ini disalin **verbatim** dari sumber. Nol perubahan rumus, nol perubahan grid parameter.

| | |
|---|---|
| **Tipe divisi** | `direction` |
| **Jumlah formula** | 22 |
| **Jumlah varian (baris ledger)** | 114 |
| **Dijalankan di fase** | F5 (prioritas tertinggi) |
| **Gerbang kelulusan** | `gates.direction` — 17 centang, **threshold only, DILARANG argmax/sort/nlargest** (§O5) |
| **Metrik penilaian** | expectancy net bps pada biaya `worst` + MC2 survival |

## Kenapa divisi ini ada

INI DIVISI PALING PENTING. Riset 3 tahun sebelumnya hanya pernah melombakan entry; kapan keluar dan seberapa besar posisi TIDAK PERNAH diuji sekalipun. Temuan intinya: yang membunuh adalah struktur payoff, bukan sinyal.

Catatan asli dari file sumber:

> Riset sebelumnya selama 3 tahun HANYA pernah melombakan entry.
> Kapan keluar dan seberapa besar posisi TIDAK PERNAH diuji sekalipun.
> Padahal temuan intinya: yang membunuh adalah struktur payoff, bukan sinyal.
> Peluang terbesar ada di divisi ini.

## Aturan yang mengikat divisi ini

- **DILARANG memberi peringkat.** `select_champion()` tidak boleh punya `sort` / `argmax` / `idxmax` / `nlargest` / `max()`. Hanya filter terhadap ambang (§O5). Memilih peringkat 1 dari daftar yang semuanya tidak berbeda dari nol = memilih keberuntungan.
- Setiap varian grid = **1 baris ledger**. Panel 1 hipotesis di 25 instrumen tetap **1 baris**.
- Syarat lolos panel: konsisten di **>= 60% instrumen panel**. Yang hanya bekerja di XAUUSD ditandai `SINGLE_ASSET_ONLY` dan dicurigai overfit.
- Semua fitur **wajib kausal** (§L1, §L2). Dilarang centered MA, Savitzky-Golay non-kausal, `filtfilt`, smoothing dua arah.
- Sinyal dari bar `t` dieksekusi **paling cepat di pembukaan bar `t+1`** (§L9).
- Scaler / PCA / normalisasi **di-fit hanya pada fold latih** (§L3). Seleksi fitur **di dalam** loop CV (§L4).
- Semua `doi: NEED_LOOKUP` **wajib diverifikasi di F3**. Dilarang mengarang DOI (§D1).

## Daftar isi divisi

| ID | Varian | n_param | Tier komputasi | Rumus (ringkas) |
|---|---:|---:|---|---|
| `X01_TRIPLE_BARRIER_GRID` 🔒 | 42 | 2 | T1 murah | TP = P0*(1 + k_tp*sigma) ; SL = P0*(1 - k_sl*sigma) ; vertical = max_hold_bar… |
| `X02_ASYMMETRIC_BARRIER_SKEW` | 4 | 2 | T2 sedang | k_tp/k_sl disetel mengikuti skewness realized: ratio = base_ratio * (1 + w*sk… |
| `X03_TIME_DECAY_BARRIER` | 3 | 3 | T2 sedang | k_sl(t) = k_sl0 * exp(-d*t/T) ; k_tp(t) = k_tp0 * exp(-d*t/T) ; t = bar sejak… |
| `X04_EMPIRICAL_QUANTILE_BARRIER` | 6 | 2 | T2 sedang | TP = kuantil_q_atas(MFE distribusi historis) ; SL = kuantil_q_bawah(MAE distr… |
| `X05_VOL_TERCILE_CONDITIONAL_BARRIER` | 4 | 3 | T2 sedang | Pilih (k_sl,k_tp) berbeda per tersile volatilitas: rendah/sedang/tinggi, ters… |
| `X06_VERTICAL_ONLY_BASELINE` 🔒 | 1 | 0 | T1 murah | Keluar HANYA pada batas waktu. Tanpa SL, tanpa TP. return = (C_{t+T} - C_t)/C… |
| `X10_POT_GPD_STOP` | 4 | 3 | T2 sedang | Excess Y = X - u untuk X > u ; F(y) = 1 - (1 + xi*y/beta)^(-1/xi) ; SL = u + … |
| `X11_HILL_TAIL_STOP` | 3 | 2 | T2 sedang | alpha_Hill = [ (1/k) * SUM_{i=1}^{k} ln(X_(i)/X_(k+1)) ]^(-1) ; SL diskalakan… |
| `X12_CVAR_OPTIMAL_STOP` | 3 | 2 | T2 sedang | min_z [ z + (1/((1-beta)*N)) * SUM_j max(L_j - z, 0) ] ; SL = z* hasil optima… |
| `X13_CONDITIONAL_EVT_STOP` | 4 | 3 | T3 mahal | Tahap 1: sigma_t dari model volatilitas ; Tahap 2: GPD pada residual terstand… |
| `X14_SEMIPARAMETRIC_TAIL_STOP` | 3 | 2 | T3 mahal | Badan distribusi dari ECDF empiris, ekor dari hukum pangkat dengan indeks Hil… |
| `X20_SPRT_EXIT` | 4 | 3 | T2 sedang | LLR_t = SUM ln( f1(r_i)/f0(r_i) ) ; keluar saat LLR >= ln((1-b)/a) atau LLR <… |
| `X21_SHIRYAEV_ROBERTS_EXIT` | 3 | 2 | T2 sedang | R_t = (1 + R_{t-1}) * L_t ; L_t = rasio kemungkinan ; keluar saat R_t >= A |
| `X22_QUICKEST_DETECTION_EXIT` | 3 | 2 | T2 sedang | CUSUM: g_t = max(0, g_{t-1} + ln(f1/f0)) ; keluar saat g_t >= h |
| `X23_SELL_AT_ULTIMATE_MAXIMUM` | 3 | 2 | T3 mahal | Keluar saat P_t <= (1-c)*max_{s<=t}(P_s) ; c dari solusi batas bebas dengan p… |
| `X24_FREE_BOUNDARY_EXIT` | 2 | 3 | T3 mahal | (blok multi-baris — lihat detail) |
| `X30_KELLY_FULL` | 3 | 2 | T1 murah | f* = (p*b - q)/b ; p = P(menang), q = 1-p, b = rasio payoff ; SEMUA diestimas… |
| `X31_FRACTIONAL_KELLY` | 4 | 1 | T1 murah | f = lambda * f_Kelly ; f_Kelly = (p*b - q)/b dari X30 ; lambda dipilih dari g… |
| `X32_VOLATILITY_TARGETING` | 3 | 2 | T1 murah | size_t = target_vol / sigma_hat_t ; sigma_hat dari V01_PARKINSON, dibatasi si… |
| `X33_DRAWDOWN_CONSTRAINED_SIZING` 🔒 | 4 | 3 | T1 murah | f_t = f_max * (1 - DD_t/DD_limit)^gamma ; DD_t = drawdown berjalan dari punca… |
| `X34_CDAR_SIZING` | 4 | 3 | T3 mahal | min f sedemikian CDaR_beta(f) <= batas ; CDaR = rata-rata drawdown pada (1-be… |
| `X35_RISK_OF_RUIN_CONSTRAINED` | 4 | 2 | T3 mahal | Pilih f terbesar sedemikian P(ruin sebelum target) <= epsilon, dihitung lewat… |

🔒 = `tidak_boleh_dipangkas_dalam_kondisi_apapun` (§trial_budget.tangga_pemangkasan)

## Peta keluarga

- **Struktur barrier — TP/SL/vertical** — `X01_TRIPLE_BARRIER_GRID`, `X02_ASYMMETRIC_BARRIER_SKEW`, `X03_TIME_DECAY_BARRIER`, `X04_EMPIRICAL_QUANTILE_BARRIER`, `X05_VOL_TERCILE_CONDITIONAL_BARRIER`, `X06_VERTICAL_ONLY_BASELINE`
- **Stop berbasis teori nilai ekstrem (ekor)** — `X10_POT_GPD_STOP`, `X11_HILL_TAIL_STOP`, `X12_CVAR_OPTIMAL_STOP`, `X13_CONDITIONAL_EVT_STOP`, `X14_SEMIPARAMETRIC_TAIL_STOP`
- **Exit berbasis optimal stopping / deteksi tercepat** — `X20_SPRT_EXIT`, `X21_SHIRYAEV_ROBERTS_EXIT`, `X22_QUICKEST_DETECTION_EXIT`, `X23_SELL_AT_ULTIMATE_MAXIMUM`, `X24_FREE_BOUNDARY_EXIT`
- **Position sizing** — `X30_KELLY_FULL`, `X31_FRACTIONAL_KELLY`, `X32_VOLATILITY_TARGETING`, `X33_DRAWDOWN_CONSTRAINED_SIZING`, `X34_CDAR_SIZING`, `X35_RISK_OF_RUIN_CONSTRAINED`

---

## Spesifikasi lengkap (verbatim dari sumber)

### Struktur barrier — TP/SL/vertical

#### `X01_TRIPLE_BARRIER_GRID`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: X01_TRIPLE_BARRIER_GRID
    division: X
    division_type: direction
    formula: "TP = P0*(1 + k_tp*sigma) ; SL = P0*(1 - k_sl*sigma) ; vertical = max_hold_bars ; breakeven_mekanis = k_sl/(k_sl+k_tp)"
    params: {k_sl: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0], k_tp: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]}
    variants: 42
    n_parameters: 2
    data_required: [ohlc]
    catatan: "INI GERBANG PAYOFF (FASE 2). Dijalankan dengan entry ACAK, 3 arm, sebelum sinyal apapun."
    mechanism:
      claim: "Grid k_sl kali k_tp dengan entry acak mengukur apakah distribusi return menyediakan asimetri mekanis sebelum sinyal apapun ikut bicara"
      counterparty: "Peserta yang memilih rasio risk-reward dari kebiasaan populer dan mewarisi kerugian mekanis di setiap trade tanpa menyadarinya"
      decay: "Titik impas mekanis adalah sifat distribusi return, bukan pola yang bisa diarbitrase habis"
    provenance:
      citation: "Lopez de Prado, Advances in Financial Machine Learning, Wiley, 2018 (monograf akademik)"
      doi: NEED_LOOKUP
      peer_reviewed: true
      catatan_sumber: "Monograf, bukan jurnal. Cari paper jurnal setara di FASE 3; kalau tidak ada, tandai SOURCE_IS_MONOGRAPH."
```

#### `X02_ASYMMETRIC_BARRIER_SKEW`

*Tier komputasi: T2 sedang*

```yaml
  - id: X02_ASYMMETRIC_BARRIER_SKEW
    division: X
    division_type: direction
    formula: "k_tp/k_sl disetel mengikuti skewness realized: ratio = base_ratio * (1 + w*skew_realized)"
    params: {base_ratio: [1.5, 2.0], w: [0.5, 1.0]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Barrier yang tidak simetris disetel mengikuti kemiringan distribusi return terukur sehingga titik impas mekanis digeser ke arah yang didukung data"
      counterparty: "Peserta yang memakai rasio simetris pada distribusi yang jelas miring dan menanggung ketidaksesuaian struktural di setiap trade"
      decay: "Kemiringan distribusi berubah antar rezim sehingga setelan yang benar hari ini harus diukur ulang"
    provenance:
      citation: "Amaya, Christoffersen, Jacobs & Vasquez, Does realized skewness predict the cross-section of equity returns, Journal of Financial Economics, 2015"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X03_TIME_DECAY_BARRIER`

*Tier komputasi: T2 sedang*

```yaml
  - id: X03_TIME_DECAY_BARRIER
    division: X
    division_type: direction
    formula: "k_sl(t) = k_sl0 * exp(-d*t/T) ; k_tp(t) = k_tp0 * exp(-d*t/T) ; t = bar sejak entry, T = max_hold"
    params: {d: [0.3, 0.6, 1.0], base: [k1_5_2_5]}
    variants: 3
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Barrier yang menyempit seiring waktu mengakui bahwa informasi entry meluruh sehingga posisi tua dituntut membuktikan diri lebih cepat"
      counterparty: "Peserta yang memakai barrier tetap dan menahan posisi tua dengan toleransi risiko sama padahal edge entry-nya sudah habis"
      decay: "Laju peluruhan informasi berbeda tiap kondisi sehingga bentuk penyempitan harus diukur ulang"
    provenance:
      citation: "Lopez de Prado, Advances in Financial Machine Learning, Wiley, 2018"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X04_EMPIRICAL_QUANTILE_BARRIER`

*Tier komputasi: T2 sedang*

```yaml
  - id: X04_EMPIRICAL_QUANTILE_BARRIER
    division: X
    division_type: direction
    formula: "TP = kuantil_q_atas(MFE distribusi historis) ; SL = kuantil_q_bawah(MAE distribusi historis) ; dihitung pada jendela LATIH saja"
    params: {q_tp: [0.60, 0.70, 0.80], q_sl: [0.20, 0.30]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Barrier ditempatkan pada kuantil empiris distribusi gerak bukan pada kelipatan volatilitas sehingga tidak mengasumsikan bentuk distribusi apapun"
      counterparty: "Peserta yang menempatkan stop pada kelipatan deviasi standar dan tersapu jauh lebih sering daripada perkiraan asumsi normal"
      decay: "Kuantil empiris harus diperbarui dengan data baru sehingga selalu tertinggal sedikit dari perubahan rezim"
    provenance:
      citation: "Embrechts, Kluppelberg & Mikosch, Modelling Extremal Events for Insurance and Finance, Springer, 1997 (monograf)"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X05_VOL_TERCILE_CONDITIONAL_BARRIER`

*Tier komputasi: T2 sedang*

```yaml
  - id: X05_VOL_TERCILE_CONDITIONAL_BARRIER
    division: X
    division_type: direction
    formula: "Pilih (k_sl,k_tp) berbeda per tersile volatilitas: rendah/sedang/tinggi, tersile dihitung pada jendela LATIH"
    params: {tercile_window: [288, 576], ratio_set: [tight, wide]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Konfigurasi barrier berbeda per rezim volatilitas menguji apakah asimetri mekanis hanya ada di sebagian rezim dan bukan di seluruhnya"
      counterparty: "Peserta yang memakai satu konfigurasi untuk semua kondisi dan menyerahkan keunggulan di rezim tempat konfigurasi lain jauh lebih baik"
      decay: "Pembagian per tersile menambah jumlah trial berlipat sehingga ambang statistiknya naik dan hanya efek besar yang lolos"
    provenance:
      citation: "Lopez de Prado, Advances in Financial Machine Learning, Wiley, 2018"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X06_VERTICAL_ONLY_BASELINE`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: X06_VERTICAL_ONLY_BASELINE
    division: X
    division_type: direction
    formula: "Keluar HANYA pada batas waktu. Tanpa SL, tanpa TP. return = (C_{t+T} - C_t)/C_t"
    params: {none: [default]}
    variants: 1
    n_parameters: 0
    data_required: [ohlc]
    mechanism:
      claim: "Keluar hanya pada batas waktu mengukur payoff dasar horizon murni sehingga jadi pembanding wajar untuk semua konfigurasi barrier lain"
      counterparty: "Peserta yang memasang stop dan target tanpa pernah membandingkannya terhadap keluar-waktu-saja dan tidak tahu apakah barriernya menambah nilai"
      decay: "Baseline selalu tersedia bagi semua orang, fungsinya sebagai pembanding permanen"
    provenance:
      citation: "Baseline konstruksi, tidak memerlukan sitasi"
      doi: NOT_APPLICABLE
      peer_reviewed: true
```

### Stop berbasis teori nilai ekstrem (ekor)

#### `X10_POT_GPD_STOP`

*Tier komputasi: T2 sedang*

```yaml
  - id: X10_POT_GPD_STOP
    division: X
    division_type: direction
    formula: "Excess Y = X - u untuk X > u ; F(y) = 1 - (1 + xi*y/beta)^(-1/xi) ; SL = u + (beta/xi)*[ (n/(Nu*(1-p)))^xi - 1 ]"
    params: {u_percentile: [90, 95], p_stop: [0.95, 0.99]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Distribusi Pareto tergeneralisasi memodelkan ekor gerak harga secara langsung sehingga jarak stop ditetapkan pada kuantil ekor yang sebenarnya"
      counterparty: "Peserta yang menetapkan stop dari kelipatan volatilitas normal dan tersapu jauh lebih sering daripada perkiraannya di pasar berekor tebal"
      decay: "Ketebalan ekor bergerak dengan ketidakpastian makro sehingga parameter ekor harus diestimasi ulang"
    provenance:
      citation: "Pickands, Statistical inference using extreme order statistics, Annals of Statistics, 1975"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X11_HILL_TAIL_STOP`

*Tier komputasi: T2 sedang*

```yaml
  - id: X11_HILL_TAIL_STOP
    division: X
    division_type: direction
    formula: "alpha_Hill = [ (1/k) * SUM_{i=1}^{k} ln(X_(i)/X_(k+1)) ]^(-1) ; SL diskalakan terbalik terhadap alpha"
    params: {k_frac: [0.05, 0.10, 0.15]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Indeks ekor Hill memberi satu angka yang meringkas ketebalan ekor sehingga jarak stop bisa diskalakan langsung terhadap ketebalan terukur"
      counterparty: "Peserta yang memakai jarak stop tetap dalam kelipatan volatilitas dan tidak menyesuaikannya saat ekor menebal menjelang kejadian besar"
      decay: "Estimator Hill sensitif terhadap jumlah statistik urutan yang dipakai sehingga hasilnya berderau dan butuh pemantauan"
    provenance:
      citation: "Hill, A simple general approach to inference about the tail of a distribution, Annals of Statistics, 1975"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X12_CVAR_OPTIMAL_STOP`

*Tier komputasi: T2 sedang*

```yaml
  - id: X12_CVAR_OPTIMAL_STOP
    division: X
    division_type: direction
    formula: "min_z [ z + (1/((1-beta)*N)) * SUM_j max(L_j - z, 0) ] ; SL = z* hasil optimasi"
    params: {beta: [0.90, 0.95, 0.99]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Optimasi conditional value at risk meminimalkan kerugian rata-rata di ekor terburuk sehingga penempatan stop dioptimalkan terhadap besarnya kerugian bukan hanya peluangnya"
      counterparty: "Peserta yang mengoptimalkan peluang menang dan mengabaikan besarnya kerugian saat kalah sehingga hancur oleh sedikit kejadian ekor"
      decay: "Optimasi CVaR menuntut sampel ekor yang cukup sehingga estimasinya rapuh justru di bagian yang paling menentukan"
    provenance:
      citation: "Rockafellar & Uryasev, Optimization of conditional value-at-risk, Journal of Risk, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X13_CONDITIONAL_EVT_STOP`

*Tier komputasi: T3 mahal*

```yaml
  - id: X13_CONDITIONAL_EVT_STOP
    division: X
    division_type: direction
    formula: "Tahap 1: sigma_t dari model volatilitas ; Tahap 2: GPD pada residual terstandar z_t ; SL_t = sigma_t * q_p(z)"
    params: {vol_model: [V01_PARKINSON, V12_EWMA], p: [0.95, 0.99]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Menggabungkan model volatilitas dengan model ekor membuat jarak stop menyesuaikan kondisi volatilitas terkini bukan rata-rata sejarah"
      counterparty: "Peserta yang memakai kuantil ekor tanpa syarat dan memasang stop terlalu jauh di periode tenang serta terlalu dekat di periode bergejolak"
      decay: "Model dua lapis menambah parameter dan risiko salah spesifikasi sehingga keunggulannya harus dibuktikan melebihi kompleksitasnya"
    provenance:
      citation: "McNeil & Frey, Estimation of tail-related risk measures for heteroscedastic financial time series an extreme value approach, Journal of Empirical Finance, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X14_SEMIPARAMETRIC_TAIL_STOP`

*Tier komputasi: T3 mahal*

```yaml
  - id: X14_SEMIPARAMETRIC_TAIL_STOP
    division: X
    division_type: direction
    formula: "Badan distribusi dari ECDF empiris, ekor dari hukum pangkat dengan indeks Hill, disambung pada ambang u"
    params: {u_percentile: [90, 95, 97]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Pendekatan semiparametrik memakai data empiris di badan distribusi dan model ekor di ujungnya sehingga tidak memaksakan satu bentuk untuk seluruh distribusi"
      counterparty: "Peserta yang memakai satu distribusi parametrik untuk badan dan ekor sekaligus dan pasti salah di salah satu bagian"
      decay: "Titik sambung antara badan dan ekor harus dipilih dan pilihannya mempengaruhi hasil"
    provenance:
      citation: "Danielsson & de Vries, Value-at-risk and extreme returns, Journal of Empirical Finance, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Exit berbasis optimal stopping / deteksi tercepat

#### `X20_SPRT_EXIT`

*Tier komputasi: T2 sedang*

```yaml
  - id: X20_SPRT_EXIT
    division: X
    division_type: direction
    formula: "LLR_t = SUM ln( f1(r_i)/f0(r_i) ) ; keluar saat LLR >= ln((1-b)/a) atau LLR <= ln(b/(1-a))"
    params: {alpha_err: [0.05, 0.10], beta_err: [0.10, 0.20]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Uji rasio kemungkinan berurutan keluar segera setelah bukti cukup untuk memutuskan sehingga jumlah bar yang dibutuhkan minimal untuk tingkat keyakinan tertentu"
      counterparty: "Peserta yang menunggu jumlah bar tetap sebelum menilai posisi dan menahan posisi rugi lebih lama daripada yang dibutuhkan bukti"
      decay: "Optimalitas berlaku pada hipotesis sederhana yang jarang persis menggambarkan pasar sehingga marginnya tipis tapi arahnya benar"
    provenance:
      citation: "Wald, Sequential tests of statistical hypotheses, Annals of Mathematical Statistics, 1945"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X21_SHIRYAEV_ROBERTS_EXIT`

*Tier komputasi: T2 sedang*

```yaml
  - id: X21_SHIRYAEV_ROBERTS_EXIT
    division: X
    division_type: direction
    formula: "R_t = (1 + R_{t-1}) * L_t ; L_t = rasio kemungkinan ; keluar saat R_t >= A"
    params: {A: [10, 30, 100]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Prosedur Shiryaev-Roberts optimal mendeteksi perubahan secepat mungkin pada laju alarm palsu tertentu sehingga memberi batas teoritis kecepatan keluar"
      counterparty: "Peserta yang memakai aturan keluar ad hoc dan membayar entah dengan keterlambatan entah dengan alarm palsu lebih banyak dari yang perlu"
      decay: "Pertukaran antara keterlambatan dan alarm palsu adalah batas informasi yang tidak bisa dilanggar siapapun"
    provenance:
      citation: "Shiryaev, On optimum methods in quickest detection problems, Theory of Probability and Its Applications, 1963"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X22_QUICKEST_DETECTION_EXIT`

*Tier komputasi: T2 sedang*

```yaml
  - id: X22_QUICKEST_DETECTION_EXIT
    division: X
    division_type: direction
    formula: "CUSUM: g_t = max(0, g_{t-1} + ln(f1/f0)) ; keluar saat g_t >= h"
    params: {h: [3, 5, 8]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Prosedur CUSUM optimal secara minimax untuk deteksi perubahan tercepat sehingga keluar posisi terjadi segera setelah rezim berbalik"
      counterparty: "Peserta yang keluar berdasarkan aturan tetap dan membayar entah dengan keterlambatan entah dengan keluar prematur"
      decay: "Batas teoritis kecepatan deteksi tidak berubah oleh perilaku pasar"
    provenance:
      citation: "Moustakides, Optimal stopping times for detecting changes in distributions, Annals of Statistics, 1986"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X23_SELL_AT_ULTIMATE_MAXIMUM`

*Tier komputasi: T3 mahal*

```yaml
  - id: X23_SELL_AT_ULTIMATE_MAXIMUM
    division: X
    division_type: direction
    formula: "Keluar saat P_t <= (1-c)*max_{s<=t}(P_s) ; c dari solusi batas bebas dengan parameter drift-vol terestimasi"
    params: {c: [0.20, 0.35, 0.50]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Masalah menjual pada maksimum akhir memberi aturan optimal untuk keluar sedekat mungkin ke puncak tanpa mengetahui puncaknya di depan"
      counterparty: "Peserta yang menahan posisi menunggu puncak sempurna dan sistematis keluar setelah sebagian besar keuntungan kembali ke pasar"
      decay: "Aturan optimal bergantung parameter drift dan volatilitas yang harus diestimasi sehingga galat estimasi memakan sebagian keunggulannya"
    provenance:
      citation: "Du Toit & Peskir, Selling a stock at the ultimate maximum, Annals of Applied Probability, 2009"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X24_FREE_BOUNDARY_EXIT`

*Tier komputasi: T3 mahal*

```yaml
  - id: X24_FREE_BOUNDARY_EXIT
    division: X
    division_type: direction
    formula: >
      Aproksimasi numerik batas bebas untuk berhenti optimal pada Brownian
      bermean-drift. Langkah konkret:
      (1) estimasi mu_hat dan sigma_hat dari jendela LATIH;
      (2) diskretkan sisa waktu ke t = 0..T bar dan keuntungan berjalan ke grid;
      (3) selesaikan mundur (backward induction) V(t,x) = max( x , E[V(t+1, x+dx)] )
          dengan dx ~ N(mu_hat, sigma_hat^2);
      (4) b(t) = x terkecil yang membuat berhenti lebih baik daripada lanjut;
      (5) keluar saat keuntungan berjalan menyentuh b(t).
      Backward induction hanya memakai parameter dari fold LATIH (§L3).
    params: {drift_est_window: [96, 288], grid_points: [200]}
    variants: 2
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Solusi batas bebas memberi aturan keluar optimal sebagai fungsi keadaan bukan sebagai level tetap sehingga titik keluar bergerak mengikuti kondisi"
      counterparty: "Peserta yang memakai level keluar tetap dan keluar terlalu cepat di kondisi yang seharusnya ditahan atau sebaliknya"
      decay: "Solusi optimal bergantung asumsi proses yang tidak pernah persis benar sehingga selalu ada jarak antara teori dan praktik"
    provenance:
      citation: "Peskir & Shiryaev, Optimal Stopping and Free-Boundary Problems, Birkhauser, 2006 (monograf)"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Position sizing

#### `X30_KELLY_FULL`

*Tier komputasi: T1 murah*

```yaml
  - id: X30_KELLY_FULL
    division: X
    division_type: direction
    formula: "f* = (p*b - q)/b ; p = P(menang), q = 1-p, b = rasio payoff ; SEMUA diestimasi dari fold LATIH saja"
    params: {est_window: [288, 576, 1152]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Kriteria Kelly memaksimalkan laju pertumbuhan majemuk jangka panjang sehingga memberi ukuran posisi yang optimal secara matematis untuk peluang dan payoff tertentu"
      counterparty: "Peserta yang menetapkan ukuran posisi dari kenyamanan dan sistematis terlalu besar saat edge kecil atau terlalu kecil saat edge besar"
      decay: "Kelly menuntut estimasi peluang dan payoff yang akurat; pada sampel kecil galat estimasi besar sehingga penerapannya harus dikecilkan"
    provenance:
      citation: "Kelly, A new interpretation of information rate, Bell System Technical Journal, 1956"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X31_FRACTIONAL_KELLY`

*Tier komputasi: T1 murah*

```yaml
  - id: X31_FRACTIONAL_KELLY
    division: X
    division_type: direction
    formula: "f = lambda * f_Kelly ; f_Kelly = (p*b - q)/b dari X30 ; lambda dipilih dari grid, BUKAN dioptimalkan ke hasil"
    params: {lambda: [0.10, 0.25, 0.33, 0.50]}
    variants: 4
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Kelly pecahan mengurangi ukuran posisi proporsional sehingga menukar sedikit laju pertumbuhan dengan penurunan besar pada risiko kehilangan modal"
      counterparty: "Peserta yang memakai Kelly penuh dengan parameter berderau dan mengalami penurunan modal jauh melebihi toleransinya"
      decay: "Pecahan yang tepat bergantung ketidakpastian estimasi yang menyusut seiring bertambahnya data"
    provenance:
      citation: "MacLean, Ziemba & Blazenko, Growth versus security in dynamic investment analysis, Management Science, 1992"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X32_VOLATILITY_TARGETING`

*Tier komputasi: T1 murah*

```yaml
  - id: X32_VOLATILITY_TARGETING
    division: X
    division_type: direction
    formula: "size_t = target_vol / sigma_hat_t ; sigma_hat dari V01_PARKINSON, dibatasi size_max"
    params: {target_vol_bps: [50, 100, 150], size_cap: [3.0]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Menskalakan eksposur berbanding terbalik dengan volatilitas terprediksi menstabilkan risiko per trade sehingga hasil tidak didominasi beberapa periode bergejolak"
      counterparty: "Peserta yang memakai ukuran lot tetap dan mengambil risiko berlipat di periode bergejolak tanpa imbalan sepadan"
      decay: "Manfaatnya berasal dari prediktabilitas volatilitas yang memang kuat dan bertahan, ini termasuk edge paling tahan lama yang ada"
    provenance:
      citation: "Fleming, Kirby & Ostdiek, The economic value of volatility timing, Journal of Finance, 2001"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X33_DRAWDOWN_CONSTRAINED_SIZING`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: X33_DRAWDOWN_CONSTRAINED_SIZING
    division: X
    division_type: direction
    formula: "f_t = f_max * (1 - DD_t/DD_limit)^gamma ; DD_t = drawdown berjalan dari puncak ekuitas"
    params: {gamma: [1.0, 2.0], f_max: [0.5, 1.0]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    catatan: "WAJIB — ini bentuk matematis persis dari aturan drawdown prop firm."
    mechanism:
      claim: "Optimasi pertumbuhan di bawah kendala penurunan modal maksimum memberi bentuk matematis persis untuk aturan prop firm sehingga sizing dioptimalkan pada kendala yang benar-benar mengikat"
      counterparty: "Peserta yang mengoptimalkan pertumbuhan tanpa kendala penurunan modal dan kehilangan akun sebelum sempat menunjukkan edge jangka panjangnya"
      decay: "Kendala penurunan modal ditetapkan penyedia dana dan tidak bisa dihilangkan sehingga solusi optimalnya selalu relevan"
    provenance:
      citation: "Grossman & Zhou, Optimal investment strategies for controlling drawdowns, Mathematical Finance, 1993"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X34_CDAR_SIZING`

*Tier komputasi: T3 mahal*

```yaml
  - id: X34_CDAR_SIZING
    division: X
    division_type: direction
    formula: "min f sedemikian CDaR_beta(f) <= batas ; CDaR = rata-rata drawdown pada (1-beta) skenario terburuk"
    params: {beta: [0.90, 0.95], dd_limit_pct: [5, 8]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Conditional drawdown at risk mengukur rata-rata penurunan modal terburuk sehingga sizing dioptimalkan terhadap ukuran risiko yang persis dipakai penyedia dana untuk mengevaluasi"
      counterparty: "Peserta yang mengoptimalkan volatilitas atau value at risk padahal yang menentukan kelangsungan akunnya adalah penurunan modal maksimum"
      decay: "Ukuran risiko berbasis penurunan modal bergantung jalur sehingga estimasinya butuh banyak jalur simulasi dan jarang dilakukan pelaku ritel"
    provenance:
      citation: "Chekhlov, Uryasev & Zabarankin, Drawdown measure in portfolio optimization, International Journal of Theoretical and Applied Finance, 2005"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `X35_RISK_OF_RUIN_CONSTRAINED`

*Tier komputasi: T3 mahal*

```yaml
  - id: X35_RISK_OF_RUIN_CONSTRAINED
    division: X
    division_type: direction
    formula: "Pilih f terbesar sedemikian P(ruin sebelum target) <= epsilon, dihitung lewat simulasi jalur MC2"
    params: {epsilon: [0.01, 0.05], target_R: [10, 20]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Memaksimalkan peluang bertahan sebelum memaksimalkan pertumbuhan memberi urutan tujuan yang benar untuk akun berkendala penarikan modal keras"
      counterparty: "Peserta yang memaksimalkan ekspektasi keuntungan tanpa kendala bertahan dan menghadapi risiko kehancuran jauh lebih besar daripada yang disadarinya"
      decay: "Kendala bertahan berasal dari struktur kontrak pendanaan yang tidak berubah karena strategi apapun"
    provenance:
      citation: "Browne, Survival and growth with a liability optimal portfolio strategies in continuous time, Mathematics of Operations Research, 1997"
      doi: NEED_LOOKUP
      peer_reviewed: true
```
