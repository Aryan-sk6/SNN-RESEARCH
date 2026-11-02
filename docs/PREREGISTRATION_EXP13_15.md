# Pre-registration: Experiments 13 (ideal-observer benchmark) and 15 (precision)

Written and committed before any run of these experiments. Roadmap items 13 and 15 (`docs/ROADMAP.md`). Both are
**exploratory follow-ups** to the Tier 2 results: I know those results, including that error in a random context did
not settle (M5) and that the omission and repeat tests pass for A2b. Code: `src/snn_oddball/exp13_15.py`,
`experiments/exp13_15.py`. All runs at the main settings (tau_w = 300 ms, original constants, time step 0.5 ms).
Development seeds 100-104 for calibration; test seeds 0-19 for every test; 95% t-intervals over seeds.

---

## Experiment 15: precision

**Why.** In Tier 2, total error in a random sequence never fell (A2b 26.6 then 26.8 per tone), which contradicted my
prediction that a network "accepts" randomness. Mechanism A has no way to know how predictable its input is. In
predictive coding this is the role of *precision*: errors are weighted by how reliable predictions have recently been.

**Mechanism (new component "P", added to A2b to make A2bP).** One slow variable Pi tracks recent error: it rises by
`a_prec` with every PE+ or PE- spike and decays with `tau_prec` = 10 s (fixed a priori: a "context" timescale of about
20 tones). Every input to the error cells is multiplied by the precision gain g = 1 / (1 + `k_prec` x Pi), so error
responses shrink when errors have been frequent. When the context is predictable, errors are rare, Pi stays low and
g stays near 1. With the component off nothing changes (all earlier results are unaffected; unit tests check this).

**Calibration (development seeds only).** Sanity targets, measured with A2bP:
- PT1: in a regular context (alternating A B, 60 tones), mean gain over the last 20 tones >= 0.8 (precision barely
  matters once the sequence is learned).
- PT2: in a random context (A, B, C, D uniformly, 100 tones), mean gain over the last 30 tones between 0.35 and 0.65.

Grid: `a_prec` in {0.001, 0.002, 0.005} x `k_prec` in {1, 2, 4} (9 sets). Selection: most targets met; ties go to the
random-context gain closest to 0.5. Neither target uses a test measure below.

**Tests (20 test seeds; A2b vs A2bP).**
1. **Random context settles (M5 repeated).** Random sequence of 200 tones over A, B, C, D (the M5/Tier 2 random block).
   Measure: total error per tone (PE+ and PE- of all channels, 0-180 ms), second half minus first half.
   - P15-1: for A2bP the change is negative (CI below 0), and more negative than for A2b (paired CI below 0).
     *Caveat stated now:* this is close to what the mechanism is built to do; it is a check that it works, not a
     surprising result.
2. **Same deviant, different contexts.** 200 tones; context either regular (A B A B ...) or random (uniform over
   A, B, C); probe tone D replaces about 10% of the tones from tone 40 on (at least 6 apart). D never appears otherwise,
   so its adaptation state is the same in both contexts. Measure: error (PE+ and PE-) on D's channel, 0-180 ms after
   each probe; also sensory E and the gain.
   - P15-2: for A2bP the D error is smaller in the random than in the regular context (paired CI below 0), and this
     context effect is more negative for A2bP than for A2b (paired CI below 0). This is the qualitative pattern the
     literature summaries describe (a deviant in an unpredictable context gets a smaller response; `docs/ROADMAP.md`
     item 15, search-level only).
3. **No harm.** A2bP on T2 unexpected repeat and T1 omission (v3), same rules as `docs/PREREGISTRATION_TIER2.md`.
   - P15-3: both pass.

---

## Experiment 13: ideal-observer benchmark

**Why.** To put the network's learning speed on an absolute scale: how close is it to the best possible learner for
these sequences?

**Observer.** A Bayesian first-order Markov learner over the four tones A, B, C, D: a symmetric Dirichlet(1) prior on
each row of the transition matrix, perfect memory, predicting each tone from the previous one. Its error on a tone is
1 - p(tone | previous), its surprise -log2 p. (Chosen because the network's delay line can only learn
previous-tone-to-next-tone timing; a higher-order or forgetting observer is not part of this test.) For learning the
alternation A B A B ... it needs **6 B exposures** to bring its error below 50% of its naive level (computed before
any network run; the naive level is 1 - 1/4).

**Tests (20 test seeds).**
1. **Learning speed.** On the same alternation, exposures for the network's PE+ at B to fall below 50% of its naive
   level (the S4 / S7 measures of `docs/RETUNE_SLOW_ADAPTATION.md`, original constants, tau_w = 300 ms): A2b and B.
   - P13-1: A2b needs at most twice the observer's exposures (<= 12); B needs more than 5 times (> 30).
