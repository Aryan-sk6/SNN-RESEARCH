"""Sequences, measures and block runners for the Tier 2 experiments (see docs/PREREGISTRATION_TIER2.md).

Each block runner takes a plain-dict spec and returns a dict of numbers/lists (JSON-serialisable), so blocks can
be cached and run in parallel by runner.py.
"""

from __future__ import annotations

import numpy as np

from . import predictive as PR
from . import stimuli as S
from .params import ADAPT_BY_LABEL, NetworkParams
from .stimuli import OMIT, Sequence

A_CH, B_CH, C_CH, D_CH = 3, 6, 8, 1
PRED_CHANNELS = (A_CH, B_CH, C_CH, D_CH)
DT_MS = 0.5
WIN = (0.0, 180.0)
BASE = (-75.0, 0.0)

NETS = {"N0": None, "B": PR.B_MECH, "A1": PR.A1_MECH, "A2b": PR.A2B_MECH}


def mech_from_spec(spec):
    if isinstance(spec.get("mech"), dict):
        return PR.Mech(**spec["mech"])
    return NETS[spec["net"]]


def pred_params(spec) -> PR.PredParams:
    return PR.PredParams(pred_channels=PRED_CHANNELS, **spec.get("pp", {}))


def net_params() -> NetworkParams:
    return NetworkParams(dt_ms=DT_MS)


# ------------------------------------------------------------------ sequence building
def build(items, isi_ms, pulse_ms, rng, jitter=0.0, tail_ms=500.0, lead_ms=300.0):
    """items: list of (tone_or_OMIT, label, gap_before_ms). Returns a Sequence."""
    if not items:
        raise ValueError("no items")
    if not 0.0 <= jitter < 1.0:
        raise ValueError("jitter must be in [0, 1)")
    onsets, tones, labels = [], [], []
    t = float(lead_ms)
    for tone, label, gap in items:
        t += float(gap)
        onsets.append(t); tones.append(int(tone)); labels.append(label)
        isi = isi_ms * (1.0 + jitter * rng.uniform(-1.0, 1.0)) if jitter > 0 else isi_ms
        t += pulse_ms + isi
    return Sequence(np.asarray(onsets), np.asarray(tones, dtype=int), np.asarray(labels, dtype=object),
                    float(pulse_ms), float(t + tail_ms))


def choose_slots(n_slots, n_pick, rng, start, min_sep):
    """n_pick slot indices in [start, n_slots) with pairwise separation >= min_sep."""
    pool = list(range(start, n_slots))
    out = []
    while len(out) < n_pick and pool:
        c = pool[int(rng.integers(len(pool)))]
        out.append(c)
        pool = [x for x in pool if abs(x - c) >= min_sep]
    if len(out) < n_pick:
        raise ValueError("could not place the requested number of events")
    return sorted(out)


def seq_omission(n_slots, p_omit, rng, isi=400.0, jitter=0.0, tone=A_CH):
    om = set(choose_slots(n_slots, int(round(p_omit * n_slots)), rng, 10, 2))
    items = [(OMIT if i in om else tone, "omit" if i in om else "tone", 0.0) for i in range(n_slots)]
    return build(items, isi, 50.0, rng, jitter), sorted(om)


def seq_aba(n_slots, p_repl, rng, isi=400.0):
    b_slots = [i for i in range(n_slots) if i % 2 == 1]
    ev = set(choose_slots(len(b_slots), int(round(p_repl * len(b_slots))), rng, 3, 6))   # >= 6 alternations apart
    ev_slots = {b_slots[k] for k in ev}
    items = []
    for i in range(n_slots):
        if i % 2 == 0:
            items.append((A_CH, "A", 0.0))
        elif i in ev_slots:
            items.append((A_CH, "rep", 0.0))
        else:
            items.append((B_CH, "B", 0.0))
    return build(items, isi, 50.0, rng), sorted(ev_slots)


CONT = {"A": [A_CH], "B": [B_CH], "C": [C_CH], "cycABC": [C_CH, A_CH, B_CH], "cycABCB": [C_CH, B_CH, A_CH, B_CH]}


