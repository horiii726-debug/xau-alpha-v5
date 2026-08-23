# DIVISI E — ENTRY / ARAH

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML di file ini disalin **verbatim** dari sumber. Nol perubahan rumus, nol perubahan grid parameter.

| | |
|---|---|
| **Tipe divisi** | `direction` |
| **Jumlah formula** | 56 |
| **Jumlah varian (baris ledger)** | 209 |
| **Dijalankan di fase** | F6 |
| **Gerbang kelulusan** | `gates.direction` — 17 centang, **threshold only, DILARANG argmax/sort/nlargest** (§O5) |
| **Metrik penilaian** | expectancy net bps pada biaya `worst`, panel pooled t dengan clustering per instrumen |

## Kenapa divisi ini ada

SINYAL ARAH. Divisi terbesar (56 formula / 209 varian) dan karena itu yang paling banyak dipangkas kalau K_eff kecil. Tidak ada peringkat: lolos ambang atau mati.

Catatan asli dari file sumber:

> TIDAK ADA PERINGKAT. Lolos ambang atau mati (§O5).
> Semua matematika umum, bukan khusus emas. Semua kausal.

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
| `E01_INTRADAY_MOMENTUM` | 4 | 1 | T1 murah | sig = sign( (C_t - C_{t-L}) / C_{t-L} ) ; L = lookback bar |
| `E02_VOL_SCALED_MOMENTUM` | 6 | 2 | T1 murah | z = (C_t - C_{t-L}) / (sigma_t * sqrt(L)) ; sig = sign(z) * 1(\|z\| > theta) |
| `E03_SHORT_HORIZON_REVERSAL` | 6 | 2 | T1 murah | z = (C_t - C_{t-L}) / (sigma_t*sqrt(L)) ; sig = -sign(z) * 1(\|z\| > theta) |
| `E04_SESSION_GAP_CONTINUATION` | 3 | 1 | T1 murah | gap = (O_t - C_{t-1})/C_{t-1} setelah jeda pasar ; sig = sign(gap) * 1(\|gap\… |
| `E10_VARIANCE_RATIO_LM` | 4 | 1 | T1 murah | VR(q) = Var(r_t(q)) / (q * Var(r_t(1))) ; sig = sign(VR-1) untuk tren, -sign(… |
| `E11_VARIANCE_RATIO_WRIGHT` | 3 | 1 | T1 murah | VR berbasis peringkat/tanda: R1(q), S1(q) dengan distribusi eksak sampel kecil |
| `E12_AUTOMATIC_VARIANCE_RATIO` | 2 | 1 | T1 murah | VR dengan pemilihan horizon otomatis lewat kriteria data-driven, menghilangka… |
| `E20_HURST_RS` | 3 | 1 | T1 murah | R/S(n) = (max_k(SUM(x_i - xbar)) - min_k(SUM(x_i - xbar))) / s_n ; H dari slo… |
| `E21_MODIFIED_RS_LO` | 2 | 2 | T2 sedang | R/S dengan penyebut HAC Newey-West: s_n(q) = s^2 + 2*SUM_j w_j(q)*gamma_j |
| `E22_DFA_ALPHA` | 6 | 2 | T1 murah | Y(k)=SUM(x_i - xbar) ; F(n)=sqrt(mean((Y - Y_fit_n)^2)) ; alpha dari slope ln… |
| `E23_MFDFA_WIDTH` | 2 | 3 | T2 sedang | F_q(n) untuk q dalam [-5,5] ; h(q) dari slope ; lebar spektrum = max(alpha)-m… |
| `E24_HIGUCHI_FD` | 6 | 2 | T2 sedang | L(k) = mean over m of [ SUM\|x(m+ik)-x(m+(i-1)k)\| * (N-1)/(floor((N-m)/k)*k^… |
| `E25_KATZ_FD` | 3 | 1 | T1 murah | D = log10(n) / (log10(n) + log10(d/L)) ; L = panjang total jalur, d = diamete… |
| `E26_PETROSIAN_FD` | 3 | 1 | T1 murah | D = log10(n) / (log10(n) + log10(n/(n + 0.4*N_delta))) ; N_delta = jumlah per… |
| `E27_RANGE_ROUGHNESS_RATIO` | 3 | 1 | T1 murah | rho = RRV / RV ; RRV = realized range variation, RV = realized variance close… |
| `E30_SHANNON_ENTROPY_SIGN` | 3 | 2 | T1 murah | H = -SUM_k p_k*log2(p_k) ; p_k dari frekuensi pola tanda return panjang m |
| `E31_APPROXIMATE_ENTROPY` | 4 | 3 | T2 sedang | ApEn(m,r,N) = phi_m(r) - phi_{m+1}(r) ; phi_m(r) = (N-m+1)^-1 SUM ln C_i^m(r) |
| `E32_SAMPLE_ENTROPY` | 4 | 3 | T2 sedang | SampEn(m,r,N) = -ln(A/B) ; A = pasangan cocok panjang m+1, B = panjang m, tan… |
| `E33_PERMUTATION_ENTROPY` | 9 | 2 | T2 sedang | PE = -SUM_pi p(pi)*ln p(pi) ; pi = pola ordinal urutan panjang d, dinormalisa… |
| `E34_WEIGHTED_PERMUTATION_ENTROPY` | 4 | 2 | T2 sedang | WPE = -SUM_pi p_w(pi)*ln p_w(pi) ; p_w berbobot varians tiap jendela ordinal |
| `E35_DISPERSION_ENTROPY` | 8 | 3 | T2 sedang | Petakan x ke c kelas lewat NCDF, bentuk pola dispersi panjang m, DE = -SUM p*… |
| `E36_LEMPEL_ZIV_COMPLEXITY` | 3 | 1 | T1 murah | Simbolkan deret jadi biner (naik/turun), hitung jumlah substring baru saat pa… |
| `E40_LYAPUNOV_ROSENSTEIN` | 4 | 4 | T3 mahal | Sematkan dengan (m, tau) ; d_j(i) = jarak tetangga terdekat setelah i langkah… |
| `E41_RQA_DETERMINISM` | 2 | 4 | T3 mahal | R_ij = Theta(eps - \|\|x_i - x_j\|\|) ; DET = SUM_{l>=lmin} l*P(l) / SUM_l l*… |
| `E42_RQA_LAMINARITY` | 2 | 4 | T3 mahal | LAM = SUM_{v>=vmin} v*P(v) / SUM_v v*P(v) ; P(v) = distribusi panjang garis v… |
| `E43_CORRELATION_DIMENSION` | 4 | 3 | T3 mahal | C(eps) = (2/(N(N-1))) * SUM_{i<j} Theta(eps - \|\|x_i-x_j\|\|) ; D2 dari slop… |
| `E44_BDS_TEST` | 4 | 3 | T3 mahal | W_m(eps) = sqrt(N)*(C_m(eps) - C_1(eps)^m)/sigma_m(eps) |
| `E45_ZERO_ONE_TEST_CHAOS` | 2 | 2 | T3 mahal | p_c(n)=SUM x_j cos(jc) ; M_c(n)=mean((p_c(j+n)-p_c(j))^2) ; K = korelasi(M_c,… |
| `E50_FFT_DOMINANT_PERIOD` | 3 | 1 | T1 murah | P(f) = \|FFT(x_detrended)\|^2 ; periode dominan = 1/argmax_f P(f) dalam pita … |
| `E51_HILBERT_INSTANT_PHASE` | 4 | 2 | T2 sedang | z(t) = x(t) + i*Hilbert(x(t)) ; phi(t) = arctan(Im/Re) ; sinyal dari kuadran … |
| `E52_HILBERT_INSTANT_FREQUENCY` | 4 | 2 | T2 sedang | omega(t) = d(phi)/dt, diaproksimasi beda maju kausal ; fitur = perubahan omega |
| `E53_WAVELET_SCALE_ENERGY` | 4 | 2 | T2 sedang | E_j = SUM_k \|W_{j,k}\|^2 ; rasio energi skala pendek terhadap skala panjang |
| `E54_SPECTRAL_ENTROPY` | 3 | 1 | T1 murah | p_f = P(f)/SUM P(f) ; SE = -SUM p_f*ln(p_f) / ln(N_f) |
| `E55_SSA_COMPONENT_SHARE` | 4 | 3 | T2 sedang | Bentuk matriks trajektori, SVD, pangsa nilai singular pertama = lambda_1 / SU… |
| `E60_DRIFT_BURST_TSTAT` | 4 | 2 | T1 murah | T_t = sqrt(h_n) * mu_hat_t / sigma_hat_t ; mu_hat = drift kernel-weighted, si… |
| `E61_LEE_MYKLAND_JUMP` | 4 | 2 | T1 murah | L_i = r_i / sigma_hat_i ; sigma_hat dari bipower jendela K ; lompatan jika \|… |
| `E62_BIPOWER_JUMP_RATIO` | 3 | 1 | T1 murah | J = max(0, (RV - BV)/RV) ; RV = realized variance, BV = bipower variation |
| `E63_SIGNED_JUMP_VARIATION` | 3 | 1 | T1 murah | SJV = RS_plus - RS_minus ; sinyal dari tanda dan besar SJV |
| `E64_REALIZED_SKEWNESS` | 3 | 1 | T1 murah | RSkew = sqrt(N) * SUM r_i^3 / RV^{3/2} |
| `E65_REALIZED_KURTOSIS` | 3 | 1 | T1 murah | RKurt = N * SUM r_i^4 / RV^2 |
| `E70_MANN_KENDALL` | 3 | 1 | T1 murah | S = SUM_{i<j} sign(x_j - x_i) ; Z = (S - sign(S))/sqrt(Var(S)) |
| `E71_COX_STUART` | 3 | 1 | T1 murah | Bandingkan x_i dengan x_{i+n/2}, hitung tanda, uji binomial |
| `E72_THEIL_SEN_SLOPE` | 4 | 1 | T2 sedang | beta = median over i<j of (x_j - x_i)/(j - i) |
| `E73_RUNS_TEST` | 3 | 1 | T1 murah | R = jumlah runtun tanda ; Z = (R - E[R])/sd(R) dengan E[R]=2*n1*n2/n + 1 |
| `E74_BARTELS_RANK_TEST` | 3 | 1 | T1 murah | RVN = SUM (R_i - R_{i+1})^2 / SUM (R_i - Rbar)^2 ; R = peringkat |
| `E80_QUANTILE_REGRESSION_SLOPE` | 6 | 2 | T1 murah | min_b SUM rho_tau(y_i - b*t_i) ; rho_tau(u) = u*(tau - 1(u<0)) |
| `E81_HUBER_SLOPE` | 3 | 2 | T1 murah | min_b SUM rho_c(y_i - b*t_i) ; rho_c kuadratik untuk \|u\|<=c, linier di luar |
| `E82_SIEGEL_REPEATED_MEDIAN` | 3 | 1 | T2 sedang | beta = median_i( median_{j!=i} (x_j - x_i)/(j - i) ) |
| `E83_RANSAC_SLOPE` | 2 | 3 | T2 sedang | Iterasi: sampel acak minimal, fit, hitung inlier dalam toleransi t, ambil mod… |
| `E90_CUSUM_CHANGEPOINT` | 4 | 2 | T1 murah | S_t^+ = max(0, S_{t-1}^+ + (x_t - mu0 - k)) ; alarm saat S_t^+ > h |
| `E91_PELT_SEGMENTATION` | 4 | 2 | T2 sedang | min SUM_{i} [ C(y_{t_{i-1}+1:t_i}) + beta ] dengan pemangkasan ; fitur = umur… |
| `E92_BOCPD_RUNLENGTH` | 3 | 3 | T2 sedang | P(r_t \| x_1:t) rekursif dengan fungsi hazard H(r) ; fitur = E[r_t] = umur re… |
| `E93_MATRIX_PROFILE_DISCORD` | 3 | 2 | T2 sedang | MP_i = min_j d(S_i, S_j) untuk \|i-j\| > exclusion ; discord = argmax MP |
| `E95_MUTUAL_INFORMATION_LAG` | 4 | 2 | T3 mahal | I(X_t ; X_{t-L}) estimator k-nearest-neighbour Kraskov |
| `E96_TRANSFER_ENTROPY_SELF` | 4 | 3 | T3 mahal | TE = SUM p(x_{t+1}, x_t^k) * log[ p(x_{t+1}\|x_t^k) / p(x_{t+1}\|x_t^{k-1}) ] |
| `E97_DISTANCE_CORRELATION` | 6 | 2 | T3 mahal | dCor(X,Y) = dCov(X,Y)/sqrt(dVar(X)*dVar(Y)) ; nol jika dan hanya jika indepen… |

🔒 = `tidak_boleh_dipangkas_dalam_kondisi_apapun` (§trial_budget.tangga_pemangkasan)

## Peta keluarga

- **Momentum & reversal jangka pendek** — `E01_INTRADAY_MOMENTUM`, `E02_VOL_SCALED_MOMENTUM`, `E03_SHORT_HORIZON_REVERSAL`, `E04_SESSION_GAP_CONTINUATION`
- **Uji rasio varians (pengganti EMA crossover)** — `E10_VARIANCE_RATIO_LM`, `E11_VARIANCE_RATIO_WRIGHT`, `E12_AUTOMATIC_VARIANCE_RATIO`
- **Memori panjang & dimensi fraktal** — `E20_HURST_RS`, `E21_MODIFIED_RS_LO`, `E22_DFA_ALPHA`, `E23_MFDFA_WIDTH`, `E24_HIGUCHI_FD`, `E25_KATZ_FD`, `E26_PETROSIAN_FD`, `E27_RANGE_ROUGHNESS_RATIO`
- **Entropi & kompleksitas** — `E30_SHANNON_ENTROPY_SIGN`, `E31_APPROXIMATE_ENTROPY`, `E32_SAMPLE_ENTROPY`, `E33_PERMUTATION_ENTROPY`, `E34_WEIGHTED_PERMUTATION_ENTROPY`, `E35_DISPERSION_ENTROPY`, `E36_LEMPEL_ZIV_COMPLEXITY`
- **Nonlinearitas & chaos (semua tier-3)** — `E40_LYAPUNOV_ROSENSTEIN`, `E41_RQA_DETERMINISM`, `E42_RQA_LAMINARITY`, `E43_CORRELATION_DIMENSION`, `E44_BDS_TEST`, `E45_ZERO_ONE_TEST_CHAOS`
- **Spektral, siklus & fase** — `E50_FFT_DOMINANT_PERIOD`, `E51_HILBERT_INSTANT_PHASE`, `E52_HILBERT_INSTANT_FREQUENCY`, `E53_WAVELET_SCALE_ENERGY`, `E54_SPECTRAL_ENTROPY`, `E55_SSA_COMPONENT_SHARE`
- **Lompatan, drift burst & momen realized** — `E60_DRIFT_BURST_TSTAT`, `E61_LEE_MYKLAND_JUMP`, `E62_BIPOWER_JUMP_RATIO`, `E63_SIGNED_JUMP_VARIATION`, `E64_REALIZED_SKEWNESS`, `E65_REALIZED_KURTOSIS`
- **Uji tren nonparametrik (pengganti RSI/Stochastic)** — `E70_MANN_KENDALL`, `E71_COX_STUART`, `E72_THEIL_SEN_SLOPE`, `E73_RUNS_TEST`, `E74_BARTELS_RANK_TEST`
- **Estimator kemiringan robust** — `E80_QUANTILE_REGRESSION_SLOPE`, `E81_HUBER_SLOPE`, `E82_SIEGEL_REPEATED_MEDIAN`, `E83_RANSAC_SLOPE`
- **Deteksi patahan rezim** — `E90_CUSUM_CHANGEPOINT`, `E91_PELT_SEGMENTATION`, `E92_BOCPD_RUNLENGTH`, `E93_MATRIX_PROFILE_DISCORD`
- **Ketergantungan & informasi (tier-3)** — `E95_MUTUAL_INFORMATION_LAG`, `E96_TRANSFER_ENTROPY_SELF`, `E97_DISTANCE_CORRELATION`

---

## Spesifikasi lengkap (verbatim dari sumber)

### Momentum & reversal jangka pendek

#### `E01_INTRADAY_MOMENTUM`

*Tier komputasi: T1 murah*

```yaml
  - id: E01_INTRADAY_MOMENTUM
    division: E
    division_type: direction
    formula: "sig = sign( (C_t - C_{t-L}) / C_{t-L} ) ; L = lookback bar"
    params: {L: [6, 12, 24, 48]}
    variants: 4
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Return interval awal memprediksi arah sisa horizon karena aliran order yang tertunda dieksekusi bertahap"
      counterparty: "Peserta yang harus menyelesaikan eksekusi besar dalam jendela waktu tetap dan rela membayar kelanjutan harga demi kepastian selesai"
      decay: "Pemecahan order adalah keharusan biaya bagi pihak besar, jejaknya tidak bisa dihilangkan tanpa membayar dampak harga lebih besar"
    provenance:
      citation: "Gao, Han, Li & Zhou, Market intraday momentum, Journal of Financial Economics, 2018"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E02_VOL_SCALED_MOMENTUM`

*Tier komputasi: T1 murah*

```yaml
  - id: E02_VOL_SCALED_MOMENTUM
    division: E
    division_type: direction
    formula: "z = (C_t - C_{t-L}) / (sigma_t * sqrt(L)) ; sig = sign(z) * 1(|z| > theta)"
    params: {L: [6, 12, 24], theta: [0.5, 1.0]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Momentum yang dinormalisasi volatilitas menahan sinyal saat range melebar sehingga hanya gerak yang besar relatif terhadap deraunya yang dianggap informatif"
      counterparty: "Peserta yang memakai ambang absolut dan sistematis salah kalibrasi ketika rezim volatilitas berubah"
      decay: "Normalisasi menggeser ambang tiap rezim sehingga tidak ada level tetap yang bisa dihafal pasar"
    provenance:
      citation: "Barroso & Santa-Clara, Momentum has its moments, Journal of Financial Economics, 2015"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E03_SHORT_HORIZON_REVERSAL`

*Tier komputasi: T1 murah*

```yaml
  - id: E03_SHORT_HORIZON_REVERSAL
    division: E
    division_type: direction
    formula: "z = (C_t - C_{t-L}) / (sigma_t*sqrt(L)) ; sig = -sign(z) * 1(|z| > theta)"
    params: {L: [3, 6, 12], theta: [1.5, 2.0]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Gerak yang terlalu besar relatif volatilitasnya sebagian berbalik karena sebagian gerak itu adalah premi likuiditas bukan informasi"
      counterparty: "Peserta yang menuntut eksekusi segera dan membayar konsesi harga kepada penyedia likuiditas yang bersedia menampung"
      decay: "Kompensasi bagi penampung inventori adalah biaya modal nyata sehingga pembalikan sebagian tidak hilang selama modal tidak gratis"
    provenance:
      citation: "Chordia, Roll & Subrahmanyam, Evidence on the speed of convergence to market efficiency, Journal of Financial Economics, 2005"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E04_SESSION_GAP_CONTINUATION`

*Tier komputasi: T1 murah*

```yaml
  - id: E04_SESSION_GAP_CONTINUATION
    division: E
    division_type: direction
    formula: "gap = (O_t - C_{t-1})/C_{t-1} setelah jeda pasar ; sig = sign(gap) * 1(|gap| > theta*sigma)"
    params: {theta: [0.5, 1.0, 1.5]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Gap harga saat pembukaan kembali berlanjut arahnya karena informasi yang menumpuk selama jeda belum terserap penuh di bar pertama"
      counterparty: "Pembuat pasar yang membuka kuotasi lebar setelah jeda dan tetap salah harga karena tidak punya harga referensi yang likuid"
      decay: "Jeda perdagangan adalah fitur venue yang tidak bisa dihapus sehingga penumpukan informasi selalu terulang"
    provenance:
      citation: "Berkman, Koch, Tuttle & Zhang, Paying attention overnight returns and the hidden cost of buying at the open, Journal of Financial and Quantitative Analysis, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Uji rasio varians (pengganti EMA crossover)

#### `E10_VARIANCE_RATIO_LM`

*Tier komputasi: T1 murah*

```yaml
  - id: E10_VARIANCE_RATIO_LM
    division: E
    division_type: direction
    formula: "VR(q) = Var(r_t(q)) / (q * Var(r_t(1))) ; sig = sign(VR-1) untuk tren, -sign(VR-1) untuk balik arah"
    params: {q: [2, 4, 8, 16]}
    variants: 4
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Rasio varians menguji apakah varians tumbuh linier terhadap horizon dan penyimpangannya mengukur kelanjutan atau pembalikan arah dengan distribusi uji yang diketahui"
      counterparty: "Peserta yang mengukur efisiensi gerak dengan rasio buatan tanpa distribusi uji dan tidak bisa membedakan hasilnya dari kebetulan"
      decay: "Penyimpangan dari jalan acak muncul dan hilang mengikuti siklus likuiditas, tidak pernah hilang permanen tapi juga tidak konstan"
    provenance:
      citation: "Lo & MacKinlay, Stock market prices do not follow random walks evidence from a simple specification test, Review of Financial Studies, 1988"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E11_VARIANCE_RATIO_WRIGHT`

*Tier komputasi: T1 murah*

```yaml
  - id: E11_VARIANCE_RATIO_WRIGHT
    division: E
    division_type: direction
    formula: "VR berbasis peringkat/tanda: R1(q), S1(q) dengan distribusi eksak sampel kecil"
    params: {q: [2, 4, 8]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Rasio varians berbasis peringkat dan tanda punya distribusi eksak sehingga valid di sampel kecil tempat versi asimptotik menyesatkan"
      counterparty: "Peserta yang memakai uji asimptotik pada sampel kecil dan menyimpulkan ada struktur padahal itu kegagalan aproksimasi distribusi"
      decay: "Validitas sampel kecil justru paling dibutuhkan pada effective N rendah seperti divisi ini"
    provenance:
      citation: "Wright, Alternative variance-ratio tests using ranks and signs, Journal of Business and Economic Statistics, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E12_AUTOMATIC_VARIANCE_RATIO`

*Tier komputasi: T1 murah*

```yaml
  - id: E12_AUTOMATIC_VARIANCE_RATIO
    division: E
    division_type: direction
    formula: "VR dengan pemilihan horizon otomatis lewat kriteria data-driven, menghilangkan kebebasan memilih q"
    params: {kernel: [bartlett, quadratic_spectral]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Pemilihan horizon otomatis menghilangkan kebebasan memilih lag secara sembarang sehingga mengurangi ruang overfit pada uji jalan acak"
      counterparty: "Peserta yang mencoba banyak lag lalu melaporkan yang paling signifikan tanpa mengoreksi jumlah percobaannya"
      decay: "Pemilihan otomatis membuat hasilnya lebih jujur tapi juga lebih lemah sehingga kurang menarik bagi pengejar angka bagus"
    provenance:
      citation: "Choi, Testing the random walk hypothesis for real exchange rates, Journal of Applied Econometrics, 1999"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Memori panjang & dimensi fraktal

#### `E20_HURST_RS`

*Tier komputasi: T1 murah*

```yaml
  - id: E20_HURST_RS
    division: E
    division_type: direction
    formula: "R/S(n) = (max_k(SUM(x_i - xbar)) - min_k(SUM(x_i - xbar))) / s_n ; H dari slope ln(R/S) vs ln(n)"
    params: {window: [96, 288, 576]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Eksponen Hurst di atas setengah menandakan jalur harga sedang persisten sehingga kelanjutan arah lebih mungkin daripada pembalikan"
      counterparty: "Peserta yang memakai aturan pembalikan tetap dan terus melawan arah selama fase persisten berlangsung"
      decay: "Nilai Hurst berayun antar rezim sehingga strategi statis yang dikalibrasi satu rezim gagal di rezim berikutnya"
    provenance:
      citation: "Hurst, Long-term storage capacity of reservoirs, Transactions of the American Society of Civil Engineers, 1951"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E21_MODIFIED_RS_LO`

*Tier komputasi: T2 sedang*

```yaml
  - id: E21_MODIFIED_RS_LO
    division: E
    division_type: direction
    formula: "R/S dengan penyebut HAC Newey-West: s_n(q) = s^2 + 2*SUM_j w_j(q)*gamma_j"
    params: {window: [288, 576], q_lag: [auto]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Rescaled range terkoreksi memisahkan memori jangka panjang asli dari autokorelasi jangka pendek biasa"
      counterparty: "Peserta yang salah membaca autokorelasi jangka pendek sebagai tren dan menahan posisi lebih lama daripada yang dibenarkan datanya"
      decay: "Koreksi memerlukan pemilihan lag pemotongan yang bergantung data sehingga tidak bisa disalin tanpa mengulang estimasinya"
    provenance:
      citation: "Lo, Long-term memory in stock market prices, Econometrica, 1991"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E22_DFA_ALPHA`

*Tier komputasi: T1 murah*

```yaml
  - id: E22_DFA_ALPHA
    division: E
    division_type: direction
    formula: "Y(k)=SUM(x_i - xbar) ; F(n)=sqrt(mean((Y - Y_fit_n)^2)) ; alpha dari slope ln F(n) vs ln n"
    params: {window: [96, 288, 576], poly_order: [1, 2]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Eksponen detrended fluctuation analysis mengukur persistensi jalur tanpa terganggu tren lokal sehingga lebih stabil daripada rescaled range biasa"
      counterparty: "Peserta yang mengukur tren dengan regresi polos dan tertipu oleh tren semu pada jendela pendek"
      decay: "Estimasi butuh jendela panjang sehingga sinyalnya bergerak lambat dan kurang menarik bagi arbitrase berfrekuensi tinggi"
    provenance:
      citation: "Peng, Buldyrev, Havlin, Simons, Stanley & Goldberger, Mosaic organization of DNA nucleotides, Physical Review E, 1994"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E23_MFDFA_WIDTH`

*Tier komputasi: T2 sedang*

```yaml
  - id: E23_MFDFA_WIDTH
    division: E
    division_type: direction
    formula: "F_q(n) untuk q dalam [-5,5] ; h(q) dari slope ; lebar spektrum = max(alpha)-min(alpha) dari transformasi Legendre"
    params: {window: [288, 576]}
    variants: 2
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Lebar spektrum multifraktal menandakan heterogenitas skala aktivitas dan penyempitannya menandakan pasar sedang didominasi satu jenis peserta"
      counterparty: "Peserta yang mengasumsikan satu skala volatilitas tunggal dan salah menetapkan ukuran posisi saat struktur skalanya berubah"
      decay: "Multifraktalitas berasal dari campuran horizon peserta yang selalu berubah"
    provenance:
      citation: "Kantelhardt, Zschiegner, Koscielny-Bunde, Havlin, Bunde & Stanley, Multifractal detrended fluctuation analysis of nonstationary time series, Physica A, 2002"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E24_HIGUCHI_FD`

*Tier komputasi: T2 sedang*

```yaml
  - id: E24_HIGUCHI_FD
    division: E
    division_type: direction
    formula: "L(k) = mean over m of [ SUM|x(m+ik)-x(m+(i-1)k)| * (N-1)/(floor((N-m)/k)*k^2) ] ; D dari slope ln L(k) vs ln(1/k)"
    params: {window: [48, 96, 288], k_max: [8, 16]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Dimensi fraktal Higuchi mengukur kekasaran jalur langsung di domain waktu dan nilai rendah menandakan jalur yang lebih terarah"
      counterparty: "Peserta yang memakai ambang volatilitas tetap dan tidak membedakan gerak besar yang terarah dari gerak besar yang berputar"
      decay: "Kekasaran jalur ditentukan campuran arus eksekusi yang berubah tiap sesi"
    provenance:
      citation: "Higuchi, Approach to an irregular time series on the basis of the fractal theory, Physica D, 1988"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E25_KATZ_FD`

*Tier komputasi: T1 murah*

```yaml
  - id: E25_KATZ_FD
    division: E
    division_type: direction
    formula: "D = log10(n) / (log10(n) + log10(d/L)) ; L = panjang total jalur, d = diameter, n = L/rata_langkah"
    params: {window: [48, 96, 288]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Dimensi fraktal Katz menormalisasi panjang jalur terhadap diameternya sehingga membedakan gerak efisien dari gerak berputar dengan satu angka"
      counterparty: "Peserta yang mengejar setiap ayunan kecil dan membayar biaya transaksi berulang pada jalur yang berputar di tempat"
      decay: "Rasio ini bergerak dengan komposisi likuiditas harian yang tidak dikendalikan pelaku manapun"
    provenance:
      citation: "Katz, Fractals and the analysis of waveforms, Computers in Biology and Medicine, 1988"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E26_PETROSIAN_FD`

*Tier komputasi: T1 murah*

```yaml
  - id: E26_PETROSIAN_FD
    division: E
    division_type: direction
    formula: "D = log10(n) / (log10(n) + log10(n/(n + 0.4*N_delta))) ; N_delta = jumlah pergantian tanda selisih"
    params: {window: [24, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Dimensi fraktal Petrosian menghitung pergantian tanda selisih sehingga menangkap kekasaran jalur dengan biaya komputasi sangat rendah"
      counterparty: "Peserta yang menunda keputusan sampai estimator berat selesai dan kehilangan bagian awal gerak yang paling menguntungkan"
      decay: "Ukuran berbasis tanda tahan terhadap perubahan skala harga sehingga tetap bermakna walau level emas berubah dua kali lipat"
    provenance:
      citation: "Petrosian, Kolmogorov complexity of finite sequences and recognition of different preictal EEG patterns, Proceedings of the IEEE Symposium on Computer-Based Medical Systems, 1995"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E27_RANGE_ROUGHNESS_RATIO`

*Tier komputasi: T1 murah*

```yaml
  - id: E27_RANGE_ROUGHNESS_RATIO
    division: E
    division_type: direction
    formula: "rho = RRV / RV ; RRV = realized range variation, RV = realized variance close-to-close"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Rasio antara variasi berbasis range dan berbasis penutupan mengukur seberapa banyak gerak terjadi di dalam bar dan menandakan kekasaran jalur"
      counterparty: "Peserta yang hanya melihat harga penutupan dan tidak menyadari biaya slippage lebih tinggi saat gerak intra-bar membesar"
      decay: "Informasi range membutuhkan data intra-bar yang tidak semua pelaku simpan"
    provenance:
      citation: "Christensen & Podolskij, Realized range-based estimation of integrated variance, Journal of Econometrics, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Entropi & kompleksitas

#### `E30_SHANNON_ENTROPY_SIGN`

*Tier komputasi: T1 murah*

```yaml
  - id: E30_SHANNON_ENTROPY_SIGN
    division: E
    division_type: direction
    formula: "H = -SUM_k p_k*log2(p_k) ; p_k dari frekuensi pola tanda return panjang m"
    params: {window: [48, 96, 288], m: [3]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Entropi urutan tanda return menghilangkan pengaruh besaran sehingga hanya struktur arah yang diukur dan tidak tertutup lonjakan volatilitas"
      counterparty: "Peserta yang membaca lonjakan besaran sebagai sinyal arah dan salah masuk pada gerak besar yang tandanya acak"
      decay: "Ukuran berbasis tanda kebal terhadap perubahan level harga sehingga tetap berlaku lintas rezim"
    provenance:
      citation: "Shannon, A mathematical theory of communication, Bell System Technical Journal, 1948"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E31_APPROXIMATE_ENTROPY`

*Tier komputasi: T2 sedang*

```yaml
  - id: E31_APPROXIMATE_ENTROPY
    division: E
    division_type: direction
    formula: "ApEn(m,r,N) = phi_m(r) - phi_{m+1}(r) ; phi_m(r) = (N-m+1)^-1 SUM ln C_i^m(r)"
    params: {m: [2], r_mult: [0.15, 0.20], window: [96, 288]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Approximate entropy rendah menandakan pola berulang di jalur harga yang menyisakan keteraturan yang bisa diprediksi pada horizon pendek"
      counterparty: "Peserta yang mengasumsikan harga jalan acak murni dan tidak mengambil sisi berlawanan saat keteraturan sedang tinggi"
      decay: "Keteraturan muncul dari eksekusi terjadwal pihak besar yang tidak bisa berhenti hanya karena terdeteksi"
    provenance:
      citation: "Pincus, Approximate entropy as a measure of system complexity, Proceedings of the National Academy of Sciences, 1991"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E32_SAMPLE_ENTROPY`

*Tier komputasi: T2 sedang*

```yaml
  - id: E32_SAMPLE_ENTROPY
    division: E
    division_type: direction
    formula: "SampEn(m,r,N) = -ln(A/B) ; A = pasangan cocok panjang m+1, B = panjang m, tanpa self-match"
    params: {m: [2, 3], r_mult: [0.20], window: [96, 288]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Sample entropy memperbaiki bias pencocokan diri pada approximate entropy sehingga estimasi keteraturan lebih andal di sampel pendek"
      counterparty: "Peserta yang memakai estimator berbias dan menyimpulkan ada keteraturan padahal itu artefak metode"
      decay: "Perbedaan bias baru terasa di sampel pendek yang justru paling relevan untuk scalping"
    provenance:
      citation: "Richman & Moorman, Physiological time-series analysis using approximate entropy and sample entropy, American Journal of Physiology Heart and Circulatory Physiology, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E33_PERMUTATION_ENTROPY`

*Tier komputasi: T2 sedang*

```yaml
  - id: E33_PERMUTATION_ENTROPY
    division: E
    division_type: direction
    formula: "PE = -SUM_pi p(pi)*ln p(pi) ; pi = pola ordinal urutan panjang d, dinormalisasi ln(d!)"
    params: {d: [3, 4, 5], window: [48, 96, 288]}
    variants: 9
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Entropi permutasi mengukur keragaman pola urutan naik turun sehingga tahan terhadap outlier dan langsung membaca struktur ordinal jalur"
      counterparty: "Peserta yang estimasi strukturnya rusak oleh satu bar ekstrem setelah rilis berita dan mundur dari pasar terlalu cepat"
      decay: "Struktur ordinal berubah tiap sesi mengikuti komposisi peserta"
    provenance:
      citation: "Bandt & Pompe, Permutation entropy a natural complexity measure for time series, Physical Review Letters, 2002"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E34_WEIGHTED_PERMUTATION_ENTROPY`

*Tier komputasi: T2 sedang*

```yaml
  - id: E34_WEIGHTED_PERMUTATION_ENTROPY
    division: E
    division_type: direction
    formula: "WPE = -SUM_pi p_w(pi)*ln p_w(pi) ; p_w berbobot varians tiap jendela ordinal"
    params: {d: [3, 4], window: [96, 288]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Entropi permutasi berbobot amplitudo memisahkan pola ordinal yang terjadi pada gerak besar dari pola yang hanya muncul di riak kecil"
      counterparty: "Peserta yang memperlakukan semua pola sama pentingnya dan bereaksi terhadap pola yang terjadi di gerak tidak signifikan"
      decay: "Pembobotan amplitudo membuat sinyal bergantung skala volatilitas yang berubah tiap rezim"
    provenance:
      citation: "Fadlallah, Chen, Keil & Principe, Weighted-permutation entropy a complexity measure for time series incorporating amplitude information, Physical Review E, 2013"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E35_DISPERSION_ENTROPY`

*Tier komputasi: T2 sedang*

```yaml
  - id: E35_DISPERSION_ENTROPY
    division: E
    division_type: direction
    formula: "Petakan x ke c kelas lewat NCDF, bentuk pola dispersi panjang m, DE = -SUM p*ln p"
    params: {c: [4, 6], m: [2, 3], window: [96, 288]}
    variants: 8
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Entropi dispersi memetakan nilai ke kelas berbasis kuantil sebelum menghitung pola sehingga stabil terhadap perubahan skala harga jangka panjang"
      counterparty: "Peserta yang memakai ambang absolut dalam dolar dan kalibrasinya rusak ketika level emas bergerak jauh"
      decay: "Pemetaan kuantil menuntut jendela referensi yang harus diperbarui"
    provenance:
      citation: "Rostaghi & Azami, Dispersion entropy a measure for time-series analysis, IEEE Signal Processing Letters, 2016"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E36_LEMPEL_ZIV_COMPLEXITY`

*Tier komputasi: T1 murah*

```yaml
  - id: E36_LEMPEL_ZIV_COMPLEXITY
    division: E
    division_type: direction
    formula: "Simbolkan deret jadi biner (naik/turun), hitung jumlah substring baru saat parsing kiri ke kanan, normalisasi n/log2(n)"
    params: {window: [96, 288, 576]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Kompleksitas Lempel-Ziv menghitung jumlah pola baru dalam urutan tersimbolkan sehingga langsung mengukur seberapa terkompresi jalur harga"
      counterparty: "Peserta yang memperlakukan semua periode sama acaknya dan tidak menambah ukuran posisi saat jalur sedang sangat terstruktur"
      decay: "Kompresibilitas naik saat satu peserta besar mendominasi arus dan turun begitu eksekusinya selesai"
    provenance:
      citation: "Lempel & Ziv, On the complexity of finite sequences, IEEE Transactions on Information Theory, 1976"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Nonlinearitas & chaos (semua tier-3)

#### `E40_LYAPUNOV_ROSENSTEIN`

*Tier komputasi: T3 mahal*

```yaml
  - id: E40_LYAPUNOV_ROSENSTEIN
    division: E
    division_type: direction
    formula: "Sematkan dengan (m, tau) ; d_j(i) = jarak tetangga terdekat setelah i langkah ; lambda dari slope ln d_j(i) vs i"
    params: {m: [3, 5], tau: [1, 3], window: [288]}
    variants: 4
    n_parameters: 4
    data_required: [ohlc]
    mechanism:
      claim: "Eksponen Lyapunov terbesar mengukur kecepatan divergensi lintasan berdekatan sehingga menandakan seberapa cepat prediktabilitas jangka pendek habis"
      counterparty: "Peserta yang memasang horizon target tetap tanpa memeriksa berapa lama informasi bertahan dan menahan posisi melewati batas prediktabilitasnya"
      decay: "Batas prediktabilitas adalah sifat dinamika pasar itu sendiri, hanya bisa dipetakan bukan dihapus"
    provenance:
      citation: "Rosenstein, Collins & De Luca, A practical method for calculating largest Lyapunov exponents from small data sets, Physica D, 1993"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E41_RQA_DETERMINISM`

*Tier komputasi: T3 mahal*

```yaml
  - id: E41_RQA_DETERMINISM
    division: E
    division_type: direction
    formula: "R_ij = Theta(eps - ||x_i - x_j||) ; DET = SUM_{l>=lmin} l*P(l) / SUM_l l*P(l)"
    params: {eps_pct: [10, 15], m: [3], lmin: [2], window: [288]}
    variants: 2
    n_parameters: 4
    data_required: [ohlc]
    mechanism:
      claim: "Determinisme dari plot rekurensi menghitung proporsi titik rekuren yang membentuk garis diagonal sehingga membedakan struktur deterministik dari rekurensi acak"
      counterparty: "Peserta yang menganggap semua pengulangan harga sama bermaknanya dan bereaksi pada rekurensi yang sebenarnya kebetulan"
      decay: "Struktur deterministik jangka pendek berasal dari algoritma eksekusi yang berjalan dan berubah tiap kali algoritmanya diganti"
    provenance:
      citation: "Marwan, Romano, Thiel & Kurths, Recurrence plots for the analysis of complex systems, Physics Reports, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E42_RQA_LAMINARITY`

*Tier komputasi: T3 mahal*

```yaml
  - id: E42_RQA_LAMINARITY
    division: E
    division_type: direction
    formula: "LAM = SUM_{v>=vmin} v*P(v) / SUM_v v*P(v) ; P(v) = distribusi panjang garis vertikal"
    params: {eps_pct: [10, 15], m: [3], window: [288]}
    variants: 2
    n_parameters: 4
    data_required: [ohlc]
    mechanism:
      claim: "Laminaritas mengukur proporsi titik rekuren yang membentuk garis vertikal sehingga menandai keadaan pasar yang macet di satu level harga"
      counterparty: "Peserta yang memasang order menembus level dan tersapu berulang kali di wilayah macet sebelum arah sebenarnya muncul"
      decay: "Keadaan macet terjadi karena order besar bertahan di satu level dan berakhir begitu order itu terisi penuh atau ditarik"
    provenance:
      citation: "Marwan, Romano, Thiel & Kurths, Recurrence plots for the analysis of complex systems, Physics Reports, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E43_CORRELATION_DIMENSION`

*Tier komputasi: T3 mahal*

```yaml
  - id: E43_CORRELATION_DIMENSION
    division: E
    division_type: direction
    formula: "C(eps) = (2/(N(N-1))) * SUM_{i<j} Theta(eps - ||x_i-x_j||) ; D2 dari slope ln C(eps) vs ln eps"
    params: {m: [3, 5], window: [288, 576]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Dimensi korelasi memperkirakan jumlah derajat kebebasan efektif yang menggerakkan harga dan nilai rendah menandakan sedikit faktor sedang mendominasi"
      counterparty: "Peserta yang mengasumsikan banyak faktor bekerja bersamaan dan melakukan diversifikasi sinyal justru saat pasar digerakkan satu faktor"
      decay: "Jumlah faktor dominan berubah mengikuti siklus makro yang tidak bisa dipengaruhi pelaku intraday"
    provenance:
      citation: "Grassberger & Procaccia, Characterization of strange attractors, Physical Review Letters, 1983"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E44_BDS_TEST`

*Tier komputasi: T3 mahal*

```yaml
  - id: E44_BDS_TEST
    division: E
    division_type: direction
    formula: "W_m(eps) = sqrt(N)*(C_m(eps) - C_1(eps)^m)/sigma_m(eps)"
    params: {m: [2, 3], eps_pct: [50, 75]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Statistik BDS menguji apakah sisa deret masih punya ketergantungan nonlinier setelah struktur linier dibuang sehingga menandai ada informasi tersisa"
      counterparty: "Peserta yang hanya membuang struktur linier dan menyimpulkan sisanya derau padahal masih ada ketergantungan nonlinier"
      decay: "Ketergantungan nonlinier sulit dieksploitasi tanpa model eksplisit sehingga bertahan lebih lama daripada struktur linier"
    provenance:
      citation: "Brock, Dechert, Scheinkman & LeBaron, A test for independence based on the correlation dimension, Econometric Reviews, 1996"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E45_ZERO_ONE_TEST_CHAOS`

*Tier komputasi: T3 mahal*

```yaml
  - id: E45_ZERO_ONE_TEST_CHAOS
    division: E
    division_type: direction
    formula: "p_c(n)=SUM x_j cos(jc) ; M_c(n)=mean((p_c(j+n)-p_c(j))^2) ; K = korelasi(M_c, n)"
    params: {window: [288, 576]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Uji nol satu membedakan dinamika teratur dari kacau langsung dari deret tanpa perlu rekonstruksi ruang fase sehingga jauh lebih sedikit parameternya"
      counterparty: "Peserta yang harus menyetel banyak parameter rekonstruksi dan hasilnya berubah-ubah mengikuti setelan bukan mengikuti data"
      decay: "Sedikit parameter berarti sedikit ruang overfit sehingga edge kecil tapi lebih mungkin bertahan keluar sampel"
    provenance:
      citation: "Gottwald & Melbourne, A new test for chaos in deterministic systems, Proceedings of the Royal Society A, 2004"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Spektral, siklus & fase

#### `E50_FFT_DOMINANT_PERIOD`

*Tier komputasi: T1 murah*

```yaml
  - id: E50_FFT_DOMINANT_PERIOD
    division: E
    division_type: direction
    formula: "P(f) = |FFT(x_detrended)|^2 ; periode dominan = 1/argmax_f P(f) dalam pita yang diizinkan"
    params: {window: [96, 288, 576]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Periode dominan memberi skala waktu siklus yang sedang aktif sehingga horizon posisi bisa disesuaikan dengan ritme pasar saat itu"
      counterparty: "Peserta yang memakai horizon tetap dan sistematis keluar di titik yang salah ketika ritme dominan pasar berubah panjangnya"
      decay: "Periode dominan berpindah mengikuti jam aktif peserta besar"
    provenance:
      citation: "Cooley & Tukey, An algorithm for the machine calculation of complex Fourier series, Mathematics of Computation, 1965"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E51_HILBERT_INSTANT_PHASE`

*Tier komputasi: T2 sedang*

```yaml
  - id: E51_HILBERT_INSTANT_PHASE
    division: E
    division_type: direction
    formula: "z(t) = x(t) + i*Hilbert(x(t)) ; phi(t) = arctan(Im/Re) ; sinyal dari kuadran fase"
    params: {bandpass_lo: [8, 16], bandpass_hi: [64, 128]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    catatan: "Transformasi Hilbert WAJIB versi kausal (analytic signal dari filter kausal). Versi non-kausal DILARANG (§L2)."
    mechanism:
      claim: "Fase sesaat menunjukkan posisi pasar di dalam siklus yang sedang berjalan sehingga arah kelanjutan bisa dibaca dari fasenya"
      counterparty: "Peserta yang masuk posisi di fase akhir siklus dan menanggung pembalikan yang sudah bisa dibaca dari fase saat masuk"
      decay: "Fase hanya bermakna selama siklus benar-benar ada dan jadi derau saat pasar bertren, sinyalnya membatasi dirinya sendiri"
    provenance:
      citation: "Gabor, Theory of communication, Journal of the Institution of Electrical Engineers, 1946"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E52_HILBERT_INSTANT_FREQUENCY`

*Tier komputasi: T2 sedang*

```yaml
  - id: E52_HILBERT_INSTANT_FREQUENCY
    division: E
    division_type: direction
    formula: "omega(t) = d(phi)/dt, diaproksimasi beda maju kausal ; fitur = perubahan omega"
    params: {bandpass_lo: [8, 16], bandpass_hi: [64, 128]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Frekuensi sesaat mengukur seberapa cepat fase berubah sehingga pemendekan siklus bisa terdeteksi sebelum terlihat pada harga"
      counterparty: "Peserta yang memakai panjang siklus tetap dan terlambat menyesuaikan ketika ritme pasar memendek mendekati rilis data"
      decay: "Perubahan frekuensi digerakkan jadwal informasi eksternal yang tidak bisa diperlambat pelaku pasar"
    provenance:
      citation: "Gabor, Theory of communication, Journal of the Institution of Electrical Engineers, 1946"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E53_WAVELET_SCALE_ENERGY`

*Tier komputasi: T2 sedang*

```yaml
  - id: E53_WAVELET_SCALE_ENERGY
    division: E
    division_type: direction
    formula: "E_j = SUM_k |W_{j,k}|^2 ; rasio energi skala pendek terhadap skala panjang"
    params: {wavelet: [db4, sym4], levels: [4, 5]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Rasio energi antar skala wavelet mengukur pergeseran aktivitas dari skala cepat ke skala lambat yang mendahului perubahan karakter jalur harga"
      counterparty: "Peserta yang menyetel indikator pada satu skala tetap dan tertinggal ketika aktivitas berpindah ke skala lain"
      decay: "Perpindahan skala aktivitas digerakkan masuknya jenis peserta baru ke pasar"
    provenance:
      citation: "Mallat, A theory for multiresolution signal decomposition the wavelet representation, IEEE Transactions on Pattern Analysis and Machine Intelligence, 1989"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E54_SPECTRAL_ENTROPY`

*Tier komputasi: T1 murah*

```yaml
  - id: E54_SPECTRAL_ENTROPY
    division: E
    division_type: direction
    formula: "p_f = P(f)/SUM P(f) ; SE = -SUM p_f*ln(p_f) / ln(N_f)"
    params: {window: [96, 288, 576]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Entropi spektral mengukur seberapa merata energi tersebar lintas frekuensi dan nilai rendah menandakan pasar digerakkan satu ritme dominan"
      counterparty: "Peserta yang memasang strategi kontra tren saat energi terkonsentrasi di satu ritme dan terus melawan gerak yang terstruktur"
      decay: "Konsentrasi spektral berumur pendek dan pecah ketika arus penggeraknya selesai"
    provenance:
      citation: "Inouye, Shinosaki, Sakamoto, Toi, Ukai, Iyama, Katsuda & Hirano, Quantification of EEG irregularity by use of the entropy of the power spectrum, Electroencephalography and Clinical Neurophysiology, 1991"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E55_SSA_COMPONENT_SHARE`

*Tier komputasi: T2 sedang*

```yaml
  - id: E55_SSA_COMPONENT_SHARE
    division: E
    division_type: direction
    formula: "Bentuk matriks trajektori, SVD, pangsa nilai singular pertama = lambda_1 / SUM lambda_i"
    params: {window_L: [24, 48], embed: [96, 288]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Pangsa nilai singular pertama mengukur seberapa besar gerak bisa dijelaskan satu komponen tunggal sehingga menandai dominasi satu penggerak"
      counterparty: "Peserta yang membangun posisi berbasis banyak sinyal independen justru ketika seluruh gerak digerakkan satu faktor tunggal"
      decay: "Dominasi satu faktor berasal dari kejadian makro yang tidak bisa diciptakan atau dihilangkan pelaku intraday"
    provenance:
      citation: "Broomhead & King, Extracting qualitative dynamics from experimental data, Physica D, 1986"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Lompatan, drift burst & momen realized

#### `E60_DRIFT_BURST_TSTAT`

*Tier komputasi: T1 murah*

```yaml
  - id: E60_DRIFT_BURST_TSTAT
    division: E
    division_type: direction
    formula: "T_t = sqrt(h_n) * mu_hat_t / sigma_hat_t ; mu_hat = drift kernel-weighted, sigma_hat = vol kernel-weighted"
    params: {h_mean: [6, 12], h_vol: [24, 48]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Rasio drift terhadap volatilitas lokal mendeteksi ledakan drift sesaat yang secara teori adalah satu-satunya bentuk tren yang bisa dibedakan dari derau pada frekuensi tinggi"
      counterparty: "Penyedia likuiditas yang terus mengutip dua sisi saat drift meledak dan menanggung kerugian seleksi merugikan sampai menarik kuotasi"
      decay: "Ledakan drift terjadi saat likuiditas menipis mendadak dan penyedia likuiditas tidak bisa menghindarinya tanpa berhenti mengutip"
    provenance:
      citation: "Christensen, Oomen & Reno, The drift burst hypothesis, Journal of Econometrics, 2022"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E61_LEE_MYKLAND_JUMP`

*Tier komputasi: T1 murah*

```yaml
  - id: E61_LEE_MYKLAND_JUMP
    division: E
    division_type: direction
    formula: "L_i = r_i / sigma_hat_i ; sigma_hat dari bipower jendela K ; lompatan jika |L_i| > ambang Gumbel"
    params: {K: [48, 96], alpha: [0.01, 0.05]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Uji lompatan Lee-Mykland memisahkan gerak lompatan dari gerak difusi sehingga fase setelah lompatan bisa diperlakukan berbeda"
      counterparty: "Peserta yang memakai model volatilitas kontinu dan salah mengukur risiko tepat setelah lompatan sehingga stopnya terpasang keliru"
      decay: "Lompatan berasal dari kedatangan informasi diskret yang jadwalnya sebagian tidak terduga"
    provenance:
      citation: "Lee & Mykland, Jumps in financial markets a new nonparametric test and jump dynamics, Review of Financial Studies, 2008"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E62_BIPOWER_JUMP_RATIO`

*Tier komputasi: T1 murah*

```yaml
  - id: E62_BIPOWER_JUMP_RATIO
    division: E
    division_type: direction
    formula: "J = max(0, (RV - BV)/RV) ; RV = realized variance, BV = bipower variation"
    params: {window: [48, 96, 288]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Rasio variasi bipower terhadap realized mengukur porsi gerak yang berasal dari lompatan sehingga membedakan hari lompatan dari hari difusi murni"
      counterparty: "Peserta yang menskala ukuran posisi dari volatilitas total dan mengambil risiko berlebih di hari yang volatilitasnya didominasi lompatan"
      decay: "Porsi lompatan ditentukan jadwal rilis makro dan kejadian geopolitik di luar kendali pelaku"
    provenance:
      citation: "Barndorff-Nielsen & Shephard, Econometrics of testing for jumps in financial economics using bipower variation, Journal of Financial Econometrics, 2006"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E63_SIGNED_JUMP_VARIATION`

*Tier komputasi: T1 murah*

```yaml
  - id: E63_SIGNED_JUMP_VARIATION
    division: E
    division_type: direction
    formula: "SJV = RS_plus - RS_minus ; sinyal dari tanda dan besar SJV"
    params: {window: [48, 96, 288]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Selisih variasi realized sisi naik dan turun memisahkan volatilitas baik dari buruk dan asimetrinya membawa informasi arah"
      counterparty: "Peserta yang memperlakukan volatilitas sebagai besaran tanpa tanda dan kehilangan informasi arah dalam asimetrinya"
      decay: "Asimetri berasal dari perbedaan urgensi likuidasi posisi rugi versus realisasi posisi untung, perilaku manusia yang bertahan"
    provenance:
      citation: "Patton & Sheppard, Good volatility bad volatility signed jumps and the persistence of volatility, Review of Economics and Statistics, 2015"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E64_REALIZED_SKEWNESS`

*Tier komputasi: T1 murah*

```yaml
  - id: E64_REALIZED_SKEWNESS
    division: E
    division_type: direction
    formula: "RSkew = sqrt(N) * SUM r_i^3 / RV^{3/2}"
    params: {window: [48, 96, 288]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Skewness realized dari return intraperiode menangkap asimetri distribusi jangka pendek yang terbukti memprediksi return periode berikutnya di literatur"
      counterparty: "Peserta yang menjual opsionalitas ekor secara implisit lewat strategi kontra tren dan menanggung kerugian saat ekor terwujud"
      decay: "Preferensi terhadap hasil miring positif adalah bias perilaku yang bertahan lintas generasi pelaku"
    provenance:
      citation: "Amaya, Christoffersen, Jacobs & Vasquez, Does realized skewness predict the cross-section of equity returns, Journal of Financial Economics, 2015"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E65_REALIZED_KURTOSIS`

*Tier komputasi: T1 murah*

```yaml
  - id: E65_REALIZED_KURTOSIS
    division: E
    division_type: direction
    formula: "RKurt = N * SUM r_i^4 / RV^2"
    params: {window: [48, 96, 288]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Kurtosis realized mengukur ketebalan ekor jangka pendek sehingga menandai periode ketika risiko tersentuh stop jauh lebih tinggi dari perkiraan volatilitas biasa"
      counterparty: "Peserta yang menetapkan jarak stop dari volatilitas standar dan tersapu jauh lebih sering pada periode berekor tebal"
      decay: "Ketebalan ekor bergerak dengan ketidakpastian makro yang tidak bisa dikurangi aktivitas intraday"
    provenance:
      citation: "Amaya, Christoffersen, Jacobs & Vasquez, Does realized skewness predict the cross-section of equity returns, Journal of Financial Economics, 2015"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Uji tren nonparametrik (pengganti RSI/Stochastic)

#### `E70_MANN_KENDALL`

*Tier komputasi: T1 murah*

```yaml
  - id: E70_MANN_KENDALL
    division: E
    division_type: direction
    formula: "S = SUM_{i<j} sign(x_j - x_i) ; Z = (S - sign(S))/sqrt(Var(S))"
    params: {window: [24, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Uji tren Mann-Kendall memakai tanda selisih semua pasangan sehingga mendeteksi tren monoton tanpa mengasumsikan bentuk distribusi return yang berekor tebal"
      counterparty: "Peserta yang memakai uji berbasis asumsi normal pada return berekor tebal dan menerima kesimpulan yang tidak valid"
      decay: "Uji nonparametrik lebih lemah dayanya sehingga hanya menangkap tren yang cukup kuat"
    provenance:
      citation: "Mann, Nonparametric tests against trend, Econometrica, 1945"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E71_COX_STUART`

*Tier komputasi: T1 murah*

```yaml
  - id: E71_COX_STUART
    division: E
    division_type: direction
    formula: "Bandingkan x_i dengan x_{i+n/2}, hitung tanda, uji binomial"
    params: {window: [24, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Uji Cox-Stuart membandingkan paruh awal dan akhir jendela lewat tanda saja sehingga sangat murah dan hampir tanpa asumsi"
      counterparty: "Peserta yang memakai uji rumit yang butuh estimasi varians dan hasilnya rusak ketika varians berubah di tengah jendela"
      decay: "Uji berbasis tanda kebal terhadap perubahan skala sehingga tetap valid lintas rezim harga"
    provenance:
      citation: "Cox & Stuart, Some quick sign tests for trend in location and dispersion, Biometrika, 1955"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E72_THEIL_SEN_SLOPE`

*Tier komputasi: T2 sedang*

```yaml
  - id: E72_THEIL_SEN_SLOPE
    division: E
    division_type: direction
    formula: "beta = median over i<j of (x_j - x_i)/(j - i)"
    params: {window: [12, 24, 48, 96]}
    variants: 4
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Kemiringan Theil-Sen adalah median dari semua kemiringan pasangan sehingga tahan sampai hampir sepertiga data merupakan pencilan"
      counterparty: "Peserta yang mengukur kemiringan tren dengan kuadrat terkecil dan estimasinya tertarik jauh oleh beberapa bar berita"
      decay: "Ketahanan terhadap pencilan berharga justru di emas yang sering melompat"
    provenance:
      citation: "Sen, Estimates of the regression coefficient based on Kendall tau, Journal of the American Statistical Association, 1968"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E73_RUNS_TEST`

*Tier komputasi: T1 murah*

```yaml
  - id: E73_RUNS_TEST
    division: E
    division_type: direction
    formula: "R = jumlah runtun tanda ; Z = (R - E[R])/sd(R) dengan E[R]=2*n1*n2/n + 1"
    params: {window: [24, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Uji runtun menghitung jumlah rentetan tanda yang sama sehingga menguji keacakan urutan arah langsung tanpa melihat besarannya"
      counterparty: "Peserta yang mengasumsikan urutan arah acak dan tidak memanfaatkan periode ketika rentetan searah jauh lebih panjang dari harapan acak"
      decay: "Panjang rentetan berubah dengan intensitas arus terarah yang datang tidak terjadwal"
    provenance:
      citation: "Wald & Wolfowitz, On a test whether two samples are from the same population, Annals of Mathematical Statistics, 1940"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E74_BARTELS_RANK_TEST`

*Tier komputasi: T1 murah*

```yaml
  - id: E74_BARTELS_RANK_TEST
    division: E
    division_type: direction
    formula: "RVN = SUM (R_i - R_{i+1})^2 / SUM (R_i - Rbar)^2 ; R = peringkat"
    params: {window: [24, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Uji peringkat Bartels menguji keacakan lewat rasio selisih peringkat berurutan sehingga lebih peka terhadap keteraturan halus daripada uji runtun biasa"
      counterparty: "Peserta yang hanya memakai uji runtun dan melewatkan keteraturan yang tidak muncul sebagai rentetan tanda panjang"
      decay: "Kepekaan lebih tinggi berarti lebih banyak alarm palsu sehingga tetap butuh koreksi pengujian berganda"
    provenance:
      citation: "Bartels, The rank version of von Neumann ratio test for randomness, Journal of the American Statistical Association, 1982"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Estimator kemiringan robust

#### `E80_QUANTILE_REGRESSION_SLOPE`

*Tier komputasi: T1 murah*

```yaml
  - id: E80_QUANTILE_REGRESSION_SLOPE
    division: E
    division_type: direction
    formula: "min_b SUM rho_tau(y_i - b*t_i) ; rho_tau(u) = u*(tau - 1(u<0))"
    params: {tau: [0.25, 0.50, 0.75], window: [24, 48]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Kemiringan regresi kuantil mengukur arah pada kuantil tertentu bukan rata-ratanya sehingga tidak tertarik oleh ekor yang jarang tapi besar"
      counterparty: "Peserta yang memakai kuadrat terkecil dan estimasi arahnya digeser beberapa bar lompatan yang tidak mewakili kondisi normal"
      decay: "Perbedaan antara median dan rata-rata hanya besar di data miring yang khas emas"
    provenance:
      citation: "Koenker & Bassett, Regression quantiles, Econometrica, 1978"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E81_HUBER_SLOPE`

*Tier komputasi: T1 murah*

```yaml
  - id: E81_HUBER_SLOPE
    division: E
    division_type: direction
    formula: "min_b SUM rho_c(y_i - b*t_i) ; rho_c kuadratik untuk |u|<=c, linier di luar"
    params: {c: [1.345], window: [24, 48, 96]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Estimator M Huber memberi bobot penuh pada residual kecil dan bobot menurun pada residual besar sehingga menggabungkan efisiensi normal dengan ketahanan pencilan"
      counterparty: "Peserta yang harus memilih antara efisien tapi rapuh atau tahan tapi tidak efisien dan kehilangan salah satu sifat itu"
      decay: "Titik potong bobot harus dikalibrasi terhadap skala residual yang berubah tiap rezim"
    provenance:
      citation: "Huber, Robust estimation of a location parameter, Annals of Mathematical Statistics, 1964"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E82_SIEGEL_REPEATED_MEDIAN`

*Tier komputasi: T2 sedang*

```yaml
  - id: E82_SIEGEL_REPEATED_MEDIAN
    division: E
    division_type: direction
    formula: "beta = median_i( median_{j!=i} (x_j - x_i)/(j - i) )"
    params: {window: [24, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Median berulang Siegel punya titik patah lima puluh persen sehingga tetap benar walau separuh data adalah pencilan tanpa parameter penyetel"
      counterparty: "Peserta yang memakai estimator bertitik patah rendah pada periode berita beruntun dan mendapat arah yang keliru total"
      decay: "Biaya komputasinya kuadratik sehingga jarang dipakai pada data frekuensi tinggi oleh pelaku bersumber daya terbatas"
    provenance:
      citation: "Siegel, Robust regression using repeated medians, Biometrika, 1982"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E83_RANSAC_SLOPE`

*Tier komputasi: T2 sedang*

```yaml
  - id: E83_RANSAC_SLOPE
    division: E
    division_type: direction
    formula: "Iterasi: sampel acak minimal, fit, hitung inlier dalam toleransi t, ambil model dengan inlier terbanyak"
    params: {t_mult: [1.0, 2.0], n_iter: [100]}
    variants: 2
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "RANSAC mencari himpunan bagian data yang paling konsisten sehingga menemukan struktur dominan walau lebih dari separuh data terkontaminasi"
      counterparty: "Peserta yang memakai estimator bertitik patah rendah dan estimasinya rusak total saat kontaminasi melewati ambang"
      decay: "Hasil bergantung jumlah iterasi acak dan ambang inlier sehingga tidak deterministik dan sulit ditiru persis"
    provenance:
      citation: "Fischler & Bolles, Random sample consensus a paradigm for model fitting with applications to image analysis and automated cartography, Communications of the ACM, 1981"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Deteksi patahan rezim

#### `E90_CUSUM_CHANGEPOINT`

*Tier komputasi: T1 murah*

```yaml
  - id: E90_CUSUM_CHANGEPOINT
    division: E
    division_type: direction
    formula: "S_t^+ = max(0, S_{t-1}^+ + (x_t - mu0 - k)) ; alarm saat S_t^+ > h"
    params: {k_mult: [0.5, 1.0], h_mult: [4.0, 6.0]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Statistik jumlah kumulatif mendeteksi pergeseran rata-rata return secepat mungkin secara teori sehingga awal fase terarah ditandai lebih awal daripada oleh penghalus"
      counterparty: "Peserta yang menunggu konfirmasi rata-rata bergerak dan selalu masuk setelah sebagian besar pergeseran sudah terjadi"
      decay: "Ambang deteksi menentukan pertukaran antara kecepatan dan sinyal palsu, tidak ada setelan unggul di semua rezim"
    provenance:
      citation: "Page, Continuous inspection schemes, Biometrika, 1954"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E91_PELT_SEGMENTATION`

*Tier komputasi: T2 sedang*

```yaml
  - id: E91_PELT_SEGMENTATION
    division: E
    division_type: direction
    formula: "min SUM_{i} [ C(y_{t_{i-1}+1:t_i}) + beta ] dengan pemangkasan ; fitur = umur segmen & arah segmen"
    params: {beta_mult: [1.0, 2.0], min_seg: [12, 24]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Segmentasi PELT menemukan titik perubahan optimal secara eksak dengan biaya linier sehingga seluruh riwayat bisa disegmentasi ulang tiap bar tanpa aproksimasi"
      counterparty: "Peserta yang memakai segmentasi heuristik dan mendapat batas segmen berbeda tergantung urutan pemrosesan"
      decay: "Hasil bergantung penalti yang harus dikalibrasi terhadap derau sampel"
    provenance:
      citation: "Killick, Fearnhead & Eckley, Optimal detection of changepoints with a linear computational cost, Journal of the American Statistical Association, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E92_BOCPD_RUNLENGTH`

*Tier komputasi: T2 sedang*

```yaml
  - id: E92_BOCPD_RUNLENGTH
    division: E
    division_type: direction
    formula: "P(r_t | x_1:t) rekursif dengan fungsi hazard H(r) ; fitur = E[r_t] = umur rezim terprediksi"
    params: {hazard: [0.005, 0.01, 0.02]}
    variants: 3
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Deteksi titik perubahan daring Bayesian menghasilkan distribusi panjang run sehingga memberi probabilitas bukan keputusan biner tentang umur rezim berjalan"
      counterparty: "Peserta yang memakai deteksi biner dan berpindah strategi penuh pada sinyal yang masih sangat tidak pasti"
      decay: "Kualitas hasil bergantung spesifikasi hazard dan prior yang harus dibenarkan tiap sampel"
    provenance:
      citation: "Adams & MacKay, Bayesian online changepoint detection, arXiv preprint, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: pending
```

#### `E93_MATRIX_PROFILE_DISCORD`

*Tier komputasi: T2 sedang*

```yaml
  - id: E93_MATRIX_PROFILE_DISCORD
    division: E
    division_type: direction
    formula: "MP_i = min_j d(S_i, S_j) untuk |i-j| > exclusion ; discord = argmax MP"
    params: {subseq_len: [12, 24, 48]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Discord dari matrix profile menemukan subrangkaian paling tidak biasa dalam riwayat sehingga anomali struktural terdeteksi tanpa mendefinisikan anomali lebih dulu"
      counterparty: "Peserta yang mendefinisikan anomali lewat ambang tetap dan buta terhadap bentuk anomali di luar definisinya"
      decay: "Bentuk anomali berubah mengikuti perubahan mikrostruktur venue sehingga definisi tetap selalu ketinggalan"
    provenance:
      citation: "Yeh, Zhu, Ulanova, Begum, Ding, Dau, Silva, Mueen & Keogh, Matrix profile I all pairs similarity joins for time series, Proceedings of the IEEE International Conference on Data Mining, 2016"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Ketergantungan & informasi (tier-3)

#### `E95_MUTUAL_INFORMATION_LAG`

*Tier komputasi: T3 mahal*

```yaml
  - id: E95_MUTUAL_INFORMATION_LAG
    division: E
    division_type: direction
    formula: "I(X_t ; X_{t-L}) estimator k-nearest-neighbour Kraskov"
    params: {L: [1, 3, 6, 12], k: [4]}
    variants: 4
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Informasi mutual antar lag menangkap ketergantungan nonlinier yang tidak terlihat oleh autokorelasi sehingga struktur tersembunyi dari korelasi bisa ditemukan"
      counterparty: "Peserta yang menyimpulkan tidak ada struktur karena autokorelasinya nol padahal ketergantungannya nonlinier"
      decay: "Ketergantungan nonlinier sulit diubah jadi aturan perdagangan langsung sehingga bertahan lebih lama daripada korelasi linier"
    provenance:
      citation: "Kraskov, Stogbauer & Grassberger, Estimating mutual information, Physical Review E, 2004"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E96_TRANSFER_ENTROPY_SELF`

*Tier komputasi: T3 mahal*

```yaml
  - id: E96_TRANSFER_ENTROPY_SELF
    division: E
    division_type: direction
    formula: "TE = SUM p(x_{t+1}, x_t^k) * log[ p(x_{t+1}|x_t^k) / p(x_{t+1}|x_t^{k-1}) ]"
    params: {k: [2, 3], bins: [4, 6]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    mechanism:
      claim: "Entropi transfer dari masa lalu ke masa depan deret yang sama mengukur aliran informasi berarah sehingga membedakan prediktabilitas dari korelasi simetris"
      counterparty: "Peserta yang memakai ukuran simetris dan tidak bisa membedakan mana yang menggerakkan mana di antara dua besaran berkorelasi"
      decay: "Aliran informasi berarah muncul dari pemrosesan informasi bertahap antar peserta, tidak bisa dipercepat jadi seketika"
    provenance:
      citation: "Schreiber, Measuring information transfer, Physical Review Letters, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `E97_DISTANCE_CORRELATION`

*Tier komputasi: T3 mahal*

```yaml
  - id: E97_DISTANCE_CORRELATION
    division: E
    division_type: direction
    formula: "dCor(X,Y) = dCov(X,Y)/sqrt(dVar(X)*dVar(Y)) ; nol jika dan hanya jika independen"
    params: {L: [1, 3, 6], window: [96, 288]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Korelasi jarak bernilai nol jika dan hanya jika dua peubah independen sehingga memberi uji independensi lengkap tanpa parameter penyetel"
      counterparty: "Peserta yang memakai korelasi Pearson sebagai uji independensi padahal nol Pearson tidak berarti independen"
      decay: "Tanpa parameter penyetel berarti sulit dioverfit sehingga edge kecil tapi lebih dipercaya keluar sampel"
    provenance:
      citation: "Szekely, Rizzo & Bakirov, Measuring and testing dependence by correlation of distances, Annals of Statistics, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: true
```
