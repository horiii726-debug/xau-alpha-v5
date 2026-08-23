# DIVISI T — INTENSITAS TICK

> ⚙️ **STATUS v6:** file ini adalah salinan **verbatim** dari v5 — nol perubahan rumus,
> nol perubahan grid parameter. Ledger: `ledger_estimasi.csv`.
>
> Dibawa UTUH dari v5. **Status v6: `PARKED`** — seluruh divisi butuh data tick yang belum tersedia, dan semua formulanya tier-2/tier-3 (mahal). Dijalankan hanya kalau data tick sudah ada DAN anggaran komputasi tersisa setelah F4-F7.
>
> Aturan v6 yang berlaku di atasnya: corong bertingkat (§07), pemisahan ledger (§O10),
> anggaran dari DSR (§08). Baca `CLAUDE.md` lebih dulu.
>
> **Jumlah varian dibawa UTUH** (grid v5 tidak dipangkas). Divisi ini masuk
> `ledger_estimasi`, jadi **tidak menaikkan `SR_0`** untuk kandidat arah (§O10) —
> yang naik hanya biaya komputasi. Kalau estimasi F1 > 72 jam, pangkas ke
> **jendela tengah, 1 varian per formula** (§08 C2).

---

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML di file ini disalin **verbatim** dari sumber. Nol perubahan rumus, nol perubahan grid parameter.

| | |
|---|---|
| **Tipe divisi** | `estimation` |
| **Jumlah formula** | 10 |
| **Jumlah varian (baris ledger)** | 27 |
| **Dijalankan di fase** | F4 |
| **Gerbang kelulusan** | `gates.estimation` — Model Confidence Set alpha=0.10, tie-break ke yang paling sederhana |
| **Metrik penilaian** | daya prediksi terhadap intensitas kedatangan tick berikutnya |

## Kenapa divisi ini ada

ALAT UKUR JAM PASAR. Mengganti jam kalender dengan jam kejadian. Semua tier-2/3 — mahal, hati-hati anggaran.

Catatan asli dari file sumber:

> Timestamp tick NYATA di CFD walaupun volumenya palsu.
> Ini satu-satunya mikrostruktur jujur yang tersedia.

## Aturan yang mengikat divisi ini

- Divisi ini punya **target terukur**, jadi boleh diperingkat — lewat **Model Confidence Set alpha=0.10**, bukan lewat argmax mentah.
- Kalau imbang di dalam MCS: **pilih yang paling sederhana** (§O6).
- Kalau tidak ada yang mengalahkan baseline naif: **pakai baseline**, catat, jangan dipaksakan.
- Semua fitur **wajib kausal** (§L1, §L2). Dilarang centered MA, Savitzky-Golay non-kausal, `filtfilt`, smoothing dua arah.
- Sinyal dari bar `t` dieksekusi **paling cepat di pembukaan bar `t+1`** (§L9).
- Scaler / PCA / normalisasi **di-fit hanya pada fold latih** (§L3). Seleksi fitur **di dalam** loop CV (§L4).
- Semua `doi: NEED_LOOKUP` **wajib diverifikasi di F3**. Dilarang mengarang DOI (§D1).

## Daftar isi divisi

