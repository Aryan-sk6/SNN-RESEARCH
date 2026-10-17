# Pre-registration: Tier 2 experiments (written before any Tier 2 result was seen)

Status: committed before running `experiments/exp2_*.py`. Changes after the first run are logged at the bottom.
Design background: `docs/EXP2_DESIGN.md`, `docs/PLAN.md` (M1-M6), `docs/THEORY_NOTES.md`.

## What was built, and what was calibrated
Prediction circuit (`src/snn_oddball/predictive.py`): per predictive channel, a tapped delay line (T), positive and
negative error populations (E), learned prediction cells (L), and for mechanism A a mismatch gate (G) that
(i) multiplies the learning rate, (ii) raises the sensory gain (sensitisation), and (iii) opens candidate
predictions (C): the tone that just erred repeats, the earlier tone returns, something new appears.
- **N0** adaptation only (spike-frequency adaptation + depression, condition `both`), no predictive layers.
- **B** core circuit T+E+L with the slow learning rate. This is a *simplified, loosely Wacongne-style* predictive
  coding network, not a faithful replication (LIF not Izhikevich cells, smaller populations, tapped delay line
  instead of a synfire chain, no NMDA currents). Every difference is in `docs/PARAMETERS.md`.
- **A1** B + gate G (fast learning, sensitisation) with replacement of old predictions.
- **A2b** B + gate G + candidates C (keeps old predictions).
Calibration (done before this document, against *sanity targets*, never against a test below): the error cells
respond to an unpredicted tone with about 60-100% of the sensory spike count; the delay cells fire about once per
cell at the right lag; the slow learner learns an alternating pair over tens of exposures; the gated learner within
about 3 exposures without large over-prediction. All values and the calibration log are in `docs/PARAMETERS.md`.
**Time step 0.5 ms** is used for every Tier 2 run (all networks including N0) for speed.

## Common protocol
Tones: A = channel 3, B = channel 6, C = channel 8, D = channel 1. Tone 50 ms, SOA 450 ms (ISI 400 ms) unless a
test says otherwise. Responses: baseline-corrected spike count in 0-180 ms after onset, baseline 75 ms before
(the Experiment 1 measure), summed over the sensory cells (E), positive-error (PE+) and negative-error (PE-) cells
of the channel ("R"); E alone, PE+ and PE- are also reported. N0 has E only. 20 seeds (5 in `--quick`), mean and
95% t-interval over seeds, paired within seed. A seed fixes the network and noise. NaNs are counted.
**Pass rule used wherever a test asks for a response:** the 95% CI excludes 0 **and** the effect is at least 10%
of the reference response. **Important caveat for A:** sensitisation and one-shot learning are assumed by
mechanism A, so M1, M2 and part of M3 test whether the implemented hypothesis behaves as designed, not whether
real brains do this. They also test whether the effect is distinguishable from the adaptation baseline.

## The experiments
**T1 Omission (fixed interval).** Tone A repeated, 160 slots, 20% omitted (never in the first 10, never
adjacent). Measure R on A's channel at omitted slots (slots >= 60) minus baseline. Pass = response above baseline
per the rule. Secondary: PE- alone; also the tone right after an omission versus a tone after a tone (post-omission
sensitisation, "omission starts the mismatch").
**T2 Unexpected repeat.** Alternating A B A B ..., 200 slots, 10% of the B slots replaced by A (>= 6 alternations
between). Measure R(A) on the repeated A versus the regular A (an A after a B), events at slots >= 80. Pass =
repeated larger than regular per the rule. The adaptation-only expectation is *smaller*; a significantly smaller
response is reported as the adaptation signature.
**M1 Post-oddball tone.** Episodes: A x n_pre (n_pre uniform 6-9), one B, then a continuation of 8 tones, then 3 s of silence (3 s is the gap before the next episode); 10 episodes.
R of the first A after the B versus the last A before the B; difference compared between networks (difference of
differences against N0). Prediction (owner, A2b): clearly larger than N0's small recovery rise. Pass = A2b minus N0
satisfies the pass rule.
**M2 Drop-off after the odd one.** Same episodes with continuation X x 8 where X = A, B or C (separate blocks).
Per seed: slope of log(R + 1) against position over positions 1-5 after the B, and the
same slope over positions 1-5 of the initial A run at the start of each episode. Prediction (owner, A2b): the slope
(steeper = more negative) after the B is steeper than the initial A run, and the order of steepness is
A after B > B after B > C after B. N0 is the baseline.
**M3 Candidate fit versus no fit.** From the M2 blocks: total error (PE+ plus PE- over all four channels) in 0-180 ms
at the first post-B position, for X = A (the earlier tone returns), B (repeats), C (new, fits only the generic
"something new" candidate), and the gate level 1 s after the first post-B onset. Prediction (A2b): total error and gate are
lower after A and B than after C. Reported for A2b only (N0 and B have no gate).
**M5 Continuations.** Same episodes with continuations of length 8: (a) A (old regime), (b) B (new regime),
(c) cycle C A B C A B..., (d) cycle C B A B ... (period 4), (e) random among {A,B,C,D}. R per position;
exponential fit R(pos) = r_inf + (r_1 - r_inf) exp(-lambda (pos-1)) per seed (fits that fail are counted, never
silently dropped); compare r_inf and lambda across continuation types and with N0 and B. Predictions (owner): C right
after the B is stronger than A; random continuation decays toward a baseline; short cycles are learned faster than
random (lower late error). Whether r_inf is 0 or above 0 is reported with CIs, together with the
owner's error definition (best guess minus event, zero for random) and the alternative (constant above 0).
**M6 Error definition and the Parras-style decomposition.** (i) Oddball (A std, B dev... as Experiment 1: standard
channel 3, deviant 6, p = 0.1, 200 trials), many-standards control (10 tones is not available in the predictive
channels, so 4 tones A,B,C,D with p = 0.25 deviant; both oddball p = 0.25 and control matched) and cascade control, for B
and A2b: iMM, iRS, iPE as in Experiment 1. Parras reports iPE > 0 in cortex. (ii) A fully random block
(200 slots, tones uniform over A,B,C,D): mean error per slot over slots >= 100. Reported against the three
definitions (`docs/THEORY_NOTES.md` 8b). No single pass/fail; it adjudicates descriptively.
**One-shot learning.** The pair A then B (SOA 450 ms) presented 12 times separated by 8 s of silence (longer than
every adaptation, gate and eligibility time constant). Per pair: R(B), PE+ at B, and P (prediction) spikes in the 100
ms before B. Learning = R(B) or PE+ falls and anticipatory P rises. Report the pair index at which PE+ at B first
falls below 50% of the first pair's, per seed (censored at 12, never dropped), for N0 (no change expected), B, A1,
A2b; and the PE+ at the second pair as a fraction of the first.
**Timing dose-response.** (i) Omission as T1 but with ISI jitter j in {0, 0.1, 0.3, 0.6} (ISI uniform 400 x (1 +/- j)),
reported separately for each j, never pooled with the fixed-interval result. Prediction (owner): omission response
shrinks as j grows. (ii) Regularity buildup: episodes of n regular tones then one omitted slot, n in {1,2,4,8},
5 s silence between episodes, order randomised, 6 episodes per n (reduced from 12 before any run, for compute). Prediction (owner): omission response rises
with n. A control block checks whether a timing *shift* after a regular rhythm (one tone arriving 150 ms late) produces
a response (Wacongne et al. predict yes).
**Ablation (roadmap item 3).** For the T1 and T2 tests, all 12 valid subsets of {T, E, L, G, C} (G needs E and L, C needs
G); smallest subset passing both is the answer to the smallest-mechanism question; same count of free parameters
reported with each.
**Robustness.** 40 random draws of A2b's constants (log-uniform within a factor of 3 around the default for: gate gain,
sensitisation, tau_gate, kappa, candidate weights), one seed each, T1 and T2: fraction passing each and both.

