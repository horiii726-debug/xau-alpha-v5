# RESUME — XAU Alpha V5, checkpoint 2026-08-22 ~03:55 UTC

> Ditulis untuk melanjutkan sesi ini di VPS/environment lain. Baca
> `xau_v5/00_KONTRAK_DAN_KELAYAKAN.md` sampai `07_FASE_EKSEKUSI.md` dulu
> kalau belum familiar — file ini asumsi Anda (atau Claude Code sesi
> berikutnya) sudah tahu aturan dasarnya, ini murni status + cara lanjut.

## Posisi fase

| Fase | Status | Ringkas |
|---|---|---|
| F0 | **TIDAK FORMAL SELESAI** | Tidak ada `config/v5.yaml` + hash resmi. Yang ada sebagai penggantinya: `xau_v5/PATCH_01_ANGGARAN.md` + `.sha256` (kunci pra-registrasi utk keputusan anggaran/tangga pemangkasan/Adendum Z saja, BUKAN config F0 penuh). K_eff/BR efektif/screen_max **belum pernah dihitung dari data nyata** — semua kerja setelah ini jalan sebagai EKSPLORASI pada panel 1-2 instrumen, bukan lewat gerbang F0 resmi. Ini penyimpangan sadar atas instruksi user eksplisit ("jangan batalkan fase karena panel kurang, jalankan tetap, tandai UNDERPOWERED_PANEL").
| F1 | ✅ **LULUS** | 30/30 test. Uji kebocoran §L10 lolos (IC fitur bocor sengaja = 0.80, kalahkan semua null B01-B08). Sanity: sinyal acak murni tidak mengalahkan null (false-positive rate MC1 terukur ~7%, dekat nominal 5%). Detail: `reports/F1_infrastruktur_validasi.md`.
| F2 | ✅ **SELESAI — NOL LOLOS** | XAUUSD, 5 horizon (H15/H30/H60/H120/H240), granularitas M1 (bukan M5/M15), 20.000 entry acak/sisi/kombinasi. Ambang lengkap (margin+gap+net_bps+sign_flip+stability): **0 kombinasi lolos di horizon manapun**. Sisi long tampak menang di cek dasar (drift capture, XAUUSD naik 2021-2026) tapi gugur juga di stability 3-subperiode. Detail: `reports/F2_payoff_gate.md`, `reports/F2_langkah2_sesi_jam.md` (jendela biaya per sesi/jam — juga nol, 7 dari ~5040 uji lolos ambang, konsisten multiple-testing noise).
| F2b | **BELUM DIKERJAKAN** | — |
| F3 | **BELUM DIKERJAKAN** | 129 sitasi masih NEED_LOOKUP, 0 diverifikasi. |
| F4 | ⚠️ **SEBAGIAN** | V: 28/41 varian diuji, MCS alpha=0.10 → 7 survivor (bipower variation, MedRV, MinRV @w48/w96, GARCH baseline), juara tie-break `V07_BIPOWER_w48`. Q: 7/35 varian, 1 survivor `Q02_CORWIN_SCHULTZ_w48`. **T: 0/27, BLOKIR** — butuh timestamp tick individual, hilang sejak pindah ke candle M1 (lihat bagian Data). Detail: `reports/F4_estimation_champions.md`.
| F5 | ✅ **SELESAI — NOL LOLOS** | Divisi X (exit/sizing), 34 kandidat (barrier X01-X03/X06, EVT stop X10-X11, optimal-stopping X20-X23, sizing X31-X33), entry acak H60, gate_checklist 15/17 centang tergradasi (MC2 PENDING, panel-consistency N/A). **0 lolos ≥13/15**. Expectancy terbaik: **-1.81 bps** (X10_POT_GPD). Detail: `reports/F5_exit_sizing.md`.
| F6 | ⚠️ **PARSIAL — DIHENTIKAN MANUAL** | Run skala PENUH (451.008 bar) di-launch 3x. Percobaan 1: macet — bug O(n²) nyata di `e10_variance_ratio_lm` (rolling-sum dihitung ulang di seluruh array tiap bar), DIPERBAIKI + diverifikasi (output numerik identik, 103/103 test tetap hijau). Percobaan 2: refactor internal sempat bikin proses diam sampai 56 sinyal selesai baru cetak progres — DIPERBAIKI jadi generator progresif. Percobaan 3: jalan normal, tapi **DIHENTIKAN atas instruksi eksplisit user** setelah 11/56 sinyal dasar selesai dievaluasi (E01 x4, E10 x4, E22 x3) — **di data PENUH, bukan smoke test**. Semua 11 gross expectancy NEGATIF. 45 sinyal sisanya + semua kombinasi entry×exit + batch checks (BH-FDR/DSR/PBO) BELUM sempat jalan. Detail & vonis parsial: `reports/F6_screening.md`. Cara lanjut: lihat perintah di bawah.
| F7 | ⚠️ **KODE DIPERLUAS, BELUM DIJALANKAN PENUH** | M06/M07/M08 (Lasso/Ridge/ElasticNet) + **M01/M02/M03 tree-ensemble (CatBoost/XGBoost monotone/LightGBM) baru ditambahkan** + M11 meta-labeling dengan primer **dipilih dinamis** dari net-expectancy terbaik F6 (bukan hardcode) — semua kode sudah ditulis dan LOLOS smoke-test (30.000 bar, terbukti jalan tanpa error). **TAPI belum pernah dijalankan di skala penuh** karena F6 (sumber primer M11) sendiri belum selesai. `reports/F7_meta_ml.md` isinya HASIL SMOKE-TEST LAMA (pra tree-ensemble utk sebagian, primer M11=E80_QUANTREG_tau0.25 dari F6 smoke-test lama) — **ditandai tebal di header file, JANGAN dibaca sebagai final**.
| F8-F11 | **TIDAK DIMULAI** | Sesuai instruksi: berhenti sebelum F8, jangan pre-register, jangan buka holdout. |

