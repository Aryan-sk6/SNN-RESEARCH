"""Prediction circuit on top of the adaptation network (Experiment 2 and the Tier 2 experiments).

Layers (per predictive channel k; only the channels listed in PredParams.pred_channels get them):

    E_k  sensory cells (the Experiment 1 network, adaptation switchable)
    D_k  tapped delay line: copies of E_k's spikes arriving after lag s * lag_ms (s = 0..n_lags-1)   [component T]
         (T off: one slow-decay trace group per channel instead, so no timing information)
    P_k  prediction cells, driven by D through plastic weights                                         [component L]
    PE+_k  positive-error cells: excited by E_k, inhibited by P_k   (input larger than predicted)     [component E]
    PE-_k  negative-error cells: excited by P_k, inhibited by E_k   (prediction without input)        [component E]

Learning (L): weight D(j, s) -> P_k grows when PE+_k is active (error trace, "teach") while the delay cell has an
eligibility trace; every pre spike applies a small depression. Fully predicted tones give no PE+, so no
learning: errors teach.

Mismatch gate (G, mechanism A): a gate variable that jumps with each PE+ spike, decays with tau_gate and is
cut by Match cells (cells that need E_k and P_k together). While it is up it (i) multiplies the learning rate
(one-shot learning) and (ii) raises the gain of the input -> E synapses (sensitisation).
Candidates (C): while the gate is up three candidate drives onto P: repeat of the tone that just erred
(PE+_k -> P_k), return to the earlier tone (slow regime trace R_k -> P_k) and a non-specific "something new".
Replacement (A1): while the gate is up the old weights are depressed faster.

Every constant is in PredParams and is documented in docs/PARAMETERS.md. Nothing here is fitted to a test result.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import brian2 as b2
from brian2 import ms, mV, Hz

from .network import make_lif_group, tone_rate_array
from .params import Adaptation, NetworkParams
from .stimuli import Sequence


@dataclass(frozen=True)
class Mech:
    """Which components are switched on. `None` as a mechanism means adaptation only (no predictive layers)."""

    T: bool = True          # tapped delay line (False: slow trace without timing)
    E: bool = True          # positive and negative error populations
    L: bool = True          # learning of the prediction weights
    G: bool = False         # mismatch gate (fast learning + sensitisation)
    C: bool = False         # candidate predictions while the gate is up
    replace: bool = False   # A1: old predictions are depressed while the gate is up
    slow_eta: bool = True   # learning rate outside the gate window: B-like slow rate (False: none)

    @property
    def label(self) -> str:
        flags = "".join(c for c, f in zip("TELGC", (self.T, self.E, self.L, self.G, self.C)) if f)
        return flags + ("+rep" if self.replace else "")


B_MECH = Mech()
A1_MECH = Mech(G=True, replace=True)
A2B_MECH = Mech(G=True, C=True)


@dataclass(frozen=True)
class PredParams:
    pred_channels: tuple = (3, 6, 8, 1)   # channels with predictive layers (A, B, C, D in the experiments)
    n_p: int = 10                          # cells per P group
    n_pe: int = 10                         # cells per error group
    n_d: int = 4                           # cells per delay group
    n_lags: int = 20                       # delay taps
    lag_ms: float = 50.0                   # spacing of the taps
    n_match: int = 5
    n_trace: int = 5
    sigma_mV: float = 1.5                  # noise of the predictive layers (small: they should be quiet)

    # delay line / trace
    p_ed: float = 0.5
    w_ed_mV: float = 22.0
    tau_trace_e_ms: float = 250.0          # T off: slow synaptic decay of the trace group
    w_trace_mV: float = 2.0

    # prediction weights
    w_max: float = 20.0                    # mV per presynaptic spike, upper bound
    w_init: float = 0.0
    eta: float = 0.0004                    # slow learning rate (per ms, per unit eligibility x teach)
    cd: float = 0.002                      # depression per presynaptic spike
    tau_x_ms: float = 120.0                # eligibility trace of delay cells
    tau_teach_ms: float = 80.0             # error (teach) trace of P cells
    tau_ptr_ms: float = 100.0              # P spike trace used to stop learning once the prediction is active
    ptr_thr: float = 3.0                   # P spikes (within tau_ptr) at which learning stops

    # error populations
    p_pe: float = 0.6
    w_e_pe_mV: float = 18.0                # E -> PE+ excitation
    w_p_pe_mV: float = 30.0                # P -> PE+ inhibition
    w_p_pm_mV: float = 16.0                # P -> PE- excitation
    w_e_pm_mV: float = 40.0                # E -> PE- inhibition
    w_teach: float = 1.0                   # teach increment per PE+ spike

    # gate (mechanism A)
    a_gate: float = 0.02                   # gate increase per PE+ spike
    g_max: float = 2.0
    tau_gate_ms: float = 1500.0
    b_match: float = 0.15                  # gate decrease per Match spike
    kappa_learn: float = 3.0               # learning-rate multiplier per unit gate (one-shot)
    k_gain: float = 0.5                    # input gain increase per unit gate (sensitisation)
    k_replace: float = 6.0                 # A1: extra depression per unit gate
    w_match_mV: float = 5.0
    c_rep_mV: float = 1.5                  # candidate drives (per unit gate)
    c_old_mV: float = 1.5
    c_new_mV: float = 0.4
    w_trace_old_mV: float = 1.5
    tau_regime_ms: float = 3000.0

    def with_(self, **kw) -> "PredParams":
        return replace(self, **kw)


@dataclass
class PredResult:
    e_t: np.ndarray
    e_idx: np.ndarray
    pep_t: np.ndarray
    pep_idx: np.ndarray
    pem_t: np.ndarray
    pem_idx: np.ndarray
    p_t: np.ndarray
    p_idx: np.ndarray
    d_t: np.ndarray
    d_idx: np.ndarray
    g_t: np.ndarray            # gate trace
    g_val: np.ndarray
    w_final: np.ndarray        # (n_pred_src, n_lags, n_pred_dst) mean weight
    pred_channels: tuple
    duration_ms: float
    pp: PredParams


def _blocks(n_groups, per):
    """Index arrays: group id of every cell for n_groups groups of `per` cells."""
    return np.repeat(np.arange(n_groups), per)


def run_predictive(seq: Sequence, p: NetworkParams, adapt: Adaptation, mech: Mech, pp: PredParams, seed: int,
                   record_gate_ms: float = 10.0) -> PredResult:
    if not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if mech is not None:
        if mech.G and not mech.E:
            raise ValueError("the gate is driven by the positive-error cells; G needs E")
        if mech.C and not mech.G:
            raise ValueError("candidates only exist inside the gate window; C needs G")
        if mech.replace and not mech.G:
            raise ValueError("replacement happens inside the gate window; it needs G")
        if mech.G and not mech.L:
            raise ValueError("the gate acts on learning; G needs L")
    chans = tuple(int(c) for c in pp.pred_channels)
    if len(set(chans)) != len(chans) or not all(0 <= c < p.n_channels for c in chans):
        raise ValueError("pred_channels must be distinct valid channels")
    if len(seq) == 0 or int(np.max(seq.tones)) >= p.n_channels:
        raise ValueError("bad sequence")

    nk = len(chans)
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), 7919]))
    b2.start_scope()
    b2.seed(int(seed))
    np.random.seed(int(seed))
    b2.defaultclock.dt = p.dt_ms * ms
    pq = p.with_(sigma_noise_mV=pp.sigma_mV)          # quieter predictive layers

    # ---------------- sensory layer (identical to Experiment 1, plus the sensitisation gain) ----------------
    E = make_lif_group(p.n_exc, p, noise=True, sfa_b_mV=p.sfa_b_mV if adapt.sfa else 0.0, name="E",
                       extra="gainG : 1")
    I = make_lif_group(p.n_inh, p, noise=True, sfa_b_mV=0.0, name="I")
    for g in (E, I):
        g.v = "E_L + rand()*(V_th - E_L)"
    tones = b2.TimedArray(tone_rate_array(seq, p) * Hz, dt=1 * ms, name="tone_rates")
    inp = b2.PoissonGroup(p.n_channels * p.n_in_per_channel, rates="tone_rates(t, i // n_in)",
                          namespace={"n_in": p.n_in_per_channel, "tone_rates": tones}, name="inp")
    ns = dict(n_in=p.n_in_per_channel, n_e=p.n_exc_per_channel, sig=p.tuning_sigma_ch, maxd=p.tuning_max_ch,
              w_in=p.w_in_mV * mV, U=p.tm_U, tau_rec=p.tm_tau_rec_ms * ms, k_gain=pp.k_gain)
    cond = "abs(i // n_in - j // n_e) <= maxd"
    wexpr = "w_in*exp(-((i // n_in - j // n_e)**2)/(2*sig**2))"
    if adapt.depression:
        syn = b2.Synapses(inp, E, model="wsyn : volt\n dx/dt = (1 - x)/tau_rec : 1 (event-driven)",
                          on_pre="Ie_post += wsyn*x*(1 + k_gain*gainG_post)\n x -= U*x", namespace=ns, name="syn_in")
    else:
        syn = b2.Synapses(inp, E, model="wsyn : volt", on_pre="Ie_post += wsyn*(1 + k_gain*gainG_post)",
                          namespace=ns, name="syn_in")
    syn.connect(condition=cond, p=p.p_in)
    syn.wsyn = wexpr
    if adapt.depression:
        syn.x = 1
    ei = b2.Synapses(E, I, on_pre="Ie_post += w_ei", namespace={"w_ei": p.w_ei_mV * mV}, name="syn_ei")
    ei.connect(p=p.p_ei)
    ie = b2.Synapses(I, E, on_pre="Ii_post += w_ie", namespace={"w_ie": p.w_ie_mV * mV}, name="syn_ie")
    ie.connect(p=p.p_ie)
    objs = [E, I, inp, syn, ei, ie]
    mE = b2.SpikeMonitor(E, name="mE")
    objs.append(mE)

    # ---------------- predictive layers ----------------
    npe, npp, ndd = pp.n_pe, pp.n_p, pp.n_d
    cells_E = lambda kk: np.arange(chans[kk] * p.n_exc_per_channel, (chans[kk] + 1) * p.n_exc_per_channel)

    def conn(source, target, pre_idx, post_idx, on_pre, namespace, model="", name=None, p_conn=1.0):
        s = b2.Synapses(source, target, model=model, on_pre=on_pre, namespace=namespace, name=name)
        pre_idx, post_idx = np.meshgrid(pre_idx, post_idx, indexing="ij")
        pre_idx, post_idx = pre_idx.ravel(), post_idx.ravel()
        if p_conn < 1.0:
            keep = rng.random(pre_idx.size) < p_conn
            pre_idx, post_idx = pre_idx[keep], post_idx[keep]
        s.connect(i=pre_idx, j=post_idx)
        return s

    def conn_multi(source, target, blocks, on_pre, namespace, name, p_conn=1.0):
        """One Synapses object for several (pre_indices, post_indices) all-to-all blocks (fewer objects = faster)."""
        ii, jj = [], []
        for pre_idx, post_idx in blocks:
            a, b = np.meshgrid(pre_idx, post_idx, indexing="ij")
            a, b = a.ravel(), b.ravel()
            if p_conn < 1.0:
                keep = rng.random(a.size) < p_conn
                a, b = a[keep], b[keep]
            ii.append(a); jj.append(b)
        s = b2.Synapses(source, target, on_pre=on_pre, namespace=namespace, name=name)
        s.connect(i=np.concatenate(ii), j=np.concatenate(jj))
        return s

    gate_ns = dict(tau_gate=pp.tau_gate_ms * ms, a_gate=pp.a_gate, g_max=pp.g_max, b_match=pp.b_match)
    mPEp = mPEm = mP = mG = mD = None
    wmon = None
    if mech is not None:
        # prediction cells P, with teach trace and gate copy
        P = make_lif_group(nk * npp, pq, noise=True, name="P",
                           extra="dteach/dt = -teach/tau_teach : 1\n dptr/dt = -ptr/tau_ptr : 1\n Gp : 1",
                           extra_ns=dict(tau_teach=pp.tau_teach_ms * ms, tau_ptr=pp.tau_ptr_ms * ms, c_new=pp.c_new_mV * mV),
                           reset_extra="ptr += 1",
                           drive_extra=("c_new*Gp" if mech.C else ""))
        P.v = "E_L"
        objs.append(P)
        pcells = lambda kk: np.arange(kk * npp, (kk + 1) * npp)

        # delay line or trace
        if mech.T:
            nd = nk * pp.n_lags * ndd
            D = make_lif_group(nd, pq, noise=True, name="D", extra="dxp/dt = -xp/tau_x : 1",
                               extra_ns=dict(tau_x=pp.tau_x_ms * ms), reset_extra="xp += 1")
            D.v = "E_L"
            objs.append(D)
            dcells = lambda kk, s: np.arange(((kk * pp.n_lags) + s) * ndd, ((kk * pp.n_lags) + s + 1) * ndd)
            pre_i, post_j, dly = [], [], []
            for kk in range(nk):
                for s in range(pp.n_lags):
                    pi_, pj_ = np.meshgrid(cells_E(kk), dcells(kk, s), indexing="ij")
                    pi_, pj_ = pi_.ravel(), pj_.ravel()
                    keep = rng.random(pi_.size) < pp.p_ed
                    pre_i.append(pi_[keep]); post_j.append(pj_[keep])
                    dly.append(np.full(keep.sum(), s * pp.lag_ms))
            sED = b2.Synapses(E, D, on_pre="Ie_post += w_ed", namespace={"w_ed": pp.w_ed_mV * mV}, name="sED")
            sED.connect(i=np.concatenate(pre_i), j=np.concatenate(post_j))
            sED.delay = np.concatenate(dly) * ms
            objs += [sED]
            n_src_per_k = pp.n_lags
            src_cells = lambda kk, s: dcells(kk, s)
        else:
            nd = nk * pp.n_trace
            D = make_lif_group(nd, pq.with_(tau_e_ms=pp.tau_trace_e_ms), noise=True, name="D",
                               extra="dxp/dt = -xp/tau_x : 1",
                               extra_ns=dict(tau_x=pp.tau_x_ms * ms, tau_e=pp.tau_trace_e_ms * ms),
                               reset_extra="xp += 1")
            D.v = "E_L"
            objs.append(D)
            tcells = lambda kk: np.arange(kk * pp.n_trace, (kk + 1) * pp.n_trace)
            # explicit per-channel wiring: E_k -> trace_k
            sED = b2.Synapses(E, D, on_pre="Ie_post += w_tr", namespace={"w_tr": pp.w_trace_mV * mV}, name="sED")
            ii, jj = [], []
            for kk in range(nk):
                a, b = np.meshgrid(cells_E(kk), tcells(kk), indexing="ij")
                ii.append(a.ravel()); jj.append(b.ravel())
            sED.connect(i=np.concatenate(ii), j=np.concatenate(jj))
            objs += [sED]
            n_src_per_k = 1
            src_cells = lambda kk, s: tcells(kk)

        # plastic weights D -> P
        plastic_ns = dict(w_max=pp.w_max, cd=pp.cd, kappa=pp.kappa_learn, k_rep=pp.k_replace, pthr=pp.ptr_thr,
                          eta=pp.eta if mech.slow_eta else 0.0)
        use_gate_learn = mech.G
        on_pre = "Ie_post += wp*mV\n wp = clip(wp - cd*(1 + k_rep*Gp_post*%s), 0, w_max)" % ("1" if mech.replace else "0")
        sDP = b2.Synapses(D, P, model="wp : 1", on_pre=on_pre, namespace=plastic_ns, name="sDP")
        ii, jj = [], []
        for kk in range(nk):
            for s in range(n_src_per_k):
                for kd in range(nk):
                    a, b = np.meshgrid(src_cells(kk, s), pcells(kd), indexing="ij")
                    ii.append(a.ravel()); jj.append(b.ravel())
        sDP.connect(i=np.concatenate(ii), j=np.concatenate(jj))
        sDP.wp = pp.w_init
        if mech.L:
            gate_term = "(1 + kappa*Gp_post)" if use_gate_learn else "1"
            sDP.run_regularly("wp = clip(wp + eta*%s*xp_pre*teach_post*clip(1 - ptr_post/pthr, 0, 1), 0, w_max)" % gate_term, dt=1 * ms)
        objs.append(sDP)

        mP = b2.SpikeMonitor(P, name="mP")
        mD = b2.SpikeMonitor(D, name="mD")
        objs += [mP, mD]

        if mech.E:
            PEp = make_lif_group(nk * npe, pq, noise=True, name="PEp")
            PEm = make_lif_group(nk * npe, pq, noise=True, name="PEm")
            PEp.v = "E_L"; PEm.v = "E_L"
            objs += [PEp, PEm]
            ecells = lambda kk: np.arange(kk * npe, (kk + 1) * npe)
            wns = dict(w_e=pp.w_e_pe_mV * mV, w_p=pp.w_p_pe_mV * mV, w_pm=pp.w_p_pm_mV * mV, w_em=pp.w_e_pm_mV * mV)
            kks = range(nk)
            objs.append(conn_multi(E, PEp, [(cells_E(k), ecells(k)) for k in kks], "Ie_post += w_e", wns, "s_e_pep", pp.p_pe))
            objs.append(conn_multi(P, PEp, [(pcells(k), ecells(k)) for k in kks], "Ii_post += w_p", wns, "s_p_pep", pp.p_pe))
            objs.append(conn_multi(P, PEm, [(pcells(k), ecells(k)) for k in kks], "Ie_post += w_pm", wns, "s_p_pem", pp.p_pe))
            objs.append(conn_multi(E, PEm, [(cells_E(k), ecells(k)) for k in kks], "Ii_post += w_em", wns, "s_e_pem", pp.p_pe))
            # error teaches the prediction cells of the same channel
            objs.append(conn_multi(PEp, P, [(ecells(k), pcells(k)) for k in kks], "teach_post += w_teach",
                                   dict(w_teach=pp.w_teach), "s_teach"))
            mPEp = b2.SpikeMonitor(PEp, name="mPEp")
            mPEm = b2.SpikeMonitor(PEm, name="mPEm")
            objs += [mPEp, mPEm]

        if mech.G:
            Gate = b2.NeuronGroup(1, "dG/dt = -G/tau_gate : 1", method="euler", namespace=gate_ns, name="Gate")
            Gate.G = 0
            objs.append(Gate)
            sg = b2.Synapses(PEp, Gate, on_pre="G_post = clip(G_post + a_gate, 0, g_max)", namespace=gate_ns, name="s_gate")
            sg.connect()
            objs.append(sg)
            sgp = b2.Synapses(Gate, P, model="Gp_post = G_pre : 1 (summed)", name="s_gp")
            sgp.connect()
            sge = b2.Synapses(Gate, E, model="gainG_post = G_pre : 1 (summed)", name="s_ge")
            sge.connect()
            objs += [sgp, sge]
            # Match cells: need E_k and P_k together; they cut the gate
            M = make_lif_group(nk * pp.n_match, pq, noise=True, name="Match")
            M.v = "E_L"
            objs.append(M)
            mcells = lambda kk: np.arange(kk * pp.n_match, (kk + 1) * pp.n_match)
            mns = dict(w_m=pp.w_match_mV * mV)
            objs.append(conn_multi(E, M, [(cells_E(k), mcells(k)) for k in range(nk)], "Ie_post += w_m*0.1", mns, "s_e_m", 0.5))
            objs.append(conn_multi(P, M, [(pcells(k), mcells(k)) for k in range(nk)], "Ie_post += w_m", mns, "s_p_m", 0.5))
            sm = b2.Synapses(M, Gate, on_pre="G_post = clip(G_post - b_match, 0, g_max)", namespace=gate_ns, name="s_match")
            sm.connect()
            objs.append(sm)
            gmon = b2.StateMonitor(Gate, "G", record=0, dt=record_gate_ms * ms, name="gmon")
            objs.append(gmon)
            mG = gmon
            if mech.C:
                cns = dict(c_rep=pp.c_rep_mV * mV, c_old=pp.c_old_mV * mV)
                # repeat candidate: the tone that just erred is predicted again (PE+ -> P, scaled by the gate)
                objs.append(conn_multi(PEp, P, [(ecells(k), pcells(k)) for k in range(nk)], "Ie_post += c_rep*Gp_post", cns, "s_rep", 0.5))
                # return candidate: slow regime trace of each channel drives its own P group
                R = make_lif_group(nk * pp.n_trace, pq.with_(tau_e_ms=pp.tau_regime_ms), noise=True, name="R",
                                   extra_ns=dict(tau_e=pp.tau_regime_ms * ms))
                R.v = "E_L"
                objs.append(R)
                rcells = lambda kk: np.arange(kk * pp.n_trace, (kk + 1) * pp.n_trace)
                objs.append(conn_multi(E, R, [(cells_E(k), rcells(k)) for k in range(nk)], "Ie_post += w_old",
                                       dict(w_old=pp.w_trace_old_mV * mV), "s_e_r", 0.5))
                objs.append(conn_multi(R, P, [(rcells(k), pcells(k)) for k in range(nk)], "Ie_post += c_old*Gp_post", cns, "s_old", 0.5))

        wmon = (sDP, n_src_per_k)

    net = b2.Network(*objs)
    net.run(seq.duration_ms * ms)

    def sp(m):
        return (np.asarray(m.t / ms), np.asarray(m.i)) if m is not None else (np.array([]), np.array([], dtype=int))
    e_t, e_idx = sp(mE)
    pep_t, pep_idx = sp(mPEp)
    pem_t, pem_idx = sp(mPEm)
    p_t, p_idx = sp(mP)
    d_t, d_idx = sp(mD)
    if mG is not None:
        g_t, g_val = np.asarray(mG.t / ms), np.asarray(mG.G[0])
    else:
        g_t, g_val = np.array([]), np.array([])
    if wmon is not None:
        sDP, nspk = wmon
        w = np.asarray(sDP.wp[:])
        # reshape mean weights as (source channel, lag, destination channel): same ordering as the connection loops
        per = (len(w) // (nk * nspk * nk))
        w_final = w.reshape(nk, nspk, nk, per).mean(axis=3)
    else:
        w_final = np.zeros((nk, 1, nk))
    return PredResult(e_t, e_idx, pep_t, pep_idx, pem_t, pem_idx, p_t, p_idx, d_t, d_idx, g_t, g_val, w_final, chans,
                      float(seq.duration_ms), pp)
