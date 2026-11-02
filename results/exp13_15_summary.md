# Experiments 13 and 15: results

Design: `docs/PREREGISTRATION_EXP13_15.md`.

## Precision calibration (development seeds 100-104)

Targets: gain in a regular context >= 0.8; gain in a random context in [0.35, 0.65].

| a_prec | k_prec | gain regular | gain random | targets met |
|---|---|---|---|---|
| 0.001 | 1.0 | 0.90 | 0.81 | 1/2 |
| 0.001 | 2.0 | 0.84 | 0.74 | 1/2 |
| 0.001 | 4.0 | 0.75 | 0.67 | 0/2 |
| 0.002 | 1.0 | 0.84 | 0.74 | 1/2 |
| 0.002 | 2.0 | 0.75 | 0.67 | 0/2 |
| 0.002 | 4.0 | 0.65 | 0.62 | 1/2 |
| 0.005 | 1.0 | 0.71 | 0.65 | 0/2 |
| 0.005 | 2.0 | 0.63 | 0.61 | 1/2 |
| 0.005 | 4.0 | 0.59 | 0.57 | 1/2 **(selected)** |

## Experiment 15: precision (20 test seeds, mean [95% CI])

### Random context: total error per tone, first vs second half (200 tones)

| net | first half | second half | change |
|---|---|---|---|
| A2b | 26.57 [24.03, 29.10] | 26.82 [24.37, 29.28] | 0.26 [-1.22, 1.74] |
| A2bP | 2.10 [2.02, 2.18] | 1.76 [1.70, 1.83] | -0.33 [-0.40, -0.27] |

Change A2bP minus change A2b (paired): -0.59 [-2.09, 0.90]

### Probe tone D in a regular vs random context

| net | context | D error (PE+ and PE-) | D PE+ | D sensory E | precision gain at probe | context error per tone |
|---|---|---|---|---|---|---|
| A2b | regular | 14.59 [13.16, 16.02] | 14.59 [13.16, 16.02] | 20.33 [19.50, 21.15] | 1.00 [1.00, 1.00] | 4.67 [4.29, 5.05] |
| A2b | random | 16.12 [14.73, 17.51] | 16.09 [14.70, 17.47] | 22.43 [21.50, 23.37] | 1.00 [1.00, 1.00] | 23.76 [21.23, 26.30] |
| A2bP | regular | 2.69 [2.06, 3.33] | 2.69 [2.06, 3.33] | 19.23 [18.49, 19.98] | 0.58 [0.57, 0.59] | 1.61 [1.50, 1.73] |
| A2bP | random | 2.63 [2.06, 3.20] | 2.63 [2.06, 3.20] | 19.49 [18.84, 20.14] | 0.57 [0.56, 0.58] | 1.68 [1.58, 1.78] |

Context effect on D error (random minus regular): A2b 1.53 [0.65, 2.41]; A2bP -0.07 [-0.38, 0.24]; A2bP minus A2b -1.59 [-2.44, -0.75]

### No-harm check: A2bP on the main tests

Unexpected repeat minus regular: -3.88 [-4.47, -3.29] (regular response 17.67 [16.95, 18.39]); omission D-: 0.00 [0.00, 0.00]

## Experiment 13: ideal-observer benchmark

### Exposures to learn the alternation (error below 50% of naive)

Ideal observer: 6. A2b: 5.10 [4.23, 5.97] (ratio 0.85 [0.70, 1.00]). B: 49.40 [38.33, 60.47] (ratio 8.23 [6.39, 10.08]; 1 seeds censored at 100).

### Tone-by-tone: network error vs observer surprise (Spearman r per seed, slots >= 80)

| net | measure | mean r |
|---|---|---|
| N0 | sensory E | -0.17 [-0.26, -0.09] |
| B | own-channel error | 0.15 [0.09, 0.22] |
| A2b | own-channel error | 0.16 [0.09, 0.23] |

### Ideal observer in the random context (bits per tone; 2 bits = chance)

First half 2.11 [2.09, 2.12], second half 2.05 [2.04, 2.07].

