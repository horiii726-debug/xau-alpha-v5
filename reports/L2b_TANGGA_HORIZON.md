# L2b -- Tangga Horizon (M5 XAUUSD 2012-2026)

Biaya round-turn terukur (spread M5 median jam aktif dari 60% LATIH + komisi FTMO + slippage 0.5x spread): **2.920 bps**, DIUKUR bukan diasumsikan. Sigma per horizon dari log-return riil pada horizon itu (data LATIH).

| horizon   |   bar_M5 |   sigma_H_bps |   biaya_bps |   kappa |   IC_breakeven |   bar_per_tahun |   trade_per_tahun_tau1.5 | LOLOS   |
|:----------|---------:|--------------:|------------:|--------:|---------------:|----------------:|-------------------------:|:--------|
| M5        |        1 |        4.6926 |      2.9195 |  0.6222 |         0.3207 |       90263.1   |               12059.2    | False   |
| M15       |        3 |        8.1423 |      2.9195 |  0.3586 |         0.1848 |       30087.7   |                4019.72   | False   |
| M30       |        6 |       11.5147 |      2.9195 |  0.2536 |         0.1307 |       15043.9   |                2009.86   | False   |
| H1        |       12 |       16.2843 |      2.9195 |  0.1793 |         0.0924 |        7521.93  |                1004.93   | False   |
| H4        |       48 |       32.0223 |      2.9195 |  0.0912 |         0.047  |        1880.48  |                 251.232  | True    |
| D1        |      288 |       79.9005 |      2.9195 |  0.0365 |         0.0188 |         313.414 |                  41.8721 | True    |

**Aturan: kappa > 0.15 DICORET dari lomba.**


**Horizon yang LOLOS dan lanjut ke Lomba: ['H4', 'D1']**
