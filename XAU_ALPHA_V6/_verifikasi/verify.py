import math

def line(t=""): print(t)
def hdr(t):
    print("\n" + "="*78); print(t); print("="*78)

# ---------------------------------------------------------------- 1. K_eff
hdr("1. K_eff — equicorrelated formula  K_eff = K / (1 + (K-1)*rho)")
def keff_equi(K, rho): return K/(1+(K-1)*rho)
print(f"{'K':>4} | " + " | ".join(f"rho={r:<5}" for r in [0.05,0.10,0.15,0.20,0.30]))
for K in [1,4,6,8,10,15,25]:
    print(f"{K:>4} | " + " | ".join(f"{keff_equi(K,r):>9.2f}" for r in [0.05,0.10,0.15,0.20,0.30]))

hdr("1b. VERIFIKASI tabel v5 (K=25) — apakah angka di file benar?")
for rho, claimed in [(0.30,3.05),(0.20,4.31),(0.10,7.35),(0.05,11.36)]:
    calc = keff_equi(25,rho)
    print(f"  rho {rho:.2f}: file={claimed:>6.2f}  hitung={calc:>6.2f}  {'OK' if abs(calc-claimed)<0.01 else 'BEDA'}")

# ---------------------------------------------------------------- 2. IR / BR
hdr("2. Fundamental Law  IR = IC * sqrt(BR_eff)   [BR_eff = trades/yr * uniqueness]")
print(f"{'horizon':>8} {'trd/yr':>7} {'uniq':>6} {'BR_eff':>7} | {'IR@IC.03':>9} {'IR@IC.05':>9}")
scen = [("H15",900,0.10),("H60",400,0.18),("H120",300,0.35),("H240",220,0.62),("H1D",120,0.85)]
for lab,tr,u in scen:
    br = tr*u
    print(f"{lab:>8} {tr:>7} {u:>6.2f} {br:>7.1f} | {0.03*math.sqrt(br):>9.3f} {0.05*math.sqrt(br):>9.3f}")

# ---------------------------------------------------------------- 3. t achievable
hdr("3. t_single = IR*sqrt(T_years)   dan   t_pooled = t_single*sqrt(K_eff)")
print("\n--- v5 AKTUAL (screen 313 hari = 0.857 thn, 1 instrumen, H60) ---")
br_v5 = 400*0.18
ir_v5 = 0.05*math.sqrt(br_v5)
T_v5 = 313/365.25
t_v5 = ir_v5*math.sqrt(T_v5)
print(f"  BR_eff={br_v5:.0f}  IR={ir_v5:.3f}  T={T_v5:.3f}thn  t_single={t_v5:.3f}  K_eff=1  t_pooled={t_v5:.3f}")
print(f"  ambang v5 = 3.0  -> defisit {3.0-t_v5:.2f}. MUSTAHIL. Butuh sampel {(3.0/t_v5)**2:.1f}x lipat.")

print("\n--- v6 rencana: panel 8 (rho_pnl 0.15), horizon H240 ---")
K, rho = 8, 0.15
ke = keff_equi(K,rho)
br_v6 = 220*0.62
ir_v6 = 0.05*math.sqrt(br_v6)
print(f"  K_eff={ke:.2f}  BR_eff={br_v6:.0f}  IR@IC0.05={ir_v6:.3f}")
print(f"\n  {'partisi':>10} {'T(thn)':>7} {'t_single':>9} {'t_pooled':>9}  vonis")
for lab, T in [("SCREEN",5.75),("CONFIRM",12.65),("HOLDOUT",4.60)]:
    ts = ir_v6*math.sqrt(T); tp = ts*math.sqrt(ke)
    v = "LOLOS 3.0" if tp>=3.0 else ("cukup utk 2.0" if tp>=2.0 else ("cukup utk 1.5" if tp>=1.5 else "KURANG"))
    print(f"  {lab:>10} {T:>7.2f} {ts:>9.3f} {tp:>9.3f}  {v}")

print("\n  pesimistis IC=0.03:")
ir_p = 0.03*math.sqrt(br_v6)
for lab, T in [("SCREEN",5.75),("CONFIRM",12.65)]:
    ts = ir_p*math.sqrt(T); tp = ts*math.sqrt(ke)
    print(f"  {lab:>10} {T:>7.2f} {ts:>9.3f} {tp:>9.3f}")

# ---------------------------------------------------------------- 4. partitions
hdr("4. Partisi dari riwayat 2003-2026 (23.0 thn), skema 25/55/20 + embargo")
TOT = 23.0
emb = 10/365.25*2
for name,f in [("SCREEN",0.25),("CONFIRM",0.55),("HOLDOUT",0.20)]:
    print(f"  {name:>8}: {TOT*f:>6.2f} thn")
print(f"  embargo total (2x10 hari): {emb:.3f} thn")
print(f"  efektif: SCREEN {TOT*0.25-emb/2:.2f} | CONFIRM {TOT*0.55-emb:.2f} | HOLDOUT {TOT*0.20:.2f}")

print("\n  Kalau panel penuh 8 instrumen baru tersedia 2012 (14.0 thn):")
T2=14.0
for name,f in [("SCREEN",0.25),("CONFIRM",0.55),("HOLDOUT",0.20)]:
    T=T2*f; ts=ir_v6*math.sqrt(T); tp=ts*math.sqrt(ke)
    print(f"  {name:>8}: {T:>5.2f} thn  t_single={ts:.3f}  t_pooled={tp:.3f}")

# ---------------------------------------------------------------- 5. tier A vs B
hdr("5. Keputusan jendela pooling: TIER-A (panjang, K kecil) vs TIER-B (pendek, K besar)")
print(f"  {'opsi':>8} {'K':>3} {'rho':>5} {'K_eff':>6} {'T_conf':>7} {'t_single':>9} {'t_pooled':>9}")
for lab,K_,rho_,Tt in [("TIER-A",4,0.20,23.0),("TIER-B",8,0.15,14.0)]:
    k_=keff_equi(K_,rho_); T=Tt*0.55; ts=ir_v6*math.sqrt(T); tp=ts*math.sqrt(k_)
    print(f"  {lab:>8} {K_:>3} {rho_:>5.2f} {k_:>6.2f} {T:>7.2f} {ts:>9.3f} {tp:>9.3f}")
print("  -> dua-duanya wajib dihitung di F0 dari data NYATA; yang dipakai dideklarasikan SEBELUM run.")
