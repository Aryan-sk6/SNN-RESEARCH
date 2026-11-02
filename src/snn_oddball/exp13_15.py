"""Experiments 13 (ideal-observer benchmark) and 15 (precision). Design: docs/PREREGISTRATION_EXP13_15.md.

Block runners take a plain-dict spec (kind="x1315") and return JSON-serialisable dicts, like tier2.py.
"""

from __future__ import annotations

import numpy as np

from . import predictive as PR
from . import tier2 as T
from .params import ADAPT_BY_LABEL

TONES4 = (T.A_CH, T.B_CH, T.C_CH, T.D_CH)


# ------------------------------------------------------------------ ideal observer (Experiment 13)
def observer_surprise(tones, alphabet=TONES4, alpha=1.0):
    """Bayesian first-order Markov observer with a symmetric Dirichlet(alpha) prior on each row of the transition
    matrix and perfect memory. Returns, for every tone after the first, p(tone | previous tone) under the counts
    seen so far, and the surprise -log2 p. The first tone gets p = 1/len(alphabet)."""
    idx = {a: i for i, a in enumerate(alphabet)}
    k = len(alphabet)
    counts = np.full((k, k), alpha)
    p = np.empty(len(tones))
    p[0] = 1.0 / k
    for t in range(1, len(tones)):
        a, b = idx[int(tones[t - 1])], idx[int(tones[t])]
        p[t] = counts[a, b] / counts[a].sum()
        counts[a, b] += 1
    return p, -np.log2(p)


def observer_exposures_alternation(n_pairs=30, alphabet=TONES4, alpha=1.0):
    """Exposures (B tones) until the observer's error 1 - p(B | A) is below 50% of its naive value (no learning:
    1 - 1/len(alphabet)). Same criterion as the network's S4 / S7 measures."""
    tones = [T.A_CH if i % 2 == 0 else T.B_CH for i in range(2 * n_pairs)]
    p, _ = observer_surprise(tones, alphabet, alpha)
    err = 1.0 - p[1::2]
    naive = 1.0 - 1.0 / len(alphabet)
    hit = np.nonzero(err < 0.5 * naive)[0]
    return float(hit[0] + 1) if hit.size else float(len(err))


# ------------------------------------------------------------------ sequences (Experiment 15)
def seq_probe(context, n_slots, rng, p_probe=0.1, start=40, min_sep=6):
    """Context of tones A, B (regular: alternating; random: uniform over A, B, C) with probe tone D at about 10% of
    the slots from `start` on (pairwise >= min_sep apart). D never appears otherwise, so adaptation to D is the same
    in both contexts."""
    if context not in ("regular", "random"):
        raise ValueError("context must be 'regular' or 'random'")
    probes = set(T.choose_slots(n_slots, int(round(p_probe * (n_slots - start))), rng, start, min_sep))
    items = []
    for i in range(n_slots):
        if i in probes:
            items.append((T.D_CH, "probe", 0.0))
        elif context == "regular":
            items.append((T.A_CH if i % 2 == 0 else T.B_CH, "ctx", 0.0))
        else:
            items.append((int(rng.choice([T.A_CH, T.B_CH, T.C_CH])), "ctx", 0.0))
    return T.build(items, 400.0, 50.0, rng), sorted(probes)


def _gain_at(res, pp, times):
    if res.pi_t is None or res.pi_t.size == 0:
        return np.ones(len(times))
    return 1.0 / (1.0 + pp.k_prec * np.interp(np.asarray(times, float), res.pi_t, res.pi_val))


def _own_channel_error(res, p, pp, seq, idx):
    """Raw PE+ and PE- spikes (0-180 ms) of each tone's own channel, and raw E spikes."""
    err, e = np.zeros(len(idx)), np.zeros(len(idx))
    for j, i in enumerate(idx):
        c = int(seq.tones[i])
        rc = T.raw_counts(res, p, pp, c, seq.onsets_ms[[i]])
        err[j] = rc["PEp"][0] + rc["PEm"][0]
        e[j] = rc["E"][0]
    return err, e


# ------------------------------------------------------------------ block runners
def run_probe(spec):
    rng = T._rng(spec, "probe:" + spec["context"])
    seq, probes = seq_probe(spec["context"], int(spec["n_slots"]), rng)
    p, pp, res = T._run(spec, seq)
    ons = seq.onsets_ms[probes]
    rc = T.raw_counts(res, p, pp, T.D_CH, ons)
    ctx = [i for i in range(40, len(seq)) if seq.labels[i] == "ctx"]
    return dict(n_probe=len(probes), probe_PEp=T._mean(rc["PEp"]), probe_err=T._mean(rc["PEp"] + rc["PEm"]),
                probe_E=T._mean(rc["E"]), gain_probe=T._mean(_gain_at(res, pp, ons)),
                ctx_err=T._mean(T.total_error(res, seq.onsets_ms[ctx])))


def run_trace(spec):
    """The Tier 2 unexpected-repeat sequence (same generator and rng tag as tier2.run_aba, so the same sequence for the
    same seed), with per-tone outputs for the ideal-observer comparison."""
    rng = T._rng(spec, "aba")
    seq, _ = T.seq_aba(int(spec["n_slots"]), 0.1, rng)
    p, pp, res = T._run(spec, seq)
    idx = list(range(len(seq)))
    err, e = _own_channel_error(res, p, pp, seq, idx)
    return dict(tones=[int(x) for x in seq.tones], err=err.tolist(), E=e.tolist())


def run_prec_calib(spec):
    """Precision sanity targets on a development seed: mean precision gain over the last 20 slots of a regular
    (alternating A B, 60 slots) context and the last 30 slots of a random (A, B, C, D, 100 slots) context."""
    seed = int(spec["seed"])
    p = T.NetworkParams(dt_ms=T.DT_MS)
    pp = T.pred_params({"pp": spec["pp"]})
    both = ADAPT_BY_LABEL["both"]
    items = [((T.A_CH if i % 2 == 0 else T.B_CH), "x", 0.0) for i in range(60)]
    reg = T.build(items, 400.0, 50.0, np.random.default_rng(0))
    r1 = PR.run_predictive(reg, p, both, PR.A2BP_MECH, pp, seed)
    rnd = T.seq_random(100, np.random.default_rng(np.random.SeedSequence([seed, 15])))
    r2 = PR.run_predictive(rnd, p, both, PR.A2BP_MECH, pp, seed)
    return dict(gain_regular=float(_gain_at(r1, pp, reg.onsets_ms[-20:]).mean()),
                gain_random=float(_gain_at(r2, pp, rnd.onsets_ms[-30:]).mean()))


RUNNERS = dict(probe=run_probe, trace=run_trace, prec_calib=run_prec_calib)


def run_block(spec):
    return RUNNERS[spec["exp"]](spec)