| ID | Varian | n_param | Tier komputasi | Rumus (ringkas) |
|---|---:|---:|---|---|
| `T01_HAWKES_EXPONENTIAL` | 3 | 3 | T3 mahal | lambda(t) = mu + SUM_{t_i<t}[ alpha * exp(-beta*(t - t_i)) ] |
| `T02_HAWKES_POWERLAW` | 2 | 4 | T3 mahal | lambda(t) = mu + SUM_{t_i<t}[ alpha / (1 + (t-t_i)/tau)^(1+gamma) ] |
| `T03_BRANCHING_RATIO` | 3 | 3 | T3 mahal | n_branch = alpha/beta (kernel eksponensial) ; mendekati 1 = pasar hampir krit… |
| `T04_ACD_EXPONENTIAL` | 3 | 3 | T2 sedang | psi_i = omega + a*x_{i-1} + b*psi_{i-1} ; x_i = durasi antar tick ; x_i = psi… |
| `T05_LOG_ACD` | 3 | 3 | T2 sedang | ln(psi_i) = omega + a*ln(x_{i-1}) + b*ln(psi_{i-1}) |
| `T06_WEIBULL_ACD` | 2 | 4 | T2 sedang | psi_i = omega + a*x_{i-1} + b*psi_{i-1} ; eps_i ~ Weibull(gamma) |
| `T07_KLEINBERG_BURST` | 2 | 3 | T3 mahal | Mesin keadaan dua tingkat: biaya transisi = gamma*ln(n) ; keadaan burst saat … |
| `T08_DISPERSION_INDEX` | 3 | 1 | T2 sedang | D = Var(N_bar) / Mean(N_bar) ; N_bar = jumlah tick per bar ; D=1 berarti Pois… |
| `T09_DIURNAL_ADJUSTED_DURATION` | 3 | 2 | T2 sedang | x_tilde_i = x_i / phi(waktu_i) ; phi = pola durasi rata-rata pada jam itu, di… |
| `T10_TICK_CLOCK_SUBORDINATION` | 3 | 1 | T2 sedang | Bar dibentuk setiap N tick (bukan setiap N menit) ; fitur = return per bar ti… |

🔒 = `tidak_boleh_dipangkas_dalam_kondisi_apapun` (§trial_budget.tangga_pemangkasan)

## Peta keluarga

- **Proses Hawkes & self-excitation** — `T01_HAWKES_EXPONENTIAL`, `T02_HAWKES_POWERLAW`, `T03_BRANCHING_RATIO`, `T07_KLEINBERG_BURST`
- **Model durasi (ACD)** — `T04_ACD_EXPONENTIAL`, `T05_LOG_ACD`, `T06_WEIBULL_ACD`, `T09_DIURNAL_ADJUSTED_DURATION`
- **Statistik intensitas & jam kejadian** — `T08_DISPERSION_INDEX`, `T10_TICK_CLOCK_SUBORDINATION`

---

## Spesifikasi lengkap (verbatim dari sumber)

### Proses Hawkes & self-excitation

#### `T01_HAWKES_EXPONENTIAL`

*Tier komputasi: T3 mahal*

```yaml
  - id: T01_HAWKES_EXPONENTIAL
    division: T
    division_type: estimation
    formula: "lambda(t) = mu + SUM_{t_i<t}[ alpha * exp(-beta*(t - t_i)) ]"
    params: {fit_window_min: [30, 120, 360]}
    variants: 3
    n_parameters: 3
    data_required: [tick_time]
    mechanism:
      claim: "Proses Hawkes memodelkan tick yang memicu tick berikutnya sehingga intensitas kedatangan bisa diprediksi dari riwayat waktu tick saja"
      counterparty: "Peserta yang memperlakukan kedatangan harga sebagai Poisson homogen dan salah memperkirakan risiko eksekusi saat ledakan aktivitas"
      decay: "Pemicuan diri berasal dari reaksi berantai algoritma eksekusi yang saling memantau, tidak bisa dihentikan tanpa mematikan algoritmanya"
    provenance:
      citation: "Hawkes, Spectra of some self-exciting and mutually exciting point processes, Biometrika, 1971"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `T02_HAWKES_POWERLAW`

*Tier komputasi: T3 mahal*

```yaml
  - id: T02_HAWKES_POWERLAW
    division: T
    division_type: estimation
    formula: "lambda(t) = mu + SUM_{t_i<t}[ alpha / (1 + (t-t_i)/tau)^(1+gamma) ]"
    params: {fit_window_min: [120, 360]}
    variants: 2
    n_parameters: 4
    data_required: [tick_time]
    mechanism:
      claim: "Kernel hukum pangkat menangkap memori panjang pemicuan tick yang tidak bisa ditangkap kernel eksponensial berekor cepat"
      counterparty: "Peserta yang memakai model bermemori pendek dan meremehkan berapa lama aktivitas tetap tinggi setelah lonjakan"
      decay: "Memori panjang aktivitas berasal dari lapisan peserta berbeda kecepatan yang komposisinya tidak bisa diseragamkan"
    provenance:
      citation: "Bacry & Muzy, Hawkes model for price and trades high-frequency dynamics, Quantitative Finance, 2014"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `T03_BRANCHING_RATIO`

*Tier komputasi: T3 mahal*

