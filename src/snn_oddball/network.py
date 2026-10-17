"""The Brian2 network: 100 E + 20 I leaky integrate-and-fire cells, 10 tone channels.

Structure (feedforward + feedback inhibition, no E->E recurrence):

    Poisson input units (per channel) --(tuned, optionally TM-depressing)--> E cells
    E cells --> I cells --> E cells                                         (feedback inhibition)

Units: the membrane potential and all synaptic "currents" are expressed in mV (a current-based
model with the membrane resistance absorbed). A synaptic jump `w` into `Ie` depolarises the cell
by roughly w * tau_e / tau_m mV per input spike.

Adaptation is switchable and independent:
  (a) spike-frequency adaptation: an adaptation variable w (mV) that is incremented at each E spike
      and decays with tau_w; it enters the membrane equation with a minus sign.
  (b) short-term depression (Tsodyks-Markram form with utilisation U fixed, i.e. facilitation omitted)
      on the input -> E synapses. Efficacy of a spike = wsyn * x, where the resource x is reduced by
      U*x per spike and recovers with tau_rec. In Tsodyks-Markram notation the absolute strength is
      A = wsyn / U, so the FIRST spike after full recovery has the same efficacy wsyn with or without
      depression, and the conditions differ only in how efficacy falls with repeated spikes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import brian2 as b2
from brian2 import ms, mV, Hz

from .params import Adaptation, NetworkParams
from .stimuli import OMIT, Sequence

try:  # compiled code is much faster; fall back silently if no compiler is available
    b2.prefs.codegen.target = "cython"
except Exception:  # pragma: no cover
    b2.prefs.codegen.target = "numpy"
b2.prefs.codegen.cpp.extra_compile_args_gcc = ["-O2"]


def lif_equations(noise: bool) -> str:
    """Membrane equation shared by E and I cells (and by the analytic-rate unit test)."""
    drive = "E_L - v + Ie - Ii + I_ext - w"
    if noise:
        drive += " + sigma_noise*sqrt(2*tau_m)*xi"
    return f"""
    dv/dt = ({drive})/tau_m : volt (unless refractory)
    dIe/dt = -Ie/tau_e : volt
    dIi/dt = -Ii/tau_i : volt
    dw/dt = -w/tau_w : volt
    I_ext : volt (constant)
    """


def lif_namespace(p: NetworkParams, sfa_b_mV: float = 0.0) -> dict:
    return dict(
        E_L=p.E_L_mV * mV, V_th=p.V_th_mV * mV, V_reset=p.V_reset_mV * mV,
        tau_m=p.tau_m_ms * ms, tau_e=p.tau_e_ms * ms, tau_i=p.tau_i_ms * ms,
        tau_w=p.tau_w_ms * ms, sigma_noise=p.sigma_noise_mV * mV, sfa_b=sfa_b_mV * mV,
    )


def make_lif_group(n, p: NetworkParams, noise: bool, sfa_b_mV: float = 0.0, name="lif"):
    """A NeuronGroup of LIF cells. Used by the network and by the analytic-rate unit test."""
    g = b2.NeuronGroup(
        n, lif_equations(noise), threshold="v > V_th", reset="v = V_reset; w += sfa_b",
        refractory=p.t_ref_ms * ms, method="euler", namespace=lif_namespace(p, sfa_b_mV), name=name)
    g.v = p.V_reset_mV * mV
    return g


@dataclass
class RunResult:
    e_t_ms: np.ndarray     # E spike times (ms)
    e_idx: np.ndarray      # E cell index (channel = idx // n_exc_per_channel)
    i_t_ms: np.ndarray
    i_idx: np.ndarray
    duration_ms: float


def tone_rate_array(seq: Sequence, p: NetworkParams) -> np.ndarray:
    """(steps, n_channels) array of Poisson rates in Hz at 1 ms resolution."""
    steps = int(np.ceil(seq.duration_ms))
    r = np.full((steps, p.n_channels), p.rate_bg_hz)
    for onset, tone in zip(seq.onsets_ms, seq.tones):
        if tone == OMIT:
            continue
        a = int(round(onset)); b = int(round(onset + seq.pulse_ms))
        r[a:b, int(tone)] = p.rate_tone_hz
    return r


def run_sequence(seq: Sequence, p: NetworkParams, adapt: Adaptation, seed: int) -> RunResult:
    """Simulate one sequence in a freshly built network. Same arguments -> identical output."""
    if not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a non-negative integer")
    if len(seq) == 0:
        raise ValueError("empty sequence")
    if int(np.max(seq.tones)) >= p.n_channels:
        raise ValueError("sequence uses a channel outside the network")

    b2.start_scope()
    b2.seed(int(seed))
    np.random.seed(int(seed))
    b2.defaultclock.dt = p.dt_ms * ms

    E = make_lif_group(p.n_exc, p, noise=True, sfa_b_mV=p.sfa_b_mV if adapt.sfa else 0.0, name="E")
    I = make_lif_group(p.n_inh, p, noise=True, sfa_b_mV=0.0, name="I")
    for g in (E, I):  # random initial membrane potentials (seeded)
        g.v = "E_L + rand()*(V_th - E_L)"

    tones = b2.TimedArray(tone_rate_array(seq, p) * Hz, dt=1 * ms, name="tone_rates")
    inp = b2.PoissonGroup(p.n_channels * p.n_in_per_channel,
                          rates="tone_rates(t, i // n_in)", namespace={"n_in": p.n_in_per_channel, "tone_rates": tones},
                          name="inp")

    ns = dict(n_in=p.n_in_per_channel, n_e=p.n_exc_per_channel, sig=p.tuning_sigma_ch,
              maxd=p.tuning_max_ch, w_in=p.w_in_mV * mV, U=p.tm_U, tau_rec=p.tm_tau_rec_ms * ms)
    cond = "abs(i // n_in - j // n_e) <= maxd"
    wexpr = "w_in*exp(-((i // n_in - j // n_e)**2)/(2*sig**2))"
    if adapt.depression:
        syn = b2.Synapses(
            inp, E, model="wsyn : volt\n dx/dt = (1 - x)/tau_rec : 1 (event-driven)",
            on_pre="Ie_post += wsyn*x\n x -= U*x", namespace=ns, name="syn_in")
    else:
        syn = b2.Synapses(inp, E, model="wsyn : volt", on_pre="Ie_post += wsyn", namespace=ns, name="syn_in")
    syn.connect(condition=cond, p=p.p_in)
    syn.wsyn = wexpr
    if adapt.depression:
        syn.x = 1  # synaptic resource starts fully recovered

    ei = b2.Synapses(E, I, on_pre="Ie_post += w_ei", namespace={"w_ei": p.w_ei_mV * mV}, name="syn_ei")
    ei.connect(p=p.p_ei)
    ie = b2.Synapses(I, E, on_pre="Ii_post += w_ie", namespace={"w_ie": p.w_ie_mV * mV}, name="syn_ie")
    ie.connect(p=p.p_ie)

    mE = b2.SpikeMonitor(E, name="mE")
    mI = b2.SpikeMonitor(I, name="mI")
    net = b2.Network(E, I, inp, syn, ei, ie, mE, mI)
    net.run(seq.duration_ms * ms)
    return RunResult(np.asarray(mE.t / ms), np.asarray(mE.i), np.asarray(mI.t / ms),
                     np.asarray(mI.i), float(seq.duration_ms))
