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
