import math, random
from statistics import NormalDist
N=NormalDist(); g=0.5772156649
random.seed(20260822)
def keff(K,rho): return K/(1+(K-1)*rho)
def hdr(t): print("\n"+"="*78); print(t); print("="*78)
def sim(t,gates,n=120000):
    ok=0
    for _ in range(n):
        c=random.gauss(0,1); good=True
        for nm,h,r in gates:
            if t+math.sqrt(r)*c+math.sqrt(1-r)*random.gauss(0,1)<h: good=False;break
        if good: ok+=1
    return ok/n

hdr("DIAGNOSIS — kenapa tahap 2 saya sendiri tidak bisa mencapai 70%")
t=2.21
for nm,h,r in [("t>=2.0",2.00,0.95),("bootstrap CI95",1.96,0.90),("permutasi p95",1.65,0.80),
               ("kalahkan B01-B08",1.10,0.60),("MC5 +/-20%",0.70,0.50),("seed 10",0.80,0.45)]:
    print(f"  {nm:<20} sendirian: {sim(t,[(nm,h,r)],60000)*100:5.1f}%")
print("""
  MASALAHNYA: t>=2.0, bootstrap CI95 (1.96) dan permutasi p95 (1.65) adalah
  UJI SIGNIFIKANSI YANG SAMA diulang tiga kali. rho ke faktor bersama 0.95/0.90/0.80.
  Menumpuk tiga uji bukti-sama di satu tahap = menghitung bukti yang sama tiga kali,
  dan tiap pengulangan hanya menambah PELUANG GAGAL, bukan informasi.""")

hdr("PERBAIKAN — tahap dikelompokkan menurut JENIS BUKTI, bukan menurut kekuatan")
t1=[("expectancy>0",0.00,0.70),("t>=1.5",1.50,0.95),("kalahkan B02",0.80,0.60),
    ("kalahkan B05",0.80,0.60),("BR_eff>=100",-0.50,0.05)]
t2_baru=[("MC5 +/-20%",0.70,0.50),("stabil 10 seed",0.80,0.45),
         ("walkforward tanda>=80%",1.30,0.55),("sepertiga akhir",1.30,0.40),
         ("CPCV>=80%",1.30,0.65),("MC2 P(breach)<=5%",0.50,0.30)]
t3=[("expect",0.00,0.70),("t3",3.00,0.95),("fdr",2.60,0.90),("dsr",2.90,0.85),("pbo",0.60,0.55),
    ("nulls",1.10,0.60),("cpcv",1.30,0.65),("boot",1.96,0.90),("perm",1.65,0.80),("wf",1.30,0.55),
    ("seed",0.80,0.45),("third",1.30,0.40),("br",-0.50,0.05),("mc2",0.50,0.30),("mc3",0.90,0.60),
    ("mc5",0.70,0.50),("panel",1.10,0.35)]
print("""  TAHAP 1 SARINGAN     : expectancy, t>=1.5, kalahkan B02+B05, BR_eff  (bukti: signifikansi dasar)
  TAHAP 2 ROBUSTNESS   : MC5, seed, walkforward, sepertiga akhir, CPCV, MC2
                         (bukti: STABILITAS — korelasi rendah ke t, BUKAN uji signifikansi ulang)
  TAHAP 3 CONFIRM      : 17 centang penuh, TERMASUK bootstrap & permutasi & DSR
                         (di partisi CONFIRM, tempat t paling besar)\n""")
out={}
for lab,K,rho,hist in [("TIER-A",4,0.20,23.0),("TIER-B",8,0.15,14.0)]:
    ke=keff(K,rho); IR=0.05*math.sqrt(220*0.62)
    tps=IR*math.sqrt(hist*0.25)*math.sqrt(ke); tpc=IR*math.sqrt(hist*0.55)*math.sqrt(ke)
    a=sim(tps,t1); b=sim(tps,t2_baru); c=sim(tpc,t3)
    out[lab]=(tps,tpc,a,b,c,a*b*c)
    print(f"  {lab} (screen t={tps:.2f}, confirm t={tpc:.2f}):")
    print(f"     tahap1 {a*100:5.1f}%  {'OK >=80' if a>=.80 else 'KURANG'}")
    print(f"     tahap2 {b*100:5.1f}%  {'OK >=70' if b>=.70 else 'KURANG'}")
    print(f"     tahap3 {c*100:5.1f}%")
    print(f"     RANTAI {a*b*c*100:5.1f}%  {'LOLOS GM-3 (>=50%)' if a*b*c>=.50 else 'DI BAWAH GM-3 50%'}\n")

hdr("SENSITIVITAS — apa yang dibutuhkan supaya rantai >= 50%")
print(f"  {'K':>3} {'rho':>5} {'K_eff':>6} {'riwayat':>8} {'t_scr':>6} {'t_cnf':>6} {'rantai':>7}")
for K,rho,hist in [(4,0.20,23),(6,0.15,20),(6,0.10,20),(8,0.15,14),(8,0.15,20),(8,0.10,20),(10,0.10,20),(8,0.10,23)]:
    ke=keff(K,rho); IR=0.05*math.sqrt(220*0.62)
    tps=IR*math.sqrt(hist*0.25)*math.sqrt(ke); tpc=IR*math.sqrt(hist*0.55)*math.sqrt(ke)
    ch=sim(tps,t1,50000)*sim(tps,t2_baru,50000)*sim(tpc,t3,50000)
    print(f"  {K:>3} {rho:>5.2f} {ke:>6.2f} {hist:>8} {tps:>6.2f} {tpc:>6.2f} {ch*100:>6.1f}% {'<-- LOLOS' if ch>=.5 else ''}")

hdr("ANGGARAN — N_maks pada IR yang benar")
def sr0(n,var): return math.sqrt(var)*((1-g)*N.inv_cdf(1-1/n)+g*N.inv_cdf(1-1/(n*math.e)))
def nmax(tg,sd,T):
    b=0
    for n in range(2,3001):
        s0=sr0(n,sd*sd); d=math.sqrt(1+0.5*tg*tg)
        if N.cdf((tg-s0)*math.sqrt(T-1)/d)>=0.95: b=n
        else: break
    return b
print(f"  {'konfigurasi':<24} {'IR_port':>8} {'T_cnf':>6} | " + " ".join(f"sd{sd:.2f}" for sd in [0.10,0.15,0.20,0.25]))
for lab,K,rho,hist in [("TIER-A (4 instr, 23thn)",4,0.20,23.0),("TIER-B (8 instr, 14thn)",8,0.15,14.0),
                       ("TARGET (8 instr, 20thn)",8,0.10,20.0)]:
    ke=keff(K,rho); IRp=0.05*math.sqrt(220*0.62*ke); T=hist*0.55
    row=" ".join(f"{nmax(IRp,sd,T):>6}" for sd in [0.10,0.15,0.20,0.25])
    print(f"  {lab:<24} {IRp:>8.3f} {T:>6.2f} | {row}")
print("\n  LANTAI registri = 23. Baris yang N_maks-nya < 23 -> §08 D3 BERHENTI.")