2. **Tone by tone.** On the Tier 2 unexpected-repeat sequences (same sequences as T2), the observer's surprise for
   each tone vs the network's error on that tone's channel (PE+ and PE-, 0-180 ms; for N0, the sensory E response),
   tones 81-200 (the T2 analysis window). Spearman correlation per seed.
   - P13-2: positive for B and A2b (CI above 0); not positive for N0 (CI includes or is below 0), because adaptation
     gives a smaller response to the surprising repeated tone.
3. **Random context (descriptive).** Observer surprise in the first and second half of the random sequences of
   Experiment 15 test 1. Expectation: it stays near 2 bits (chance) in both halves, i.e. an ideal learner also does not
   reduce its surprise in a random sequence. This reframes the M5 result; it is reported, not tested.

---

Any prediction that fails is reported as failed. Results: `results/exp13_15_summary.md`.

---

## Results (added after the run; tables `results/exp13_15_summary.md`)

### Experiment 15: precision, failed

**Calibration.** No candidate met both targets. The precision gain came out almost the same in the regular and the
random context for every setting (for example 0.59 vs 0.57 for the selected a_prec = 0.005, k_prec = 4; 0.84 vs 0.74
for a_prec = 0.002, k_prec = 1). The rule selected a_prec = 0.005, k_prec = 4 (met PT2 only; random gain closest to 0.5).

| test | prediction | result | verdict |
|---|---|---|---|
| Random context, error change (2nd minus 1st half) | A2bP below 0, and below A2b | A2bP -0.33 [-0.40, -0.27]; A2b +0.26 [-1.22, 1.74]; difference -0.59 [-2.09, 0.90] | **Partly**: falls for A2bP, but not reliably more than A2b |
| Probe D, random minus regular context | A2bP below 0, and below A2b | A2bP -0.07 [-0.38, 0.24]; A2b +1.53 [0.65, 2.41]; difference -1.59 [-2.44, -0.75] | **Not supported** (A2bP shows no context effect) |
| No harm (T2 repeat, T1 omission) | both pass | repeat -3.88 [-4.47, -3.29]; omission 0.00 | **Fails badly**: both main results are lost |

**Why.** With a single global precision variable, the feedback loop sets its own level. Low gain means fewer error
spikes, which means lower Pi, so every context ends up at about the same error rate (A2bP context error 1.61 per tone
in the regular context, 1.68 in the random one, against 4.67 and 23.76 for A2b). The mechanism acts as global gain
control: it silences error everywhere, including the errors the network needs to learn the alternation and to signal
the repeat and the omission. Context-specific precision needs something this version lacks, for example a precision
estimate per channel or one driven by how reliable predictions have been rather than by raw error counts. That is a
redesign, not a parameter change, and is left for future work. Unexpected side observation: without precision, A2b's
error to the probe D is *larger* in the random context (+1.53), the opposite of the qualitative literature pattern.

### Experiment 13: ideal observer, supported

| test | prediction | result | verdict |
|---|---|---|---|
| Exposures to learn the alternation | A2b <= 12; B > 30 (observer: 6) | A2b 5.10 [4.23, 5.97] (0.85 x observer); B 49.4 [38.3, 60.5] (8.2 x; 1 seed censored at 100) | **Supported** |
| Tone-by-tone error vs observer surprise (Spearman r) | B, A2b above 0; N0 not | B 0.15 [0.09, 0.22]; A2b 0.16 [0.09, 0.23]; N0 -0.17 [-0.26, -0.09] | **Supported** (correlations weak) |
| Observer surprise in a random context (descriptive) | stays near 2 bits | 2.11 then 2.05 bits | As expected |

- A2b is slightly *faster* than this observer. That is not a contradiction: the observer starts with no idea which of
  four tones comes next, whereas the gate's candidates build in a bias towards "the tone repeats" and "the earlier tone
  returns", which happens to fit an alternation. A2b is fast because of that built-in bias, not because it beats
  Bayesian inference. B is about 8 times slower than the observer.
- The correlations are positive but weak: the network's error follows the observer's surprise in direction, not
  closely tone by tone. Adaptation alone correlates negatively, as expected.
- An ideal learner also does not reduce its surprise in a random sequence (about 2 bits throughout). So "error does
  not settle in random input" (M5) is partly what any learner would do; Experiment 9 shows the network's specific
  problem is over-confident guesses, which an ideal learner does not make.
