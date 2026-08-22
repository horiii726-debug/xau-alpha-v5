# F2 langkah 2 -- Jendela biaya per sesi & jam (SHORT, arm demeaned, XAUUSD)

Filter: margin_min_pp>=2.0 DAN net_bps>0 saja (sign_flip/stability dilewati -- sampel per jendela kecil, ini eksplorasi bukan gerbang resmi ulang).

## Jendela di mana SHORT lolos margin>=2pp & net_bps>0: 7 kejadian

| Horizon | k_sl | k_tp | Jendela | Tipe | Margin (pp) | Net bps | N trade |
|---|---:|---:|---|---|---:|---:|---:|
| H15 | 3.0 | 2.0 | 15:00 UTC | hour | 4.81 | 1.11 | 378 |
| H15 | 3.0 | 1.5 | 15:00 UTC | hour | 2.72 | 0.62 | 454 |
| H120 | 3.0 | 4.0 | 03:00 UTC | hour | 2.37 | 0.39 | 597 |
| H120 | 3.0 | 0.5 | 14:00 UTC | hour | 2.28 | 0.38 | 733 |
| H240 | 3.0 | 4.0 | 03:00 UTC | hour | 2.24 | 0.38 | 663 |
| H30 | 3.0 | 3.0 | 15:00 UTC | hour | 2.12 | 0.37 | 472 |
| H15 | 3.0 | 1.0 | 16:00 UTC | hour | 2.00 | 0.30 | 500 |

## Interpretasi jujur

Total ~5.040 kombinasi (horizon x k_sl x k_tp x jam) diuji di sini. Menemukan 7 yang lewat ambang 2pp TIDAK mengejutkan secara statistik murni dari jumlah uji sebanyak itu -- ini pola klasik multiple-testing, bukan bukti jendela biaya nyata. **Tidak ada satupun level SESI (sampel lebih besar, ~200+ trade minimum) yang lolos** -- hanya jendela JAM tunggal sempit yang lolos, dan semuanya bermargin tipis (2.0-4.8pp) dengan N kecil (378-733 trade). Tidak dikoreksi dengan DSR/FDR karena ini eksplorasi langkah 2, bukan kandidat resmi -- tapi kalau dikoreksi, kemungkinan besar semuanya gugur. Kesimpulan: langkah 2 protokol_nol_lolos TIDAK menemukan jendela biaya yang menyelamatkan gerbang.