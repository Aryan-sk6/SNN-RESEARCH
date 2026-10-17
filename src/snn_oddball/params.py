"""All model parameters in one place. Plain floats; the unit is in the name.

Provenance rule: every value below is a first-choice value fixed BEFORE looking at any
oddball/omission/ABABAA result. The only values calibrated against a target are
`w_in_mV`, `w_ei_mV`, `w_ie_mV` and `sigma_noise_mV`, and only against the
*unadapted, single-tone* targets listed in docs/PARAMETERS.md (spontaneous rate and
evoked rate), never against an experiment outcome. Any later change must be logged
in docs/PARAMETERS.md with its reason.
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class NetworkParams:
    # ---- architecture -------------------------------------------------------------
    n_channels: int = 10            # tone channels (abstract tonotopic positions)
    n_exc_per_channel: int = 10     # excitatory cells per channel -> 100 E in total
    n_inh: int = 20                 # inhibitory cells (shared pool)
    n_in_per_channel: int = 20      # Poisson "thalamic" input units per channel

    # ---- LIF neuron (shared by E and I) ------------------------------------------
    tau_m_ms: float = 20.0          # membrane time constant
    E_L_mV: float = -65.0           # rest
    V_th_mV: float = -50.0          # spike threshold
    V_reset_mV: float = -65.0       # reset
    t_ref_ms: float = 2.0           # absolute refractory period
    sigma_noise_mV: float = 6.0     # std of the membrane-potential noise (OU), calibrated
    tau_e_ms: float = 5.0           # excitatory synaptic current decay
    tau_i_ms: float = 10.0          # inhibitory synaptic current decay

    # ---- connectivity -------------------------------------------------------------
    p_in: float = 0.6               # input unit -> E connection probability
    tuning_sigma_ch: float = 0.7    # width (channels) of the input tuning curve
    tuning_max_ch: int = 2          # no synapse beyond this channel distance
    w_in_mV: float = 5.0            # input -> E weight at best channel, calibrated
    p_ei: float = 0.5               # E -> I
    w_ei_mV: float = 4.0            # calibrated
    p_ie: float = 0.5               # I -> E
    w_ie_mV: float = 3.0            # calibrated

    # ---- tone input ---------------------------------------------------------------
    pulse_ms: float = 50.0          # tone pulse duration (brief)
    rate_tone_hz: float = 100.0     # Poisson rate of each input unit of the active channel
    rate_bg_hz: float = 0.0         # background Poisson rate of every input unit

    # ---- adaptation (a): spike-frequency adaptation, E cells ----------------------
    sfa_b_mV: float = 2.0           # adaptation-variable increment per spike
    tau_w_ms: float = 300.0         # decay of the adaptation variable

    # ---- adaptation (b): Tsodyks-Markram short-term depression, input -> E --------
    tm_U: float = 0.1               # utilisation (release probability); facilitation omitted
    tm_tau_rec_ms: float = 500.0    # recovery time constant

    # ---- numerics -----------------------------------------------------------------
    dt_ms: float = 0.25

    def __post_init__(self):
        pos = ("n_channels n_exc_per_channel n_inh n_in_per_channel tau_m_ms tau_e_ms tau_i_ms "
               "t_ref_ms pulse_ms rate_tone_hz tau_w_ms tm_tau_rec_ms dt_ms tuning_sigma_ch").split()
        for name in pos:
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be > 0, got {getattr(self, name)}")
        for name in ("p_in", "p_ei", "p_ie"):
            if not 0.0 <= getattr(self, name) <= 1.0:
                raise ValueError(f"{name} must be in [0, 1]")
        if not 0.0 < self.tm_U <= 1.0:
            raise ValueError("tm_U must be in (0, 1]")
        if self.V_th_mV <= self.V_reset_mV:
            raise ValueError("V_th_mV must be above V_reset_mV")
        if self.sigma_noise_mV < 0 or self.rate_bg_hz < 0 or self.sfa_b_mV < 0:
            raise ValueError("sigma_noise_mV, rate_bg_hz and sfa_b_mV must be >= 0")
        if self.dt_ms > self.tau_e_ms / 4:
            raise ValueError("dt_ms too large relative to tau_e_ms")

    @property
    def n_exc(self) -> int:
        return self.n_channels * self.n_exc_per_channel

    def with_(self, **kw) -> "NetworkParams":
        return replace(self, **kw)


@dataclass(frozen=True)
class Adaptation:
    """Which adaptation mechanisms are switched on. Tested separately."""

    sfa: bool = False         # (a) spike-frequency adaptation
    depression: bool = False  # (b) Tsodyks-Markram short-term depression

    @property
    def label(self) -> str:
        if self.sfa and self.depression:
            return "sfa+std"
        if self.sfa:
            return "sfa"
        if self.depression:
            return "std"
        return "none"


NONE = Adaptation()
SFA = Adaptation(sfa=True)
STD = Adaptation(depression=True)
BOTH = Adaptation(sfa=True, depression=True)
