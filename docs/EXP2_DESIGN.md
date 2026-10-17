# Experiment 2 and ablation: design draft (NOT yet pre-registered)

Status: **draft for the owner's review.** Becomes `docs/PREREGISTRATION_EXP2.md` once approved and before
any Experiment 2 run. Undecided items are marked **[OWNER]**. Nothing here has been run.

## Question
What is the smallest mechanism added to adaptation that gives (a) a response to a **missing** tone and
(b) a response to an **unexpected repeat** in an alternating sequence (A B A B A B A **A**)? These are the
tests where adaptation alone is said to fail (Wacongne et al. 2012, `docs/PRIOR_ART.md` entry 1).

## Networks compared (same seeds, same sequences)
| Label | What it is |
|---|---|
| N0 | adaptation only (condition `both`, the most favourable to adaptation; `std` alone also reported) |
| A1 | N0 + owner's mechanism, direct re-prediction version |
| A2b | N0 + owner's mechanism, hyperactive many-candidate version (the blank state A2 is an ablation of it) |
| B | N0 + simplified Wacongne-style predictive coding (delay-line memory, learned transitions, prediction-error units). Labelled **a replication of their approach**, not the owner's idea. Every simplification will be listed (they use Izhikevich neurons, NMDA currents, 40-cell populations, 400+100 delay-line neurons; ours are LIF and smaller). |

## Mechanism A as it will be built (proposal, **[OWNER]** to approve)
Components (each is a switch for the ablation):
1. **Timing expectation (T):** a rhythm-locked signal that raises the prediction for the next tone at the
   expected onset. Learned from the last few intervals; weak or absent if intervals are irregular.
2. **Error populations (E):** per channel a **positive-error** and a **negative-error** population (spike
   counts), each a subtractive comparison between the input and the prediction. Negative error carries
   the omission response. (Brain-grounded design: `docs/PRIOR_ART.md` entry 12.)
3. **Mismatch gate (G):** a large error opens a high-gain, high-plasticity window (decays with a fixed
   time constant).
4. **Candidate set (C):** during the window several candidate continuations are active at once (repeat of
   the deviant, return to old pattern, new tone, cycle built from items seen); the next input is compared
   with all of them; a fitting candidate wins and the window closes, no fit keeps it open.
5. **One-shot learning (L):** the winning candidate, together with the preceding context, is stored.
   A1 = G + L with a single candidate (immediate replacement). A2b = G + C + L.
Parameters of A are fixed once from plausible ranges before Experiment 2 runs, listed in `docs/PARAMETERS.md`,
**with a count of free parameters**, and never changed after seeing results.

## Test 1: omission (fixed interval primary)
- Sequence: tone A (channel 6), SOA 450 ms (50 ms pulse + 400 ms), 200 slots, 20% omitted (never in the
  first 10, never adjacent). Same as the Experiment 1 omission block, so N0 is already measured.
- Measure: baseline-corrected spike count, 0-180 ms after the expected onset, on the **expected** channel
  and on the **negative-error population** where it exists. Baseline: 75 ms before.
- **Pass** = omission response above baseline with the 95% CI over 20 seeds excluding 0 **and** at least
  10% of the response to a present tone (effect floor fixed now to avoid trivial passes). Report the
  effect size and the CI half-width, not only pass/fail.
- Second version (Wacongne-style): pairs A-B 150 ms apart, pairs 500 ms apart, 10% omit B; control block
  has A alone. Both comparisons reported.
- **Timing dose-response:** jitter 0, 10, 30, 60% of the SOA; and regularity buildup, n = 1, 2, 4, 8 regular
  tones before an omission, with a >= 3 s gap between runs. Owner's rule: no meaningful omission response
  when timing is irregular. Also record whether a timing *shift* after a regular rhythm produces a response
  (Wacongne predicts it does).
- Jittered runs are reported separately and are never pooled with the fixed-interval result.

## Test 2: unexpected repeat in an alternating sequence
- Sequence: A and B alternate (channels 3 and 6), fixed SOA 450 ms, 400 slots; 10% of the B slots are replaced
  by A, never fewer than 6 alternations between replacements.
- Measure: response of channel A on the **repeated A** vs on the regular A (the A that follows a B), both
  baseline-corrected, 0-180 ms.
- **Pass** = repeated-A response **larger** than the regular-A response, 95% CI excluding 0, effect at least
  10% of the regular-A response. The adaptation-only expectation is **smaller** (the previous A was one slot
  earlier, so the A cells are more adapted); a significantly smaller response is reported as the
  adaptation signature, not as a failure of the test setup.
- Control for the ABABAA effect not being explained by the tone **pair**: also run pairs separated by > 10 s
  (Wacongne's habituation test), so that adaptation cannot carry over.

## Statistics and bookkeeping
- 20 seeds (5 quick); mean and 95% t-interval; NaN seeds counted. Paired within seed.
- One table per mechanism: pass/fail of each test with effect size and CI. Passing is reported next to the
  number of free parameters of that mechanism.
- Development vs test: any parameter calibration uses seeds 100-104 and a different tone pair; the test uses
  seeds 0-19 and the tone pair above. Calibration targets are sanity targets (adaptation behaviour, spontaneous
  rate), never the pass/fail tests.

## Ablation (roadmap item 3): what is the smallest mechanism?
- Components: T, E, G, C, L (5 switches) plus the full A2b. Run all **32 subsets** on Tests 1 and 2.
- Report which subsets pass which test; the **smallest subset that passes both** is the answer to the
  question; also report which single removals break which test.
- Where a component is meaningless without another (for example C without G), the subset is skipped and listed.
- Same ablation for B (delay line, learned transitions, error units), so both mechanisms get the same treatment.
- Cost estimate: 32 subsets x 2 tests x 20 seeds, shorter sequences (200 slots), roughly a few hours on 4 cores
  once the mechanism is built.

## Robustness (roadmap item 4)
Random sampling of A's free parameters (log-uniform over a 10x range around the default): fraction of
samples that pass Test 1, Test 2 and both.

## Not in this experiment
M1-M6, one-shot test, cycle experiments and the ideal-observer benchmark (`docs/PLAN.md`, `docs/ROADMAP.md`).
They use the same Mechanism A build and come after it.

## Open items for the owner
1. **[OWNER]** Approve the component list T, E, G, C, L, and the brain-grounded error design (two signed
   error populations, spike counts).
2. **[OWNER]** The window time constant and candidate list are my choices; fine to fix them once?
3. **[OWNER]** Confirm "pass" needs both significance and the 10% effect floor.
