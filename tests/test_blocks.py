import numpy as np
import pytest

from snn_oddball import blocks, runner

BASE = dict(adapt="none", seed=1, n_trials=60, isi=400.0)


def test_block_kinds_return_finite_numbers():
    odd = blocks.run_block(dict(BASE, kind="odd", std=3, dev=6, p_dev=0.1, min_std=3))
    ctr = blocks.run_block(dict(BASE, kind="ctrl", style="cascade", target=6, n_tones=10))
    om = blocks.run_block(dict(BASE, kind="omit", tone=6, p_omit=0.2))
    for d in (odd, ctr, om):
        assert all(np.isfinite(v) for v in d.values())
    assert odd["n_dev"] == 6 and om["n_omit"] == 12
    assert om["tone"] > 5.0          # the positive control is detectable


def test_block_is_deterministic():
    spec = dict(BASE, kind="odd", std=3, dev=6, p_dev=0.1, min_std=3)
    assert blocks.run_block(spec) == blocks.run_block(spec)


def test_unknown_kind_rejected():
    with pytest.raises(ValueError):
        blocks.run_block(dict(BASE, kind="nope"))


def test_runner_caches(tmp_path):
    specs = [dict(BASE, kind="ctrl", style="many", target=6, n_tones=10)]
    a = runner.run_specs(specs, tmp_path, jobs=1, verbose=False)
    files = list(tmp_path.glob("*.json"))
    assert len(files) == 1
    mtime = files[0].stat().st_mtime_ns
    b = runner.run_specs(specs, tmp_path, jobs=1, verbose=False)
    assert a == b and files[0].stat().st_mtime_ns == mtime     # second call reads the cache
