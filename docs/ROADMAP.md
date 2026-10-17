# Roadmap: which theories can be tested in simulation, and which stay open

Written 2026-10-17 from `docs/THEORY_NOTES.md` and `docs/PLAN.md`. Nothing here is a result. "Innovative" is
**not** claimed anywhere: the literature has not been checked for these specific ideas (see "Novelty check"
below). A theory counts as "done" when it has been tested in simulation, pre-registered first, and reported
honestly, including when it fails.

Key to status: **done** = run and reported, **running** = in progress, **planned** = designed, not built,
**open** = cannot be tested in this repo.

## Tier 1: the core (these make a defensible paper on their own)
| # | Experiment | Question | Status |
|---|---|---|---|
| 1 | Exp 1: adaptation alone (oddball, controls, SSA index, decomposition, omission check) | What does adaptation explain? | running |
| 2 | Exp 2: omission and ABABAA for adaptation-only, A (A1, A2b) and B (Wacongne-style) | What is the smallest mechanism to add? | planned |
| 3 | **Ablation of Mechanism A**: remove one part at a time (candidate generator, blank/hyperactive gain, learning, timing signal) and rerun Exp 2 | Which part is actually necessary? This is the "smallest mechanism" question made precise. | planned |
| 4 | **Robustness**: sample A's free parameters over wide ranges and report how often each test passes | Does the result survive without tuning? Reports the number of free parameters. | planned |

## Tier 2: the signature predictions of your theory (what makes it different from adaptation and from B)
| # | Experiment | Prediction (yours unless marked) | Status |
|---|---|---|---|
| 5 | M1 post-oddball tone | The tone right after the odd one is amplified beyond the small adaptation recovery rise | planned |
| 6 | M2 drop-off after the oddball | Sharper drop-off for A-after-B than in the first A-run; steepness A after B > B after B > C after B | planned |
| 7 | M3 candidate fit vs no fit | Inputs that fit a candidate settle sooner than inputs that fit none | planned |
| 8 | M5 continuations | C after B is stronger than A; random continuation decays exponentially to a baseline; short cycles are learned | planned |
| 9 | M6 error definition | Your definition (best guess minus event) vs mine (1 minus event): random context gives zero vs constant error | planned |
| 10 | One-shot learning (under "Aryan is confused") | After seeing old pattern, odd beep, next tone once and a >10 s gap, the next tone is predicted | planned, 4 open questions |
| 11 | **Omission fires the mismatch** | Omitted tone triggers the same mismatch and blank/hyperactive state; the tone after an omission is amplified | planned |
| 12 | **Timing dose-response** (your timing rule) | Omission/ABABAA response shrinks as timing jitter grows (0, 10, 30, 60%); and rises with the number of regular intervals first (1, 2, 4, 8). Also: does a timing shift after a regular rhythm count as an error (Wacongne says yes)? | planned |

## Tier 3: new experiments I would add (extensions; each is optional)
| # | Experiment | Why it is worth it | Status |
|---|---|---|---|
| 13 | **Ideal-observer benchmark** | Build a tiny Bayesian sequence learner and compare how many repeats the network needs to detect a cycle with how many an ideal observer needs. Search-level literature says human brain responses look ideal-observer-like, and detecting regularity in random input needs time. Cheap to build, strongly falsifiable. | planned |
| 14 | **Cycle length vs memory window** | Cycles of period 2, 3, 4, 6, 8 against the network's memory length. Prediction: there is a critical length beyond which the sequence looks "random" to the model. This gives "random" an operational meaning in your cycle idea (A B C B A B C B...). | planned |
| 15 | **Context uncertainty (precision)** | Oddball response as the surrounding context gets more random. Qualitative target from search-level literature: the same deviant gets a smaller response in a random context. Compare with and without an error-weight (precision) mechanism. | planned |
| 16 | **Energy accounting** | Define energy = total activity (spikes + synaptic current). Measure it over time after a surprise for fit vs no-fit, and under persistent unpredictability: does it escalate, saturate or recover? Tests your two-system claim in the only form the model allows. | planned |
| 17 | **Recovery time constant** | How long until the high-energy state relaxes after resolution? A single fixed constant is chosen once; here it is swept to show the effect does not depend on it. | planned |
| 18 | **Naive vs trained / development** | Network with no stored patterns vs pre-trained (M4), plus a learning-curve version: how much exposure before the mismatch response appears? Qualitative analogue of "newborn vs adult" only. | planned |
| 19 | Slower spike-frequency adaptation (sensitivity) | Exp 1 shows it explains almost nothing at tau_w = 300 ms. Report it also at 1000 and 3000 ms, labelled exploratory | waiting for owner |
| 20 | Fixed-interval oddball (Parras-style) | Comparability with Parras's isochronous design; additive to the cache | optional |
| 21 | Global context (AAAAB) | Does A, like Wacongne's model, stay blind to the global rule, or does its sequence memory pick it up? | optional |

## Tier 4: stays open (cannot be tested in this repo)
| Theory | Why it cannot be tested here | What would test it |
|---|---|---|
| Real brains literally lower "energy" like chemical systems | A simulation defines its own energy; it cannot show what the brain does | Metabolic or imaging data with sequence manipulations |
| Emotions (fear, shock, surprise) as energy surges or lack | Needs emotion measures, not spike counts | Physiology/behaviour experiments with surprise and arousal measures |
| Fetus inherits "training" from the mother via nerve connections | No developmental or maternal data exist in a toy network | Developmental neuroscience studies |
| Real post-oddball sensitisation and real one-shot learning | A simulation shows a mechanism is sufficient, not that the brain uses it | Existing or new neural recordings (single-unit, MEG/EEG) |
| E1 vs E2 as the brain's error rule | The model can implement both, but data are needed to choose | Recordings in random vs structured contexts with controls |
| The introspective observations | One trained human; a hypothesis generator, not evidence | A behavioural/EEG study (a possible follow-up paper) |
| Any claim about real brains or clinical use | This is a simplified toy model | Out of scope |

## Novelty check (not done yet)
For each Tier 2 and Tier 3 prediction, run a targeted literature search before the paper claims it is new,
for example: post-deviant response enhancement; mismatch-triggered plasticity or "labile state" after
errors; multiple-hypothesis or candidate-pattern accounts of the oddball; ideal-observer sequence models of
auditory regularity. Until then the README says only "a variant I am testing".

## Scope and honesty notes
- Seventeen-plus experiments is a lot for one paper. A strong paper usually has a tight core. Suggested
  split: **paper 1** = Tier 1 plus items 5, 7, 11, 12 (the omission/ABABAA story with your mechanism);
  **paper 2 or an extended repo** = the rest.
- The real work is **building Mechanism A**: candidate units, gating, plasticity and the timing detector in
  Brian2, three variants (A1, A2, A2b) plus the Wacongne-style B. The experiments after that are mostly
  protocol and analysis.
- Each experiment gets a short pre-registration before it runs, and the number of free parameters of A is
  reported next to every pass/fail.
- If A fails a test, that goes in the README.
