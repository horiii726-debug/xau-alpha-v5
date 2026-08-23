# DIVISI Q — SPREAD & LIKUIDITAS

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML di file ini disalin **verbatim** dari sumber. Nol perubahan rumus, nol perubahan grid parameter.

| | |
|---|---|
| **Tipe divisi** | `estimation` |
| **Jumlah formula** | 12 |
| **Jumlah varian (baris ledger)** | 35 |
| **Dijalankan di fase** | F4 |
| **Gerbang kelulusan** | `gates.estimation` — Model Confidence Set alpha=0.10, tie-break ke yang paling sederhana |
| **Metrik penilaian** | akurasi terhadap spread efektif terukur dari tick Dukascopy |

## Kenapa divisi ini ada

ALAT UKUR BIAYA. Menentukan apakah sebuah trade layak dieksekusi sama sekali. Q10 & Q12 tidak boleh dipangkas.

Catatan asli dari file sumber:

> Spread tick nyata sudah dimiliki tapi selama ini HANYA dipakai sebagai biaya,
> belum pernah diuji sebagai informasi.

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
| `Q01_ROLL_SPREAD` | 3 | 1 | T1 murah | s = 2*sqrt(-Cov(r_t, r_{t-1})) kalau Cov < 0, selain itu tidak terdefinisi |
| `Q02_CORWIN_SCHULTZ` | 2 | 1 | T2 sedang | s = 2*(exp(alpha)-1)/(1+exp(alpha)) ; alpha dari rasio beta (dua hari) dan ga… |
| `Q03_ABDI_RANALDO` | 2 | 1 | T2 sedang | s = 2*sqrt( max( E[(c_t - eta_t)*(c_t - eta_{t+1})], 0 ) ) ; eta = (h+l)/2 da… |
| `Q04_AMIHUD_ILLIQUIDITY` | 3 | 1 | T1 murah | ILLIQ = (1/n) * SUM_i[ \|r_i\| / aktivitas_i ] ; aktivitas = jumlah tick di b… |
| `Q05_EFFECTIVE_TICK` | 2 | 2 | T2 sedang | s_eff = SUM_j[ gamma_j * s_j ] ; gamma_j = probabilitas kelompok tick j dari … |
| `Q06_SPREAD_VELOCITY` | 3 | 1 | T1 murah | v_t = (s_t - s_{t-k}) / k ; s = spread tick rata-rata per bar |
| `Q07_SPREAD_ACCELERATION` | 3 | 1 | T1 murah | a_t = s_t - 2*s_{t-k} + s_{t-2k} |
| `Q08_SPREAD_TO_VOL_RATIO` | 3 | 1 | T1 murah | kappa_t = s_t_bps / sigma_t_bps ; sigma dari V01_PARKINSON pada horizon holdi… |
| `Q09_SPREAD_RESILIENCY` | 3 | 2 | T2 sedang | tau = jumlah bar sampai s_t kembali ke persentil-50 jendela referensi setelah… |
| `Q10_SPREAD_PERCENTILE_GATE` 🔒 | 6 | 2 | T1 murah | gate_t = 1 jika s_t <= persentil_p(s) pada jendela referensi, selain itu 0 |
| `Q11_SPREAD_REGIME_BREAK` | 2 | 1 | T2 sedang | ICSS pada deret s_t: statistik D_k = (C_k/C_T) - k/T ; patahan saat max\|D_k\… |
| `Q12_REALIZED_SPREAD_COST` 🔒 | 3 | 1 | T1 murah | biaya_realized_bps = (2 * s_eksekusi + slippage_model) / harga_bar * 1e4 |

🔒 = `tidak_boleh_dipangkas_dalam_kondisi_apapun` (§trial_budget.tangga_pemangkasan)

## Peta keluarga

- **Estimator spread dari OHLC** — `Q01_ROLL_SPREAD`, `Q02_CORWIN_SCHULTZ`, `Q03_ABDI_RANALDO`, `Q05_EFFECTIVE_TICK`
- **Likuiditas & dampak harga** — `Q04_AMIHUD_ILLIQUIDITY`, `Q09_SPREAD_RESILIENCY`
- **Dinamika spread** — `Q06_SPREAD_VELOCITY`, `Q07_SPREAD_ACCELERATION`, `Q08_SPREAD_TO_VOL_RATIO`, `Q11_SPREAD_REGIME_BREAK`
- **Gerbang & akuntansi biaya (TIDAK BOLEH DIPANGKAS)** — `Q10_SPREAD_PERCENTILE_GATE`, `Q12_REALIZED_SPREAD_COST`

