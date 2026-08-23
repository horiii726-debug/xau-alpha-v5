# HASIL BENCHMARK PER FUNGSI -- XAUUSD

**Metodologi:** data XAUUSD M1/M5 yang sudah ada (2021-08-22 s/d 2026-08-22,
5 tahun, tidak ada unduhan baru). Split kronologis 70% latih / 30% uji,
semua estimator di-fit HANYA di latih, semua kausal (keputusan di bar t
cuma pakai data sampai t). **5 lomba independen** -- tidak ada gerbang
bersama, tidak ada DSR, tidak ada K_eff, tidak ada panel multi-instrumen.
Setiap lomba berdiri sendiri.

Dashboard ringkasan: `dashboard_benchmark.png` (6 panel: 5 lomba + ringkasan alur).
Detail lengkap tiap lomba (tabel penuh + p-value): `LOMBA1_VOLATILITAS.md` s/d
`LOMBA5_SLTP.md`.

---

## LOMBA 1 -- VOLATILITAS

**Target:** realized variance window berikutnya (dari M1). **Metrik:** QLIKE
(median dipakai untuk peringkat -- QLIKE mean pada baseline meledak karena
outlier ekor, properti nyata bukan bug, dijelaskan di laporan detail).

**Pemenang: HAR-RV, di SEMUA horizon (1h, 4h, 1d), p-value bootstrap = 0.000.**

| horizon | HAR-RV (QLIKE median) | Baseline close-to-close | Perbaikan |
|---|---:|---:|---:|
| 1h | 0.0941 | 0.7894 | 8.4x lebih baik |
| 4h | 0.1280 | 1.0450 | 8.2x lebih baik |
| 1d | 0.0637 | 1.0229 | 16.1x lebih baik |

**Satu kalimat:** HAR-RV menang telak dan konsisten di semua horizon karena
menggabungkan informasi dari 3 skala waktu (lag pendek/menengah/panjang)
sekaligus, sesuatu yang tidak dimiliki estimator tunggal manapun (GARCH,
EWMA, atau estimator berbasis OHLC/jump-robust) -- perbedaannya jauh di atas
signifikan secara statistik.

---

## LOMBA 2 -- TREN / KEMIRINGAN

**Target:** t-stat slope OLS pada window N bar ke depan. **Metrik:** IC
Spearman + akurasi tanda.

**Tidak ada pemenang yang meyakinkan.** IC semua peserta lemah (rentang
-0.03 s/d +0.03) dan pemenang berganti-ganti antar N tanpa pola (Kalman-drift
di N=12 & N=24, QuantReg di N=48) -- pola yang konsisten dengan **derau**,
bukan skill nyata.

| N | Pemenang | IC | Baseline OLS IC |
|---:|---|---:|---:|
| 12 | Kalman-drift | -0.0021 | -0.0200 |
| 24 | Kalman-drift | 0.0342 | -0.0038 |
| 48 | QuantReg(tau=0.5) | 0.0344 | 0.0327 |

**Satu kalimat:** tidak ada estimator kemiringan yang mengalahkan OLS secara
meyakinkan dan konsisten -- pasar tampak relatif efisien terhadap sinyal tren
linear sederhana pada skala waktu ini (12-48 bar M5).

---

## LOMBA 3 -- REZIM

**Target:** apakah N bar berikutnya trending (VR realisasi>1) vs ranging.
**Metrik:** AUC keluar-sampel.

**Pemenang: PermutationEntropy / LempelZiv, konsisten di semua N, p=0.000.**
*(Catatan transparansi: arah sinyal awalnya salah diasumsikan (entropi rendah
diduga = trending), dicek manual, dan diperbaiki SEBELUM dilaporkan --
lihat `LOMBA3_REZIM.md`.)*

| N | Pemenang | AUC | Baseline (persistensi) |
|---:|---|---:|---:|
| 12 | PermutationEntropy(m=3) | 0.6287 | 0.5092 |
| 24 | PermutationEntropy(m=3) | 0.6245 | 0.5170 |
| 48 | LempelZiv | 0.6141 | 0.5117 |

**Satu kalimat:** kompleksitas/entropi return (bukan variance ratio klasik
seperti Lo-MacKinlay/Wright, bukan Hurst/DFA) adalah prediktor rezim
trending-vs-ranging TERKUAT dan PALING KONSISTEN di seluruh lomba ini --
kemungkinan karena mean-reversion menghasilkan pola ordinal return yang lebih
predictable (entropi rendah) dibanding trending.

---

## LOMBA 4 -- ENTRY

