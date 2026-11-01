# Architecture: what every file does and why

A file-by-file guide to the code. The model is a **simplified spiking network**; it says
nothing about real brains or clinical use.

## The idea in one paragraph
A small leaky integrate-and-fire network receives tone pulses. Two kinds of "tiredness" (adaptation) can be switched on
independently. Experiment 1 asks what adaptation alone explains in oddball sequences. Experiment 2 asks what must be
added to adaptation to respond to a **missing** tone and to an **unexpected repeat**: a prediction circuit (error
cells, a timing delay line, learned predictions), in a slow version (B, loosely Wacongne-style) and in the
proposed gated, fast-learning versions (A1, A2b). Every experiment runs over many random seeds and reports mean
and 95% confidence interval.

## Data flow
```
stimuli.py / tier2.py   build a tone sequence (onsets, channels, labels)
        |
network.py              Brian2 network: Poisson input -> E cells (+ I cells); adaptation switches
predictive.py           adds delay line, prediction cells, error cells, optional gate and candidates
        |   spikes
analysis.py / tier2.py  window counts -> baseline-corrected responses, SSA index, iMM/iRS/iPE
        |
blocks.py               "one block -> a few numbers" (a spec dict in, a result dict out)
runner.py               run many blocks in parallel, cached on disk (resume after interruption)
        |
experiments/*.py        build the specs, aggregate over seeds (stats.py), make figures and tables
```

## Source files (`src/snn_oddball/`)
| File | Role | Things to know |
|---|---|---|
| `params.py` | All model constants in one frozen dataclass (`NetworkParams`), with validation, and the adaptation switch (`Adaptation`: spike-frequency adaptation, depression) | Units are in the variable names (`_ms`, `_mV`, `_hz`). Provenance rules at the top. |
| `network.py` | The Brian2 network of Experiment 1: 100 E and 20 I LIF cells, 10 tone channels of 10 E cells, Poisson thalamic inputs with Gaussian tuning, feedback inhibition. Also `make_lif_group` / `lif_equations`, shared with the analytic-rate test | `run_sequence(seq, params, adaptation, seed)` is deterministic: same arguments, same spikes. Adaptation (a) is an adaptation current on E cells, (b) is Tsodyks-Markram-style depression (utilisation fixed, facilitation omitted) on the input synapses. |
| `stimuli.py` | Sequence generators: oddball (Parras-style constraints), many-standards, cascade, repeated tone, omission sequence | `ISI` is the silent gap between pulses; omitted slots keep their onset time. All randomness comes from a seeded generator the caller passes. |
| `analysis.py` | The response measure (0-180 ms count minus 75 ms baseline, scaled), SSA index, and `decompose` (iMM, iRS, iPE, raw and Euclidean-normalised) | Undefined SSA gives NaN, never 0. |
| `stats.py` | `mean_ci`: mean and Student-t 95% interval over seeds, NaN-aware | One seed gives no interval. |
| `blocks.py` | Experiment 1 block runners (`odd`, `ctrl`, `omit`) and the dispatcher to Tier 2 blocks | A block is a pure function of its spec (including the seed). |
| `runner.py` | `run_specs`: parallel (spawned processes), on-disk cache keyed by a hash of the spec, atomic writes | Interrupt and rerun: finished blocks are not recomputed. |
| `predictive.py` | The prediction circuit and mechanism switches (`Mech`: T, E, L, G, C, replacement) | See its docstring for each layer. B = T+E+L, A1 = B+G+replacement, A2b = B+G+C. |
| `tier2.py` | Tier 2 sequences (omission, alternation with repeats, episodes, one-shot, regularity buildup, random, decomposition), measures and block runners | Time step 0.5 ms for all Tier 2 runs. |

## Experiments (`experiments/`)
| File | What it does |
|---|---|
| `exp1_adaptation.py` | Experiment 1 end to end: specs, run, aggregate, figure `results/fig1_adaptation_*.png`, tables |
| `exp2_tier2.py` | Experiment 2 and all Tier 2 suites, ablation and robustness; figure `results/fig2_tier2_*.png`, tables `results/tier2_summary_*.md` |

## Tests (`tests/`)
| File | Covers |
|---|---|
| `test_lif.py` | LIF firing rate against the analytic value for constant current (within 2%) |
| `test_adaptation.py` | Adaptation lowers the response to repeated input; the mechanisms work separately; channel specificity |
| `test_reproducibility.py` | Same seed gives identical results; different seeds differ |
| `test_validation.py` | Input validation of parameters, sequences, seeds, channels |
| `test_decomposition.py` | iMM/iRS/iPE and SSA arithmetic on hand-made numbers |
| `test_stimuli_stats.py` | Sequence constraints, matched control probabilities, `mean_ci` |
| `test_blocks.py` | Block runners and the cache |
| `test_predictive.py` | Circuit validity checks, learning at the right lag, no learning when switched off, gate behaviour, Tier 2 sequence constraints |

## Docs (`docs/`)
| File | Purpose |
|---|---|
| `PRIOR_ART.md` | Papers actually retrieved, with a verification level for each (full text, abstract only, search summary) |
| `PREREGISTRATION.md`, `PREREGISTRATION_TIER2.md` | Designs, measures, predictions and pass rules fixed **before** the runs |
| `PARAMETERS.md` | Every constant, how it was chosen, calibration log |
| `EXP1_RESULTS.md` | Experiment 1 against the pre-registered predictions |
| `EXP2_DESIGN.md`, `PLAN.md`, `ROADMAP.md` | Design, plan, and what can and cannot be tested |

## Invariants worth remembering
1. **Determinism:** every random draw comes from a seed; blocks are cached by spec hash. Same spec, same numbers.
2. **Units:** membrane potential and synaptic "currents" are in mV (current-based model).
3. **Experiment 1 cannot change by accident:** `network.py` was extended compatibly; a regression test compares a rerun with the cached results.
4. **Nothing is tuned to a result:** calibration uses fixed sanity targets only (see `docs/PARAMETERS.md`).
5. **Negative results are reported** in the results tables and in the README.
