#!/usr/bin/env python3
"""LOMBA 5 -- SL/TP. Entry DIKUNCI = pemenang Lomba 4 (CUSUM, H=1d, tau=1.5,
expectancy net +14.1bps, p=0.000). Barrier SIMETRIS = k * vol_estimate,
k=2.0 TETAP untuk semua peserta (yang berbeda HANYA metode estimasi vol/
kuantil -- supaya perbandingan adil, satu variabel diubah). Baseline =
Parkinson (barrier tetap k x Parkinson) -- identik dgn peserta 'Parkinson'
by construction (dicatat, bukan disembunyikan, sama seperti kasus OLS di
Lomba 2). Simulasi first-passage pada M1 (bukan M5) untuk akurasi SL/TP.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m1, load_m5, chronological_split, bootstrap_pvalue, measure_cost_bps, FIG_DIR, REPORTS
from lomba4_entry import build_signals, H_GRID

warnings.filterwarnings("ignore")

K_BARRIER = 2.0
H_M5 = H_GRID["1d"]  # 288 M5 bars = 1 day
TAU_LOCKED = 1.5


def parkinson_vol_daily(m5: pd.DataFrame, day_bars: int = H_M5, roll_days: int = 20) -> pd.Series:
    """Rolling Parkinson vol on trailing 1-day windows, dikonversi ke UNIT
    HARGA (bukan skala log-return) supaya bisa dipakai langsung sebagai
    jarak barrier."""
    high = m5["mid_close"].rolling(day_bars).max()
    low = m5["mid_close"].rolling(day_bars).min()
    park_var_1window = (1.0 / (4 * np.log(2))) * (np.log(high / low)) ** 2
    sigma_logret = np.sqrt(park_var_1window.rolling(roll_days).mean())
    return sigma_logret * m5["mid_close"]


def empirical_quantile_vol(m5: pd.DataFrame, day_bars: int = H_M5, roll_days: int = 60, q: float = 0.90) -> pd.Series:
    ret_1d = m5["mid_close"].pct_change(day_bars).abs()
    return ret_1d.rolling(day_bars * roll_days).quantile(q) * m5["mid_close"]


def pot_gpd_vol(m5: pd.DataFrame, day_bars: int = H_M5, roll_days: int = 60, thresh_q: float = 0.90) -> pd.Series:
    """Rolling POT/GPD: fit GPD to exceedances of |1-day return| over
    thresh_q, derive 90th-percentile-equivalent level from the fitted tail
    (bukan langsung dari kuantil empiris -- ekstrapolasi parametrik)."""
    ret_1d_abs = m5["mid_close"].pct_change(day_bars).abs()
    n = len(ret_1d_abs)
    out = np.full(n, np.nan)
    vals = ret_1d_abs.values
    window = day_bars * roll_days
    step = max(1, day_bars // 4)  # recompute every ~1/4 day for speed, ffill between
    last = np.nan
    for i in range(window, n, step):
        seg = vals[i - window:i]
        seg = seg[np.isfinite(seg)]
        if len(seg) < 50:
            continue
        u = np.quantile(seg, thresh_q)
        exceed = seg[seg > u] - u
        if len(exceed) < 20:
            continue
        try:
            c, loc, scale = stats.genpareto.fit(exceed, floc=0)
            level = u + stats.genpareto.ppf(thresh_q, c, loc=0, scale=scale)
            last = level
        except Exception:
            pass
        out[i] = last
    out = pd.Series(out, index=m5.index).ffill().values
    return pd.Series(out * m5["mid_close"].values, index=m5.index)


def garch_vol_daily(m5: pd.DataFrame, train_mask: np.ndarray, day_bars: int = H_M5) -> pd.Series:
    from arch import arch_model
    ret_1d = np.log(m5["mid_close"]).diff(day_bars).dropna()
    r_pct = ret_1d.values * 100
    n_full = len(m5)
    idx_map = ret_1d.index
    train_end = int(n_full * 0.70)
    train_sel = idx_map < train_end
    am = arch_model(r_pct[train_sel], vol="GARCH", p=1, q=1, dist="normal", mean="Zero")
    res = am.fit(disp="off")
    omega, alpha, beta = res.params["omega"], res.params["alpha[1]"], res.params["beta[1]"]
    h = np.full(len(r_pct), np.nan)
    long_run = omega / max(1e-12, 1 - alpha - beta)
    h[0] = long_run
    for t in range(1, len(r_pct)):
        prev_r = r_pct[t - 1] if np.isfinite(r_pct[t - 1]) else 0.0
        prev_h = h[t - 1] if np.isfinite(h[t - 1]) else long_run
        h[t] = omega + alpha * prev_r ** 2 + beta * prev_h
    sigma_pct = np.sqrt(h) / 100.0
    out = pd.Series(np.nan, index=m5.index)
    out.iloc[idx_map] = sigma_pct * m5["mid_close"].values[idx_map]
    return out.ffill()


def simulate_barrier(m1: pd.DataFrame, entry_ts, direction: float, sl_dist: float, tp_dist: float,
                      max_bars_m1: int, cost_bps: float, entry_price_lookup):
    entry_idx = entry_price_lookup.get(entry_ts)
    if entry_idx is None:
        return None
    entry_price = m1["mid_close"].values[entry_idx]
    sl_level = entry_price - direction * sl_dist
    tp_level = entry_price + direction * tp_dist
    end_idx = min(entry_idx + max_bars_m1, len(m1) - 1)
    path = m1["mid_close"].values[entry_idx + 1: end_idx + 1]
    if len(path) < 2:
        return None
    if direction > 0:
        hit_sl = np.where(path <= sl_level)[0]
        hit_tp = np.where(path >= tp_level)[0]
    else:
        hit_sl = np.where(path >= sl_level)[0]
        hit_tp = np.where(path <= tp_level)[0]
    first_sl = hit_sl[0] if len(hit_sl) else np.inf
    first_tp = hit_tp[0] if len(hit_tp) else np.inf
    favorable_excursion = (path - entry_price) * direction
    mfe = float(np.max(favorable_excursion)) if len(favorable_excursion) else 0.0
    adverse_excursion = -(path - entry_price) * direction
    mae = float(np.max(adverse_excursion)) if len(adverse_excursion) else 0.0

    if first_sl < first_tp:
        exit_price = sl_level
        exit_type = "SL"
    elif first_tp < first_sl:
        exit_price = tp_level
        exit_type = "TP"
    else:
        exit_price = path[-1]
        exit_type = "TIME"
    pnl_price = (exit_price - entry_price) * direction
    pnl_bps = pnl_price / entry_price * 1e4 - cost_bps
    realized_favorable_frac = (pnl_price / mfe) if mfe > 1e-12 else np.nan
    return {"exit_type": exit_type, "pnl_net_bps": pnl_bps, "mae_bps": mae / entry_price * 1e4,
            "mfe_bps": mfe / entry_price * 1e4, "mae_mfe_efficiency": realized_favorable_frac}


def run():
    m5 = load_m5()
    m1 = load_m1()
    n_total = len(m5)
    train_mask, test_mask = chronological_split(n_total, 0.70)
    cost_info = measure_cost_bps(m1, chronological_split(len(m1), 0.70)[0])
    cost_bps = cost_info["round_trip_cost_bps"]

    signals = build_signals(m5)
    cusum_z = signals["CUSUM"].values
    direction_all = np.sign(cusum_z)
    take = (np.abs(cusum_z) >= TAU_LOCKED) & test_mask
    entry_positions = np.where(take)[0]
    print(f"Entry terkunci: CUSUM tau={TAU_LOCKED}, H=1d -- {len(entry_positions)} entri di TEST")

    park_vol = parkinson_vol_daily(m5)
    emp_vol = empirical_quantile_vol(m5)
    pot_vol = pot_gpd_vol(m5)
    print("fitting GARCH utk barrier (bisa perlu waktu)...")
    garch_vol = garch_vol_daily(m5, train_mask)

    entry_ts_list = m5["bar_time"].values[entry_positions]
    m1_ts_to_idx = pd.Series(np.arange(len(m1)), index=m1["ts"].values)
    entry_price_lookup = {}
    for ts in entry_ts_list:
        pos = m1_ts_to_idx.index.searchsorted(ts)
        if pos < len(m1_ts_to_idx):
            entry_price_lookup[ts] = int(m1_ts_to_idx.iloc[pos])

    vol_methods = {"Parkinson": park_vol, "EmpiricalQuantile(p90)": emp_vol,
                   "POT-GPD": pot_vol, "GARCH": garch_vol}

    results_by_method = {}
    for name, vol_series in vol_methods.items():
        vol_vals = vol_series.values
        recs = []
        for pos, ts in zip(entry_positions, entry_ts_list):
            vol_at_entry = vol_vals[pos]
            if not np.isfinite(vol_at_entry) or vol_at_entry <= 0:
                continue
            direction = direction_all[pos]
            r = simulate_barrier(m1, ts, direction, K_BARRIER * vol_at_entry, K_BARRIER * vol_at_entry,
                                  max_bars_m1=H_M5 * 5, cost_bps=cost_bps, entry_price_lookup=entry_price_lookup)
            if r is not None:
                recs.append(r)
        results_by_method[name] = pd.DataFrame(recs)
        print(f"{name}: {len(recs)} trade tersimulasi")

    rows = []
    for name, df in results_by_method.items():
        if len(df) < 20:
            rows.append({"peserta": name, "n_trades": len(df), "expectancy_net_bps": np.nan,
                         "premature_stop_ratio": np.nan, "mae_mfe_efficiency_median": np.nan, "p_value_boot": np.nan})
            continue
        exp_net = df["pnl_net_bps"].mean()
        stop_ratio = (df["exit_type"] == "SL").mean()
        eff = df["mae_mfe_efficiency"].median()
        pval = bootstrap_pvalue(df["pnl_net_bps"].values)
        rows.append({"peserta": name, "n_trades": len(df), "expectancy_net_bps": exp_net,
                     "premature_stop_ratio": stop_ratio, "mae_mfe_efficiency_median": eff, "p_value_boot": pval})

    result_df = pd.DataFrame(rows).sort_values("expectancy_net_bps", ascending=False)
    print(result_df.to_string(index=False))
    winner = result_df.iloc[0]
    base_row = result_df[result_df.peserta == "Parkinson"].iloc[0]
    print(f"WINNER: {winner['peserta']} expectancy_net={winner['expectancy_net_bps']:.3f}bps "
          f"(baseline/Parkinson={base_row['expectancy_net_bps']:.3f}bps)")

    report_lines = ["# LOMBA 5 -- SL/TP\n",
                     f"**Entry DIKUNCI**: pemenang Lomba 4 = CUSUM, H=1d, tau={TAU_LOCKED} "
                     f"(expectancy net Lomba 4: +14.1bps, p=0.000). {len(entry_positions)} entri di TEST.\n",
                     f"Barrier simetris = k * vol_estimate, **k=2.0 TETAP untuk semua peserta** -- yang "
                     f"berbeda HANYA metode estimasi vol. Biaya round-trip: {cost_bps:.3f}bps (sama seperti "
                     f"Lomba 4). Simulasi first-passage pada M1 (bukan M5) untuk akurasi SL/TP.\n",
                     "\n" + result_df.round(4).to_markdown(index=False)]
    sig = pd.notna(winner['p_value_boot']) and winner['p_value_boot'] < 0.05
    report_lines.append(f"\n**Menang: {winner['peserta']}** (expectancy net={winner['expectancy_net_bps']:.3f}bps "
                         f"vs baseline/Parkinson={base_row['expectancy_net_bps']:.3f}bps). p-value bootstrap="
                         f"{winner['p_value_boot']:.4f} ({'signifikan' if sig else 'TIDAK signifikan'}).\n")
    if winner["peserta"] == "Parkinson":
        report_lines.append("*(Catatan: peserta Parkinson = baseline by construction, sama seperti kasus OLS di Lomba 2.)*\n")

    fig, ax = plt.subplots(figsize=(9, 6))
    plot_df = result_df.dropna(subset=["expectancy_net_bps"]).sort_values("expectancy_net_bps")
    colors = ["#888888" if p == "Parkinson" else ("#2ca02c" if v > base_row["expectancy_net_bps"] else "#d62728")
              for v, p in zip(plot_df["expectancy_net_bps"], plot_df["peserta"])]
    ax.barh(plot_df["peserta"], plot_df["expectancy_net_bps"], color=colors)
    ax.axvline(base_row["expectancy_net_bps"], color="black", linestyle="--", label="baseline (Parkinson)")
    ax.set_title("LOMBA 5 -- SL/TP: expectancy bersih (bps), entry=CUSUM H=1d tau=1.5")
    ax.set_xlabel("expectancy net (bps)")
    ax.legend(fontsize=8)
    plt.tight_layout()
    out_png = FIG_DIR / "lomba5_sltp.png"
    plt.savefig(out_png, dpi=120)
    print(f"saved {out_png}")

    (REPORTS / "LOMBA5_SLTP.md").write_text("\n".join(report_lines))
    return result_df


if __name__ == "__main__":
    run()
