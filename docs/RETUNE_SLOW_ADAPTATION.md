# Re-tuning for slower adaptation (design written before any run at the new time constants)

## Why
The slow-adaptation sensitivity run (`docs/SENSITIVITY_SLOW_ADAPTATION.md`) slowed the decay of spike-frequency adaptation
(tau_w) from 300 ms to 1000 and 3000 ms **without re-tuning** the predictive circuit. Mechanism A's unexpected-repeat
and omission effects then disappeared (repeat +1.10 [-1.23, 3.43] at 1000 ms, -5.74 at 3000 ms). The circuit's constants
had been calibrated at 300 ms, so that run cannot tell apart two explanations:
1. the mechanism only works when adaptation is fast, or
2. the circuit was simply mis-calibrated for the new adaptation level (for example, weaker sensory responses no
   longer drive the delay line and error cells as intended).

This run re-tunes the circuit at the new tau_w using **the same sanity targets as the original calibration** and then
repeats the main tests. I had seen the untuned sensitivity results before writing this, so this is a follow-up check,
not a blind test. It is labelled exploratory.

## Procedure
**What may change.** Only constants that were sanity-calibrated originally (`docs/PARAMETERS.md`), in a fixed grid:
- `f_E` in {1.0, 1.15, 1.3, 1.5, 1.75, 2.0}: one common factor on the three weights driven by the sensory cells
  (E -> delay line 22 mV, E -> PE+ 18 mV, E -> PE- 40 mV). Slower adaptation lowers sensory firing, and these are the
  weights that turn it into delay-line and error activity.
- `kappa_learn` in {3, 4.5, 6}: the gated learning multiplier (mechanism A only).
- `f_eta` in {1, 2}: a factor on the slow learning rate (shared by B and A).

That is 36 candidate sets. Nothing else changes, including the sensory network, the adaptation itself and every
analysis. B and A share the core constants, so B is re-tuned too (fairness).

**Sanity targets** (from `docs/PARAMETERS.md`; measured on an alternating A B sequence, 400 ms gaps, both adaptation
mechanisms on, mean over development seeds 100-104; test seeds 0-19 are never used here):

| # | Target | Measure | Range |
|---|---|---|---|
| S1 | An unpredicted tone drives PE+ to 60-100% of the sensory count | no-learning network (TE), B tones 11-30: PE+ / E | 0.6-1.0 |
| S2 | Delay cells fire about once per cell at their lag | TE, channel A, lags 4-19, spikes per cell per tone | 0.5-2.0 |
| S3 | Gate peak about 1 after the first error | A2b, gate maximum within 1 s of the first B | 0.5-1.5 |
| S4 | Gated learner predicts within about 3 exposures | A2b, first B exposure with PE+ below 50% of naive PE+ | 1-5 |
| S5 | A predicted tone gives mostly no error | A2b, PE+ at B tones 21-30 / naive PE+ | 0-0.4 |
| S6 | No large over-prediction | A2b, PE- at B tones 11-30 / naive PE+ | 0-0.3 |
| S7 | Slow learner learns over tens of exposures | B, 100 B tones, first exposure where the 5-tone running mean of PE+ falls below 50% of naive | 10-100 |

"Naive PE+" is the mean PE+ of the TE network on the first three B tones.
None of these uses an omission, an unexpected repeat or a post-oddball tone.

**Protocol check (done before this document was committed, at tau_w = 300 ms with the original constants).** First
version of the ranges: S4 1-4, S5 0-0.3. The original constants scored 4.6 and 0.33 there (5 of 7 met), so those two
ranges were stricter than the original "about 3 exposures" and "mostly no error". They were widened to 1-5 and 0-0.4,
after which the original constants meet 7 of 7 (S1 0.61, S2 0.88, S3 0.95, S4 4.6, S5 0.33, S6 0.11, S7 69.8). No run at
1000 or 3000 ms had been made at that point.

**Selection rule.** The candidate meeting the most targets wins; ties go to the smallest change from the original
constants (sum of absolute log-ratios of f_E, kappa/3 and f_eta). If the original constants already meet all targets
at the new tau_w, they are kept. Selection is automatic (`experiments/retune_slow_adaptation.py calibrate`).