```yaml
  - id: T03_BRANCHING_RATIO
    division: T
    division_type: estimation
    formula: "n_branch = alpha/beta (kernel eksponensial) ; mendekati 1 = pasar hampir kritis"
    params: {fit_window_min: [30, 120, 360]}
    variants: 3
    n_parameters: 3
    data_required: [tick_time]
    mechanism:
      claim: "Rasio percabangan mengukur proporsi aktivitas yang berasal dari reaksi internal pasar bukan dari informasi luar sehingga menandai kerapuhan mikrostruktur"
      counterparty: "Peserta yang menganggap semua gerak berasal dari informasi dan memberi bobot berlebih pada gerak yang sebenarnya gema reaksi internal"
      decay: "Tingkat refleksivitas naik saat pelaku otomatis mendominasi dan turun saat manusia kembali, terus berubah"
    provenance:
      citation: "Filimonov & Sornette, Quantifying reflexivity in financial markets toward a prediction of flash crashes, Physical Review E, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `T07_KLEINBERG_BURST`

*Tier komputasi: T3 mahal*

```yaml
  - id: T07_KLEINBERG_BURST
    division: T
    division_type: estimation
    formula: "Mesin keadaan dua tingkat: biaya transisi = gamma*ln(n) ; keadaan burst saat laju kedatangan melampaui s*laju_dasar"
    params: {s: [2.0, 3.0], gamma: [1.0]}
    variants: 2
    n_parameters: 3
    data_required: [tick_time]
    mechanism:
      claim: "Deteksi ledakan berbasis mesin keadaan menemukan periode intensitas tinggi secara optimal sehingga awal dan akhir ledakan tertandai bukan hanya puncaknya"
      counterparty: "Peserta yang memakai ambang intensitas tetap dan menandai ledakan terlambat serta melepasnya terlalu cepat"
      decay: "Struktur ledakan berasal dari kedatangan informasi yang berkelompok secara alami"
    provenance:
      citation: "Kleinberg, Bursty and hierarchical structure in streams, Data Mining and Knowledge Discovery, 2003"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Model durasi (ACD)

#### `T04_ACD_EXPONENTIAL`

*Tier komputasi: T2 sedang*

```yaml
  - id: T04_ACD_EXPONENTIAL
    division: T
    division_type: estimation
    formula: "psi_i = omega + a*x_{i-1} + b*psi_{i-1} ; x_i = durasi antar tick ; x_i = psi_i * eps_i"
    params: {fit_window_min: [30, 120, 360]}
    variants: 3
    n_parameters: 3
    data_required: [tick_time]
    mechanism:
      claim: "Model durasi bersyarat autoregresif memodelkan jeda antar tick langsung sehingga klaster aktivitas terprediksi tanpa mengagregasi ke bar waktu"
      counterparty: "Peserta yang bekerja pada bar waktu tetap dan kehilangan informasi bahwa lima tick dalam satu detik berbeda dari lima tick dalam satu menit"
      decay: "Klaster durasi berasal dari sifat kedatangan informasi yang berkelompok, bukan kesalahan yang bisa diperbaiki"
    provenance:
      citation: "Engle & Russell, Autoregressive conditional duration a new model for irregularly spaced transaction data, Econometrica, 1998"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `T05_LOG_ACD`

*Tier komputasi: T2 sedang*

```yaml
  - id: T05_LOG_ACD
    division: T
    division_type: estimation
    formula: "ln(psi_i) = omega + a*ln(x_{i-1}) + b*ln(psi_{i-1})"
    params: {fit_window_min: [30, 120, 360]}
    variants: 3
    n_parameters: 3
    data_required: [tick_time]
    mechanism:
      claim: "Versi logaritmik menghilangkan kendala non-negatif pada parameter sehingga estimasi lebih stabil dan bisa memuat variabel penjelas bebas"
      counterparty: "Peserta yang memakai spesifikasi berkendala dan estimasinya menabrak batas parameter lalu gagal konvergen di periode ekstrem"
      decay: "Keunggulan numerik bukan keunggulan informasi, bertahan selama pesaing memakai spesifikasi yang lebih rapuh"
    provenance:
      citation: "Bauwens & Giot, The logarithmic ACD model an application to the bid-ask quote process of three NYSE stocks, Annales d Economie et de Statistique, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `T06_WEIBULL_ACD`

