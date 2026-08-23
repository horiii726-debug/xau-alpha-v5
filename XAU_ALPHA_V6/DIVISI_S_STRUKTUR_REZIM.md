# DIVISI S — STRUKTUR & REZIM

> Bagian dari **XAU ALPHA RESEARCH v6**. 🔄 **Divisi baru** — bukan formula baru,
> tapi **reklasifikasi** 29 formula yang di v5 salah ditempatkan di divisi E.
> Seluruh spesifikasi rumus disalin **verbatim** dari `DIVISI_E_ENTRY_ARAH.md` v5.

| | |
|---|---|
| **Tipe divisi** | `estimation` ← 🔄 di v5 mereka `direction` |
| **Ledger** | `ledger_estimasi.csv` ← 🔄 **tidak masuk N untuk DSR** |
| **Formula** | 29 aktif + 9 `PARKED` |
| **Varian** | 29 (1 per formula) |
| **Fase** | F4 |
| **Gerbang** | `gates.estimation` — Model Confidence Set α=0.10, tie-break ke tersederhana |
| **Fungsi hilir** | memberi fitur rezim untuk **router multi-strategi** (§09) |

---

## Kenapa divisi ini ada: kesalahan kategori v5

**Permutation entropy tidak memberi tahu long atau short.** Hurst tidak. Dimensi
korelasi tidak. Lyapunov tidak. Entropi spektral tidak.

Semuanya mengukur **keadaan pasar**, bukan **arah**.

v5 memaksa mereka mengeluarkan arah, lalu mengujinya dengan `gates.direction` —
17 centang, expectancy bersih setelah biaya, t ≥ 3.0, MC2. Itu seperti menilai
termometer dari kemampuannya menebak cuaca besok.

Buktinya paling telanjang di `E10_VARIANCE_RATIO_LM`. Rumusnya di v5:

```
sig = sign(VR-1) untuk tren, -sign(VR-1) untuk balik arah
```

**Formula yang sama memberi sinyal berlawanan tergantung interpretasi.** Ambiguitas
itu sendiri adalah bukti bahwa VR mengukur **rezim**, bukan **arah**. VR memberi tahu
"pasar sedang trending atau mean-reverting", bukan "harga akan naik atau turun".

### Tiga akibat langsung

| akibat | penjelasan |
|---|---|
| **Mereka dijamin gagal** | targetnya bukan yang mereka ukur |
| **Mereka menghabiskan anggaran arah** | ~88 varian di v5, dan tiap varian menaikkan `SR_0` untuk **semua** kandidat lain lewat DSR |
| **Router multi-strategi tidak pernah terbangun** | padahal bahannya persis ada di sini |

Reklasifikasi ini **satu tindakan yang memperbaiki tiga hal sekaligus**: membebaskan
anggaran, memberi mereka target yang benar, dan membangun router yang Anda minta.

---

## Target terukur

Divisi `estimation` butuh target yang bisa diukur langsung — kalau tidak, MCS tidak
punya arti. Dua target, keduanya wajib dilaporkan:

```yaml
target_primer:
  nama: "Separasi expectancy bersyarat"
  definisi: >
    Apakah membagi sampel dengan fitur ini menghasilkan sub-sampel yang expectancy
    BASELINE-nya berbeda secara signifikan?
  prosedur: >
    1. Bagi sampel jadi kuintil berdasarkan nilai fitur pada bar t (kausal).
    2. Untuk tiap kuintil, hitung expectancy strategi BASELINE (X06_VERTICAL_ONLY
       dengan entry acak) pada bar-bar itu.
    3. Metrik = |expectancy(kuintil-5) - expectancy(kuintil-1)|, dengan CI bootstrap.
  kenapa_ini_target_yang_benar: >
    Fitur rezim berguna kalau dia memberi tahu KAPAN sesuatu bekerja lebih baik.
    Itu persis yang diukur separasi expectancy bersyarat — dan itu persis yang
    dibutuhkan router.

target_sekunder:
  nama: "Prediksi rezim keluar-sampel"
  definisi: "AUC memprediksi label rezim periode berikutnya (label dari §05 Bagian D)"
  baseline_naif: "rezim persisten — 'besok sama dengan hari ini'"

aturan:
  - "Juara per horizon lewat Model Confidence Set alpha=0.10"
  - "Imbang di dalam MCS -> pilih yang PALING SEDERHANA (§O6)"
  - "Tidak ada yang mengalahkan baseline naif -> pakai baseline, catat, jangan dipaksakan"
  - "HANYA yang lolos MCS yang boleh masuk router F7b (§09 C3)"
```

---

## Aturan yang mengikat divisi ini

