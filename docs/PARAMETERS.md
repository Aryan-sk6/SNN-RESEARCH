# Parameters, calibration and change log

Source of truth: `src/snn_oddball/params.py`. Units are in the variable names. Everything here is
a **simplified model**; no value is fitted to data from a real brain.

## Provenance rules
1. Values were fixed before running any oddball, omission or ABABAA experiment.
2. Four values were **calibrated** (below), only against single-tone, unadapted targets that were
   written down first. They were never adjusted to improve an experiment outcome.
3. Any later change is appended to the change log with its reason.
4. Time constants and sizes are "typical order of magnitude" choices, **not** taken from a retrieved
   paper, except where a source is named. The Tsodyks-Markram model is named in the brief but its
   original paper has **not** been retrieved for this repo, so it is not cited here yet.

## Architecture
| Item | Value | Note |
|---|---|---|
| Tone channels | 10 | abstract tonotopic positions, not Hz |
| Excitatory (E) cells | 100 (10 per channel) | LIF |
| Inhibitory (I) cells | 20, one shared pool | LIF |
| Input units | 20 Poisson units per channel | stand in for thalamic afferents |
| Tone pulse | 50 ms | per the brief |
| Recurrent E->E | none | the network is feedforward plus feedback inhibition |

## Neuron and synapses (current-based; "current" is in mV)
| Parameter | Value | Unit |
|---|---|---|
| membrane time constant `tau_m` | 20 | ms |
| rest `E_L` / threshold `V_th` / reset `V_reset` | -65 / -50 / -65 | mV |
| refractory period | 2 | ms |
| excitatory / inhibitory synaptic decay | 5 / 10 | ms |
| membrane noise (OU std) `sigma_noise` | 6 | mV (**calibrated**) |
| input -> E weight `w_in`, p = 0.6 | 5 | mV (**calibrated**) |
| E -> I weight `w_ei`, p = 0.5 | 4 | mV (**calibrated**) |
| I -> E weight `w_ie`, p = 0.5 | 3 | mV |
| input tuning width | 0.7 channels (Gaussian), no synapse beyond 2 channels | fixed a priori |
| tone input rate | 100 Hz per active input unit; background 0 | |
| time step | 0.25 ms | |

The tuning width means a tone on channel k also drives channels k+-1 at 36% of full weight and
k+-2 at 1.7%. The frequency-gap sweep therefore changes overlap as it should. "Gap" is in channel
units.

## Adaptation (switchable, tested separately)
| Mechanism | Parameters |
|---|---|
| (a) spike-frequency adaptation on E cells | +2 mV per spike, decay 300 ms |
| (b) short-term depression on input -> E | utilisation `U` = 0.1, recovery 500 ms, facilitation omitted |

Depression is parametrised so that the first spike after full recovery has the same efficacy as without
depression. The conditions differ only in how efficacy falls with repeats. Facilitation is omitted: this is
a simplification of the full Tsodyks-Markram model.

## Calibration targets (written before looking at results)
- spontaneous E rate on unstimulated channels between 1 and 5 Hz (so a baseline window is informative)
- unadapted evoked response of the target channel (10 cells, 0-180 ms after onset) between 20 and 60 spikes
- I cells active but below 30 Hz

Result with the final values: spontaneous about 1.1 Hz, evoked about 29 spikes, I cells about 3 Hz.
**Caveat:** feedback inhibition is weak (I cells fire about 3 Hz), so inhibition plays a small role.

## Measured adaptation strength (single tone repeated, ISI 400 ms, 3 seeds, 0-180 ms count)
| Condition | first tone | tones 21-30 | vs no adaptation |
|---|---|---|---|
| none | 29.0 | 27.9 | - |
| SFA | 23.7 | 22.6 | -19% |
| depression | 22.3 | 16.1 | -42% |
| both | 17.7 | 12.9 | -54% |

## Analysis windows
Response 0-180 ms after onset, baseline 75 ms before onset, both from Parras et al. 2017 (Methods).
Response = window count minus baseline count scaled by 180/75, mean over trials, E cells of one channel.

## Change log
| # | Change | Reason | Before any experiment? |
|---|---|---|---|
| 1 | `sigma_noise` 3 -> 6 mV | spontaneous rate was 0 Hz, which makes a null result uninterpretable | yes |
| 2 | `w_in` 3 -> 5 mV | evoked response was 11 spikes (below the 20-60 target) | yes |
| 3 | `w_ei` 2 -> 4 mV | I cells were silent | yes |
| 4 | `tm_U` 0.3 -> 0.1 | with 0.3 the synapse is depleted inside a single 50 ms pulse (steady-state efficacy about 6%); the first tone's response fell to 16% of the unadapted value | yes |
| 5 | bug fix: depression variable `x` initialised to 1 | Brian2 initialises to 0, so the first tone saw no input | yes |

