# Experiment 1 results: what adaptation alone explains

Full run: 20 seeds, 400 trials, ISI 300-500 ms. Figure `results/fig1_adaptation_full.png`, table
`results/exp1_summary_full.md`, data `results/exp1_summary_full.json`. Design and predictions were fixed in
`docs/PREREGISTRATION.md` before the run. No parameter or analysis changed after seeing results. The run was
interrupted several times by container restarts and resumed from the on-disk cache; every block is a function of
its spec and seed, so interruptions do not change results.

## Against the pre-registered predictions
| Prediction | Result | Verdict |
|---|---|---|
| P1 `none`: SSA and iRS about 0 | SSA -0.000 [-0.006, 0.006], iRS 0.008 [-0.006, 0.021] | **holds** |
| P2 `sfa` and `std`: SSA > 0 and iRS > 0 | std: SSA 0.161 [0.153, 0.169], iRS 0.178 [0.165, 0.191]. sfa: SSA 0.019 [0.012, 0.026] but iRS 0.009 [-0.005, 0.023] | **holds for depression; spike-frequency adaptation (sfa) gives a small SSA whose repetition-suppression part is not distinguishable from 0** |
| P3 iPE about 0 under adaptation alone | cascade control: none -0.008, sfa 0.011, std -0.006, both -0.000, all CIs include 0 (half-widths about 0.01-0.015); many-standards control gives the same | **holds** (sensitivity: effects larger than about 0.015 would have been seen) |
| P4 omission: no response above baseline, and the null is meaningful | omitted-slot response: none 0.10 [-0.10, 0.30], sfa 0.10 [-0.06, 0.27], std -0.09 [-0.26, 0.08], both 0.21 [0.015, 0.40]; tone-present response 11-26 spikes; CI half-width is 0.8-1.7% of the tone response (criterion was < 5%) | **holds, with one caveat**: `both` has a CI that just excludes 0, but the effect is 1.8% of the tone response (floor for a "response" is 10%), and it is one of four conditions tested; reported as marginal and negligible, not as a response |
| P5 SSA falls with deviant probability and rises with frequency gap | flat across the gap sweep (std 0.160-0.167, sfa 0.014-0.019). Flat for p = 0.05-0.2 (std 0.158-0.165); lower only at p = 0.3 (0.126) | **not supported** |

## Why P5 fails (explanations, not yet tested)
- **Gap:** each depressing synapse belongs to one input channel, so a tone only depresses its own channel. Spike-frequency adaptation
  can spread to a neighbour only through the 2-channel tuning overlap, and that is small. No gap dependence follows from
  the architecture. This is a limitation, not a finding about brains.
- **Probability:** the adaptation recovers within the 300-500 ms gap, so the standard's state is the same whether the
  deviant is 5% or 20% of tones. Models with slower or multi-timescale adaptation (the literature we retrieved at
  abstract level, Mill 2011 and Yarden & Nelken 2017, reproduce probability dependence) would differ. The drop at p = 0.3 is
  confounded with the changed placement rule (min 2 standards before each deviant instead of 3), so it should not be
  read as a probability effect.

## Other observations
- Spike-frequency adaptation (time constant 300 ms, +2 mV per spike) explains very little: SSA about 0.02. The tone
  interval (about 450 ms) is longer than its decay, so little builds up across tones. A slower-adaptation sensitivity
  analysis was proposed and has not been run.
- Under all four adaptation conditions the many-standards and cascade controls give indistinguishable responses
  (for example std: 19.20 vs 19.27 spikes), so this model cannot tell the two controls apart (it has no sequence
  expectation to differ on).
- The decomposition behaves as the arithmetic says: iMM = iRS + iPE within rounding.

## What this means (and does not)
In this simplified network, adaptation reproduces the deviant-vs-standard difference (SSA, via repetition
suppression) and produces **no** prediction-error component and **no** omission response. That is the baseline that Experiment 2
asks mechanisms to beat. It says nothing about real brains or clinical use.

## Limitations
- One tone pair geometry per sweep (deviant above the standard only; the deviant channel fixed at 6).
- Input-channel-private depression, 300 ms spike-frequency adaptation and 500 ms recovery are single a-priori choices
  (`docs/PARAMETERS.md`), not fitted; only two time constants for adaptation.
- The decomposition uses spike counts of 10 cells per channel; no LFP-like proxy.
- Feedback inhibition is weak (I cells fire about 3 Hz).
