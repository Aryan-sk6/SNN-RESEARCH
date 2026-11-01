"""Sanity-target measurements for re-tuning the predictive circuit (see docs/RETUNE_SLOW_ADAPTATION.md).

Development seeds only; no omission, unexpected-repeat or post-oddball measure is used here.
"""

from __future__ import annotations

import numpy as np

from . import predictive as PR
from . import tier2 as T
from .params import ADAPT_BY_LABEL


def alt_seq(n_slots):
    items = [((T.A_CH if i % 2 == 0 else T.B_CH), "AB"[i % 2], 0.0) for i in range(n_slots)]
    return T.build(items, 400.0, 50.0, np.random.default_rng(0))


def _first_below(x, thr, smooth=1):
    """1-based exposure at which the running mean (window `smooth`) first drops below thr; the sequence length if never."""
    if smooth > 1:
        x = np.convolve(x, np.ones(smooth) / smooth, mode="valid")
    hit = np.nonzero(x < thr)[0]
    return float(hit[0] + 1) if hit.size else float(len(x) + smooth - 1)


def calib_block(spec):
    """One development seed, one constant set: the seven sanity metrics (see TARGETS)."""
    tau, seed, pov = float(spec["tau"]), int(spec["seed"]), spec["pp"]
    p = T.NetworkParams(dt_ms=T.DT_MS, tau_w_ms=tau)
    pp = T.pred_params({"pp": pov})
    both = ADAPT_BY_LABEL["both"]
    short, long_ = alt_seq(60), alt_seq(200)
    onA, onB = short.onsets_ms[0::2], short.onsets_ms[1::2]

    te = PR.run_predictive(short, p, both, PR.Mech(L=False), pp, seed)
    rc = T.raw_counts(te, p, pp, T.B_CH, onB)
    naive = float(rc["PEp"][:3].mean())
    err_gain = float(rc["PEp"][10:].mean() / max(rc["E"][10:].mean(), 1e-9))
    # delay line of channel A (index 0): spikes per cell at each lag 4..19, A tones 10..29
    rates = []
    for s in range(pp.min_lag, pp.n_lags):
        lo_c, hi_c = s * pp.n_d, (s + 1) * pp.n_d
        tt = np.sort(te.d_t[(te.d_idx >= lo_c) & (te.d_idx < hi_c)])
        rates.append(T._cnt(tt, onA[10:], s * pp.lag_ms, s * pp.lag_ms + 100.0).mean() / pp.n_d)
    delay_rate = float(np.mean(rates))

    a2 = PR.run_predictive(short, p, both, PR.A2B_MECH, pp, seed)
    ra = T.raw_counts(a2, p, pp, T.B_CH, onB)
    g = a2.g_val[(a2.g_t >= onB[0]) & (a2.g_t <= onB[0] + 1000.0)]
    nv = max(naive, 1e-9)

    b = PR.run_predictive(long_, p, both, PR.B_MECH, pp, seed)
    rb = T.raw_counts(b, p, pp, T.B_CH, long_.onsets_ms[1::2])
    return dict(naive=naive, err_gain=err_gain, delay_rate=delay_rate,
                gate_peak=float(g.max()) if g.size else float("nan"),
                fast_exposures=_first_below(ra["PEp"], 0.5 * naive),
                pred_err=float(ra["PEp"][20:].mean() / nv), over_pred=float(ra["PEm"][10:].mean() / nv),
                slow_exposures=min(_first_below(rb["PEp"], 0.5 * naive, smooth=5), 100.0))
