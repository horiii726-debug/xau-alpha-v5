# VIEW: DIVISI REZIM — deteksi keadaan pasar

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> 
> ⚠️ **FILE INI TIDAK MENAMBAH KANDIDAT APAPUN.** Ini indeks silang — cara lain membaca
> registry yang sudah ada. Tiap formula tetap dihitung **satu kali** di `ledger_trials.csv`.
> Sebuah formula muncul di beberapa file view **tidak** berarti dia dijalankan beberapa kali.


## Kenapa view ini ada

Registry v5 tidak punya divisi bernama "rezim", tapi punya **26 formula yang fungsinya persis itu**:
menjawab *"pasar sedang dalam keadaan apa, dan apakah keadaan itu baru saja berubah?"*

Ini penting karena satu temuan yang berulang di seluruh blok `mechanism` file sumber:
**hampir semua edge bersifat kondisional terhadap rezim.** Nilai Hurst berayun antar rezim,
kemiringan distribusi berubah antar rezim, ambang absolut salah kalibrasi ketika volatilitas berpindah.
Kandidat yang diuji tanpa memisahkan rezim akan tampak lemah karena dua efek berlawanan saling
membatalkan di dalam rata-rata.

## Cara pakai yang BENAR

Rezim dipakai sebagai **variabel pengondisi**, bukan sebagai sinyal arah sendiri.

- ✅ Boleh: "kandidat X dijalankan, lalu hasilnya dipecah per tersile volatilitas untuk dilaporkan"
- ✅ Boleh: `X05_VOL_TERCILE_CONDITIONAL_BARRIER` — barrier berbeda per rezim, sudah ada di registry
- ⛔ **DILARANG:** menyetel parameter berbeda per rezim lalu melaporkan hasil gabungannya.
  Itu overfit terselubung, dan §universe.aturan_panel sudah melarang penyetelan per-instrumen dengan alasan yang sama.
- ⛔ **DILARANG:** memilih rezim yang hasilnya paling bagus setelah melihat hasil (§O8).

> **Aritmetika yang membunuh:** memecah sampel jadi 3 rezim membagi `eff N` jadi ~1/3 di tiap rezim.
> Dengan `eff N` panel target 800, tiap rezim tinggal ~267. Itu **menaikkan** ambang deteksi,
> bukan menurunkan. Pemecahan rezim harus dibayar dengan sampel, sama seperti semua hal lain di sistem ini.

---

## 1. Patahan rezim eksplisit (changepoint detection)

