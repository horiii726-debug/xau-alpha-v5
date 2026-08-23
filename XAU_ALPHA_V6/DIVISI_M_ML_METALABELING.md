# DIVISI M — MACHINE LEARNING & META-LABELING

> ⚙️ **STATUS v6:** file ini adalah salinan **verbatim** dari v5 — nol perubahan rumus,
> nol perubahan grid parameter. Ledger: `ledger_arah.csv`.
>
> Dibawa dari v5 dengan **pemangkasan besar: 15 formula/81 varian -> 5 formula/12 varian**. Yang disisakan: M06+M07 (baseline wajib aturan M6), M11 (meta-labeling — **satu-satunya mekanisme yang TERBUKTI bekerja di run v5**), M01+M02 (dua model pohon, dipotong pertama kalau anggaran ketat). Dibuang: M03,M04,M05,M08,M09,M10,M12,M13,M14,M15. Grid hyperparameter WAJIB <=8 per model — M5 berarti grid 100 = 100 baris ledger_arah = seluruh anggaran v6.
>
> **GRID v6 (menimpa grid v5 di bawah — 32 varian jadi 12):**
> `M06_LASSO` lambda [0.01, 0.1] = 2 · `M07_RIDGE` lambda [0.1, 1.0] = 2 ·
> `M11_META_LABELING` primary × threshold, secondary dikunci M06 = 4 ·
> `M01_CATBOOST` depth [4,6] iterations dikunci 300 = 2 · `M02_XGBOOST` max_depth [3,5] = 2.
>
> ⚠️ **Dua aturan di blok "Aturan yang mengikat" file ini SUDAH DIGANTI v6:**
> "panel 25 instrumen" → panel **8** (§04); "konsisten >= 60% instrumen panel" →
> **pooled t dengan clustering** (§07 C, centang 17). Baca §04 dan §07, bukan blok di bawah.
>
> Aturan v6 yang berlaku di atasnya: corong bertingkat (§07), pemisahan ledger (§O10),
> anggaran dari DSR (§08). Baca `CLAUDE.md` lebih dulu.

---

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML di file ini disalin **verbatim** dari sumber. Nol perubahan rumus, nol perubahan grid parameter.

| | |
|---|---|
| **Tipe divisi** | `direction` |
| **Jumlah formula** | 15 → **v6: 5** (M01, M02, M06, M07, M11) |
| **Jumlah varian (v5)** | 81 → **v6: 12** (5 formula disisakan, grid dipangkas) |
| **Dijalankan di fase** | F7 |
| **Gerbang kelulusan** | `gates.direction` + seluruh §machine_learning (M1–M9) |
| **Metrik penilaian** | harus mengalahkan baseline linear teregularisasi (M06/M07) DAN sinyal primer polos |

## Kenapa divisi ini ada

PENAJAM, BUKAN PENCARI SINYAL BARU. Meta-labeling (M11) duluan: memakai sinyal yang sudah ada dan hanya memutuskan taruh/tidak.

Catatan asli dari file sumber:

