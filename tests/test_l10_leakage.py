"""§L10 uji kebocoran wajib (01_HUKUM.md):

"Bangun satu fitur yang SENGAJA bocor (memakai return masa depan). Fitur
itu HARUS menghasilkan IC > 0.5 dan mengalahkan semua null. Kalau tidak,
pipeline validasinya sendiri yang rusak. Jalankan SEBELUM kandidat
pertama."

Plus the null_benchmarks.uji_sanity_wajib:
- "Sinyal acak murni TIDAK boleh mengalahkan null manapun"
- "Sinyal lookahead sengaja HARUS mengalahkan semuanya (kalau tidak, bug di null)"

This is the F1 pass/fail gate itself (07_FASE_EKSEKUSI.md F1.lulus /
F1.gagal): run on SYNTHETIC data (self-generated random walk), because
its entire purpose is to validate that the null-testing machinery works
correctly BEFORE any real candidate or real market data is involved.
"""
import numpy as np
import pytest

from src.stats import nulls
from src.validation import montecarlo as mc


def make_random_walk(n=8000, seed=0, drift=0.0, sigma=0.001):
    rng = np.random.default_rng(seed)
    r = rng.normal(drift, sigma, size=n)
    mid = 100 * np.exp(np.cumsum(r))
    return mid, r


def information_coefficient(signal: np.ndarray, forward_return: np.ndarray) -> float:
    n = min(len(signal), len(forward_return))
    s, f = signal[:n], forward_return[:n]
    mask = np.isfinite(s) & np.isfinite(f)
    if mask.sum() < 2:
        return 0.0
    return float(np.corrcoef(s[mask], f[mask])[0, 1])


def strategy_return_from_signal(signal: np.ndarray, r: np.ndarray) -> np.ndarray:
    """signal[t] decides the position HELD DURING (t, t+1] -- i.e. applied to
    r[t] (r[t] = log(mid[t+1]/mid[t])). No shift here: callers construct
    `signal` to already be causal (or, for the deliberately-leaky feature,
    deliberately NOT causal -- that's the point of this test)."""
    n = min(len(signal), len(r))
    return signal[:n] * r[:n]


@pytest.fixture
def synthetic_market():
    mid, r = make_random_walk(n=8000, seed=123, drift=0.0, sigma=0.0008)
    return mid, r


def test_deliberately_leaky_feature_achieves_ic_above_0_5(synthetic_market):
    mid, r = synthetic_market
    # THE LEAK: signal = sign of the return that is about to happen --
    # this uses information from bar t+1 to decide the position at bar t,
    # which is exactly what L1/L9 forbid for a real candidate. On purpose,
    # here, to prove the measurement pipeline can catch it.
    leaky_signal = np.sign(r)  # perfectly informed about r[t] itself
    ic = information_coefficient(leaky_signal, r)
    assert ic > 0.5, f"leaky feature IC={ic:.3f}, expected > 0.5 -- L10 uji kebocoran GAGAL"


def test_deliberately_leaky_feature_beats_all_must_beat_all_nulls(synthetic_market):
    mid, r = synthetic_market
    rng = np.random.default_rng(999)

    leaky_signal = np.sign(r)
    leaky_returns = strategy_return_from_signal(leaky_signal, r)
    leaky_total = leaky_returns.sum()

    null_totals = {
        "B01": nulls.b01_buy_and_hold(mid).sum(),
        "B02": nulls.b02_random_matched(mid, costs_bps=np.array([0.0]), holding_bars=5, n_trades=200, rng=rng).sum(),
        "B03": nulls.b03_block_permuted(mid, block_size=20, rng=rng).sum(),
        "B04": nulls.b04_tsmom_12m(mid, lookback_bars=200).sum(),
        "B05": nulls.b05_coin_flip(mid, rng).sum(),
        "B06": nulls.b06_always_long(mid).sum(),
        "B07": nulls.b07_always_short(mid).sum(),
        "B08": nulls.b08_random_freq_matched(mid, n_trades=200, holding_bars=5, rng=rng).sum(),
    }

    failures = {k: v for k, v in null_totals.items() if leaky_total <= v}
    assert not failures, (
        f"Leaky feature (total={leaky_total:.4f}) FAILED to beat: {failures} "
        f"-- L10 says pipeline validasinya sendiri yang rusak, bukan fiturnya."
    )


def test_pure_random_signal_does_not_beat_any_null(synthetic_market):
    """uji_sanity_wajib: 'Sinyal acak murni TIDAK boleh mengalahkan null
    manapun.'

    First attempt at this test compared raw summed totals of a random
    +-1 signal against B01/B06/B07. That failed at a 33.5% rate -- not
    because the nulls are wrong, but because B01(=B06) and B07 are exact
    mirror images (+X and -X) around a near-zero-drift synthetic walk, so
    "beat both simultaneously" collapses to "|random_total| > |X|", which
    a wide, unbiased random_total distribution clears far more than 10%
    of the time. That was a weak test design, not a finding about the
    nulls.

    What L10's sanity check actually needs to verify is that the
    STATISTICAL PROCEDURE used to judge real candidates (MC1 block
    permutation, the actual gate mechanism) doesn't flag pure noise as
    significant more often than roughly its nominal false-positive rate.
    That's what's tested here, reusing the real mc1_permutation function.
    """
    mid, r = synthetic_market

    n_repeats = 100
    false_positives = 0
    for i in range(n_repeats):
        rng = np.random.default_rng(1000 + i)
        random_signal = rng.choice([-1.0, 1.0], size=len(r))
        result = mc.mc1_permutation(random_signal, r, n=200, block_size=20, rng=np.random.default_rng(5000 + i))
        if result["gate_pass"]:
            false_positives += 1

    false_positive_rate = false_positives / n_repeats
    # nominal rate for a 95th-percentile gate is 5%; generous ceiling to
    # absorb Monte Carlo noise from a modest n_repeats/n
    assert false_positive_rate < 0.15, (
        f"MC1 flagged pure-noise signals as significant in {false_positive_rate:.1%} of trials "
        f"(nominal ~5% expected) -- the gate itself may be broken"
    )


def test_causal_signal_cannot_see_same_bar_leak_when_properly_shifted(synthetic_market):
    """Regression guard: if a candidate's signal is properly shifted to be
    causal (decided at bar t using only data up to t, applied to r[t] which
    is the (t,t+1] return), IC against the SAME-bar return it's built from
    should collapse relative to the deliberately-leaky version -- proving
    the shift actually removes the leak rather than being a no-op."""
    mid, r = synthetic_market
    leaky_signal = np.sign(r)  # sees r[t] directly
    causal_signal = np.concatenate([[0], np.sign(r[:-1])])  # sees r[t-1], applied to r[t]

    ic_leaky = information_coefficient(leaky_signal, r)
    ic_causal = information_coefficient(causal_signal, r)

    assert ic_leaky > 0.5
    assert abs(ic_causal) < 0.15, f"causal-shifted signal still has IC={ic_causal:.3f} against a pure random walk -- shift logic is broken"
