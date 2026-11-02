"""Experiment 9 (roadmap item 9, plan M6): two definitions of prediction error read out from the same network.
Design: docs/PREREGISTRATION_EXP9.md.

The network's prediction before a tone is read from the prediction (P) cells of the four predictive channels in the
100 ms before the onset, normalised to a probability distribution p_hat (flat 1/4 if they are silent).
    E1 (subtractive):  1 - p_hat(event)                 (0.75 for a flat prediction)
    E2 (owner's):      max_c p_hat(c) - p_hat(event)    (0 for a flat prediction, 0 for a correct top guess)
"""

from __future__ import annotations

import numpy as np

from . import tier2 as T

CH = T.PRED_CHANNELS
WIN = (-100.0, 0.0)


def p_hat(counts, floor=1.0):
    """Rows of P-cell counts (n_tones, 4) -> probability rows. Rows with fewer than `floor` spikes in total are flat."""
    counts = np.asarray(counts, float)
    tot = counts.sum(axis=1, keepdims=True)
    flat = np.full_like(counts, 1.0 / counts.shape[1])
    return np.where(tot >= floor, counts / np.maximum(tot, 1e-12), flat)


def errors(p, event_idx):
    """E1 and E2 per tone from probability rows p and the index (0..3) of the tone that occurred."""
    pe = p[np.arange(len(p)), event_idx]
    return 1.0 - pe, p.max(axis=1) - pe


def _p_counts(res, pp, onsets):
    out = np.zeros((len(onsets), len(CH)))
    for k, c in enumerate(CH):
        out[:, k] = T.pred_spikes(res, pp, c, onsets, *WIN)
    return out


def run_block(spec):
    if spec["seqkind"] == "random":
        rng = T._rng(spec, "random")                 # same sequence as the Tier 2 / Experiment 15 random block
        seq = T.seq_random(int(spec["n_slots"]), rng)
        meta = {}
    else:
        rng = T._rng(spec, "aba")                    # same sequence as Tier 2 T2
        seq, ev = T.seq_aba(int(spec["n_slots"]), 0.1, rng)
        first = int(spec.get("analyse_from", 80))
        meta = dict(rep=[int(i) for i in ev if i >= first],
                    reg=[i for i in range(first, len(seq)) if seq.labels[i] == "A" and seq.labels[i - 1] == "B"])
    p, pp, res = T._run(spec, seq)
    return dict(tones=[int(x) for x in seq.tones], pcounts=_p_counts(res, pp, seq.onsets_ms).tolist(), **meta)
