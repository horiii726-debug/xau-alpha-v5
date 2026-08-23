"""L11 -- uji daya gerbang (06_VALIDASI_STATISTIK.md MC6_transmitansi_gerbang,
02_HUKUM.md L11). Suntikkan sinyal sintetis ber-IC terkontrol ke data harga
NYATA, jalankan lewat corong 3-tingkat v6 (07_GERBANG_CORONG.md §B3), ukur
proporsi lolos per tahap.

Simplifikasi yang DIDOKUMENTASIKAN secara eksplisit (bukan disembunyikan):
- "Trade" = blok non-overlapping H240 (16 bar M15) -- uniqueness=1 per trade
  by construction, jadi effective_n = n_trades (tidak butuh mesin konkurensi
  Lopez de Prado penuh untuk sinyal sintetis blok-non-tumpang-tindih ini).
- Tier-2 "gangguan parameter" diimplementasikan sebagai gangguan ASUMSI BIAYA
  (+/-20% pada skenario alpha/beta), bukan gangguan hyperparameter formula --
  karena sinyal sintetis L11 tidak punya hyperparameter formula (dia dibangun
  langsung dari IC target, bukan dari lookback/threshold).
- n_seeds default 150 (bukan 500 di spec) untuk kecepatan -- didokumentasikan,
  bukan disembunyikan. Transmitansi pada n=150 punya margin error binomial
  ~+/-8% pada p=0.5 (95% CI) -- cukup untuk vonis GM-3 (jauh dari ambang 50%
  atau jauh di bawahnya, yang menentukan keputusan).
"""
import numpy as np

from src.validation.montecarlo import mc2_survival_paths, deflated_sharpe_ratio


def make_h240_blocks(mid: np.ndarray, block_bars: int = 16):
    """Non-overlapping M15 blocks -> H240 (16*15min=240min) trade returns."""
    n_blocks = len(mid) // block_bars
    mid = mid[: n_blocks * block_bars + 1] if len(mid) > n_blocks * block_bars else mid
    idx = np.arange(0, n_blocks * block_bars, block_bars)
    idx = idx[idx + block_bars < len(mid)]
    r_block = np.log(mid[idx + block_bars] / mid[idx])
    return r_block  # one return per non-overlapping H240 block


def synthetic_signal(r_block: np.ndarray, ic_target: float, rng: np.random.Generator) -> np.ndarray:
    """signal_i = IC*z_futuro_i + sqrt(1-IC^2)*noise_i, per §L11."""
    z_future = (r_block - r_block.mean()) / (r_block.std() + 1e-12)
    noise = rng.normal(size=len(r_block))
    return ic_target * z_future + np.sqrt(max(0.0, 1 - ic_target**2)) * noise


