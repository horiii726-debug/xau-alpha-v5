# LOMBA 4 -- ENTRY

**Biaya round-trip terukur (jam trading aktif saja, dari TRAIN):** spread median=1.736bps, komisi FTMO round-trip=0.280bps, slippage(0.5x spread)=0.868bps -> **TOTAL=2.885bps** (n=1,150,608 bar M1 jam aktif).


Target: tanda return H bar ke depan. Tiap sinyal di-z-score, entry hanya kalau |z|>=tau. Baseline: entry ACAK dicocokkan jumlah trade & holding period per (H,tau).


## H=1h, tau=1.0

| peserta               |   tau |   n_trades |      IC |   hit_rate |   expectancy_net_bps |   p_value_boot |
|:----------------------|------:|-----------:|--------:|-----------:|---------------------:|---------------:|
| MAD-Zscore-momentum   |     1 |      34744 | -0.0143 |     0.4865 |              -2.2264 |              1 |
| Momentum-VolScaled    |     1 |     112199 | -0.017  |     0.4798 |              -2.5858 |              1 |
| ORB                   |     1 |      47881 | -0.0174 |     0.4658 |              -2.7577 |              1 |
| DriftBurst-tstat      |     1 |      36127 | -0.018  |     0.478  |              -2.7849 |              1 |
| BASELINE (entry acak) |     1 |      58460 |  0      |     0.4084 |              -2.9204 |            nan |
| CUSUM                 |     1 |       7610 | -0.01   |     0.4954 |              -3.1716 |              1 |
| ShortHorizon-Reversal |     1 |     112199 |  0.017  |     0.4985 |              -3.1836 |              1 |

**Menang: MAD-Zscore-momentum** (expectancy bersih=-2.226bps vs baseline -2.920bps). p-value bootstrap=1.0. (TIDAK signifikan/NA).


## H=1h, tau=1.5

| peserta               |   tau |   n_trades |      IC |   hit_rate |   expectancy_net_bps |   p_value_boot |
|:----------------------|------:|-----------:|--------:|-----------:|---------------------:|---------------:|
| MAD-Zscore-momentum   |   1.5 |      20565 | -0.0143 |     0.4909 |              -2.2238 |              1 |
| Momentum-VolScaled    |   1.5 |     112180 | -0.017  |     0.4798 |              -2.586  |              1 |
| DriftBurst-tstat      |   1.5 |      15758 | -0.018  |     0.481  |              -2.6985 |              1 |
| ORB                   |   1.5 |      26085 | -0.0174 |     0.4669 |              -2.7195 |              1 |
| BASELINE (entry acak) |   1.5 |      48911 |  0      |     0.4096 |              -2.9526 |            nan |
| CUSUM                 |   1.5 |       6701 | -0.01   |     0.4987 |              -3.0017 |              1 |
| ShortHorizon-Reversal |   1.5 |     112180 |  0.017  |     0.4985 |              -3.1834 |              1 |

**Menang: MAD-Zscore-momentum** (expectancy bersih=-2.224bps vs baseline -2.953bps). p-value bootstrap=1.0. (TIDAK signifikan/NA).


## H=4h, tau=1.0

| peserta               |   tau |   n_trades |      IC |   hit_rate |   expectancy_net_bps |   p_value_boot |
|:----------------------|------:|-----------:|--------:|-----------:|---------------------:|---------------:|
| CUSUM                 |     1 |       7610 | -0.025  |     0.4925 |               0.1447 |         0.4305 |
| MAD-Zscore-momentum   |     1 |      34729 |  0.0032 |     0.4978 |              -1.5109 |         1      |
| Momentum-VolScaled    |     1 |     112164 |  0.0028 |     0.4897 |              -1.7548 |         1      |
| ORB                   |     1 |      47858 |  0.0053 |     0.4828 |              -1.8784 |         1      |
| DriftBurst-tstat      |     1 |      36109 | -0.0044 |     0.4921 |              -2.44   |         1      |
| BASELINE (entry acak) |     1 |      58439 |  0      |     0.4227 |              -2.9154 |       nan      |
| ShortHorizon-Reversal |     1 |     112164 | -0.0028 |     0.4931 |              -4.0146 |         1      |

