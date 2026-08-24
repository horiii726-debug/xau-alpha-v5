#!/usr/bin/env python3
"""L11 -- cek ulang G1 (simetri long/short) pada return DEMEANED, bukan
mentah, untuk SEMUA 130 kombinasi yang sebelumnya diuji (36+42 di H1
2003-2026, 24+28 di M5 H4/D1 2021-2026). G1-mentah bias oleh headwind
sekuler emas (+11.6%/thn = 4.62bps/hari) yang menghukum SEMUA short.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import HuberRegressor

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m5, load_m1, measure_cost_bps, REPORTS
from lomba4_entry import build_signals as build_signals_m5, H_GRID as H_GRID_M5
from lomba2_tren import ols_slope_tstat, theil_sen_slope, siegel_repeated_median, mann_kendall_z, quantile_reg_slope, huber_slope, KalmanDrift
from l3_lomba4_h1 import build_signals_h1, H_GRID_H1
from l3b_lomba4_gated import H_GRID_GATED

warnings.filterwarnings("ignore")

TAU_GRID = [1.0, 1.5]
LATIH_FRAC = 0.60
UJI_FRAC = 0.25


def g1_demeaned(direction, net_demeaned):
    long_m, short_m = direction > 0, direction < 0
    pnl_l = net_demeaned[long_m].sum() if long_m.any() else np.nan
    pnl_s = net_demeaned[short_m].sum() if short_m.any() else np.nan
    return (pnl_l > 0) and (pnl_s > 0), pnl_l, pnl_s


def demeaned_price(logp, window_bars):
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean = day_ret.rolling(window_bars, min_periods=window_bars // 6).mean()
    return np.cumsum((day_ret - roll_mean.fillna(0)).values)


def run_entry_family(bars, signals, cost_bps, h_grid, latih_uji_mask, uji_end, demeaned_window, label):
    mid = bars["mid_close"].values
    logp = np.log(mid)
    dlogp = demeaned_price(logp, demeaned_window)
    results = []
    for hname, H in h_grid.items():
        fwd_d = (np.roll(dlogp, -H) - dlogp) * 1e4
        fwd_d[-H:] = np.nan
        for tau in TAU_GRID:
            for name in signals.columns:
                z = signals[name].values
                take = (np.abs(z) >= tau) & latih_uji_mask & np.isfinite(fwd_d)
                n = int(take.sum())
                if n < 50:
                    continue
                direction = np.sign(z)[take]
                net_d = direction * fwd_d[take] - cost_bps
                passed, pnl_l, pnl_s = g1_demeaned(direction, net_d)
                results.append({"family": label, "horizon": hname, "tau": tau, "peserta": name,
                                 "n": n, "pnl_long_demean": pnl_l, "pnl_short_demean": pnl_s,
                                 "G1_demeaned_pass": passed})
    return results


def run_trend_family(bars, cost_bps, n_grid, latih_uji_mask, uji_end, latih_end, demeaned_window, label, n_eval=2500):
    mid = bars["mid_close"].values
    logp = np.log(mid)
    dlogp = demeaned_price(logp, demeaned_window)
    n_total = len(bars)

    kf_std = np.std(np.diff(logp[:latih_end]))
    kf = KalmanDrift(q_level=(kf_std * mid[0]) ** 2 * 0.01, q_drift=(kf_std * mid[0]) ** 2 * 1e-4, r_obs=(kf_std * mid[0]) ** 2 * 4)
    kalman_series = kf.run(mid)

    estimators = {"OLS": lambda y: ols_slope_tstat(y)[0], "Theil-Sen": theil_sen_slope,
                  "Siegel-RepMedian": siegel_repeated_median, "Mann-Kendall-Z": mann_kendall_z,
                  "QuantReg(tau=0.5)": quantile_reg_slope, "Huber": huber_slope}

    results = []
    for hname, N in n_grid.items():
        valid_range = np.arange(N, uji_end - N)
        eval_idx = np.linspace(0, len(valid_range) - 1, min(n_eval, len(valid_range))).astype(int)
        eval_t = valid_range[eval_idx]
        raw_slopes = {nm: np.full(len(eval_t), np.nan) for nm in list(estimators.keys()) + ["Kalman-drift"]}
        fwd_d = np.full(len(eval_t), np.nan)
        for i, t in enumerate(eval_t):
            past = mid[t - N:t]
            fwd_d[i] = (dlogp[t + N] - dlogp[t]) * 1e4 if t + N < len(dlogp) else np.nan
            for nm, fn in estimators.items():
                try:
                    raw_slopes[nm][i] = fn(past)
                except Exception:
                    pass
            raw_slopes["Kalman-drift"][i] = kalman_series[t]
        for tau in TAU_GRID:
            for nm, slopes in raw_slopes.items():
                latih_eval = eval_t < latih_end
                s_std = np.nanstd(slopes[latih_eval]) if latih_eval.sum() > 30 else np.nanstd(slopes)
                s_mean = np.nanmean(slopes[latih_eval]) if latih_eval.sum() > 30 else np.nanmean(slopes)
                zz = (slopes - s_mean) / (s_std + 1e-15)
                take = (np.abs(zz) >= tau) & np.isfinite(fwd_d) & np.isfinite(slopes)
                n = int(take.sum())
                if n < 50:
                    continue
                direction = np.sign(slopes[take])
                net_d = direction * fwd_d[take] - cost_bps
                passed, pnl_l, pnl_s = g1_demeaned(direction, net_d)
                results.append({"family": label, "horizon": hname, "tau": tau, "peserta": nm,
                                 "n": n, "pnl_long_demean": pnl_l, "pnl_short_demean": pnl_s,
                                 "G1_demeaned_pass": passed})
    return results


def main():
    all_results = []

    # ---- H1 2003-2026 ----
    h1 = pd.read_parquet("/workspace/data/bars_h1/XAUUSD_H1.parquet")
    n_h1 = len(h1)
    latih_end_h1 = int(n_h1 * LATIH_FRAC)
    uji_end_h1 = int(n_h1 * (LATIH_FRAC + UJI_FRAC))
    mask_h1 = np.zeros(n_h1, dtype=bool); mask_h1[:uji_end_h1] = True

    m1 = load_m1()
    m1_mask = np.zeros(len(m1), dtype=bool); m1_mask[: int(len(m1) * 0.70)] = True
    cost_bps = measure_cost_bps(m1, m1_mask)["round_trip_cost_bps"]

    print("=== H1 2003-2026, Lomba 4 (entry) ===")
    sig_h1 = build_signals_h1(h1)
    r = run_entry_family(h1, sig_h1, cost_bps, H_GRID_H1, mask_h1, uji_end_h1, 60 * 24, "H1-Lomba4")
    all_results += r
    print(f"  {sum(x['G1_demeaned_pass'] for x in r)}/{len(r)} lolos G1-demeaned")

    print("=== H1 2003-2026, Lomba 2 (tren) ===")
    r = run_trend_family(h1, cost_bps, {"12h": 12, "1d": 24, "5d": 120}, mask_h1, uji_end_h1, latih_end_h1, 60 * 24, "H1-Lomba2")
    all_results += r
    print(f"  {sum(x['G1_demeaned_pass'] for x in r)}/{len(r)} lolos G1-demeaned")

    # ---- M5 2021-2026, H4/D1 ----
    m5 = load_m5()
    n_m5 = len(m5)
    latih_end_m5 = int(n_m5 * LATIH_FRAC)
    uji_end_m5 = int(n_m5 * (LATIH_FRAC + UJI_FRAC))
    mask_m5 = np.zeros(n_m5, dtype=bool); mask_m5[:uji_end_m5] = True

    print("=== M5 2021-2026 (H4/D1), Lomba 4 (entry) ===")
    sig_m5 = build_signals_m5(m5)
    r = run_entry_family(m5, sig_m5, cost_bps, H_GRID_GATED, mask_m5, uji_end_m5, 60 * 288, "M5-Lomba4")
    all_results += r
    print(f"  {sum(x['G1_demeaned_pass'] for x in r)}/{len(r)} lolos G1-demeaned")

    print("=== M5 2021-2026 (H4/D1), Lomba 2 (tren) ===")
    r = run_trend_family(m5, cost_bps, {"H4": 48, "D1": 288}, mask_m5, uji_end_m5, latih_end_m5, 60 * 288, "M5-Lomba2", n_eval=2000)
    all_results += r
    print(f"  {sum(x['G1_demeaned_pass'] for x in r)}/{len(r)} lolos G1-demeaned")

    df = pd.DataFrame(all_results)
    n_pass = int(df["G1_demeaned_pass"].sum())
    n_total = len(df)
    print(f"\n{'='*60}\nTOTAL: {n_pass}/{n_total} lolos G1 (demeaned)\n{'='*60}")

    lines = ["# L11 -- G1 (simetri) diuji ulang pada return DEMEANED\n",
              f"Alasan: emas naik ~11.6%/thn 2003-2026 (headwind ~4.62bps/hari untuk SEMUA short di "
              f"return mentah). G1 sebelumnya berpotensi bias menolak alpha nyata. Diuji ulang: SEMUA "
              f"130 kombinasi sebelumnya, G1 dicek pada return DEMEANED (60-hari rolling mean dibuang).\n",
              f"\n**TOTAL: {n_pass}/{n_total} lolos G1-demeaned.**\n"]
    if n_pass > 0:
        surv = df[df["G1_demeaned_pass"]].sort_values("family")
        lines.append("\n## Kombinasi yang lolos G1-demeaned\n")
        lines.append(surv.round(4).to_markdown(index=False))
    lines.append(f"\n## Per keluarga\n")
    fam_summary = df.groupby("family")["G1_demeaned_pass"].agg(["sum", "count"])
    lines.append(fam_summary.to_markdown())

    verdict = "LOLOS <=3 -- harga saja SELESAI, lanjut L12 (data makro)" if n_pass <= 3 else f"{n_pass} lolos -- perlu diperiksa lebih lanjut sebelum lanjut L12"
    lines.append(f"\n## Verdict L11\n\n**{verdict}**\n")
    print(verdict)

    (REPORTS / "L11_G1_DEMEANED_RETEST.md").write_text("\n".join(lines))
    return n_pass


if __name__ == "__main__":
    n_pass = main()