**Kesimpulan sementara (BUKAN final — F6 baru 11/56 sinyal, F7 belum jalan penuh, F4/T blokir, panel cuma 1-2 instrumen):**
F2 dan F5 (selesai penuh) NOL LOLOS. F6 (11/56 sinyal, data penuh) semuanya gross negatif sejauh ini tapi
sampelnya kecil dan bukan representatif (formula yang sempat diuji secara historis memang lemah). F7 kode-nya
siap tapi belum ada hasil skala-penuh sama sekali. Terlalu dini untuk kesimpulan definitif — TIDAK bisa bilang
"4/4 nol" karena 2 dari 4 fase itu (F6, F7) belum benar-benar selesai diuji. Lihat `protokol_nol_lolos` di
`xau_v5/06_GERBANG_DAN_ANGGARAN.md` untuk langkah SETELAH semua fase benar-benar tuntas.

---

## Data yang sudah ada

| Instrumen | Hari (dari 1826, 2021-08-22 s/d 2026-08-21) | Rentang aktual | Format |
|---|---:|---|---|
| XAUUSD | **1826/1826 (100%)** | 2021-08-22 s/d 2026-08-21 | M1 candle, bid+ask OHLC |
| XAGUSD | **1206/1826 (66%)** | 2021-08-22 s/d 2024-12-09 (kontinu dari awal) | M1 candle, bid+ask OHLC |
| EURUSD | 0/1826 | — | belum diunduh |
| USOIL (kode Dukascopy: `LIGHTCMDUSD`) | 0/1826 | — | belum diunduh |

- Lokasi: `data/raw_candles/{SYMBOL}/{SYMBOL}_YYYYMMDD.parquet`, 1 file/hari.
- Kolom per file: `ts_s` (unix seconds, UTC), `bid_open/high/low/close/vol`, `ask_open/high/low/close/vol`,
  `spread` (ask_close-bid_close), `mid_close`, `spread_bps`.