---

## Spesifikasi lengkap (verbatim dari sumber)

### Estimator spread dari OHLC

#### `Q01_ROLL_SPREAD`

*Tier komputasi: T1 murah*

```yaml
  - id: Q01_ROLL_SPREAD
    division: Q
    division_type: estimation
    formula: "s = 2*sqrt(-Cov(r_t, r_{t-1})) kalau Cov < 0, selain itu tidak terdefinisi"
    params: {window: [48, 96, 288]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc, tick_spread]
    mechanism:
      claim: "Autokovariansi negatif return berurutan berasal dari bid-ask bounce sehingga besarnya bisa dipakai menyimpulkan spread efektif"
      counterparty: "Peserta yang memakai biaya transaksi tetap dan tetap masuk posisi saat biaya implisit sudah naik"
      decay: "Komponen biaya implisit ditentukan sikap risiko penyedia likuiditas yang berubah mengikuti inventori mereka"
    provenance:
      citation: "Roll, A simple implicit measure of the effective bid-ask spread in an efficient market, Journal of Finance, 1984"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q02_CORWIN_SCHULTZ`

*Tier komputasi: T2 sedang*

```yaml
  - id: Q02_CORWIN_SCHULTZ
    division: Q
    division_type: estimation
    formula: "s = 2*(exp(alpha)-1)/(1+exp(alpha)) ; alpha dari rasio beta (dua hari) dan gamma (dua hari gabungan) berbasis high-low"
    params: {window: [48, 96]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc, tick_spread]
    mechanism:
      claim: "Rasio high-low dua periode memisahkan komponen volatilitas dari komponen spread karena keduanya berskala berbeda terhadap waktu"
      counterparty: "Peserta yang hanya punya data OHLC dan memakai proxy spread berbias lalu salah menghitung kelayakan strategi"
      decay: "Pemisahan berdasarkan skala waktu adalah sifat matematis, tidak habis oleh arbitrase"
    provenance:
      citation: "Corwin & Schultz, A simple way to estimate bid-ask spreads from daily high and low prices, Journal of Finance, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q03_ABDI_RANALDO`

*Tier komputasi: T2 sedang*

```yaml
  - id: Q03_ABDI_RANALDO
    division: Q
    division_type: estimation
    formula: "s = 2*sqrt( max( E[(c_t - eta_t)*(c_t - eta_{t+1})], 0 ) ) ; eta = (h+l)/2 dalam log"
    params: {window: [48, 96]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc, tick_spread]
    mechanism:
      claim: "Memakai selisih antara harga penutupan dan titik tengah high-low untuk menyimpulkan spread tanpa mengasumsikan autokovariansi negatif"
      counterparty: "Peserta yang memakai estimator Roll pada instrumen yang premis bid-ask bounce-nya tidak berlaku dan mendapat hasil degenerate"
      decay: "Validitas premis berbeda antar instrumen, jadi perlu diuji ulang tiap venue"
    provenance:
      citation: "Abdi & Ranaldo, A simple estimation of bid-ask spreads from daily close high and low prices, Review of Financial Studies, 2017"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q05_EFFECTIVE_TICK`

*Tier komputasi: T2 sedang*

