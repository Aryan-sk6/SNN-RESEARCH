import numpy as np
import pytest

from snn_oddball import stimuli as S
from snn_oddball.stats import mean_ci


def test_oddball_structure_follows_parras(rng):
    seq = S.oddball(3, 6, 400, 0.1, 10, rng)
    lab = list(seq.labels)
    assert len(seq) == 400 and lab.count("dev") == 40
    assert all(l == "std" for l in lab[:10])
    dev_pos = [i for i, l in enumerate(lab) if l == "dev"]
    for i in dev_pos:
        assert all(l == "std" for l in lab[i - 3:i])           # >= 3 standards before each deviant
    assert set(seq.tones[np.array(lab) == "dev"]) == {6}


def test_fixed_and_jittered_timing(rng):
    fixed = S.oddball(3, 6, 100, 0.1, 10, rng, isi_ms=400.0, pulse_ms=50.0)
    assert np.allclose(np.diff(fixed.onsets_ms), 450.0)
    jit = S.oddball(3, 6, 100, 0.1, 10, rng, isi_ms=(300.0, 500.0), pulse_ms=50.0)
    d = np.diff(jit.onsets_ms)
    assert d.min() >= 350.0 and d.max() <= 550.0 and d.std() > 20.0


def test_many_standards_equiprobable_no_repeats(rng):
    seq = S.many_standards(6, 10, 400, 10, rng)
    assert np.all(np.bincount(seq.tones, minlength=10) == 40)
    assert not np.any(np.diff(seq.tones) == 0)
    assert (seq.labels == "ctr").sum() == 40


def test_cascade_is_regular_and_matched_in_count(rng):
    seq = S.cascade(6, 5, 400, 10, rng)
    assert list(seq.tones[:6]) == [0, 2, 4, 6, 8, 0]
    assert (seq.labels == "ctr").sum() == 80
    desc = S.cascade(6, 5, 400, 10, rng, direction="descending")
    assert list(desc.tones[:5]) == [8, 6, 4, 2, 0]


def test_control_probability_matches_deviant_probability(rng):
    """n_tones equiprobable control tones give the target probability 1/n_tones."""
    for n in (5, 10):
        ctrl = S.many_standards(6, n, 400, 10, rng)
        odd = S.oddball(3, 6, 400, 1 / n, 10, rng)
        assert (ctrl.labels == "ctr").sum() == (odd.labels == "dev").sum()


def test_mean_ci_known_values():
    m, lo, hi, n, nn = mean_ci([1, 2, 3, 4, 5])
    assert (m, n, nn) == (3.0, 5, 0)
    h = 2.7764451 * np.sqrt(2.5) / np.sqrt(5)       # t(0.975, 4) * sem
    assert (hi - lo) / 2 == pytest.approx(h, rel=1e-5)


def test_mean_ci_nan_handling():
    m, lo, hi, n, nn = mean_ci([1.0, np.nan, 3.0])
    assert (m, n, nn) == (2.0, 2, 1)
    m1 = mean_ci([4.0])
    assert m1[0] == 4.0 and np.isnan(m1[1]) and np.isnan(m1[2])
    assert mean_ci([np.nan])[3] == 0


def test_omission_sequence(rng):
    seq = S.omission_sequence(6, 200, 0.2, 10, rng)
    om = np.where(seq.tones == S.OMIT)[0]
    assert len(om) == 40 and om.min() >= 10 and not np.any(np.diff(om) == 1)
    assert np.all(seq.labels[om] == "omit") and len(seq.onsets_ms) == 200
    with pytest.raises(ValueError):
        S.omission_sequence(6, 200, 0.6, 10, rng)
