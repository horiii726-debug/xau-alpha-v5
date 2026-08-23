mom=[2,2,2,2,2,2,1,2,2,1,2]
mrv=[2,2,2,2,2,2]
brk=[3,2,2,2,2,1,1]
x=[1,3,2,2,2,2,2,2,2,2]
m=[2,2,4,2,2]
r=[2,1,1]
tot=sum(mom)+sum(mrv)+sum(brk)+sum(x)+sum(m)+sum(r)
nf=len(mom)+len(mrv)+len(brk)+len(x)+len(m)+len(r)
print(f"MOM {len(mom)}f/{sum(mom)}v  MRV {len(mrv)}f/{sum(mrv)}v  BRK {len(brk)}f/{sum(brk)}v")
print(f"X {len(x)}f/{sum(x)}v  M {len(m)}f/{sum(m)}v  RTR {len(r)}f/{sum(r)}v")
print(f"TOTAL ARAH: {nf} formula / {tot} varian")
e_var=sum(mom)+sum(mrv)+sum(brk); e_form=len(mom)+len(mrv)+len(brk)
print(f"E gabungan: {e_form} formula / {e_var} varian")
# tangga
cur=tot; print(f"\n{'awal':<52}{cur:>4}")
for lab,cut in [("L1 buang M01,M02",4),("L2 X sizing X30/X31/X32 -> 1 var",3),
                ("L3 X exit X04/X10/X12/X20/X22 -> 1 var",5)]:
    cur-=cut; print(f"{lab:<52}{cur:>4}")
cut=e_var-e_form; cur-=cut; print(f"{'L4 seluruh E -> 1 varian/formula (-'+str(cut)+')':<52}{cur:>4}")
cur-=2; print(f"{'L5 M11 4->2':<52}{cur:>4}")
cur-=5; print(f"{'L6 buang X exit sekunder (5 formula)':<52}{cur:>4}")
cur-=3; print(f"{'L7 buang X sizing sekunder (3 formula)':<52}{cur:>4}")
cur-=15; print(f"{'L8 tiap keluarga E -> 3 formula jangkar (-15)':<52}{cur:>4}")
lantai = 9 + (1+3) + (2+2+2) + (2+1+1)
print(f"\nLANTAI terhitung dari daftar terlindungi: {lantai}")
print(f"Tangga mencapai: {cur}  ->  {'KONSISTEN' if cur==lantai else 'TIDAK KONSISTEN'}")
print(f"\nEstimasi: V 14f/20v  Q 12f/16v  T 10f/10v  S 29f/29v = {14+12+10+29}f/{20+16+10+29}v")
print(f"\nv5 507 -> v6 {tot}  ({(1-tot/507)*100:.0f}% dipotong)")