```yaml
  - id: Q05_EFFECTIVE_TICK
    division: Q
    division_type: estimation
    formula: "s_eff = SUM_j[ gamma_j * s_j ] ; gamma_j = probabilitas kelompok tick j dari frekuensi harga pada kelipatan tick"
    params: {window: [96, 288]}
    variants: 2
    n_parameters: 2
    data_required: [ohlc, tick_spread]
    mechanism:
      claim: "Frekuensi harga jatuh pada kelipatan tick yang berbeda mengungkap ukuran spread efektif tanpa butuh data kuotasi lengkap"
      counterparty: "Peserta yang tidak punya data kuotasi dan terpaksa memakai proxy yang biasnya besar"
      decay: "Ukuran tick venue jarang berubah, sehingga estimator ini stabil tapi harus dikalibrasi ulang saat spesifikasi instrumen berubah"
    provenance:
      citation: "Holden, New low-frequency spread measures, Journal of Financial Markets, 2009"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Likuiditas & dampak harga

#### `Q04_AMIHUD_ILLIQUIDITY`

*Tier komputasi: T1 murah*

```yaml
  - id: Q04_AMIHUD_ILLIQUIDITY
    division: Q
    division_type: estimation
    formula: "ILLIQ = (1/n) * SUM_i[ |r_i| / aktivitas_i ] ; aktivitas = jumlah tick di bar i (BUKAN volume lot)"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc, tick_time]
    mechanism:
      claim: "Rasio gerak harga absolut terhadap aktivitas mengukur berapa besar harga bergerak per satuan aktivitas sehingga jadi ukuran langsung dampak likuiditas"
      counterparty: "Peserta yang mengeksekusi ukuran sama di kondisi likuiditas berbeda dan membayar dampak harga jauh lebih besar tanpa menyadarinya"
      decay: "Likuiditas berubah mengikuti jam kerja dan kejadian makro yang di luar kendali pelaku"
    provenance:
      citation: "Amihud, Illiquidity and stock returns cross-section and time-series effects, Journal of Financial Markets, 2002"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q09_SPREAD_RESILIENCY`

*Tier komputasi: T2 sedang*

```yaml
  - id: Q09_SPREAD_RESILIENCY
    division: Q
    division_type: estimation
    formula: "tau = jumlah bar sampai s_t kembali ke persentil-50 jendela referensi setelah melewati persentil-90"
    params: {ref_window: [48, 96, 288]}
    variants: 3
    n_parameters: 2
    data_required: [tick_spread]
    mechanism:
      claim: "Waktu pemulihan spread ke level normal setelah pelebaran mengukur ketahanan likuiditas sehingga memberi skala waktu untuk menunda masuk setelah guncangan"
      counterparty: "Peserta yang masuk segera setelah guncangan dan membayar spread lebar padahal menunggu beberapa detik memberi harga jauh lebih baik"
      decay: "Kecepatan pemulihan ditentukan modal penyedia likuiditas yang tersedia saat itu"
    provenance:
      citation: "Large, Measuring the resiliency of an electronic limit order book, Journal of Financial Markets, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Dinamika spread

#### `Q06_SPREAD_VELOCITY`

*Tier komputasi: T1 murah*

```yaml
  - id: Q06_SPREAD_VELOCITY
    division: Q
    division_type: estimation
    formula: "v_t = (s_t - s_{t-k}) / k ; s = spread tick rata-rata per bar"
    params: {k: [1, 3, 6]}
    variants: 3
    n_parameters: 1
    data_required: [tick_spread]
    mechanism:
      claim: "Kecepatan pelebaran spread mengukur laju penarikan likuiditas sehingga penarikan cepat bisa dibedakan dari pelebaran perlahan antar sesi"
      counterparty: "Penyedia likuiditas yang menarik kuotasi karena menduga ada arus terinformasi dan dengan itu mengungkapkan dugaannya"
      decay: "Penarikan likuiditas adalah tindakan defensif yang wajib dilakukan penyedia likuiditas untuk bertahan, tidak bisa disembunyikan"
    provenance:
      citation: "Foucault, Kadan & Kandel, Limit order book as a market for liquidity, Review of Financial Studies, 2005"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q07_SPREAD_ACCELERATION`

*Tier komputasi: T1 murah*

```yaml
  - id: Q07_SPREAD_ACCELERATION
    division: Q
    division_type: estimation
    formula: "a_t = s_t - 2*s_{t-k} + s_{t-2k}"
    params: {k: [1, 3, 6]}
    variants: 3
    n_parameters: 1
    data_required: [tick_spread]
    mechanism:
      claim: "Percepatan pelebaran spread menandai titik ketika penarikan likuiditas berubah dari bertahap jadi mendadak sehingga risiko slippage melonjak nonlinier"
      counterparty: "Peserta yang mengirim order pasar berdasarkan kondisi spread sedetik lalu dan terisi pada spread yang sudah jauh lebih lebar"
      decay: "Penyedia likuiditas saling memantau dan mundur bersamaan, itu dinamika permainan yang bertahan"
    provenance:
      citation: "Foucault, Kadan & Kandel, Limit order book as a market for liquidity, Review of Financial Studies, 2005"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q08_SPREAD_TO_VOL_RATIO`