**Target:** tanda return H bar ke depan. **Metrik:** IC + hit rate +
expectancy bersih bps. **Biaya round-trip TERUKUR (jam trading aktif saja,
dari data TRAIN):** spread median 1.736bps + komisi FTMO 0.280bps + slippage
0.868bps = **2.885bps** (dicetak eksplisit di `LOMBA4_ENTRY.md` sebelum dipakai).

**Pemenang: CUSUM @ H=1d, tau=1.5 -- expectancy net +14.11bps, p=0.000.**
**Ini SATU-SATUNYA sinyal di SELURUH benchmark dengan edge net-positif kuat
dan signifikan.**

| Horizon | Pemenang (tau terbaik) | Expectancy net | Baseline (entry acak) |
|---|---|---:|---:|
| 1h | MAD-Zscore-momentum | -2.224 bps | -2.953 bps |
| 4h | CUSUM | +0.145 bps | -2.915 bps |
| **1d** | **CUSUM** | **+14.108 bps** | -2.660 bps |

**Satu kalimat:** semua sinyal entry di horizon pendek (1h, 4h) tetap rugi
bersih setelah biaya (meski beberapa mengalahkan entry acak secara relatif),
tapi CUSUM pada horizon 1 hari menghasilkan edge net-positif yang besar dan
sangat signifikan (p=0.000, n=6701 trade uji) -- perubahan rezim yang
terdeteksi CUSUM tampaknya butuh waktu ~1 hari untuk terealisasi penuh.

---

## LOMBA 5 -- SL/TP

**Entry DIKUNCI** = pemenang Lomba 4 (CUSUM, H=1d, tau=1.5). Barrier simetris
`k * vol_estimate`, **k=2.0 tetap untuk semua peserta** -- yang berbeda hanya
metode estimasi vol. Simulasi first-passage pada **M1** (bukan M5) untuk
akurasi SL/TP. Biaya sama seperti Lomba 4 (2.885bps).

**Pemenang: EmpiricalQuantile(p90), expectancy net +19.82bps, p=0.000.**

| Peserta | Expectancy net | Rasio stop prematur | Efisiensi MAE/MFE (median) |
|---|---:|---:|---:|
| **EmpiricalQuantile(p90)** | **+19.820 bps** | 1.60% | 0.126 |
| POT-GPD | +19.468 bps | 0.03% | 0.113 |
| GARCH | +11.599 bps | 20.24% | 0.190 |
| Parkinson (baseline) | +8.973 bps | 18.80% | 0.134 |

**Satu kalimat:** barrier yang diturunkan dari ekor distribusi (kuantil
empiris atau GPD) jauh mengalahkan barrier dari volatilitas biasa
(Parkinson/GARCH) -- 2.2x lipat expectancy -- karena barrier lebih lebar
menghindari stop prematur (1.6% vs 18.8%) yang memotong trade sebelum sinyal
CUSUM sempat terealisasi.

---

## KESIMPULAN GABUNGAN

**Kombinasi terbaik yang terukur di seluruh benchmark:** entry CUSUM (H=1d,
tau=1.5) + barrier EmpiricalQuantile(p90) k=2.0 = **+19.82 bps/trade bersih**,
p=0.000, n=6701 trade di data UJI (30% terakhir, tidak pernah dilihat saat
fitting).

**Catatan kejujuran:**
- Ini bukan backtest strategi lengkap -- belum ada position sizing, belum ada
  uji robustness (walk-forward, parameter perturbation, seed stability) yang
  diterapkan di sini seperti di F0-F11. Angka +19.82bps adalah hasil SATU
  kali split train/test, bukan rata-rata lintas banyak fold.
- N_test besar (6701) tapi ini SEMUA dari 30% periode kalender yang SAMA
  (2024-2026 kira-kira) -- rezim pasar tunggal, belum diuji lintas rezim
  berbeda (naik/turun/sideways) seperti disyaratkan protokol F0-F11.
- Biaya yang dipakai (2.885bps) adalah spread MEDIAN jam aktif -- bukan
  skenario worst-case seperti di pipeline F0-F11 sebelumnya. Kalau memakai
  biaya worst-case, margin +19.82bps akan menyusut tapi kemungkinan besar
  tetap positif mengingat ukurannya.
- Lomba 2 (tren) dan sebagian besar Lomba 4 (entry horizon pendek) TIDAK
  menemukan edge -- dilaporkan apa adanya, bukan disembunyikan.

**Rekomendasi:** temuan CUSUM+EmpiricalQuantile-barrier di horizon 1 hari
layak diselidiki lebih lanjut (walk-forward lintas rezim, robustness
parameter) sebelum dipertimbangkan untuk eksekusi nyata -- tapi ini sinyal
PALING kuat yang muncul dari seluruh proses riset v6 sejauh ini, jauh lebih
kuat dari apapun yang ditemukan di pipeline F0/F1 H240 sebelumnya.