- Sumber: Dukascopy datafeed candle M1 (`BID_candles_min_1.bi5` / `ASK_candles_min_1.bi5`) —
  **BUKAN tick individual** (diganti dari tick demi kecepatan download setelah rate-limit
  Dukascopy bikin unduh tick 5 tahun x 4 instrumen ≈ 51+ jam; M1 candle 12x lebih sedikit request).
  Konsekuensi: **Divisi T (intensitas tick) tidak bisa dijalankan** — butuh timestamp antar-tick individual.
- Hash SHA256 gabungan seluruh `data/raw_candles/*.parquet` (sorted filename, sha256 per file lalu
  di-sha256 lagi): `fda2d07f61e1ffcc6503c2d0023761bf24929ae444fb0c1ebc59e560deb7835d`
  — **BELUM diverifikasi ulang**, dicatat sekali saat checkpoint ini dibuat, bukan hash resmi F0.
- Bar M5/M15 hasil agregasi ada di `data/bars_candles/` (regenerasi cepat dari `raw_candles/`, lihat
  `data/aggregate_bars_candles.py` — TIDAK di-commit ke git, terlalu besar & mudah dibuat ulang).
- Rate limit Dukascopy: **~1 request/detik aman, lebih dari itu langsung 429/503**. Sudah dikonfirmasi
  empiris (bukan tebakan) — lihat commit history untuk detail eksperimen. `data/download_candles.py`
  sudah punya backoff eskalasi (5/10/20/40/80/120 detik) + circuit breaker (20 gagal beruntun → tidur
  30 menit lalu reset). **Kalau lanjut download XAGUSD/EURUSD/USOIL: jalankan langsung, jangan disetel
  lebih agresif, akan diblokir lagi.**

---

## Yang masih LOOKUP (belum dicari / belum lengkap)

- `markup_prop_firm_pct`, `komisi` (USD/lot round-trip), `swap` long/short/triple-day — **semua masih
  LOOKUP**. FTMO menyembunyikan angka spesifik XAUUSD di balik widget JS (WebFetch tidak bisa baca).
- MC2 (`P(breach dalam 250 trade) <= 5%`) — **PENDING_COST_LOOKUP di semua kandidat**, bukan FAILED,
  sesuai instruksi user. Parameter YANG SUDAH ADA dari riset sebelumnya (F0 awal, sumber: ftmo.com resmi):
  - FTMO 1-Step: daily loss 3%, max loss 10% (trailing, naik seiring ekuitas puncak)
  - FTMO 2-Step: daily loss 5%, max loss 10% (statis)
  - Profit target: 10% (challenge), 5% (verification)
  - FundedNext/The5ers: angka dari agregator pihak ketiga, BELUM diverifikasi ke sumber resmi.
  - Ini SUDAH CUKUP untuk menjalankan MC2 kalau mau — cuma belum di-wire ke `src/costs/cost_model.py`.
- Cost model saat ini pakai proxy kasar `COST_BPS_WORST = 3.0` bps di semua skrip F5/F6/F7 —
  **bukan angka terverifikasi**, ditandai jelas di tiap laporan.

---

## Cakupan formula yang sudah diimplementasi (dari 507+17 total registry)

| Divisi | Diimplementasi | Total registry | File |
|---|---:|---:|---|
| V (volatilitas) | 14/14 formula (28/41 varian diuji) | 41 varian | `src/formulas/division_v.py` |
| Q (spread) | 12/12 formula (7/35 varian diuji) | 35 varian | `src/formulas/division_q.py` |
| T (tick) | 0/10 — BLOKIR data | 27 varian | — |
| X (exit/sizing) | 15/22 formula diimplementasi, 34 varian diuji | 114 varian | `src/formulas/division_x_*.py` |
| E (entry) | 19/56 formula, 34+ varian diuji (sebagian smoke-test saja) | 209 varian | `src/formulas/pilot_f2b.py` + `division_e.py` |
| Z (Adendum) | 0/3 — tidak bisa diuji (butuh panel/sinyal lolos) | 17 varian | `src/formulas/` (belum ada, spec di `xau_v5/ADENDUM_Z_ENTRY.md`) |
| M (ML) | Lasso/Ridge/ElasticNet/meta-labeling/CatBoost/XGBoost(monotone)/LightGBM (7/15 formula, KODE siap semua) — TAPI tree-ensemble+M11-dinamis baru diverifikasi lewat smoke-test 30K bar, BELUM full-scale | 81 varian | `data/run_f7_division_m.py` |

