"""Sensitivity to slower spike-frequency adaptation (tau_w = 1000 and 3000 ms). Exploratory; see
docs/SENSITIVITY_SLOW_ADAPTATION.md (design and predictions written before the run).

    python experiments/sensitivity_slow_adaptation.py --jobs 4
    python experiments/sensitivity_slow_adaptation.py --plot-only     # aggregate from the cache
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import exp1_adaptation as E1      # noqa: E402
import exp2_tier2 as E2           # noqa: E402
from snn_oddball import analysis as A          # noqa: E402
from snn_oddball.runner import run_specs, spec_key   # noqa: E402
from snn_oddball.stats import mean_ci          # noqa: E402

TAUS = [1000.0, 3000.0]
SEEDS = 20
ADAPTS = ["sfa", "both"]
NETS = ["N0", "B", "A2b"]


def with_net(spec, tau):
    """Experiment 1 blocks read `net`; the predictive (Tier 2) blocks already use `net` as the network label, so they
    read the override from `netover`."""
    return dict(spec, **{("netover" if spec.get("kind") == "pred" else "net"): dict(tau_w_ms=tau)})


def exp1_specs(tau):
    sp = []
    for s in range(SEEDS):
        for a in ADAPTS:
            sp += [with_net(x, tau) for x in E1.odd_specs(a, E1.MAIN["gap"], E1.MAIN["p"], s, 400)]
            sp += [with_net(x, tau) for x in E1.ctrl_specs(a, E1.MAIN["p"], s, 400).values()]
            sp.append(with_net(E1.omit_spec(a, s, 200), tau))
    return sp


def t2_specs(tau):
    sp = []
    cfg = E2.settings(False)
    for s in range(SEEDS):
        for n in NETS:
            sp.append(with_net(E2.P(exp="aba", net=n, seed=s, n_slots=cfg["aba"], analyse_from=cfg["aba_from"]), tau))
            sp.append(with_net(E2.P(exp="omit", net=n, seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"]), tau))
            sp.append(with_net(E2.P(exp="ep", net=n, seed=s, cont="A", n_ep=cfg["n_ep"], m=cfg["m"]), tau))
    return sp


def ci(v):
    m, lo, hi, n, nn = mean_ci(v)
    return dict(mean=m, lo=lo, hi=hi)


def fmt(d):
    return f"{d['mean']:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--plot-only", action="store_true")
    args = ap.parse_args()
    cache = ROOT / "results" / "raw" / "sens_slow"
    allsp = [x for t in TAUS for x in exp1_specs(t) + t2_specs(t)]
    if not args.plot_only:
        run_specs(list({spec_key(s): s for s in allsp}.values()), cache, jobs=args.jobs)
    res = {spec_key(s): json.loads((cache / f"{spec_key(s)}.json").read_text())["result"] for s in allsp
           if (cache / f"{spec_key(s)}.json").exists()}
    if len(res) < len({spec_key(s) for s in allsp}):
        print(f"[sens] incomplete: {len(res)} of {len({spec_key(s) for s in allsp})} blocks cached", flush=True)
        return
    get = lambda s: res[spec_key(s)]
    clip = lambda v: max(0.0, v)
    out, L = {}, ["# Sensitivity: slower spike-frequency adaptation (20 seeds, mean [95% CI])", "",
                  "Exploratory; design and predictions in `docs/SENSITIVITY_SLOW_ADAPTATION.md`. tau_w = 300 ms rows are the "
                  "main runs (`results/exp1_summary_full.md`, `results/tier2_summary_full.md`). Predictive networks are not "
                  "recalibrated.", "", "## Experiment 1 main configuration", "",
                  "| tau_w (ms) | adaptation | SSA index | iMM | iRS | iPE (cascade) | iPE (many) | omission slot response |",
                  "|---|---|---|---|---|---|---|---|"]
    for tau in TAUS:
        for a in ADAPTS:
            rows = []
            for s in range(SEEDS):
                sa, sb = (with_net(x, tau) for x in E1.odd_specs(a, E1.MAIN["gap"], E1.MAIN["p"], s, 400))
                ra, rb = get(sa), get(sb)
                D, S = clip(ra["dev"]) + clip(rb["dev"]), clip(ra["std"]) + clip(rb["std"])
                dev, std = clip(ra["dev"]), clip(rb["std"])
                row = dict(ssa=A.ssa_index(D, S))
                for style, cs in E1.ctrl_specs(a, E1.MAIN["p"], s, 400).items():
                    d = A.decompose(dev, std, clip(get(with_net(cs, tau))["ctr"]), normalise=True)
                    row[f"iMM_{style}"], row[f"iRS_{style}"], row[f"iPE_{style}"] = d["iMM"], d["iRS"], d["iPE"]
                row["omit"] = get(with_net(E1.omit_spec(a, s, 200), tau))["omit"]
                rows.append(row)
            c = {k: ci([r[k] for r in rows]) for k in rows[0]}
            out[f"exp1|{a}|{tau}"] = c
            L.append(f"| {tau:.0f} | {a} | {fmt(c['ssa'])} | {fmt(c['iMM_cascade'])} | {fmt(c['iRS_cascade'])} | "
                     f"{fmt(c['iPE_cascade'])} | {fmt(c['iPE_many'])} | {fmt(c['omit'])} |")
    L += ["", "## Tier 2 (adaptation = both)", "",
          "| tau_w (ms) | net | unexpected repeat minus regular | omission D- (PE- omitted minus present) | M1 post1 - pre1 (cont. A) | M1 sensory-only (E cells) |",
          "|---|---|---|---|---|---|"]
    cfg = E2.settings(False)
    for tau in TAUS:
        for n in NETS:
            ab = [get(with_net(E2.P(exp="aba", net=n, seed=s, n_slots=cfg["aba"], analyse_from=cfg["aba_from"]), tau)) for s in range(SEEDS)]
            om = [get(with_net(E2.P(exp="omit", net=n, seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"]), tau)) for s in range(SEEDS)]
            ep = [get(with_net(E2.P(exp="ep", net=n, seed=s, cont="A", n_ep=cfg["n_ep"], m=cfg["m"]), tau)) for s in range(SEEDS)]
            c = dict(aba=ci([r["rep_R"] - r["reg_R"] for r in ab]),
                     omit=ci([r["v3_PEm_omit"] - r["v3_PEm_pres"] for r in om]),
                     m1=ci([r["R_post"][0] - r["R_pre1"] for r in ep]),
                     m1s=ci([r["E_post"][0] - r["E_pre1"] for r in ep]))
            out[f"t2|{n}|{tau}"] = c
            L.append(f"| {tau:.0f} | {n} | {fmt(c['aba'])} | {fmt(c['omit'])} | {fmt(c['m1'])} | {fmt(c['m1s'])} |")
    (ROOT / "results" / "sens_slow_summary.json").write_text(json.dumps(out, indent=1, default=float))
    (ROOT / "results" / "sens_slow_summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
