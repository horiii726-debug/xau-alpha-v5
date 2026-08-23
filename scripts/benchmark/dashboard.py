#!/usr/bin/env python3
"""Dashboard ringkasan 5 lomba -- satu panel per lomba, menunjukkan pemenang
vs baseline. Angka diambil dari hasil run aktual (lihat reports/LOMBA*.md
untuk tabel lengkap per lomba) -- bukan dihitung ulang di sini, supaya
dashboard konsisten persis dengan laporan detail.
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

FIG_DIR = Path("/workspace/xau-alpha-v5/reports/figs")
REPORTS = Path("/workspace/xau-alpha-v5/reports")

fig, axes = plt.subplots(2, 3, figsize=(20, 12))
fig.suptitle("BENCHMARK PER FUNGSI -- XAUUSD M1/M5, 5 tahun, split 70/30 kronologis, 5 LOMBA INDEPENDEN",
             fontsize=15, fontweight="bold")

# ---- Panel 1: Lomba 1 Volatilitas (QLIKE median, winner=HAR-RV semua horizon) ----
ax = axes[0, 0]
horizons = ["1h", "4h", "1d"]
har_rv = [0.0941, 0.1280, 0.0637]
baseline = [0.7894, 1.0450, 1.0229]
x = np.arange(3)
w = 0.35
ax.bar(x - w/2, har_rv, w, label="HAR-RV (menang di 3/3)", color="#2ca02c")
ax.bar(x + w/2, baseline, w, label="Baseline (close-to-close)", color="#888888")
ax.set_xticks(x); ax.set_xticklabels(horizons)
ax.set_ylabel("QLIKE median (rendah=baik)")
ax.set_title("LOMBA 1 -- VOLATILITAS\nHAR-RV menang di SEMUA horizon, p<0.001")
ax.legend(fontsize=8)

# ---- Panel 2: Lomba 2 Tren (IC Spearman, tidak ada pemenang konsisten) ----
ax = axes[0, 1]
ns = ["N=12", "N=24", "N=48"]
winners_ic = [-0.0021, 0.0342, 0.0344]  # Kalman, Kalman, QuantReg
baseline_ic = [-0.0200, -0.0038, 0.0327]
winner_names = ["Kalman", "Kalman", "QuantReg"]
x = np.arange(3)
ax.bar(x - w/2, winners_ic, w, label="Peserta terbaik", color="#2ca02c")
ax.bar(x + w/2, baseline_ic, w, label="Baseline OLS", color="#888888")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x); ax.set_xticklabels(ns)
ax.set_ylabel("IC Spearman")
ax.set_title("LOMBA 2 -- TREN\nSemua IC lemah (~0.02-0.03), TIDAK ada pemenang\nkonsisten lintas N -- kemungkinan besar derau")
ax.legend(fontsize=8)
for i, n in enumerate(winner_names):
    ax.annotate(n, (x[i] - w/2, winners_ic[i]), textcoords="offset points", xytext=(0, 5), fontsize=7, ha="center")

# ---- Panel 3: Lomba 3 Rezim (AUC, entropi menang konsisten) ----
ax = axes[0, 2]
ns = ["N=12", "N=24", "N=48"]
perm_ent = [0.6287, 0.6245, 0.6091]
lempel_ziv = [0.6104, 0.6121, 0.6141]
baseline_auc = [0.5092, 0.5170, 0.5117]
x = np.arange(3)
ax.bar(x - w, perm_ent, w, label="PermutationEntropy", color="#2ca02c")
ax.bar(x, lempel_ziv, w, label="LempelZiv", color="#98df8a")
ax.bar(x + w, baseline_auc, w, label="Baseline (persistensi)", color="#888888")
ax.axhline(0.5, color="red", linestyle=":", linewidth=1, label="AUC=0.5 (acak)")
ax.set_xticks(x); ax.set_xticklabels(ns)
ax.set_ylabel("AUC")
ax.set_title("LOMBA 3 -- REZIM\nEntropi/kompleksitas menang KONSISTEN\ndi semua N, p=0.000")
ax.legend(fontsize=7)

# ---- Panel 4: Lomba 4 Entry (expectancy net bps, CUSUM menang di 1d) ----
ax = axes[1, 0]
hs = ["1h", "4h", "1d"]
winner_exp = [-2.224, 0.145, 14.108]  # tau terbaik per H
baseline_exp = [-2.953, -2.915, -2.660]
winner_names4 = ["MAD-Zscore", "CUSUM", "CUSUM"]
x = np.arange(3)
colors_w = ["#d62728" if v < 0 else "#2ca02c" for v in winner_exp]
ax.bar(x - w/2, winner_exp, w, label="Peserta terbaik", color=colors_w)
ax.bar(x + w/2, baseline_exp, w, label="Baseline (entry acak)", color="#888888")
ax.axhline(0, color="black", linewidth=0.8)
ax.set_xticks(x); ax.set_xticklabels(hs)
ax.set_ylabel("expectancy net (bps)")
ax.set_title("LOMBA 4 -- ENTRY (biaya real=2.88bps)\nCUSUM @H=1d: +14.1bps, p=0.000 -- SATU-SATUNYA\nedge net-positif kuat di seluruh benchmark")
ax.legend(fontsize=8)
for i, n in enumerate(winner_names4):
    ax.annotate(n, (x[i] - w/2, winner_exp[i]), textcoords="offset points", xytext=(0, 5 if winner_exp[i]>=0 else -12), fontsize=7, ha="center")

# ---- Panel 5: Lomba 5 SL/TP (expectancy net, entry dikunci CUSUM H=1d) ----
ax = axes[1, 1]
methods = ["Parkinson\n(baseline)", "GARCH", "POT-GPD", "EmpiricalQ\n(p90)"]
exp5 = [8.973, 11.599, 19.468, 19.820]
colors5 = ["#888888", "#2ca02c", "#2ca02c", "#2ca02c"]
ax.bar(methods, exp5, color=colors5)
ax.set_ylabel("expectancy net (bps)")
ax.set_title("LOMBA 5 -- SL/TP (entry dikunci: CUSUM H=1d)\nBarrier lebih lebar (EmpiricalQ/POT-GPD) >> Parkinson\n(stop rasio 1.6% vs 18.8%) -- semua p=0.000")

# ---- Panel 6: Ringkasan alur temuan ----
ax = axes[1, 2]
ax.axis("off")
summary_text = (
    "RINGKASAN ALUR TEMUAN\n\n"
    "1. VOLATILITAS: HAR-RV terbaik di semua horizon\n"
    "   (menggabungkan info lag pendek+menengah+panjang)\n\n"
    "2. TREN: sinyal slope linear LEMAH (IC~0.02-0.03),\n"
    "   tidak ada pemenang konsisten -- market\n"
    "   relatif efisien terhadap tren linear sederhana\n\n"
    "3. REZIM: entropi/kompleksitas return (BUKAN\n"
    "   variance ratio klasik) adalah prediktor\n"
    "   trending-vs-ranging terkuat & paling konsisten\n\n"
    "4. ENTRY: CUSUM @H=1d SATU-SATUNYA sinyal\n"
    "   dengan edge net-positif kuat (+14.1bps, p=0.000)\n"
    "   -- entry horizon pendek (1h/4h) semua rugi\n"
    "   setelah biaya\n\n"
    "5. SL/TP: barrier ADAPTIF dari ekor distribusi\n"
    "   (EmpiricalQuantile/POT-GPD) >> barrier dari\n"
    "   volatilitas biasa (Parkinson/GARCH) --\n"
    "   +19.8bps vs +8.97bps, 2.2x lipat\n\n"
    "KOMBINASI TERBAIK YANG TERUKUR:\n"
    "CUSUM entry (H=1d, tau=1.5) + barrier\n"
    "EmpiricalQuantile(p90) = +19.8bps/trade bersih,\n"
    "p=0.000, n=6701 trade di TEST"
)
ax.text(0.02, 0.98, summary_text, transform=ax.transAxes, fontsize=10, va="top", family="monospace",
        bbox=dict(boxstyle="round", facecolor="#f0f8ff", edgecolor="#4a6fa5"))

plt.tight_layout()
out_png = REPORTS / "dashboard_benchmark.png"
plt.savefig(out_png, dpi=130)
print(f"saved {out_png}")
