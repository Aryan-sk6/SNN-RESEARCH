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