def seq_episodes(cont, n_ep, m, rng, isi=400.0, gap_ms=3000.0):
    """Episodes: A x n_pre, one B, then m continuation tones. Returns (Sequence, meta)."""
    items, meta = [], dict(init=[], pre1=[], dev=[], post=[])
    for e in range(n_ep):
        n_pre = int(rng.integers(6, 10))
        first = len(items)
        for k in range(n_pre):
            items.append((A_CH, f"e{e}:init{k}", gap_ms if (k == 0 and e > 0) else 0.0))
        meta["init"].append(list(range(first, first + 6)))
        meta["pre1"].append(len(items) - 1)
        meta["dev"].append(len(items))
        items.append((B_CH, f"e{e}:dev", 0.0))
        post = []
        for k in range(m):
            if cont == "random":
                tone = int(PRED_CHANNELS[int(rng.integers(len(PRED_CHANNELS)))])
            else:
                cyc = CONT[cont]
                tone = cyc[k % len(cyc)]
            post.append(len(items))
            items.append((tone, f"e{e}:post{k + 1}", 0.0))
        meta["post"].append(post)
    return build(items, isi, 50.0, rng), meta


def seq_oneshot(n_pairs, rng, gap_ms=8000.0, isi=400.0):
    items = []
    for k in range(n_pairs):
        items.append((A_CH, f"p{k}:A", gap_ms if k > 0 else 0.0))
        items.append((B_CH, f"p{k}:B", 0.0))
    return build(items, isi, 50.0, rng)


def seq_buildup(ns, eps_per_n, rng, gap_ms=5000.0, isi=400.0):
    order = [n for n in ns for _ in range(eps_per_n)]
    rng.shuffle(order)
    items, meta = [], []
    for e, n in enumerate(order):
        for k in range(n):
            items.append((A_CH, f"e{e}:t{k}", gap_ms if (k == 0 and e > 0) else 0.0))
        meta.append((n, len(items)))
        items.append((OMIT, f"e{e}:om", 0.0))
    return build(items, isi, 50.0, rng), meta


def seq_random(n_slots, rng, isi=400.0):
    items = [(int(PRED_CHANNELS[int(rng.integers(len(PRED_CHANNELS)))]), "r", 0.0) for _ in range(n_slots)]
    return build(items, isi, 50.0, rng)


def seq_decomp(kind, n_trials, p_dev, rng, isi=400.0):
    if kind == "oddA":
        s = S.oddball(A_CH, B_CH, n_trials, p_dev, 10, rng, isi_ms=isi, min_std_before_dev=2)
    elif kind == "oddB":
        s = S.oddball(B_CH, A_CH, n_trials, p_dev, 10, rng, isi_ms=isi, min_std_before_dev=2)
    else:
        tset = sorted(PRED_CHANNELS)
        if kind == "many":
            order = []
            while len(order) < n_trials:
                blk = list(rng.permutation(tset))
                while order and blk[0] == order[-1]:
                    blk = list(rng.permutation(tset))
                order += blk
            order = order[:n_trials]
        elif kind == "cascade":
            order = [tset[i % len(tset)] for i in range(n_trials)]
        else:
            raise ValueError(kind)
        items = [(t, "ctr" if t == B_CH else "oth", 0.0) for t in order]
        return build(items, isi, 50.0, rng)
    items = [(int(t), str(l), 0.0) for t, l in zip(s.tones, s.labels)]
    return build(items, isi, 50.0, rng)


# ------------------------------------------------------------------ measures
def _cnt(tt, onsets, lo, hi):
    return np.searchsorted(tt, onsets + hi, side="left") - np.searchsorted(tt, onsets + lo, side="left")