Ini eksplorasi breadth-first pada anggaran waktu terbatas — BUKAN klaim registry penuh teruji.
Infrastruktur pengujian (gate_checklist 15/17, CPCV, MCS, null benchmarks, MC1/3/5, numba JIT triple-barrier)
SUDAH lengkap dan reusable — menambah formula baru = tinggal panggil `evaluate_candidate()`.

---

## Perintah persis untuk melanjutkan

```bash
# 1. Clone & masuk
git clone <URL_REPO_INI> xau-alpha-v5 && cd xau-alpha-v5

# 2. Setup environment (Python 3.12, Ubuntu 24.04 diasumsikan; gcc/g++ harus ada untuk numba)
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# 3. Verifikasi semua test masih hijau
pytest tests/ -v   # harus 103/103 passed

# 4. LANGKAH BERIKUTNYA YANG PALING PENTING -- F6 baru 11/56 sinyal, SELESAIKAN dulu:
python data/run_f6_division_e.py
# TIDAK ADA checkpoint parsial di dalam skrip -- run ini akan mengulang dari
# sinyal pertama (E01), bukan lanjut dari sinyal ke-12. Estimasi total waktu
# ~35-45 menit di 451.008 bar (E01+E10 cepat ~1 menit total, E22/E30/E70/E20
# yang berat -- SUDAH di-benchmark per-formula, BUKAN dugaan, lihat riwayat
# teknis di reports/F6_screening.md). JANGAN interupsi kalau tidak perlu --
# progres tercetak per sinyal (~1-4 menit per baris untuk formula berat),
# diam beberapa menit itu WAJAR bukan macet, cek `ps` kalau ragu.
# Akan menimpa reports/F6_screening.md dengan hasil PENUH.

# 5. Setelah F6 BENAR-BENAR selesai (semua 56 sinyal + kombinasi entry x exit
#    + apply_batch_checks jalan sampai akhir skrip, exit code manapun OK):
python data/run_f7_division_m.py
# M11 akan otomatis pakai sinyal E net-expectancy terbaik dari F6_screening.md
# yang BARU (parsing otomatis, lihat load_best_f6_base_signal_name() di skrip).
# ~10-15 menit (CPCV 12 path x ~10 model linear+tree, subsample 15rb baris).

# 6. Setelah F6 DAN F7 selesai penuh, cek vonis akhir 4 fase (F2,F5,F6,F7):
#    Kalau SEMUA nol lolos -> jalankan protokol_nol_lolos dari langkah 1
#    (xau_v5/06_GERBANG_DAN_ANGGARAN.md), MULAI dari langkah 3 (perbesar
#    panel) karena langkah 1 (horizon) sudah dicoba (F2, gagal semua) dan
#    langkah 2 (sesi/jam) juga sudah dicoba (gagal, lihat F2_langkah2_sesi_jam.md).

# 7. Kalau mau lanjut panel: resume download XAGUSD dari hari 1207, lalu EURUSD, USOIL:
python data/download_candles.py --start 2021-08-22 --end 2026-08-21
# Skrip otomatis skip hari yang sudah ada (resumable), JALANKAN VIA nohup:
nohup python -u data/download_candles.py --start 2021-08-22 --end 2026-08-21 \
  > data/logs/download_candles.log 2>&1 &
# Estimasi: XAGUSD sisa ~620 hari + EURUSD/USOIL 1826 hari masing-masing,
# @ ~1 req/detik, 2 req/hari (BID+ASK) -> total sisa ~(620+1826*2)*2/1 detik
# = sekitar 2.9 jam kalau lancar, BISA lebih lama kalau kena rate-limit lagi
# (skrip sudah self-healing, cuma lambat).

# 8. Rebuild ledger setelah fase baru selesai:
python data/build_ledger.py
```

