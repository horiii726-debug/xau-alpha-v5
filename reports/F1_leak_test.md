# F1 -- Uji Kebocoran L10 (pytest)

**Hasil: LOLOS** (exit code 0)

```
============================= test session starts ==============================
platform linux -- Python 3.12.13, pytest-9.1.1, pluggy-1.6.0 -- /venv/main/bin/python
cachedir: .pytest_cache
rootdir: /workspace/xau-alpha-v5
configfile: pytest.ini
plugins: anyio-4.14.2
collecting ... collected 4 items

tests/test_l10_leakage.py::test_deliberately_leaky_feature_achieves_ic_above_0_5 PASSED [ 25%]
tests/test_l10_leakage.py::test_deliberately_leaky_feature_beats_all_must_beat_all_nulls PASSED [ 50%]
tests/test_l10_leakage.py::test_pure_random_signal_does_not_beat_any_null PASSED [ 75%]
tests/test_l10_leakage.py::test_causal_signal_cannot_see_same_bar_leak_when_properly_shifted PASSED [100%]

============================== 4 passed in 1.44s ===============================


```