## Predictions by network (stated before the runs)
- N0: T1 null, T2 smaller-repeat (adaptation signature), M1 small rise, no one-shot learning.
- B: T1 and T2 pass only after enough learning (late slots); one-shot slow; no sensitisation.
- A1, A2b: T1 and T2 pass earlier; sensitisation after the odd one (by design); one-shot within a few exposures.
Where a prediction fails, it is reported as failed.

## Not done in this document
Roadmap items 13-26 (ideal observer, cycle length vs memory, context uncertainty, energy accounting, naive vs trained,
leak and overlap) come after Tier 2.

## Change log after the first run

### v1 quick run (5 seeds, short sequences) and what it exposed
The v1 quick results are archived in `results/archive/tier2_summary_quick_v1.*`. Headline (preliminary, 5 seeds): omission
response was small (A2b 2.25 [0.35, 4.15] spikes, 13% of a tone; B and N0 about 0); unexpected repeat passed only for
A1; one-shot learning, regularity buildup and jitter dose-response were not distinguishable from null; no ablation subset
passed both tests; M1 (tone after the odd one) was reproduced by A2b **and** by B. Diagnosing why B's negative error was
exactly zero showed the following **faults in my implementation, not changes to a hypothesis**:
1. **Acausal self-prediction.** The delay cell at lag 0 (firing with the tone itself) was allowed to learn to predict
   the same tone, giving a fake cancellation and weakening the true timed prediction, in every same-channel test
   (omission, A-runs). Fix: delay lags below `min_lag = 2` (100 ms) do not connect to the prediction cells (and the T-off
   trace is delayed by the same amount).
2. **Wrong window for anticipatory activity.** Prediction spikes arrive after tone onset (response latency), so the
   100 ms *before* onset missed them. Fix: window -100 to +180 ms around the expected onset (prediction cells have no
   direct sensory drive, so this is still predictive activity).
3. **Aggregation artifact:** for N0 (no error cells) the one-shot "first pair below half" read 1; now not applicable.
4. **Measurement added:** sensory-only (E) response before the odd tone, so M1's sensitisation can be separated from
   ordinary prediction error.
Changes 1-2 were made after seeing the v1 quick results. They are corrections of implementation flaws found by
inspecting learned weights, not adjustments of a threshold or a gate constant. Gate and candidate constants, the learning
multiplier and all pass rules are **unchanged**. Re-calibration against the sanity targets was repeated on development seeds
(100-104) and a different tone, never on the test seeds.
5. **Causality margin:** the first fix (`min_lag` 2) was insufficient because the tone's own response lasts about 180 ms
   and the lag-2 delay cell (100 ms) still overlapped it; the rule is now `min_lag = 4` (200 ms), derived from the
   measurement window.
6. **Fairness check added (not a change to any test):** the slow core B was trained for only 160 slots whereas Wacongne
   et al. trained on about 1500 pairs. A *long-training* suite (600 slots, analysed from slot 400) is added for B and A2b for
   omission and the unexpected repeat. It is reported alongside, not instead of, the pre-registered 160/200-slot tests.
7. **Secondary omission measure:** because predictions start before the tone, the pre-registered baseline (75 ms before)
   contains anticipatory negative-error spikes. The primary measure is unchanged; a secondary measure uses the 0-180 ms
   raw PE- count minus a quiet baseline (-250 to -175 ms). The v1 negative results (one-shot, buildup, no passing ablation
subset) are reported as v1 results and are not erased.
