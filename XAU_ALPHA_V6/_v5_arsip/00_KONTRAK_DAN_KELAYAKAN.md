# 00 — KONTRAK KEJUJURAN & KELAYAKAN STATISTIK

> Bagian dari **XAU ALPHA RESEARCH v5**. Sumber: `XAU_ALPHA_V5.yaml`, sha256 `264fe974c1c1fa70…`
> Blok YAML disalin **verbatim**. Nol perubahan aturan, ambang, atau rumus.


Ini file yang dibaca **paling awal**. Isinya bukan strategi — isinya jawaban atas pertanyaan
*"apakah proyek ini secara aritmetika masuk akal dijalankan sama sekali?"*

Tiga hal yang dikunci di sini:

1. **Tiga permintaan user yang saling bertabrakan** (nol survivor / winrate 60% / 500 kandidat) diselesaikan **di depan**, bukan disembunyikan sampai hasilnya keluar.
2. **Power analysis** — berapa besar edge yang bisa dicapai (Fundamental Law) versus berapa besar sampel untuk mendeteksinya (uji daya). Dua hal berbeda, dipisah.
3. **Anggaran komputasi** — triase 3 tier supaya formula kuadratik tidak membakar berminggu-minggu.

> **Gerbang mati F0:** kalau `K_eff` **terukur** < `K_eff` yang **dibutuhkan** pada IC 0.05 → **BERHENTI**
> sebelum kandidat pertama dijalankan. Dilarang lanjut dengan berharap.

## Metadata sumber

```yaml
meta:
  version: "5.0"
  name: xau-alpha-v5
  instrument_target: XAUUSD
  style: scalping_intraday
  purpose: >
    Menemukan aturan trading dengan expectancy bersih positif setelah biaya
    prop firm nyata, yang bertahan di data yang belum pernah dilihat.
    Sistem ini akan dipakai dengan UANG NYATA, bukan demo.
  locked_on: null
  config_sha256: null              # WAJIB diisi & di-commit sebelum FASE 2
  language_of_reports: id
  revisi:
    r1_koreksi_power_analysis: >
      Draf awal memakai "t = IC * sqrt(eff N)" dengan IC 0.15. Itu SALAH dua
      kali: (a) mencampur besaran edge dengan deteksi statistik, (b) memakai IC
      optimistis. Diganti blok power_analysis yang memisahkan Fundamental Law
      (IR = IC*sqrt(BR)) dari uji daya (t = IR*sqrt(T)), dan memakai IC 0.05
      sebagai dasar, 0.03 sebagai pesimistis.
    r2_koreksi_K_eff: >
      Draf awal menjumlahkan eff N lintas instrumen seolah instrumen independen.
      SALAH — instrumen berkorelasi tidak memberi sampel independen. Diganti
      K_eff (jumlah instrumen independen efektif) lewat eigenvalue matriks
      korelasi PnL STRATEGI, wajib DIUKUR di F0 bukan diasumsikan.
    r3_koreksi_anggaran_trial: >
      Draf awal: 507 varian x 6 horizon = 3042 baris ledger, melewati batas 500
      dan dijamin nol survivor. Ditambahkan FASE F2b (pemilihan horizon lewat
      pilot 72 baris), registri penuh hanya jalan di 1-2 horizon terpilih.
      Total maksimum 572 baris.
    r4_anggaran_komputasi: >
      Ditambahkan blok compute_budget dengan triase 3 tier. Formula
      berkompleksitas kuadratik dilarang dijalankan penuh saat screening.
    sisa_kelemahan_yang_diakui:
      - "129 sitasi masih ditulis dari ingatan, NOL diverifikasi. Wajib dicek di F3."
      - "Sekitar 15% formula masih butuh detail implementasi tambahan saat dikodekan."
      - "Belum ada satu barispun dieksekusi. Nilai eksekusi: belum ada."
```

## Kontrak kejujuran

Ini yang membatasi apa yang boleh dijanjikan sistem ini. Baca sebelum menuntut hasil.

