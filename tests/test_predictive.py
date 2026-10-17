"""Prediction circuit and Tier 2 sequence builders."""
import numpy as np
import pytest

from snn_oddball import predictive as PR
from snn_oddball import stimuli as S
from snn_oddball import tier2 as T
from snn_oddball.params import BOTH, NetworkParams

P5 = NetworkParams(dt_ms=0.5)
PP = PR.PredParams(pred_channels=T.PRED_CHANNELS)


def _alt(n, isi=400.0):
    items = []
    for i in range(n):
        items += [(T.A_CH, "A", 0.0), (T.B_CH, "B", 0.0)]
    return T.build(items, isi, 50.0, np.random.default_rng(0))


# ---------------------------------------------------------------- validation
@pytest.mark.parametrize("mech", [PR.Mech(G=True, E=False), PR.Mech(C=True), PR.Mech(replace=True),
                                  PR.Mech(G=True, L=False)])
def test_invalid_component_combinations_rejected(mech):
    with pytest.raises(ValueError):
        PR.run_predictive(_alt(2), P5, BOTH, mech, PP, 1)


def test_predictive_input_validation():
    with pytest.raises(ValueError):
        PR.run_predictive(_alt(2), P5, BOTH, PR.B_MECH, PP, -1)
    with pytest.raises(ValueError):
        PR.run_predictive(_alt(2), P5, BOTH, PR.B_MECH, PP.with_(pred_channels=(3, 3)), 1)
    with pytest.raises(ValueError):
        T.build([], 400.0, 50.0, np.random.default_rng(0))
    with pytest.raises(ValueError):
        T.build([(3, "x", 0.0)], 400.0, 50.0, np.random.default_rng(0), jitter=1.5)


# ---------------------------------------------------------------- sequence builders
def test_omission_sequence_constraints():
    seq, om = T.seq_omission(160, 0.2, np.random.default_rng(1))
    assert len(om) == 32 and min(om) >= 10 and np.all(np.diff(om) >= 2)
    assert np.all(seq.tones[om] == S.OMIT) and np.all(np.diff(seq.onsets_ms) == 450.0)


def test_jitter_changes_intervals_but_keeps_mean():
    seq, _ = T.seq_omission(160, 0.2, np.random.default_rng(1), jitter=0.3)
    d = np.diff(seq.onsets_ms)
    assert d.min() >= 450 - 120 - 1e-6 and d.max() <= 450 + 120 + 1e-6 and d.std() > 20
    assert abs(d.mean() - 450.0) < 15.0


def test_aba_sequence_events_far_apart_and_alternating():
    seq, ev = T.seq_aba(200, 0.1, np.random.default_rng(2))
    assert len(ev) == 10 and np.all(np.diff(ev) >= 12)
    lab = seq.labels
    assert all(lab[i] == "rep" and lab[i - 1] == "A" for i in ev)
    assert all(lab[i] == "A" for i in range(0, 200, 2))


def test_episode_metadata_consistent():
    seq, meta = T.seq_episodes("cycABCB", 3, 8, np.random.default_rng(3))
    for e in range(3):
        assert seq.tones[meta["dev"][e]] == T.B_CH
        assert seq.tones[meta["pre1"][e]] == T.A_CH and meta["pre1"][e] == meta["dev"][e] - 1
        post = [seq.tones[i] for i in meta["post"][e]]
        assert post[:4] == [T.C_CH, T.B_CH, T.A_CH, T.B_CH]
        assert len(meta["init"][e]) == 6
    gaps = np.diff(seq.onsets_ms)
    assert (gaps > 3000).sum() == 2        # a silent gap between the three episodes only


def test_random_sequence_uses_all_channels():
    seq = T.seq_random(200, np.random.default_rng(4))
    assert set(seq.tones) == set(T.PRED_CHANNELS)


# ---------------------------------------------------------------- circuit behaviour (spiking, slowish)
@pytest.fixture(scope="module")
def alt_runs():
    seq = _alt(14)
    return {m.label + str(i): PR.run_predictive(seq, P5, BOTH, m, PP, 1)
            for i, m in enumerate((PR.B_MECH, PR.Mech(L=False), PR.A2B_MECH))}


def test_same_seed_identical(alt_runs):
    a = PR.run_predictive(_alt(3), P5, BOTH, PR.B_MECH, PP, 5)
    b = PR.run_predictive(_alt(3), P5, BOTH, PR.B_MECH, PP, 5)
    assert np.array_equal(a.e_t, b.e_t) and np.array_equal(a.pep_t, b.pep_t) and np.array_equal(a.w_final, b.w_final)


def test_learning_builds_weight_at_the_right_lag(alt_runs):
    w = alt_runs["TEL0"].w_final[0, :, 1]            # A (source 0) -> B (destination 1)
    assert w.argmax() in (8, 9, 10)                  # tone interval 450 ms = lag index 9
    assert w.max() > 5 * np.median(w[[0, 1, 2, 17, 18, 19]]) + 0.5


def test_no_weights_without_learning(alt_runs):
    assert alt_runs["TE1"].w_final.max() == 0.0


def test_gated_learner_learns_faster_than_slow_learner(alt_runs):
    assert alt_runs["TELGC2"].w_final[0, :, 1].max() > 2 * alt_runs["TEL0"].w_final[0, :, 1].max()


def test_error_falls_as_prediction_forms(alt_runs):
    res = alt_runs["TEL0"]
    on = _alt(14).onsets_ms[1::2]
    c = T._cnt(np.sort(res.pep_t[(res.pep_idx // PP.n_pe) == 1]), on, 0, 180)
    assert c[-4:].mean() < 0.7 * c[:3].mean()


def test_gate_only_exists_for_mechanism_a(alt_runs):
    assert alt_runs["TEL0"].g_val.size == 0 and alt_runs["TELGC2"].g_val.max() > 0.2


def test_baseline_network_has_no_error_cells():
    res = PR.run_predictive(_alt(3), P5, BOTH, None, PP, 1)
    assert len(res.pep_t) == 0 and len(res.pem_t) == 0 and len(res.e_t) > 0
    parts = T.parts(res, P5, PP, T.B_CH, _alt(3).onsets_ms[1::2])
    assert np.all(parts["PEp"] == 0) and np.all(parts["R"] == parts["E"])
