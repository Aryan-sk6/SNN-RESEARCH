"""Experiments 13 (ideal-observer benchmark) and 15 (precision). Design and predictions:
docs/PREREGISTRATION_EXP13_15.md (committed before any run).

    python experiments/exp13_15.py calibrate     # precision constants on development seeds 100-104
    python experiments/exp13_15.py test          # all test runs, 20 test seeds
    python experiments/exp13_15.py report        # tables from the cache
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

import exp2_tier2 as E2                        # noqa: E402
from snn_oddball import exp13_15 as X         # noqa: E402
from snn_oddball.runner import run_specs, spec_key   # noqa: E402
from snn_oddball.stats import mean_ci         # noqa: E402

DEV = [100, 101, 102, 103, 104]
SEEDS = list(range(20))
CACHE = ROOT / "results" / "raw" / "exp13_15"
OUT = ROOT / "results"
STATE = OUT / "exp13_15_state.json"

A_PREC = [0.001, 0.002, 0.005]
K_PREC = [1.0, 2.0, 4.0]
T_REG_MIN = 0.8
T_RAND = (0.35, 0.65)


def S(**kw):
    return dict(kind="x1315", **kw)


def load(spec):
    return json.loads((CACHE / f"{spec_key(spec)}.json").read_text())["result"]


def ci(v):
    m, lo, hi, *_ = mean_ci(list(v))
    return dict(mean=m, lo=lo, hi=hi)


def fmt(d):
    return f"{d['mean']:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]"


# ------------------------------------------------------------------------------------------- calibration
def calib_specs(a, k):
    return [S(exp="prec_calib", seed=s, pp=dict(a_prec=a, k_prec=k)) for s in DEV]


def calibrate(jobs):
    grid = list(itertools.product(A_PREC, K_PREC))
    run_specs([s for a, k in grid for s in calib_specs(a, k)], CACHE, jobs=jobs)
    rows = []
    for a, k in grid:
        r = [load(s) for s in calib_specs(a, k)]
        g_reg, g_rnd = float(np.mean([x["gain_regular"] for x in r])), float(np.mean([x["gain_random"] for x in r]))
        ok = (g_reg >= T_REG_MIN) + (T_RAND[0] <= g_rnd <= T_RAND[1])
        rows.append(dict(a=a, k=k, gain_regular=g_reg, gain_random=g_rnd, met=int(ok)))
    best = min(rows, key=lambda r: (-r["met"], abs(r["gain_random"] - 0.5)))
    return rows, dict(a_prec=best["a"], k_prec=best["k"])


# ------------------------------------------------------------------------------------------- test specs
def test_specs(ppP):
    cfg = E2.settings(False)
    sp = dict(random=[], probe=[], t2=[], trace=[], curve=[])
    for s in SEEDS:
        for n in ("A2b", "A2bP"):
            extra = dict(pp=ppP) if n == "A2bP" else {}
            sp["random"].append(E2.P(exp="random", net=n, seed=s, n_slots=cfg["random"], **extra))
            for c in ("regular", "random"):
                sp["probe"].append(dict(S(exp="probe", net=n, seed=s, context=c, n_slots=200), **extra))
        sp["t2"].append(E2.P(exp="aba", net="A2bP", seed=s, n_slots=cfg["aba"], analyse_from=cfg["aba_from"], pp=ppP))
        sp["t2"].append(E2.P(exp="omit", net="A2bP", seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"], pp=ppP))
        for n in ("N0", "B", "A2b"):
            sp["trace"].append(S(exp="trace", net=n, seed=s, n_slots=cfg["aba"]))
        # learning curve on the alternation: the re-tune sanity block (A2b fast and B slow exposures), original constants
        sp["curve"].append(dict(kind="retune_calib", tau=300.0, seed=s,
                                pp=dict(w_ed_mV=22.0, w_e_pe_mV=18.0, w_e_pm_mV=40.0, kappa_learn=3.0, eta=0.0004)))
    return sp


def report(ppP):
    sp = test_specs(ppP)
    out, L = {}, []
    by = lambda lst, **f: [load(s) for s in lst if all(s.get(k) == v for k, v in f.items())]

    # ---- Experiment 15
    L += ["## Experiment 15: precision (20 test seeds, mean [95% CI])", ""]
    rA, rP = by(sp["random"], net="A2b"), by(sp["random"], net="A2bP")
    dA = [r["err_second"] - r["err_first"] for r in rA]
    dP = [r["err_second"] - r["err_first"] for r in rP]
    out["random"] = dict(A2b_first=ci(r["err_first"] for r in rA), A2b_second=ci(r["err_second"] for r in rA),
                         A2bP_first=ci(r["err_first"] for r in rP), A2bP_second=ci(r["err_second"] for r in rP),
                         A2b_change=ci(dA), A2bP_change=ci(dP), diff=ci(np.subtract(dP, dA)))
    o = out["random"]
    L += ["### Random context: total error per tone, first vs second half (200 tones)", "",
          "| net | first half | second half | change |", "|---|---|---|---|",
          f"| A2b | {fmt(o['A2b_first'])} | {fmt(o['A2b_second'])} | {fmt(o['A2b_change'])} |",
          f"| A2bP | {fmt(o['A2bP_first'])} | {fmt(o['A2bP_second'])} | {fmt(o['A2bP_change'])} |",
          "", f"Change A2bP minus change A2b (paired): {fmt(o['diff'])}", ""]

    L += ["### Probe tone D in a regular vs random context", "",
          "| net | context | D error (PE+ and PE-) | D PE+ | D sensory E | precision gain at probe | context error per tone |",
          "|---|---|---|---|---|---|---|"]
    ctxeff = {}
    for n in ("A2b", "A2bP"):
        reg, rnd = by(sp["probe"], net=n, context="regular"), by(sp["probe"], net=n, context="random")
        for c, rr in (("regular", reg), ("random", rnd)):
            L.append(f"| {n} | {c} | {fmt(ci(r['probe_err'] for r in rr))} | {fmt(ci(r['probe_PEp'] for r in rr))} | "
                     f"{fmt(ci(r['probe_E'] for r in rr))} | {fmt(ci(r['gain_probe'] for r in rr))} | "
                     f"{fmt(ci(r['ctx_err'] for r in rr))} |")
        ctxeff[n] = [b["probe_err"] - a["probe_err"] for a, b in zip(reg, rnd)]
        out[f"probe_ctx_{n}"] = ci(ctxeff[n])
    out["probe_ctx_diff"] = ci(np.subtract(ctxeff["A2bP"], ctxeff["A2b"]))
    L += ["", f"Context effect on D error (random minus regular): A2b {fmt(out['probe_ctx_A2b'])}; "
          f"A2bP {fmt(out['probe_ctx_A2bP'])}; A2bP minus A2b {fmt(out['probe_ctx_diff'])}", ""]

    ab, om = by(sp["t2"], exp="aba"), by(sp["t2"], exp="omit")
    out["t2_A2bP"] = dict(repeat=ci(r["rep_R"] - r["reg_R"] for r in ab), regular=ci(r["reg_R"] for r in ab),
                          omission=ci(r["v3_PEm_omit"] - r["v3_PEm_pres"] for r in om))
    o = out["t2_A2bP"]
    L += ["### No-harm check: A2bP on the main tests", "",
          f"Unexpected repeat minus regular: {fmt(o['repeat'])} (regular response {fmt(o['regular'])}); "
          f"omission D-: {fmt(o['omission'])}", ""]

    # ---- Experiment 13
    L += ["## Experiment 13: ideal-observer benchmark", ""]
    obs = X.observer_exposures_alternation()
    cur = [load(s) for s in sp["curve"]]
    fast, slow = [r["fast_exposures"] for r in cur], [r["slow_exposures"] for r in cur]
    out["exposures"] = dict(observer=obs, A2b=ci(fast), B=ci(slow), B_censored=int(sum(x >= 100 for x in slow)),
                            ratio_A2b=ci(np.array(fast) / obs), ratio_B=ci(np.array(slow) / obs))
    o = out["exposures"]
    L += ["### Exposures to learn the alternation (error below 50% of naive)", "",
          f"Ideal observer: {obs:.0f}. A2b: {fmt(o['A2b'])} (ratio {fmt(o['ratio_A2b'])}). "
          f"B: {fmt(o['B'])} (ratio {fmt(o['ratio_B'])}; {o['B_censored']} seeds censored at 100).", ""]

    L += ["### Tone-by-tone: network error vs observer surprise (Spearman r per seed, slots >= 80)", "",
          "| net | measure | mean r |", "|---|---|---|"]
    for n in ("N0", "B", "A2b"):
        rs = []
        for r in by(sp["trace"], net=n):
            _, sur = X.observer_surprise(r["tones"])
            y = np.array(r["E"] if n == "N0" else r["err"])[80:]
            rs.append(spearmanr(sur[80:], y).statistic)
        out[f"corr_{n}"] = ci(rs)
        L.append(f"| {n} | {'sensory E' if n == 'N0' else 'own-channel error'} | {fmt(out[f'corr_{n}'])} |")
    L.append("")

    halves = []
    import snn_oddball.tier2 as T
    for s in SEEDS:
        seq = T.seq_random(200, T._rng(dict(seed=s), "random"))
        _, sur = X.observer_surprise(seq.tones)
        halves.append((sur[:100].mean(), sur[100:].mean()))
    h = np.array(halves)
    out["observer_random"] = dict(first=ci(h[:, 0]), second=ci(h[:, 1]))
    L += ["### Ideal observer in the random context (bits per tone; 2 bits = chance)", "",
          f"First half {fmt(out['observer_random']['first'])}, second half {fmt(out['observer_random']['second'])}.", ""]
    return out, L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["calibrate", "test", "report"])
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    if a.cmd == "calibrate":
        rows, ppP = calibrate(a.jobs)
        st.update(calib=rows, ppP=ppP)
    elif a.cmd == "test":
        sp = test_specs(st["ppP"])
        run_specs([s for v in sp.values() for s in v], CACHE, jobs=a.jobs)
    L = ["# Experiments 13 and 15: results", "", "Design: `docs/PREREGISTRATION_EXP13_15.md`.", ""]
    if "calib" in st:
        L += ["## Precision calibration (development seeds 100-104)", "",
              f"Targets: gain in a regular context >= {T_REG_MIN}; gain in a random context in {list(T_RAND)}.", "",
              "| a_prec | k_prec | gain regular | gain random | targets met |", "|---|---|---|---|---|"]
        L += [f"| {r['a']} | {r['k']} | {r['gain_regular']:.2f} | {r['gain_random']:.2f} | {r['met']}/2"
              + (" **(selected)**" if r["a"] == st["ppP"]["a_prec"] and r["k"] == st["ppP"]["k_prec"] else "") + " |"
              for r in st["calib"]]
        L.append("")
    if a.cmd in ("test", "report") and "ppP" in st:
        out, L2 = report(st["ppP"])
        st["results"] = out
        L += L2
    STATE.write_text(json.dumps(st, indent=1, default=float))
    (OUT / "exp13_15_summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
