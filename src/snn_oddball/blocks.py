"""One simulated block -> a few numbers. A "spec" is a plain dict so it can be hashed, cached and
sent to worker processes. Responses are UNCLIPPED baseline-corrected mean spike counts of the 10 E
cells of one channel (see analysis.py)."""

from __future__ import annotations

import zlib

import numpy as np

from . import analysis as A
from . import network as N
from . import params as P
from . import stimuli as S

ADAPT = {"none": P.NONE, "sfa": P.SFA, "std": P.STD, "both": P.BOTH}


def _isi(spec):
    isi = spec["isi"]
    return tuple(isi) if isinstance(isi, (list, tuple)) else float(isi)


def _rng(spec):
    key = repr(sorted((k, repr(v)) for k, v in spec.items() if k != "seed"))
    return np.random.default_rng(np.random.SeedSequence([int(spec["seed"]), zlib.crc32(key.encode())]))


def run_block(spec: dict) -> dict:
    if spec.get("kind") == "pred":
        from .tier2 import run_pred_block
        return run_pred_block(spec)
    if spec.get("kind") == "x1315":
        from .exp13_15 import run_block as rb
        return rb(spec)
    if spec.get("kind") == "retune_calib":
        from .retune import calib_block
        return calib_block(spec)
    p = P.NetworkParams(**(spec.get("net") or {}))
    adapt = ADAPT[spec["adapt"]]
    seed = int(spec["seed"])
    rng = _rng(spec)
    kind = spec["kind"]
    isi = _isi(spec)
    nt = int(spec["n_trials"])

    if kind == "odd":       # standard channel `std`, deviant channel `dev`
        seq = S.oddball(spec["std"], spec["dev"], nt, spec["p_dev"], p.n_channels, rng, isi_ms=isi,
                        min_std_before_dev=int(spec.get("min_std", 3)))
        res = N.run_sequence(seq, p, adapt, seed)
        dev_idx = np.where(seq.labels == "dev")[0]
        std_idx = A.last_standard_before_deviant(seq.labels)
        return dict(dev=A.role_response(res, seq, p, spec["dev"], dev_idx, clip=False),
                    std=A.role_response(res, seq, p, spec["std"], std_idx, clip=False),
                    n_dev=int(len(dev_idx)), n_std=int(len(std_idx)))

    if kind == "ctrl":      # target channel inside a control sequence
        if spec["style"] == "many":
            seq = S.many_standards(spec["target"], spec["n_tones"], nt, p.n_channels, rng, isi_ms=isi)
        elif spec["style"] == "cascade":
            seq = S.cascade(spec["target"], spec["n_tones"], nt, p.n_channels, rng, isi_ms=isi)
        else:
            raise ValueError(f"unknown control style {spec['style']!r}")
        res = N.run_sequence(seq, p, adapt, seed)
        idx = np.where(seq.labels == "ctr")[0]
        return dict(ctr=A.role_response(res, seq, p, spec["target"], idx, clip=False), n_ctr=int(len(idx)))

    if kind == "omit":      # repeated tone with omitted slots
        seq = S.omission_sequence(spec["tone"], nt, spec["p_omit"], p.n_channels, rng, isi_ms=isi)
        res = N.run_sequence(seq, p, adapt, seed)
        om = np.where(seq.labels == "omit")[0]
        # tones that are not right after an omission, so adaptation history is comparable
        pr = np.array([i for i in np.where(seq.labels == "std")[0] if i >= 10 and (i - 1) not in set(om)])
        w_o, b_o = A.trial_counts(res, p, seq.onsets_ms[om], spec["tone"])
        return dict(tone=A.role_response(res, seq, p, spec["tone"], pr, clip=False),
                    omit=A.role_response(res, seq, p, spec["tone"], om, clip=False),
                    omit_win=float(w_o.mean()), omit_base=float(b_o.mean()), n_omit=int(len(om)))

    raise ValueError(f"unknown block kind {kind!r}")
