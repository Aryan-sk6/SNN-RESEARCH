import numpy as np

from snn_oddball import network as N
from snn_oddball import params as P
from snn_oddball import stimuli as S


def _seq(seed, n=6):
    return S.repeat_tone(4, n, 10, np.random.default_rng(seed), isi_ms=300.0)


def test_same_seed_identical_results(p):
    seq = _seq(0)
    for adapt in (P.NONE, P.SFA, P.STD):
        a = N.run_sequence(seq, p, adapt, seed=7)
        b = N.run_sequence(seq, p, adapt, seed=7)
        assert np.array_equal(a.e_t_ms, b.e_t_ms) and np.array_equal(a.e_idx, b.e_idx)
        assert np.array_equal(a.i_t_ms, b.i_t_ms)
        assert len(a.e_t_ms) > 0


def test_different_seed_differs(p):
    seq = _seq(0)
    a = N.run_sequence(seq, p, P.NONE, seed=7)
    b = N.run_sequence(seq, p, P.NONE, seed=8)
    assert not (len(a.e_t_ms) == len(b.e_t_ms) and np.array_equal(a.e_t_ms, b.e_t_ms))


def test_stimulus_generation_is_seeded():
    a = S.oddball(3, 6, 100, 0.1, 10, np.random.default_rng(5), isi_ms=(300, 500))
    b = S.oddball(3, 6, 100, 0.1, 10, np.random.default_rng(5), isi_ms=(300, 500))
    assert np.array_equal(a.tones, b.tones) and np.array_equal(a.onsets_ms, b.onsets_ms)