*Tier komputasi: T1 murah*

```yaml
  - id: Q08_SPREAD_TO_VOL_RATIO
    division: Q
    division_type: estimation
    formula: "kappa_t = s_t_bps / sigma_t_bps ; sigma dari V01_PARKINSON pada horizon holding"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc, tick_spread]
    mechanism:
      claim: "Rasio biaya terhadap peluang gerak adalah kappa itu sendiri, jadi mengukurnya per bar memberi gerbang kelayakan yang bergerak real-time"
      counterparty: "Peserta yang mengejar volatilitas tinggi tanpa memeriksa bahwa spread ikut melebar sebanding sehingga peluang bersihnya tidak membaik"
      decay: "Spread dan volatilitas bergerak bersama karena mencerminkan ketidakpastian yang sama, rasionya lebih stabil daripada keduanya"
    provenance:
      citation: "Amihud, Illiquidity and stock returns cross-section and time-series effects, Journal of Financial Markets, 2002"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q11_SPREAD_REGIME_BREAK`

*Tier komputasi: T2 sedang*

```yaml
  - id: Q11_SPREAD_REGIME_BREAK
    division: Q
    division_type: estimation
    formula: "ICSS pada deret s_t: statistik D_k = (C_k/C_T) - k/T ; patahan saat max|D_k| melewati nilai kritis"
    params: {window: [288, 576]}
    variants: 2
    n_parameters: 1
    data_required: [tick_spread]
    mechanism:
      claim: "Deteksi patahan varians pada deret spread menandai perpindahan rezim biaya sehingga asumsi biaya dalam gate kelayakan bisa dihitung ulang tepat waktu"
      counterparty: "Peserta yang memakai satu asumsi biaya untuk seluruh sampel dan menghitung kelayakan dengan biaya kedaluwarsa"
      decay: "Rezim biaya berpindah mengikuti kebijakan broker dan likuiditas global yang tidak bisa diprediksi dari harga"
    provenance:
      citation: "Inclan & Tiao, Use of cumulative sums of squares for retrospective detection of changes of variance, Journal of the American Statistical Association, 1994"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Gerbang & akuntansi biaya (TIDAK BOLEH DIPANGKAS)

#### `Q10_SPREAD_PERCENTILE_GATE`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: Q10_SPREAD_PERCENTILE_GATE
    division: Q
    division_type: estimation
    formula: "gate_t = 1 jika s_t <= persentil_p(s) pada jendela referensi, selain itu 0"
    params: {percentile: [25, 40, 50], ref_window: [96, 288]}
    variants: 6
    n_parameters: 2
    data_required: [tick_spread]
    mechanism:
      claim: "Spread dipakai sebagai gerbang eksekusi bukan sinyal arah, posisi hanya dibuka saat biaya di bawah persentil tertentu jendela terkini"
      counterparty: "Peserta yang mengeksekusi tanpa memeriksa biaya saat itu dan menyerahkan sebagian besar edge tipisnya ke penyedia likuiditas"
      decay: "Pada kappa tinggi setiap perbaikan biaya langsung mengalir ke expectancy, bernilai selama biaya masih material"
    provenance:
      citation: "Goyenko, Holden & Trzcinka, Do liquidity measures measure liquidity, Journal of Financial Economics, 2009"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `Q12_REALIZED_SPREAD_COST`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: Q12_REALIZED_SPREAD_COST
    division: Q
    division_type: estimation
    formula: "biaya_realized_bps = (2 * s_eksekusi + slippage_model) / harga_bar * 1e4"
    params: {slippage_alpha: [0.5, 1.0, 1.5]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc, tick_spread]
    mechanism:
      claim: "Biaya total per trade dihitung dari spread pada bar eksekusi ditambah model slippage, bukan dari satu angka rata-rata untuk seluruh sampel"
      counterparty: "Peserta yang memakai biaya rata-rata dan sistematis salah menilai kelayakan di sesi mahal maupun sesi murah"
      decay: "Struktur biaya per sesi ditentukan jam kerja penyedia likuiditas yang tersebar di beberapa zona waktu"
    provenance:
      citation: "Goyenko, Holden & Trzcinka, Do liquidity measures measure liquidity, Journal of Financial Economics, 2009"
      doi: NEED_LOOKUP
      peer_reviewed: true
```
