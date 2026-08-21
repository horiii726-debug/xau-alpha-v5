import numpy as np
from src.stats.effective_n import concurrency, label_uniqueness, effective_n, uniqueness_ratio


def test_non_overlapping_labels_have_uniqueness_1():
    starts = np.array([0, 10, 20, 30])
    ends = np.array([10, 20, 30, 40])
    uniq = label_uniqueness(starts, ends, n_bars=40)
    assert np.allclose(uniq, 1.0)
    assert np.isclose(effective_n(starts, ends, 40), 4.0)
    assert np.isclose(uniqueness_ratio(starts, ends, 40), 1.0)


def test_fully_overlapping_labels_split_uniqueness():
    # 4 labels, all spanning the same [0,10) window -> concurrency=4 everywhere
    starts = np.array([0, 0, 0, 0])
    ends = np.array([10, 10, 10, 10])
    uniq = label_uniqueness(starts, ends, n_bars=10)
    assert np.allclose(uniq, 0.25)
    assert np.isclose(effective_n(starts, ends, 10), 1.0)  # 4 labels * 0.25 uniqueness = 1 effective obs


def test_partial_overlap_gives_intermediate_uniqueness():
    # label A: [0,10), label B: [5,15) -- overlap in [5,10)
    starts = np.array([0, 5])
    ends = np.array([10, 15])
    conc = concurrency(starts, ends, n_bars=15)
    assert list(conc[:5]) == [1, 1, 1, 1, 1]
    assert list(conc[5:10]) == [2, 2, 2, 2, 2]
    assert list(conc[10:15]) == [1, 1, 1, 1, 1]
    en = effective_n(starts, ends, 15)
    assert 1.0 < en < 2.0  # less than fully independent (2.0), more than fully overlapping (1.0)
