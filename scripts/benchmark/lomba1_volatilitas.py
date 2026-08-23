#!/usr/bin/env python3
"""LOMBA 1 -- VOLATILITAS. Target: realized variance periode berikutnya (dari
M1). Semua estimator memprediksi RV window [t, t+H) memakai HANYA data
sampai akhir window SEBELUMNYA (kausal, persistence-style forecast) --
kecuali GARCH/EWMA yang recursive filter, dan HAR-RV yang model OLS-fit-di-
train.
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m1, chronological_split, bootstrap_pvalue, qlike, qlike_median, rmse, mincer_zarnowitz_r2, FIG_DIR, REPORTS

warnings.filterwarnings("ignore")

HORIZONS = {"1h": 60, "4h": 240, "1d": 1440}  # in M1 bars


def build_windows(m1: pd.DataFrame, h_bars: int):
    """Partition M1 into non-overlapping windows of h_bars. Returns per-window:
    open,high,low,close (mid), realized_variance (sum of M1 log-return^2),
    and the raw M1 log-returns list per window (for bipower/medrv/minrv)."""
    n = len(m1)
    n_win = n // h_bars
    mid = m1["mid_close"].values[: n_win * h_bars]
    o = m1["mid_open"].values[: n_win * h_bars]
    hi = m1["mid_high"].values[: n_win * h_bars]
    lo = m1["mid_low"].values[: n_win * h_bars]
    logp = np.log(mid)
    r1 = np.diff(logp, prepend=logp[0])  # M1 log returns (first element ~0, harmless)
    r1 = r1.reshape(n_win, h_bars)
    r1[:, 0] = 0.0  # drop cross-window contamination on first bar of each window
    open_w = o.reshape(n_win, h_bars)[:, 0]
    close_w = mid.reshape(n_win, h_bars)[:, -1]
    high_w = hi.reshape(n_win, h_bars).max(axis=1)
    low_w = lo.reshape(n_win, h_bars).min(axis=1)
    rv = (r1 ** 2).sum(axis=1)
    ts_w = m1["ts"].values[: n_win * h_bars].reshape(n_win, h_bars)[:, 0]
    return {"ts": ts_w, "open": open_w, "high": high_w, "low": low_w, "close": close_w,
            "rv": rv, "r1_matrix": r1}


# ---------------------------------------------------------------- OHLC-range estimators (prior-window persistence) --

def parkinson(o, h, l, c):
    return (1.0 / (4 * np.log(2))) * (np.log(h / l)) ** 2


def garman_klass(o, h, l, c):
    return 0.5 * (np.log(h / l)) ** 2 - (2 * np.log(2) - 1) * (np.log(c / o)) ** 2


def rogers_satchell(o, h, l, c):
    return np.log(h / c) * np.log(h / o) + np.log(l / c) * np.log(l / o)


def yang_zhang(o, h, l, c, window: int = 20):
    """Rolling-window YZ (perlu beberapa bar prior), kausal: pakai window bar
    SEBELUM window target."""
    n = len(o)
    out = np.full(n, np.nan)
    log_o_prevc = np.full(n, np.nan)
    log_o_prevc[1:] = np.log(o[1:] / c[:-1])  # overnight (open vs prior close)
    log_c_o = np.log(c / o)
    rs = rogers_satchell(o, h, l, c)
    k = 0.34 / (1.34 + (window + 1) / (window - 1))
    for i in range(window, n):
        seg_o = log_o_prevc[i - window + 1: i + 1]
        seg_co = log_c_o[i - window + 1: i + 1]
        seg_rs = rs[i - window + 1: i + 1]
        var_o = np.nanvar(seg_o, ddof=1)
        var_c = np.nanvar(seg_co, ddof=1)
        var_rs = np.nanmean(seg_rs)
        out[i] = var_o + k * var_c + (1 - k) * var_rs
    return out


def bipower(r1_matrix):
    mu1 = np.sqrt(2 / np.pi)
    absr = np.abs(r1_matrix)
    prod = absr[:, 1:] * absr[:, :-1]
    return (1.0 / mu1 ** 2) * prod.sum(axis=1)


def medrv(r1_matrix):
    n_bars = r1_matrix.shape[1]
    scale = np.pi / (6 - 4 * np.sqrt(3) + np.pi)
    out = np.empty(r1_matrix.shape[0])
    for i in range(r1_matrix.shape[0]):
        row = np.abs(r1_matrix[i])
        triples = np.stack([row[:-2], row[1:-1], row[2:]], axis=1)
        med = np.median(triples, axis=1)
        out[i] = scale * (n_bars / (n_bars - 2)) * (med ** 2).sum()
    return out


def minrv(r1_matrix):
    n_bars = r1_matrix.shape[1]
    scale = np.pi / (np.pi - 2)
    absr = np.abs(r1_matrix)
    pair_min = np.minimum(absr[:, 1:], absr[:, :-1])
    return scale * (n_bars / (n_bars - 1)) * (pair_min ** 2).sum(axis=1)


def close_to_close_baseline(close):
    """Naive: prior period's own squared close-to-close return as forecast."""
    logc = np.log(close)
    r = np.diff(logc, prepend=logc[0])
    r[0] = np.nan
    return r ** 2  # already "prior period's realized var proxy" when shifted by 1 downstream