*Tier komputasi: T2 sedang*

```yaml
  - id: T06_WEIBULL_ACD
    division: T
    division_type: estimation
    formula: "psi_i = omega + a*x_{i-1} + b*psi_{i-1} ; eps_i ~ Weibull(gamma)"
    params: {fit_window_min: [120, 360]}
    variants: 2
    n_parameters: 4
    data_required: [tick_time]
    mechanism:
      claim: "Distribusi Weibull mengizinkan hazard naik atau turun sehingga bentuk risiko kedatangan tick berikutnya tidak dipaksa konstan"
      counterparty: "Peserta yang mengasumsikan hazard konstan dan salah memperkirakan peluang tick berikutnya datang segera setelah jeda panjang"
      decay: "Bentuk hazard berubah antar sesi mengikuti siapa yang sedang aktif"
    provenance:
      citation: "Engle & Russell, Autoregressive conditional duration a new model for irregularly spaced transaction data, Econometrica, 1998"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `T09_DIURNAL_ADJUSTED_DURATION`

*Tier komputasi: T2 sedang*

```yaml
  - id: T09_DIURNAL_ADJUSTED_DURATION
    division: T
    division_type: estimation
    formula: "x_tilde_i = x_i / phi(waktu_i) ; phi = pola durasi rata-rata pada jam itu, diestimasi dari data LATIH saja"
    params: {phi_bins: [24, 48, 96]}
    variants: 3
    n_parameters: 2
    data_required: [tick_time]
    mechanism:
      claim: "Durasi antar tick yang dinormalisasi terhadap pola aktivitas harian memisahkan lonjakan aktivitas sejati dari pola jadwal biasa"
      counterparty: "Peserta yang membaca naiknya aktivitas pada jam sibuk sebagai sinyal informasi dan bertindak pada pola yang sepenuhnya terjadwal"
      decay: "Pola harian bergeser pelan mengikuti perubahan jam kerja pusat perdagangan"
    provenance:
      citation: "Engle & Russell, Autoregressive conditional duration a new model for irregularly spaced transaction data, Econometrica, 1998"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Statistik intensitas & jam kejadian

#### `T08_DISPERSION_INDEX`

*Tier komputasi: T2 sedang*

```yaml
  - id: T08_DISPERSION_INDEX
    division: T
    division_type: estimation
    formula: "D = Var(N_bar) / Mean(N_bar) ; N_bar = jumlah tick per bar ; D=1 berarti Poisson murni"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [tick_time]
    mechanism:
      claim: "Indeks dispersi membandingkan varians terhadap rata-rata jumlah tick sehingga menguji langsung apakah kedatangan menyimpang dari Poisson murni"
      counterparty: "Peserta yang memakai asumsi Poisson dalam model risiko eksekusinya dan meremehkan peluang rentetan tick padat"
      decay: "Penyimpangan dari Poisson adalah konsekuensi pengelompokan informasi yang bersifat struktural"
    provenance:
      citation: "Fisher, The significance of deviations from expectation in a Poisson series, Biometrics, 1950"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `T10_TICK_CLOCK_SUBORDINATION`

*Tier komputasi: T2 sedang*

```yaml
  - id: T10_TICK_CLOCK_SUBORDINATION
    division: T
    division_type: estimation
    formula: "Bar dibentuk setiap N tick (bukan setiap N menit) ; fitur = return per bar tick-clock"
    params: {ticks_per_bar: [100, 250, 500]}
    variants: 3
    n_parameters: 1
    data_required: [tick_time, ohlc]
    mechanism:
      claim: "Jumlah tick berfungsi sebagai jam stokastik yang membuat return tersubordinasi mendekati normal sehingga inferensi statistik jadi jauh lebih valid"
      counterparty: "Peserta yang bekerja pada jam kalender dan menerapkan uji berbasis normal pada return yang jelas tidak normal di jam kalender"
      decay: "Sifat subordinasi adalah struktur matematis pasar, bukan anomali, tidak hilang oleh arbitrase"
    provenance:
      citation: "Ane & Geman, Order flow transaction clock and normality of asset returns, Journal of Finance, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```
