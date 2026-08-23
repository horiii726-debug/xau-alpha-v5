import math
from statistics import NormalDist
N = NormalDist(); g = 0.5772156649
def hdr(t): print("\n"+"="*78); print(t); print("="*78)
def sr0(n, var): 
    return math.sqrt(var)*((1-g)*N.inv_cdf(1-1/n) + g*N.inv_cdf(1-1/(n*math.e)))

hdr("9. TEMUAN KRITIS — BR harus dihitung LINTAS PANEL, bukan satu instrumen")
def keff(K,rho): return K/(1+(K-1)*rho)
ke = keff(8,0.15)
br_single = 220*0.62
br_panel  = br_single*ke
print(f"  BR_eff satu instrumen (H240)      = {br_single:.0f}")
print(f"  K_eff panel 8 @ rho_pnl 0.15      = {ke:.2f}")
print(f"  BR_eff PORTOFOLIO = BR x K_eff    = {br_panel:.0f}")
for ic in [0.03,0.05,0.07]:
    print(f"    IC {ic}: IR_single={ic*math.sqrt(br_single):.3f}   IR_PORTOFOLIO={ic*math.sqrt(br_panel):.3f}")
print("  (konsisten dgn t_pooled = t_single*sqrt(K_eff) — dua-duanya naik sqrt(K_eff))")

hdr("10. DSR: berapa Sharpe yang DIBUTUHKAN, sebagai fungsi N dan sd(SR antar trial)")
T = 12.65
def sr_needed(n, var):
    s0 = sr0(n,var)
    lo,hi = s0, s0+6
    for _ in range(200):
        m=(lo+hi)/2
        z=(m-s0)*math.sqrt(T-1)/math.sqrt(1-0.0*m+((3.0-1)/4)*m*m)
        if N.cdf(z) < 0.95: lo=m
        else: hi=m
    return hi
print(f"  T_confirm={T} thn, skew 0, kurt 3, ambang DSR 0.95")
print(f"\n  {'N trial':>8} | " + " | ".join(f"sd(SR)={s}" for s in [0.20,0.25,0.35,0.50]))
print(f"  {'':>8} | " + " | ".join("  SR wajib " for _ in range(4)))
for n in [10,20,30,50,80,120,200,300,500]:
    row=[]
    for sd in [0.20,0.25,0.35,0.50]:
        row.append(f"{sr_needed(n,sd*sd):>10.2f}")
    print(f"  {n:>8} | " + " | ".join(row))

print("\n  Sharpe portofolio yang BISA dicapai:")
for ic in [0.03,0.05,0.07,0.09]:
    print(f"    IC {ic:.2f} -> IR {ic*math.sqrt(br_panel):.2f}")

hdr("11. KOMBINASI YANG LAYAK — cari (N, sd_SR) yang meloloskan IR IC=0.05")
target = 0.05*math.sqrt(br_panel)
print(f"  Target Sharpe portofolio (IC 0.05) = {target:.3f}\n")
print(f"  {'sd(SR)':>7} | N maksimum yang masih lolos DSR 0.95")
for sd in [0.15,0.20,0.25,0.30,0.35,0.50]:
    best=0
    for n in range(2,2001):
        if sr_needed(n,sd*sd) <= target: best=n
        else: break
    print(f"  {sd:>7.2f} | {best if best>=2 else 'NOL — tidak ada N yang lolos'}")

hdr("12. KESIMPULAN ANGGARAN")
sd_assumed=0.25
best=0
for n in range(2,2001):
    if sr_needed(n,sd_assumed**2) <= target: best=n
    else: break
print(f"  Pada sd(SR)=0.25 dan IC 0.05: N maksimum = {best}")
for ic in [0.06,0.07,0.08]:
    t2=ic*math.sqrt(br_panel); b=0
    for n in range(2,3001):
        if sr_needed(n,sd_assumed**2)<=t2: b=n
        else: break
    print(f"  Pada IC {ic:.2f} (IR {t2:.2f}): N maksimum = {b}")
print("\n  v5 menjalankan N=507 dengan IC realistis 0.05 -> SR wajib "
      f"{sr_needed(507,0.25**2):.2f} vs tercapai {target:.2f}. Selisih {sr_needed(507,0.25**2)-target:.2f} Sharpe.")
