# VIEW: DIVISI TREN — arah & kemiringan

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> 
> ⚠️ **FILE INI TIDAK MENAMBAH KANDIDAT APAPUN.** Ini indeks silang — cara lain membaca
> registry yang sudah ada. Tiap formula tetap dihitung **satu kali** di `ledger_trials.csv`.
> Sebuah formula muncul di beberapa file view **tidak** berarti dia dijalankan beberapa kali.


## Kenapa view ini ada

Ini kumpulan formula yang menjawab *"apakah ada kemiringan (drift) yang nyata, dan ke arah mana?"* —
**tanpa memakai satupun indikator ritel**.

Yang digantikan, sesuai `§laws.anti_rumus_ritel.padanan_akademik_wajib`:

| Yang dilarang | Penggantinya di sini |
|---|---|
| RSI, Stochastic | `E70_MANN_KENDALL`, `E71_COX_STUART`, `E73_RUNS_TEST`, `E74_BARTELS_RANK_TEST` |
| MACD | `E60_DRIFT_BURST_TSTAT`, `E01_INTRADAY_MOMENTUM` |
| EMA/SMA crossover | `E10`, `E11`, `E12` (uji rasio varians) |

Bedanya bukan kosmetik. RSI memberi angka tanpa distribusi null — kamu tidak bisa bertanya
"berapa peluang angka ini muncul dari keacakan?". Mann-Kendall memberi **statistik uji dengan
distribusi yang diketahui**, jadi pertanyaan itu bisa dijawab. Itu seluruh perbedaannya.

---

## 1. Uji tren nonparametrik — ada tren atau tidak?

Nonparametrik = tidak mengasumsikan return berdistribusi normal. Untuk emas yang sering melompat,
asumsi normal adalah asumsi yang salah.

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E70_MANN_KENDALL` | E | 3 | T1 | S = SUM_{i<j} sign(x_j - x_i) ; Z = (S - sign(S))/sqrt(Var(S)) |
| `E71_COX_STUART` | E | 3 | T1 | Bandingkan x_i dengan x_{i+n/2}, hitung tanda, uji binomial |
| `E73_RUNS_TEST` | E | 3 | T1 | R = jumlah runtun tanda ; Z = (R - E[R])/sd(R) dengan E[R]=2*n1*n2/n … |
| `E74_BARTELS_RANK_TEST` | E | 3 | T1 | RVN = SUM (R_i - R_{i+1})^2 / SUM (R_i - Rbar)^2 ; R = peringkat |

## 2. Estimator kemiringan robust — seberapa curam trennya?

Regresi OLS biasa hancur oleh satu bar berita. Semua estimator di bawah tahan outlier.

> ⚠️ `E72_THEIL_SEN_SLOPE` dan `E82_SIEGEL_REPEATED_MEDIAN` adalah **tier-2**, bukan tier-1.
> Keduanya menghitung SELURUH kemiringan pasangan: O(w²) dan O(w² log w) per bar.
> Pada w=96 itu ~4.600 dan ~9.200 operasi per bar per instrumen. **Wajib** implementasi bergulir
> inkremental atau batasi w <= 48. Lihat `AUDIT_TEMUAN.md` temuan #2.

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E72_THEIL_SEN_SLOPE` | E | 4 | T2 | beta = median over i<j of (x_j - x_i)/(j - i) |
| `E80_QUANTILE_REGRESSION_SLOPE` | E | 6 | T1 | min_b SUM rho_tau(y_i - b*t_i) ; rho_tau(u) = u*(tau - 1(u<0)) |
| `E81_HUBER_SLOPE` | E | 3 | T1 | min_b SUM rho_c(y_i - b*t_i) ; rho_c kuadratik untuk \|u\|<=c, linier… |
| `E82_SIEGEL_REPEATED_MEDIAN` | E | 3 | T2 | beta = median_i( median_{j!=i} (x_j - x_i)/(j - i) ) |
| `E83_RANSAC_SLOPE` | E | 2 | T2 | Iterasi: sampel acak minimal, fit, hitung inlier dalam toleransi t, a… |

## 3. Momentum & kelanjutan arah

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E01_INTRADAY_MOMENTUM` | E | 4 | T1 | sig = sign( (C_t - C_{t-L}) / C_{t-L} ) ; L = lookback bar |
| `E02_VOL_SCALED_MOMENTUM` | E | 6 | T1 | z = (C_t - C_{t-L}) / (sigma_t * sqrt(L)) ; sig = sign(z) * 1(\|z\| >… |
| `E04_SESSION_GAP_CONTINUATION` | E | 3 | T1 | gap = (O_t - C_{t-1})/C_{t-1} setelah jeda pasar ; sig = sign(gap) * … |

## 4. Lawan tren — reversal jangka pendek

Dimasukkan di sini justru karena dia **hipotesis tandingan**. Kalau E03 dan E01 sama-sama lolos gerbang, salah satunya kemungkinan besar keberuntungan — periksa korelasi PnL-nya (§dedup, ambang 0.90).

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E03_SHORT_HORIZON_REVERSAL` | E | 6 | T1 | z = (C_t - C_{t-L}) / (sigma_t*sqrt(L)) ; sig = -sign(z) * 1(\|z\| > … |

## 5. Drift & lompatan

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E60_DRIFT_BURST_TSTAT` | E | 4 | T1 | T_t = sqrt(h_n) * mu_hat_t / sigma_hat_t ; mu_hat = drift kernel-weig… |
| `E61_LEE_MYKLAND_JUMP` | E | 4 | T1 | L_i = r_i / sigma_hat_i ; sigma_hat dari bipower jendela K ; lompatan… |
| `E62_BIPOWER_JUMP_RATIO` | E | 3 | T1 | J = max(0, (RV - BV)/RV) ; RV = realized variance, BV = bipower varia… |
| `E63_SIGNED_JUMP_VARIATION` | E | 3 | T1 | SJV = RS_plus - RS_minus ; sinyal dari tanda dan besar SJV |

## 6. Drift laten (divisi M)

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `M12_KALMAN_LATENT_DRIFT` | M | 3 | T2 | Keadaan: mu_t = mu_{t-1} + w_t ; Observasi: r_t = mu_t + v_t ; fitur … |

---

## Peringatan yang mengikat view ini

- **Tren bukan sinyal sampai dia lolos `gates.direction`.** 17 centang, biaya `worst`, MC2 survival.
- **DILARANG mengurutkan** kandidat tren dan mengambil yang teratas (§O5). Threshold only.
- Riset sebelumnya mengukur: pasar memberi hit rate **37.86%** pada RR 1.67, sementara breakeven
  mekanisnya **37.50%**. Marginnya **0.36 poin persen**, sebelum biaya. Semua formula di halaman ini
  berkelahi memperebutkan margin setipis itu. Perlakukan sesuai.