def parts(res, p, pp, chan, onsets):
    """Per-onset baseline-corrected spike counts of the channel's E, PE+ and PE- cells, and their sum R."""
    onsets = np.asarray(onsets, dtype=float)
    kk = list(pp.pred_channels).index(chan) if chan in pp.pred_channels else None
    scale = (WIN[1] - WIN[0]) / (BASE[1] - BASE[0])
    out = {}
    for name, (t, idx, per) in dict(E=(res.e_t, res.e_idx, p.n_exc_per_channel), PEp=(res.pep_t, res.pep_idx, pp.n_pe),
                                    PEm=(res.pem_t, res.pem_idx, pp.n_pe)).items():
        if name == "E":
            sel = (idx // per) == chan
        else:
            sel = ((idx // per) == kk) if kk is not None else np.zeros(len(idx), dtype=bool)
        tt = np.sort(t[sel])
        out[name] = _cnt(tt, onsets, *WIN) - _cnt(tt, onsets, *BASE) * scale
    out["R"] = out["E"] + out["PEp"] + out["PEm"]
    return out


def pem_raw(res, pp, chan, onsets, quiet=(-250.0, -175.0)):
    """Anticipation-robust negative-error measures: raw PE- count in 0-180 ms, and the same minus a quiet
    baseline (-250..-175 ms, i.e. 200-275 ms after the previous tone, before any predicted onset)."""
    onsets = np.asarray(onsets, dtype=float)
    if chan not in pp.pred_channels:
        z = np.zeros(len(onsets)); return z, z
    kk = list(pp.pred_channels).index(chan)
    tt = np.sort(res.pem_t[(res.pem_idx // pp.n_pe) == kk])
    raw = _cnt(tt, onsets, *WIN).astype(float)
    scale = (WIN[1] - WIN[0]) / (quiet[1] - quiet[0])
    return raw, raw - _cnt(tt, onsets, *quiet) * scale


def raw_counts(res, p, pp, chan, onsets, lo=0.0, hi=180.0):
    """Raw (no baseline) spike counts in [lo, hi] ms after each onset: sensory E cells of `chan`, and the PE+ / PE-
    populations of `chan` (zeros if the channel has no error cells)."""
    onsets = np.asarray(onsets, dtype=float)
    out = {}
    e = np.sort(res.e_t[(res.e_idx // p.n_exc_per_channel) == chan])
    out["E"] = _cnt(e, onsets, lo, hi).astype(float)
    if chan in pp.pred_channels:
        kk = list(pp.pred_channels).index(chan)
        for name, t, idx in (("PEp", res.pep_t, res.pep_idx), ("PEm", res.pem_t, res.pem_idx)):
            out[name] = _cnt(np.sort(t[(idx // pp.n_pe) == kk]), onsets, lo, hi).astype(float)
    else:
        out["PEp"] = np.zeros(len(onsets)); out["PEm"] = np.zeros(len(onsets))
    return out


def total_error(res, onsets):
    onsets = np.asarray(onsets, dtype=float)
    tt = np.sort(np.concatenate([res.pep_t, res.pem_t]))
    return _cnt(tt, onsets, *WIN).astype(float)


def pred_spikes(res, pp, chan, onsets, lo=-100.0, hi=180.0):
    onsets = np.asarray(onsets, dtype=float)
    if chan not in pp.pred_channels:
        return np.zeros(len(onsets))
    kk = list(pp.pred_channels).index(chan)
    tt = np.sort(res.p_t[(res.p_idx // pp.n_p) == kk])
    return _cnt(tt, onsets, lo, hi).astype(float)


def gate_at(res, times):
    if res.g_t.size == 0:
        return np.full(len(times), np.nan)
    return np.interp(np.asarray(times, dtype=float), res.g_t, res.g_val)


def _mean(x):
    x = np.asarray(x, dtype=float)
    return float(x.mean()) if x.size else float("nan")


def _run(spec, seq):
    p, pp = net_params(), pred_params(spec)
    return p, pp, PR.run_predictive(seq, p, ADAPT_BY_LABEL[spec.get("adapt", "both")], mech_from_spec(spec), pp,
                                     int(spec["seed"]))


def _rng(spec, tag):
    import zlib
    return np.random.default_rng(np.random.SeedSequence([int(spec["seed"]), zlib.crc32(tag.encode())]))


# ------------------------------------------------------------------ block runners
def run_omit(spec):
    rng = _rng(spec, "omit")
    seq, om = seq_omission(int(spec["n_slots"]), 0.2, rng, jitter=float(spec.get("jitter", 0.0)))
    p, pp, res = _run(spec, seq)
    lab = seq.labels
    n = len(seq)
    first = int(spec.get("analyse_from", 60))
    om = [i for i in om if i >= first]
    pres = [i for i in range(first, n) if lab[i] == "tone" and lab[i - 1] == "tone"]
    post = [i for i in range(first, n) if lab[i] == "tone" and lab[i - 1] == "omit"]
    ons = seq.onsets_ms
    po, pr, pq = parts(res, p, pp, A_CH, ons[om]), parts(res, p, pp, A_CH, ons[pres]), parts(res, p, pp, A_CH, ons[post])
    ro, rp = raw_counts(res, p, pp, A_CH, ons[om]), raw_counts(res, p, pp, A_CH, ons[pres])
    ref = raw_counts(res, p, pp, A_CH, ons[pres], 60.0, 240.0)
    v3 = dict(v3_PEm_omit=_mean(ro["PEm"]), v3_PEm_pres=_mean(rp["PEm"]),
              v3_err_omit=_mean(ro["PEp"] + ro["PEm"]), v3_err_pres=_mean(rp["PEp"] + rp["PEm"]),
              v3_E_omit=_mean(ro["E"]), v3_E_ref=_mean(ref["E"]))
    return dict(n_omit=len(om), n_pres=len(pres), n_post=len(post), **v3,
                **{f"omit_{k}": _mean(v) for k, v in po.items()}, **{f"pres_{k}": _mean(v) for k, v in pr.items()},
                **{f"post_{k}": _mean(v) for k, v in pq.items()},
                omit_P_pre=_mean(pred_spikes(res, pp, A_CH, ons[om])),
                omit_PEm_raw=_mean(pem_raw(res, pp, A_CH, ons[om])[0]), omit_PEm_q=_mean(pem_raw(res, pp, A_CH, ons[om])[1]),
                pres_PEm_q=_mean(pem_raw(res, pp, A_CH, ons[pres])[1]))


def run_aba(spec):
    rng = _rng(spec, "aba")
    seq, ev = seq_aba(int(spec["n_slots"]), 0.1, rng)
    p, pp, res = _run(spec, seq)
    lab, ons = seq.labels, seq.onsets_ms
    first = int(spec.get("analyse_from", 80))
    ev = [i for i in ev if i >= first]
    reg = [i for i in range(first, len(seq)) if lab[i] == "A" and lab[i - 1] == "B"]
    pe, pg = parts(res, p, pp, A_CH, ons[ev]), parts(res, p, pp, A_CH, ons[reg])
    return dict(n_rep=len(ev), n_reg=len(reg), **{f"rep_{k}": _mean(v) for k, v in pe.items()},
                **{f"reg_{k}": _mean(v) for k, v in pg.items()})


def run_episodes(spec):
    rng = _rng(spec, "ep:" + spec["cont"])
    n_ep, m = int(spec["n_ep"]), int(spec["m"])
    seq, meta = seq_episodes(spec["cont"], n_ep, m, rng)
    p, pp, res = _run(spec, seq)
    ons, tones = seq.onsets_ms, seq.tones

    def resp(idx_lists, chan_of=lambda i: A_CH):
        return [parts(res, p, pp, chan_of(i), ons[[i]])["R"][0] for i in idx_lists]
    out = {}
    out["R_init"] = [_mean([parts(res, p, pp, A_CH, ons[[meta["init"][e][k]]])["R"][0] for e in range(n_ep)]) for k in range(6)]
    out["R_pre1"] = _mean(resp(meta["pre1"]))
    out["E_pre1"] = _mean([parts(res, p, pp, A_CH, ons[[i]])["E"][0] for i in meta["pre1"]])
    out["R_dev"] = _mean(resp(meta["dev"], lambda i: B_CH))
    out["R_post"], out["E_post"], out["err_post"], out["gate_post1_1s"] = [], [], [], None
    for k in range(m):
        idxs = [meta["post"][e][k] for e in range(n_ep)]
        rr = [parts(res, p, pp, int(tones[i]), ons[[i]]) for i in idxs]
        out["R_post"].append(_mean([r["R"][0] for r in rr]))
        out["E_post"].append(_mean([r["E"][0] for r in rr]))
        out["err_post"].append(_mean(total_error(res, ons[idxs])))
    p1 = [meta["post"][e][0] for e in range(n_ep)]
    out["gate_post1_1s"] = _mean(gate_at(res, ons[p1] + 1000.0))
    out["gate_dev"] = _mean(gate_at(res, ons[meta["dev"]] + 100.0))
    return out


def run_oneshot(spec):
    rng = _rng(spec, "oneshot")
    n_pairs = int(spec["n_pairs"])
    seq = seq_oneshot(n_pairs, rng)
    p, pp, res = _run(spec, seq)
    iB = np.arange(1, 2 * n_pairs, 2)
    pb = parts(res, p, pp, B_CH, seq.onsets_ms[iB])
    return dict(R_B=[float(x) for x in pb["R"]], PEp_B=[float(x) for x in pb["PEp"]], E_B=[float(x) for x in pb["E"]],
                P_pre=[float(x) for x in pred_spikes(res, pp, B_CH, seq.onsets_ms[iB])])


def run_buildup(spec):
    rng = _rng(spec, "buildup")
    ns = spec["ns"]
    seq, meta = seq_buildup(ns, int(spec["eps_per_n"]), rng)
    p, pp, res = _run(spec, seq)
    out = {}
    for n in ns:
        idx = [i for (nn, i) in meta if nn == n]
        pm = parts(res, p, pp, A_CH, seq.onsets_ms[idx])
        out[f"R_{n}"] = _mean(pm["R"]); out[f"PEm_{n}"] = _mean(pm["PEm"])
        last = [i - 1 for i in idx]
        out[f"v3_PEm_{n}"] = _mean(raw_counts(res, p, pp, A_CH, seq.onsets_ms[idx])["PEm"])
        out[f"v3_PEm_last_{n}"] = _mean(raw_counts(res, p, pp, A_CH, seq.onsets_ms[last])["PEm"])
    return out


def run_decomp(spec):
    rng = _rng(spec, "decomp:" + spec["seqkind"])
    seq = seq_decomp(spec["seqkind"], int(spec["n_trials"]), float(spec["p_dev"]), rng)
    p, pp, res = _run(spec, seq)
    lab, ons = seq.labels, seq.onsets_ms
    if spec["seqkind"] == "oddA":
        idx = [i for i in range(len(seq)) if lab[i] == "dev"]
    elif spec["seqkind"] == "oddB":
        idx = [i for i in range(1, len(seq)) if lab[i] == "dev" and lab[i - 1] == "std"]
        idx = [i - 1 for i in idx]
    else:
        idx = [i for i in range(len(seq)) if lab[i] == "ctr"]
    pm = parts(res, p, pp, B_CH, ons[idx])
    return dict(n=len(idx), R=_mean(pm["R"]), E=_mean(pm["E"]), PEp=_mean(pm["PEp"]), PEm=_mean(pm["PEm"]))


def run_random(spec):
    rng = _rng(spec, "random")
    seq = seq_random(int(spec["n_slots"]), rng)
    p, pp, res = _run(spec, seq)
    n = len(seq)
    half = n // 2
    err = total_error(res, seq.onsets_ms)
    return dict(err_first=_mean(err[:half]), err_second=_mean(err[half:]),
                R_second=_mean(np.concatenate([parts(res, p, pp, c, seq.onsets_ms[[i for i in range(half, n) if seq.tones[i] == c]])["R"]
                                                for c in PRED_CHANNELS])))


RUNNERS = dict(omit=run_omit, aba=run_aba, ep=run_episodes, oneshot=run_oneshot, buildup=run_buildup,
               decomp=run_decomp, random=run_random)


def run_pred_block(spec: dict) -> dict:
    fn = RUNNERS.get(spec["exp"])
    if fn is None:
        raise ValueError(f"unknown predictive experiment {spec['exp']!r}")
    return fn(spec)
