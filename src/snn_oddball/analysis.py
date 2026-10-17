"""Response measures, the SSA index and the iMM / iRS / iPE decomposition.

Response measure (follows Parras et al. 2017, Methods; the exact windows are theirs):
  response = (spike count of the E cells of one channel in [0, 180) ms after pulse onset)
             - (spike count in [-75, 0) ms) * (180 / 75)
i.e. a baseline-corrected spike count. A condition's response is the MEAN over its trials. For the
indices the condition response is clipped at 0 (Parras analyse positive area only); the unclipped
value is available too so that a null or negative result stays visible.
"""

from __future__ import annotations

import numpy as np

from .network import RunResult
from .params import NetworkParams
from .stimuli import Sequence

WINDOW_MS = (0.0, 180.0)
BASELINE_MS = (-75.0, 0.0)


def channel_spikes(res: RunResult, p: NetworkParams, channel: int) -> np.ndarray:
    if not 0 <= channel < p.n_channels:
        raise ValueError(f"channel {channel} outside 0..{p.n_channels - 1}")
    sel = (res.e_idx // p.n_exc_per_channel) == channel
    return np.sort(res.e_t_ms[sel])


def trial_counts(res: RunResult, p: NetworkParams, onsets_ms, channel: int,
                 window_ms=WINDOW_MS, baseline_ms=BASELINE_MS):
    """Per-trial (window count, baseline count) for the E cells of `channel`."""
    t = channel_spikes(res, p, channel)
    on = np.asarray(onsets_ms, dtype=float)
    def cnt(lo, hi):
        return np.searchsorted(t, on + hi, side="left") - np.searchsorted(t, on + lo, side="left")
    return cnt(*window_ms).astype(float), cnt(*baseline_ms).astype(float)


def baseline_corrected(win_counts, base_counts, window_ms=WINDOW_MS, baseline_ms=BASELINE_MS,
                       clip=True) -> float:
    """Mean baseline-corrected spike count over trials (NaN if there are no trials)."""
    w = np.asarray(win_counts, dtype=float)
    b = np.asarray(base_counts, dtype=float)
    if w.shape != b.shape:
        raise ValueError("window and baseline counts must have the same shape")
    if w.size == 0:
        return float("nan")
    scale = (window_ms[1] - window_ms[0]) / (baseline_ms[1] - baseline_ms[0])
    r = float(w.mean() - b.mean() * scale)
    return max(0.0, r) if clip else r


def last_standard_before_deviant(labels) -> np.ndarray:
    """Indices of the standard immediately preceding each deviant (Parras: only these are analysed)."""
    lab = np.asarray(labels, dtype=object)
    idx = [i - 1 for i in range(1, len(lab)) if lab[i] == "dev" and lab[i - 1] == "std"]
    return np.asarray(idx, dtype=int)


def role_response(res: RunResult, seq: Sequence, p: NetworkParams, channel: int, trial_idx,
                  clip=True) -> float:
    """Baseline-corrected response of `channel` on the given trials of `seq`."""
    trial_idx = np.asarray(trial_idx, dtype=int)
    w, b = trial_counts(res, p, seq.onsets_ms[trial_idx], channel)
    return baseline_corrected(w, b, clip=clip)


def ssa_index(deviant: float, standard: float) -> float:
    """(d - s) / (d + s). NaN when d + s == 0 (undefined; never silently set to 0)."""
    if deviant < 0 or standard < 0:
        raise ValueError("responses must be >= 0 for the SSA index (clip before calling)")
    tot = deviant + standard
    return float("nan") if tot == 0 else (deviant - standard) / tot


def common_ssa_index(d1: float, d2: float, s1: float, s2: float) -> float:
    """Flip-flop SSA index: tone f1 and f2 each as deviant (d) and as standard (s)."""
    return ssa_index(d1 + d2, s1 + s2)


def decompose(dev: float, std: float, ctr: float, normalise: bool = True) -> dict:
    """Decomposition used by Parras et al. 2017 and Carbajal & Malmierca 2018.

        iMM = DEV - STD   (neuronal mismatch)
        iRS = CTR - STD   (repetition suppression)
        iPE = DEV - CTR   (prediction error)        and always  iMM = iRS + iPE

    normalise=True divides the three responses by the Euclidean norm sqrt(DEV^2+STD^2+CTR^2)
    first (Parras et al., Methods), which puts every index in [-1, 1]. If the norm is 0 the
    normalised indices are NaN.
    """
    for name, v in (("dev", dev), ("std", std), ("ctr", ctr)):
        if not np.isfinite(v) or v < 0:
            raise ValueError(f"{name} must be a finite response >= 0, got {v}")
    d, s, c = float(dev), float(std), float(ctr)
    if normalise:
        n = np.sqrt(d * d + s * s + c * c)
        if n == 0:
            return dict(iMM=np.nan, iRS=np.nan, iPE=np.nan)
        d, s, c = d / n, s / n, c / n
    return dict(iMM=d - s, iRS=c - s, iPE=d - c)
