import math, random
from statistics import NormalDist
N=NormalDist(); g=0.5772156649
def keff(K,rho): return K/(1+(K-1)*rho)
def hdr(t): print("\n"+"="*78); print(t); print("="*78)

hdr("KOREKSI 1 — TIER-A dan TIER-B dihitung KONSISTEN (tidak dicampur)")
BR=220*0.62
print(f"  BR_eff single H240 = {BR:.1f}\n")
res={}
for lab,K,rho,hist in [("TIER-A",4,0.20,23.0),("TIER-B",8,0.15,14.0)]:
    ke=keff(K,rho); IR=0.05*math.sqrt(BR); BRp=BR*ke; IRp=0.05*math.sqrt(BRp)
    sc,cf,ho = hist*0.25, hist*0.55, hist*0.20
    ts_s=IR*math.sqrt(sc); tp_s=ts_s*math.sqrt(ke)
    ts_c=IR*math.sqrt(cf); tp_c=ts_c*math.sqrt(ke)
    ts_h=IR*math.sqrt(ho); tp_h=ts_h*math.sqrt(ke)
    res[lab]=dict(ke=ke,IRp=IRp,BRp=BRp,sc=sc,cf=cf,ho=ho,tps=tp_s,tpc=tp_c,tph=tp_h)
    print(f"  {lab}: K={K} rho={rho} -> K_eff={ke:.2f} | riwayat {hist} thn")
    print(f"     BR_portofolio={BRp:.0f}  IR_portofolio@IC0.05={IRp:.3f}")
    print(f"     SCREEN  {sc:5.2f}thn  t_single={ts_s:.3f}  t_pooled={tp_s:.3f}")
    print(f"     CONFIRM {cf:5.2f}thn  t_single={ts_c:.3f}  t_pooled={tp_c:.3f}  {'LOLOS 3.0' if tp_c>=3 else 'GAGAL'}")
    print(f"     HOLDOUT {ho:5.2f}thn  t_single={ts_h:.3f}  t_pooled={tp_h:.3f}")
    print(f"     IC 0.03 pesimistis: CONFIRM t_pooled={0.03*math.sqrt(BR)*math.sqrt(cf)*math.sqrt(ke):.3f}\n")

hdr("KOREKSI 2 — transmitansi dihitung ulang pada t yang BENAR")
random.seed(20260822)
def sim(t_true, gates, n=200000):
    ok=0
    for _ in range(n):
        c=random.gauss(0,1); good=True
        for nm,h,r in gates:
            if t_true+math.sqrt(r)*c+math.sqrt(1-r)*random.gauss(0,1) < h: good=False; break
        if good: ok+=1
    return ok/n
v5g=[("expect",0.00,0.70),("t3",3.00,0.95),("fdr",2.60,0.90),("dsr",2.90,0.85),("pbo",0.60,0.55),
     ("nulls",1.10,0.60),("cpcv",1.30,0.65),("boot",1.96,0.90),("perm",1.65,0.80),("wf",1.30,0.55),
     ("seed",0.80,0.45),("third",1.30,0.40),("trades",-0.50,0.05),("mc2",0.50,0.30),("mc3",0.90,0.60),
     ("mc5",0.70,0.50),("panel",1.10,0.35)]
t1=[("expect",0.00,0.70),("t15",1.50,0.95),("b02",0.80,0.60),("b05",0.80,0.60),("br",-0.50,0.05)]
t2=[("t20",2.00,0.95),("nulls",1.10,0.60),("boot",1.96,0.90),("perm",1.65,0.80),("mc5",0.70,0.50),("seed",0.80,0.45)]
print(f"  v5 (t tercapai 0.39, 17 gerbang di SCREEN): {sim(0.39,v5g)*100:.2f}%\n")
for lab in ["TIER-A","TIER-B"]:
    r=res[lab]
    a=sim(r['tps'],t1); b=sim(r['tps'],t2); c=sim(r['tpc'],v5g)
    res[lab].update(T1=a,T2=b,T3=c,Tall=a*b*c)
    print(f"  {lab} (screen t={r['tps']:.2f}, confirm t={r['tpc']:.2f}):")
    print(f"     tahap1 {a*100:5.1f}%  {'OK' if a>=.80 else 'DI BAWAH target 80%'}")
    print(f"     tahap2 {b*100:5.1f}%  {'OK' if b>=.70 else 'DI BAWAH target 70%'}")
    print(f"     tahap3 {c*100:5.1f}%")
    print(f"     RANTAI {a*b*c*100:5.1f}%  {'OK' if a*b*c>=.50 else 'DI BAWAH GM-3 50%'}\n")

hdr("KOREKSI 3 — ambang tahap disesuaikan supaya target transmitansi TERCAPAI")
print("  Aturan §07 B1: ambang = tertinggi yang masih memberi P(lolos|IC0.05) >= target")
for lab in ["TIER-A","TIER-B"]:
    r=res[lab]
    best1=best2=None
    for h in [x/10 for x in range(30,0,-1)]:
        gg=[("expect",0.00,0.70),("tX",h,0.95),("b02",0.80,0.60),("b05",0.80,0.60),("br",-0.50,0.05)]
        if sim(r['tps'],gg,50000)>=0.80: best1=h; break
    for h in [x/10 for x in range(30,0,-1)]:
        gg=[("tX",h,0.95),("nulls",1.10,0.60),("boot",1.96,0.90),("perm",1.65,0.80),("mc5",0.70,0.50),("seed",0.80,0.45)]
        if sim(r['tps'],gg,50000)>=0.70: best2=h; break
    print(f"  {lab}: ambang tahap1 -> {best1}   ambang tahap2 -> {best2}")
    res[lab]['h1']=best1; res[lab]['h2']=best2

hdr("KOREKSI 4 — anggaran DSR pada IR yang BENAR")
def sr0(n,var): return math.sqrt(var)*((1-g)*N.inv_cdf(1-1/n)+g*N.inv_cdf(1-1/(n*math.e)))
def nmax(target,sd,T):
    best=0
    for n in range(2,3001):
        s0=sr0(n,sd*sd); d=math.sqrt(1+((3-1)/4)*target**2)
        if N.cdf((target-s0)*math.sqrt(T-1)/d)>=0.95: best=n
        else: break
    return best
for lab in ["TIER-A","TIER-B"]:
    r=res[lab]
    print(f"\n  {lab}: IR_portofolio={r['IRp']:.3f}, T_confirm={r['cf']:.2f} thn")
    print(f"     {'sd_SR':>7} | N_maks")
    for sd in [0.15,0.20,0.25,0.30]:
        nm=nmax(r['IRp'],sd,r['cf'])
        print(f"     {sd:>7.2f} | {nm if nm>=2 else 'NOL'}")