Ini yang menggantikan "support/resistance manual" dan "pivot point" (§laws.anti_rumus_ritel.padanan_akademik_wajib).

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E90_CUSUM_CHANGEPOINT` | E | 4 | T1 | S_t^+ = max(0, S_{t-1}^+ + (x_t - mu0 - k)) ; alarm saat S_t^+ > h |
| `E91_PELT_SEGMENTATION` | E | 4 | T2 | min SUM_{i} [ C(y_{t_{i-1}+1:t_i}) + beta ] dengan pemangkasan ; fitu… |
| `E92_BOCPD_RUNLENGTH` | E | 3 | T2 | P(r_t \| x_1:t) rekursif dengan fungsi hazard H(r) ; fitur = E[r_t] =… |
| `E93_MATRIX_PROFILE_DISCORD` | E | 3 | T2 | MP_i = min_j d(S_i, S_j) untuk \|i-j\| > exclusion ; discord = argmax… |

## 2. Rezim memori: trending vs mean-reverting

Menggantikan **EMA/SMA crossover**. Pertanyaannya bukan "MA mana yang menyilang" tapi "apakah seri ini secara statistik punya memori sama sekali?"

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E10_VARIANCE_RATIO_LM` | E | 4 | T1 | VR(q) = Var(r_t(q)) / (q * Var(r_t(1))) ; sig = sign(VR-1) untuk tren… |
| `E11_VARIANCE_RATIO_WRIGHT` | E | 3 | T1 | VR berbasis peringkat/tanda: R1(q), S1(q) dengan distribusi eksak sam… |
| `E12_AUTOMATIC_VARIANCE_RATIO` | E | 2 | T1 | VR dengan pemilihan horizon otomatis lewat kriteria data-driven, meng… |
| `E20_HURST_RS` | E | 3 | T1 | R/S(n) = (max_k(SUM(x_i - xbar)) - min_k(SUM(x_i - xbar))) / s_n ; H … |
| `E21_MODIFIED_RS_LO` | E | 2 | T2 | R/S dengan penyebut HAC Newey-West: s_n(q) = s^2 + 2*SUM_j w_j(q)*gam… |
| `E22_DFA_ALPHA` | E | 6 | T1 | Y(k)=SUM(x_i - xbar) ; F(n)=sqrt(mean((Y - Y_fit_n)^2)) ; alpha dari … |
| `E23_MFDFA_WIDTH` | E | 2 | T2 | F_q(n) untuk q dalam [-5,5] ; h(q) dari slope ; lebar spektrum = max(… |
| `E24_HIGUCHI_FD` | E | 6 | T2 | L(k) = mean over m of [ SUM\|x(m+ik)-x(m+(i-1)k)\| * (N-1)/(floor((N-… |
| `E25_KATZ_FD` | E | 3 | T1 | D = log10(n) / (log10(n) + log10(d/L)) ; L = panjang total jalur, d =… |
| `E26_PETROSIAN_FD` | E | 3 | T1 | D = log10(n) / (log10(n) + log10(n/(n + 0.4*N_delta))) ; N_delta = ju… |
| `E27_RANGE_ROUGHNESS_RATIO` | E | 3 | T1 | rho = RRV / RV ; RRV = realized range variation, RV = realized varian… |

## 3. Rezim prediktabilitas (entropi & kompleksitas)

Mengukur berapa banyak struktur yang tersisa di seri. Entropi tinggi = rezim tanpa informasi = jangan trading.

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E30_SHANNON_ENTROPY_SIGN` | E | 3 | T1 | H = -SUM_k p_k*log2(p_k) ; p_k dari frekuensi pola tanda return panja… |
| `E31_APPROXIMATE_ENTROPY` | E | 4 | T2 | ApEn(m,r,N) = phi_m(r) - phi_{m+1}(r) ; phi_m(r) = (N-m+1)^-1 SUM ln … |
| `E32_SAMPLE_ENTROPY` | E | 4 | T2 | SampEn(m,r,N) = -ln(A/B) ; A = pasangan cocok panjang m+1, B = panjan… |
| `E33_PERMUTATION_ENTROPY` | E | 9 | T2 | PE = -SUM_pi p(pi)*ln p(pi) ; pi = pola ordinal urutan panjang d, din… |
| `E34_WEIGHTED_PERMUTATION_ENTROPY` | E | 4 | T2 | WPE = -SUM_pi p_w(pi)*ln p_w(pi) ; p_w berbobot varians tiap jendela … |
| `E35_DISPERSION_ENTROPY` | E | 8 | T2 | Petakan x ke c kelas lewat NCDF, bentuk pola dispersi panjang m, DE =… |
| `E36_LEMPEL_ZIV_COMPLEXITY` | E | 3 | T1 | Simbolkan deret jadi biner (naik/turun), hitung jumlah substring baru… |

## 4. Rezim volatilitas (dari divisi V)

Bukan formula rezim sendiri, tapi **pemasok label rezim** untuk semua yang di atas.

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `V11_HAR_RV` | V | 3 | T2 | RV_{t+1} = c + b_d*RV_t^{(d)} + b_w*RV_t^{(w)} + b_m*RV_t^{(m)} + e ;… |
| `V12_EWMA_VARIANCE` | V | 3 | T1 | sigma_t^2 = lambda*sigma_{t-1}^2 + (1-lambda)*r_t^2 |
| `V13_GARCH11_BASELINE` | V | 2 | T2 | sigma_t^2 = omega + alpha*e_{t-1}^2 + beta*sigma_{t-1}^2 |
| `V14_REALIZED_KERNEL` | V | 3 | T2 | RK = SUM_{h=-H}^{H} k(h/(H+1)) * gamma_h ; gamma_h = SUM_i r_i*r_{i-h… |

## 5. Rezim biaya

Rezim yang paling sering dilupakan orang, padahal paling langsung memakan uang.

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `Q11_SPREAD_REGIME_BREAK` | Q | 2 | T2 | ICSS pada deret s_t: statistik D_k = (C_k/C_T) - k/T ; patahan saat m… |
| `Q10_SPREAD_PERCENTILE_GATE` | Q | 6 | T1 | gate_t = 1 jika s_t <= persentil_p(s) pada jendela referensi, selain … |

## 6. Konsumen rezim yang sudah ada di registry

| ID | Cara dia memakai rezim |
|---|---|
| `X05_VOL_TERCILE_CONDITIONAL_BARRIER` | Konfigurasi barrier berbeda per tersile volatilitas — menguji apakah asimetri mekanis hanya ada di sebagian rezim |
| `M12_KALMAN_LATENT_DRIFT` | Estimator keadaan laten (rezim tersembunyi). **BUKAN** anchor mean-reversion — bentuk itu dilarang |
| `M13_KALMAN_LATENT_VOL` | Sama, untuk volatilitas tersembunyi |
| `payoff_gate.stability_sub_periods: 3` | Gerbang payoff sudah wajib stabil di 3 sub-periode — itu uji rezim minimal yang sudah terpasang |
