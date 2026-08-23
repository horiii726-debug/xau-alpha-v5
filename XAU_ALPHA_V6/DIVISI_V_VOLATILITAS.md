# DIVISI V — VOLATILITAS

> ⚙️ **STATUS v6:** file ini adalah salinan **verbatim** dari v5 — nol perubahan rumus,
> nol perubahan grid parameter. Ledger: `ledger_estimasi.csv`.
>
> Dibawa UTUH dari v5. **V07_BIPOWER dan V08_MEDRV sudah LOLOS di run v5** — konfirmasi ulang di sampel baru. Juara MCS divisi ini dipakai untuk: penskalaan barrier, normalisasi MOM02/MOM11/BRK01/BRK03, dan sumbu volatilitas router (§09 C3).
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
| **Jumlah formula** | 14 |
| **Jumlah varian (baris ledger)** | 41 |
| **Dijalankan di fase** | F4 |
| **Gerbang kelulusan** | `gates.estimation` — Model Confidence Set alpha=0.10, tie-break ke yang paling sederhana |
| **Metrik penilaian** | QLIKE terhadap realized variance periode berikutnya |

## Kenapa divisi ini ada

ALAT UKUR. Ini pengganti ATR. ATR dilarang total (§laws.anti_rumus_ritel). V01_PARKINSON dipakai menskala barrier TP/SL di §labeling dan §X01.

Catatan asli dari file sumber:

