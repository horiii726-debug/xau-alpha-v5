#!/usr/bin/env python3
"""L15 -- MAC05 (COT crowding) + MAC07 (Ridge realyield+DXY) diuji ULANG di
horizon MINGGUAN (5 hari, bukan D1). Alasan (M5 sudah terbukti MATI di
UJI_BUNUH_M5): COT dirilis mingguan; sigma naik ~sqrt(5)=2.236x sedangkan
biaya round-turn TETAP sama nilainya (dibayar sekali per trade, bukan per
hari) -> kappa turun ~2.236x -> expectancy -12..-14bps di D1 (L13) berpotensi
positif di W1 TANPA mengubah sinyalnya sama sekali.

Gerbang G1-G5 PERSIS SAMA seperti L13/L11 -- tidak dilonggarkan. Sinyal
dipakai APA ADANYA dari l13_lomba_makro.py, hanya target/horizon forward
return yang berubah dari 1 hari ke 5 hari.
"""
import sys
import warnings

import numpy as np
import pandas as pd

sys.path.insert(0, "/workspace/xau-alpha-v5")
sys.path.insert(0, "/workspace/xau-alpha-v5/scripts/benchmark")
from common import load_m1, measure_cost_bps, REPORTS, FIG_DIR
from src.stats.effective_n import effective_n as ldp_effective_n
from l13_lomba_makro import load_xau_d1, load_macro, build_macro_features, build_signals
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

LATIH_FRAC = 0.60
UJI_FRAC = 0.25
TAU_GRID = [1.0, 1.5]
HOLD_DAYS = 5  # 1 minggu perdagangan
TARGET_SIGNALS = ["MAC05_cot_crowding", "MAC07_ridge_combo"]


