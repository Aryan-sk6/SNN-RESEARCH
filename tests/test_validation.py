"""Input validation."""
import numpy as np
import pytest

from snn_oddball import network as N
from snn_oddball import params as P
from snn_oddball import stimuli as S
from snn_oddball.stats import mean_ci


@pytest.mark.parametrize("kw", [dict(tau_m_ms=0), dict(n_inh=-1), dict(p_in=1.5), dict(tm_U=0),
                                dict(V_th_mV=-70.0), dict(sigma_noise_mV=-1), dict(dt_ms=5.0)])
def test_params_rejected(kw):
    with pytest.raises(ValueError):
        P.NetworkParams(**kw)


def test_sizes_match_brief():
    p = P.NetworkParams()
    assert (p.n_channels, p.n_exc, p.n_inh, p.pulse_ms) == (10, 100, 20, 50.0)


@pytest.mark.parametrize("kw", [dict(p_dev=0.0), dict(p_dev=0.6), dict(n_trials=0), dict(deviant=3),
                                dict(deviant=11), dict(isi_ms=(500, 300)), dict(isi_ms=-1),
                                dict(isi_ms=(1, 2, 3))])
def test_oddball_rejects_bad_input(kw, rng):
    args = dict(standard=3, deviant=6, n_trials=100, p_dev=0.1, n_channels=10, rng=rng)
    args.update(kw)
    with pytest.raises(ValueError):
        S.oddball(**args)


def test_oddball_rejects_impossible_placement(rng):
    # 25% deviants with >=3 standards before each cannot fit in 400 trials
    with pytest.raises(ValueError):
        S.oddball(3, 6, 400, 0.25, 10, rng)


@pytest.mark.parametrize("n_tones", [1, 3, 4, 11])
def test_control_sets_need_even_spacing(n_tones, rng):
    with pytest.raises(ValueError):
        S.many_standards(6, n_tones, 100, 10, rng)


def test_cascade_direction_validated(rng):
    with pytest.raises(ValueError):
        S.cascade(6, 5, 100, 10, rng, direction="sideways")


def test_run_sequence_rejects_bad_seed_and_channels(p, rng):
    seq = S.repeat_tone(4, 3, 10, rng)
    for bad in (-1, 1.5, "a"):
        with pytest.raises(ValueError):
            N.run_sequence(seq, p, P.NONE, bad)
    small = P.NetworkParams(n_channels=4)
    with pytest.raises(ValueError):
        N.run_sequence(seq, small, P.NONE, 1)


def test_channel_out_of_range_in_analysis(p):
    from snn_oddball import analysis as A
    res = N.RunResult(np.array([]), np.array([], dtype=int), np.array([]), np.array([], dtype=int), 10.0)
    with pytest.raises(ValueError):
        A.channel_spikes(res, p, 10)


def test_mean_ci_validation():
    with pytest.raises(ValueError):
        mean_ci([1, 2, 3], conf=1.2)