def trial(r_block: np.ndarray, ic_target: float, seed: int, cost_bps_worst: float,
          br_eff_per_year_full: float, mc2_rules: dict, target_trades_per_year: float = 220.0) -> dict:
    rng = np.random.default_rng(seed)
    signal = synthetic_signal(r_block, ic_target, rng)

    # Threshold entry pada |signal| supaya frekuensi trade realistis (~220/thn,
    # acuan H240 di spec), BUKAN trading di setiap blok. Trading setiap blok
    # (1800+/thn) membuat biaya mendominasi murni karena frekuensi -- bukan
    # temuan tentang gerbangnya. n_blocks_per_year dari data NYATA.
    n_blocks_per_year = br_eff_per_year_full  # uniqueness=1, semua blok dihitung sebelum threshold
    trade_rate = min(1.0, target_trades_per_year / max(n_blocks_per_year, 1.0))
    threshold = np.quantile(np.abs(signal), 1 - trade_rate)
    take = np.abs(signal) >= threshold
    position = np.where(take, np.sign(signal), 0.0)

    gross = position * r_block
    net = (gross - cost_bps_worst / 1e4)[take]  # hanya baris yang benar-benar trade
    n = len(net)
    br_eff_actual_per_year = br_eff_per_year_full * n / max(len(r_block), 1)
    if n < 20:
        return {"tier1": False, "tier2": False, "tier3": False, "t_stat": 0.0, "sharpe": 0.0, "n": n}

    # ---- basic stats (uniqueness=1: non-overlapping blocks) ----
    mean_net = net.mean()
    se = net.std(ddof=1) / np.sqrt(n)
    t_stat = mean_net / se if se > 0 else 0.0
    sharpe = mean_net / (net.std(ddof=1) + 1e-12)

    # ---- tier 1: SARINGAN ----
    # B02/B05 dicocokkan PERSIS ke timing & jumlah trade kandidat (r_block[take]),
    # bukan seluruh seri -- supaya perbandingan adil (arah acak, timing SAMA).
    r_traded = r_block[take]
    f_expect = mean_net > 0
    f_t15 = t_stat >= 1.5
    b02_entries = rng.integers(0, len(r_block), size=n)  # entry acak, jumlah & biaya dicocokkan
    b02_returns = r_block[b02_entries] - cost_bps_worst / 1e4
    f_b02 = net.sum() > b02_returns.sum()
    b05_sign = rng.choice([-1.0, 1.0], size=n)
    b05_returns = b05_sign * r_traded - cost_bps_worst / 1e4
    f_b05 = net.sum() > b05_returns.sum()
    f_br = br_eff_actual_per_year >= 100.0  # uniqueness=1 for H240 blocks -> BR_eff = trades/year directly
    tier1_checks = [f_expect, f_t15, f_b02, f_b05, f_br]
    tier1_pass = all(tier1_checks)

    if not tier1_pass:
        return {"tier1": False, "tier2": False, "tier3": False, "t_stat": t_stat, "sharpe": sharpe, "n": n}

    # ---- tier 2: ROBUSTNESS ----
    # F_MC5 (di sini: gangguan ASUMSI BIAYA +/-20%, bukan hyperparameter formula)
    signs_cost = [np.sign((gross - cost_bps_worst * m / 1e4).mean()) for m in (0.8, 0.9, 1.1, 1.2)]
    f_mc5 = len(set(signs_cost)) == 1 and signs_cost[0] == np.sign(mean_net)

    seed_signs = [np.sign(rng.choice(net, size=n, replace=True).mean()) for _ in range(10)]
    f_seed = len(set(seed_signs)) == 1

    order = np.arange(n)
    windows = np.array_split(net[order], min(8, max(2, n // 15)))
    dom_sign = np.sign(mean_net)
    wf_signs = [np.sign(w.mean()) for w in windows if len(w) > 0]
    f_wf = np.mean([s == dom_sign for s in wf_signs]) >= 0.80 if wf_signs else False

    last_third = net[-max(10, n // 3):]
    lt_se = last_third.std(ddof=1) / np.sqrt(len(last_third)) if len(last_third) > 1 else 0.0
    lt_t = last_third.mean() / lt_se if lt_se > 0 else 0.0
    f_third = len(last_third) >= 10 and abs(lt_t) > 1.96 and np.sign(last_third.mean()) == dom_sign

    k = 8
    folds = np.array_split(net, k)
    f_cpcv = np.mean([f.mean() > 0 for f in folds if len(f) > 0]) >= 0.80

    mc2 = mc2_survival_paths(net + cost_bps_worst / 1e4, n_paths=2000, **mc2_rules, horizons=(250,))
    f_mc2 = mc2.get("gate_pass_250", False)

    tier2_checks = [f_mc5, f_seed, f_wf, f_third, f_cpcv, f_mc2]
    tier2_pass = all(tier2_checks)

    return {"tier1": True, "tier2": tier2_pass, "t_stat": t_stat, "sharpe": sharpe, "n": n,
            "mean_net": mean_net, "checks_t1": tier1_checks, "checks_t2": tier2_checks}


def run_l11(r_block: np.ndarray, ic_grid, n_seeds: int, cost_bps_worst: float,
            br_eff_per_year_full: float, mc2_rules: dict, seed0: int = 10000) -> dict:
    out = {}
    for ic in ic_grid:
        trials = [trial(r_block, ic, seed0 + s, cost_bps_worst, br_eff_per_year_full, mc2_rules)
                  for s in range(n_seeds)]
        n_t1 = sum(t["tier1"] for t in trials)
        n_t2 = sum(t.get("tier2", False) for t in trials)

        # tier 3 CONFIRM: t>=3.0 AND tier2 passed AND batch-level DSR>=0.95
        sharpes = np.array([t["sharpe"] for t in trials if t["tier1"]])
        sharpe_std = float(sharpes.std(ddof=1)) if len(sharpes) > 1 else 0.30
        n_t3 = 0
        for t in trials:
            if not t.get("tier2", False):
                continue
            if t["t_stat"] < 3.0:
                continue
            dsr = deflated_sharpe_ratio(t["sharpe"], n_seeds, sharpe_std, 0.0, 3.0, t["n"])
            if dsr >= 0.95:
                n_t3 += 1

        out[ic] = {
            "n_seeds": n_seeds,
            "transmit_tier1_pct": 100 * n_t1 / n_seeds,
            "transmit_tier2_pct": 100 * n_t2 / n_seeds,
            "transmit_chain_pct": 100 * n_t3 / n_seeds,
            "sharpe_std_empirical": sharpe_std,
            "n_pass_tier1": n_t1, "n_pass_tier2": n_t2, "n_pass_tier3": n_t3,
        }
    return out
