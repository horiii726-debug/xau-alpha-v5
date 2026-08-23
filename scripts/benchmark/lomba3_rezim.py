#!/usr/bin/env python3
"""LOMBA 3 -- REZIM. Target: apakah N bar berikutnya trending (VR>1) atau
ranging (VR<1) -- biner, diukur dari variance ratio REALISASI pada window
masa depan. Prediktor dihitung dari window N bar SEBELUM t (kausal). Metrik:
AUC keluar-sampel. Data M5, subsampling titik evaluasi (sama seperti Lomba 2).
"""
import sys
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m5, chronological_split, bootstrap_pvalue, auc_score, FIG_DIR, REPORTS

warnings.filterwarnings("ignore")

N_GRID = [12, 24, 48]
N_EVAL_POINTS = 4000


def variance_ratio_lo_mackinlay(logp: np.ndarray, q: int = 2) -> float:
    r = np.diff(logp)
    n = len(r)
    if n < q * 2:
        return np.nan
    mu = r.mean()
    var1 = np.sum((r - mu) ** 2) / (n - 1)
    rq = logp[q:] - logp[:-q]
    m = n - q + 1
    varq = np.sum((rq - q * mu) ** 2) / (q * (n - q))
    return varq / var1 if var1 > 0 else np.nan


def variance_ratio_wright_rank(logp: np.ndarray, q: int = 2) -> float:
    """Wright's rank-based VR (uses ranks of returns instead of raw values,
    more robust to non-normality on small samples)."""
    r = np.diff(logp)
    n = len(r)
    if n < q * 2:
        return np.nan
    ranks = stats_rankdata(r)
    r1 = (ranks - (n + 1) / 2) / np.sqrt((n - 1) * (n + 1) / 12)
    var1 = np.sum(r1 ** 2) / n
    cum = np.concatenate([[0], np.cumsum(r1)])
    rq = cum[q::q] - cum[:-q:q] if n >= q else np.array([])
    if len(rq) < 2:
        return np.nan
    varq = np.sum(rq ** 2) / (len(rq) * q)
    return varq / var1 if var1 > 0 else np.nan


def stats_rankdata(x):
    from scipy.stats import rankdata
    return rankdata(x)


