"""Combinatorial Purged Cross-Validation (CPCV), purged + embargo.

Per 05_VALIDASI_STATISTIK.md: cpcv: {n_paths_min: 66, purged: true,
embargo: true, min_positive_pct: 80}. Per M1 (machine_learning.aturan):
"Validasi HANYA CPCV purged + embargo. K-fold biasa DILARANG (bocor lewat
label tumpang tindih)."

Standard CPCV (Lopez de Prado): split the timeline into N groups. For
every combination of k held-out test groups (k>=2 so every path has
train data on both sides of each test block where possible), the
remaining groups form the training set, MINUS any training sample whose
label window overlaps a test sample's label window (purging), MINUS an
embargo of `embargo_bars` bars immediately after each test block (to
remove residual serial-correlation leakage across the train/test
boundary). Total paths = C(N, k).
"""
import itertools
from dataclasses import dataclass

import numpy as np


@dataclass
class CPCVSplit:
    train_idx: np.ndarray
    test_idx: np.ndarray
    path_id: int


def _group_bounds(n_bars: int, n_groups: int):
    edges = np.linspace(0, n_bars, n_groups + 1).astype(int)
    return [(edges[i], edges[i + 1]) for i in range(n_groups)]


def cpcv_splits(
    n_bars: int,
    label_starts: np.ndarray,
    label_ends: np.ndarray,
    n_groups: int = 12,
    n_test_groups: int = 2,
    embargo_bars: int = 0,
):
    """Default n_groups=12, n_test_groups=2 -> C(12,2)=66 paths, matching
    05_VALIDASI_STATISTIK.md cpcv.n_paths_min=66 exactly."""
    """Yield CPCVSplit objects. label_starts/ends: per-SAMPLE (not per-bar)
    label window [start,end) in bar-index units, used for purging.
    Samples here are assumed to be indexed 0..n_samples-1 with a bar
    position given by label_starts (the entry bar)."""
    bounds = _group_bounds(n_bars, n_groups)
    n_samples = len(label_starts)
    sample_bar = np.asarray(label_starts)

    combos = list(itertools.combinations(range(n_groups), n_test_groups))
    for path_id, combo in enumerate(combos):
        test_ranges = [bounds[g] for g in combo]
        test_mask = np.zeros(n_samples, dtype=bool)
        for lo, hi in test_ranges:
            test_mask |= (sample_bar >= lo) & (sample_bar < hi)
        test_idx = np.where(test_mask)[0]

        train_mask = ~test_mask
        # Purge: drop train samples whose label window [start,end) overlaps
        # ANY test sample's label window.
        if len(test_idx) > 0:
            test_starts = np.asarray(label_starts)[test_idx]
            test_ends = np.asarray(label_ends)[test_idx]
            test_lo = test_starts.min()
            test_hi = test_ends.max()
            train_starts = np.asarray(label_starts)
            train_ends = np.asarray(label_ends)
            overlap = (train_starts < test_hi) & (train_ends > test_lo)
            train_mask &= ~overlap

        # Embargo: drop train samples starting within embargo_bars bars
        # AFTER any test block's end.
        if embargo_bars > 0:
            for lo, hi in test_ranges:
                embargo_lo, embargo_hi = hi, min(n_bars, hi + embargo_bars)
                in_embargo = (sample_bar >= embargo_lo) & (sample_bar < embargo_hi)
                train_mask &= ~in_embargo

        train_idx = np.where(train_mask)[0]
        yield CPCVSplit(train_idx=train_idx, test_idx=test_idx, path_id=path_id)


def n_paths(n_groups: int, n_test_groups: int) -> int:
    from math import comb

    return comb(n_groups, n_test_groups)
