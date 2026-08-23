#!/usr/bin/env python3
"""XAU ALPHA v6 -- Dashboard F0. 10 panel wajib.

Run ini BERHENTI di F0 (GM-1/GM-1b gagal) -- panel yang butuh kandidat/F1+
(equity vs null, payoff heatmap F2, t-stat kandidat, bobot router, transmitansi
L11 terukur) ditandai eksplisit TIDAK TERCAPAI, bukan diisi angka karangan.
Panel yang bisa dihitung dari data F0 nyata (K_eff/korelasi, kappa, MC2, funnel)
dihitung penuh.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPORTS = Path("/workspace/xau-alpha-v5/reports")
BAR_DIR = Path("/workspace/data/bars_candles")

result = json.loads((REPORTS / "F0_result.json").read_text())
k_eff = result["universe"]["k_eff_eigen"]
rho = result["universe"]["rho"]
t_confirm = result["power"]["t_confirm_years"]

fig, axes = plt.subplots(5, 2, figsize=(16, 26))
fig.suptitle("XAU ALPHA RESEARCH v6 -- Dashboard F0 (BERHENTI di GM-1/GM-1b)",
             fontsize=16, fontweight="bold", y=0.995)

NA_STYLE = dict(ha="center", va="center", fontsize=12, color="#7a1f1f",
                bbox=dict(boxstyle="round", facecolor="#fde8e8", edgecolor="#7a1f1f"))


def na_panel(ax, title, reason):
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.text(0.5, 0.5, f"TIDAK TERCAPAI\n\n{reason}", transform=ax.transAxes, **NA_STYLE)
    ax.set_xticks([]); ax.set_yticks([])


# ---- 1. Equity curve -- N/A kandidat, tampilkan baseline PnL diagnostik ----
ax = axes[0, 0]
try:
    xau = pd.read_parquet(BAR_DIR / "XAUUSD_M5.parquet")
    xag = pd.read_parquet(BAR_DIR / "XAGUSD_M5.parquet")
    for df, label, color in [(xau, "XAUUSD baseline", "#b8860b"), (xag, "XAGUSD baseline", "#708090")]:
        mid = df.set_index(pd.to_datetime(df["bar_time"], utc=True))["mid_close"]
        mom = mid.pct_change(12)
        sig = np.sign(mom).shift(1)
        ret = mid.pct_change()
        strat = (sig * ret).fillna(0)
        eq = (1 + strat).cumprod()
        ax.plot(eq.index, eq.values, label=label, color=color, linewidth=0.8)
    ax.set_title("1. Equity Curve -- BASELINE (bukan kandidat, alat ukur K_eff)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Waktu"); ax.set_ylabel("Equity (x awal)")
    ax.legend(fontsize=8)
    ax.text(0.02, 0.95, "Kandidat B01-B08 & CONFIRM tidak pernah dijalankan (stop di F0)",
            transform=ax.transAxes, fontsize=8, va="top", color="#7a1f1f")
except Exception as e:
    na_panel(ax, "1. Equity Curve kandidat vs null", f"error memuat data: {e}")

# ---- 2. Distribusi drawdown MC2 (10,000 jalur) ----
ax = axes[0, 1]
np.random.seed(42)
N_PATHS, N_TRADES = 10000, 250
ASSUMED_SHARPE = 1.15  # dari spec 06_VALIDASI_STATISTIK.md -- ASUMSI PERENCANAAN, bukan kandidat terukur
daily_mu = ASSUMED_SHARPE / np.sqrt(252)
daily_sigma = 1.0
trade_ret_pct = np.random.normal(daily_mu, daily_sigma, size=(N_PATHS, N_TRADES)) * 0.0025  # scaled to ~0.25% risk/trade
equity = np.cumprod(1 + trade_ret_pct, axis=1)
running_max = np.maximum.accumulate(equity, axis=1)
dd = (running_max - equity) / running_max
max_dd = dd.max(axis=1) * 100
ax.hist(max_dd, bins=60, color="#4a6fa5", alpha=0.85)
ax.axvline(6.0, color="red", linestyle="--", linewidth=2, label="batas 6% (statis)")
ax.axvline(10.0, color="darkred", linestyle="--", linewidth=2, label="batas 10% (statis)")
ax.set_title(f"2. Distribusi Max Drawdown MC2 (n={N_PATHS:,} jalur, asumsi Sharpe={ASSUMED_SHARPE})",
             fontsize=11, fontweight="bold")
ax.set_xlabel("Max Drawdown (%)"); ax.set_ylabel("Frekuensi jalur")
ax.legend(fontsize=9)
ax.text(0.98, 0.95, f"P(DD>6%)={100*(max_dd>6).mean():.2f}%\nP(DD>10%)={100*(max_dd>10).mean():.2f}%\n"
        f"ASUMSI Sharpe -- bukan dari kandidat terukur (stop di F0)",
        transform=ax.transAxes, fontsize=8, va="top", ha="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.7))

# ---- 3. Frontier P(target) vs P(breach) per ukuran posisi ----
ax = axes[1, 0]
risk_grid = [0.15, 0.25, 0.50, 0.75, 1.00]
p_breach, p_target = [], []
for risk in risk_grid:
    tr = np.random.normal(daily_mu, daily_sigma, size=(3000, 250)) * (risk / 100.0)
    eq = np.cumprod(1 + tr, axis=1)
    rmax = np.maximum.accumulate(eq, axis=1)
    ddp = (rmax - eq) / rmax
    breach = (ddp.max(axis=1) > 0.06).mean() * 100
    target = (eq.max(axis=1) >= 1.10).mean() * 100
    p_breach.append(breach); p_target.append(target)
ax2 = ax
sc = ax2.scatter(p_breach, p_target, c=risk_grid, cmap="viridis", s=150, zorder=3, edgecolor="k")
for r, pb, pt in zip(risk_grid, p_breach, p_target):
    ax2.annotate(f"{r}%", (pb, pt), textcoords="offset points", xytext=(6, 6), fontsize=9)
ax2.axvline(5.0, color="red", linestyle="--", label="gerbang MC2: P(breach)<=5%")
cb = plt.colorbar(sc, ax=ax2); cb.set_label("risk % / trade")
ax2.set_title("3. Frontier P(capai target +10%) vs P(breach 6% DD)", fontsize=11, fontweight="bold")
ax2.set_xlabel("P(breach) %"); ax2.set_ylabel("P(capai target) %")
ax2.legend(fontsize=9)

# ---- 4. Heatmap payoff F2 -- N/A ----
ax = axes[1, 1]
na_panel(ax, "4. Heatmap permukaan payoff F2 (k_sl x k_tp) + IC_minimum",
         "F2 belum dijalankan -- proyek berhenti di F0\n(GM-1/GM-1b gagal, lihat STOP_REPORT.md)")

# ---- 5. Bar chart t-stat kandidat -- N/A, tampilkan t_pooled proyeksi F0 ----
ax = axes[2, 0]
ic_grid = [0.03, 0.05, 0.08]
br_eff_assumed = 136  # H240, dari tabel spec sebagai acuan perencanaan
t_single = [ic * np.sqrt(br_eff_assumed) * np.sqrt(t_confirm) for ic in ic_grid]
t_pooled = [t * np.sqrt(k_eff) for t in t_single]
bars = ax.bar([f"IC={ic}" for ic in ic_grid], t_pooled, color="#c97b63")
for b, v in zip(bars, t_pooled):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.05, f"{v:.2f}", ha="center", fontsize=10)
for y, lbl, c in [(1.5, "screening 1.5", "orange"), (2.0, "robustness 2.0", "darkorange"), (3.0, "CONFIRM 3.0", "red")]:
    ax.axhline(y, color=c, linestyle="--", linewidth=1)
    ax.text(2.55, y + 0.05, lbl, fontsize=8, color=c)
ax.set_title(f"5. t_pooled PROYEKSI (K_eff={k_eff:.2f}, T_confirm={t_confirm:.2f}thn, BR_eff asumsi={br_eff_assumed})",
             fontsize=11, fontweight="bold")
ax.set_ylabel("t_pooled")
ax.text(0.02, 0.95, "BUKAN t-stat kandidat nyata -- F6 tidak pernah dijalankan (stop di F0)",
        transform=ax.transAxes, fontsize=8, va="top", color="#7a1f1f")

# ---- 6. Funnel chart corong ----
ax = axes[2, 1]
stages = ["Formula\ndirancang\n(82 arah)", "F0 gate\n(K_eff/GM-1)", "Tahap 1\nSARINGAN", "Tahap 2\nROBUSTNESS", "CONFIRM\n(17 centang)"]
counts = [82, 0, 0, 0, 0]
colors_f = ["#4a6fa5", "#7a1f1f", "#cccccc", "#cccccc", "#cccccc"]
bars = ax.barh(stages, counts, color=colors_f)
ax.set_title("6. Funnel Corong -- kandidat masuk & lolos tiap tahap", fontsize=11, fontweight="bold")
ax.set_xlabel("Jumlah kandidat")
for i, (s, c) in enumerate(zip(stages, counts)):
    ax.text(max(c, 2) + 1, i, f"{c}", va="center", fontsize=10)
ax.text(0.98, 0.05, "82 formula terdaftar di spec, 0 pernah DIUJI --\nproyek berhenti di gerbang F0 sebelum F1",
        transform=ax.transAxes, fontsize=8, ha="right", va="bottom",
        bbox=dict(boxstyle="round", facecolor="#fde8e8", edgecolor="#7a1f1f"))
ax.invert_yaxis()

# ---- 7. Matriks korelasi PnL + K_eff ----
ax = axes[3, 0]
corr_mat = np.array([[1.0, rho], [rho, 1.0]])
im = ax.imshow(corr_mat, cmap="RdYlGn_r", vmin=-1, vmax=1)
ax.set_xticks([0, 1]); ax.set_yticks([0, 1])
ax.set_xticklabels(["XAUUSD", "XAGUSD"]); ax.set_yticklabels(["XAUUSD", "XAGUSD"])
for i in range(2):
    for j in range(2):
        ax.text(j, i, f"{corr_mat[i, j]:.4f}", ha="center", va="center", fontsize=13, fontweight="bold")
plt.colorbar(im, ax=ax, label="korelasi PnL")
ax.set_title(f"7. Matriks Korelasi PnL Baseline -- K_eff(eigen)={k_eff:.4f} (K=2, panel lengkap=8)",
             fontsize=11, fontweight="bold")
ax.text(0, 2.05, f"K_eff untuk K=2 terikat matematis ke (1,2] -- tidak mungkin >=3.0 (GM-1)",
        fontsize=8, color="#7a1f1f")

# ---- 8. Bobot router MOM/MRV/BRK -- N/A ----
ax = axes[3, 1]
na_panel(ax, "8. Bobot 3 keluarga (MOM/MRV/BRK) dari router sepanjang waktu",
         "F7b (router multi-strategi) belum dijalankan\nproyek berhenti di F0")

# ---- 9. Kappa per horizon per skenario biaya (REZIM-SEKARANG, 3 thn terakhir) ----
ax = axes[4, 0]
horizons = [("H15", 15), ("H60", 60), ("H120", 120), ("H240", 240), ("H1D", 1440)]
x = np.arange(len(horizons))
width = 0.35
for offset, symbol, color in [(-width/2, "XAUUSD", "#b8860b"), (width/2, "XAGUSD", "#708090")]:
    bars_df = pd.read_parquet(BAR_DIR / f"{symbol}_M5.parquet")
    bars_df["bar_time"] = pd.to_datetime(bars_df["bar_time"], utc=True)
    years_avail = sorted(bars_df["bar_time"].dt.year.unique().tolist())
    recent = years_avail[-3:]
    bars_df = bars_df[bars_df["bar_time"].dt.year.isin(recent)]
    bars_df["mid_ret"] = bars_df["mid_close"].pct_change()
    sigma_m5 = bars_df["mid_ret"].std() * 1e4
    sb = bars_df["spread_bps"].dropna()
    sb = sb[(sb > 0) & (sb < 1000)]
    p50 = sb.quantile(0.50)  # KOREKSI: bersyarat Q10 (spread<=p50), bukan p90 -- lihat F1_gate_power.md
    komisi_rt = 2 * (0.160 if symbol == "XAGUSD" else 0.140)
    sigma_m1 = sigma_m5 / np.sqrt(5.0)
    sigma_lat10 = sigma_m1 * np.sqrt(10 / 60.0)
    slip = 1.5 * p50 + 0.5 * sigma_lat10
    total_worst = (2 * p50 + slip) * 1.5 + komisi_rt
    kappas = [total_worst / (sigma_m5 * np.sqrt(m / 5.0)) for _, m in horizons]
    ax.bar(x + offset, kappas, width, label=f"{symbol} ({recent[0]}-{recent[-1]})", color=color)
ax.set_xticks(x); ax.set_xticklabels([h[0] for h in horizons])
ax.set_title("9. Kappa per horizon -- REZIM-SEKARANG, biaya bersyarat Q10 (p50)", fontsize=10, fontweight="bold")
ax.set_ylabel("kappa (worst)"); ax.legend(fontsize=8)
ax.axhline(1.0, color="red", linestyle="--", linewidth=1)
ax.text(4.3, 1.02, "kappa=1 (biaya=gerak)", fontsize=8, color="red")

# ---- 10. Transmitansi L11 -- N/A, tampilkan target saja ----
ax = axes[4, 1]
stages_l11 = ["Screening\n(target>=80%)", "Robustness\n(target>=70%)", "Rantai penuh\n(target>=50%)"]
targets = [80, 70, 50]
bars = ax.bar(stages_l11, targets, color="#cccccc", edgecolor="black", hatch="//")
for b, v in zip(bars, targets):
    ax.text(b.get_x() + b.get_width() / 2, v + 2, f"target {v}%", ha="center", fontsize=9)
ax.set_title("10. Transmitansi L11 -- TARGET SAJA (uji belum dijalankan)", fontsize=11, fontweight="bold")
ax.set_ylabel("% transmitansi")
ax.set_ylim(0, 100)
ax.text(0.5, 0.5, "L11 dijalankan di F1.\nProyek berhenti di F0 --\nbatang abu-abu = target dari spec,\nBUKAN hasil ukur.",
        transform=ax.transAxes, ha="center", va="center", fontsize=9,
        bbox=dict(boxstyle="round", facecolor="#fde8e8", edgecolor="#7a1f1f"))

plt.tight_layout(rect=[0, 0, 1, 0.985])
out = REPORTS / "dashboard.png"
plt.savefig(out, dpi=130)
print(f"wrote {out}")
