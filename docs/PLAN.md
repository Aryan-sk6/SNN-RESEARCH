# Plan and open doubts

Status: Step 0 (prior art) is drafted at abstract level only. Waiting for review before any modelling.

## Plan

| Stage | Output | Gate |
|---|---|---|
| 0. Prior art | `docs/PRIOR_ART.md` | **Stop for your review** (now) |
| 1. Network + tests | `src/snn_oddball/` (params, network, stimuli, analysis, stats), `tests/`, pinned env, `make setup` | — |
| 2. Experiment 1 | `experiments/exp1_adaptation.py --quick`, figure in `results/`, README results section | **Ask before Exp 2** |
| 3. Experiment 2 | `experiments/exp2_minimal_mechanism.py`, Mechanism B (replication), Mechanism A only if you supply it | — |
| 4. Docs | README, ARCHITECTURE.md, LICENSE (MIT) | — |

Pins, from PyPI today: Python ≥ 3.11, brian2 2.10.1, numpy, scipy, matplotlib and
pytest pinned to exact versions in `requirements.txt`. These are checked to
install together before pinning.

Statistics: every condition runs over 20 seeds (5 with `--quick`). Each seed
gets a mean and a 95% CI, with a t-interval across seeds (n is small, so I use
the t-distribution, not z). The test, window and pass/fail criteria for each
experiment are written into `docs/PREREGISTRATION.md` **before** the
experiment is run. Any later change is logged with its reason.

## Doubts: decisions I need from you (or will default as stated)

1. **Literature access (blocking).** I could not read any full text (see
   PRIOR_ART.md). Mechanism B in particular needs the Wacongne 2012 Methods.
   One secondary source says that model uses Izhikevich neurons, not LIF.
2. **"Review by Parras et al. (2017)".** Parras 2017 (Nat Commun) is an
   empirical paper. The methodology review is Carbajal & Malmierca 2018. Which
   one did you mean? I've included both.
3. **Mechanism A is the empty placeholder.** As instructed, I will skip it and
   say so in the README unless you send the description.
4. **Probability mismatch between oddball and controls.** You specified an
   80/20 oddball. With 10 tones, the many-standards and cascade controls give
   the target a probability of 10%, not 20%. Comparing a 20% deviant with a
   10% control mixes probability with context. Default: run the decomposition
   at a matched 10% deviant probability, report 20% too, and include both in
   the probability sweep. Alternative: use 5-tone controls at 20%.
5. **Frequency gap needs tonotopic overlap.** If each tone drives only its
   own disjoint group, the frequency gap cannot matter. Default: each tone
   drives its own group fully and neighbouring groups with a Gaussian fall-off
   (width fixed a priori and documented, not tuned). The gap sweep is then
   meaningful.
6. **ISI vs SOA, and jitter.** Default: ISI is the silent interval between
   pulse offset and next onset, drawn uniformly from 300–500 ms. For
   *omission*, jitter blurs when a tone is "due". The literature I could
   see uses rhythmic sequences, so in Exp 2 I'd use a fixed SOA for omission
   and ABAB trials, and report the jittered version as a secondary result.
7. **Response measure.** Default: spike count of the excitatory group tuned to
   the target tone, 0–100 ms after onset, minus the same group's count in the
   100 ms before onset (the baseline window). Background Poisson drive gives
   a non-zero spontaneous rate, so "no response" is measurable and not
   trivially zero.
8. **SSA index (d − s)/(d + s)** is undefined when d + s = 0. Default: report
   NaN and count such seeds, never silently set them to 0.
9. **Normalised iMM/iRS/iPE.** Parras's exact normalisation is unverified.
   Default: report the raw-difference decomposition (exact arithmetic,
   unit-tested). Add the normalised version only once I've read the formula.
10. **ABABAA pass criterion.** Adaptation predicts that the repeated A is
    *smaller* than an A in the alternating context. "Pass" means the
    repeated-A response is *larger* than the alternating-A response, with the
    95% CI of the difference excluding 0. **Omission pass** means the
    omission-window response exceeds the baseline window, with the CI
    excluding 0. These are fixed before running.
11. **Repo name.** The GitHub repo is `snnresearch`. Default: the repo root
    *is* "snn-oddball" (package `snn_oddball`, README title snn-oddball).
    The repo itself is not renamed.
