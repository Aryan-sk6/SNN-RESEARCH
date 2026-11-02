"""Experiment 9: E1 vs E2 error definitions read out from the same networks. Design: docs/PREREGISTRATION_EXP9.md.

    python experiments/exp9_error_definitions.py run --jobs 2
    python experiments/exp9_error_definitions.py report
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from snn_oddball import exp9 as X9                      # noqa: E402
from snn_oddball import exp13_15 as X13                 # noqa: E402
from snn_oddball.runner import run_specs, spec_key      # noqa: E402
from snn_oddball.stats import mean_ci                   # noqa: E402

SEEDS = list(range(20))
NETS = ("B", "A2b")
CACHE = ROOT / "results" / "raw" / "exp9"
OUT = ROOT / "results"


def specs():
    return [dict(kind="x9", net=n, seed=s, seqkind=k, n_slots=200, **({"analyse_from": 80} if k == "aba" else {}))
            for s in SEEDS for n in NETS for k in ("random", "aba")]


def ci(v):
    m, lo, hi, *_ = mean_ci(list(v))
    return dict(mean=m, lo=lo, hi=hi)


def fmt(d):
    return f"{d['mean']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}]"


def obs_rows(tones):
    """Ideal-observer predictive distributions (first-order Markov, Dirichlet(1)), one row per tone."""
    idx = {c: i for i, c in enumerate(X9.CH)}
    counts = np.ones((4, 4))
    rows = [np.full(4, 0.25)]
    for t in range(1, len(tones)):
        a = idx[tones[t - 1]]
        rows.append(counts[a] / counts[a].sum())
        counts[a, idx[tones[t]]] += 1
    return np.array(rows)


def report():
    get = lambda s: json.loads((CACHE / f"{spec_key(s)}.json").read_text())["result"]
    out, L = {}, ["# Experiment 9: E1 vs E2 error definitions (20 test seeds, mean [95% CI])", "",
                  "Design: `docs/PREREGISTRATION_EXP9.md`. E1 = 1 - p(event); E2 = p(top guess) - p(event); "
                  "p read from prediction cells 100 ms before each tone (network) or from the Bayesian observer.", "",
                  "| source | random context E1 (tones 101-200) | random context E2 | silent-prediction share | "
                  "T2: repeated minus regular A, E1 | T2: repeated minus regular A, E2 |", "|---|---|---|---|---|---|"]
    rows = {}
    for src in NETS + ("observer",):
        r1, r2, sil, d1, d2 = [], [], [], [], []
        for s in SEEDS:
            net = "A2b" if src == "observer" else src
            rr = get(dict(kind="x9", net=net, seed=s, seqkind="random", n_slots=200))
            ra = get(dict(kind="x9", net=net, seed=s, seqkind="aba", n_slots=200, analyse_from=80))
            for res, dest in ((rr, "random"), (ra, "aba")):
                tones = res["tones"]
                ev = np.array([X9.CH.index(t) for t in tones])
                if src == "observer":
                    p = obs_rows(tones); silent = np.zeros(len(tones))
                else:
                    pc = np.array(res["pcounts"]); p = X9.p_hat(pc); silent = (pc.sum(axis=1) < 1.0)
                e1, e2 = X9.errors(p, ev)
                if dest == "random":
                    r1.append(e1[100:].mean()); r2.append(e2[100:].mean()); sil.append(silent[100:].mean())
                else:
                    rep, reg = res["rep"], res["reg"]
                    d1.append(e1[rep].mean() - e1[reg].mean()); d2.append(e2[rep].mean() - e2[reg].mean())
        o = dict(rand_E1=ci(r1), rand_E2=ci(r2), silent=ci(sil), rep_E1=ci(d1), rep_E2=ci(d2))
        out[src] = o
        L.append(f"| {src} | {fmt(o['rand_E1'])} | {fmt(o['rand_E2'])} | {fmt(o['silent'])} | "
                 f"{fmt(o['rep_E1'])} | {fmt(o['rep_E2'])} |")
    (OUT / "exp9_summary.json").write_text(json.dumps(out, indent=1, default=float))
    (OUT / "exp9_summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "report"])
    ap.add_argument("--jobs", type=int, default=2)
    a = ap.parse_args()
    if a.cmd == "run":
        run_specs(specs(), CACHE, jobs=a.jobs)
    report()


if __name__ == "__main__":
    main()
