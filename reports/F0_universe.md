# F0 -- Universe & K_eff

**Panel diminta oleh spec v6 (§04): 8 instrumen** (XAUUSD, XAGUSD, EURUSD, USDJPY, US100, US30, USOIL, NATGAS). **Panel data tersedia & terverifikasi di run ini: K=2** (XAUUSD, XAGUSD) -- lihat PREREGISTRATION.md untuk alasan & konsekuensi yang dinyatakan SEBELUM angka di bawah dihitung.

Baseline strategi untuk mengukur korelasi PnL (alat ukur struktur, BUKAN kandidat): `sign(momentum M5 L=12)`, hold 12 bar, TANPA biaya (sama seperti metodologi v5 `compute_keff.py`).

- N observasi PnL selaras (irisan timestamp XAUUSD & XAGUSD): 450,995
- **Korelasi PnL strategi baseline XAUUSD-XAGUSD (rho_PnL terukur): 0.4779**
- Eigenvalues matriks korelasi 2x2: [0.5221, 1.4779]
- **K_eff (metode eigenvalue, WAJIB dipakai resmi): 1.6281**
- K_eff (metode equicorrelated, perencanaan saja): 1.3532

## Batas matematis (dinyatakan SEBELUM run, lihat PREREGISTRATION.md)

Untuk K=2 instrumen, `K_eff_eigen = 2 / (1 + rho^2)`, yang **terikat ke rentang (1, 2]** untuk SEMUA nilai rho yang mungkin (termasuk rho negatif). Tidak ada nilai korelasi PnL yang bisa membuat K_eff panel 2-instrumen mencapai 3.0 (GM-1), apalagi 4.0 (GM-1b). Angka 1.6281 di atas mengonfirmasi ini secara empiris: **hasil ukur, bukan kejutan** -- sudah diprediksi secara aljabar sebelum data dilihat.


## Verdict gerbang mati

- **GM-1 (K_eff >= 3.0): GAGAL (K_eff terukur = 1.6281)**
