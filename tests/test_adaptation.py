"""Adaptation lowers the response to repeated input; the mechanisms are switched separately."""
import numpy as np
import pytest

from snn_oddball import analysis as A
from snn_oddball import network as N
from snn_oddball import params as P
from snn_oddball import stimuli as S

CH, N_TRIALS, SEEDS = 4, 20, (1, 2, 3, 4)


def _responses(p, adapt, seed):
    seq = S.repeat_tone(CH, N_TRIALS, p.n_channels, np.random.default_rng(seed), isi_ms=300.0)
    res = N.run_sequence(seq, p, adapt, seed)
    w, b = A.trial_counts(res, p, seq.onsets_ms, CH)
    return w - b * (180.0 / 75.0)          # per-trial baseline-corrected counts


@pytest.fixture(scope="module")
def resp(p):
    return {a.label: np.array([_responses(p, a, s) for s in SEEDS])
            for a in (P.NONE, P.SFA, P.STD)}


def test_all_conditions_respond(resp):
    for label, r in resp.items():
        assert r[:, :3].mean() > 3.0, f"{label}: no evoked response"


@pytest.mark.parametrize("label", ["sfa", "std"])
def test_adaptation_lowers_response_to_repeated_tone(resp, label):
    """Adapted steady-state response (trials 6-20) is >= 10% below the no-adaptation response."""
    adapted = resp[label][:, 5:].mean()
    control = resp["none"][:, 5:].mean()
    assert adapted < 0.9 * control, f"{label}: {adapted:.1f} vs none {control:.1f}"


def test_depression_builds_up_over_repeats(resp):
    """Short-term depression: later presentations are smaller than the first (resource depleted)."""
    assert resp["std"][:, 5:].mean() < 0.9 * resp["std"][:, 0].mean()


def test_no_adaptation_stays_flat(resp):
    """Control: with both mechanisms off the response does not decline with repeats."""
    r = resp["none"]
    assert r[:, 5:].mean() > 0.85 * r[:, :3].mean()


def test_adaptation_is_channel_specific(p):
    """Adapting channel 4 leaves a far channel's response alone (stimulus-specific)."""
    rng = np.random.default_rng(0)
    seq = S.repeat_tone(CH, N_TRIALS, p.n_channels, rng, isi_ms=300.0)
    res = N.run_sequence(seq, p, P.STD, 1)
    w4, _ = A.trial_counts(res, p, seq.onsets_ms, CH)
    w9, _ = A.trial_counts(res, p, seq.onsets_ms, 9)
    assert w4[5:].mean() > 3 * w9[5:].mean()