- Divisi ini punya **target terukur**, jadi **boleh diperingkat** — lewat MCS, bukan argmax mentah. `forbid_argmax` **tidak** berlaku di sini (§O6, bukan §O5).
- Semua fitur **wajib kausal** (§L1, §L2). Dilarang centered MA, Savitzky-Golay non-kausal, `filtfilt`, smoothing dua arah.
- Kuantil dan normalisasi di-fit **hanya pada fold latih** (§L3).
- 🔄 **§L13a berlaku:** deteksi rezim retrospektif hanya boleh dipakai sebagai **umur segmen berjalan** yang kausal, bukan sebagai penanda titik balik.
- Semua `doi: NEED_LOOKUP` wajib diverifikasi di F3 (§D1).
- 1 varian per formula. Jendela dipilih **tengah** dari grid v5, dikunci di F0.

---

## Daftar isi — 29 formula aktif

### Persistensi & rasio varians (3)

| ID | Tier | Jendela v6 | Rumus (ringkas) |
|---|---|---|---|
| `E10_VARIANCE_RATIO_LM` | T1 | q=4 | `VR(q) = Var(r_t(q)) / (q·Var(r_t(1)))` |
| `E11_VARIANCE_RATIO_WRIGHT` | T1 | q=4 | VR berbasis peringkat/tanda, distribusi eksak sampel kecil |
| `E12_AUTOMATIC_VARIANCE_RATIO` | T1 | bartlett | VR dengan pemilihan horizon otomatis |

> **Ketiganya adalah sumbu utama router.** `VR > 1` → rezim persisten → tilt ke MOM.
> `VR < 1` → rezim anti-persisten → tilt ke MRV. Tanda ini **dipra-registrasi** (§09 C3).

### Memori panjang & dimensi fraktal (8)

| ID | Tier | Jendela v6 | Rumus (ringkas) |
|---|---|---|---|
| `E20_HURST_RS` | T1 | 288 | `R/S(n)`; H dari slope `ln(R/S)` vs `ln(n)` |
| `E21_MODIFIED_RS_LO` | T2 | 288 | R/S dengan penyebut HAC Newey-West |
| `E22_DFA_ALPHA` | T1 | 288, ord 1 | `F(n)=√mean((Y−Y_fit)²)`; α dari slope |
| `E23_MFDFA_WIDTH` | T2 | 288 | lebar spektrum multifraktal |
| `E24_HIGUCHI_FD` | T2 | 96, k=8 | dimensi fraktal domain waktu |
| `E25_KATZ_FD` | T1 | 96 | `D = log₁₀(n)/(log₁₀(n)+log₁₀(d/L))` |
| `E26_PETROSIAN_FD` | T1 | 48 | berbasis pergantian tanda selisih |
| `E27_RANGE_ROUGHNESS_RATIO` | T1 | 48 | `ρ = RRV/RV` |

### Entropi & kompleksitas (7)

| ID | Tier | Jendela v6 | Rumus (ringkas) |
|---|---|---|---|
| `E30_SHANNON_ENTROPY_SIGN` | T1 | 96, m=3 | `H = −Σ p_k log₂ p_k` atas pola tanda |
| `E31_APPROXIMATE_ENTROPY` | T2 | 96, r=0.20 | `ApEn = φ_m(r) − φ_{m+1}(r)` |
| `E32_SAMPLE_ENTROPY` | T2 | 96, m=2 | `SampEn = −ln(A/B)`, tanpa self-match |
| `E33_PERMUTATION_ENTROPY` | T2 | 96, d=4 | entropi pola ordinal |
| `E34_WEIGHTED_PERMUTATION_ENTROPY` | T2 | 96, d=3 | PE berbobot varians |
| `E35_DISPERSION_ENTROPY` | T2 | 96, c=6, m=2 | pola dispersi via NCDF |
| `E36_LEMPEL_ZIV_COMPLEXITY` | T1 | 288 | jumlah substring baru |

### Spektral, siklus & fase (6)

| ID | Tier | Jendela v6 | Rumus (ringkas) |
|---|---|---|---|
| `E50_FFT_DOMINANT_PERIOD` | T1 | 288 | periode dominan `1/argmax_f P(f)` |
| `E51_HILBERT_INSTANT_PHASE` | T2 | 16–64 | fase sesaat — **wajib versi kausal (§L2)** |
| `E52_HILBERT_INSTANT_FREQUENCY` | T2 | 16–64 | `ω(t) = dφ/dt`, beda maju kausal |
| `E53_WAVELET_SCALE_ENERGY` | T2 | db4, lvl 4 | rasio energi skala pendek/panjang |
| `E54_SPECTRAL_ENTROPY` | T1 | 288 | `SE = −Σ p_f ln p_f / ln N_f` |
| `E55_SSA_COMPONENT_SHARE` | T2 | L=48, 288 | pangsa nilai singular pertama |

### Momen realized & lompatan (4)