def ewma_forecast(prior_period_return_sq: np.ndarray, lam: float) -> np.ndarray:
    n = len(prior_period_return_sq)
    out = np.full(n, np.nan)
    out[0] = np.nanmean(prior_period_return_sq[: max(1, n // 10)])
    for t in range(1, n):
        prev = out[t - 1] if np.isfinite(out[t - 1]) else prior_period_return_sq[t - 1]
        r2 = prior_period_return_sq[t - 1] if np.isfinite(prior_period_return_sq[t - 1]) else prev
        out[t] = lam * prev + (1 - lam) * r2
    return out


def garch_forecast(period_returns: np.ndarray, train_mask: np.ndarray, dist: str = "normal") -> np.ndarray:
    from arch import arch_model
    r_pct = period_returns * 100  # arch prefers %-scale for numerical stability
    train_r = r_pct[train_mask]
    train_r = train_r[np.isfinite(train_r)]
    am = arch_model(train_r, vol="GARCH", p=1, q=1, dist=dist, mean="Zero")
    res = am.fit(disp="off")
    omega, alpha, beta = res.params["omega"], res.params["alpha[1]"], res.params["beta[1]"]
    n = len(r_pct)
    h = np.full(n, np.nan)
    h[0] = res.conditional_volatility[0] ** 2 if len(res.conditional_volatility) else np.nanvar(train_r)
    long_run = omega / max(1e-12, 1 - alpha - beta)
    for t in range(1, n):
        prev_r = r_pct[t - 1] if np.isfinite(r_pct[t - 1]) else 0.0
        prev_h = h[t - 1] if np.isfinite(h[t - 1]) else long_run
        h[t] = omega + alpha * prev_r ** 2 + beta * prev_h
    return (h / 1e4)  # back to return-scale variance (undo the *100)


def har_rv_forecast(rv: np.ndarray, train_mask: np.ndarray, short=1, med=5, long=22) -> np.ndarray:
    import statsmodels.api as sm
    n = len(rv)
    rv_d = pd.Series(rv)
    lag1 = rv_d.shift(1)
    lag_med = rv_d.shift(1).rolling(med).mean()
    lag_long = rv_d.shift(1).rolling(long).mean()
    X = pd.DataFrame({"lag1": lag1, "lag_med": lag_med, "lag_long": lag_long})
    valid = X.notna().all(axis=1)
    train_fit_mask = train_mask & valid.values
    Xtr = sm.add_constant(X[train_fit_mask])
    ytr = rv_d[train_fit_mask]
    model = sm.OLS(ytr, Xtr).fit()
    Xall = sm.add_constant(X, has_constant="add")
    pred = model.predict(Xall).to_numpy().copy()
    pred[~valid.values] = np.nan
    return pred


def run():
    m1 = load_m1()
    all_results = {}
    fig, axes = plt.subplots(1, 3, figsize=(19, 6))
    fig.suptitle("LOMBA 1 -- VOLATILITAS: QLIKE per peserta (lebih rendah = lebih baik)", fontsize=13, fontweight="bold")

    report_lines = ["# LOMBA 1 -- VOLATILITAS\n",
                     "Target: realized variance window berikutnya (dari M1 log-return^2). "
                     "Metrik utama QLIKE (lebih rendah lebih baik). Split 70/30 kronologis, fit hanya di train.\n"]

    for ax_i, (hname, hbars) in enumerate(HORIZONS.items()):
        print(f"\n=== Lomba 1 -- horizon {hname} ({hbars} M1 bar) ===")
        w = build_windows(m1, hbars)
        n = len(w["rv"])
        train_mask, test_mask = chronological_split(n, 0.70)
        rv_target = w["rv"]  # RV of window i itself

        # OHLC-range & jump-robust estimators: PRIOR window's estimate -> forecast for CURRENT window (shift by 1)
        park = parkinson(w["open"], w["high"], w["low"], w["close"])
        gk = garman_klass(w["open"], w["high"], w["low"], w["close"])
        rs = rogers_satchell(w["open"], w["high"], w["low"], w["close"])
        yz = yang_zhang(w["open"], w["high"], w["low"], w["close"], window=20)
        bp = bipower(w["r1_matrix"])
        mrv = medrv(w["r1_matrix"])
        mnrv = minrv(w["r1_matrix"])
        c2c = close_to_close_baseline(w["close"])

        def shift1(x):
            out = np.full(len(x), np.nan)
            out[1:] = x[:-1]
            return out

        participants = {
            "Parkinson": shift1(park),
            "Garman-Klass": shift1(gk),
            "Rogers-Satchell": shift1(rs),
            "Yang-Zhang(w20)": shift1(yz),
            "Bipower": shift1(bp),
            "MedRV": shift1(mrv),
            "MinRV": shift1(mnrv),
            "EWMA(0.94)": ewma_forecast(shift1(c2c), 0.94),
            "EWMA(0.97)": ewma_forecast(shift1(c2c), 0.97),
        }

        period_ret = np.diff(np.log(w["close"]), prepend=np.log(w["close"])[0])
        period_ret[0] = np.nan
        try:
            participants["GARCH(1,1)-normal"] = garch_forecast(period_ret, train_mask, "normal")
        except Exception as e:
            print(f"  GARCH normal failed: {e}")
        try:
            participants["GARCH(1,1)-student-t"] = garch_forecast(period_ret, train_mask, "studentst")
        except Exception as e:
            print(f"  GARCH t failed: {e}")
        try:
            med_lag = {"1h": 24, "4h": 6, "1d": 5}[hname]
            long_lag = {"1h": 168, "4h": 30, "1d": 22}[hname]
            participants["HAR-RV"] = har_rv_forecast(rv_target, train_mask, 1, med_lag, long_lag)
        except Exception as e:
            print(f"  HAR-RV failed: {e}")

        baseline = shift1(c2c)  # naive close-to-close variance persistence

        rows = []
        for name, pred in participants.items():
            test_pred = pred[test_mask]
            test_tgt = rv_target[test_mask]
            test_base = baseline[test_mask]
            q = qlike(test_pred, test_tgt)
            qm = qlike_median(test_pred, test_tgt)
            q_base = qlike(test_base, test_tgt)
            r_ = rmse(test_pred, test_tgt)
            r2 = mincer_zarnowitz_r2(test_pred, test_tgt)
            # bootstrap: per-obs QLIKE diff (baseline_loss - participant_loss), positive = participant better
            mask = np.isfinite(test_pred) & np.isfinite(test_tgt) & np.isfinite(test_base) & (test_pred > 0) & (test_base > 0) & (test_tgt > 0)
            loss_p = test_tgt[mask] / test_pred[mask] - np.log(test_tgt[mask] / test_pred[mask]) - 1
            loss_b = test_tgt[mask] / test_base[mask] - np.log(test_tgt[mask] / test_base[mask]) - 1
            pval = bootstrap_pvalue(loss_b - loss_p)  # positive means participant loss < baseline loss
            rows.append({"peserta": name, "QLIKE_mean": q, "QLIKE_median": qm, "RMSE": r_, "MZ_R2": r2,
                         "QLIKE_vs_baseline": q - q_base, "p_value_boot": pval, "n_test": int(mask.sum())})

        rows.append({"peserta": "BASELINE (close-to-close)", "QLIKE_mean": qlike(baseline[test_mask], rv_target[test_mask]),
                     "QLIKE_median": qlike_median(baseline[test_mask], rv_target[test_mask]),
                     "RMSE": rmse(baseline[test_mask], rv_target[test_mask]),
                     "MZ_R2": mincer_zarnowitz_r2(baseline[test_mask], rv_target[test_mask]),
                     "QLIKE_vs_baseline": 0.0, "p_value_boot": np.nan, "n_test": int(test_mask.sum())})

        df = pd.DataFrame(rows).sort_values("QLIKE_median")
        all_results[hname] = df
        winner = df.iloc[0]
        base_row = df[df.peserta.str.contains("BASELINE")].iloc[0]
        print(df.to_string(index=False))
        print(f"WINNER {hname}: {winner['peserta']} QLIKE_median={winner['QLIKE_median']:.4f} "
              f"(baseline QLIKE_median={base_row['QLIKE_median']:.4f}; QLIKE_mean baseline meledak ke "
              f"{base_row['QLIKE_mean']:.1f} karena outlier ekor -- lihat catatan robustness)")

        report_lines.append(f"\n## Horizon {hname}\n")
        report_lines.append(df.round(4).to_markdown(index=False))
        report_lines.append(
            f"\n> **Catatan robustness:** `QLIKE_mean` baseline meledak ({base_row['QLIKE_mean']:.1f}) karena "
            f"baseline (return kuadrat SATU periode) kadang kebetulan hampir nol -> rasio RV/pred meledak. "
            f"Ini properti nyata dari estimator naive (dikonfirmasi manual, bukan bug), bukan alasan "
            f"mengabaikannya -- karena itu **`QLIKE_median` dipakai untuk peringkat** (lebih robust ke ekor), "
            f"`QLIKE_mean` tetap dilaporkan apa adanya untuk transparansi.\n"
        )
        sig = winner['p_value_boot'] < 0.05 if pd.notna(winner['p_value_boot']) else False
        report_lines.append(f"\n**Menang: {winner['peserta']}** (QLIKE_median={winner['QLIKE_median']:.4f} vs "
                             f"baseline {base_row['QLIKE_median']:.4f}). "
                             f"p-value bootstrap={winner['p_value_boot']:.4f} "
                             f"({'signifikan' if sig else 'TIDAK signifikan'} pada alpha=0.05).\n")

        ax = axes[ax_i]
        plot_df = df[~df.peserta.str.contains("BASELINE")].sort_values("QLIKE_median")
        colors = ["#2ca02c" if v < base_row["QLIKE_median"] else "#d62728" for v in plot_df["QLIKE_median"]]
        ax.barh(plot_df["peserta"], plot_df["QLIKE_median"], color=colors)
        ax.axvline(base_row["QLIKE_median"], color="black", linestyle="--", label="baseline")
        ax.set_title(f"Horizon {hname}")
        ax.set_xlabel("QLIKE median (rendah=baik)")
        ax.legend(fontsize=8)
        ax.invert_yaxis()

    plt.tight_layout()
    out_png = FIG_DIR / "lomba1_volatilitas.png"
    plt.savefig(out_png, dpi=120)
    print(f"\nsaved {out_png}")

    (REPORTS / "LOMBA1_VOLATILITAS.md").write_text("\n".join(report_lines))
    return all_results


if __name__ == "__main__":
    run()
