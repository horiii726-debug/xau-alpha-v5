"""V7.1 LANGKAH 3 -- gerbang simetri G1-G4, WAJIB dievaluasi SEBELUM kandidat
arah manapun boleh masuk peringkat. Urutan: G1 -> G2 -> G3 -> G4 -> BARU
peringkat.
"""
import numpy as np
import pandas as pd

from common import bootstrap_pvalue


def check_g1_symmetry(direction: np.ndarray, net_bps: np.ndarray) -> dict:
    long_mask = direction > 0
    short_mask = direction < 0
    pnl_long = net_bps[long_mask].sum() if long_mask.any() else np.nan
    pnl_short = net_bps[short_mask].sum() if short_mask.any() else np.nan
    exp_long = net_bps[long_mask].mean() if long_mask.any() else np.nan
    exp_short = net_bps[short_mask].mean() if short_mask.any() else np.nan
    passed = (pnl_long > 0) and (pnl_short > 0)
    return {"pass": bool(passed), "pnl_long": float(pnl_long), "pnl_short": float(pnl_short),
            "exp_long_bps": float(exp_long), "exp_short_bps": float(exp_short),
            "n_long": int(long_mask.sum()), "n_short": int(short_mask.sum())}


def check_g2_demeaned(direction: np.ndarray, net_bps_demeaned: np.ndarray) -> dict:
    mean_exp = float(np.nanmean(net_bps_demeaned))
    passed = mean_exp > 0
    return {"pass": bool(passed), "expectancy_demeaned_bps": mean_exp}


def check_g3_regime(direction: np.ndarray, net_bps: np.ndarray, entry_bar_time: np.ndarray,
                     regime_bounds: list) -> dict:
    """regime_bounds: list of (name, start_ts, end_ts) tuples."""
    results = []
    for name, start_ts, end_ts in regime_bounds:
        mask = (entry_bar_time >= start_ts) & (entry_bar_time < end_ts)
        n = int(mask.sum())
        exp = float(net_bps[mask].mean()) if n >= 10 else np.nan
        results.append({"blok": name, "n_trades": n, "expectancy_bps": exp})
    n_positive_blocks = sum(1 for r in results if pd.notna(r["expectancy_bps"]) and r["expectancy_bps"] > 0)
    passed = n_positive_blocks >= 2
    return {"pass": bool(passed), "blocks": results, "n_positive_blocks": n_positive_blocks}


def check_g4_walkforward(net_bps: np.ndarray, entry_bar_idx: np.ndarray, n_total_bars: int,
                          n_windows: int = 10) -> dict:
    edges = np.linspace(0, n_total_bars, n_windows + 1).astype(int)
    window_results = []
    for w in range(n_windows):
        lo, hi = edges[w], edges[w + 1]
        wmask = (entry_bar_idx >= lo) & (entry_bar_idx < hi)
        n = int(wmask.sum())
        exp = float(net_bps[wmask].mean()) if n >= 5 else np.nan
        pnl = float(net_bps[wmask].sum()) if n >= 5 else 0.0
        window_results.append({"jendela": w + 1, "n_trades": n, "expectancy_bps": exp, "pnl_total_bps": pnl})
    wf_df = pd.DataFrame(window_results)
    n_positive = int((wf_df["expectancy_bps"] > 0).sum())
    total_pnl = wf_df["pnl_total_bps"].sum()
    top2 = wf_df["pnl_total_bps"].abs().nlargest(2).sum()
    top2_share = (wf_df.loc[wf_df["pnl_total_bps"].abs().nlargest(2).index, "pnl_total_bps"].sum() / total_pnl
                  if total_pnl != 0 else np.nan)
    passed = (n_positive >= 7) and pd.notna(top2_share) and (abs(top2_share) <= 0.60)
    return {"pass": bool(passed), "n_positive": n_positive, "top2_share": float(top2_share) if pd.notna(top2_share) else None,
            "windows": window_results}


def run_all_gates(direction: np.ndarray, net_bps: np.ndarray, net_bps_demeaned: np.ndarray,
                   entry_bar_time: np.ndarray, entry_bar_idx: np.ndarray, n_total_bars: int,
                   regime_bounds: list) -> dict:
    g1 = check_g1_symmetry(direction, net_bps)
    if not g1["pass"]:
        return {"g1": g1, "g2": None, "g3": None, "g4": None, "overall_pass": False, "stopped_at": "G1"}
    g2 = check_g2_demeaned(direction, net_bps_demeaned)
    if not g2["pass"]:
        return {"g1": g1, "g2": g2, "g3": None, "g4": None, "overall_pass": False, "stopped_at": "G2"}
    g3 = check_g3_regime(direction, net_bps, entry_bar_time, regime_bounds)
    if not g3["pass"]:
        return {"g1": g1, "g2": g2, "g3": g3, "g4": None, "overall_pass": False, "stopped_at": "G3"}
    g4 = check_g4_walkforward(net_bps, entry_bar_idx, n_total_bars)
    return {"g1": g1, "g2": g2, "g3": g3, "g4": g4, "overall_pass": g4["pass"],
            "stopped_at": None if g4["pass"] else "G4"}
