# Re-tune for slower adaptation: results

Design and rules: `docs/RETUNE_SLOW_ADAPTATION.md`. Mean over development seeds for calibration; mean [95% CI] over 20 test seeds for the tests.

### Protocol check: original constants at tau_w = 300 ms

| f_E | kappa | f_eta | err_gain | delay_rate | gate_peak | fast_exposures | pred_err | over_pred | slow_exposures | met |
|---|---|---|---|---|---|---|---|---|---|---|
| 1.0 | 3.0 | 1.0 | 0.61 | 0.88 | 0.95 | 4.60 | 0.33 | 0.11 | 69.80 | 7/7 |

Targets: err_gain in [0.6, 1.0]; delay_rate in [0.5, 2.0]; gate_peak in [0.5, 1.5]; fast_exposures in [1.0, 5.0]; pred_err in [0.0, 0.4]; over_pred in [0.0, 0.3]; slow_exposures in [10.0, 100.0]. A star marks a missed target.