---

## Struktur repo

```
xau_v5/                    -- 20 file spesifikasi .md (sumber kebenaran aturan/formula)
src/
  stats/                   -- effective_n (LdP uniqueness), nulls (B01-B09)
  validation/               -- cpcv, montecarlo (MC1-5), mcs (Model Confidence Set), gate_checklist
  labeling/                 -- triple_barrier (numba JIT)
  costs/                    -- cost_model
  formulas/                 -- division_v, division_q, division_x_*, division_e, pilot_f2b
data/                       -- semua skrip runner (download_candles.py, run_f*.py, build_ledger.py)
data/raw_candles/           -- data M1 mentah (lihat tabel Data di atas)
tests/                      -- 103 test, semua hijau
reports/                    -- laporan tiap fase (.md)
ledger_trials.csv           -- konsolidasi semua kandidat yang diuji (76 baris per checkpoint ini --
                                TURUN dari checkpoint sebelumnya 108 karena 55 baris F6 SMOKE-TEST LAMA
                                digantikan 11 baris F6 PARSIAL SKALA-PENUH yang lebih valid, dan F7
                                sekarang 29 baris smoke-test M01-M11 vs 17 sebelumnya M06-M11 saja)
PATCH_01_ANGGARAN.md + .sha256  -- (di xau_v5/) kunci pra-registrasi keputusan anggaran ronde 1+2
requirements.txt            -- freeze pip lengkap (140 paket)
```

---

## DAFTAR YANG BELUM DIUJI (per divisi, dicek ke `ledger_trials.csv` -- BUKAN ditebak)

**Divisi V (volatilitas, 14 formula/41 varian):** 28/41 varian teruji (F4). Belum: 13 varian sisa
(kombinasi window/estimator yang belum sempat di grid F4 karena anggaran waktu). Lihat `reports/F4_estimation_champions.md`.

**Divisi Q (spread, 12 formula/35 varian):** 7/35 varian teruji (F4). Belum: 28 varian sisa.

**Divisi T (intensitas tick, 10 formula/27 varian):** 0/27. BLOKIR total -- butuh timestamp tick individual,
data yang ada cuma M1 candle. Perlu re-download tick-level utk instrumen manapun sebelum divisi ini bisa jalan sama sekali.

**Divisi X (exit/sizing, 22 formula/114 varian):** 34 varian teruji (F5, semua di ledger trial_id 1-36),
15/22 formula diimplementasi. Belum diimplementasi: X15-X19, X25-X29 (lihat `xau_v5/DIVISI_X_EXIT_SL_TP_SIZING.md`
utk daftar lengkap ID). Vonis F5: NOL LOLOS, terbaik -1.81bps (X10_POT_GPD).

**Divisi E (entry, 56 formula/209 varian):** HANYA 11/56 formula-varian teruji SEJAUH INI (E01 x4, E10 x4,
E22 x3 -- di ledger trial_id 37-47, formula_id E01/E10/E22), semua di data skala PENUH. 45 sinyal dasar
BELUM tersentuh sama sekali di run ini: E22 sisa (1 varian), E30, E60, E70, E90 (7 formula pilot sisa),
E02, E03, E04, E11, E20, E50, E54, E64, E71, E73, E80, E81 (12 formula tambahan). Plus formula yang dari
awal tidak diimplementasi: E12, E21, E23-E29, E31-E36, E40-E45, E51-E53/E55, E61-E63/E65, E72/E74/E82/E83,
E91-E97 (lihat `xau_v5/DIVISI_E_ENTRY_ARAH.md`). **Belum ada vonis** -- run dihentikan manual sebelum cukup data.

