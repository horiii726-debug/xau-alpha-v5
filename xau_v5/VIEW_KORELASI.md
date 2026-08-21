# VIEW: KORELASI — K_eff, dedup & ketergantungan

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> 
> ⚠️ **FILE INI TIDAK MENAMBAH KANDIDAT APAPUN.** Ini indeks silang — cara lain membaca
> registry yang sudah ada. Tiap formula tetap dihitung **satu kali** di `ledger_trials.csv`.
> Sebuah formula muncul di beberapa file view **tidak** berarti dia dijalankan beberapa kali.


## Kenapa korelasi adalah blok terpenting di seluruh sistem ini

Korelasi muncul di **empat tempat berbeda** di v5, dan tiga di antaranya adalah gerbang mati.
Salah satu penyebab sebenarnya nol survivor di riset sebelumnya adalah salah kelola korelasi.

| Tempat | Perannya | Konsekuensi kalau salah |
|---|---|---|
| `K_eff` (§power_analysis.c) | Menentukan berapa instrumen **independen** yang sebenarnya kamu punya | Gerbang mati F0 — proyek berhenti sebelum kandidat pertama |
| `screen_max` (§trial_budget) | Anggaran kandidat = `min(500, floor(50 × K_eff))` | Anggaran salah → ambang DSR salah untuk semua kandidat |
| `dedup` (ambang 0.90) | Membunuh kandidat kembar sebelum dijalankan | Registry penuh alias → N trial membengkak → semua kandidat dihukum lebih berat |
| Matriks korelasi null | Menghitung jumlah null independen efektif | 8 null berkorelasi ≠ 8 rintangan |

---

## 1. K_eff — jumlah instrumen independen efektif

**Ini bukan jumlah instrumen.** 25 instrumen yang saling berkorelasi 0.30 memberi `K_eff = 3.05`,
bukan 25.

```
Metode 1 (resmi, eigenvalue):  K_eff = (Σ λᵢ)² / Σ λᵢ²
Metode 2 (equicorrelated):     K_eff = K / (1 + (K−1)·ρ̄)
```

| ρ̄ rata-rata | K_eff pada K=25 |
|---:|---:|
| 0.30 | 3.05 |
| 0.20 | 4.31 |
| 0.10 | 7.35 |
| 0.05 | 11.36 |

> **WAJIB:** hitung ulang tabel ini dari rumusnya. Kalau hasil hitung beda dari tabel, **pakai hasil
> hitung dan laporkan** (§power_analysis.c.catatan_verifikasi).

**Yang paling sering salah:** korelasi yang dihitung harus korelasi **PnL STRATEGI** antar instrumen,
**BUKAN korelasi harga**. Dua instrumen bisa berkorelasi harga 0.9 tapi PnL strateginya berkorelasi 0.1,
dan sebaliknya.

### Syarat lolos

```
K_eff_dibutuhkan = (t_target / t_single)²

IC 0.05 → t_single 1.74 → K_eff harus ≥ 2.97
IC 0.03 → t_single 1.04 → K_eff harus ≥ 8.32   ← skenario pesimistis
```

⛔ `K_eff` terukur < yang dibutuhkan pada IC 0.05 → **STOP di F0**, sebelum kandidat pertama.
⛔ `K_eff` < 3 → **jangan jalankan apapun** (§trial_budget.tangga_pemangkasan).

### Implikasi pemilihan panel

**8 instrumen tidak berkorelasi lebih berharga daripada 25 instrumen yang saling berkorelasi 0.3.**
Panel dipilih untuk **meminimalkan korelasi PnL**, bukan memaksimalkan jumlah instrumen.
Ini kebalikan dari naluri kebanyakan orang.

---

## 2. Dedup — membunuh kandidat kembar

```yaml
corr_threshold: 0.90
vs_same_division: "korelasi >= 0.90 -> alias, tidak masuk registry"
vs_graveyard:     "korelasi >= 0.90 -> auto-kill, tidak dijalankan"
computed_on: partisi_screen
```

Kenapa ini penting secara aritmetika: **menambah kandidat menaikkan ambang untuk semua kandidat lain**
(§lessons_carried.8). Kandidat kembar tidak menambah informasi tapi tetap menaikkan N trial —
jadi dia merugikan kandidat yang benar-benar berbeda. Dedup adalah cara membela kandidat bagus.

Contoh nyata dari riset sebelumnya: **seluruh keluarga Kalman punya korelasi 1.000 antar varian.**
Itu bukan 6 kandidat, itu 1 kandidat yang dihitung 6 kali.

---

## 3. Formula pengukur ketergantungan di registry

Formula yang mengukur ketergantungan nonlinear — berguna justru karena korelasi Pearson buta
terhadap hubungan nonlinear.

| ID | Divisi asal | Varian | Tier | Rumus (ringkas) |
|---|---|---:|---|---|
| `E95_MUTUAL_INFORMATION_LAG` | E | 4 | T3 | I(X_t ; X_{t-L}) estimator k-nearest-neighbour Kraskov |
| `E96_TRANSFER_ENTROPY_SELF` | E | 4 | T3 | TE = SUM p(x_{t+1}, x_t^k) * log[ p(x_{t+1}\|x_t^k) / p(x_{t+1}\|x_t^… |
| `E97_DISTANCE_CORRELATION` | E | 6 | T3 | dCor(X,Y) = dCov(X,Y)/sqrt(dVar(X)*dVar(Y)) ; nol jika dan hanya jika… |

> Ketiganya **tier-3 mahal**. DILARANG dijalankan penuh di seluruh panel saat screening.
> Prosedur: subsampel 20% partisi screen di 5 instrumen paling tidak berkorelasi dulu; yang gagal
> di subsampel ditandai `UNDERPOWERED_SCREEN`, **bukan** `REJECTED`.

---

## 4. Korelasi antar null benchmark

`§null_benchmarks.wajib_dilaporkan` menuntut dua hal yang sering dilewati:

- matriks korelasi antar null (B01–B08)
- **jumlah null independen efektif** lewat eigenvalue matriks korelasinya

Alasannya sama persis dengan K_eff: kalau `ALWAYS_LONG` (B06) dan `BUY_AND_HOLD` (B01) berkorelasi 0.95,
mengalahkan keduanya bukan dua rintangan — itu satu rintangan yang dihitung dua kali.

---

## 5. Checklist korelasi per fase

- [ ] **F0** — matriks korelasi PnL strategi baseline antar instrumen, `K_eff` eigenvalue, `K_eff` dibutuhkan, verdict gerbang
- [ ] **F0** — `screen_max = min(500, floor(50 × K_eff))` dihitung, bukan diasumsikan
- [ ] **F1** — matriks korelasi antar null + jumlah null independen efektif
- [ ] **F2b** — `K_eff` dihitung ulang **per horizon** (K_eff berbeda di horizon berbeda)
- [ ] **F3** — dedup vs divisi sendiri & vs graveyard, ambang 0.90
- [ ] **F6/F7** — korelasi PnL antar survivor sebelum masuk CONFIRM