## Representation note (2026-10-17)
Tones are coded as 10 localist tonotopic channels (10 E cells per channel, overlapping input tuning). This is a
deliberate simplification for pure-tone oddball experiments. It is **not** a claim about how concepts are
represented; for the memory extensions the plan is sparse distributed overlapping ensembles
(`docs/THEORY_NOTES.md` 12b).

---

# Predictive circuit and mechanism A (Tier 2; `src/snn_oddball/predictive.py`)

All of the following are single a-priori or sanity-calibrated choices. **No value was set to make an omission,
unexpected-repeat, M1-M6, one-shot or timing result come out a certain way.** Count of free constants of
mechanism A on top of the core circuit: gate (`a_gate`, `g_max`, `tau_gate_ms`, `b_match`, `kappa_learn`, `k_gain`,
`k_replace`), candidates (`c_rep_mV`, `c_old_mV`, `c_new_mV`, `w_trace_old_mV`, `tau_regime_ms`), Match cells (`w_match_mV`,
and the 0.1 factor of E -> Match), about **13 constants** specific to A; the core circuit has about 25 more (shared by B and A).

## Structure (per predictive channel A, B, C, D = channels 3, 6, 8, 1)
| Item | Value |
|---|---|
| prediction cells P, error cells PE+ and PE- | 10 cells each |
| delay line | 20 lags of 50 ms, 4 cells per lag (tapped delay: E spikes copied with a lag-specific delay, p = 0.5) |
| no-timing control (T off) | one slow trace group of 5 cells per channel, synaptic decay 250 ms |
| noise of predictive layers | 1.5 mV (the sensory layer keeps 6 mV) |
| time step for all Tier 2 runs | **0.5 ms** (Experiment 1 used 0.25 ms; the adaptation-only baseline N0 is re-run at 0.5 ms for Tier 2) |
| adaptation | both mechanisms on (condition `both`) in every Tier 2 network |

## Sanity-calibrated values (calibration targets fixed before looking at any test)
| Constant | Value | Calibration target |
|---|---|---|
| E -> delay cells weight 22 mV | each delay group fires about once per cell at its own lag, small timing jitter |
| E -> PE+ 18 mV, P -> PE+ (inhibition) 30 mV, P -> PE- 16 mV, E -> PE- (inhibition) 40 mV | an unpredicted tone drives PE+ to about 60-100% of the sensory spike count; a predicted tone gives mostly no error cell firing; an omitted predicted tone drives PE- |
| prediction weight bound 20 mV, slow learning rate 0.0004, LTD 0.002 per pre spike | the slow learner builds the right-lag weight over tens of exposures |
| learning stops once P is itself active (`ptr_thr` 3 spikes within 100 ms) | prevents run-away potentiation while a prediction is already cancelling the error |
| gate: +0.02 per PE+ spike, cap 2, decay 1500 ms, -0.15 per Match spike | peak about 1 after the first error; settles when predictions fit |
| gated learning multiplier 3, sensitisation 0.5 per gate unit | gated learner reaches a cancelling prediction within about 3 exposures without large over-prediction (PE- at a present tone below 30% of the naive PE+) |
| candidate drives 1.5 / 1.5 / 0.4 mV per gate unit | fixed a priori, not calibrated |

## Calibration log
| # | Change | Reason |
|---|---|---|
| 1 | E -> PE+ 2.5 -> 18 mV, E -> delay 4 -> 22 mV | first guesses were silent; error and delay cells did not reach threshold |
| 2 | prediction weight bound 6 -> 20 mV, learning rate 0.004 -> 0.0004 | P cells could not fire; slow learner was too fast |
| 3 | separated the four error-cell weights | predicted tone left PE- at 31 spikes (over-prediction mis-cancelled) |
| 4 | gate +0.06 -> +0.02, cap 3 -> 2, multiplier 40 -> 3; added self-limiting learning | a single gated event saturated the weights and over-predicted |
| 5 | merged synapse objects; time step 0.25 -> 0.5 ms | 2.4x faster, spike counts within 4% |

## What is NOT claimed
- B is not a faithful replication of Wacongne et al. (2012): their Izhikevich neurons, NMDA currents, 40/400/100-cell
  populations and synfire-chain delay lines are replaced by LIF cells, smaller groups and a tapped delay line.
- The delay line, the error populations and the candidate drives are designed structures; passing a test with them
  shows sufficiency of a design in a toy network, not that a brain works this way.
