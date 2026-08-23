#!/usr/bin/env python3
"""LOMBA 2 -- TREN/KEMIRINGAN. Target: slope N bar ke depan, distandardisasi
(t-stat dari regresi OLS harga vs indeks-bar di window MASA DEPAN). Prediktor
dihitung dari window N bar SEBELUM t (kausal). Data M5 (M1 terlalu besar
untuk estimator O(N^2) di tiap titik evaluasi -- disubsampling ke ~4000 titik
evaluasi merata sepanjang seri, kronologis, supaya waktu komputasi wajar).
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import HuberRegressor
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m5, chronological_split, bootstrap_pvalue, spearman_ic, sign_accuracy, FIG_DIR, REPORTS

warnings.filterwarnings("ignore")

N_GRID = [12, 24, 48]
N_EVAL_POINTS = 4000


def ols_slope_tstat(y: np.ndarray) -> tuple:
    x = np.arange(len(y))
    slope, intercept, r, p, se = stats.linregress(x, y)
    tstat = slope / se if se > 0 else 0.0
    return slope, tstat


def theil_sen_slope(y: np.ndarray) -> float:
    slope, intercept, lo, hi = stats.theilslopes(y, np.arange(len(y)))
    return slope


def siegel_repeated_median(y: np.ndarray) -> float:
    n = len(y)
    x = np.arange(n)
    medians = np.empty(n)
    for i in range(n):
        slopes = [(y[i] - y[j]) / (x[i] - x[j]) for j in range(n) if j != i]
        medians[i] = np.median(slopes)
    return float(np.median(medians))


def mann_kendall_z(y: np.ndarray) -> float:
    n = len(y)
    s = 0
    for i in range(n - 1):
        s += np.sum(np.sign(y[i + 1:] - y[i]))
    var_s = n * (n - 1) * (2 * n + 5) / 18.0
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0.0
    return float(z)


def quantile_reg_slope(y: np.ndarray) -> float:
    x = np.arange(len(y))
    X = sm.add_constant(x)
    mod = sm.QuantReg(y, X)
    res = mod.fit(q=0.5, max_iter=100)
    return float(res.params[1])


def huber_slope(y: np.ndarray) -> float:
    x = np.arange(len(y)).reshape(-1, 1)
    hr = HuberRegressor(max_iter=100)
    hr.fit(x, y)
    return float(hr.coef_[0])


class KalmanDrift:
    """Local-level-with-drift Kalman filter: state=[level, drift]. Dipakai
    SECARA RECURSIVE sepanjang seri penuh (bukan per-window), causal by
    construction -- state pada bar t hanya pakai observasi sampai t."""
    def __init__(self, q_level=1e-5, q_drift=1e-7, r_obs=1e-4):
        self.F = np.array([[1.0, 1.0], [0.0, 1.0]])
        self.Q = np.array([[q_level, 0.0], [0.0, q_drift]])
        self.H = np.array([[1.0, 0.0]])
        self.R = np.array([[r_obs]])
        self.x = None
        self.P = None

    def run(self, prices: np.ndarray) -> np.ndarray:
        n = len(prices)
        drift_out = np.full(n, np.nan)
        x = np.array([prices[0], 0.0])
        P = np.eye(2) * 1.0
        for t in range(n):
            x_pred = self.F @ x
            P_pred = self.F @ P @ self.F.T + self.Q
            y_resid = prices[t] - (self.H @ x_pred)[0]
            S = (self.H @ P_pred @ self.H.T + self.R)[0, 0]
            K = (P_pred @ self.H.T).flatten() / S
            x = x_pred + K * y_resid
            P = P_pred - np.outer(K, self.H @ P_pred)
            drift_out[t] = x[1]
        return drift_out


def run():
    m5 = load_m5()
    mid = m5["mid_close"].values
    n_total = len(mid)
    train_mask_full, test_mask_full = chronological_split(n_total, 0.70)

    # Precompute Kalman drift ONCE over the full series (recursive, causal) --
    # fit noise params on a quick heuristic from train volatility.
    train_ret_std = np.std(np.diff(np.log(mid[:int(n_total * 0.7)])))
    kf = KalmanDrift(q_level=(train_ret_std * mid[0]) ** 2 * 0.01,
                      q_drift=(train_ret_std * mid[0]) ** 2 * 1e-4,
                      r_obs=(train_ret_std * mid[0]) ** 2 * 4)
    kalman_drift_series = kf.run(mid)

    report_lines = ["# LOMBA 2 -- TREN / KEMIRINGAN\n",
                     "Target: t-stat slope OLS pada window N bar KE DEPAN (standardisasi otomatis via se(slope)). "
                     "Prediktor dari window N bar SEBELUM t. Data M5, subsampling "
                     f"{N_EVAL_POINTS} titik evaluasi merata sepanjang seri.\n"]

    fig, axes = plt.subplots(1, 3, figsize=(19, 6))
    fig.suptitle("LOMBA 2 -- TREN: IC Spearman per peserta", fontsize=13, fontweight="bold")

    all_results = {}
    for ax_i, N in enumerate(N_GRID):
        print(f"\n=== Lomba 2 -- N={N} bar ===")
        valid_range = np.arange(N, n_total - N)
        eval_idx = np.linspace(0, len(valid_range) - 1, min(N_EVAL_POINTS, len(valid_range))).astype(int)
        eval_t = valid_range[eval_idx]

        preds = {name: np.full(len(eval_t), np.nan) for name in
                  ["OLS", "Theil-Sen", "Siegel-RepMedian", "Mann-Kendall-Z", "QuantReg(tau=0.5)", "Huber", "Kalman-drift"]}
        targets = np.full(len(eval_t), np.nan)

        for i, t in enumerate(eval_t):
            past = mid[t - N: t]
            future = mid[t: t + N]
            _, target_tstat = ols_slope_tstat(future)
            targets[i] = target_tstat

            slope_ols, _ = ols_slope_tstat(past)
            preds["OLS"][i] = slope_ols
            preds["Theil-Sen"][i] = theil_sen_slope(past)
            preds["Siegel-RepMedian"][i] = siegel_repeated_median(past) if N <= 48 else np.nan
            preds["Mann-Kendall-Z"][i] = mann_kendall_z(past)
            try:
                preds["QuantReg(tau=0.5)"][i] = quantile_reg_slope(past)
            except Exception:
                pass
            try:
                preds["Huber"][i] = huber_slope(past)
            except Exception:
                pass
            preds["Kalman-drift"][i] = kalman_drift_series[t]

        train_eval_mask = eval_t < int(n_total * 0.70)
        test_eval_mask = ~train_eval_mask

        rows = []
        for name, pred in preds.items():
            tr_pred, tr_tgt = pred[test_eval_mask], targets[test_eval_mask]
            ic = spearman_ic(tr_pred, tr_tgt)
            sa = sign_accuracy(tr_pred, tr_tgt)
            mask = np.isfinite(tr_pred) & np.isfinite(tr_tgt)
            correct = (np.sign(tr_pred[mask]) == np.sign(tr_tgt[mask])).astype(float)
            pval = bootstrap_pvalue(correct - 0.5)
            rows.append({"peserta": name, "IC_spearman": ic, "sign_accuracy": sa,
                         "n_test": int(mask.sum()), "p_value_boot_vs_50pct": pval})

        base_pred = preds["OLS"]
        rows_df = pd.DataFrame(rows).sort_values("IC_spearman", ascending=False)
        all_results[N] = rows_df
        print(rows_df.to_string(index=False))
        winner = rows_df.iloc[0]
        base_row = rows_df[rows_df.peserta == "OLS"].iloc[0]
        print(f"WINNER N={N}: {winner['peserta']} IC={winner['IC_spearman']:.4f} "
              f"(baseline OLS IC={base_row['IC_spearman']:.4f})")

        report_lines.append(f"\n## N={N} bar\n")
        report_lines.append(rows_df.round(4).to_markdown(index=False))
        sig = winner['p_value_boot_vs_50pct'] < 0.05
        report_lines.append(f"\n**Menang: {winner['peserta']}** (IC={winner['IC_spearman']:.4f}, akurasi tanda="
                             f"{winner['sign_accuracy']:.3f} vs baseline OLS IC={base_row['IC_spearman']:.4f}). "
                             f"p-value(akurasi tanda vs 50%)={winner['p_value_boot_vs_50pct']:.4f} "
                             f"({'signifikan' if sig else 'TIDAK signifikan'}).\n")
        if winner["peserta"] == "OLS":
            report_lines.append("*(Catatan: peserta OLS dan baseline OLS identik by construction -- lihat spesifikasi lomba.)*\n")

        ax = axes[ax_i]
        plot_df = rows_df.sort_values("IC_spearman")
        colors = ["#2ca02c" if v > base_row["IC_spearman"] else ("#888888" if row=="OLS" else "#d62728") for v, row in zip(plot_df["IC_spearman"], plot_df["peserta"])]
        ax.barh(plot_df["peserta"], plot_df["IC_spearman"], color=colors)
        ax.axvline(base_row["IC_spearman"], color="black", linestyle="--", label="baseline OLS")
        ax.set_title(f"N={N} bar")
        ax.set_xlabel("IC Spearman")
        ax.legend(fontsize=8)

    plt.tight_layout()
    out_png = FIG_DIR / "lomba2_tren.png"
    plt.savefig(out_png, dpi=120)
    print(f"\nsaved {out_png}")
    (REPORTS / "LOMBA2_TREN.md").write_text("\n".join(report_lines))
    return all_results


if __name__ == "__main__":
    run()