> Target terukur langsung: realized variance periode berikutnya.
> Metrik: QLIKE. Juara lewat Model Confidence Set, tie-break ke tersederhana.
> INI PENGGANTI ATR. ATR dilarang total.

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
| `V01_PARKINSON` 🔒 | 3 | 1 | T1 murah | sigma^2 = (1/(4*n*ln(2))) * SUM_i[ (ln(H_i/L_i))^2 ] |
| `V02_GARMAN_KLASS` | 3 | 1 | T1 murah | sigma^2 = (1/n)*SUM_i[ 0.5*(ln(H_i/L_i))^2 - (2*ln(2)-1)*(ln(C_i/O_i))^2 ] |
| `V03_ROGERS_SATCHELL` | 3 | 1 | T1 murah | sigma^2 = (1/n)*SUM_i[ ln(H_i/C_i)*ln(H_i/O_i) + ln(L_i/C_i)*ln(L_i/O_i) ] |
| `V04_YANG_ZHANG` | 3 | 1 | T1 murah | sigma^2 = sigma_overnight^2 + k*sigma_open_close^2 + (1-k)*sigma_RS^2 ; k = 0… |
| `V05_CLOSE_TO_CLOSE` 🔒 | 3 | 1 | T1 murah | sigma^2 = (1/(n-1)) * SUM_i[ (r_i - rbar)^2 ] ; r_i = ln(C_i/C_{i-1}) |
| `V06_REALIZED_RANGE` | 6 | 2 | T2 sedang | RRV = (1/(4*ln(2))) * SUM_i[ (ln(H_i) - ln(L_i))^2 ] atas sub-interval di dal… |
| `V07_BIPOWER_VARIATION` | 2 | 1 | T1 murah | BV = (pi/2) * (n/(n-1)) * SUM_i[ \|r_i\| * \|r_{i-1}\| ] |
| `V08_MEDRV` | 2 | 1 | T1 murah | MedRV = (pi/(6-4*sqrt(3)+pi)) * (n/(n-2)) * SUM_i[ median(\|r_{i-1}\|,\|r_i\|… |
| `V09_MINRV` | 2 | 1 | T1 murah | MinRV = (pi/(pi-2)) * (n/(n-1)) * SUM_i[ min(\|r_i\|,\|r_{i+1}\|)^2 ] |
| `V10_REALIZED_SEMIVARIANCE` | 3 | 1 | T1 murah | RS_plus = SUM_i[ r_i^2 * 1(r_i>0) ] ; RS_minus = SUM_i[ r_i^2 * 1(r_i<0) ] ; … |
| `V11_HAR_RV` | 3 | 4 | T2 sedang | RV_{t+1} = c + b_d*RV_t^{(d)} + b_w*RV_t^{(w)} + b_m*RV_t^{(m)} + e ; kompone… |
| `V12_EWMA_VARIANCE` | 3 | 1 | T1 murah | sigma_t^2 = lambda*sigma_{t-1}^2 + (1-lambda)*r_t^2 |
| `V13_GARCH11_BASELINE` | 2 | 4 | T2 sedang | sigma_t^2 = omega + alpha*e_{t-1}^2 + beta*sigma_{t-1}^2 |
| `V14_REALIZED_KERNEL` | 3 | 2 | T2 sedang | RK = SUM_{h=-H}^{H} k(h/(H+1)) * gamma_h ; gamma_h = SUM_i r_i*r_{i-h} ; k = … |

🔒 = `tidak_boleh_dipangkas_dalam_kondisi_apapun` (§trial_budget.tangga_pemangkasan)

## Peta keluarga

- **Estimator range-based (pengganti langsung ATR)** — `V01_PARKINSON`, `V02_GARMAN_KLASS`, `V03_ROGERS_SATCHELL`, `V04_YANG_ZHANG`
- **Baseline wajib** — `V05_CLOSE_TO_CLOSE`
- **Realized & jump-robust** — `V06_REALIZED_RANGE`, `V07_BIPOWER_VARIATION`, `V08_MEDRV`, `V09_MINRV`, `V10_REALIZED_SEMIVARIANCE`
- **Model dinamis volatilitas** — `V11_HAR_RV`, `V12_EWMA_VARIANCE`, `V13_GARCH11_BASELINE`, `V14_REALIZED_KERNEL`

---

## Spesifikasi lengkap (verbatim dari sumber)

### Estimator range-based (pengganti langsung ATR)

#### `V01_PARKINSON`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: V01_PARKINSON
    division: V
    division_type: estimation
    formula: "sigma^2 = (1/(4*n*ln(2))) * SUM_i[ (ln(H_i/L_i))^2 ]"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Range intra-bar memuat informasi jalur yang hilang kalau hanya memakai harga penutupan, sehingga estimasi variansnya jauh lebih efisien"
      counterparty: "Peserta yang mengukur risiko dari close-to-close saja dan meremehkan risiko sebenarnya saat gerak intra-bar besar"
      decay: "Efisiensi estimator adalah sifat matematis, bukan pola pasar — tidak bisa diarbitrase habis"
    provenance:
      citation: "Parkinson, The extreme value method for estimating the variance of the rate of return, Journal of Business, 1980"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V02_GARMAN_KLASS`

*Tier komputasi: T1 murah*

```yaml
  - id: V02_GARMAN_KLASS
    division: V
    division_type: estimation
    formula: "sigma^2 = (1/n)*SUM_i[ 0.5*(ln(H_i/L_i))^2 - (2*ln(2)-1)*(ln(C_i/O_i))^2 ]"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Menggabungkan informasi range dan open-close menghasilkan estimator varians dengan efisiensi lebih tinggi daripada range saja"
      counterparty: "Peserta yang membuang informasi open-close dan butuh sampel lebih besar untuk ketelitian yang sama"
      decay: "Sifat matematis estimator, tidak terpengaruh aktivitas arbitrase"
    provenance:
      citation: "Garman & Klass, On the estimation of security price volatilities from historical data, Journal of Business, 1980"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V03_ROGERS_SATCHELL`

*Tier komputasi: T1 murah*

```yaml
  - id: V03_ROGERS_SATCHELL
    division: V
    division_type: estimation
    formula: "sigma^2 = (1/n)*SUM_i[ ln(H_i/C_i)*ln(H_i/O_i) + ln(L_i/C_i)*ln(L_i/O_i) ]"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Estimator ini tetap tak bias ketika harga punya drift, berbeda dari Parkinson dan Garman-Klass yang mengasumsikan drift nol"
      counterparty: "Peserta yang memakai estimator berasumsi drift nol pada sampel yang jelas bertren dan mendapat estimasi volatilitas yang bias"
      decay: "Koreksi drift adalah sifat matematis; relevansinya justru naik saat pasar bertren kuat"
    provenance:
      citation: "Rogers & Satchell, Estimating variance from high low and closing prices, Annals of Applied Probability, 1991"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V04_YANG_ZHANG`

*Tier komputasi: T1 murah*

```yaml
  - id: V04_YANG_ZHANG
    division: V
    division_type: estimation
    formula: "sigma^2 = sigma_overnight^2 + k*sigma_open_close^2 + (1-k)*sigma_RS^2 ; k = 0.34/(1.34 + (n+1)/(n-1))"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Menangani gap overnight secara eksplisit dan tetap tak bias terhadap drift sehingga bekerja pada instrumen yang punya jeda perdagangan"
      counterparty: "Peserta yang mengabaikan gap dan meremehkan volatilitas total pada instrumen dengan jeda sesi"
      decay: "Gap adalah fitur permanen venue, jadi keunggulan estimator ini tidak hilang"
    provenance:
      citation: "Yang & Zhang, Drift-independent volatility estimation based on high low open and close prices, Journal of Business, 2000"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Baseline wajib

#### `V05_CLOSE_TO_CLOSE`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: V05_CLOSE_TO_CLOSE
    division: V
    division_type: estimation
    formula: "sigma^2 = (1/(n-1)) * SUM_i[ (r_i - rbar)^2 ] ; r_i = ln(C_i/C_{i-1})"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Estimator paling sederhana yang wajib jadi pembanding — kalau estimator kompleks tidak mengalahkan ini, kompleksitasnya tidak dibenarkan"
      counterparty: "Peserta yang memakai model rumit tanpa membandingkannya terhadap baseline paling sederhana"
      decay: "Baseline selalu tersedia untuk semua orang, fungsinya sebagai pembanding permanen"
    provenance:
      citation: "Standard sample variance estimator, textbook baseline"
      doi: NOT_APPLICABLE
      peer_reviewed: true
```

### Realized & jump-robust

#### `V06_REALIZED_RANGE`

*Tier komputasi: T2 sedang*

```yaml
  - id: V06_REALIZED_RANGE
    division: V
    division_type: estimation
    formula: "RRV = (1/(4*ln(2))) * SUM_i[ (ln(H_i) - ln(L_i))^2 ] atas sub-interval di dalam periode"
    params: {window: [12, 48, 96], subsample: [5, 10]}
    variants: 6
    n_parameters: 2
    data_required: [ohlc]
    mechanism:
      claim: "Variasi berbasis range yang dihitung dari sub-interval menangkap lebih banyak informasi jalur daripada satu range per periode"
      counterparty: "Peserta yang hanya melihat range agregat dan kehilangan struktur pergerakan di dalamnya"
      decay: "Membutuhkan data intra-bar yang tidak semua pelaku simpan, sehingga aksesnya tidak merata"
    provenance:
      citation: "Christensen & Podolskij, Realized range-based estimation of integrated variance, Journal of Econometrics, 2007"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V07_BIPOWER_VARIATION`

*Tier komputasi: T1 murah*

```yaml
  - id: V07_BIPOWER_VARIATION
    division: V
    division_type: estimation
    formula: "BV = (pi/2) * (n/(n-1)) * SUM_i[ |r_i| * |r_{i-1}| ]"
    params: {window: [48, 96]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Variasi bipower tahan terhadap lompatan sehingga memisahkan komponen difusi dari komponen lompatan pada volatilitas"
      counterparty: "Peserta yang menskala ukuran posisi dari volatilitas total dan mengambil risiko berlebih di hari yang volatilitasnya didominasi lompatan"
      decay: "Porsi lompatan ditentukan jadwal rilis makro dan kejadian geopolitik yang di luar kendali pelaku"
    provenance:
      citation: "Barndorff-Nielsen & Shephard, Power and bipower variation with stochastic volatility and jumps, Journal of Financial Econometrics, 2004"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V08_MEDRV`

*Tier komputasi: T1 murah*

```yaml
  - id: V08_MEDRV
    division: V
    division_type: estimation
    formula: "MedRV = (pi/(6-4*sqrt(3)+pi)) * (n/(n-2)) * SUM_i[ median(|r_{i-1}|,|r_i|,|r_{i+1}|)^2 ]"
    params: {window: [48, 96]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Estimator berbasis median jauh lebih tahan terhadap outlier tunggal daripada bipower, sehingga tidak melonjak karena satu bar berita"
      counterparty: "Peserta yang estimasi volatilitasnya melonjak karena satu bar ekstrem lalu mengecilkan posisi tepat sebelum gerak menguntungkan"
      decay: "Ketahanan terhadap outlier berharga justru di emas yang sering melompat"
    provenance:
      citation: "Andersen, Dobrev & Schaumburg, Jump-robust volatility estimation using nearest neighbor truncation, Journal of Econometrics, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V09_MINRV`

*Tier komputasi: T1 murah*

```yaml
  - id: V09_MINRV
    division: V
    division_type: estimation
    formula: "MinRV = (pi/(pi-2)) * (n/(n-1)) * SUM_i[ min(|r_i|,|r_{i+1}|)^2 ]"
    params: {window: [48, 96]}
    variants: 2
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Varian minimum dari keluarga nearest-neighbor truncation dengan bias dan varians berbeda dari MedRV, dipakai sebagai pembanding sesama estimator tahan lompatan"
      counterparty: "Peserta yang memakai satu estimator tahan lompatan tanpa membandingkannya dengan alternatif sekelas"
      decay: "Perbedaan bias antar estimator hanya terasa di sampel terbatas, menuntut disiplin metodologis"
    provenance:
      citation: "Andersen, Dobrev & Schaumburg, Jump-robust volatility estimation using nearest neighbor truncation, Journal of Econometrics, 2012"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V10_REALIZED_SEMIVARIANCE`

*Tier komputasi: T1 murah*

```yaml
  - id: V10_REALIZED_SEMIVARIANCE
    division: V
    division_type: estimation
    formula: "RS_plus = SUM_i[ r_i^2 * 1(r_i>0) ] ; RS_minus = SUM_i[ r_i^2 * 1(r_i<0) ] ; fitur = RS_plus - RS_minus"
    params: {window: [12, 48, 96]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Memisahkan volatilitas sisi naik dan sisi turun mengungkap asimetri yang hilang kalau keduanya digabung jadi satu angka"
      counterparty: "Peserta yang memperlakukan volatilitas sebagai besaran tanpa tanda dan kehilangan informasi arah dalam asimetrinya"
      decay: "Asimetri berasal dari perbedaan urgensi likuidasi posisi rugi versus realisasi posisi untung, perilaku manusia yang bertahan"
    provenance:
      citation: "Barndorff-Nielsen, Kinnebrock & Shephard, Measuring downside risk realised semivariance, in Volatility and Time Series Econometrics, 2010"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Model dinamis volatilitas

#### `V11_HAR_RV`

*Tier komputasi: T2 sedang*

```yaml
  - id: V11_HAR_RV
    division: V
    division_type: estimation
    formula: "RV_{t+1} = c + b_d*RV_t^{(d)} + b_w*RV_t^{(w)} + b_m*RV_t^{(m)} + e ; komponen harian, mingguan, bulanan"
    params: {lag_set: ["1_5_22", "1_6_24", "1_4_20"]}
    variants: 3
    n_parameters: 4
    data_required: [ohlc]
    mechanism:
      claim: "Volatilitas digerakkan pelaku berhorizon berbeda sehingga model dengan tiga komponen skala meniru struktur kaskade itu dengan sedikit parameter"
      counterparty: "Peserta yang memodelkan volatilitas dengan satu skala tunggal dan salah memprediksi saat komposisi horizon pasar bergeser"
      decay: "Campuran horizon pelaku selalu berubah, tidak ada satu setelan tetap yang selalu benar"
    provenance:
      citation: "Corsi, A simple approximate long-memory model of realized volatility, Journal of Financial Econometrics, 2009"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V12_EWMA_VARIANCE`

*Tier komputasi: T1 murah*

```yaml
  - id: V12_EWMA_VARIANCE
    division: V
    division_type: estimation
    formula: "sigma_t^2 = lambda*sigma_{t-1}^2 + (1-lambda)*r_t^2"
    params: {lambda: [0.94, 0.97, 0.99]}
    variants: 3
    n_parameters: 1
    data_required: [ohlc]
    mechanism:
      claim: "Pembobotan eksponensial pada KUADRAT return adalah estimator varians, bukan penghalus harga, sehingga tidak melanggar larangan EMA sebagai sinyal"
      counterparty: "Peserta yang memakai jendela bergulir dengan bobot rata dan bereaksi terlambat saat rezim volatilitas berpindah"
      decay: "Parameter peluruhan optimal berubah tiap rezim, harus dikalibrasi ulang"
    provenance:
      citation: "RiskMetrics Technical Document, JP Morgan, 1996; formalized in Engle, Autoregressive conditional heteroscedasticity, Econometrica, 1982"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V13_GARCH11_BASELINE`

*Tier komputasi: T2 sedang*

```yaml
  - id: V13_GARCH11_BASELINE
    division: V
    division_type: estimation
    formula: "sigma_t^2 = omega + alpha*e_{t-1}^2 + beta*sigma_{t-1}^2"
    params: {dist: [normal, student_t]}
    variants: 2
    n_parameters: 4
    data_required: [ohlc]
    mechanism:
      claim: "Dipakai sebagai PEMBANDING wajib, bukan kandidat juara — riset sebelumnya menemukan seluruh keluarga GARCH kalah telak dari estimator range sederhana di ketiga horizon"
      counterparty: "Peserta yang memakai model kompleks tanpa membandingkannya dengan estimator satu baris yang lebih sederhana"
      decay: "Sebagai pembanding fungsinya permanen, terlepas dari performanya"
    provenance:
      citation: "Bollerslev, Generalized autoregressive conditional heteroskedasticity, Journal of Econometrics, 1986"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `V14_REALIZED_KERNEL`

*Tier komputasi: T2 sedang*

```yaml
  - id: V14_REALIZED_KERNEL
    division: V
    division_type: estimation
    formula: "RK = SUM_{h=-H}^{H} k(h/(H+1)) * gamma_h ; gamma_h = SUM_i r_i*r_{i-h} ; k = kernel Parzen"
    params: {bandwidth_H: [5, 10, 20]}
    variants: 3
    n_parameters: 2
    data_required: [ohlc, tick_time]
    mechanism:
      claim: "Kernel realized menangani derau mikrostruktur secara eksplisit sehingga estimasi varians tetap konsisten pada frekuensi tinggi"
      counterparty: "Peserta yang menghitung realized variance pada frekuensi tinggi tanpa koreksi derau dan mendapat estimasi yang meledak"
      decay: "Derau mikrostruktur adalah bagian permanen venue CFD"
    provenance:
      citation: "Barndorff-Nielsen, Hansen, Lunde & Shephard, Designing realized kernels to measure the ex post variation of equity prices in the presence of noise, Econometrica, 2008"
      doi: NEED_LOOKUP
      peer_reviewed: true
```