## Tests (20 test seeds, same as the main run)
With the selected constants, at tau_w = 1000 ms (primary) and 3000 ms (secondary, same procedure):
N0, B, A1 and A2b on T2 unexpected repeat, T1 omission (v3 measure D-) and M1 tone after the odd one (continuation A).
Same sequences, measures and pass rules as `docs/PREREGISTRATION_TIER2.md` (T2: CI above 0 and at least 10% of the
regular response; T1: CI above 0 and mean at least 1 spike).

## Predictions
- R1: N0 keeps the adaptation signature on the repeat (repeat smaller than regular) and its omission contrast stays 0.
- R2: re-tuned A2b and A1 pass T2 and T1 at 1000 ms.
- R3: A2b's M1 rise stays above N0's.

## What each outcome means
- If R2 holds, the earlier failure was a calibration mismatch: the mechanism works with slower adaptation once its
  constants are set by the same rules. The paper's limitation is then replaced by this result.
- If R2 fails although the targets are met, the effects depend on fast adaptation, and the paper says so as a main limitation.
- If no candidate meets the targets, the circuit cannot be calibrated at that tau_w within this grid; that is reported.
Every outcome is reported.

Results: `results/retune_summary.md`.

---

## Results at tau_w = 1000 ms (added after the run)
Full tables: `results/retune_summary.md`.

**Calibration.** With the original constants, the circuit at 1000 ms misses three of the seven sanity targets: the
error cells respond too weakly (S1 0.51), and the gated learner is too slow (S4 9.0 exposures) and leaves too much error
at predicted tones (S5 0.56). So the untuned sensitivity run was out of its calibrated range. Twelve of the 36
candidates meet all seven targets (all with f_E 1.15 or 1.3). The rule selects the smallest change:
**f_E = 1.15, kappa = 3, f_eta = 1**. That is a 15% increase of the three sensory-driven weights
(E -> delay 22 -> 25.3 mV, E -> PE+ 18 -> 20.7 mV, E -> PE- 40 -> 46 mV); the learning constants are unchanged. Its
sanity scores: S1 0.72, S2 0.92, S3 1.21, S4 3.6, S5 0.39, S6 0.15, S7 62.8.

**Tests (20 test seeds, mean [95% CI], spikes).**

| net | unexpected repeat minus regular | omission D- | M1 post1 - pre1 | M1 minus N0 (paired) |
|---|---|---|---|---|
| N0 | -3.38 [-4.00, -2.76] | 0.00 | 3.51 [2.81, 4.20] | |
| B | -3.51 [-4.54, -2.47] | 0.05 [-0.03, 0.13] | 7.85 [6.20, 9.50] | 4.35 [2.71, 5.98] |
| A1 | +7.71 [3.61, 11.81] | 4.36 [2.69, 6.03] | 10.47 [7.83, 13.11] | 6.96 [4.07, 9.85] |
| A2b | +6.75 [2.95, 10.55] | 4.98 [3.09, 6.88] | 10.30 [7.76, 12.84] | 6.79 [4.16, 9.42] |

Regular-tone responses (for the 10% rule): N0 13.2, B 18.5, A1 9.7, A2b 9.9.

**Against the predictions.**
- R1 holds: N0 keeps the adaptation signature (repeat smaller) and its omission contrast is exactly 0.
- R2 holds: A1 and A2b pass the unexpected repeat (CI above 0, effect well above 10% of the regular response) and the
  omission test (CI above 0, mean above 1 spike). The effects are a little smaller than at 300 ms (repeat 6.75 vs
  7.57, omission 4.98 vs 5.97 for A2b) but well inside each other's intervals.
- R3 holds: A2b's M1 rise is above N0's (6.79 [4.16, 9.42]).
- B, re-tuned with the same core constants, still fails both tests at normal training, as at 300 ms.

**What this means.** The failure in the untuned sensitivity run was a calibration mismatch, not a dependence of the
mechanism on fast adaptation: when the circuit is set by the same sanity rules at tau_w = 1000 ms, the main Tier 2
results come back. Caveats: only the selected candidate was tested (11 others also met all targets); I had seen the
untuned results before designing this; the tests used the same 20 test seeds as before.