```yaml
honesty_contract:

  K1_zero_survivors:
    permintaan_user: "Jangan sampai yang lolos 0"
    status: TIDAK_BISA_DIJANJIKAN
    alasan: >
      Sistem validasi jujur HARUS bisa mengeluarkan hasil nol. Sistem yang
      dijamin selalu menghasilkan pemenang berarti gerbangnya tidak menyaring
      apapun. Itu mesin pembenaran, bukan mesin riset.
    yang_dilakukan_sebagai_ganti: >
      Memperbesar SAMPEL supaya kandidat bagus punya kesempatan nyata lolos.
      Bukan menurunkan ambang.
    aritmetika: "lihat blok power_analysis — dihitung ulang dengan benar, bukan dengan IC 0.15 yang optimistis"
    catatan: >
      Kalau setelah breadth dinaikkan tetap nol yang lolos, itu temuan nyata
      tentang pasarnya. Wajib dilaporkan apa adanya. Jauh lebih murah daripada
      menemukannya lewat akun yang habis.

# =============================================================================
# 1b. POWER ANALYSIS — matematika kelayakan, dihitung dengan benar
# =============================================================================
# Blok ini MENGGANTIKAN perhitungan kasar "t = IC * sqrt(eff N)" yang dipakai
# di draf awal. Perhitungan itu mencampur dua hal berbeda:
#   (a) seberapa BESAR edge yang bisa dicapai   -> Fundamental Law
#   (b) seberapa BESAR sampel untuk MENDETEKSINYA -> power uji
```

## Power analysis — matematika kelayakan

`K_eff` dan `BR efektif` **WAJIB DIUKUR di F0**, bukan diasumsikan. Tabel angka di dalam blok ini **wajib dihitung ulang dari rumusnya**; kalau hasil hitung beda, pakai hasil hitung dan laporkan.

