# Tier 2 results (20 seeds, full run; omission measure v3)

All numbers: mean [95% CI over 20 seeds] from `results/tier2_summary_full.md`; figure `results/fig2_tier2_full.png`.
Predictions were fixed before the runs in `docs/PREREGISTRATION_TIER2.md`; changes made after the quick runs are in its
change log. This is a simplified spiking model. It says nothing about real brains or clinical use, and a result here
shows only that a mechanism is **sufficient in this toy network**.

**Update (v3).** The first full run used an omission measure (baseline-corrected R) that was unsuitable: the
negative-error response starts before the expected onset, so the baseline contained part of it, and the subsets without
the delay line fire a burst before every slot (see `docs/PREREGISTRATION_TIER2.md`, v3). The omission, jitter,
buildup, ablation, long-training and robustness rows below use the v3 measure (raw PE- spikes at omitted slots minus
present-tone slots, same 0-180 ms window; pass = CI above 0 and mean at least 1 spike). The v2 results are in
`results/archive/v2_*`. I had looked at spike traces of one test seed (seed 0) when designing v3.

Networks: N0 adaptation only; B slow predictive core (delay line, error cells, learning; a simplified, labelled
replication of the Wacongne et al. idea, not of their code); A1 and A2b = B plus the mismatch gate and candidates
(the owner's Mechanism A, two variants).

## Summary

| Test | Pre-registered expectation | Result | Verdict |
|---|---|---|---|
| T1 omission (v3 primary D-, PE- omitted minus present) | A passes; N0 null | N0 0.00; B 0.14 [-0.07, 0.34] fails; A1 5.66 [3.83, 7.49] and A2b 5.97 [3.80, 8.15] pass | **Supported** for A (v2 measure was null for all; superseded) |
| T2 unexpected repeat | A larger than regular; N0 smaller | A1 +8.58 [5.09, 12.07], A2b +7.57 [3.98, 11.15] pass; B -1.15 [-2.69, 0.39] fails; N0 -2.84 [-3.62, -2.07] (adaptation signature) | **Supported** for A |
| Long-training fairness check | (added) | B repeat +5.84 [2.15, 9.52] passes; B omission D- 2.76 [1.48, 4.03] passes; A2b omission 6.82 [5.00, 8.63], repeat 12.35 | A's advantage is **speed**, not capability |
| M1 tone after the odd one | A2b rise larger than N0's | N0 2.68, B 6.36, A1 11.70, A2b 10.83; A2b minus N0 8.15 [5.78, 10.52] | Supported, but B also shows 3.68 [2.05, 5.31] |
| M1 sensory-only (E cells) | | N0 2.68, B 2.64, A1 5.41, A2b 5.27 | Sensitisation about +2.6, by design of the gate |
| M2 drop-off steeper after the odd one | after-B slope steeper than initial slope; order A > B > C | A2b -0.17 vs initial -0.19 (not steeper); order A -0.17, C -0.09, B +0.09 | **Not supported** |
| M3 candidate fit | error and gate lower after A, B than after C | A2b error 9.40 [8.65, 10.16], 4.69 [4.08, 5.31], 12.35 [10.92, 13.78]; gate 0.37, 0.40, 0.46 | **Supported** (A2b) |
| M5 continuations | random decays to baseline; cycles learned faster | Random error does **not** decay (A2b 26.6 first half, 26.8 second half); r_inf CIs too wide to separate cycles from random | Not supported / inconclusive |
| M6 decomposition | iPE > 0 against cascade | A2b iPE(cascade) 0.14 [0.09, 0.20], B 0.04 [0.02, 0.06]; iPE(many) about 0 for both | Partly; see below |
| One-shot learning | PE+ falls within a few pairs | PE+ pair 2 / pair 1 = 1.11 [0.89, 1.32] (A2b); half-level reached only slowly (9.6 [8.0, 11.2], censored at 13) | **Not supported** |
| Regularity buildup | omission response rises with n | A2b D-: n=1 0.97, n=2 4.51, n=4 1.97, n=8 2.05; slope per doubling 0.07 [-0.25, 0.39]; B, N0 zero | **Not supported** as a steady rise (jump from n=1 to n=2: +3.54 [1.71, 5.38], then flat) |
| Timing jitter | omission shrinks with jitter | A2b D-: 5.97, 5.61, 4.38, 3.23 for jitter 0, 0.1, 0.3, 0.6; drop vs 0 (paired, post hoc) 0.37 [-0.63, 1.36], 1.59 [0.03, 3.16], 2.75 [0.72, 4.77]; B and N0 about 0 | **Supported** (monotone fall; the comparison was not pre-specified as a trend test) |
| Ablation | smallest subset passing both | Passing both: TELGC, TELG, ELGC (4 components at least); EL, ELG pass repeat only (omission D- 0.61, 0.73, small) | Needs error cells, learning and the gate; timing or candidates as the 4th |
| Robustness (40 random constants of A2b) | | omission 82%, repeat 75%, both 62% | Single-seed, effect floor only |

## What can be said

1. **Adaptation alone gives the opposite sign of an unexpected repeat** (N0: repeat smaller). A1 and A2b reverse it
   with large effects. The slow core B does not within normal training, but does with 600 slots. So the supported
   claim is "the added gate and candidates speed up learning of the expectation", not "B cannot".
2. **Omission response (v3).** With a measure that does not subtract a contaminated baseline, A1 and A2b show a clear
   negative-error response at omitted tones (about 6 spikes more than at present tones). B does not at normal training
   (0.14) but does with 600 slots (2.76 [1.48, 4.03]). N0 has no error cells (exactly 0). The negative-error cells are
   built to be suppressed by input, so "omitted > present" is partly structural; the informative parts are below.
   The earlier "failure" was the measure, not the network. The sensory (E-cell) omission response is tiny (about 0.5
   spikes above a quiet window).
   - It shrinks as timing becomes irregular (jitter 0 to 0.6: 5.97 to 3.23), which fits a timing-based prediction.
   - It does not grow steadily with the number of regular tones (n=2 high, n=4 and n=8 lower), so "builds up with
     regularity" is not supported in this form.
3. **The owner's drop-off ordering (M2) and the one-shot prediction are not supported.** Adaptation alone already
   gives a steep drop for the new tone C; the drop after the odd one is not steeper than the initial one; learning is
   gradual (about 10 exposures), not one-shot.
4. **Candidate fit (M3) is supported for A2b**, but the error ordering also appears in B (8.22, 5.87, 12.77 for
   A, B, C), so it is not unique to the candidate mechanism. The gate ordering is specific to A.
5. **Randomness is not accepted.** Error in a random context stays at its starting level in all learning networks.
   No precision or uncertainty scaling is implemented, which the owner's "accepting randomness" idea would need.
6. **M6:** with the cascade control, iPE is positive for B and A2b; with the many-standards control it is about zero.
   In A2b the many-standards control responds as strongly as the deviant (23.53 vs 23.10), because an unpredictable
   sequence keeps the error cells busy. This is a property of this model and is not a match to, or test of, the
   cortical data in Parras et al.
7. **Ablation (v3):** both tests pass in TELGC, TELG and ELGC. Without the gate (TEL, EL) the repeat passes only without
   timing, and omission does not pass (EL 0.61 [0.13, 1.10] is above 0 but below the 1-spike floor). So error cells,
   learning and the gate together are what the omission and repeat tests need here; the delay line is replaceable.
   The earlier very negative omission numbers for the no-timing subsets were the baseline artefact, now removed.

## Caveats
- The v3 measure was designed after the v2 failure, and one test seed was inspected during that design. It is also partly structural (see above).
- Robustness uses one seed per draw and an effect floor without a CI, so it is more lenient than the 20-seed tests and
  not directly comparable. A passes T2 in 75% of random constant sets, so the T2 result is moderately but not fully
  robust to constants.
- A2b constants were calibrated on sanity targets with development seeds (100-104); test seeds were separate.
- Post-hoc additions (quiet-baseline PE-, long-training suite, sensory-only M1, N0 NaN handling) are flagged in the
  pre-registration change log.
- Not implemented: precision scaling, population/ensemble coding (one 10-cell channel per tone), energy or
  two-system effects. Those theories remain untested here (see `docs/ROADMAP.md`).
