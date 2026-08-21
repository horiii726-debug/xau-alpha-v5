# F1 — Infrastruktur Validasi

> Dijalankan pada data SINTETIS (random walk yang dibangkitkan sendiri), sesuai instruksi: F1 tidak butuh data pasar nyata, hanya perlu membuktikan alat ukurnya sendiri jujur sebelum dipakai pada kandidat/data nyata di F2 dan seterusnya.

## pytest

30 passed, 0 failed (exit code 0)

## §L10 — Uji Kebocoran Wajib

- IC fitur bocor (sengaja pakai return masa depan) = **0.7996** (syarat: > 0.5) -> LOLOS
- Total return strategi bocor = 5.1210
- Mengalahkan SEMUA null (B01-B08)? -> **YA, LOLOS**

| Null | Total return | Bocor > Null? |
|---|---:|---|
| B01_BUY_AND_HOLD | 0.0364 | ya |
| B02_RANDOM_MATCHED | -0.0342 | ya |
| B03_BLOCK_PERMUTED | 0.0381 | ya |
| B04_TSMOM_12M | -0.0473 | ya |
| B05_COIN_FLIP | -0.0203 | ya |
| B06_ALWAYS_LONG | 0.0364 | ya |
| B07_ALWAYS_SHORT | -0.0364 | ya |
| B08_RANDOM_FREQ_MATCHED | 0.0155 | ya |

## Uji Sanity — Sinyal Acak Murni

- 100 sinyal acak murni (+-1 tanpa hubungan dengan return), diuji lewat MC1 permutation (gate: persentil >= 95)
- False positive rate (persentil >= 95 padahal sinyal murni acak) = **7.0%** (nominal ~5% diharapkan)
- Rata-rata persentil = 50.2, median = 49.8
- Verdict: LOLOS (di bawah 15% ceiling)

## Matriks Korelasi Null + Null Independen Efektif

> Dihitung pada data SINTETIS untuk memvalidasi mekanismenya. WAJIB dihitung ulang
> pada data panel NYATA begitu tersedia -- angka di bawah bukan angka final untuk F6/F7.

```
       B01    B04    B06    B07
B01  1.000  0.103  1.000 -1.000
B04  0.103  1.000  0.103 -0.103
B06  1.000  0.103  1.000 -1.000
B07 -1.000 -0.103 -1.000  1.000
```

K_eff null (metode eigenvalue) = 1.590 dari 4 null yang diuji
(B01 dan B06 identik by construction -- keduanya BUY_AND_HOLD/ALWAYS_LONG -- korelasi 1.0 diharapkan)

## Modul yang dibangun

- `src/stats/effective_n.py` -- Lopez de Prado uniqueness, concurrency, sample weights
- `src/stats/nulls.py` -- B01-B09 sebagai kode, null_correlation_matrix
- `src/validation/cpcv.py` -- CPCV purged + embargo, default 12 grup x 2 test = 66 path (cocok n_paths_min)
- `src/validation/montecarlo.py` -- MC1 (permutasi, DIPERBAIKI dari bug awal), MC2 (survival), MC3 (eksekusi/slippage), MC4 (DSR), MC5 (gangguan parameter)
- `src/costs/cost_model.py` -- model biaya bps, kappa, skenario best/base/worst, LOOKUP yang belum terisi TIDAK didefaultkan ke nol
- `tests/` -- 30 test, termasuk L10 dan sanity check di atas

## Catatan jujur

- **Bug ditemukan & diperbaiki selama membangun ini**: MC1 versi pertama mem-permutasi 
  return trade YANG SUDAH TERWUJUD secara langsung lalu menjumlahkannya -- jumlah dari himpunan 
  angka yang sama selalu sama walau diacak urutannya, jadi ujinya tidak pernah bisa gagal atau 
  berhasil secara berarti (vacuous). Diperbaiki: sekarang mem-permutasi return BAR yang mendasari, 
  lalu menerapkan ULANG sinyal (tetap) ke return yang sudah diacak. Test regresi ditambahkan.
- Test sanity pertama (bandingkan total mentah sinyal acak vs B01/B06/B07) gagal di percobaan pertama 
  (33.5% vs target <10%) -- ternyata itu kelemahan DESAIN TES (B01=B06 dan B07=-B01 nyaris cermin 
  sempurna pada walk berdrift nol, jadi 'kalahkan keduanya sekaligus' bukan filter yang berarti), 
  bukan kesalahan pada null-nya. Diganti dengan uji false-positive-rate MC1 yang sesungguhnya.
- Model biaya (`cost_model.py`) TIDAK memiliki markup_prop_firm_pct / commission_usd_per_lot terisi 
  untuk XAUUSD -- keduanya masih LOOKUP dari F0 (FTMO menyembunyikan angka XAUUSD spesifik di balik 
  widget JS). Kode SENGAJA tidak mendefaultkan ini ke 0 -- field `missing_lookups` melaporkannya, 
  diuji di `test_missing_lookup_flagged_not_defaulted`.
- MC2 (survival/prop-firm-breach) BELUM bisa dijalankan dengan angka final -- max_total_drawdown_pct 
  dkk juga masih menunggu F0 (FTMO: 10% max loss, 3%/5% daily loss SUDAH ada dari riset F0 sebelumnya; 
  FundedNext/The5ers belum terverifikasi presisi). Kode sudah teruji tidak mengarang angka saat LOOKUP kosong.

## Verdict F1

**LULUS** -- semua syarat 07_FASE_EKSEKUSI.md F1.lulus terpenuhi.