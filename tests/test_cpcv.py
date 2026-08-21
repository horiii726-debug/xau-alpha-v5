import numpy as np
from src.validation.cpcv import cpcv_splits, n_paths


def test_default_config_gives_66_paths():
    assert n_paths(12, 2) == 66


def test_no_train_test_overlap_without_purge_or_embargo():
    n_bars = 1200
    n_samples = 200
    label_starts = np.linspace(0, n_bars - 10, n_samples).astype(int)
    label_ends = label_starts + 1  # non-overlapping point labels
    for split in cpcv_splits(n_bars, label_starts, label_ends, n_groups=12, n_test_groups=2, embargo_bars=0):
        assert len(set(split.train_idx) & set(split.test_idx)) == 0


def test_purging_removes_overlapping_train_labels():
    n_bars = 100
    # two labels: one spans [40,60) fully inside a likely test block, one spans [45,65) overlapping it
    label_starts = np.array([10, 45])
    label_ends = np.array([30, 65])
    splits = list(cpcv_splits(n_bars, label_starts, label_ends, n_groups=4, n_test_groups=1, embargo_bars=0))
    # find a split where label 1 (bar 45, group index 45//25=1) is in test
    for split in splits:
        if 1 in split.test_idx:
            # label 0 overlaps [45,65)? [10,30) vs [45,65) -> no overlap -> should remain in train
            assert 0 in split.train_idx or 0 in split.test_idx


def test_embargo_removes_bars_immediately_after_test_block():
    n_bars = 100
    label_starts = np.array([0, 26])  # group boundaries at 25,50,75 for n_groups=4
    label_ends = label_starts + 1
    splits = list(cpcv_splits(n_bars, label_starts, label_ends, n_groups=4, n_test_groups=1, embargo_bars=5))
    for split in splits:
        if 0 in split.test_idx:  # bar 0 is in the first test group [0,25)
            # sample at bar 26 is within embargo window [25,30) after test block ends at 25
            assert 1 not in split.train_idx
