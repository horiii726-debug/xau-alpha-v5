"""Null benchmarks B01-B09, as executable code -- per 05_VALIDASI_STATISTIK.md:
"Null benchmark harus berupa KODE, bukan aturan di dokumen." B09 (perfect
foresight) is reference-only (capture_ratio denominator), never part of
must_beat_all.

Each null returns a per-bar return series (same length convention as the
candidate being tested: index-aligned to bar closes) representing that
null strategy's return stream, so a candidate's return series can be
compared against it (t-test / bootstrap / permutation, done elsewhere).

All nulls are causal: no null here uses information from bar t to decide
its own position at bar t (positions decided at t are applied to the
return realized over (t, t+1], consistent with L9 -- execution at the
next bar's open).
"""
import numpy as np


def _to_returns(mid: np.ndarray) -> np.ndarray:
    r = np.diff(np.log(mid))
    return r


def b01_buy_and_hold(mid: np.ndarray) -> np.ndarray:
    """Always long, full period."""
    return _to_returns(mid)


def b02_random_matched(mid: np.ndarray, costs_bps: np.ndarray, holding_bars: int, n_trades: int, rng: np.random.Generator) -> np.ndarray:
    """RANDOM_MATCHED -- entry acak, holding-time & biaya dicocokkan dengan
    kandidat. PALING PENTING (§null_benchmarks.daftar.B02.catatan).
    costs_bps: round-trip cost in bps, applied once per trade at entry."""
    r = _to_returns(mid)
    n_bars = len(r)
    if n_bars <= holding_bars:
        return np.array([])
    entries = rng.integers(0, n_bars - holding_bars, size=n_trades)
    trade_returns = []
    for e in entries:
        seg = r[e : e + holding_bars]
        gross = seg.sum()
        cost = float(np.mean(costs_bps)) / 1e4 if len(costs_bps) else 0.0
        trade_returns.append(gross - cost)
    return np.array(trade_returns)


def b03_block_permuted(mid: np.ndarray, block_size: int, rng: np.random.Generator) -> np.ndarray:
    """BLOCK_PERMUTED -- shuffle contiguous blocks of returns, preserving
    within-block autocorrelation (unlike naive iid permutation)."""
    r = _to_returns(mid)
    n = len(r)
    n_blocks = max(1, n // block_size)
    blocks = [r[i * block_size : (i + 1) * block_size] for i in range(n_blocks)]
    order = rng.permutation(n_blocks)
    return np.concatenate([blocks[i] for i in order])


def b04_tsmom_12m(mid: np.ndarray, lookback_bars: int) -> np.ndarray:
    """Time-series momentum: long if trailing lookback_bars return > 0, short
    if < 0 (12-month TSMOM, generalized to whatever bar frequency is passed)."""
    r = _to_returns(mid)
    n = len(r)
    sig = np.zeros(n)
    for t in range(lookback_bars, n):
        trail = mid[t] / mid[t - lookback_bars] - 1
        sig[t] = np.sign(trail)
    # signal at t acts on return r[t] (already the (t,t+1] return in our indexing since
    # r[t] = log(mid[t+1]/mid[t]); shift signal by 1 to stay causal)
    sig_shifted = np.concatenate([[0], sig[:-1]])
    return sig_shifted * r


def b05_coin_flip(mid: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Arah acak setiap bar, timing sama dengan seluruh seri (bukan hanya
    subset trade seperti B02)."""
    r = _to_returns(mid)
    sig = rng.choice([-1.0, 1.0], size=len(r))
    return sig * r


def b06_always_long(mid: np.ndarray) -> np.ndarray:
    return _to_returns(mid)


def b07_always_short(mid: np.ndarray) -> np.ndarray:
    return -_to_returns(mid)


def b08_random_freq_matched(mid: np.ndarray, n_trades: int, holding_bars: int, rng: np.random.Generator) -> np.ndarray:
    """Like B02 but WITHOUT cost matching -- frequency matched only. Kept
    distinct from B02 per the registry (8 named nulls, each a different
    control)."""
    r = _to_returns(mid)
    n_bars = len(r)
    if n_bars <= holding_bars:
        return np.array([])
    entries = rng.integers(0, n_bars - holding_bars, size=n_trades)
    return np.array([r[e : e + holding_bars].sum() for e in entries])


def b09_perfect_foresight(mid: np.ndarray) -> np.ndarray:
    """MUSTAHIL dikalahkan by definition -- REFERENCE ONLY. Position = sign of
    the return that is about to happen (uses future information deliberately;
    never a fair comparison, only used for capture_ratio = PnL_kandidat / PnL_B09)."""
    r = _to_returns(mid)
    return np.abs(r)


NULL_REGISTRY = {
    "B01": "BUY_AND_HOLD",
    "B02": "RANDOM_MATCHED",
    "B03": "BLOCK_PERMUTED",
    "B04": "TSMOM_12M",
    "B05": "COIN_FLIP",
    "B06": "ALWAYS_LONG",
    "B07": "ALWAYS_SHORT",
    "B08": "RANDOM_FREQ_MATCHED",
    "B09": "PERFECT_FORESIGHT",
}
MUST_BEAT_ALL = ["B01", "B02", "B03", "B04", "B05", "B06", "B07", "B08"]
REFERENCE_ONLY = ["B09"]


def null_correlation_matrix(null_returns: dict) -> tuple:
    """§null_benchmarks.wajib_dilaporkan: matriks korelasi antar null +
    jumlah null independen efektif (eigenvalue). null_returns: dict of
    {null_id: 1d array}, must all be the same length (align/truncate first)."""
    import pandas as pd

    min_len = min(len(v) for v in null_returns.values())
    df = pd.DataFrame({k: v[:min_len] for k, v in null_returns.items()})
    corr = df.corr()
    eigvals = np.linalg.eigvalsh(corr.values)
    eigvals = np.clip(eigvals, 0, None)
    k_eff_null = (eigvals.sum() ** 2) / (eigvals**2).sum() if (eigvals**2).sum() > 0 else float("nan")
    return corr, k_eff_null
