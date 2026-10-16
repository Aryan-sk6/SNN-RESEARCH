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
