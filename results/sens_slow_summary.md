# Sensitivity: slower spike-frequency adaptation (20 seeds, mean [95% CI])

Exploratory; design and predictions in `docs/SENSITIVITY_SLOW_ADAPTATION.md`. tau_w = 300 ms rows are the main runs (`results/exp1_summary_full.md`, `results/tier2_summary_full.md`). Predictive networks are not recalibrated.

## Experiment 1 main configuration

| tau_w (ms) | adaptation | SSA index | iMM | iRS | iPE (cascade) | iPE (many) | omission slot response |
|---|---|---|---|---|---|---|---|
| 1000 | sfa | 0.12 [0.12, 0.13] | 0.14 [0.13, 0.15] | 0.14 [0.13, 0.15] | 0.00 [-0.01, 0.02] | -0.01 [-0.02, 0.01] | 0.06 [-0.01, 0.13] |
| 1000 | both | 0.29 [0.28, 0.29] | 0.29 [0.28, 0.31] | 0.29 [0.27, 0.30] | 0.01 [-0.00, 0.02] | 0.01 [0.00, 0.03] | 0.07 [-0.03, 0.17] |
| 3000 | sfa | 0.34 [0.33, 0.35] | 0.35 [0.34, 0.36] | 0.33 [0.32, 0.34] | 0.02 [0.00, 0.03] | 0.02 [0.00, 0.03] | 0.00 [-0.02, 0.02] |
| 3000 | both | 0.45 [0.43, 0.46] | 0.42 [0.40, 0.43] | 0.42 [0.41, 0.44] | -0.01 [-0.02, 0.01] | -0.00 [-0.02, 0.02] | 0.05 [0.00, 0.10] |

## Tier 2 (adaptation = both)

| tau_w (ms) | net | unexpected repeat minus regular | omission D- (PE- omitted minus present) | M1 post1 - pre1 (cont. A) | M1 sensory-only (E cells) |
|---|---|---|---|---|---|
| 1000 | N0 | -3.38 [-4.00, -2.76] | 0.00 [0.00, 0.00] | 3.51 [2.81, 4.20] | 3.51 [2.81, 4.20] |
| 1000 | B | -6.42 [-7.34, -5.50] | 0.00 [0.00, 0.00] | 6.92 [5.42, 8.42] | 3.45 [2.58, 4.32] |
| 1000 | A2b | 1.10 [-1.23, 3.43] | 1.02 [0.12, 1.91] | 12.19 [10.47, 13.91] | 6.21 [5.28, 7.15] |
| 3000 | N0 | -3.05 [-3.66, -2.44] | 0.00 [0.00, 0.00] | 3.23 [2.62, 3.83] | 3.23 [2.62, 3.83] |
| 3000 | B | -4.79 [-5.54, -4.03] | 0.00 [0.00, 0.00] | 4.45 [3.49, 5.41] | 3.03 [2.38, 3.68] |
| 3000 | A2b | -5.74 [-6.66, -4.83] | 0.00 [0.00, 0.00] | 8.92 [7.35, 10.49] | 5.14 [4.41, 5.86] |
