# XAU ALPHA RESEARCH v5 — INSTRUKSI KERJA

> **Untuk Claude Code.** Ini pintu masuk. Baca file ini penuh sebelum mengetik satu baris kode.
>
> Sumber tunggal: `XAU_ALPHA_V5.yaml` · sha256 `264fe974c1c1fa70b155b8a4f6b2c865860ef948194c3041d2df648b0a9d0b30`
> 3.352 baris · 129 formula · 507 varian · 6 divisi.
>
> Paket ini adalah **pemecahan verbatim** dari sumber itu. Nol rumus diubah, nol ambang diubah,
> nol grid parameter diubah, urutan fase tidak diubah. Satu-satunya konten baru ada di
> `ADENDUM_Z_ENTRY.md`, dan statusnya **usulan yang belum disetujui**.

---

## Tujuh aturan yang tidak bisa ditawar

1. **Baca file ini penuh sebelum mengetik satu baris kode.**
2. **Kerjakan SATU fase, lalu BERHENTI dan lapor** sebelum fase berikutnya.
3. Commit per fase: `v5 FASE Fn — <judul>`.
4. Tiap laporan memuat: **angka apa adanya, apa yang gagal, apa yang dilewati, apa yang belum yakin.**
5. **Kalau tidak yakin — bilang tidak yakin.** Dilarang menebak angka, sitasi, atau hasil yang belum dihitung.
6. **Kalau hasilnya jelek — laporkan jeleknya.** Jangan dipoles. Sistem ini dipakai dengan uang nyata.
7. Dilarang melonggarkan gerbang manapun tanpa **OVERRIDE V5 tertulis dari user**.

Ditambah satu yang paling sering dilanggar:

> **§stop_conditions.6** — masalah yang tidak diatur file ini → **BERHENTI, tanya user, jangan putuskan sendiri.**

---

## ⛔ Baca ini sebelum F0: ada 2 temuan material yang belum diputuskan

`AUDIT_TEMUAN.md` memuat 7 temuan hasil pemeriksaan. Dua di antaranya **memblokir F0**:

- **Tangga pemangkasan tidak bisa mencapai anggarannya sendiri.** Pada K_eff = 4 anggaran jadi 200, tapi lantai struktural tangga adalah **219**. Contoh di file menjanjikan ~200 — tidak tercapai.
- **Pada K_eff = 3, sisa slot untuk divisi E dan M adalah nol.** Hanya X + baseline estimasi yang bisa jalan.

Jangan hitung `screen_max` sebelum kedua ini diputuskan user. Angkanya akan salah.

---

## Peta file

### Inti — baca berurutan
| File | Isi | Kapan dibaca |
|---|---|---|
| `00_KONTRAK_DAN_KELAYAKAN.md` | Kontrak kejujuran, power analysis, anggaran komputasi | **Pertama.** Menjawab: apakah proyek ini masuk akal dijalankan sama sekali |
| `01_HUKUM.md` | Anti-lookahead L1–L10, anti-overfit O1–O9, anti-rumus-ritel, anti-data-palsu | Sebelum menulis kode apapun |
| `02_DATA_DAN_BIAYA.md` | Sumber data, model biaya tanpa MT5, skenario worst, kappa | F0 |
| `03_UNIVERSE_DAN_HORIZON.md` | Panel 25 instrumen, grid 6 horizon | F0, F2b |
| `04_PARTISI_LABELING_PAYOFF.md` | Partisi, triple-barrier, **gerbang payoff = TES PERTAMA** | F2 |
| `05_VALIDASI_STATISTIK.md` | Null B01–B09, ambang statistik, dedup, Monte Carlo MC1–MC5, aturan ML | F1, lalu terus |
| `06_GERBANG_DAN_ANGGARAN.md` | Gerbang kelulusan, anggaran trial, ledger, protokol nol lolos | F0, lalu tiap gerbang |
| `07_FASE_EKSEKUSI.md` | F0–F11, stop condition, cara kerja, pelajaran | Peta jalan keseluruhan |

### Divisi — registry formula, verbatim
| File | Divisi | Formula | Varian | Fase | Tipe |
|---|---|---:|---:|---|---|
| `DIVISI_V_VOLATILITAS.md` | V — Volatilitas | 14 | 41 | F4 | estimation |
| `DIVISI_Q_SPREAD_LIKUIDITAS.md` | Q — Spread & likuiditas | 12 | 35 | F4 | estimation |
| `DIVISI_T_INTENSITAS_TICK.md` | T — Intensitas tick | 10 | 27 | F4 | estimation |
| `DIVISI_X_EXIT_SL_TP_SIZING.md` | **X — Exit, SL/TP & sizing** | 22 | 114 | **F5** | direction |
| `DIVISI_E_ENTRY_ARAH.md` | E — Entry / arah | 56 | 209 | F6 | direction |
| `DIVISI_M_ML_METALABELING.md` | M — ML & meta-labeling | 15 | 81 | F7 | direction |
| | **TOTAL** | **129** | **507** | | |