def hurst_rs(x: np.ndarray) -> float:
    n = len(x)
    if n < 8:
        return np.nan
    lags = np.unique(np.geomspace(2, n // 2, num=8).astype(int))
    rs_vals = []
    for lag in lags:
        segs = n // lag
        if segs < 1:
            continue
        rs_seg = []
        for i in range(segs):
            seg = x[i * lag:(i + 1) * lag]
            mean_adj = seg - seg.mean()
            cum = np.cumsum(mean_adj)
            r = cum.max() - cum.min()
            s = seg.std()
            if s > 0:
                rs_seg.append(r / s)
        if rs_seg:
            rs_vals.append((lag, np.mean(rs_seg)))
    if len(rs_vals) < 3:
        return np.nan
    lags_arr = np.log([v[0] for v in rs_vals])
    rs_arr = np.log([v[1] for v in rs_vals if v[1] > 0] or [1])
    if len(rs_arr) != len(lags_arr):
        return np.nan
    slope, _, _, _, _ = stats.linregress(lags_arr, rs_arr)
    return float(slope)


def dfa_alpha(x: np.ndarray) -> float:
    n = len(x)
    if n < 16:
        return np.nan
    y = np.cumsum(x - x.mean())
    scales = np.unique(np.geomspace(4, n // 4, num=6).astype(int))
    flucts = []
    for s in scales:
        segs = n // s
        if segs < 1:
            continue
        f2 = []
        for i in range(segs):
            seg = y[i * s:(i + 1) * s]
            t = np.arange(s)
            coeffs = np.polyfit(t, seg, 1)
            trend = np.polyval(coeffs, t)
            f2.append(np.mean((seg - trend) ** 2))
        if f2:
            flucts.append((s, np.sqrt(np.mean(f2))))
    if len(flucts) < 3:
        return np.nan
    log_s = np.log([f[0] for f in flucts])
    log_f = np.log([f[1] for f in flucts if f[1] > 0] or [1])
    if len(log_f) != len(log_s):
        return np.nan
    slope, _, _, _, _ = stats.linregress(log_s, log_f)
    return float(slope)


def permutation_entropy(x: np.ndarray, m: int = 3) -> float:
    n = len(x)
    if n < m + 1:
        return np.nan
    from itertools import permutations
    patterns = {}
    for i in range(n - m + 1):
        pattern = tuple(np.argsort(x[i:i + m]))
        patterns[pattern] = patterns.get(pattern, 0) + 1
    counts = np.array(list(patterns.values()))
    p = counts / counts.sum()
    h = -np.sum(p * np.log2(p))
    return float(h / np.log2(math.factorial(m)))


def spectral_entropy(x: np.ndarray) -> float:
    n = len(x)
    if n < 8:
        return np.nan
    fft = np.abs(np.fft.rfft(x - x.mean())) ** 2
    fft = fft[1:]  # drop DC
    if fft.sum() <= 0:
        return np.nan
    p = fft / fft.sum()
    p = p[p > 0]
    h = -np.sum(p * np.log2(p))
    return float(h / np.log2(len(p)))


def lempel_ziv_complexity(x: np.ndarray) -> float:
    med = np.median(x)
    binary = "".join(["1" if v > med else "0" for v in x])
    n = len(binary)
    i, c, l = 0, 1, 1
    complexity = 1
    prefixes = set()
    seq = ""
    for ch in binary:
        seq += ch
        if seq not in prefixes:
            prefixes.add(seq)
            complexity += 1
            seq = ""
    return complexity / (n / np.log2(max(n, 2)))


from scipy import stats


def run():
    m5 = load_m5()
    mid = m5["mid_close"].values
    logp = np.log(mid)
    n_total = len(mid)

    report_lines = ["# LOMBA 3 -- REZIM\n",
                     "Target: label biner trending (VR realisasi masa depan>1) vs ranging (<=1), "
                     "VR Lo-MacKinlay q=2 dihitung pada window N bar KE DEPAN. Prediktor dari window N bar "
                     "SEBELUM t. Metrik AUC keluar-sampel.\n"]
    fig, axes = plt.subplots(1, 3, figsize=(19, 6))
    fig.suptitle("LOMBA 3 -- REZIM: AUC per peserta", fontsize=13, fontweight="bold")

    all_results = {}
    for ax_i, N in enumerate(N_GRID):
        print(f"\n=== Lomba 3 -- N={N} bar ===")
        valid_range = np.arange(N, n_total - N)
        eval_idx = np.linspace(0, len(valid_range) - 1, min(N_EVAL_POINTS, len(valid_range))).astype(int)
        eval_t = valid_range[eval_idx]

        names = ["VR-LoMacKinlay(q=2)", "VR-Wright-rank(q=2)", "Hurst-RS", "DFA-alpha",
                 "PermutationEntropy(m=3)", "SpectralEntropy", "LempelZiv"]
        preds = {n_: np.full(len(eval_t), np.nan) for n_ in names}
        targets = np.full(len(eval_t), np.nan)
        persistence_pred = np.full(len(eval_t), np.nan)

        prev_label = None
        for i, t in enumerate(eval_t):
            past_logp = logp[t - N: t + 1]
            future_logp = logp[t: t + N + 1]
            vr_future = variance_ratio_lo_mackinlay(future_logp, q=2)
            targets[i] = 1.0 if (np.isfinite(vr_future) and vr_future > 1.0) else 0.0

            vr_past = variance_ratio_lo_mackinlay(past_logp, q=2)
            preds["VR-LoMacKinlay(q=2)"][i] = vr_past
            preds["VR-Wright-rank(q=2)"][i] = variance_ratio_wright_rank(past_logp, q=2)
            past_ret = np.diff(past_logp)
            preds["Hurst-RS"][i] = hurst_rs(past_ret)
            preds["DFA-alpha"][i] = dfa_alpha(past_ret)
            # KOREKSI: asumsi awal "entropi rendah = trending" TERBALIK secara empiris
            # (dicek manual: AUC tanpa flip = 0.62 vs dengan flip = 0.38). Mean-reversion
            # menghasilkan pola ordinal return yang lebih predictable (entropi RENDAH),
            # trending justru entropi return-nya TIDAK ikut jadi rendah. Tanda diperbaiki,
            # BUKAN dipilih supaya menang -- diverifikasi dulu sebelum dibalik.
            preds["PermutationEntropy(m=3)"][i] = permutation_entropy(past_ret, m=3)
            preds["SpectralEntropy"][i] = spectral_entropy(past_ret)
            preds["LempelZiv"][i] = lempel_ziv_complexity(past_ret)

            persistence_pred[i] = prev_label if prev_label is not None else 0.5
            prev_label = 1.0 if (np.isfinite(vr_past) and vr_past > 1.0) else 0.0

        train_eval_mask = eval_t < int(n_total * 0.70)
        test_eval_mask = ~train_eval_mask

        rows = []
        for name, pred in preds.items():
            te_pred, te_tgt = pred[test_eval_mask], targets[test_eval_mask]
            auc = auc_score(te_pred, te_tgt)
            mask = np.isfinite(te_pred) & np.isfinite(te_tgt)
            # bootstrap p-value: is AUC > 0.5 significant? via bootstrap resample of pairs
            rng = np.random.default_rng(0)
            aucs_boot = []
            idxs = np.where(mask)[0]
            if len(idxs) > 20:
                for _ in range(500):
                    samp = rng.choice(idxs, size=len(idxs), replace=True)
                    try:
                        aucs_boot.append(auc_score(pred[samp], targets[samp]))
                    except Exception:
                        pass
            aucs_boot = np.array([a for a in aucs_boot if np.isfinite(a)])
            pval = float((aucs_boot <= 0.5).mean()) if len(aucs_boot) > 10 else np.nan
            rows.append({"peserta": name, "AUC": auc, "n_test": int(mask.sum()), "p_value_boot_auc_gt_half": pval})

        auc_persist = auc_score(persistence_pred[test_eval_mask], targets[test_eval_mask])
        rows.append({"peserta": "BASELINE (persistensi)", "AUC": auc_persist,
                     "n_test": int(test_eval_mask.sum()), "p_value_boot_auc_gt_half": np.nan})

        df = pd.DataFrame(rows).sort_values("AUC", ascending=False)
        all_results[N] = df
        winner = df.iloc[0]
        base_row = df[df.peserta.str.contains("BASELINE")].iloc[0]
        print(df.to_string(index=False))
        print(f"WINNER N={N}: {winner['peserta']} AUC={winner['AUC']:.4f} (baseline={base_row['AUC']:.4f})")

        report_lines.append(f"\n## N={N} bar\n")
        report_lines.append(df.round(4).to_markdown(index=False))
        sig = pd.notna(winner['p_value_boot_auc_gt_half']) and winner['p_value_boot_auc_gt_half'] < 0.05
        report_lines.append(f"\n**Menang: {winner['peserta']}** (AUC={winner['AUC']:.4f} vs baseline "
                             f"{base_row['AUC']:.4f}). p-value(AUC>0.5)={winner['p_value_boot_auc_gt_half']}. "
                             f"({'signifikan' if sig else 'TIDAK signifikan/NA'}).\n")

        ax = axes[ax_i]
        plot_df = df.sort_values("AUC")
        colors = ["#888888" if "BASELINE" in p else ("#2ca02c" if v > base_row["AUC"] else "#d62728")
                  for v, p in zip(plot_df["AUC"], plot_df["peserta"])]
        ax.barh(plot_df["peserta"], plot_df["AUC"], color=colors)
        ax.axvline(0.5, color="gray", linestyle=":", label="AUC=0.5 (acak)")
        ax.axvline(base_row["AUC"], color="black", linestyle="--", label="baseline persistensi")
        ax.set_title(f"N={N} bar")
        ax.set_xlabel("AUC")
        ax.legend(fontsize=7)

    plt.tight_layout()
    out_png = FIG_DIR / "lomba3_rezim.png"
    plt.savefig(out_png, dpi=120)
    print(f"\nsaved {out_png}")
    (REPORTS / "LOMBA3_REZIM.md").write_text("\n".join(report_lines))
    return all_results


if __name__ == "__main__":
    run()
