# LOMBA 3 -- REZIM

Target: label biner trending (VR realisasi masa depan>1) vs ranging (<=1), VR Lo-MacKinlay q=2 dihitung pada window N bar KE DEPAN. Prediktor dari window N bar SEBELUM t. Metrik AUC keluar-sampel.


## N=12 bar

| peserta                 |      AUC |   n_test |   p_value_boot_auc_gt_half |
|:------------------------|---------:|---------:|---------------------------:|
| PermutationEntropy(m=3) |   0.6287 |     1200 |                      0     |
| LempelZiv               |   0.6104 |     1200 |                      0     |
| Hurst-RS                |   0.5196 |      985 |                      0.312 |
| BASELINE (persistensi)  |   0.5092 |     1200 |                    nan     |
| VR-LoMacKinlay(q=2)     |   0.5    |      985 |                      0.758 |
| SpectralEntropy         |   0.4945 |      985 |                      0.956 |
| VR-Wright-rank(q=2)     |   0.4907 |      985 |                      0.846 |
| DFA-alpha               | nan      |        0 |                    nan     |

**Menang: PermutationEntropy(m=3)** (AUC=0.6287 vs baseline 0.5092). p-value(AUC>0.5)=0.0. (signifikan).


## N=24 bar

| peserta                 |    AUC |   n_test |   p_value_boot_auc_gt_half |
|:------------------------|-------:|---------:|---------------------------:|
| PermutationEntropy(m=3) | 0.6245 |     1200 |                      0     |
| LempelZiv               | 0.6121 |     1200 |                      0     |
| BASELINE (persistensi)  | 0.517  |     1200 |                    nan     |
| SpectralEntropy         | 0.5062 |      992 |                      0.412 |
| Hurst-RS                | 0.4838 |      992 |                      0.808 |
| DFA-alpha               | 0.4802 |      992 |                      0.626 |
| VR-Wright-rank(q=2)     | 0.4795 |      992 |                      0.834 |
| VR-LoMacKinlay(q=2)     | 0.4718 |      992 |                      0.598 |

**Menang: PermutationEntropy(m=3)** (AUC=0.6245 vs baseline 0.5170). p-value(AUC>0.5)=0.0. (signifikan).


## N=48 bar

| peserta                 |    AUC |   n_test |   p_value_boot_auc_gt_half |
|:------------------------|-------:|---------:|---------------------------:|
| LempelZiv               | 0.6141 |     1200 |                      0     |
| PermutationEntropy(m=3) | 0.6091 |     1200 |                      0     |
| VR-Wright-rank(q=2)     | 0.5229 |     1013 |                      0.754 |
| BASELINE (persistensi)  | 0.5117 |     1200 |                    nan     |
| DFA-alpha               | 0.496  |     1013 |                      0.114 |
| SpectralEntropy         | 0.4941 |     1013 |                      0.488 |
| Hurst-RS                | 0.4912 |     1013 |                      0.594 |
| VR-LoMacKinlay(q=2)     | 0.4801 |     1013 |                      0.236 |

**Menang: LempelZiv** (AUC=0.6141 vs baseline 0.5117). p-value(AUC>0.5)=0.0. (signifikan).
