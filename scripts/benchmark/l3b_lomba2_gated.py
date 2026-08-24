#!/usr/bin/env python3
"""L3 -- ulang LOMBA 2 (tren) di data M5 2021-2026, HANYA horizon lolos L2b
(H4=48bar M5, D1=288bar M5), gerbang G1-G4 di depan. N dikonversi ke satuan
bar M5 yang setara: H4~48 -> N=[24,48,96] (setengah/satu/dua kali H4),
D1~288 -> N=[144,288,576]."""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import HuberRegressor
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m5, load_m1, measure_cost_bps, FIG_DIR, REPORTS
from gates_g1g4 import run_all_gates
from lomba2_tren import ols_slope_tstat, theil_sen_slope, siegel_repeated_median, mann_kendall_z, quantile_reg_slope, huber_slope, KalmanDrift

warnings.filterwarnings("ignore")

LATIH_FRAC = 0.60
UJI_FRAC = 0.25
TAU_GRID = [1.0, 1.5]
N_GRID = {"H4": 48, "D1": 288}
N_EVAL_POINTS = 3000


def main():
    m5 = load_m5()
    mid = m5["mid_close"].values
    logp = np.log(mid)
    n_total = len(m5)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    bar_time = m5["bar_time"].values

    m1 = load_m1()
    m1_train_mask = np.zeros(len(m1), dtype=bool)
    m1_train_mask[: int(len(m1) * 0.70)] = True
    cost_bps = measure_cost_bps(m1, m1_train_mask)["round_trip_cost_bps"]

    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60 * 288, min_periods=288 * 10).mean()
    demeaned_logp = np.cumsum((day_ret - roll_mean_60d.fillna(0)).values)

    t0 = pd.Timestamp(bar_time[0]); t_uji_end = pd.Timestamp(bar_time[uji_end - 1])
    span = (t_uji_end - t0) / 3
    regime_bounds = [
        (f"blok-1", np.datetime64(t0), np.datetime64(t0 + span)),
        (f"blok-2", np.datetime64(t0 + span), np.datetime64(t0 + 2 * span)),
        (f"blok-3", np.datetime64(t0 + 2 * span), np.datetime64(t_uji_end)),
    ]

    kf_std = np.std(np.diff(logp[:latih_end]))
    kf = KalmanDrift(q_level=(kf_std * mid[0]) ** 2 * 0.01, q_drift=(kf_std * mid[0]) ** 2 * 1e-4, r_obs=(kf_std * mid[0]) ** 2 * 4)
    kalman_drift_series = kf.run(mid)

    estimators = {
        "OLS": lambda y: ols_slope_tstat(y)[0], "Theil-Sen": theil_sen_slope,
        "Siegel-RepMedian": siegel_repeated_median, "Mann-Kendall-Z": mann_kendall_z,
        "QuantReg(tau=0.5)": quantile_reg_slope, "Huber": huber_slope,
    }

    report = ["# L3 -- Lomba 2 (Tren) diulang, gerbang G1-G4, HANYA N setara horizon lolos L2b (H4, D1)\n"]
    survivors = []
    all_results = {}
    for hname, N in N_GRID.items():
        valid_range = np.arange(N, uji_end - N)
        eval_idx = np.linspace(0, len(valid_range) - 1, min(N_EVAL_POINTS, len(valid_range))).astype(int)
        eval_t = valid_range[eval_idx]
        raw_slopes = {name: np.full(len(eval_t), np.nan) for name in list(estimators.keys()) + ["Kalman-drift"]}
        fwd_bps = np.full(len(eval_t), np.nan)
        fwd_bps_demeaned = np.full(len(eval_t), np.nan)
        for i, t in enumerate(eval_t):
            past = mid[t - N: t]
            fwd_bps[i] = (logp[t + N] - logp[t]) * 1e4 if t + N < n_total else np.nan
            fwd_bps_demeaned[i] = (demeaned_logp[t + N] - demeaned_logp[t]) * 1e4 if t + N < len(demeaned_logp) else np.nan
            for name, fn in estimators.items():
                try:
                    raw_slopes[name][i] = fn(past)
                except Exception:
                    pass
            raw_slopes["Kalman-drift"][i] = kalman_drift_series[t]

        for tau in TAU_GRID:
            for name, slopes in raw_slopes.items():
                latih_eval_mask = eval_t < latih_end
                slope_std = np.nanstd(slopes[latih_eval_mask]) if latih_eval_mask.sum() > 30 else np.nanstd(slopes)
                slope_mean = np.nanmean(slopes[latih_eval_mask]) if latih_eval_mask.sum() > 30 else np.nanmean(slopes)
                z = (slopes - slope_mean) / (slope_std + 1e-15)
                take = (np.abs(z) >= tau) & np.isfinite(fwd_bps) & np.isfinite(slopes)
                n = int(take.sum())
                if n < 50:
                    continue
                direction = np.sign(slopes[take])
                net = direction * fwd_bps[take] - cost_bps
                net_demeaned = direction * fwd_bps_demeaned[take] - cost_bps
                entry_idx = eval_t[take]
                entry_bt = bar_time[entry_idx]
                gates = run_all_gates(direction, net, net_demeaned, entry_bt, entry_idx, uji_end, regime_bounds)
                key = (hname, tau, name)
                all_results[key] = gates
                status = "LOLOS SEMUA" if gates["overall_pass"] else f"GAGAL di {gates['stopped_at']}"
                print(f"[{hname} N={N} tau={tau}] {name}: n={n}, {status}")
                if gates["overall_pass"]:
                    survivors.append({"horizon": hname, "N": N, "tau": tau, "peserta": name, "n_trades": n,
                                       "expectancy_net_bps": float(net.mean())})

    report.append(f"\n## Ringkasan: {len(survivors)} lolos dari {len(all_results)} diuji\n")
    if survivors:
        surv_df = pd.DataFrame(survivors).sort_values("expectancy_net_bps", ascending=False)
        report.append(surv_df.round(4).to_markdown(index=False))
        print(f"SURVIVOR:\n{surv_df.to_string(index=False)}")
    else:
        report.append("\n**NOL survivor.**\n")
        print("NOL SURVIVOR")
    stop_counts = {}
    for key, g in all_results.items():
        stop_counts[g["stopped_at"] or "LOLOS"] = stop_counts.get(g["stopped_at"] or "LOLOS", 0) + 1
    report.append("\n## Gerbang gugur\n\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(stop_counts.items(), key=lambda x: -x[1])))
    print("Distribusi:", stop_counts)
    (REPORTS / "L3_LOMBA2_GATED.md").write_text("\n".join(report))

    fig, ax = plt.subplots(figsize=(9, 5.5))
    labels = list(stop_counts.keys()); values = [stop_counts[k] for k in labels]
    colors = ["#2ca02c" if k == "LOLOS" else "#d62728" for k in labels]
    ax.bar(labels, values, color=colors)
    ax.set_title(f"L3 Lomba 2 (H4+D1, 2021-2026): {len(survivors)}/{len(all_results)} lolos")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "l3_lomba2_gated.png", dpi=120)
    return survivors


if __name__ == "__main__":
    s = main()
    sys.exit(0 if s else 1)
