# Pre-registration: Experiment 1 (written before any Experiment 1 result was seen)

Status: committed before running `experiments/exp1_adaptation.py`. Changes after the first full run are
listed at the bottom with their reasons. A pre-registration here means "the analysis was fixed first",
not that the result is guaranteed to be informative.

## Question
How much of the oddball response difference (deviant vs standard) does adaptation alone explain, and does
a feedforward adaptation network show any "prediction-error" component or omission response?

## Design
- Adaptation conditions: `none`, `sfa` (spike-frequency adaptation only), `std` (short-term depression
  only), `both`. The two mechanisms are tested separately; `both` is reported but is not the main claim.
- Seeds: 20 (5 with `--quick`). A seed fixes the network instance (connectivity, initial state) and the
  noise. Within a seed the same network is used for all blocks, so conditions are paired.
- Tones: target tone **d = channel 6**. Standard **s = d - gap**; default gap 3 (s = 3). Deviants are
  ascending (above the standard).
- Oddball blocks (flip-flop): A = standard s with deviant d; B = standard d with deviant s. 400 trials.
  First 10 trials are standards and at least 3 standards precede each deviant (Parras et al. 2017);
  for p_dev >= 0.25 the minimum is 2 because 3 cannot be satisfied (departure, documented).
- ISI (silent gap between pulses): uniform 300-500 ms (as in the brief); pulse 50 ms. Fixed ISI is
  Experiment 2's primary design. No fixed-ISI rerun of Experiment 1 is planned.
- Controls, both containing d and matched in target probability to the oddball deviant (p = 1/n):
  **many-standards** (n equiprobable tones, random order, no immediate repeat) and **cascade**
  (the same n tones in a regular ascending run). Default p = 0.1 so n = 10.
- Response: baseline-corrected spike count of the 10 E cells of the relevant channel, window 0-180 ms,
  baseline 75 ms before onset (Parras 2017). Standards: only the last standard before each deviant.
  Condition response = mean over trials, clipped at 0 for the indices (unclipped values also saved).

## Outcome measures (per seed, then mean and 95% t-interval over seeds)
1. **SSA index** (flip-flop): (D - S)/(D + S), where D = response of each of the two tones when it is the
   deviant (summed over the two tones) and S = response of each tone when it is the standard. NaN if D + S = 0;
   NaN seeds are counted and reported.
2. **Decomposition for tone d**: DEV (A), STD (B), CTR (many-standards or cascade). Raw differences and
   Euclidean-normalised indices: iMM = DEV - STD, iRS = CTR - STD, iPE = DEV - CTR.
3. **Sweeps** (sfa, std; see `docs/PARAMETERS.md`): gap in {1,2,3,4,6} channels; deviant probability
   {0.05, 0.1, 0.2, 0.3} for SSA, with matched controls only where 1/p divides 10 (p = 0.1, 0.2).
4. **Omission check** (all adaptation conditions): regular tone on channel 6, fixed ISI 400 ms, 200 slots,
   20% omitted (never in the first 10, never adjacent). Measure: window 0-180 ms after the expected onset
   minus the 75 ms baseline, on omitted slots. Positive control: the same measure on present tones.

## Predictions, stated before the run (these are expectations, not tuned targets)
- P1. `none`: SSA index and iRS about 0 (CI includes 0) because nothing adapts.
- P2. `sfa` and `std`: SSA > 0 and iRS > 0.
- P3. iPE for `sfa` and `std` is about 0, **but could differ from 0** because the oddball and control
  contexts are not identical in neighbouring-channel adaptation. Any iPE != 0 here is an artefact of
  adaptation in this model, not evidence of prediction. Reported as measured.
- P4. Omission: no response above baseline for any adaptation condition (feedforward network, no input).
  A null counts as meaningful only if the positive control is clearly detectable and the CI half-width
  of the omission response is below 5% of the positive-control response.
- P5. SSA should fall with larger deviant probability and rise with frequency gap (more channel
  separation means less shared adaptation). Whether it does is the result.

## What would change the interpretation (declared now)
- If `none` shows SSA != 0: the measure or the network has a bias; stop and debug before reading anything else.
- If iPE is clearly > 0 with matched controls under adaptation alone: report it plainly as an effect of this
  model's adaptation, and do not read it as evidence of prediction.
- No parameter is changed to make P2-P5 come true.

## Change log after first run
(none yet)