```yaml
power_analysis:

  a_besaran_edge:
    hukum: "Fundamental Law of Active Management (Grinold)"
    formula: "IR = IC * sqrt(BR)"
    keterangan:
      IR: "information ratio ~ Sharpe strategi"
      IC: "korelasi antara sinyal dan return berikutnya"
      BR: "breadth = jumlah taruhan INDEPENDEN per tahun (bukan jumlah trade)"
    contoh_pada_300_trade_per_tahun:
      ic_0.03: {IR: 0.52}
      ic_0.05: {IR: 0.87}
      ic_0.087: {IR: 1.51}
      ic_0.15: {IR: 2.60}
    catatan_jujur: >
      IC 0.15 yang dipakai sebagai batas di riset sebelumnya adalah BATAS ATAS
      yang optimistis, bukan angka realistis. IC sinyal nyata biasanya 0.02-0.05.
      Semua perhitungan di bawah memakai IC 0.05 sebagai skenario dasar, dan
      IC 0.03 sebagai skenario pesimistis.
    peringatan_BR: >
      BR bukan jumlah trade. Trade yang labelnya tumpang tindih TIDAK
      independen. BR efektif = jumlah trade * rasio keunikan sampel. Pada rasio
      keunikan 0.18 (terukur di riset sebelumnya), 300 trade/tahun hanya memberi
      BR efektif ~54. Itu memotong IR jadi kurang dari setengahnya.
      BR efektif WAJIB DIUKUR di F0, jangan diasumsikan.

  b_deteksi_statistik:
    formula: "t = IR * sqrt(T_tahun)"
    keterangan: "T = panjang partisi yang dipakai menguji, dalam tahun"
    data_tersedia:
      total_tahun: 6.6
      T_screen: 1.3
      T_confirm: 4.0
      T_holdout: 1.3
    contoh_pada_T_confirm_4_tahun:
      IR_0.52: {t: 1.04, vonis: GAGAL}
      IR_0.87: {t: 1.74, vonis: GAGAL}
      IR_1.51: {t: 3.02, vonis: "LOLOS PAS-PASAN"}
      IR_2.60: {t: 5.20, vonis: LOLOS}
    kesimpulan_satu_instrumen: >
      Pada 4 tahun data dan 300 trade/tahun, satu instrumen tunggal MEMBUTUHKAN
      IC >= 0.087 supaya edge-nya bisa dideteksi pada t = 3.0.
      Itu di atas IC realistis (0.02-0.05).
      Artinya: menguji di XAU saja, dengan data yang ada, HAMPIR PASTI GAGAL —
      bukan karena tidak ada edge, tapi karena tidak cukup data untuk
      membuktikannya. Ini penyebab sebenarnya nol survivor di riset sebelumnya.

  c_penyelamatnya_breadth_lintas_instrumen:
    formula_pooling: "t_pooled = t_single * sqrt(K_eff)"
    K_eff_definisi: >
      JUMLAH INSTRUMEN INDEPENDEN EFEKTIF, bukan jumlah instrumen mentah.
      Instrumen yang berkorelasi TIDAK memberi sampel independen.
    formula_K_eff:
      metode_1_eigenvalue: "K_eff = (SUM lambda_i)^2 / SUM (lambda_i^2) ; lambda = eigenvalue matriks korelasi PnL STRATEGI antar instrumen"
      metode_2_equicorrelated: "K_eff = K / (1 + (K-1)*rho_bar) ; rho_bar = korelasi rata-rata berpasangan"
    contoh_metode_2_pada_K_25:
      # DIPERBAIKI r5: dua nilai salah hitung. K_eff = K/(1+(K-1)*rho), K=25.
      rho_0.30: {K_eff: 3.05}    # 25/8.2
      rho_0.20: {K_eff: 4.31}    # 25/5.8   (sebelumnya ditulis 4.4 — SALAH)
      rho_0.10: {K_eff: 7.35}    # 25/3.4   (sebelumnya ditulis 7.6 — SALAH)
      rho_0.05: {K_eff: 11.36}   # 25/2.2
    catatan_verifikasi: "Claude Code WAJIB menghitung ulang tabel ini dari rumus, jangan menyalin angkanya. Kalau hasil hitung beda dari tabel, PAKAI HASIL HITUNG dan laporkan."
    syarat_lolos_yang_benar:
      formula: "K_eff >= (t_target / t_single)^2"
      contoh: "t_target 3.0, t_single 1.74 (IC 0.05) -> K_eff >= 2.97"
      contoh_pesimistis: "t_target 3.0, t_single 1.04 (IC 0.03) -> K_eff >= 8.32"
    catatan_penting: >
      Korelasi yang dihitung HARUS korelasi PnL STRATEGI antar instrumen, BUKAN
      korelasi harga. Dua instrumen bisa berkorelasi harga tinggi tapi PnL
      strateginya rendah korelasinya, dan sebaliknya.
      Panel WAJIB dipilih untuk MEMINIMALKAN korelasi PnL, bukan untuk
      memaksimalkan jumlah instrumen. 8 instrumen tidak berkorelasi lebih
      berharga daripada 25 instrumen yang saling berkorelasi 0.3.

  d_hukuman_pengujian_berganda:
    catatan: >
      Rumus kasar E[max t] ~ sqrt(2*ln N) HANYA berlaku kalau N trial saling
      independen. Kandidat riset SANGAT berkorelasi (banyak varian dari formula
      yang sama), jadi rumus itu terlalu menghukum.
      Yang dipakai sebagai gerbang resmi adalah DSR (Deflated Sharpe Ratio),
      yang memakai VARIANS EMPIRIS dari Sharpe seluruh trial, bukan asumsi
      independen.
    formula_dsr: "DSR = Phi[ ((SR_hat - SR_0) * sqrt(T-1)) / sqrt(1 - skew*SR_hat + ((kurt-1)/4)*SR_hat^2) ]"
    SR_0: "expected maximum Sharpe di bawah null, dihitung dari N trial dan varians Sharpe antar trial"
    aturan: "DSR adalah gerbang resmi. sqrt(2*ln N) hanya dipakai sebagai perkiraan kasar di perencanaan."

  e_yang_wajib_diukur_di_F0:
    catatan: "SEMUA angka di bawah adalah PENGUKURAN, bukan asumsi. Anggaran kandidat dihitung DARI hasil ini."
    daftar:
      - "rasio keunikan sampel per instrumen per horizon -> menentukan BR efektif"
      - "matriks korelasi PnL strategi baseline antar instrumen -> menentukan K_eff"
      - "K_eff lewat metode eigenvalue"
      - "t_single yang bisa dicapai pada IC 0.03 dan IC 0.05"
      - "K_eff minimum yang dibutuhkan = (3.0 / t_single)^2"
    gerbang_F0: >
      Kalau K_eff TERUKUR < K_eff yang DIBUTUHKAN pada IC 0.05 -> BERHENTI dan
      lapor ke user SEBELUM menjalankan kandidat apapun. Pilihannya saat itu:
      (a) tambah instrumen yang korelasi PnL-nya rendah,
      (b) perpanjang riwayat data,
      (c) turunkan target trades/tahun dan naikkan horizon,
      (d) terima bahwa data yang ada tidak cukup untuk membuktikan apapun.
      DILARANG melanjutkan dengan berharap.

  K2_target_winrate:
    permintaan_user: "60% win rate dengan RR 1:2"
    status: DICATAT_SEBAGAI_ASPIRASI_BUKAN_GERBANG
    aritmetika:
      breakeven_winrate_pada_rr_1_2: 0.333
      expectancy_pada_60_persen: "+0.80R per trade"
      implikasi_tahunan: "~240% pada 300 trade/thn, risiko 1% per trade"
      pembanding: "Di atas Medallion Fund (~66% kotor/thn)"
      pengukuran_riset_sebelumnya:
        barrier: "k_sl=1.5 / k_tp=2.5 (RR 1:1.67)"
        breakeven_mekanis_pct: 37.50
        hit_rate_aktual_pct: 37.86
        coin_flip_net_pct: 40.49
        arti: "Pasar memberi ~38% pada RR 1.67. Naik ke 60% pada RR 2.0 menuntut IC jauh di atas 0.15."
    keputusan: >
      Gerbang kelulusan dinilai pada EXPECTANCY BERSIH SETELAH BIAYA, bukan
      pada win rate. Kombinasi winrate/RR apapun yang expectancy-nya positif
      dan lolos seluruh uji statistik = LULUS, meski win rate 40%.
      Menyetel sistem mengejar angka win rate tertentu = definisi overfitting.

  K3_banyak_kandidat:
    permintaan_user: "Banyak kandidat (500) biar hasilnya tidak 0"
    status: DITERIMA_DENGAN_SYARAT
    hukuman_pengujian_berganda:
      n_30:   {ambang_t: 2.61}
      n_100:  {ambang_t: 3.03}
      n_200:  {ambang_t: 3.26}
      n_500:  {ambang_t: 3.53}
      n_1000: {ambang_t: 3.72}
    syarat_500_kandidat:
      catatan: "Angka di tabel atas hanya perkiraan kasar (asumsi trial independen). Gerbang resminya DSR — lihat power_analysis.d"
      masalah_yang_ditemukan_saat_audit: >
        507 varian x 6 horizon = 3042 baris ledger. Itu JAUH melewati
        screen_max 500, dan ambang kasarnya jadi sqrt(2*ln 3042) = 4.00 —
        di atas kemampuan sampel manapun yang realistis.
        Menjalankan seluruh registry di seluruh horizon sekaligus DIJAMIN
        menghasilkan nol. Ini kesalahan perencanaan, bukan kesalahan pasar.
      solusi_penahapan: >
        Horizon TIDAK dijalankan bersamaan dengan registri penuh.
        Ditambahkan FASE F2b: pilih horizon dulu memakai PILOT SET kecil
        (12 formula murah, 1 varian masing-masing = 12 baris x 6 horizon
        = 72 baris ledger). Setelah 1-2 horizon terpilih, registri penuh
        dijalankan HANYA di horizon itu.
      hitungan_setelah_penahapan:
        F2b_pilot: 72
        F4_F5_F6_F7_pada_horizon_terpilih: "<= 500"
        total_maksimum: "<= 572 baris ledger"
    aturan_mengikat: >
      Jumlah kandidat yang boleh DIJALANKAN ditentukan oleh K_eff dan BR efektif
      yang BENAR-BENAR TERUKUR di F0 (lihat power_analysis.e), bukan oleh
      keinginan. Kalau pengukuran F0 tidak mendukung 500, anggaran turun
      otomatis. Beli sampel dulu, baru tambah kandidat.
    pencarian_ide: TIDAK_DIBATASI     # gratis, tidak masuk ledger
    yang_dibatasi: jumlah_yang_dijalankan_di_data
```

