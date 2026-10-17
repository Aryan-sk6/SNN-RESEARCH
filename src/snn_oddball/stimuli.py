"""Tone-sequence generators: oddball, many-standards control, cascade control.

All randomness comes from a numpy Generator that the caller seeds.

Timing. `isi_ms` is the SILENT interval between the end of one pulse and the start of the next.
It is either a float (fixed, isochronous) or a (low, high) tuple (uniform jitter). The stimulus
onset asynchrony is pulse_ms + ISI.

Roles ("labels"): 'std' standard, 'dev' deviant, 'ctr' control tone, 'oth' other control tone.
A tone value of -1 marks an omitted slot (a tone was due but no pulse is played).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

OMIT = -1


@dataclass(frozen=True)
class Sequence:
    onsets_ms: np.ndarray   # (n,) start of each slot, ms
    tones: np.ndarray       # (n,) channel index, or OMIT
    labels: np.ndarray      # (n,) role strings
    pulse_ms: float
    duration_ms: float      # end of the last slot + tail

    def __len__(self) -> int:
        return len(self.tones)


def _check_common(n_trials, n_channels, tones):
    if not isinstance(n_trials, (int, np.integer)) or n_trials < 1:
        raise ValueError(f"n_trials must be a positive integer, got {n_trials!r}")
    for t in tones:
        if not 0 <= int(t) < n_channels:
            raise ValueError(f"tone {t} outside channel range 0..{n_channels - 1}")


def _timing(n, isi_ms, pulse_ms, rng, tail_ms=400.0):
    if pulse_ms <= 0:
        raise ValueError("pulse_ms must be > 0")
    if isinstance(isi_ms, (tuple, list, np.ndarray)):
        if len(isi_ms) != 2:
            raise ValueError("isi_ms must be a float or a (low, high) pair")
        lo, hi = float(isi_ms[0]), float(isi_ms[1])
        if not 0 < lo <= hi:
            raise ValueError(f"need 0 < low <= high for the ISI range, got {isi_ms!r}")
        isi = rng.uniform(lo, hi, size=n) if hi > lo else np.full(n, lo)
    else:
        if isi_ms <= 0:
            raise ValueError("isi_ms must be > 0")
        isi = np.full(n, float(isi_ms))
    soa = pulse_ms + isi
    onsets = 200.0 + np.concatenate([[0.0], np.cumsum(soa[:-1])])   # 200 ms lead-in
    return onsets, float(onsets[-1] + soa[-1] + tail_ms)


def _build(tones, labels, isi_ms, pulse_ms, rng) -> Sequence:
    onsets, dur = _timing(len(tones), isi_ms, pulse_ms, rng)
    return Sequence(onsets, np.asarray(tones, dtype=int), np.asarray(labels, dtype=object),
                    float(pulse_ms), dur)


def oddball(standard, deviant, n_trials, p_dev, n_channels, rng, isi_ms=400.0, pulse_ms=50.0,
            first_standards=10, min_std_before_dev=3) -> Sequence:
    """Oddball block. Constraints follow Parras et al. 2017 (Methods): the first
    `first_standards` tones are standards and at least `min_std_before_dev` standards precede
    every deviant. Deviants are otherwise placed pseudorandomly.
    """
    _check_common(n_trials, n_channels, (standard, deviant))
    if standard == deviant:
        raise ValueError("standard and deviant must differ")
    if not 0.0 < p_dev < 0.5:
        raise ValueError(f"p_dev must be in (0, 0.5), got {p_dev}")
    n_dev = int(round(p_dev * n_trials))
    if n_dev < 1:
        raise ValueError("p_dev * n_trials rounds to zero deviants")
    n_std = n_trials - n_dev
    need = first_standards + min_std_before_dev * (n_dev - 1)
    if need > n_std:
        raise ValueError(f"cannot place {n_dev} deviants with >= {min_std_before_dev} standards "
                         f"before each in {n_trials} trials (need {need} standards, have {n_std})")
    extra = n_std - need
    # distribute the spare standards over the n_dev + 1 gaps
    add = rng.multinomial(extra, np.ones(n_dev + 1) / (n_dev + 1))
    gaps = np.array([first_standards] + [min_std_before_dev] * (n_dev - 1) + [0]) + add
    tones, labels = [], []
    for k in range(n_dev + 1):
        tones += [standard] * int(gaps[k]); labels += ["std"] * int(gaps[k])
        if k < n_dev:
            tones.append(deviant); labels.append("dev")
    return _build(tones, labels, isi_ms, pulse_ms, rng)


def control_tone_set(target, n_tones, n_channels):
    """`n_tones` channels evenly spaced over the channel range, containing `target`.

    Only divisors of `n_channels` are allowed (2, 5, 10 for 10 channels), so the spacing is
    exactly even. Matched control for deviant probability p = 1 / n_tones.
    """
    if not 2 <= n_tones <= n_channels or n_channels % n_tones:
        raise ValueError(f"n_tones must divide n_channels={n_channels} (and be >= 2), got {n_tones}")
    _check_common(1, n_channels, (target,))
    step = n_channels // n_tones
    return sorted({(target + k * step) % n_channels for k in range(n_tones)})


def many_standards(target, n_tones, n_trials, n_channels, rng, isi_ms=400.0, pulse_ms=50.0) -> Sequence:
    """Random succession of `n_tones` equiprobable tones; no tone repeats back-to-back."""
    tset = control_tone_set(target, n_tones, n_channels)
    _check_common(n_trials, n_channels, tset)
    n_blocks = -(-n_trials // n_tones)
    order = []
    for _ in range(n_blocks):
        blk = list(rng.permutation(tset))
        while order and blk[0] == order[-1]:
            blk = list(rng.permutation(tset))
        order += blk
    order = order[:n_trials]
    labels = ["ctr" if t == target else "oth" for t in order]
    return _build(order, labels, isi_ms, pulse_ms, rng)


def cascade(target, n_tones, n_trials, n_channels, rng, direction="ascending", isi_ms=400.0,
            pulse_ms=50.0) -> Sequence:
    """The same tones in a regular ascending (or descending) run, repeated."""
    if direction not in ("ascending", "descending"):
        raise ValueError("direction must be 'ascending' or 'descending'")
    tset = control_tone_set(target, n_tones, n_channels)
    _check_common(n_trials, n_channels, tset)
    run = tset if direction == "ascending" else tset[::-1]
    order = [run[i % n_tones] for i in range(n_trials)]
    labels = ["ctr" if t == target else "oth" for t in order]
    return _build(order, labels, isi_ms, pulse_ms, rng)


def repeat_tone(tone, n_trials, n_channels, rng, isi_ms=400.0, pulse_ms=50.0) -> Sequence:
    """The same tone n times (used to test that adaptation lowers the response)."""
    _check_common(n_trials, n_channels, (tone,))
    return _build([tone] * n_trials, ["std"] * n_trials, isi_ms, pulse_ms, rng)
