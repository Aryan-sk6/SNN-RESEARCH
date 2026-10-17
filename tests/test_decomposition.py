"""Decomposition and index arithmetic on hand-made examples."""
import numpy as np
import pytest

from snn_oddball import analysis as A


def test_raw_decomposition_hand_example():
    # DEV=6, STD=2, CTR=3 spikes  ->  iMM=4, iRS=1, iPE=3
    d = A.decompose(6, 2, 3, normalise=False)
    assert d == {"iMM": 4, "iRS": 1, "iPE": 3}
    assert d["iMM"] == d["iRS"] + d["iPE"]


def test_normalised_decomposition_hand_example():
    # norm = sqrt(36+4+9) = 7, so normalised responses are 6/7, 2/7, 3/7
    d = A.decompose(6, 2, 3, normalise=True)
    assert d["iMM"] == pytest.approx(4 / 7)
    assert d["iRS"] == pytest.approx(1 / 7)
    assert d["iPE"] == pytest.approx(3 / 7)
    assert d["iMM"] == pytest.approx(d["iRS"] + d["iPE"])


def test_identity_holds_for_random_inputs():
    rng = np.random.default_rng(0)
    for _ in range(50):
        dev, std, ctr = rng.uniform(0.01, 30, 3)
        for norm in (True, False):
            d = A.decompose(dev, std, ctr, normalise=norm)
            assert d["iMM"] == pytest.approx(d["iRS"] + d["iPE"])
            if norm:
                assert all(-1 <= v <= 1 for v in d.values())


def test_adaptation_only_pattern_has_zero_prediction_error():
    # DEV equals CTR (no extra response to the deviant) -> iPE = 0, all mismatch is repetition suppression
    d = A.decompose(5, 2, 5)
    assert d["iPE"] == 0 and d["iMM"] == d["iRS"] > 0


def test_zero_responses_give_nan_not_zero():
    d = A.decompose(0, 0, 0)
    assert all(np.isnan(v) for v in d.values())


@pytest.mark.parametrize("bad", [(-1, 1, 1), (1, np.nan, 1), (1, 1, np.inf)])
def test_decompose_rejects_invalid(bad):
    with pytest.raises(ValueError):
        A.decompose(*bad)


def test_ssa_index_hand_example():
    assert A.ssa_index(6, 2) == pytest.approx(0.5)      # (6-2)/(6+2)
    assert A.ssa_index(2, 6) == pytest.approx(-0.5)
    assert A.ssa_index(3, 3) == 0.0
    assert np.isnan(A.ssa_index(0, 0))
    assert A.common_ssa_index(6, 4, 2, 2) == pytest.approx(6 / 14)   # (10-4)/(10+4)=3/7
    with pytest.raises(ValueError):
        A.ssa_index(-1, 2)


def test_baseline_correction_hand_example():
    # window count 10, baseline count 1 in a 75 ms window -> 1 * 180/75 = 2.4 subtracted
    assert A.baseline_corrected([10], [1], clip=False) == pytest.approx(10 - 2.4)
    assert A.baseline_corrected([1], [1], clip=False) == pytest.approx(1 - 2.4)
    assert A.baseline_corrected([1], [1], clip=True) == 0.0
    assert np.isnan(A.baseline_corrected([], []))
    with pytest.raises(ValueError):
        A.baseline_corrected([1, 2], [1])


def test_last_standard_before_deviant():
    lab = ["std", "std", "dev", "std", "std", "std", "dev", "std"]
    assert list(A.last_standard_before_deviant(lab)) == [1, 5]