12. **Publishing.** I commit locally and won't push until you say so. Pushing
    publishes under your name.

---

## Decisions recorded 2026-10-17

- **Defaults:** user replied "yes run it as that". Interpreted as approval of the
  defaults in doubts 4-12 above. Not yet confirmed explicitly per item.
- **Timing (user's rule):** A regular rhythm is required before a missed or
  displaced tone can count as a prediction-error event. If successive
  intervals vary arbitrarily, the next onset is not predictable and no error
  should be expected.
  - Primary Exp 2 runs (omission, ABABAA): **fixed interval**.
  - Secondary run: **random intervals**, reported separately and labelled as
    limited. It is never pooled with the fixed-interval result.
  - Proposed addition (needs user OK): vary the number of regular intervals
    before the omission/repeat (1, 2, 4, 8) to test the buildup idea.
- **Mechanism A:** still not supplied. The timing remark above may be the
  hypothesis, but that is unconfirmed. Mechanism A stays skipped until the user
  describes it.
- **Papers requested from user:** Parras 2017, Wacongne 2012, Carbajal &
  Malmierca 2018, Ruhnau 2012 (optional: Eissa 2025, Mill 2011, Yarden &
  Nelken 2017). Prior art stays at ABSTRACT level until they are in
  `docs/papers/`.

---

## Mechanism A: rough description from the user (2026-10-17), NOT YET SPECIFIED

User's description (pasted restatement, accepted as the rough idea):

    Sensory input arrives -> does not match current prediction
      -> MMN fires, carrying the sensory pattern that caused the mismatch
      -> that combined signal is used immediately to form an updated expectation
      -> the new expectation replaces the old one (instantly)
      -> the next similar input is already expected
    i.e. MMN = error signal + context carrier + re-prediction trigger in one
    event; the mismatch spike burst carries the input pattern, which becomes
    the new prediction template via STDP.

Status: working label "input-carrying error with one-shot re-prediction".
Making no novelty claim; whether the literature already contains this is
unverified (see PRIOR_ART.md, Wacongne 2012 learns predictions with STDP).

Open questions before implementation (asked of the user):
1. Omission: the error carries sensory input, so with no input nothing fires.
   As described, A is expected to fail omission by construction. Either report
   that result, or add an input-free, timing-driven component (the fixed
   interval rule). Which is intended?
2. "Replace the old expectation" with the last tone would flag every tone in
   ABAB as an error. Plan: learn transitions (after A expect B), one-shot,
   from the surprising input. Needs confirmation.
3. Learning rule, time constants and how the "payload" is wired are
   unspecified. Will be chosen once, documented, and not tuned to results.

Prediction recorded in advance: A should pass ABABAA only if it learns
transitions, and should fail omission unless a timing component is added.

---

## Update 2026-10-17: Parras 2017 read

- Normalisation resolved: Euclidean norm of (DEV, STD, CTR) per tone, then iMM = DEV-STD,
  iRS = CTR-STD, iPE = DEV-CTR (all in [-1, 1]). Report these *and* the raw-difference version.
- Oddball in the source is 90/10, isochronous (about 250-333 ms), 400 tones, 10 tones, 40 presentations
  of the target per sequence. Response window 0-180 ms, baseline 75 ms. We keep our own windows
  (0-100 ms, 100 ms baseline) unless the user prefers Parras's. Needs a decision: **default to Parras's
  windows** for comparability.
- Doubt 4 (matched 10% probability) is now supported by the source.

---

## Mechanism A, revised by the user (2026-10-17)

Corrections to the earlier rough description:
- Learned transitions **add to** the old expectation; they do not replace it.
- An "expectation" can be a **pattern or series**, not a single tone (needs a multi-tone sequence memory).
- Hypothesis to test **first** (A2): on a mismatch the network does **not** form a new prediction directly.
  It enters a **blank, labile state**: the previous expectation is still faintly remembered, no new
  prediction can form, activity is high, any input is strongly amplified, and connection formation is
  strong. The **next input**, together with the previous expectation and the oddball, is used to form the
  new prediction.
- **A1** (direct re-prediction, from the earlier description) is kept as a comparison.
- Wiring and parameters: no user preference. Choose once, document, do not tune to results.

Predictions recorded in advance (testable signatures, to be confirmed or refuted):
1. The tone immediately after an oddball is amplified under A2 (adaptation alone predicts no such effect).
2. One-shot learning: after the sequence old-pattern, oddball, next tone has occurred once, a repeat of it
   is predicted and gives a smaller response.
3. The sensitised state decays if no input arrives (decay constant chosen once, not tuned).

Open question for the user: should the blank state also start after an **omission** (expected tone absent),
or only after a wrong tone? Omission detection itself still needs a timing-driven expectation signal.

---

## Decision 2026-10-17: omission starts the mismatch mechanism

User confirmed: the "no input" omission case **should fire the mismatch mechanism** (and so start the
A2 blank, sensitised state). Consequences recorded in advance:
- Mechanism A needs an **input-free mismatch detector**: a timing-driven expectation that, at the expected
  onset, compares "expected tone" with "no input". Its parameters are chosen once and documented.
- Prediction: under A2 the tone **after an omission** is sensitised, like the tone after an oddball.
- Adaptation-only and the Wacongne-style replication (B) are unaffected: they get no such detector other
  than what B's own design contains.

---

## Added 2026-10-17: new measures for Experiment 2 (fixed before any Experiment 2 run)

Hypotheses behind them are in `docs/THEORY_NOTES.md`. Every measure below is also taken on the
**adaptation-only** network so it has a baseline.

### M1. Post-oddball tone
Sequence A A A A A **B** A A A A A (deviant B). The tone right after the deviant is excluded from the
Experiment 1 analysis (as in Parras and Wacongne); here it is the object of study.
- Measure: response to the first A after the B, compared with (i) the last A before the B and (ii) an A
  several tones after the B.
- Adaptation-only expectation: a small **rise** (B adds waiting time, so the A cells recover a bit), not a
  large one. A2/A2b has to exceed that baseline.
- A2/A2b prediction: a clear amplification beyond that baseline.

### M2. Drop-off after the deviant
Trial-by-trial response curve in the repeated run after the deviant, for three continuations:
A A A A A B **A A A...**, A A A A A B **B B B...**, A A A A A B **C C C...**.
- A2b prediction (from the owner): sharper drop-off for A-after-B than in the initial A run; steepness
  ordered A after B > B after B > C after B.
- Adaptation-only prediction: no special sharpening for A-after-B; C restarts a normal drop curve.
- Also record the **initial** A-run curve. The adaptation functions in the model are exponential and
  saturating (drop front-loaded, then flattening), not linear. Measured earlier for the repeated tone
  (3 seeds, short probe): depression 22 -> 17 -> 16 spikes (about 85% of the fall by tones 2-3); spike-frequency
  adaptation 24 -> 21 -> 23 (small). The full per-trial curve will be saved and plotted.

### M3. Candidate-fit vs no-fit (A2b)
After the deviant B, the next input is one of: the old tone A, the deviant again (B), a new tone C, or a
tone outside any plausible candidate. Prediction: inputs that fit a candidate settle sooner (smaller or
shorter response) than inputs that fit none (larger or longer response).

### M4. Naive vs pre-trained network
Run M1-M3 in an untrained network and in one pre-trained on varied sequences. Reported as a factor, with
the pre-training protocol fixed first.

---

## Aryan is confused

Separate from the plan above. Items the owner is unsure about, kept apart on purpose.

### One-shot-learning test (what it is, and what is still unsettled)
Show the network "old pattern, odd beep, next tone" exactly **once**. Wait a long silence (> 10 s, longer
than any adaptation lasts; Wacongne et al. used > 10 s gaps for the same reason). Then show the pattern up to
the odd beep again.
- If it learned in one shot, the next tone should now be predicted: **smaller response** to it, or
  **anticipatory activity** before it arrives.
- Adaptation alone cannot fake this once the gap exceeds its time constants.

Unsettled (needs the owner's decision before it is run):
1. What counts as "learned": a smaller response to the next tone, anticipatory firing, or both?
2. The silence must be longer than every adaptation time constant. How long is long enough? (> 10 s is
   the starting proposal.)
3. It needs a memory of the recent pattern, which the plain adaptation network does not have. Whether that
   belongs inside Mechanism A or is a separate component is undecided.
4. Compared with Wacongne's STDP model, which learns over many trials, "one shot" is a strong claim and may
   fail. If it fails, that is reported as a result.
