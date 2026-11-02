# Pre-registration: Experiment 9, two definitions of prediction error (roadmap item 9, plan M6)

Written and committed before any run. Exploratory follow-up: the Tier 2 results are known to me.
Code: `src/snn_oddball/exp9.py`, `experiments/exp9_error_definitions.py`.

## Question
My plan (`docs/PLAN.md`, M6) contrasts two definitions of prediction error:
- **E1, subtractive:** error = 1 - p(event). A flat prediction (no idea what comes next) gives a constant error
  (0.75 with four tones).
- **E2, mine:** error = p(top guess) - p(event). A flat prediction gives **zero** error, and so does a correct top guess;
  only a confident wrong guess gives a large error.

The planned prediction: in a random sequence, E2 gives an error baseline near zero (randomness is "accepted"),
whereas E1 stays constant above zero.

## Method
The network's error cells count spikes, which is neither definition, so both are computed as **readouts** of the
same networks; the network itself is unchanged. The network's prediction before each tone is read from its
prediction cells: spike counts of the four predictive channels in the 100 ms before the onset, normalised to a
probability p_hat. If the prediction cells are silent (fewer than 1 spike in total), p_hat is flat (1/4 each).
The same two quantities are also computed for the ideal Bayesian observer of Experiment 13 as a reference.

Networks: B and A2b, original constants, tau_w = 300 ms, 20 test seeds. Sequences (the same ones as earlier tests,
same generators and seeds):
1. random context: 200 tones uniformly over A, B, C, D; tones 101-200 analysed;
2. the Tier 2 unexpected-repeat sequence (A B A B ... with 10% of B replaced by A); repeated A vs regular A, from tone 81.

## Predictions (for A2b; B and the observer are reported alongside)
- P9-1: in the random context, mean E2 is near zero: 95% CI upper bound below 0.1.
- P9-2: in the random context, mean E1 is clearly above zero: 95% CI lower bound above 0.5.
- P9-3: both definitions give a larger error for the repeated A than for the regular A (paired CI above 0).
- Caveat stated now: a silent prediction layer gives a flat p_hat and therefore E2 = 0 by construction. The share of
  tones with silent prediction cells is reported; P9-1 counts as informative only if that share is below 50% in the
  random context.

Any prediction that fails is reported as failed. Results: `results/exp9_summary.md`.
