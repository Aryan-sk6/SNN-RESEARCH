"""Re-tune the predictive circuit for slower spike-frequency adaptation, then re-run the main Tier 2 tests.

Design, targets, search grid and selection rule: docs/RETUNE_SLOW_ADAPTATION.md (written before any run at the new
time constants). The sanity targets are the ones in docs/PARAMETERS.md; they use development seeds 100-104 only and
never an omission, unexpected-repeat or post-oddball measure.

    python experiments/retune_slow_adaptation.py check            # protocol check at tau_w = 300 ms, original constants
    python experiments/retune_slow_adaptation.py calibrate 1000   # grid search on development seeds
    python experiments/retune_slow_adaptation.py test 1000        # 20 test seeds with the selected constants
    python experiments/retune_slow_adaptation.py report           # tables from the cache
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from snn_oddball import predictive as PR      # noqa: E402
from snn_oddball.runner import run_specs, spec_key   # noqa: E402
from snn_oddball.stats import mean_ci          # noqa: E402

DEV_SEEDS = [100, 101, 102, 103, 104]
TEST_SEEDS = list(range(20))
OUT = ROOT / "results"
CACHE = OUT / "raw" / "retune"

# Search grid (fixed in the design doc). f_e scales the three weights driven by the sensory cells
# (E -> delay line, E -> PE+, E -> PE-); kappa is the gated learning multiplier; f_eta scales the slow learning rate.
F_E = [1.0, 1.15, 1.3, 1.5, 1.75, 2.0]
KAPPA = [3.0, 4.5, 6.0]
F_ETA = [1.0, 2.0]
BASE = PR.PredParams()

TARGETS = {   # name: (low, high), inclusive
    "err_gain": (0.6, 1.0),        # S1 PE+ / E for an unpredicted (adapted) tone, no learning
    "delay_rate": (0.5, 2.0),      # S2 delay-line spikes per cell per tone at its own lag
    "gate_peak": (0.5, 1.5),       # S3 gate peak within 1 s of the first error
    "fast_exposures": (1.0, 5.0),  # S4 gated learner: exposures until PE+ < 50% of naive ("about 3")
    "pred_err": (0.0, 0.4),        # S5 gated learner: PE+ at learned tones / naive PE+ ("mostly no error")
    "over_pred": (0.0, 0.3),       # S6 gated learner: PE- at present tones / naive PE+
    "slow_exposures": (10.0, 100.0),  # S7 slow learner (B): exposures until PE+ < 50% of naive (100 = never)
}


def overrides(f_e, kappa, f_eta):
    return dict(w_ed_mV=BASE.w_ed_mV * f_e, w_e_pe_mV=BASE.w_e_pe_mV * f_e, w_e_pm_mV=BASE.w_e_pm_mV * f_e,
                kappa_learn=kappa, eta=BASE.eta * f_eta)


def calib_specs(tau, grid):
    return [dict(kind="retune_calib", tau=tau, seed=s, pp=overrides(*c)) for c in grid for s in DEV_SEEDS]


def summarise(rows):
    m = {k: float(np.mean([r[k] for r in rows])) for k in TARGETS}
    met = {k: TARGETS[k][0] <= m[k] <= TARGETS[k][1] for k in TARGETS}
    return m, met


def distance(c):
    f_e, kappa, f_eta = c
    return abs(math.log(f_e)) + abs(math.log(kappa / BASE.kappa_learn)) + abs(math.log(f_eta))


def run_calib(tau, grid, jobs):
    specs = calib_specs(tau, grid)
    run_specs(specs, CACHE, jobs=jobs)
    table = []
    for c in grid:
        rows = [json.loads((CACHE / f"{spec_key(s)}.json").read_text())["result"]
                for s in calib_specs(tau, [c])]
        m, met = summarise(rows)
        table.append(dict(cand=c, metrics=m, met=met, n_met=sum(met.values()), dist=distance(c)))
    return table


def fmt_calib(tau, table, chosen=None):
    L = [f"## Calibration at tau_w = {tau:.0f} ms (development seeds {DEV_SEEDS[0]}-{DEV_SEEDS[-1]})", "",
         "| f_E | kappa | f_eta | " + " | ".join(TARGETS) + " | met |", "|" + "---|" * (len(TARGETS) + 4)]
    for r in table:
        mark = " **(selected)**" if chosen is not None and r["cand"] == chosen else ""
        cells = [f"{r['metrics'][k]:.2f}" + ("" if r["met"][k] else "*") for k in TARGETS]
        L.append(f"| {r['cand'][0]} | {r['cand'][1]} | {r['cand'][2]} | " + " | ".join(cells) +
                 f" | {r['n_met']}/{len(TARGETS)}{mark} |")
    L += ["", "Targets: " + "; ".join(f"{k} in [{lo}, {hi}]" for k, (lo, hi) in TARGETS.items()) +
          ". A star marks a missed target."]
    return L


def select(table):
    """Most targets met; ties broken by the smallest change from the original constants."""
    return min(table, key=lambda r: (-r["n_met"], r["dist"]))["cand"]


# ------------------------------------------------------------------------------------------- test runs
NETS = ["N0", "B", "A1", "A2b"]


def test_specs(tau, ppov):
    import exp2_tier2 as E2
    cfg = E2.settings(False)
    sp = []
    for s in TEST_SEEDS:
        for n in NETS:
            extra = dict(netover=dict(tau_w_ms=tau), retune=1)
            if n != "N0":
                extra["pp"] = ppov
            sp.append(E2.P(exp="aba", net=n, seed=s, n_slots=cfg["aba"], analyse_from=cfg["aba_from"], **extra))
            sp.append(E2.P(exp="omit", net=n, seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"], **extra))
            sp.append(E2.P(exp="ep", net=n, seed=s, cont="A", n_ep=cfg["n_ep"], m=cfg["m"], **extra))
    return sp


def ci(v):
    m, lo, hi, *_ = mean_ci(v)
    return dict(mean=m, lo=lo, hi=hi)


def fmt(d):
    return f"{d['mean']:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]"


def test_table(tau, ppov):
    sp = test_specs(tau, ppov)
    get = lambda s: json.loads((CACHE / f"{spec_key(s)}.json").read_text())["result"]
    by = {}
    for s in sp:
        by.setdefault((s["net"], s["exp"]), []).append(get(s))
    out, L = {}, [f"## Tier 2 at tau_w = {tau:.0f} ms with re-tuned constants (20 test seeds)", "",
                  "| net | unexpected repeat minus regular | omission D- (PE- omitted minus present) | "
                  "M1 post1 - pre1 | M1 sensory-only (E) |", "|---|---|---|---|---|"]
    for n in NETS:
        ab, om, ep = by[(n, "aba")], by[(n, "omit")], by[(n, "ep")]
        c = dict(aba=ci([r["rep_R"] - r["reg_R"] for r in ab]),
                 omit=ci([r["v3_PEm_omit"] - r["v3_PEm_pres"] for r in om]),
                 m1=ci([r["R_post"][0] - r["R_pre1"] for r in ep]),
                 m1s=ci([r["E_post"][0] - r["E_pre1"] for r in ep]))
        out[n] = c
        L.append(f"| {n} | {fmt(c['aba'])} | {fmt(c['omit'])} | {fmt(c['m1'])} | {fmt(c['m1s'])} |")
    m1n0 = by[("N0", "ep")]
    for n in ("B", "A1", "A2b"):
        d = ci([a["R_post"][0] - a["R_pre1"] - (z["R_post"][0] - z["R_pre1"]) for a, z in zip(by[(n, "ep")], m1n0)])
        out[n]["m1_minus_n0"] = d
        L.append(f"\nM1 {n} minus N0 (paired): {fmt(d)}")
    return out, L


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "calibrate", "test", "report"])
    ap.add_argument("tau", nargs="?", type=float)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    state_p = OUT / "retune_state.json"
    state = json.loads(state_p.read_text()) if state_p.exists() else {}
    if a.cmd == "check":
        table = run_calib(300.0, [(1.0, 3.0, 1.0)], a.jobs)
        state["check_300"] = table
        print("\n".join(fmt_calib(300.0, table)))
    elif a.cmd == "calibrate":
        grid = list(itertools.product(F_E, KAPPA, F_ETA))
        table = run_calib(a.tau, grid, a.jobs)
        chosen = select(table)
        state[f"calib_{a.tau:.0f}"] = dict(table=table, chosen=list(chosen))
        print("\n".join(fmt_calib(a.tau, table, chosen)))
    elif a.cmd == "test":
        chosen = state[f"calib_{a.tau:.0f}"]["chosen"]
        ppov = overrides(*chosen)
        run_specs(test_specs(a.tau, ppov), CACHE, jobs=a.jobs)
        out, L = test_table(a.tau, ppov)
        state[f"test_{a.tau:.0f}"] = dict(chosen=chosen, pp=ppov, results=out)
        print("\n".join(L))
    state_p.write_text(json.dumps(state, indent=1, default=float))
    if a.cmd == "report" or a.cmd in ("calibrate", "test", "check"):
        L = ["# Re-tune for slower adaptation: results", "",
             "Design and rules: `docs/RETUNE_SLOW_ADAPTATION.md`. Mean over development seeds for calibration; "
             "mean [95% CI] over 20 test seeds for the tests.", ""]
        if "check_300" in state:
            L += ["### Protocol check: original constants at tau_w = 300 ms", ""] + fmt_calib(300.0, [
                dict(r, cand=tuple(r["cand"])) for r in state["check_300"]])[2:] + [""]
        for tau in (1000, 3000):
            if f"calib_{tau}" in state:
                st = state[f"calib_{tau}"]
                L += fmt_calib(tau, [dict(r, cand=tuple(r["cand"])) for r in st["table"]], tuple(st["chosen"])) + [""]
            if f"test_{tau}" in state:
                L += test_table(tau, state[f"test_{tau}"]["pp"])[1] + [""]
        (OUT / "retune_summary.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
