import math, random
from statistics import NormalDist
N = NormalDist()
def hdr(t):
    print("\n"+"="*78); print(t); print("="*78)

# ============================================================ GATE TRANSMITTANCE
hdr("6. TRANSMITANSI GERBANG — P(lolos | edge NYATA ada)")
print("""Model: tiap gerbang statistik mengukur ulang besaran yang sama (t) dengan derau
sendiri. Statistik gerbang g:  z_g = sqrt(rho_g)*Z_common + sqrt(1-rho_g)*eps_g + t_true
rho_g = seberapa besar gerbang itu mengukur hal yang sama dengan gerbang lain.
Gerbang lolos kalau z_g >= hurdle_g. Ini SIMULASI, bukan asumsi independen.""")

random.seed(20260822)
def simulate(t_true, gates, n=200000):
    """gates = list of (nama, hurdle_dalam_satuan_t, rho_ke_faktor_bersama)"""
    npass_all = 0
    per = [0]*len(gates)
    for _ in range(n):
        common = random.gauss(0,1)
        ok_all = True
        for i,(nm,h,r) in enumerate(gates):
            z = t_true + math.sqrt(r)*common + math.sqrt(1-r)*random.gauss(0,1)
            if z >= h: per[i]+=1
            else: ok_all = False
        if ok_all: npass_all += 1
    return npass_all/n, [p/n for p in per]

# --- v5: 17 centang sekaligus di partisi SCREEN (t_true tercapai = 0.39) ---
v5_gates = [
 ("expectancy_net>0",        0.00, 0.70),
 ("t_effN >= 3.0",           3.00, 0.95),
 ("BH-FDR q0.10",            2.60, 0.90),
 ("DSR >= 0.95",             2.90, 0.85),
 ("PBO <= 0.50",             0.60, 0.55),
 ("kalahkan B01..B08",       1.10, 0.60),
 ("CPCV positif >= 80%",     1.30, 0.65),
 ("bootstrap CI95 != 0",     1.96, 0.90),
 ("permutasi > p95",         1.65, 0.80),
 ("walkforward tanda>=80%",  1.30, 0.55),
 ("stabil 10 seed",          0.80, 0.45),
 ("sepertiga akhir signif",  1.30, 0.40),
 ("trades/thn >= 300",      -0.50, 0.05),
 ("MC2 P(breach)<=5%",       0.50, 0.30),
 ("MC3 pctile5 > 0",         0.90, 0.60),
 ("MC5 +/-20% tdk runtuh",   0.70, 0.50),
 ("konsisten >=60% panel",   1.10, 0.35),
]
for label, t_true in [("v5 SCREEN (t tercapai 0.39)",0.39), ("kalau t tercapai 2.0",2.0), ("kalau t tercapai 3.5",3.5)]:
    T,per = simulate(t_true, v5_gates)
    print(f"\n  {label}:  TRANSMITANSI TOTAL = {T*100:.2f}%")
    worst = sorted(zip([g[0] for g in v5_gates], per), key=lambda x:x[1])[:4]
    print("    4 gerbang paling mematikan: " + ", ".join(f"{n}={p*100:.0f}%" for n,p in worst))

hdr("7. CORONG v6 — gerbang bertingkat, ambang diturunkan DARI daya partisinya")
tahap1 = [
 ("expectancy_net>0 (worst)",0.00,0.70),
 ("t_effN >= 1.5",           1.50,0.95),
 ("kalahkan B02 RANDOM_MATCHED",0.80,0.60),
 ("kalahkan B05 COIN_FLIP",  0.80,0.60),
 ("BR_eff >= 100/thn",      -0.50,0.05),
]
tahap2 = [
 ("t_effN >= 2.0",           2.00,0.95),
 ("kalahkan B01..B08",       1.10,0.60),
 ("bootstrap CI95 != 0",     1.96,0.90),
 ("permutasi blok > p95",    1.65,0.80),
 ("MC5 +/-20% tdk runtuh",   0.70,0.50),
 ("stabil 10 seed",          0.80,0.45),
]
tahap3 = [g for g in v5_gates]  # CONFIRM = 17 penuh, tidak dilonggarkan

print("  t_true di SCREEN = 2.77 (hasil hitung blok 3), di CONFIRM = 4.10")
T1,_ = simulate(2.77, tahap1); print(f"\n  TAHAP 1 SCREENING  (5 filter, t>=1.5) : transmitansi {T1*100:.1f}%")
T2,_ = simulate(2.77, tahap2); print(f"  TAHAP 2 ROBUSTNESS (6 filter, t>=2.0) : transmitansi {T2*100:.1f}%")
T3,_ = simulate(4.10, tahap3); print(f"  TAHAP 3 CONFIRM    (17 filter, t>=3.0): transmitansi {T3*100:.1f}%")
print(f"\n  TRANSMITANSI RANTAI PENUH v6 = {T1*T2*T3*100:.1f}%")
Tv5,_ = simulate(0.39, v5_gates)
print(f"  TRANSMITANSI RANTAI v5       = {Tv5*100:.4f}%")
print(f"\n  -> ambang CONFIRM TIDAK diubah sedikitpun. Yang berubah: KAPAN dipasang,")
print(f"     dan berapa besar sampel di bawahnya.")

# ============================================================ DSR / BUDGET
hdr("8. ANGGARAN KANDIDAT dari DSR (Bailey & Lopez de Prado)")
g = 0.5772156649
def sr0(n_trials, var_sr):
    """expected max Sharpe di bawah null"""
    e = math.e
    return math.sqrt(var_sr)*((1-g)*N.inv_cdf(1-1/n_trials) + g*N.inv_cdf(1-1/(n_trials*e)))

print("  SR kandidat sejati (tahunan) = IR = 0.584   [IC 0.05, BR_eff 136]")
print("  T_confirm = 12.65 thn.  Var(SR antar trial) diasumsikan 0.25 (sd 0.5) -> WAJIB DIUKUR di F0")
print("  skew=0, kurt=3 (konservatif; wajib pakai momen empiris saat dijalankan)\n")
SR, T_yr, var_sr = 0.584, 12.65, 0.25
skew, kurt = 0.0, 3.0
print(f"  {'N trial':>8} {'SR_0':>7} {'z_DSR':>7} {'DSR':>7}  vonis")
prev_ok = 0
for n_tr in [50,100,150,200,250,300,400,500,750,1000,3042]:
    s0 = sr0(n_tr, var_sr)
    denom = math.sqrt(1 - skew*SR + ((kurt-1)/4)*SR**2)
    z = (SR - s0)*math.sqrt(T_yr-1)/denom
    dsr = N.cdf(z)
    ok = dsr >= 0.95
    if ok: prev_ok = n_tr
    print(f"  {n_tr:>8} {s0:>7.3f} {z:>7.3f} {dsr:>7.4f}  {'LOLOS' if ok else 'GAGAL'}")
print(f"\n  -> N maksimum yang masih meloloskan kandidat IR 0.584: sekitar {prev_ok}")

print("\n  Pembanding — kalau T hanya 0.857 thn (v5 screen) dan SR 0.424:")
for n_tr in [100,507,3042]:
    s0 = sr0(n_tr,var_sr); d=math.sqrt(1-0*0.424+((3-1)/4)*0.424**2)
    z=(0.424-s0)*math.sqrt(0.857-1)/d if 0.857>1 else float('nan')
    print(f"     N={n_tr}: SR_0={s0:.3f} > SR_hat=0.424 -> DSR mustahil (sqrt(T-1) juga imajiner, T<1 thn)")