### View — indeks silang, **tidak menambah kandidat**
| File | Isi |
|---|---|
| `VIEW_REZIM.md` | 26 formula yang fungsinya deteksi rezim, dikelompokkan. Plus peringatan: memecah rezim membagi eff N |
| `VIEW_TREN.md` | Formula tren & kemiringan, dipetakan ke indikator ritel yang digantikannya |
| `VIEW_KORELASI.md` | K_eff, dedup, korelasi null — 4 tempat korelasi jadi gerbang mati |

> Satu formula muncul di beberapa view **tidak** berarti dijalankan beberapa kali.
> Ledger tetap menghitungnya **sekali**.

### Tambahan & audit
| File | Isi | Status |
|---|---|---|
| `ADENDUM_Z_ENTRY.md` | 3 kandidat z-score untuk entry (Z01, Z02, Z03 — 17 varian) | 🆕 **usulan, belum disetujui** |
| `AUDIT_TEMUAN.md` | 7 temuan pemeriksaan + 5 hal yang lolos verifikasi | perlu keputusan user |

---

## Urutan fase — tidak boleh diubah

```
F0  fondasi, biaya, K_eff        ──► ⛔ K_eff kurang → STOP sebelum kandidat pertama
F1  infrastruktur validasi       ──► ⛔ uji kebocoran §L10 gagal → STOP, null-nya yang bug
F2  GERBANG PAYOFF (entry ACAK)  ──► ⛔ nol lolos → STOP TOTAL          ★ TES PERTAMA
F2b pilot pemilihan horizon      ──► ⛔ t_pooled < 3.0 → STOP
F3  verifikasi DOI & registry    ──►    ≥90% resolve, nol DOI karangan
F4  divisi estimasi V, Q, T      ──►    Model Confidence Set
F5  divisi X — EXIT & SIZING     ──►    ★ PRIORITAS TERTINGGI
F6  divisi E — screening arah    ──►    threshold only, dilarang argmax
F7  divisi M — meta-labeling     ──►    wajib kalahkan baseline linear
F8  freeze & pre-register        ──►    hash di-commit
F9  CONFIRM — maks 8 slot        ──►    tidak boleh ditambah
F10 GOLDEN HOLDOUT — sekali      ──►    tidak bisa dibuka dua kali
F11 paket deployment             ──►    kill switch ditulis sebelum uang masuk
```

**Perhatikan F2 dan F5.** Struktur payoff divalidasi sebelum sinyal dicari; exit diuji sebelum entry.
Kebalikan dari cara kebanyakan orang — dan itu memang disengaja. Riset 3 tahun sebelumnya
melakukannya terbalik dan membuang 3 tahun.

---

## Yang paling mudah dilanggar tanpa sadar

| Jebakan | Pasal | Cara mengeceknya sendiri |
|---|---|---|
| Memilih kandidat terbaik dari daftar | §O5 | `grep -nE "sort\|argmax\|idxmax\|nlargest\|max\(" select_champion` — ada satu saja, langgar |
| Menghitung p-value tanpa bobot keunikan | §statistics | 16 dari 112 "signifikan" jadi 0–1 setelah dikoreksi. Assertion wajib menolak tanpa bobot |
| Menghitung kappa dari batas waktu maksimum | §cost_model.kappa | Meremehkan biaya **3x**. Wajib dari durasi hit barrier NYATA |
| Menormalkan pakai statistik seluruh sampel | §L3 | Fit **hanya** di fold latih |
| Seleksi fitur sebelum loop CV | §L4 | Harus **di dalam** loop |
| Menjalankan registri penuh di 6 horizon | §trial_budget | 3.042 baris ledger, dijamin nol survivor. Pilih horizon di F2b dulu |
| Menambah kandidat saat nol lolos | §protokol_nol_lolos | Menambah kandidat **menaikkan ambang** untuk semua kandidat lain |
| Menamai ulang rumus ritel dengan notasi statistik | §anti_rumus_ritel | Lihat `ADENDUM_Z_ENTRY.md` §Z.1 — contoh nyatanya |

---

## Yang tidak bisa dijanjikan sistem ini

**Nol survivor adalah hasil yang sah.** Sistem validasi jujur harus bisa mengeluarkan hasil nol.
Sistem yang dijamin selalu menghasilkan pemenang berarti gerbangnya tidak menyaring apapun —
itu mesin pembenaran, bukan mesin riset.

**Target 60% winrate pada RR 1:2 dicatat sebagai aspirasi, bukan gerbang.** Pengukuran nyata:
pasar memberi hit rate **37.86%** pada RR 1.67, dengan breakeven mekanis **37.50%**.
Marginnya 0.36 poin persen sebelum biaya. Menuntut 60% pada RR 2.0 menuntut IC jauh di atas 0.15,
sementara IC sinyal nyata biasanya 0.02–0.05. Yang dinilai adalah **expectancy bersih setelah biaya**.
Kombinasi apapun yang expectancy-nya positif dan lolos semua uji = **LULUS**, meski winrate 40%.

Kalau setelah semua ini hasilnya tetap nol: itu **temuan nyata tentang pasarnya**, wajib dilaporkan
apa adanya. Jauh lebih murah daripada menemukannya lewat akun yang habis.
