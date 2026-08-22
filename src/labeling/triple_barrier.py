"""Triple-barrier labeling, per 04_PARTISI_LABELING_PAYOFF.md.

vol_estimator_untuk_barrier = V01_PARKINSON (NOT ATR -- ATR is banned).
TP = P0*(1+k_tp*sigma), SL = P0*(1-k_sl*sigma), vertical = max_hold_bars.
Execution: entry at next bar's open after the entry signal (L9). Barrier
touch is checked using each bar's HIGH/LOW (a bar can touch either side
intrabar even if its open/close don't)."""
from dataclasses import dataclass

import numpy as np
from numba import njit


def parkinson_sigma(high: np.ndarray, low: np.ndarray, window: int) -> np.ndarray:
    """V01_PARKINSON: sigma^2 = (1/(4*n*ln2)) * sum[(ln(H/L))^2] over a
    trailing window, computed causally (uses only bars up to and including
    t)."""
    log_hl2 = np.log(high / low) ** 2
    n = len(log_hl2)
    sigma2 = np.full(n, np.nan)
    c = 1.0 / (4 * np.log(2))
    cumsum = np.concatenate([[0], np.cumsum(log_hl2)])
    for t in range(window, n + 1):
        window_sum = cumsum[t] - cumsum[t - window]
        sigma2[t - 1] = c * window_sum / window
    return np.sqrt(sigma2)


@dataclass
class BarrierResult:
    outcome: np.ndarray  # +1 = TP hit, -1 = SL hit, 0 = vertical (time) exit
    ret: np.ndarray  # realized return of the trade
    bars_held: np.ndarray
    entry_idx: np.ndarray
    ambiguous: np.ndarray  # True if TP and SL were BOTH touched within the same bar (tie-break: assume SL first)


@njit(cache=True)
def _triple_barrier_core(open_, high, low, close, entry_bar_idx, direction, sigma, k_sl, k_tp, max_hold_bars):
    n = len(entry_bar_idx)
    outcome = np.zeros(n, dtype=np.int8)
    ret = np.zeros(n, dtype=np.float64)
    bars_held = np.zeros(n, dtype=np.int64)
    ambiguous = np.zeros(n, dtype=np.bool_)

    n_bars = len(open_)
    for i in range(n):
        e = entry_bar_idx[i]
        d = direction[i]
        if e >= n_bars or e < 0:
            continue
        s = sigma[e - 1] if e > 0 else np.nan
        if np.isnan(s) or s <= 0:
            continue
        p0 = open_[e]
        if d > 0:
            tp_price = p0 * (1 + k_tp * s)
            sl_price = p0 * (1 - k_sl * s)
        else:
            tp_price = p0 * (1 - k_tp * s)
            sl_price = p0 * (1 + k_sl * s)

        end = min(n_bars, e + max_hold_bars)
        hit = 0
        exit_bar = end - 1
        exit_price = close[end - 1] if end - 1 < n_bars else close[-1]
        for t in range(e, end):
            if d > 0:
                touched_tp = high[t] >= tp_price
                touched_sl = low[t] <= sl_price
            else:
                touched_tp = low[t] <= tp_price
                touched_sl = high[t] >= sl_price
            if touched_tp and touched_sl:
                hit = -1
                exit_bar = t
                exit_price = sl_price
                ambiguous[i] = True
                break
            elif touched_tp:
                hit = 1
                exit_bar = t
                exit_price = tp_price
                break
            elif touched_sl:
                hit = -1
                exit_bar = t
                exit_price = sl_price
                break
        outcome[i] = hit
        bars_held[i] = exit_bar - e + 1
        raw_ret = (exit_price - p0) / p0
        ret[i] = raw_ret * d

    return outcome, ret, bars_held, ambiguous


def triple_barrier_labels(
    open_: np.ndarray,
    high: np.ndarray,
    low: np.ndarray,
    close: np.ndarray,
    entry_bar_idx: np.ndarray,
    direction: np.ndarray,  # +1 long, -1 short, per entry
    sigma: np.ndarray,  # causal vol estimate, indexed same as open/high/low/close
    k_sl: float,
    k_tp: float,
    max_hold_bars: int,
) -> BarrierResult:
    """entry_bar_idx: the bar whose OPEN is the fill price (already the
    bar AFTER the signal bar, per L9 -- caller's responsibility to shift).
    Core loop is numba-JIT-compiled (see _triple_barrier_core) -- this
    function is called with millions of entries across F2/F5, and a pure
    Python per-bar loop does not scale to M1 granularity."""
    outcome, ret, bars_held, ambiguous = _triple_barrier_core(
        np.asarray(open_, dtype=np.float64),
        np.asarray(high, dtype=np.float64),
        np.asarray(low, dtype=np.float64),
        np.asarray(close, dtype=np.float64),
        np.asarray(entry_bar_idx, dtype=np.int64),
        np.asarray(direction, dtype=np.int64),
        np.asarray(sigma, dtype=np.float64),
        float(k_sl), float(k_tp), int(max_hold_bars),
    )
    return BarrierResult(outcome=outcome, ret=ret, bars_held=bars_held, entry_idx=entry_bar_idx, ambiguous=ambiguous)


def breakeven_mekanis(k_sl: float, k_tp: float) -> float:
    return k_sl / (k_sl + k_tp)