**Menang: CUSUM** (expectancy bersih=0.145bps vs baseline -2.915bps). p-value bootstrap=0.4305. (TIDAK signifikan/NA).


## H=4h, tau=1.5

| peserta               |   tau |   n_trades |      IC |   hit_rate |   expectancy_net_bps |   p_value_boot |
|:----------------------|------:|-----------:|--------:|-----------:|---------------------:|---------------:|
| CUSUM                 |   1.5 |       6701 | -0.025  |     0.4872 |              -0.9926 |         0.8855 |
| MAD-Zscore-momentum   |   1.5 |      20565 |  0.0032 |     0.4968 |              -1.7151 |         1      |
| Momentum-VolScaled    |   1.5 |     112145 |  0.0028 |     0.4897 |              -1.7574 |         1      |
| ORB                   |   1.5 |      26071 |  0.0053 |     0.4813 |              -2.5335 |         1      |
| BASELINE (entry acak) |   1.5 |      48895 |  0      |     0.4242 |              -2.5761 |       nan      |
| DriftBurst-tstat      |   1.5 |      15746 | -0.0044 |     0.488  |              -2.9685 |         1      |
| ShortHorizon-Reversal |   1.5 |     112145 | -0.0028 |     0.4931 |              -4.012  |         1      |

**Menang: CUSUM** (expectancy bersih=-0.993bps vs baseline -2.576bps). p-value bootstrap=0.8855. (TIDAK signifikan/NA).


## H=1d, tau=1.0

| peserta               |   tau |   n_trades |      IC |   hit_rate |   expectancy_net_bps |   p_value_boot |
|:----------------------|------:|-----------:|--------:|-----------:|---------------------:|---------------:|
| CUSUM                 |     1 |       7609 | -0.0038 |     0.5085 |              13.0533 |         0      |
| MAD-Zscore-momentum   |     1 |      34653 |  0.0091 |     0.4964 |               1.2169 |         0.0585 |
| Momentum-VolScaled    |     1 |     111924 |  0.0129 |     0.4987 |              -0.2628 |         0.7505 |
| DriftBurst-tstat      |     1 |      36031 | -0.0013 |     0.4917 |              -0.3362 |         0.6885 |
| ORB                   |     1 |      47770 |  0.002  |     0.492  |              -3.1496 |         1      |
| BASELINE (entry acak) |     1 |      58318 |  0      |     0.4926 |              -3.5405 |       nan      |
| ShortHorizon-Reversal |     1 |     111924 | -0.0129 |     0.4914 |              -5.5066 |         1      |

**Menang: CUSUM** (expectancy bersih=13.053bps vs baseline -3.541bps). p-value bootstrap=0.0. (signifikan).


## H=1d, tau=1.5

| peserta               |   tau |   n_trades |      IC |   hit_rate |   expectancy_net_bps |   p_value_boot |
|:----------------------|------:|-----------:|--------:|-----------:|---------------------:|---------------:|
| CUSUM                 |   1.5 |       6700 | -0.0038 |     0.5106 |              14.1081 |         0      |
| MAD-Zscore-momentum   |   1.5 |      20532 |  0.0091 |     0.5013 |               3.4555 |         0.001  |
| Momentum-VolScaled    |   1.5 |     111905 |  0.0129 |     0.4987 |              -0.2658 |         0.753  |
| DriftBurst-tstat      |   1.5 |      15703 | -0.0013 |     0.4902 |              -2.4982 |         0.9835 |
| BASELINE (entry acak) |   1.5 |      48796 |  0      |     0.4942 |              -2.6601 |       nan      |
| ORB                   |   1.5 |      26034 |  0.002  |     0.4863 |              -4.6131 |         1      |
| ShortHorizon-Reversal |   1.5 |     111905 | -0.0129 |     0.4914 |              -5.5036 |         1      |

**Menang: CUSUM** (expectancy bersih=14.108bps vs baseline -2.660bps). p-value bootstrap=0.0. (signifikan).