## Anggaran komputasi

⚠️ Lihat `AUDIT_TEMUAN.md` — `E72` dan `E82` saat ini terdaftar di **dua tier sekaligus**. Belum diperbaiki di sumber; butuh keputusan user.

```yaml
compute_budget:
  aturan_utama: "Formula murah dijalankan penuh. Formula mahal HANYA untuk survivor atau pada subsampel."

  # DIPERBAIKI r5: E72 & E82 dipindah dari tier-1 (dua-duanya O(w^2) per bar),
  # T17 dihapus (ID tidak eksis, sisa dari registry lama), E83 & seluruh M
  # sebelumnya tidak punya tier sama sekali — sekarang ditugaskan.
  # ATURAN: setiap formula WAJIB punya tepat satu tier. Diverifikasi di F1.

  tier_1_murah:
    kompleksitas: "O(n) atau O(n log n) terhadap panjang data, O(1)..O(w) per bar"
    daftar: [E01, E02, E03, E04, E10, E11, E12, E20, E22, E25, E26, E27, E30, E36,
             E50, E54, E60, E61, E62, E63, E64, E65, E70, E71, E73, E74, E80, E81, E90,
             V01, V02, V03, V04, V05, V07, V08, V09, V10, V12,
             Q01, Q04, Q06, Q07, Q08, Q10, Q12,
             X01, X06, X30, X31, X32, X33,
             M06, M07, M08]
    aturan: "Jalankan penuh di seluruh panel dan horizon terpilih."

  tier_2_sedang:
    kompleksitas: "O(n log n) berat, atau O(w^2) per bar dengan w <= 96"
    daftar: [E21, E23, E24, E31, E32, E33, E34, E35, E51, E52, E53, E55,
             E72, E82, E83, E91, E92, E93,
             V06, V11, V13, V14, Q02, Q03, Q05, Q09, Q11,
             T04, T05, T06, T08, T09, T10,
             X02, X03, X04, X05, X10, X11, X12, X20, X21, X22,
             M01, M02, M03, M04, M05, M11, M12, M13, M14]
    aturan: >
      Jalankan penuh, TAPI batasi jendela terpanjang dan pakai implementasi
      tervektorisasi/Numba. Ukur waktu per instrumen dulu di F1, laporkan
      estimasi total sebelum jalan.
    catatan_E72_E82: >
      Theil-Sen (E72) dan Siegel repeated median (E82) menghitung SELURUH
      kemiringan pasangan: O(w^2) dan O(w^2 log w) per bar. Pada w=96 itu
      ~4600 dan ~9200 operasi per bar per instrumen. Draf awal salah menaruh
      keduanya di tier-1. WAJIB pakai implementasi bergulir inkremental atau
      batasi w <= 48.

  tier_3_mahal:
    kompleksitas: "O(n^2) global, atau O(w^2)..O(w^3) per bar dengan w >= 288"
    daftar: [E40, E41, E42, E43, E44, E45, E95, E96, E97,
             T01, T02, T03, T07,
             X13, X14, X23, X24, X34, X35,
             M09, M10, M15]
    aturan: >
      DILARANG dijalankan penuh di seluruh panel pada tahap screening.
      Prosedur wajib:
      (1) jalankan pada SUBSAMPEL 20% partisi screen di 5 instrumen paling tidak berkorelasi;
      (2) hanya yang lolos ambang awal yang dijalankan penuh;
      (3) catat SEMUA yang dijalankan di ledger, termasuk yang cuma disubsampel.
    catatan_kejujuran: "Subsampel MENURUNKAN daya uji. Kandidat tier-3 yang gagal di subsampel WAJIB ditandai UNDERPOWERED_SCREEN, bukan REJECTED."

  wajib_dilaporkan_di_F1:
    - "waktu eksekusi per formula per instrumen per horizon (diukur, bukan ditebak)"
    - "estimasi total jam komputasi untuk F4-F7"
    - "kalau estimasi > 72 jam: BERHENTI, lapor ke user, usulkan pemangkasan"
```
