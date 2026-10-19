# Tier 2 results (20 seeds, full run)

All numbers: mean [95% CI over 20 seeds] from `results/tier2_summary_full.md`; figure `results/fig2_tier2_full.png`.
Predictions were fixed before the runs in `docs/PREREGISTRATION_TIER2.md`; changes made after the quick runs are in its
change log. This is a simplified spiking model. It says nothing about real brains or clinical use, and a result here
shows only that a mechanism is **sufficient in this toy network**.

Networks: N0 adaptation only; B slow predictive core (delay line, error cells, learning; a simplified, labelled
replication of the Wacongne et al. idea, not of their code); A1 and A2b = B plus the mismatch gate and candidates
(the owner's Mechanism A, two variants).

## Summary

| Test | Pre-registered expectation | Result | Verdict |
|---|---|---|---|
| T1 omission (primary measure) | A passes; N0 null | Fails for **every** network, including A (0.94 [-1.45, 3.34]) | **Not supported** |
| T1 omission (quiet-baseline PE-, added after seeing the quick runs) | not pre-registered | A1 7.43 [5.27, 9.60], A2b 7.48 [4.99, 9.97]; B 0.17 [-0.06, 0.39] | Post hoc; A clear, B not |
| T2 unexpected repeat | A larger than regular; N0 smaller | A1 +8.58 [5.09, 12.07], A2b +7.57 [3.98, 11.15] pass; B -1.15 [-2.69, 0.39] fails; N0 -2.84 [-3.62, -2.07] (adaptation signature) | **Supported** for A |
| Long-training fairness check | (added) | B repeat +5.84 [2.15, 9.52] passes; B omission PE- 3.69 [2.05, 5.34]; A2b 12.35 and 8.23 | A's advantage is **speed**, not capability |
| M1 tone after the odd one | A2b rise larger than N0's | N0 2.68, B 6.36, A1 11.70, A2b 10.83; A2b minus N0 8.15 [5.78, 10.52] | Supported, but B also shows 3.68 [2.05, 5.31] |
| M1 sensory-only (E cells) | | N0 2.68, B 2.64, A1 5.41, A2b 5.27 | Sensitisation about +2.6, by design of the gate |
| M2 drop-off steeper after the odd one | after-B slope steeper than initial slope; order A > B > C | A2b -0.17 vs initial -0.19 (not steeper); order A -0.17, C -0.09, B +0.09 | **Not supported** |
| M3 candidate fit | error and gate lower after A, B than after C | A2b error 9.40 [8.65, 10.16], 4.69 [4.08, 5.31], 12.35 [10.92, 13.78]; gate 0.37, 0.40, 0.46 | **Supported** (A2b) |
| M5 continuations | random decays to baseline; cycles learned faster | Random error does **not** decay (A2b 26.6 first half, 26.8 second half); r_inf CIs too wide to separate cycles from random | Not supported / inconclusive |
| M6 decomposition | iPE > 0 against cascade | A2b iPE(cascade) 0.14 [0.09, 0.20], B 0.04 [0.02, 0.06]; iPE(many) about 0 for both | Partly; see below |
| One-shot learning | PE+ falls within a few pairs | PE+ pair 2 / pair 1 = 1.11 [0.89, 1.32] (A2b); half-level reached only slowly (9.6 [8.0, 11.2], censored at 13) | **Not supported** |
| Regularity buildup | omission response rises with n | A2b slope per doubling 0.11 [-0.23, 0.45]; B and N0 zero | **Not supported** |
| Timing jitter | omission shrinks with jitter | Primary measure is null at every jitter, including 0 | **Uninformative** (no effect to dose) |
| Ablation | smallest subset passing both | **No subset passes both** | See below |
| Robustness (40 random constants of A2b) | | omission 38%, repeat 75%, both 28% | Single-seed, effect-floor only |

## What can be said

1. **Adaptation alone gives the opposite sign of an unexpected repeat** (N0: repeat smaller). A1 and A2b reverse it
   with large effects. The slow core B does not within normal training, but does with 600 slots. So the supported
   claim is "the added gate and candidates speed up learning of the expectation", not "B cannot".
2. **The omission response was not found with the pre-registered measure for any network.** Anticipatory PE- spikes
   contaminate the pre-tone baseline. With a quiet baseline (added post hoc, labelled as such) A shows a clear PE-
   response at the omitted slot, B only with long training. Treat this as exploratory.
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
7. **Ablation:** T2 passes with error cells plus learning and no timing (EL, ELG, ELGC), so timing (delay line) is not
   needed for the unexpected repeat here. Omission passes nowhere on the primary measure. For these subsets without
   timing the omitted-slot R is strongly negative (-14 to -25), which I have **not** explained; I suspect the baseline
   contamination again and do not interpret it until checked.

## Caveats
- The omission primary measure failing makes timing results (jitter, buildup) uninformative, not negative evidence.
- Robustness uses one seed per draw and an effect floor without a CI, so it is more lenient than the 20-seed tests and
  not directly comparable. A passes T2 in 75% of random constant sets, so the T2 result is moderately but not fully
  robust to constants.
- A2b constants were calibrated on sanity targets with development seeds (100-104); test seeds were separate.
- Post-hoc additions (quiet-baseline PE-, long-training suite, sensory-only M1, N0 NaN handling) are flagged in the
  pre-registration change log.
- Not implemented: precision scaling, population/ensemble coding (one 10-cell channel per tone), energy or
  two-system effects. Those theories remain untested here (`docs/THEORY_NOTES.md`).