| ID | Tier | Jendela v6 | Rumus (ringkas) |
|---|---|---|---|
| `E61_LEE_MYKLAND_JUMP` | T1 | K=96, α=0.05 | `L_i = r_i/σ̂_i`; ambang Gumbel |
| `E62_BIPOWER_JUMP_RATIO` | T1 | 96 | `J = max(0,(RV−BV)/RV)` |
| `E64_REALIZED_SKEWNESS` | T1 | 96 | `RSkew = √N·Σr³/RV^{3/2}` |
| `E65_REALIZED_KURTOSIS` | T1 | 96 | `RKurt = N·Σr⁴/RV²` |

### Anomali struktural (1)

| ID | Tier | Jendela v6 | Rumus (ringkas) |
|---|---|---|---|
| `E93_MATRIX_PROFILE_DISCORD` | T2 | 24 | `MP_i = min_j d(S_i,S_j)`, `\|i−j\|>exclusion` |

---

## 🅿️ PARKED — 9 formula tier-3, tidak dijalankan di v6

| ID | Tier | Alasan parkir |
|---|---|---|
| `E40_LYAPUNOV_ROSENSTEIN` | T3 | O(n²) global, biaya tidak sebanding |
| `E41_RQA_DETERMINISM` | T3 | idem |
| `E42_RQA_LAMINARITY` | T3 | idem |
| `E43_CORRELATION_DIMENSION` | T3 | idem |
| `E44_BDS_TEST` | T3 | idem |
| `E45_ZERO_ONE_TEST_CHAOS` | T3 | idem |
| `E95_MUTUAL_INFORMATION_LAG` | T3 | estimator kNN Kraskov, O(n²) |
| `E96_TRANSFER_ENTROPY_SELF` | T3 | idem |
| `E97_DISTANCE_CORRELATION` | T3 | idem |

> **Bukan dibuang — `PARKED`.** Kalau v6 menghasilkan survivor dan anggaran komputasi
> tersisa, mereka antre pertama. Kalau v6 nol, menjalankan mereka tidak akan menolong:
> masalahnya bukan kurang fitur rezim eksotis.
>
> Kalau tetap dijalankan, §compute_budget tier-3 berlaku penuh: subsampel 20% partisi
> screen di 5 instrumen paling tidak berkorelasi, dan yang gagal ditandai
> `UNDERPOWERED_SCREEN`, **bukan** `REJECTED`.

---

## Cara divisi ini menyuplai router

Hanya fitur yang **lolos MCS di F4** yang boleh masuk router (§09 C3).

| sumbu router | kandidat fitur dari divisi S | MOM | MRV | BRK |
|---|---|:---:|:---:|:---:|
| **persistensi** | `E10`, `E11`, `E12`, `E20`, `E22` | **+** | **−** | 0 |
| **transisi volatilitas** | dari divisi V (bukan S) | **+** | 0 | **+** |
| **level volatilitas** | dari divisi V (bukan S) | 0 | **−** | 0 |
| **kebaruan changepoint** | umur segmen `E90`/`E92` (kausal, §L13a) | 0 | **+** | **−** |
| **kompleksitas / keteraturan** | `E30`–`E36`, `E54` | **+** | 0 | 0 |
| **resiliensi spread** | dari divisi Q (bukan S) | 0 | **+** | 0 |

**Tanda di tabel ini DIPRA-REGISTRASI dan di-hash sebelum F0** (§O11, §L13c).
Kandidat router yang hasilnya bagus tapi dengan tanda **terbalik** → `SIGN_FLIP_SUSPECT`,
**dilarang masuk CONFIRM**.

### Peringatan: jangan memecah rezim sampai eff N habis

`VIEW_REZIM` v5 sudah memperingatkan ini dan peringatannya tetap berlaku:

> Memecah sampel jadi rezim **membagi eff N**. Tiga rezim = tiap sub-sampel dapat
> sepertiga data. Pada eff N yang sudah tipis, itu menghancurkan daya uji.

Itu sebabnya router v6 memakai **bounded tilt** (§09 C2), bukan hard switch:
tiap keluarga tetap dievaluasi di **seluruh** sampel, dan rezim hanya menggeser bobot
dalam batas 0.5×–1.5×. **eff N tiap keluarga utuh.**

Divisi S dipakai untuk **membobot**, bukan untuk **memotong**.

---

## Catatan pemangkasan

Kalau anggaran komputasi memaksa (§01 Bagian C):

1. Seluruh tier-2 di divisi S → potong pertama (`E21`, `E23`, `E24`, `E31`–`E35`, `E51`–`E53`, `E55`, `E93`)
2. Sisakan satu wakil per keluarga: `E10` (persistensi), `E22` (memori panjang), `E30` (entropi), `E54` (spektral), `E62` (lompatan)
3. **Lantai divisi S: 5 formula.** Di bawah itu router kehilangan sumbu dan §09 tidak bisa dijalankan.
