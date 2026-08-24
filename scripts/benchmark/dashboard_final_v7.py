#!/usr/bin/env python3
"""Dashboard final -- funnel semua yang sudah diuji sepanjang proyek v6/v7,
dan kenapa semuanya berhenti di gerbang simetri G1."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPORTS = Path("/workspace/xau-alpha-v5/reports")

fig = plt.figure(figsize=(20, 13))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1])
fig.suptitle("XAU ALPHA v7.2 -- PERJALANAN LENGKAP: dari 12-fase pipeline sampai gerbang simetri G1-G4",
             fontsize=15, fontweight="bold")

# ---- Panel 1: L2b tangga horizon ----
ax = fig.add_subplot(gs[0, 0])
horizons = ["M5", "M15", "M30", "H1", "H4", "D1"]
kappas = [0.622, 0.359, 0.254, 0.179, 0.091, 0.037]
colors = ["#d62728"] * 4 + ["#2ca02c"] * 2
ax.bar(horizons, kappas, color=colors)
ax.axhline(0.15, color="black", linestyle="--", label="ambang kappa=0.15")
ax.set_title("L2b: Tangga Horizon -- kappa (biaya/sigma)")
ax.set_ylabel("kappa")
ax.legend(fontsize=8)
for i, k in enumerate(kappas):
    ax.text(i, k + 0.015, f"{k:.3f}", ha="center", fontsize=9)

# ---- Panel 2: funnel kombinasi diuji vs lolos ----
ax = fig.add_subplot(gs[0, 1])
stages = ["Diuji\n(H1 23thn)", "Lolos G1\n(H1)", "Diuji\n(M5 H4/D1)", "Lolos G1\n(M5)"]
counts = [78, 1, 52, 0]  # Lomba4(36)+Lomba2(42)=78 di H1; 1 lolos G1 tapi gagal G4; 24+28=52 di M5, 0 lolos G1
colors_f = ["#4a6fa5", "#d62728", "#4a6fa5", "#d62728"]
bars = ax.bar(stages, counts, color=colors_f)
for b, c in zip(bars, counts):
    ax.text(b.get_x() + b.get_width()/2, c + 1, str(c), ha="center", fontsize=10, fontweight="bold")
ax.set_title("Kombinasi (horizon x tau x peserta) diuji vs lolos G1")
ax.set_ylabel("jumlah kombinasi")

# ---- Panel 3: distribusi gerbang gugur, semua uji digabung ----
ax = fig.add_subplot(gs[0, 2])
gate_fail = {"G1\n(simetri)": 34 + 41 + 24 + 27, "G2\n(demeaned)": 1, "G3\n(rezim)": 0, "G4\n(walk-fwd)": 2 + 1}
ax.bar(gate_fail.keys(), gate_fail.values(), color="#d62728")
ax.set_title("Total kegagalan per gerbang (semua lomba, kedua dataset)")
ax.set_ylabel("jumlah kombinasi gugur")
for i, (k, v) in enumerate(gate_fail.items()):
    ax.text(i, v + 1, str(v), ha="center", fontsize=10, fontweight="bold")

# ---- Panel 4: drift capture bukti (D3.1, ulang dari sebelumnya) ----
ax = fig.add_subplot(gs[1, 0])
sides = ["LONG\n(raw)", "SHORT\n(raw)", "LONG\n(demean)", "SHORT\n(demean)"]
vals = [7.885, -8.310, 2.060, -2.910]
colors_d = ["#2ca02c" if v > 0 else "#d62728" for v in vals]
ax.bar(sides, vals, color=colors_d)
ax.axhline(0, color="black", linewidth=0.8)
ax.set_title("Bukti drift capture (CUSUM @H=1d, D3.1)")
ax.set_ylabel("expectancy net (bps)")

# ---- Panel 5: garis waktu perjalanan proyek ----
ax = fig.add_subplot(gs[1, 1])
ax.axis("off")
timeline = (
    "PERJALANAN PROYEK (kronologis)\n\n"
    "1. F0/F1 pipeline 12-fase, panel 2 instrumen\n"
    "   -> K_eff=1.63, GM-3 gagal (biaya>edge H240)\n\n"
    "2. 5 Lomba benchmark per-fungsi (M5, 2021-2026)\n"
    "   -> HAR-RV & entropi menang (non-arah, VALID)\n"
    "   -> CUSUM entry +14.1bps (BELUM diuji simetri)\n\n"
    "3. D3.1/D3.3 uji prioritas -> CUSUM = drift capture\n"
    "   LONG +7.9bps vs SHORT -8.3bps, WF 5/10\n\n"
    "4. L1 autopsi arm demeaned -> 1/4 lolos, t-stat=0.72\n\n"
    "5. L2 unduh H1 2003-2026 (23 tahun, 6 tahun negatif)\n\n"
    "6. L3 @H1, gerbang G1-G4 di depan -> 0/78 lolos\n\n"
    "7. L2b tangga horizon (M5 2021-2026)\n"
    "   -> hanya H4, D1 lolos kappa<=0.15\n\n"
    "8. L3 @H4/D1, gerbang G1-G4 -> 0/52 lolos\n\n"
    "TOTAL: 130 kombinasi diuji, 0 lolos G1-G4"
)
ax.text(0.02, 0.98, timeline, transform=ax.transAxes, fontsize=9.5, va="top", family="monospace",
        bbox=dict(boxstyle="round", facecolor="#f0f8ff", edgecolor="#4a6fa5"))

# ---- Panel 6: kesimpulan & rekomendasi ----
ax = fig.add_subplot(gs[1, 2])
ax.axis("off")
conclusion = (
    "KESIMPULAN\n\n"
    "Tidak ada sinyal arah (13 formula, 5 horizon,\n"
    "2 dataset independen 5thn & 23thn) yang lolos\n"
    "simetri long/short paling dasar.\n\n"
    "Ini pola menyeluruh, bukan kegagalan 1 formula.\n"
    "83+/84 (H1) dan 51/52 (M5) mati di G1 -- gerbang\n"
    "PALING DASAR, bukan uji lanjutan yang halus.\n\n"
    "L4-L10 (sistem, Monte Carlo, ML) TIDAK dijalankan\n"
    "-- tidak ada trade nyata untuk disimulasikan.\n\n"
    "REKOMENDASI (3 pilihan, tidak berubah dari v7.1):\n"
    "A. Horizon >5-20 hari (di atas D1)\n"
    "B. Kelas edge lain: spread lintas-aset,\n"
    "   musiman sesi, event-driven (FOMC/NFP)\n"
    "C. Terima sebagai beta long-only\n"
    "   (TIDAK cocok prop firm)\n\n"
    "HOLDOUT tidak pernah dibuka."
)
ax.text(0.02, 0.98, conclusion, transform=ax.transAxes, fontsize=9.5, va="top", family="monospace",
        bbox=dict(boxstyle="round", facecolor="#fde8e8", edgecolor="#b23a3a"))

plt.tight_layout()
out = REPORTS / "dashboard_final_v7.png"
plt.savefig(out, dpi=130)
print(f"saved {out}")
