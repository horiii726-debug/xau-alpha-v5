import math, random
def hdr(t): print("\n"+"="*78); print(t); print("="*78)
random.seed(11)

hdr("18. FRONTIER KEPUTUSAN — P(capai target) vs P(breach). INI TABEL PALING PENTING.")
def race(risk, sharpe, target, dd_max, dl, tpd=1.5, max_trades=1500, paths=30000):
    mu=sharpe/math.sqrt(250); win=0; brk=0; tt=[]
    for _ in range(paths):
        eq=1.0;peak=1.0;ds=1.0;cnt=0
        for i in range(max_trades):
            eq*=(1+risk*random.gauss(mu,1.0)); peak=max(peak,eq)
            if (peak-eq)/peak>=dd_max: brk+=1; break
            if eq/ds-1<=-dl: brk+=1; break
            if eq-1>=target: win+=1; tt.append(i+1); break
            cnt+=1
            if cnt>=tpd: cnt=0; ds=eq
        else:
            pass
    med = sorted(tt)[len(tt)//2] if tt else None
    return win/paths, brk/paths, med

print("\n  --- FTMO 2-Step Fase 1 (target +10%, daily 5%, maxDD 10% statis) ---")
print(f"  {'risk':>6} {'Sharpe':>7} | {'P(target)':>10} {'P(breach)':>10} {'trade s/d target (median)':>26}")
for sh in [1.15, 1.60]:
    for r in [0.0025,0.005,0.0075,0.01]:
        w,b,m = race(r,sh,0.10,0.10,0.05)
        print(f"  {r*100:>5.2f}% {sh:>7.2f} | {w*100:>9.1f}% {b*100:>9.1f}% {str(m) if m else '-':>26}")

print("\n  --- FundedNext Stellar 1-Step (target +10%, daily 3%, maxDD 6% statis) ---")
print(f"  {'risk':>6} {'Sharpe':>7} | {'P(target)':>10} {'P(breach)':>10} {'trade s/d target (median)':>26}")
for sh in [1.15, 1.60]:
    for r in [0.0025,0.005,0.0075]:
        w,b,m = race(r,sh,0.10,0.06,0.03)
        print(f"  {r*100:>5.2f}% {sh:>7.2f} | {w*100:>9.1f}% {b*100:>9.1f}% {str(m) if m else '-':>26}")

hdr("19. IMBAL HASIL TAHUNAN pada ukuran posisi yang LOLOS MC2")
print(f"  {'risk':>6} {'vol tahunan':>12} {'return @Sh1.15':>15} {'return @Sh1.60':>15}")
for r in [0.0015,0.0025,0.005]:
    v=r*math.sqrt(250)
    print(f"  {r*100:>5.2f}% {v*100:>11.2f}% {1.15*v*100:>14.2f}% {1.60*v*100:>14.2f}%")
print("""
  Bandingkan aspirasi K2 di v5: '~240% per tahun pada 300 trade, risiko 1% per trade'.
  Pada risiko 1% per trade, P(breach) = 98.8% di aturan terketat.
  Aspirasi itu bukan agresif — secara aritmetika TIDAK BISA DIJALANKAN di akun prop firm.""")

hdr("20. REKAP ANGKA MENGIKAT UNTUK PAKET v6")
rows=[
 ("K_eff panel 8 @ rho_pnl 0.15","3.90","hitung ulang di F0 dari korelasi PnL NYATA"),
 ("BR_eff single H240","136","220 trade/thn x uniqueness 0.62 — WAJIB DIUKUR"),
 ("BR_eff portofolio","532","= BR_single x K_eff"),
 ("IR portofolio @IC 0.05","1.154",""),
 ("t_pooled SCREEN (5.75 thn)","2.77","ambang tahap-1 dipasang 1.5"),
 ("t_pooled CONFIRM (12.65 thn)","4.10","ambang tahap-3 tetap 3.0"),
 ("Transmitansi rantai v5","0.17%","= gerbang tidak menyaring, hanya membunuh"),
 ("Transmitansi rantai v6","53.1%","ambang CONFIRM TIDAK diubah"),
 ("N maks lolos DSR (sd_SR .25)","34","<- WAJIB ukur sd_SR di F0; kalau .20 -> 144"),
 ("Anggaran arah v6 (rencana)","<=120","dipotong otomatis kalau sd_SR terukur besar"),
 ("Biaya RT worst @gold 3000","13.36 bps","setelah koreksi satuan beta"),
 ("kappa H240 worst","0.327","v5 mengukur 0.079 di H60"),
 ("Risk/trade lolos MC2 (ketat)","<=0.25%","P(breach)=3.6%"),
 ("Return tahunan pd sizing itu","~4.5%","@Sharpe 1.15 — ini angka jujurnya"),
]
for a,b,c in rows: print(f"  {a:<32} {b:>12}   {c}")
