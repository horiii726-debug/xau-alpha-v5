# CARA MENJALANKAN — untuk Hori

## Langkah 1 — taruh folder ini di repo

```bash
cd ~/QUANTITIVE-V3-XAU-USD          # atau folder repo Anda
mkdir -p spec
cp -r /path/ke/XAU_ALPHA_V6 spec/
git add spec/XAU_ALPHA_V6
git commit -m "v6 spec"
```

Pastikan `CLAUDE.md` ada di **root repo** supaya otomatis kebaca Claude Code:

```bash
cp spec/XAU_ALPHA_V6/CLAUDE.md ./CLAUDE.md
```

## Langkah 2 — jawab 6 keputusan dulu

**JANGAN lewati ini.** Claude Code akan berhenti di F0 kalau belum dijawab.

Buat file `KEPUTUSAN_USER.md` di root repo, isi dengan jawaban Anda:

```markdown
# OVERRIDE V6 — Keputusan Hori, tanggal: ____

1. Corong bertingkat (§07)               : SETUJU / TOLAK
2. F2 jadi pengukuran, bukan STOP (§05C) : SETUJU / TOLAK
3. Koreksi satuan beta slippage (§03C2)  : SETUJU / TOLAK
4. Ledger dipisah arah vs estimasi (§O10): SETUJU / TOLAK
5. sd_SR diukur di F0 dulu (§01B5)       : SETUJU / TOLAK
6. Syarat gabungan K_eff>=4.0 & T>=11thn : SETUJU / TOLAK

Tanda tangan: ____
```

Kalau ada yang Anda TOLAK, tulis alasannya — Claude Code wajib memakai aturan v5 lama
untuk poin itu dan melaporkan konsekuensinya.

## Langkah 3 — prompt pertama ke Claude Code

Copy-paste persis ini:

```
Baca seluruh file di spec/XAU_ALPHA_V6/ — mulai dari CLAUDE.md, lalu 00 sampai 10
berurutan, lalu file DIVISI_*. Jangan tulis kode apapun sebelum selesai membaca.

Baca juga KEPUTUSAN_USER.md di root — itu jawaban saya atas 6 item OVERRIDE V6.

Setelah itu, kerjakan HANYA FASE F0. Berhenti dan lapor sebelum F1.

F0 harus menghasilkan:
- audit data: tanggal mulai NYATA tiap instrumen di Dukascopy, gap, duplikat,
  outlier, hash snapshot
- spread terukur dari tick, dalam BPS, persentil 50/75/90/99 per sesi per jam
- rasio keunikan sampel per instrumen per horizon (DIUKUR, bukan ditebak)
- matriks korelasi PnL STRATEGI antar instrumen -> K_eff lewat eigenvalue
- pilot 24 trial -> sd_SR empiris -> N_maks -> anggaran kandidat
- skew & kurt empiris
- cek 5 gerbang mati GM-1 sampai GM-5

Aturan yang mengikat:
- Kalau salah satu gerbang mati kena, BERHENTI dan lapor. Jangan lanjut dengan berharap.
- Kalau angka hasil ukur berbeda dari angka rencana di dokumen, PAKAI HASIL UKUR
  dan laporkan selisihnya.
- Kalau ada yang tidak yakin, bilang tidak yakin. Dilarang menebak.
- Commit: "v6 FASE F0 — fondasi, biaya, K_eff, sd_SR"
```

## Langkah 4 — setelah F0 selesai

Baca laporannya. Tiga angka yang menentukan segalanya:

| Angka | Kalau bagus | Kalau jelek |
|---|---|---|
| `K_eff` terukur | ≥ 4.0 → lanjut | < 3.0 → **BERHENTI**, panel harus diganti |
| Riwayat bersama | ≥ 11 thn → lanjut | < 11 thn → **BERHENTI** atau kecilkan panel |
| `sd_SR` terukur | ≤ 0.20 → anggaran aman | ≥ 0.25 → registri wajib dipangkas keras |

Kalau ketiganya lolos, prompt berikutnya cukup: **"Lanjut F1."**

Kalau ada yang gagal — **itu bukan kegagalan, itu informasi.** Kirim laporannya ke saya,
kita putuskan bareng: ganti komposisi panel, perpanjang riwayat, atau persempit registri.

## Yang belum ada di paket ini

| # | Kurang | Akibat |
|---|---|---|
| 1 | `DIVISI_X_EXIT_SL_TP_SIZING.md` v5 | Spesifikasi 22 rumus divisi X tidak ada. **Jangan jalankan F5 dengan rumus yang ditebak.** Kirim file itu, atau minta saya tulis ulang dari nol |
| 2 | `VIEW_REZIM/TREN/KORELASI.md` v5 | Bukan penghalang — view tidak menambah kandidat |
| 3 | Data Dukascopy 2003+ | Perlu diunduh sebelum F0 bisa selesai |

## Aturan kerja yang saya minta Anda tegakkan

Claude Code akan tergoda melanggar tiga ini. Tolak kalau terjadi:

1. **Satu fase, lalu berhenti.** Jangan biarkan dia lari sampai F6 sekaligus.
2. **Angka hasil ukur mengalahkan angka di dokumen.** Kalau beda, dokumen yang salah.
3. **Nol survivor itu jawaban yang sah.** Jangan pernah setujui "turunkan ambang sedikit
   biar ada yang lolos". Itu yang bikin orang kehilangan uang, bukan hasil nol.
