"""LIF firing rate against the analytic value for constant current."""
import numpy as np
import pytest
import brian2 as b2
from brian2 import ms, mV

from snn_oddball import network as N
from snn_oddball import params as P


def analytic_rate_hz(p, I_ext_mV):
    """Noise-free LIF with refractory period: T = t_ref + tau*ln((EL+I-Vr)/(EL+I-Vth))."""
    drive = p.E_L_mV + I_ext_mV
    if drive <= p.V_th_mV:
        return 0.0
    T_ms = p.t_ref_ms + p.tau_m_ms * np.log((drive - p.V_reset_mV) / (drive - p.V_th_mV))
    return 1000.0 / T_ms


def simulated_rate_hz(p, I_ext_mV, dur_ms=4000.0):
    b2.start_scope()
    b2.defaultclock.dt = p.dt_ms * ms
    g = N.make_lif_group(1, p, noise=False, name="g")
    g.I_ext = I_ext_mV * mV
    m = b2.SpikeMonitor(g)
    b2.Network(g, m).run(dur_ms * ms)
    return m.num_spikes / (dur_ms / 1000.0)


@pytest.mark.parametrize("I_ext_mV", [20.0, 25.0, 35.0, 60.0])
def test_rate_matches_analytic(I_ext_mV):
    p = P.NetworkParams(dt_ms=0.05)
    sim, ana = simulated_rate_hz(p, I_ext_mV), analytic_rate_hz(p, I_ext_mV)
    assert ana > 0
    assert sim == pytest.approx(ana, rel=0.02), f"sim {sim:.2f} Hz vs analytic {ana:.2f} Hz"


def test_subthreshold_current_never_fires():
    p = P.NetworkParams(dt_ms=0.05)
    # E_L + I = -65 + 14 = -51 mV < threshold (-50 mV)
    assert simulated_rate_hz(p, 14.0, dur_ms=1000.0) == 0.0
    assert analytic_rate_hz(p, 14.0) == 0.0
