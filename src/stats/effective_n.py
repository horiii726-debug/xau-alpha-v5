"""Lopez de Prado sample uniqueness / effective N.

Per 05_VALIDASI_STATISTIK.md: "effective_n: method: lopez_de_prado_uniqueness,
mandatory_for_all_pvalues: true, assertion_reject_without_weight: true".

A label spans [t0, t1) (its holding period). Labels that overlap in time
share information -- they are not independent observations. Concurrency at
bar t = number of labels whose interval covers t. A label's average
uniqueness = mean over its span of 1/concurrency(t). Effective N = sum of
per-label average uniqueness (Lopez de Prado, Advances in Financial
Machine Learning, ch.4).
"""
import numpy as np


def concurrency(starts: np.ndarray, ends: np.ndarray, n_bars: int) -> np.ndarray:
    """starts/ends are integer bar indices, half-open [start, end). Returns
    an array of length n_bars with the number of overlapping labels at each bar."""
    conc = np.zeros(n_bars, dtype=np.int64)
    for s, e in zip(starts, ends):
        s = max(0, int(s))
        e = min(n_bars, int(e))
        if e > s:
            conc[s:e] += 1
    return conc


def label_uniqueness(starts: np.ndarray, ends: np.ndarray, n_bars: int) -> np.ndarray:
    """Average uniqueness per label = mean(1/concurrency) over the label's span."""
    conc = concurrency(starts, ends, n_bars)
    conc_safe = np.where(conc == 0, 1, conc)  # avoid div-by-zero for bars with no label (shouldn't happen for a label's own span)
    inv_conc = 1.0 / conc_safe
    uniq = np.empty(len(starts), dtype=np.float64)
    for i, (s, e) in enumerate(zip(starts, ends)):
        s = max(0, int(s))
        e = min(n_bars, int(e))
        if e <= s:
            uniq[i] = 0.0
        else:
            uniq[i] = inv_conc[s:e].mean()
    return uniq


def effective_n(starts: np.ndarray, ends: np.ndarray, n_bars: int) -> float:
    """Effective sample size = sum of per-label average uniqueness."""
    return float(label_uniqueness(starts, ends, n_bars).sum())


def uniqueness_ratio(starts: np.ndarray, ends: np.ndarray, n_bars: int) -> float:
    """Effective N / raw N -- used to derive BR_efektif = trades_per_year * ratio."""
    n = len(starts)
    if n == 0:
        return float("nan")
    return effective_n(starts, ends, n_bars) / n


def sample_weights(starts: np.ndarray, ends: np.ndarray, n_bars: int) -> np.ndarray:
    """Per-sample weights for weighted p-values / regression (weight = uniqueness,
    normalized to sum to n_samples, standard LdP convention)."""
    uniq = label_uniqueness(starts, ends, n_bars)
    total = uniq.sum()
    if total <= 0:
        return np.ones_like(uniq)
    return uniq / total * len(uniq)
