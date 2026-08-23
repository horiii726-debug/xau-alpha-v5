# Verifikasi angka paket v6

Setiap angka di paket ini dihasilkan script di folder ini. **Wajib dijalankan ulang
sebelum F0 dikunci** (§working_rules.9: "Setiap tabel angka WAJIB dihitung ulang dari
rumusnya. Beda -> pakai hasil hitung, laporkan.")

| script | menghasilkan |
|---|---|
| `verify.py` | K_eff, Fundamental Law, t_single/t_pooled, partisi, TIER-A vs TIER-B |
| `verify2.py` | transmitansi gerbang v5 vs corong v6, DSR vs N |
| `verify3.py` | BR lintas panel, Sharpe wajib vs N & sd_SR, batas anggaran |
| `verify4.py` | biaya bps, kappa per horizon, aturan akun prop firm |
| `verify5.py` | koreksi satuan beta slippage, MC2 P(breach) per ukuran posisi |
| `verify6.py` | frontier P(target) vs P(breach), imbal hasil tahunan, rekap |
| `v7.py` | komposisi registri, tangga pemangkasan, verifikasi lantai |

```bash
for f in verify.py verify2.py verify3.py verify4.py verify5.py verify6.py v7.py; do
  echo "=== $f ==="; python3 "$f"; done
```

## Asumsi yang WAJIB diganti hasil ukur di F0

| asumsi | dipakai di | pengganti |
|---|---|---|
| `rho_pnl = 0.15` | K_eff = 3.90 | matriks korelasi PnL strategi NYATA (eigenvalue) |
| `trades/thn`, `keunikan` per horizon | BR_eff | pengukuran per instrumen per horizon |
| `sd_SR = 0.25` | N_maks = 34 | **pilot 24 trial di F0** |
| `skew=0, kurt=3` | penyebut DSR | momen empiris return kandidat |
| `sigma harian emas = 100 bps` | kappa | pengukuran per rezim |
| `spread $0.15-0.30` | biaya bps | tick Dukascopy + markup prop firm |
| `Sharpe 1.15` | MC2 | distribusi trade NYATA kandidat, bukan Gaussian |

Kalau hasil ukur berbeda material, **seluruh anggaran dan gerbang dihitung ulang
sebelum kandidat pertama dijalankan.**

## Script koreksi (dijalankan setelah audit internal)

| script | menghasilkan |
|---|---|
| `fix1_koreksi_tier.py` | TIER-A vs TIER-B dihitung KONSISTEN (draf awal mencampurnya), transmitansi & N_maks terkoreksi |
| `fix2_restruktur_corong.py` | diagnosis kenapa tahap-2 draf awal tidak bisa capai 70%, restruktur tahap menurut jenis bukti, tabel sensitivitas ρ_PnL |

**Angka yang MENGIKAT ada di dua script ini**, bukan di `verify.py`/`verify2.py`
(yang memakai konfigurasi campuran dari draf awal dan disimpan sebagai jejak audit).