**Divisi M (ML, 15 formula/81 varian):** KODE utk 7/15 formula (M06/M07/M08/M11 + M01/M02/M03 baru)
SUDAH SIAP, tapi HANYA diverifikasi lewat smoke-test 30K bar (ledger trial_id 48-76, semua status
`gross_bps=` di notes, BUKAN hasil final). Belum diimplementasi sama sekali: M04/M05/M09/M10 (formula
tree/ensemble lain di luar CatBoost/XGBoost/LightGBM), M12-M15 (lihat `xau_v5/DIVISI_M_ML_METALABELING.md`).

**Adendum Z (3 formula/17 varian):** 0/3, TIDAK BISA diuji dengan data/hasil yang ada (Z02/Z03 butuh
panel >1 instrumen dengan histori sebanding, Z01 butuh sinyal E yang sudah lolos F6 sebagai input).

**Ledger:** 76 baris total (F2: 0 baris granular -- lihat poin 5 di bawah, tapi F2 tetap SELESAI dan
vonisnya NOL LOLOS di level agregat; F5: 36; F6: 11; F7: 29). `screen_max`/anggaran trial resmi
BELUM pernah dihitung dari K_eff nyata (poin 4 di bawah) -- semua nomor di atas adalah HITUNGAN
EKSPLORASI, bukan dibandingkan ke anggaran resmi.

---

## Catatan integritas yang WAJIB dibaca sebelum lanjut

1. **F6 baru 11/56 sinyal, F7 belum jalan skala penuh sama sekali.** Jangan kutip `reports/F6_screening.md`
   atau `reports/F7_meta_ml.md` sebagai hasil final — kedua file sudah diberi peringatan tebal di headernya,
   tapi tegaskan lagi di sini supaya tidak terlewat.
2. **Ledger `ledger_trials.csv` tidak lengkap secara kolom** — `eff_n`, `ic`, `p_raw`/`p_effN`, `sharpe`,
   `max_dd`, `capture_ratio` kosong karena tidak dipersist individual saat run (cuma t_stat, n_trades,
   expectancy_bps, dan jumlah centang lolos yang disimpan). Kalau mau kolom itu terisi, perlu re-run
   dengan logging tambahan di `src/validation/gate_checklist.py`, bukan ditebak sekarang.
3. **Cost model masih proxy** (`COST_BPS_WORST=3.0` bps hardcoded) — bukan angka terverifikasi dari
   markup prop firm / komisi / swap asli. Semua expectancy_bps di laporan F5/F6/F7 pakai proxy ini.
4. **F0 formal belum ada.** K_eff belum pernah dihitung dari korelasi PnL strategi lintas instrumen
   (baru bisa setelah panel >=2 instrumen lengkap). `screen_max` yang dipakai sepanjang F4-F7 BUKAN
   hasil formula `min(500, floor(50*K_eff))` — semua dijalankan sebagai eksplorasi tanpa anggaran resmi,
   sesuai instruksi eksplisit user.
5. **BARU DITEMUKAN saat checkpoint ini: `data/build_ledger.py` tidak bisa mem-parse detail per-kombinasi
   F2** (`reports/F2_payoff_gate.md` isinya ringkasan per-horizon, BUKAN tabel per k_sl/k_tp/side yang
   diharapkan parser F2-nya) — jadi ledger TIDAK punya baris individual utk ~200 kombinasi F2 yang
   sebenarnya dijalankan (cuma agregat "36/38/42/42/42 lolos margin dasar, 0 lolos semua syarat" di
   `F2_payoff_gate.md` sendiri). Vonis F2 (NOL LOLOS) tetap valid dan tidak berubah — ini murni gap
   granularitas ledger, bukan gap hasil. Belum diperbaiki karena di luar scope checkpoint ini
   (butuh keputusan: re-run F2 dengan log per-baris, atau terima gap ini).