> SEMUA tunduk pada §machine_learning. Validasi HANYA CPCV purged + embargo.
> Setiap kombinasi hyperparameter = 1 BARIS LEDGER (M5).
> WAJIB mengalahkan baseline linear teregularisasi (M6).

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
| `M01_CATBOOST` | 8 | 20 | T2 sedang | Gradient boosting dengan ordered target statistics & ordered boosting untuk m… |
| `M02_XGBOOST_MONOTONE` | 8 | 20 | T2 sedang | Boosting pohon dengan KENDALA MONOTON pada fitur yang hipotesisnya berarah |
| `M03_LIGHTGBM` | 8 | 20 | T2 sedang | Boosting berbasis pertumbuhan daun dengan gradient-based one-side sampling |
| `M04_RANDOM_FOREST` | 4 | 15 | T2 sedang | Ansambel pohon bootstrap dengan pemilihan fitur acak per split |
| `M05_EXTRA_TREES` | 4 | 15 | T2 sedang | Pohon dengan ambang split ACAK, bukan optimal, lalu dirata-ratakan |
| `M06_LASSO` 🔒 | 4 → **2** | 5 | T1 murah | min \|\|y - Xb\|\|^2 + lambda*\|\|b\|\|_1 |
| `M07_RIDGE` 🔒 | 4 → **2** | 3 | T1 murah | min \|\|y - Xb\|\|^2 + lambda*\|\|b\|\|_2^2 |
| `M08_ELASTIC_NET` | 6 | 6 | T1 murah | min \|\|y - Xb\|\|^2 + lambda*( alpha*\|\|b\|\|_1 + (1-alpha)*\|\|b\|\|_2^2 ) |
| `M09_SVM_RBF` | 6 | 8 | T3 mahal | min 0.5\|\|w\|\|^2 + C*SUM xi_i ; kernel K(x,x') = exp(-gamma*\|\|x-x'\|\|^2) |
| `M10_KERNEL_RIDGE` | 6 | 5 | T3 mahal | alpha = (K + lambda*I)^-1 * y ; prediksi f(x) = SUM alpha_i*K(x_i, x) |
| `M11_META_LABELING` 🔒 | 8 → **4** | 20 | T2 sedang | Model primer memberi ARAH. Model sekunder (biner) memutuskan TARUH / TIDAK TA… |
| `M12_KALMAN_LATENT_DRIFT` | 3 | 3 | T2 sedang | Keadaan: mu_t = mu_{t-1} + w_t ; Observasi: r_t = mu_t + v_t ; fitur = mu_t_h… |
| `M13_KALMAN_LATENT_VOL` | 4 | 4 | T2 sedang | Model ruang keadaan pada ln(r_t^2): h_t = phi*h_{t-1} + eta_t ; fitur = exp(h… |
| `M14_MDA_FEATURE_SELECTION` | 4 | 15 | T2 sedang | MDA_j = mean over folds of ( skor_baseline - skor_setelah_fitur_j_diacak ) pa… |
| `M15_STACKED_ENSEMBLE` | 4 | 25 | T3 mahal | Prediksi keluar-fold dari model dasar jadi input model tingkat kedua (logisti… |

🔒 = `tidak_boleh_dipangkas_dalam_kondisi_apapun` (§trial_budget.tangga_pemangkasan)

## Peta keluarga

- **Baseline linear WAJIB (aturan M6)** — `M06_LASSO`, `M07_RIDGE`, `M08_ELASTIC_NET`
- **Meta-labeling — PRIORITAS TERTINGGI DIVISI M** — `M11_META_LABELING`
- **Model pohon** — `M01_CATBOOST`, `M02_XGBOOST_MONOTONE`, `M03_LIGHTGBM`, `M04_RANDOM_FOREST`, `M05_EXTRA_TREES`
- **Kernel** — `M09_SVM_RBF`, `M10_KERNEL_RIDGE`
- **Estimator keadaan laten (Kalman — BUKAN anchor mean-reversion)** — `M12_KALMAN_LATENT_DRIFT`, `M13_KALMAN_LATENT_VOL`
- **Seleksi fitur & ensemble** — `M14_MDA_FEATURE_SELECTION`, `M15_STACKED_ENSEMBLE`

---

## Spesifikasi lengkap (verbatim dari sumber)

### Baseline linear WAJIB (aturan M6)

#### `M06_LASSO`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: M06_LASSO
    division: M
    division_type: direction
    formula: "min ||y - Xb||^2 + lambda*||b||_1"
    params: {lambda: [0.001, 0.01, 0.1, 1.0]}
    variants: 4
    n_parameters: 5
    data_required: [ohlc]
    catatan: "BASELINE WAJIB. Model kompleks harus mengalahkan ini (aturan M6)."
    mechanism:
      claim: "Regularisasi L1 memilih sedikit fitur yang benar-benar berkontribusi sehingga menghasilkan model jarang yang bisa diperiksa manusia"
      counterparty: "Peserta yang memasukkan puluhan fitur tanpa seleksi dan mendapat koefisien yang saling menutupi tanpa arti ekonomi"
      decay: "Fitur yang terpilih berubah tiap sampel sehingga tidak menghasilkan formula tetap yang bisa disalin pesaing"
    provenance:
      citation: "Tibshirani, Regression shrinkage and selection via the lasso, Journal of the Royal Statistical Society Series B, 1996"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M07_RIDGE`  🔒

*Tier komputasi: T1 murah*

```yaml
  - id: M07_RIDGE
    division: M
    division_type: direction
    formula: "min ||y - Xb||^2 + lambda*||b||_2^2"
    params: {lambda: [0.01, 0.1, 1.0, 10.0]}
    variants: 4
    n_parameters: 3
    data_required: [ohlc]
    catatan: "BASELINE WAJIB bersama M06."
    mechanism:
      claim: "Penyusutan L2 menstabilkan estimasi ketika jumlah fitur mendekati jumlah observasi efektif sehingga prediksi tidak meledak oleh kolinearitas"
      counterparty: "Peserta yang memakai kuadrat terkecil biasa pada fitur berkolinearitas dan mendapat koefisien besar berlawanan tanda yang tidak stabil"
      decay: "Tingkat penyusutan optimal bergantung rasio sinyal terhadap derau yang berubah tiap rezim"
    provenance:
      citation: "Hoerl & Kennard, Ridge regression biased estimation for nonorthogonal problems, Technometrics, 1970"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M08_ELASTIC_NET`

*Tier komputasi: T1 murah*

```yaml
  - id: M08_ELASTIC_NET
    division: M
    division_type: direction
    formula: "min ||y - Xb||^2 + lambda*( alpha*||b||_1 + (1-alpha)*||b||_2^2 )"
    params: {lambda: [0.01, 0.1, 1.0], alpha: [0.3, 0.7]}
    variants: 6
    n_parameters: 6
    data_required: [ohlc]
    mechanism:
      claim: "Kombinasi penalti L1 dan L2 menangani fitur yang saling berkorelasi tinggi sehingga seleksi tidak melompat-lompat antar fitur kembar"
      counterparty: "Peserta yang memakai L1 murni pada fitur berkorelasi dan mendapat pilihan fitur yang tidak stabil antar periode"
      decay: "Struktur korelasi antar fitur berubah tiap rezim sehingga bobot campuran penalti harus dikalibrasi ulang"
    provenance:
      citation: "Zou & Hastie, Regularization and variable selection via the elastic net, Journal of the Royal Statistical Society Series B, 2005"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Meta-labeling — PRIORITAS TERTINGGI DIVISI M

#### `M11_META_LABELING`

*Tier komputasi: T2 sedang*

```yaml
  - id: M11_META_LABELING
    division: M
    division_type: direction
    formula: "Model primer memberi ARAH. Model sekunder (biner) memutuskan TARUH / TIDAK TARUH. Label sekunder = 1 kalau trade primer menguntungkan."
    params: {primary: [best_E, best_X], secondary_model: [M01_CATBOOST, M06_LASSO], threshold: [0.5, 0.6]}
    variants: 8
    n_parameters: 20
    data_required: [ohlc]
    catatan: "PRIORITAS TERTINGGI di divisi M — jalur tercepat ke perbaikan nyata."
    mechanism:
      claim: "Meta-labeling tidak mencari arah baru tapi memakai sinyal yang sudah ada lalu melatih model kedua yang hanya memutuskan taruh atau tidak sehingga presisi naik tanpa menambah trial di ruang arah"
      counterparty: "Peserta yang mengeksekusi setiap sinyal primer tanpa filter dan membayar biaya penuh untuk sinyal berkualitas rendah"
      decay: "Kualitas filter bergantung fitur kondisi pasar yang berubah, harus dilatih ulang berkala"
    provenance:
      citation: "Lopez de Prado, Advances in Financial Machine Learning, Wiley, 2018 (monograf)"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Model pohon

#### `M01_CATBOOST`

*Tier komputasi: T2 sedang*

```yaml
  - id: M01_CATBOOST
    division: M
    division_type: direction
    formula: "Gradient boosting dengan ordered target statistics & ordered boosting untuk mencegah target leakage"
    params: {depth: [4, 6], l2_leaf_reg: [3, 10], iterations: [300, 600]}
    variants: 8
    n_parameters: 20
    data_required: [ohlc]
    fitur_input: "seluruh divisi V, Q, T yang sudah lolos FASE 4, plus fitur E terpilih lewat MDA"
    mechanism:
      claim: "Ordered boosting menghitung statistik target hanya dari observasi sebelumnya sehingga secara struktural mencegah kebocoran target yang menghantui boosting biasa"
      counterparty: "Peserta yang memakai target encoding biasa dan modelnya diam-diam melihat informasi dari observasi yang sedang diprediksi"
      decay: "Interaksi yang ditemukan bergantung rezim dan harus dilatih ulang terus sehingga tidak bisa dibekukan jadi aturan permanen"
    provenance:
      citation: "Prokhorenkova, Gusev, Vorobev, Dorogush & Gulin, CatBoost unbiased boosting with categorical features, Advances in Neural Information Processing Systems, 2018"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M02_XGBOOST_MONOTONE`

*Tier komputasi: T2 sedang*

```yaml
  - id: M02_XGBOOST_MONOTONE
    division: M
    division_type: direction
    formula: "Boosting pohon dengan KENDALA MONOTON pada fitur yang hipotesisnya berarah"
    params: {max_depth: [3, 5], min_child_weight: [10, 50], subsample: [0.7, 1.0]}
    variants: 8
    n_parameters: 20
    data_required: [ohlc]
    mechanism:
      claim: "Kendala monoton memaksa hubungan fitur dan prediksi searah dengan hipotesis ekonomi sehingga mengurangi ruang overfit secara struktural"
      counterparty: "Peserta yang membiarkan model bebas menemukan hubungan berbentuk apapun dan mendapat pola tanpa penjelasan ekonomi"
      decay: "Kendala monoton mengurangi kapasitas overfit tapi tidak menghapusnya, tetap butuh validasi keluar sampel ketat"
    provenance:
      citation: "Chen & Guestrin, XGBoost a scalable tree boosting system, Proceedings of the ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2016"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M03_LIGHTGBM`

*Tier komputasi: T2 sedang*

```yaml
  - id: M03_LIGHTGBM
    division: M
    division_type: direction
    formula: "Boosting berbasis pertumbuhan daun dengan gradient-based one-side sampling"
    params: {num_leaves: [15, 31], min_data_in_leaf: [50, 200], feature_fraction: [0.7, 1.0]}
    variants: 8
    n_parameters: 20
    data_required: [ohlc]
    mechanism:
      claim: "Pertumbuhan berbasis daun mempercepat pelatihan sehingga validasi silang bersarang yang mahal jadi terjangkau"
      counterparty: "Peserta yang tidak mampu menjalankan validasi bersarang karena biaya komputasi dan melaporkan hasil yang bias optimistis"
      decay: "Keunggulannya kecepatan bukan informasi, bertahan hanya selama pesaing belum menjalankan validasi setara"
    provenance:
      citation: "Ke, Meng, Finley, Wang, Chen, Ma, Ye & Liu, LightGBM a highly efficient gradient boosting decision tree, Advances in Neural Information Processing Systems, 2017"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M04_RANDOM_FOREST`

*Tier komputasi: T2 sedang*

```yaml
  - id: M04_RANDOM_FOREST
    division: M
    division_type: direction
    formula: "Ansambel pohon bootstrap dengan pemilihan fitur acak per split"
    params: {max_depth: [4, 8], min_samples_leaf: [50, 200], max_features: [sqrt]}
    variants: 4
    n_parameters: 15
    data_required: [ohlc]
    mechanism:
      claim: "Hutan acak merata-ratakan banyak pohon berkorelasi rendah sehingga variansnya turun tanpa harus menyetel banyak parameter seperti boosting"
      counterparty: "Peserta yang menyetel model tunggal berlebihan dan mendapat model yang sangat sensitif terhadap sampel pelatihan"
      decay: "Rata-rata ansambel menekan derau tapi juga menekan sinyal lemah sehingga tetap butuh sinyal dasar yang nyata"
    provenance:
      citation: "Breiman, Random forests, Machine Learning, 2001"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M05_EXTRA_TREES`

*Tier komputasi: T2 sedang*

```yaml
  - id: M05_EXTRA_TREES
    division: M
    division_type: direction
    formula: "Pohon dengan ambang split ACAK, bukan optimal, lalu dirata-ratakan"
    params: {max_depth: [4, 8], min_samples_leaf: [50, 200]}
    variants: 4
    n_parameters: 15
    data_required: [ohlc]
    mechanism:
      claim: "Pemilihan ambang acak mengurangi varians lebih jauh daripada hutan acak biasa sehingga lebih tahan derau pada data berderau tinggi"
      counterparty: "Peserta yang memakai pemisahan optimal per simpul dan justru memasang derau sampel ke dalam struktur pohonnya"
      decay: "Keacakan tambahan menaikkan bias sehingga hanya menang di rezim berderau tinggi"
    provenance:
      citation: "Geurts, Ernst & Wehenkel, Extremely randomized trees, Machine Learning, 2006"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Kernel

#### `M09_SVM_RBF`

*Tier komputasi: T3 mahal*

```yaml
  - id: M09_SVM_RBF
    division: M
    division_type: direction
    formula: "min 0.5||w||^2 + C*SUM xi_i ; kernel K(x,x') = exp(-gamma*||x-x'||^2)"
    params: {C: [0.1, 1.0, 10.0], gamma: [scale, 0.1]}
    variants: 6
    n_parameters: 8
    data_required: [ohlc]
    mechanism:
      claim: "Mesin vektor dukung memaksimalkan margin pemisah sehingga fokus pada titik keputusan yang sulit bukan pada seluruh massa data"
      counterparty: "Peserta yang mengoptimalkan rata-rata galat dan mengabaikan titik batas yang justru menentukan keputusan masuk atau tidak"
      decay: "Lebar kernel dan penalti harus disetel bersama dan optimumnya bergeser tiap rezim"
    provenance:
      citation: "Cortes & Vapnik, Support-vector networks, Machine Learning, 1995"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M10_KERNEL_RIDGE`

*Tier komputasi: T3 mahal*

```yaml
  - id: M10_KERNEL_RIDGE
    division: M
    division_type: direction
    formula: "alpha = (K + lambda*I)^-1 * y ; prediksi f(x) = SUM alpha_i*K(x_i, x)"
    params: {lambda: [0.01, 0.1, 1.0], kernel: [rbf, laplacian]}
    variants: 6
    n_parameters: 5
    data_required: [ohlc]
    mechanism:
      claim: "Regresi ridge berkernel memberi solusi bentuk tertutup untuk regresi nonlinier sehingga hasilnya deterministik dan tidak bergantung inisialisasi acak"
      counterparty: "Peserta yang memakai model nonlinier beroptimasi iteratif dan mendapat hasil berbeda tiap kali dilatih ulang dengan benih berbeda"
      decay: "Biaya komputasi tumbuh kuadratik terhadap jumlah sampel sehingga sulit dipakai pada data tick penuh"
    provenance:
      citation: "Saunders, Gammerman & Vovk, Ridge regression learning algorithm in dual variables, Proceedings of the International Conference on Machine Learning, 1998"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Estimator keadaan laten (Kalman — BUKAN anchor mean-reversion)

#### `M12_KALMAN_LATENT_DRIFT`

*Tier komputasi: T2 sedang*

```yaml
  - id: M12_KALMAN_LATENT_DRIFT
    division: M
    division_type: direction
    formula: "Keadaan: mu_t = mu_{t-1} + w_t ; Observasi: r_t = mu_t + v_t ; fitur = mu_t_hat (drift laten terestimasi)"
    params: {Q_over_R: [0.001, 0.01, 0.1], window: [288]}
    variants: 3
    n_parameters: 3
    data_required: [ohlc]
    catatan: >
      DIIZINKAN sebagai estimator keadaan laten. DILARANG dipakai sebagai anchor
      mean-reversion (sinyal harga-minus-Kalman). Bentuk itu sudah mati total di
      riset sebelumnya: korelasi 1.000 antar varian, mati di lima uji robustness.
    mechanism:
      claim: "Filter Kalman memisahkan drift laten dari derau observasi secara optimal di bawah asumsi linear-Gaussian sehingga memberi estimasi arah yang lebih halus daripada return mentah"
      counterparty: "Peserta yang membaca return mentah sebagai sinyal arah dan bereaksi terhadap derau observasi yang bukan informasi"
      decay: "Rasio Q/R harus diestimasi dari data dan berubah tiap rezim; kalau observasi didominasi informasi bukan derau, filter ini tidak menyaring apa-apa"
    provenance:
      citation: "Kalman, A new approach to linear filtering and prediction problems, Journal of Basic Engineering, 1960"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M13_KALMAN_LATENT_VOL`

*Tier komputasi: T2 sedang*

```yaml
  - id: M13_KALMAN_LATENT_VOL
    division: M
    division_type: direction
    formula: "Model ruang keadaan pada ln(r_t^2): h_t = phi*h_{t-1} + eta_t ; fitur = exp(h_t_hat/2)"
    params: {phi_init: [0.95, 0.98], window: [288, 576]}
    variants: 4
    n_parameters: 4
    data_required: [ohlc]
    mechanism:
      claim: "Volatilitas stokastik sebagai keadaan laten memberi estimasi volatilitas yang tidak dipaksa jadi fungsi deterministik dari return lampau seperti pada GARCH"
      counterparty: "Peserta yang memakai model volatilitas deterministik dan salah memperkirakan volatilitas saat guncangan datang dari sumber yang tidak terlihat di return"
      decay: "Estimasi keadaan laten butuh asumsi struktur yang tidak pernah persis benar"
    provenance:
      citation: "Harvey, Ruiz & Shephard, Multivariate stochastic variance models, Review of Economic Studies, 1994"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

### Seleksi fitur & ensemble

#### `M14_MDA_FEATURE_SELECTION`

*Tier komputasi: T2 sedang*

```yaml
  - id: M14_MDA_FEATURE_SELECTION
    division: M
    division_type: direction
    formula: "MDA_j = mean over folds of ( skor_baseline - skor_setelah_fitur_j_diacak ) pada fold UJI"
    params: {n_repeats: [5, 10], base_model: [M01_CATBOOST, M04_RANDOM_FOREST]}
    variants: 4
    n_parameters: 15
    data_required: [ohlc]
    catatan: "WAJIB dipakai untuk seleksi fitur. MDI (impurity, in-sample) DILARANG."
    mechanism:
      claim: "Penurunan akurasi rata-rata saat fitur diacak mengukur kontribusi fitur secara keluar sampel sehingga seleksi tidak memakai informasi dalam sampel"
      counterparty: "Peserta yang menyeleksi fitur berdasarkan kepentingan dalam sampel dan menyimpan fitur yang hanya bekerja di data latih"
      decay: "Peringkat kepentingan fitur bergeser tiap rezim sehingga seleksi harus diulang"
    provenance:
      citation: "Breiman, Random forests, Machine Learning, 2001"
      doi: NEED_LOOKUP
      peer_reviewed: true
```

#### `M15_STACKED_ENSEMBLE`

*Tier komputasi: T3 mahal*

```yaml
  - id: M15_STACKED_ENSEMBLE
    division: M
    division_type: direction
    formula: "Prediksi keluar-fold dari model dasar jadi input model tingkat kedua (logistic teregularisasi)"
    params: {base_set: [trees_only, trees_plus_linear], meta_reg: [0.1, 1.0]}
    variants: 4
    n_parameters: 25
    data_required: [ohlc]
    mechanism:
      claim: "Generalisasi bertumpuk menggabungkan prediksi beberapa model lewat model tingkat kedua sehingga bobot gabungan dipelajari bukan ditetapkan sembarang"
      counterparty: "Peserta yang menggabungkan sinyal dengan bobot sama rata dan memberi bobot sama pada model kuat dan model lemah"
      decay: "Model tingkat kedua menambah lapisan overfit dan hanya aman bila prediksi dasarnya benar-benar keluar sampel"
    provenance:
      citation: "Wolpert, Stacked generalization, Neural Networks, 1992"
      doi: NEED_LOOKUP
      peer_reviewed: true
```
