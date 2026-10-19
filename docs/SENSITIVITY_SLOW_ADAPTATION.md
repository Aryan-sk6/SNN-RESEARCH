# Sensitivity: slower spike-frequency adaptation (exploratory; written before the run)

**Why.** In Experiment 1 adaptation alone explained little of the deviant-specific response at tau_w = 300 ms
(spike-frequency adaptation decay), and the 450 ms inter-tone interval is longer than that decay. A reviewer could
say the result depends on this choice. So the decay is made slower and the key results are repeated.
`docs/ROADMAP.md` item 19. **Exploratory**: the extra values were not part of the original pre-registration, and
nothing is retuned to improve any result.

**What changes.** Only `tau_w_ms` (the decay of the adaptation variable): 300 ms (the original, reused, not re-run),
1000 ms and 3000 ms. Nothing else, and **the predictive networks are not recalibrated** (their weights were set at
300 ms), so differences for B and A2b mix the adaptation change with that mismatch. Depression (tm_tau_rec 500 ms)
is unchanged; the "both" condition therefore changes only through its adaptation part.

**Runs (20 seeds each, same seeds as the main runs).**
1. Experiment 1 main configuration (standard/deviant three channels apart, p = 0.1, 400 trials), adaptation = SFA
   and SFA + depression: SSA index, iMM / iRS / iPE (normalised) against both controls, and the omission block.
2. Tier 2 at tau_w = 1000 and 3000 ms for N0, B, A2b: unexpected repeat (ABABAA), omission (v3 measure),
   post-oddball tone M1 with continuation A. Same measures and rules as the main Tier 2 run.

**Predictions (stated now).**
- P-s1: slower adaptation raises N0's SSA index and iMM; iPE stays near 0 (adaptation alone still does not produce
  prediction error), because iPE is built from controls that are adapted equally.
- P-s2: N0 keeps the adaptation signature on the unexpected repeat (repeat smaller than regular), N0's omission
  contrast stays exactly 0 (no error cells), and N0's M1 rise stays below A2b's.
- P-s3: A2b keeps a positive unexpected-repeat effect and a positive omission contrast. These could weaken because
  the network is not recalibrated; if they do, that is reported, not fixed.
Any prediction that fails is reported as failed.

## Results (20 seeds; full table `results/sens_slow_summary.md`)

Experiment 1 main configuration, SSA index and prediction-error component (iPE, normalised; cascade control):

| adaptation | tau_w 300 (main run) | 1000 | 3000 |
|---|---|---|---|
| SFA only, SSA index | 0.019 [0.012, 0.026] | 0.12 [0.12, 0.13] | 0.34 [0.33, 0.35] |
| SFA only, iPE | 0.011 [-0.003, 0.025] | 0.00 [-0.01, 0.02] | 0.02 [0.00, 0.03] |
| SFA + depression, SSA index | 0.187 [0.178, 0.195] | 0.29 [0.28, 0.29] | 0.45 [0.43, 0.46] |
| SFA + depression, iPE | -0.000 [-0.011, 0.011] | 0.01 [-0.00, 0.02] | -0.01 [-0.02, 0.01] |

Tier 2 (adaptation = SFA + depression; predictive networks not recalibrated):

| tau_w | unexpected repeat minus regular: N0 / B / A2b | omission D-: N0 / B / A2b | M1 post1 - pre1: N0 / B / A2b |
|---|---|---|---|
| 300 (main) | -2.84 / -1.15 / +7.57 | 0 / 0.14 / 5.97 | 2.68 / 6.36 / 10.83 |
| 1000 | -3.38 / -6.42 / +1.10 [-1.23, 3.43] | 0 / 0 / 1.02 [0.12, 1.91] | 3.51 / 6.92 / 12.19 |
| 3000 | -3.05 / -4.79 / -5.74 | 0 / 0 / 0 | 3.23 / 4.45 / 8.92 |

### Against the predictions
- **P-s1 holds.** Slower adaptation raises the SSA index and iMM/iRS a lot (SFA alone 0.02 to 0.34), but iPE stays at
  about 0 (all CIs within about +/-0.03). Adaptation alone, however slow, still produces no prediction-error component in
  this model. It does produce a much larger apparent "mismatch" response: this is the answer to the objection that the
  Experiment 1 result depended on tau_w = 300 ms for the SSA index. At 3000 ms adaptation alone explains a large
  share of the deviant-versus-standard difference, all of it in the stimulus-specific adaptation (iRS) part.
- **P-s2 holds.** N0 keeps the adaptation signature on the unexpected repeat (-3.38, -3.05), its omission contrast is
  exactly 0, and its M1 rise (3.5, 3.2) stays well below A2b's.
- **P-s3 fails.** A2b's unexpected-repeat effect is no longer clearly positive at 1000 ms (+1.10 [-1.23, 3.43]) and is
  negative at 3000 ms (-5.74); its omission contrast shrinks to 1.02 at 1000 ms and 0 at 3000 ms. B also becomes more
  negative. So the main Tier 2 results for the repeat and omission depend on adaptation being fast, at the settings
  the networks were calibrated for. This is confounded with the lack of recalibration (the predictive weights were
  set at 300 ms), so it shows that the result is **not robust to this change without re-tuning**; it does not show
  that the mechanism cannot work with slow adaptation.
- The tone after the odd one (M1) stays above N0 in A2b at both values (12.19 vs 3.51; 8.92 vs 3.23), the most robust
  Tier 2 result here.
