# RESUME — XAU Alpha V5, checkpoint 2026-08-22 ~01:45 UTC

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
| F6 | ❌ **TERPUTUS — TIDAK SELESAI** | Run penuh di-launch tapi DIHENTIKAN (`pkill`) atas instruksi user sebelum selesai. **`reports/F6_screening.md` yang ada di repo HANYA smoke test 50.000 bar (~11% dari 451.008 bar partisi SCREEN penuh)** — sudah ditandai jelas di file itu, JANGAN dipakai sebagai vonis final. Perintah lanjut: lihat di bawah. 19/56 formula E diimplementasi (di `src/formulas/pilot_f2b.py` + `src/formulas/division_e.py`), Adendum Z tidak bisa diuji (Z02/Z03 butuh panel >1 instrumen, Z01 butuh sinyal E yang sudah lolos).
| F7 | ✅ **SELESAI — NOL LOLOS** | M06/M07/M08 (Lasso/Ridge/ElasticNet, CPCV purged+embargo) + M11 meta-labeling. 16 kandidat, 0 lolos ≥13/15. Expectancy terbaik: **-0.89 bps** (M11_META_LABELING_t0.5). Temuan menarik: meta-labeling MENGALAHKAN sinyal primer polos (-0.89 vs -3.38 bps) — membaik signifikan meski belum positif, konsisten teori meta-labeling. Model tree-ensemble (CatBoost/XGBoost/LightGBM) TIDAK diuji — belum terpasang. Detail: `reports/F7_meta_ml.md`.
| F8-F11 | **TIDAK DIMULAI** | Sesuai instruksi: berhenti sebelum F8, jangan pre-register, jangan buka holdout. |

**Kesimpulan sementara (BUKAN final — F6 belum selesai, F4/T blokir, panel cuma 1-2 instrumen):**
Empat dari lima fase yang selesai (F2, F5, F7, dan F6-parsial) semuanya NOL LOLOS. Kalau F6 penuh juga nol,
itu 4/4 divisi arah (X, E, M) + gerbang payoff nol semua di XAUUSD — sinyal kuat bahwa data yang ada
(1 instrumen, 5 tahun, biaya belum lengkap) TIDAK cukup untuk membuktikan edge apapun, BUKAN berarti
tidak ada edge. Lihat `protokol_nol_lolos` di `xau_v5/06_GERBANG_DAN_ANGGARAN.md`.

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
| M (ML) | Lasso/Ridge/ElasticNet/meta-labeling (4/15 formula); tree-ensemble TIDAK (butuh catboost/xgboost/lightgbm, belum terpasang) | 81 varian | `data/run_f7_division_m.py` |

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
pytest tests/ -v   # harus 102/102 (atau lebih kalau ditambah) passed

# 4. LANGKAH BERIKUTNYA YANG PALING PENTING -- selesaikan F6 dulu (belum tuntas):
python data/run_f6_division_e.py
# ~10 menit di 451.008 bar penuh (skala dari smoke test: 66 detik utk 50.000 bar).
# Akan menimpa reports/F6_screening.md dengan hasil PENUH (bukan smoke test lagi).

# 5. Setelah F6 selesai, cek vonis akhir 4 fase (F2,F5,F6,F7):
#    Kalau SEMUA nol lolos -> jalankan protokol_nol_lolos dari langkah 1
#    (xau_v5/06_GERBANG_DAN_ANGGARAN.md), MULAI dari langkah 3 (perbesar
#    panel) karena langkah 1 (horizon) sudah dicoba (F2, gagal semua) dan
#    langkah 2 (sesi/jam) juga sudah dicoba (gagal, lihat F2_langkah2_sesi_jam.md).

# 6. Kalau mau lanjut panel: resume download XAGUSD dari hari 1207, lalu EURUSD, USOIL:
python data/download_candles.py --start 2021-08-22 --end 2026-08-21
# Skrip otomatis skip hari yang sudah ada (resumable), JALANKAN VIA nohup:
nohup python -u data/download_candles.py --start 2021-08-22 --end 2026-08-21 \
  > data/logs/download_candles.log 2>&1 &
# Estimasi: XAGUSD sisa ~620 hari + EURUSD/USOIL 1826 hari masing-masing,
# @ ~1 req/detik, 2 req/hari (BID+ASK) -> total sisa ~(620+1826*2)*2/1 detik
# = sekitar 2.9 jam kalau lancar, BISA lebih lama kalau kena rate-limit lagi
# (skrip sudah self-healing, cuma lambat).

# 7. Rebuild ledger setelah fase baru selesai:
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
tests/                      -- 102 test, semua hijau
reports/                    -- laporan tiap fase (.md)
ledger_trials.csv           -- konsolidasi semua kandidat yang diuji (108 baris per checkpoint ini)
PATCH_01_ANGGARAN.md + .sha256  -- (di xau_v5/) kunci pra-registrasi keputusan anggaran ronde 1+2
requirements.txt            -- freeze pip lengkap (140 paket)
```

---

## Catatan integritas yang WAJIB dibaca sebelum lanjut

1. **F6 belum selesai.** Jangan kutip `reports/F6_screening.md` sebagai hasil final — file itu sudah
   diberi peringatan tebal di headernya, tapi tegaskan lagi di sini supaya tidak terlewat.
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
