import math, random
def hdr(t): print("\n"+"="*78); print(t); print("="*78)

hdr("15-REVISI. TEMUAN BARU: parameter beta di model slippage v5 salah satuan")
print("""  v5 menulis:  slippage_bps = alpha*spread_bps + beta*sigma_BAR_bps,  beta grid [0, .25, .5]
  Masalah: sigma_BAR adalah volatilitas SATU BAR PENUH (5-15 menit).
  Slippage terjadi antara sinyal dan fill = HITUNGAN DETIK, bukan 5 menit.
  beta=0.5 x sigma_bar berarti 'setengah gerak 5 menit hilang jadi slippage'.""")
sig_day = 100.0
for bar,menit in [("M5",5),("M15",15)]:
    print(f"    sigma_{bar:<3} = {sig_day*math.sqrt(menit/1440):.2f} bps   -> beta 0.5 memberi slippage {0.5*sig_day*math.sqrt(menit/1440):.2f} bps")
for det in [1,3,10]:
    print(f"    sigma_{det}detik = {sig_day*math.sqrt(det/86400):.3f} bps -> beta 0.5 memberi slippage {0.5*sig_day*math.sqrt(det/86400):.3f} bps")
print("""
  -> USULAN v6: acuan beta diganti dari sigma_bar ke sigma_LATENSI (grid latensi 1/3/10 detik).
     Ini KOREKSI SATUAN, bukan pelonggaran gerbang. TAPI mengubah hasil, jadi
     WAJIB persetujuan tertulis user + di-hash sebelum F2.""")

hdr("15b. TABEL BIAYA ROUND-TRIP v6 (koreksi satuan), gold 3000")
print("  RT = spread_penuh + 2*slippage + komisi_RT ; lalu x penalti pada 'worst'")
print(f"\n  {'skenario':>8} {'spread$':>8} {'spread bps':>10} {'slip/sisi':>10} {'komisi RT':>10} {'TOTAL RT':>9} {'kappa H240':>11}")
sig_lat = sig_day*math.sqrt(3/86400)
for nm, sp_usd, a, b, pen in [("best",0.20,0.5,0.00,1.0),("base",0.30,1.0,0.25,1.0),("worst",0.60,1.5,0.50,1.5)]:
    sp = sp_usd/3000*1e4
    slip = a*sp + b*sig_lat
    tot = (sp + 2*slip + 0.32)*pen
    print(f"  {nm:>8} {sp_usd:>8.2f} {sp:>10.3f} {slip:>10.3f} {0.32:>10.2f} {tot:>9.3f} {tot/(sig_day*math.sqrt(4/24)):>11.4f}")
print("\n  Pembanding pakai satuan v5 (beta x sigma_M5 = 5.89 bps):")
for nm, sp_usd, a, b, pen in [("worst",0.60,1.5,0.50,1.5)]:
    sp=sp_usd/3000*1e4; slip=a*sp+b*5.89; tot=(sp+2*slip+0.32)*pen
    print(f"  {nm:>8} -> TOTAL RT {tot:.2f} bps, kappa H240 = {tot/40.8:.3f}  <- membunuh semua kandidat")

hdr("17-REVISI. MC2 KASAR — simulasi jalur, aturan TERKETAT (daily 3%, maxDD 6% statis)")
random.seed(7)
def sim(risk, sharpe_ann, n_trades=250, trades_per_day=1.5, paths=20000):
    mu_t = sharpe_ann/math.sqrt(250)      # Sharpe per trade
    breach=0; dds=[]
    for _ in range(paths):
        eq=1.0; peak=1.0; day_start=1.0; cnt=0; mdd=0.0; brk=False
        for i in range(n_trades):
            pnl = risk*random.gauss(mu_t,1.0)
            eq *= (1+pnl)
            peak=max(peak,eq); mdd=max(mdd,(peak-eq)/peak)
            if (peak-eq)/peak >= 0.06: brk=True; break
            if eq/day_start - 1 <= -0.03: brk=True; break
            cnt+=1
            if cnt>=trades_per_day: cnt=0; day_start=eq
        if brk: breach+=1
        dds.append(mdd)
    dds.sort()
    return breach/paths, dds[int(0.5*len(dds))], dds[int(0.95*len(dds))]

print(f"  Sharpe tahunan 1.15 (IC 0.05 + panel), 250 trade, ~1.5 trade/hari")
print(f"\n  {'risk/trade':>10} {'P(breach 250)':>14} {'DD median':>10} {'DD p95':>8}  vonis (gate <=5%)")
for r in [0.0015,0.0025,0.005,0.0075,0.01]:
    pb,d50,d95 = sim(r,1.15)
    print(f"  {r*100:>9.2f}% {pb*100:>13.2f}% {d50*100:>9.2f}% {d95*100:>7.2f}%  {'LOLOS' if pb<=0.05 else 'GAGAL'}")
print(f"\n  Pembanding aturan longgar (FTMO 2-Step: daily 5%, maxDD 10% statis):")
def sim2(risk, sharpe_ann, dd_max=0.10, dl=0.05, n_trades=250, tpd=1.5, paths=20000):
    mu_t=sharpe_ann/math.sqrt(250); breach=0
    for _ in range(paths):
        eq=1.0;peak=1.0;ds=1.0;cnt=0;brk=False
        for i in range(n_trades):
            eq*= (1+risk*random.gauss(mu_t,1.0)); peak=max(peak,eq)
            if (peak-eq)/peak>=dd_max: brk=True;break
            if eq/ds-1<=-dl: brk=True;break
            cnt+=1
            if cnt>=tpd: cnt=0; ds=eq
        if brk: breach+=1
    return breach/paths
for r in [0.0025,0.005,0.0075,0.01]:
    print(f"  {r*100:>9.2f}% {sim2(r,1.15)*100:>13.2f}%   {'LOLOS' if sim2(r,1.15)<=0.05 else 'GAGAL'}")
print("""
  KESIMPULAN: kendala prop firm MENGIKAT LEBIH KERAS daripada edge-nya.
  Bahkan strategi Sharpe 1.15 hanya selamat di risiko per trade yang sangat kecil.
  Ini WAJIB dihitung SEBELUM memilih kandidat, bukan sesudah.""")
