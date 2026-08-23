import math
def hdr(t): print("\n"+"="*78); print(t); print("="*78)

hdr("13. MODEL BIAYA — angka NYATA FTMO / FundedNext, dinyatakan dalam bps")
print("""  Komisi metals (TERVERIFIKASI dari halaman resmi):
    FTMO       : 0.0014% x notional   -> 0.140 bps per aplikasi
    FundedNext : 0.0016% x notional   -> 0.160 bps per aplikasi
    Verifikasi contoh FundedNext: 1 lot XAUUSD @ 4466.22""")
lot, contract, px = 1, 100, 4466.22
print(f"    hitung = {lot}x{contract}x{px}x0.000016 = ${lot*contract*px*0.000016:.2f}  (situs menulis $7.14) OK")
print("    -> AMBIGU: per sisi atau round-trip? WAJIB dikonfirmasi ke support sebelum F9.\n")

print("  Spread XAUUSD: $0.15-$0.30 (sumber SEKUNDER, bukan halaman resmi) -> tandai UNVERIFIED")
print(f"\n  {'harga emas':>11} | {'spread $':>9} | {'spread bps':>11} | {'komisi RT bps':>14} | {'total RT bps':>13}")
for gold in [1200, 1800, 2400, 3200, 4400]:
    for sp in [0.20, 0.60]:
        sp_bps = sp/gold*1e4
        com_rt = 0.16*2
        print(f"  {gold:>11} | {sp:>9.2f} | {sp_bps:>11.3f} | {com_rt:>14.2f} | {sp_bps+com_rt:>13.3f}")
print("\n  -> biaya bps yang SAMA dalam USD bervariasi 3.7x lintas rentang harga 2003-2026.")
print("     Model biaya WAJIB bps & kontemporer. v5 sudah benar soal ini; sekarang ada angkanya.")

hdr("14. KAPPA = biaya_RT_bps / volatilitas_horizon_bps")
print("  sigma harian emas ~1.0% = 100 bps (wajib diukur ulang per rezim di F0)")
for hz, jam in [("H15",0.25),("H60",1.0),("H120",2.0),("H240",4.0),("H1D",24.0)]:
    sig = 100*math.sqrt(jam/24)
    for lab, cost in [("murah(4400)",0.77),("mahal(1800)",2.24)]:
        print(f"  {hz:>5} sigma={sig:>6.1f}bps | biaya {lab:>12} {cost:>5.2f}bps -> kappa {cost/sig:>6.4f}")
print("\n  v5 mengukur kappa 0.079 di horizon ~24 menit. Naik ke H240 memotong kappa ~4x.")

hdr("15. SKENARIO BIAYA v6 (gate dihitung pada 'worst')")
print(f"  {'skenario':>7} | {'spread pct':>10} | {'alpha':>5} | {'beta':>5} | {'penalti':>7} | contoh total RT bps @gold 3000, sigma_bar 25bps")
for nm, pct, a, b, pen in [("best",50,0.5,0.00,1.0),("base",75,1.0,0.25,1.0),("worst",90,1.5,0.50,1.5)]:
    sp_usd = {50:0.20,75:0.30,90:0.60}[pct]
    sp_bps = sp_usd/3000*1e4
    slip = a*sp_bps + b*25
    total = (sp_bps + 2*0.16 + 2*slip)*pen
    print(f"  {nm:>7} | p{pct:<9} | {a:>5.1f} | {b:>5.2f} | {pen:>7.1f} | {total:>6.3f}")

hdr("16. ATURAN AKUN PROP FIRM (input MC2 — sebelumnya KOSONG, sekarang TERISI)")
rows = [
 ("FTMO 2-Step",      "10% / 5%", "5%", "10% statis",  "4 hari", "-"),
 ("FTMO 1-Step",      "10%",      "3%", "10% trailing EOD", "-", "best day <=50%"),
 ("FundedNext Stellar 2-Step","8% / 5%","5%","10% statis","5 hari","konsistensi payout"),
 ("FundedNext Stellar 1-Step","10%",    "3%","6% statis", "2 hari","konsistensi payout"),
 ("FundedNext Stellar Lite",  "8% / 4%","4%","8% statis", "5 hari","risiko/trade <=1%"),
]
print(f"  {'model':>28} | {'target':>10} | {'daily':>5} | {'max DD':>18} | {'min hari':>8} | catatan")
for r in rows: print(f"  {r[0]:>28} | {r[1]:>10} | {r[2]:>5} | {r[3]:>18} | {r[4]:>8} | {r[5]}")
print("\n  MC2 gate: P(breach dalam 250 trade) <= 5% pada aturan TERKETAT = daily 3% / maxDD 6% statis")
print("  (FundedNext Stellar 1-Step). Kalau lolos di situ, lolos di semua model lain.")

hdr("17. UKURAN POSISI YANG SELAMAT — batas kasar sebelum MC2 dijalankan")
print("  Aturan terketat: max total DD 6%. Untuk P(ruin) rendah butuh DD_typical << 6%.")
print(f"  {'risk/trade':>10} | {'DD 99pct kasar (Sharpe 1.15, 250 trade)':>40}")
for r in [0.0025,0.005,0.0075,0.01,0.02]:
    dd = 2.5*math.sqrt(250)*r*0.5
    print(f"  {r*100:>9.2f}% | {dd*100:>39.2f}%  {'AMAN' if dd<0.04 else 'BAHAYA vs 6%'}")
print("  -> perkiraan kasar saja. Angka mengikat WAJIB dari MC2 bootstrap 10.000 jalur.")