def main():
    d1 = load_xau_d1()
    fred, cot = load_macro()
    df = build_macro_features(d1, fred, cot)
    n_total = len(df)
    latih_end = int(n_total * LATIH_FRAC)
    uji_end = int(n_total * (LATIH_FRAC + UJI_FRAC))
    print(f"D1 total={n_total:,} hari ({df['date'].iloc[0].date()} s/d {df['date'].iloc[uji_end-1].date()}), "
          f"LATIH+UJI={uji_end:,}. HOLDOUT (15% terakhir) tidak disentuh. Horizon uji: {HOLD_DAYS} hari (mingguan).")

    m1 = load_m1()
    m1_mask = np.zeros(len(m1), dtype=bool); m1_mask[: int(len(m1) * 0.70)] = True
    cost_info = measure_cost_bps(m1, m1_mask)
    cost_base = cost_info["round_trip_cost_bps"]
    spread_p90 = m1.loc[m1_mask, "spread_bps"].dropna().pipe(lambda s: s[(s > 0) & (s < 500)]).quantile(0.90)
    cost_worst = spread_p90 * 2.5 + 0.28
    print(f"Biaya base={cost_base:.3f}bps, biaya worst={cost_worst:.3f}bps (SAMA seperti L13 -- "
          f"biaya round-turn dibayar sekali per trade, tidak berskala dengan horizon)")

    signals = build_signals(df, latih_end)
    logp = np.log(df["mid_close"].values)
    day_ret = pd.Series(np.diff(logp, prepend=logp[0]))
    roll_mean_60d = day_ret.rolling(60, min_periods=15).mean()
    demeaned_logp = np.cumsum((day_ret - roll_mean_60d.fillna(0)).values)

    H = HOLD_DAYS
    fwd_bps = (np.roll(logp, -H) - logp) * 1e4; fwd_bps[-H:] = np.nan
    fwd_bps_demeaned = (np.roll(demeaned_logp, -H) - demeaned_logp) * 1e4; fwd_bps_demeaned[-H:] = np.nan

    sigma_1d_bps = float(np.std(day_ret.values[1:latih_end])) * 1e4
    sigma_w_bps = sigma_1d_bps * np.sqrt(H)
    kappa_d1 = cost_base / sigma_1d_bps
    kappa_w1 = cost_base / sigma_w_bps
    print(f"sigma_1d={sigma_1d_bps:.3f}bps, sigma_{H}d={sigma_w_bps:.3f}bps "
          f"(naik {sigma_w_bps/sigma_1d_bps:.3f}x). kappa D1={kappa_d1:.4f} -> kappa W1={kappa_w1:.4f} "
          f"(turun {kappa_d1/kappa_w1:.3f}x)")

    bar_time = df["date"].values
    regime_bounds = [
        ("2003-2011 bull", np.datetime64("2003-01-01"), np.datetime64("2012-01-01")),
        ("2012-2015 BEAR", np.datetime64("2012-01-01"), np.datetime64("2016-01-01")),
        ("2016-cutoff", np.datetime64("2016-01-01"), pd.Timestamp(df["date"].iloc[uji_end-1]).to_datetime64()),
    ]
    latih_uji_mask = np.zeros(n_total, dtype=bool); latih_uji_mask[:uji_end] = True

    def check_g1(direction, net_d):
        l, s = direction > 0, direction < 0
        pl = net_d[l].sum() if l.any() else np.nan
        ps = net_d[s].sum() if s.any() else np.nan
        return (pl > 0) and (ps > 0), pl, ps

    def check_g3(direction, net, entry_bt):
        res = []
        for name, s0, s1 in regime_bounds:
            m = (entry_bt >= s0) & (entry_bt < s1)
            n = int(m.sum())
            exp = float(net[m].mean()) if n >= 10 else np.nan
            res.append((name, n, exp))
        npos = sum(1 for _, n, e in res if pd.notna(e) and e > 0)
        return npos >= 2, res

    def check_g4(net, entry_idx, n_windows=10):
        edges = np.linspace(0, uji_end, n_windows + 1).astype(int)
        wf = []
        for w in range(n_windows):
            lo, hi = edges[w], edges[w+1]
            m = (entry_idx >= lo) & (entry_idx < hi)
            n = int(m.sum())
            exp = float(net[m].mean()) if n >= 5 else np.nan
            pnl = float(net[m].sum()) if n >= 5 else 0.0
            wf.append((w+1, n, exp, pnl))
        npos = sum(1 for _, n, e, p in wf if pd.notna(e) and e > 0)
        total_pnl = sum(p for _, n, e, p in wf)
        top2 = sorted(wf, key=lambda x: -abs(x[3]))[:2]
        top2_share = sum(x[3] for x in top2) / total_pnl if total_pnl != 0 else np.nan
        passed = npos >= 7 and pd.notna(top2_share) and abs(top2_share) <= 0.60
        return passed, npos, top2_share, wf

    rows = []
    survivors = []
    for tau in TAU_GRID:
        for name in TARGET_SIGNALS:
            z = signals[name].values
            take = (np.abs(z) >= tau) & latih_uji_mask & np.isfinite(fwd_bps) & np.isfinite(z)
            n = int(take.sum())
            if n < 30:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "n<30"})
                continue
            direction = np.sign(z)[take]
            net_base = direction * fwd_bps[take] - cost_base
            net_demeaned = direction * fwd_bps_demeaned[take] - cost_base
            net_worst = direction * fwd_bps[take] - cost_worst
            entry_idx = np.where(take)[0]
            entry_bt = bar_time[take]

            g1, pl, ps = check_g1(direction, net_demeaned)
            if not g1:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G1",
                              "pnl_long_demean": pl, "pnl_short_demean": ps})
                continue
            g2 = float(net_worst.mean()) > 0
            if not g2:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G2",
                              "expectancy_worst": float(net_worst.mean())})
                continue
            g3, g3_detail = check_g3(direction, net_base, entry_bt)
            if not g3:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G3", "g3_detail": g3_detail})
                continue
            g4, g4_npos, g4_top2, g4_detail = check_g4(net_base, entry_idx)
            if not g4:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G4",
                              "wf_positive": g4_npos, "wf_top2_share": g4_top2})
                continue
            starts = entry_idx; ends = np.minimum(entry_idx + H, n_total)
            eff_n = ldp_effective_n(starts, ends, n_total)
            se = net_base.std(ddof=1) / np.sqrt(max(eff_n, 2))
            t_stat = net_base.mean() / se if se > 0 else 0.0
            g5 = t_stat >= 3.0
            if not g5:
                rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "G5",
                              "eff_n": eff_n, "t_stat": t_stat})
                continue
            rows.append({"peserta": name, "tau": tau, "n": n, "stopped_at": "LOLOS",
                          "expectancy_base_bps": float(net_base.mean()), "eff_n": eff_n, "t_stat": t_stat})
            survivors.append({"peserta": name, "tau": tau, "n": n,
                               "expectancy_base_bps": float(net_base.mean()), "t_stat_effn": t_stat})
            print(f"tau={tau} {name}: LOLOS SEMUA G1-G5! t={t_stat:.2f} exp={net_base.mean():.3f}bps")

    for r in rows:
        extra = ""
        if r["stopped_at"] == "G1":
            extra = f" (pnl_long={r['pnl_long_demean']:.2f}, pnl_short={r['pnl_short_demean']:.2f})"
        elif r["stopped_at"] == "G2":
            extra = f" (expectancy_worst={r['expectancy_worst']:.3f}bps)"
        print(f"tau={r['tau']} {r['peserta']}: n={r['n']}, stopped_at={r['stopped_at']}{extra}")

    stop_counts = {}
    for r in rows:
        stop_counts[r["stopped_at"]] = stop_counts.get(r["stopped_at"], 0) + 1
    print(f"\nDistribusi gerbang gugur: {stop_counts}")
    print(f"\nTOTAL SURVIVOR: {len(survivors)}/{len(rows)}")

    lines = [f"# L15 -- MAC05 & MAC07 di horizon MINGGUAN ({H} hari), gerbang G1-G5 SAMA PERSIS seperti L13\n",
              f"Alasan: M5 terbukti MATI (UJI_BUNUH_M5 -- winrate aktual < breakeven di semua hold & "
              f"semua peserta termasuk MAC05/MAC07). COT dirilis mingguan; menguji sinyal ini di horizon "
              f"sesuai frekuensi rilisnya sendiri, bukan mengubah sinyal atau melonggarkan gerbang.\n",
              f"\nD1={n_total:,} hari ({df['date'].iloc[0].date()} s/d {df['date'].iloc[uji_end-1].date()}), "
              f"LATIH+UJI dipakai={uji_end:,}. Biaya base={cost_base:.3f}bps, worst={cost_worst:.3f}bps "
              f"(TETAP -- dibayar sekali per trade).\n",
              f"\nsigma harian={sigma_1d_bps:.3f}bps -> sigma {H}-hari={sigma_w_bps:.3f}bps "
              f"(naik {sigma_w_bps/sigma_1d_bps:.3f}x). kappa D1={kappa_d1:.4f} -> kappa W1={kappa_w1:.4f} "
              f"(turun {kappa_d1/kappa_w1:.3f}x).\n",
              f"\n## Hasil per kombinasi (tau x peserta)\n"]
    rdf = pd.DataFrame(rows)
    lines.append(rdf.to_markdown(index=False))
    lines.append(f"\n## Distribusi gerbang gugur\n\n" + "\n".join(f"- {k}: {v}" for k, v in sorted(stop_counts.items(), key=lambda x: -x[1])))
    if survivors:
        lines.append(f"\n## SURVIVOR ({len(survivors)})\n\n" + pd.DataFrame(survivors).round(4).to_markdown(index=False))
        lines.append(f"\n## L14 -- syarat >=1 lolos G1-G5 TERPENUHI\n\nLanjut ke Bagian B-E "
                      f"(SISTEM_TRADING_V7.md) dengan sinyal ini SAJA di horizon mingguan, memakai ulang "
                      f"(tanpa uji ulang) HAR-RV untuk barrier/sizing, deteksi rezim untuk router, "
                      f"EmpiricalQuantile p90 untuk SL/TP -- sesuai instruksi eksplisit.\n")
    else:
        lines.append("\n## NOL SURVIVOR\n\nSyarat L14 (>=1 lolos G1-G5) TIDAK terpenuhi. Bagian B-E tidak dikerjakan.\n")
    (REPORTS / "L15_LOMBA_MAKRO_MINGGUAN.md").write_text("\n".join(lines))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
    ax = axes[0]
    labels = list(stop_counts.keys()); values = [stop_counts[k] for k in labels]
    colors = ["#2ca02c" if k == "LOLOS" else "#d62728" for k in labels]
    ax.bar(labels, values, color=colors)
    ax.set_title(f"L15 (W1, {H}hari): {len(survivors)}/{len(rows)} lolos G1-G5")
    ax.set_ylabel("jumlah kombinasi")

    ax = axes[1]
    ax.bar(["kappa D1 (L13)", f"kappa W1 ({H}hari)"], [kappa_d1, kappa_w1], color=["#d62728", "#4a6fa5"])
    ax.axhline(0.15, color="black", linestyle="--", linewidth=0.8, label="ambang kappa<=0.15")
    ax.set_ylabel("kappa = biaya/sigma")
    ax.set_title("Kappa turun di horizon mingguan")
    ax.legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(FIG_DIR / "l15_lomba_makro_mingguan.png", dpi=120)
    print(f"saved {FIG_DIR / 'l15_lomba_makro_mingguan.png'}")

    return survivors


if __name__ == "__main__":
    s = main()
    sys.exit(0 if s else 1)
