"""Experiment 2 and the Tier 2 experiments (omission, unexpected repeat, M1-M6, one-shot, timing, ablation, robustness).

    python experiments/exp2_tier2.py --quick            # 5 seeds, shorter sequences
    python experiments/exp2_tier2.py                    # 20 seeds (hours; resumable, cached in results/raw/)
    python experiments/exp2_tier2.py --only omit aba    # a subset of suites
    python experiments/exp2_tier2.py --plot-only

Protocols, measures, predictions and pass rules were fixed in docs/PREREGISTRATION_TIER2.md before any run.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import curve_fit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from snn_oddball import analysis as A                      # noqa: E402
from snn_oddball.runner import run_specs, spec_key         # noqa: E402
from snn_oddball.stats import mean_ci                      # noqa: E402

SUITES = ["omit", "aba", "ep", "oneshot", "buildup", "jitter", "decomp", "random", "ablation", "robust", "long"]
CONTS = ["A", "B", "C", "cycABC", "cycABCB", "random"]
NETS_MAIN = ["N0", "B", "A1", "A2b"]
NETS_3 = ["N0", "B", "A2b"]
COL = {"N0": "#6b6a66", "B": "#2a78d6", "A1": "#1baf7a", "A2b": "#eb6834"}
NAME = {"N0": "adaptation only (N0)", "B": "slow predictive core (B)", "A1": "A1 direct re-prediction",
        "A2b": "A2b hyperactive candidates"}


def settings(quick):
    if quick:
        return dict(seeds=5, omit=100, omit_from=40, aba=120, aba_from=50, n_ep=4, m=8, pairs=8, eps_per_n=3,
                    decomp=100, random=100, jit=[0.3], robust_draws=10, long=300, long_from=200)
    return dict(seeds=20, omit=160, omit_from=60, aba=200, aba_from=80, n_ep=10, m=8, pairs=12, eps_per_n=6,
                decomp=200, random=200, jit=[0.1, 0.3, 0.6], robust_draws=40, long=600, long_from=400)


def P(**kw):
    return dict(kind="pred", **kw)


# ---------------------------------------------------------------------------------------------- specs
ABLATION_FLAGS = ["T", "E", "L", "G", "C"]


def valid_subsets():
    out = []
    for bits in itertools.product([True, False], repeat=5):
        d = dict(zip(ABLATION_FLAGS, bits))
        if d["G"] and not (d["E"] and d["L"]):
            continue
        if d["C"] and not d["G"]:
            continue
        out.append(d)
    return out


def mech_label(d):
    return "".join(k for k in ABLATION_FLAGS if d[k]) or "none"


def robust_pp(draw, rng_seed=12345):
    """Log-uniform factor in [1/3, 3] on the main constants of mechanism A for draw `draw` (draw 0 = defaults)."""
    rng = np.random.default_rng([rng_seed, draw])
    from snn_oddball.predictive import PredParams
    base = PredParams()
    keys = ["a_gate", "kappa_learn", "k_gain", "tau_gate_ms", "c_rep_mV", "c_old_mV", "c_new_mV"]
    return {k: float(getattr(base, k) * np.exp(rng.uniform(-np.log(3), np.log(3)))) for k in keys}


def specs_for(suite, cfg, only_seed=None):
    sp = []
    seeds = range(cfg["seeds"])
    for s in seeds:
        if suite == "omit":
            for n in NETS_MAIN:
                sp.append(P(exp="omit", net=n, seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"]))
        elif suite == "aba":
            for n in NETS_MAIN:
                sp.append(P(exp="aba", net=n, seed=s, n_slots=cfg["aba"], analyse_from=cfg["aba_from"]))
        elif suite == "ep":
            for c in CONTS:
                for n in NETS_3 + (["A1"] if c == "A" else []):
                    sp.append(P(exp="ep", net=n, seed=s, cont=c, n_ep=cfg["n_ep"], m=cfg["m"]))
        elif suite == "oneshot":
            for n in NETS_MAIN:
                sp.append(P(exp="oneshot", net=n, seed=s, n_pairs=cfg["pairs"]))
        elif suite == "buildup":
            for n in NETS_3:
                sp.append(P(exp="buildup", net=n, seed=s, ns=[1, 2, 4, 8], eps_per_n=cfg["eps_per_n"]))
        elif suite == "jitter":
            for n in NETS_3:
                for j in cfg["jit"]:
                    sp.append(P(exp="omit", net=n, seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"], jitter=j))
        elif suite == "decomp":
            for n in NETS_3:
                for k in ("oddA", "oddB", "many", "cascade"):
                    sp.append(P(exp="decomp", net=n, seed=s, seqkind=k, n_trials=cfg["decomp"], p_dev=0.25))
        elif suite == "random":
            for n in NETS_3:
                sp.append(P(exp="random", net=n, seed=s, n_slots=cfg["random"]))
        elif suite == "ablation":
            for d in valid_subsets():
                for ex, ns_, fr in (("omit", cfg["omit"], cfg["omit_from"]), ("aba", cfg["aba"], cfg["aba_from"])):
                    sp.append(P(exp=ex, net=mech_label(d), mech=dict(d), seed=s, n_slots=ns_, analyse_from=fr))
        elif suite == "long":
            for n in ("B", "A2b"):
                sp.append(P(exp="omit", net=n, seed=s, n_slots=cfg["long"], analyse_from=cfg["long_from"]))
                sp.append(P(exp="aba", net=n, seed=s, n_slots=cfg["long"], analyse_from=cfg["long_from"]))
        elif suite == "robust":
            pass
    if suite == "robust":
        for dr in range(cfg["robust_draws"]):
            ppd = robust_pp(dr)
            for ex, ns_, fr in (("omit", cfg["omit"], cfg["omit_from"]), ("aba", cfg["aba"], cfg["aba_from"])):
                sp.append(P(exp=ex, net="A2b", seed=dr, pp=ppd, n_slots=ns_, analyse_from=fr, draw=dr))
    return sp


# ---------------------------------------------------------------------------------------------- helpers
def ci(vals):
    m, lo, hi, n, nn = mean_ci(vals)
    return dict(mean=m, lo=lo, hi=hi, n=n, n_nan=nn)


def passes(d, ref):
    """Pre-registered rule: 95% CI excludes 0 and the effect is at least 10% of the reference response."""
    if not np.isfinite(d["lo"]):
        return False
    return bool(d["lo"] > 0 and d["mean"] >= 0.1 * ref)


def slope(r, lo=0, hi=5):
    y = np.log(np.maximum(np.asarray(r[lo:hi], dtype=float), 0.0) + 1.0)
    return float(np.polyfit(np.arange(len(y)), y, 1)[0])


def fit_exp(y):
    y = np.asarray(y, dtype=float)
    x = np.arange(len(y))
    try:
        popt, _ = curve_fit(lambda x, rinf, r1, lam: rinf + (r1 - rinf) * np.exp(-lam * x), x, y,
                            p0=[y[-3:].mean(), y[0], 0.5], bounds=([-10, -10, 0], [200, 200, 5]), maxfev=4000)
        return float(popt[0]), float(popt[2]), True
    except Exception:
        return np.nan, np.nan, False


# ---------------------------------------------------------------------------------------------- aggregation
def agg_omit(cfg, get, jitter=None):
    out = {}
    for n in NETS_MAIN if jitter is None else NETS_3:
        rows = []
        for s in range(cfg["seeds"]):
            kw = dict(exp="omit", net=n, seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"])
            if jitter is not None:
                kw["jitter"] = jitter
            rows.append(get(P(**kw)))
        om, pr = ci([r["omit_R"] for r in rows]), ci([r["pres_R"] for r in rows])
        out[n] = dict(omit_R=om, pres_R=pr, omit_PEm=ci([r["omit_PEm"] for r in rows]),
                      post_minus_pres=ci([r["post_R"] - r["pres_R"] for r in rows]),
                      P_pre=ci([r["omit_P_pre"] for r in rows]),
                      PEm_q=ci([r["omit_PEm_q"] for r in rows]), PEm_q_pres=ci([r["pres_PEm_q"] for r in rows]),
                      pass_=passes(om, pr["mean"]), halfwidth_over_tone=((om["hi"] - om["lo"]) / 2 / pr["mean"]
                                                                       if pr["mean"] else np.nan))
    return out


def agg_aba(cfg, get):
    out = {}
    for n in NETS_MAIN:
        rows = [get(P(exp="aba", net=n, seed=s, n_slots=cfg["aba"], analyse_from=cfg["aba_from"])) for s in range(cfg["seeds"])]
        d = ci([r["rep_R"] - r["reg_R"] for r in rows])
        reg = ci([r["reg_R"] for r in rows])
        out[n] = dict(diff=d, reg_R=reg, rep_R=ci([r["rep_R"] for r in rows]), pass_=passes(d, reg["mean"]),
                      adaptation_signature=bool(np.isfinite(d["hi"]) and d["hi"] < 0))
    return out


def agg_ep(cfg, get):
    out = {}
    for c in CONTS:
        for n in NETS_3 + (["A1"] if c == "A" else []):
            rows = [get(P(exp="ep", net=n, seed=s, cont=c, n_ep=cfg["n_ep"], m=cfg["m"])) for s in range(cfg["seeds"])]
            entry = dict(
                m1=ci([r["R_post"][0] - r["R_pre1"] for r in rows]), pre1=ci([r["R_pre1"] for r in rows]),
                m1_sensory=ci([r["E_post"][0] - r["E_pre1"] for r in rows]),
                slope_post=ci([slope(r["R_post"]) for r in rows]), slope_init=ci([slope(r["R_init"]) for r in rows]),
                slope_diff=ci([slope(r["R_post"]) - slope(r["R_init"]) for r in rows]),
                err_post1=ci([r["err_post"][0] for r in rows]), gate_1s=ci([r["gate_post1_1s"] for r in rows]),
                R_post=[ci([r["R_post"][k] for r in rows]) for k in range(cfg["m"])],
                err_post=[ci([r["err_post"][k] for r in rows]) for k in range(cfg["m"])],
                R_dev=ci([r["R_dev"] for r in rows]))
            fits = [fit_exp(r["R_post"]) for r in rows]
            entry["r_inf"] = ci([f[0] for f in fits]); entry["lam"] = ci([f[1] for f in fits])
            entry["fit_failures"] = int(sum(not f[2] for f in fits))
            out[f"{c}|{n}"] = entry
    # paired differences against N0 (same seeds)
    for c in CONTS:
        for n in ("B", "A2b"):
            a = [get(P(exp="ep", net=n, seed=s, cont=c, n_ep=cfg["n_ep"], m=cfg["m"])) for s in range(cfg["seeds"])]
            b = [get(P(exp="ep", net="N0", seed=s, cont=c, n_ep=cfg["n_ep"], m=cfg["m"])) for s in range(cfg["seeds"])]
            out[f"{c}|{n}"]["m1_minus_N0"] = ci([(x["R_post"][0] - x["R_pre1"]) - (y["R_post"][0] - y["R_pre1"]) for x, y in zip(a, b)])
    return out


def agg_oneshot(cfg, get):
    out = {}
    for n in NETS_MAIN:
        rows = [get(P(exp="oneshot", net=n, seed=s, n_pairs=cfg["pairs"])) for s in range(cfg["seeds"])]
        first_below = []
        for r in rows:
            pe = np.asarray(r["PEp_B"], dtype=float)
            if pe[0] <= 0:                       # no positive error at the first pair (no error cells, or silent): undefined
                first_below.append(np.nan)
                continue
            hit = np.where(pe < 0.5 * pe[0])[0]
            first_below.append(float(hit[0] + 1) if hit.size else float(len(pe) + 1))   # censored: n_pairs + 1
        ratio = lambda k: [r["PEp_B"][k] / r["PEp_B"][0] if r["PEp_B"][0] > 0 else np.nan for r in rows]
        pe_curve = [ci(ratio(k)) for k in range(cfg["pairs"])]
        out[n] = dict(first_below_half=ci(first_below), frac_pair2=ci(ratio(1)),
                      curve=pe_curve, P_pre_late=ci([np.mean(r["P_pre"][4:]) for r in rows]),
                      P_pre_first=ci([r["P_pre"][0] for r in rows]))
    return out


def agg_buildup(cfg, get):
    out = {}
    for n in NETS_3:
        rows = [get(P(exp="buildup", net=n, seed=s, ns=[1, 2, 4, 8], eps_per_n=cfg["eps_per_n"])) for s in range(cfg["seeds"])]
        out[n] = dict(by_n={str(k): ci([r[f"PEm_{k}"] for r in rows]) for k in (1, 2, 4, 8)},
                      R_by_n={str(k): ci([r[f"R_{k}"] for r in rows]) for k in (1, 2, 4, 8)},
                      slope=ci([np.polyfit(np.log2([1, 2, 4, 8]), [r[f"PEm_{k}"] for k in (1, 2, 4, 8)], 1)[0] for r in rows]))
    return out


def agg_jitter(cfg, get):
    out = {"0.0": agg_omit(cfg, get, jitter=None)}
    out["0.0"] = {n: v for n, v in out["0.0"].items() if n in NETS_3}
    for j in cfg["jit"]:
        out[str(j)] = agg_omit(cfg, get, jitter=j)
    return out


def agg_decomp(cfg, get):
    out = {}
    for n in NETS_3:
        rows = []
        for s in range(cfg["seeds"]):
            g = lambda k: get(P(exp="decomp", net=n, seed=s, seqkind=k, n_trials=cfg["decomp"], p_dev=0.25))["R"]
            dev, std, many, casc = max(g("oddA"), 0), max(g("oddB"), 0), max(g("many"), 0), max(g("cascade"), 0)
            row = dict(dev=dev, std=std, many=many, cascade=casc)
            for style, c in (("cascade", casc), ("many", many)):
                d = A.decompose(dev, std, c, normalise=True)
                row.update({f"{k}_{style}": v for k, v in d.items()})
            rows.append(row)
        out[n] = {k: ci([r[k] for r in rows]) for k in rows[0]}
    return out


def agg_random(cfg, get):
    out = {}
    for n in NETS_3:
        rows = [get(P(exp="random", net=n, seed=s, n_slots=cfg["random"])) for s in range(cfg["seeds"])]
        out[n] = dict(err_first=ci([r["err_first"] for r in rows]), err_second=ci([r["err_second"] for r in rows]),
                      R_second=ci([r["R_second"] for r in rows]))
    return out


def agg_ablation(cfg, get):
    out = {}
    for d in valid_subsets():
        lab = mech_label(d)
        om, ab = [], []
        for s in range(cfg["seeds"]):
            om.append(get(P(exp="omit", net=lab, mech=dict(d), seed=s, n_slots=cfg["omit"], analyse_from=cfg["omit_from"])))
            ab.append(get(P(exp="aba", net=lab, mech=dict(d), seed=s, n_slots=cfg["aba"], analyse_from=cfg["aba_from"])))
        o = ci([r["omit_R"] for r in om]); pr = ci([r["pres_R"] for r in om])
        a = ci([r["rep_R"] - r["reg_R"] for r in ab]); rg = ci([r["reg_R"] for r in ab])
        out[lab] = dict(flags=d, omit=o, aba=a, pass_omit=passes(o, pr["mean"]), pass_aba=passes(a, rg["mean"]),
                        n_components=sum(d.values()))
    both = [k for k, v in out.items() if v["pass_omit"] and v["pass_aba"]]
    out["_smallest_passing_both"] = sorted(both, key=lambda k: (out[k]["n_components"], k))[:3]
    return out


def agg_robust(cfg, get):
    rows = []
    for dr in range(cfg["robust_draws"]):
        ppd = robust_pp(dr)
        o = get(P(exp="omit", net="A2b", seed=dr, pp=ppd, n_slots=cfg["omit"], analyse_from=cfg["omit_from"], draw=dr))
        a = get(P(exp="aba", net="A2b", seed=dr, pp=ppd, n_slots=cfg["aba"], analyse_from=cfg["aba_from"], draw=dr))
        rows.append((o["omit_R"] >= 0.1 * o["pres_R"] and o["omit_R"] > 0, a["rep_R"] - a["reg_R"] >= 0.1 * a["reg_R"] and a["rep_R"] > a["reg_R"]))
    po, pa = np.mean([r[0] for r in rows]), np.mean([r[1] for r in rows])
    return dict(n_draws=len(rows), frac_omit=float(po), frac_aba=float(pa), frac_both=float(np.mean([r[0] and r[1] for r in rows])),
                note="per-draw single-seed pass uses the effect floor only (no CI possible with one seed per draw)")


def agg_long(cfg, get):
    out = {}
    for n in ("B", "A2b"):
        om = [get(P(exp="omit", net=n, seed=s, n_slots=cfg["long"], analyse_from=cfg["long_from"])) for s in range(cfg["seeds"])]
        ab = [get(P(exp="aba", net=n, seed=s, n_slots=cfg["long"], analyse_from=cfg["long_from"])) for s in range(cfg["seeds"])]
        o, pr = ci([r["omit_R"] for r in om]), ci([r["pres_R"] for r in om])
        a, rg = ci([r["rep_R"] - r["reg_R"] for r in ab]), ci([r["reg_R"] for r in ab])
        out[n] = dict(omit=o, pres=pr, omit_PEm_q=ci([r["omit_PEm_q"] for r in om]), aba=a, reg=rg,
                      pass_omit=passes(o, pr["mean"]), pass_aba=passes(a, rg["mean"]))
    return out


AGG = dict(long=agg_long, omit=agg_omit, aba=agg_aba, ep=agg_ep, oneshot=agg_oneshot, buildup=agg_buildup, jitter=agg_jitter,
           decomp=agg_decomp, random=agg_random, ablation=agg_ablation, robust=agg_robust)


# ---------------------------------------------------------------------------------------------- plots
def plot_main(S, cfg, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False, "axes.titlesize": 9.5,
                         "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.edgecolor": "#52514e"})
    fig, ax = plt.subplots(3, 3, figsize=(14, 11), facecolor="#fcfcfb")
    for a_ in ax.ravel():
        a_.set_facecolor("#fcfcfb"); a_.grid(axis="y", color="#e6e5e1", lw=0.6); a_.set_axisbelow(True)

    def err(a_, x, d, c, **kw):
        y = [d["mean"]]
        e = [[d["mean"] - d["lo"]], [d["hi"] - d["mean"]]] if np.isfinite(d["lo"]) else None
        a_.errorbar([x], y, yerr=e, color=c, capsize=3, lw=1.4, **kw)

    def band(a_, xs, ds, c, label=None, ls="-"):
        m = np.array([d["mean"] for d in ds]); lo = np.array([d["lo"] for d in ds]); hi = np.array([d["hi"] for d in ds])
        if np.isfinite(lo).all():
            a_.fill_between(xs, lo, hi, color=c, alpha=0.15, lw=0)
        a_.plot(xs, m, ls, color=c, lw=1.6, label=label, marker="o", ms=3.5)

    if "omit" in S:
        a_ = ax[0, 0]
        for i, n in enumerate(NETS_MAIN):
            d = S["omit"][n]
            a_.bar(i, d["pres_R"]["mean"], width=0.55, color=COL[n], alpha=0.22, lw=0)
            err(a_, i, d["omit_R"], COL[n], fmt="o", ms=6)
        a_.axhline(0, color="#52514e", lw=0.8); a_.set_xticks(range(4)); a_.set_xticklabels(NETS_MAIN)
        a_.set_title("T1 omission: dot = omitted slot, pale bar = tone present"); a_.set_ylabel("R (spikes, 0-180 ms)")
    if "aba" in S:
        a_ = ax[0, 1]
        for i, n in enumerate(NETS_MAIN):
            err(a_, i, S["aba"][n]["diff"], COL[n], fmt="o", ms=6)
        a_.axhline(0, color="#52514e", lw=0.8); a_.set_xticks(range(4)); a_.set_xticklabels(NETS_MAIN)
        a_.set_title("T2 unexpected repeat: repeated A minus regular A"); a_.set_ylabel("R difference (spikes)")
    if "ep" in S:
        a_ = ax[0, 2]
        for i, n in enumerate(NETS_3):
            err(a_, i, S["ep"][f"A|{n}"]["m1"], COL[n], fmt="o", ms=6)
        a_.axhline(0, color="#52514e", lw=0.8); a_.set_xticks(range(3)); a_.set_xticklabels(NETS_3)
        a_.set_title("M1 tone after the odd one minus tone before"); a_.set_ylabel("R difference (spikes)")
        a_ = ax[1, 0]
        for n in NETS_3:
            for j, c in enumerate(["A", "B", "C"]):
                err(a_, j + (NETS_3.index(n) - 1) * 0.2, S["ep"][f"{c}|{n}"]["slope_post"], COL[n], fmt="o", ms=5)
        a_.axhline(0, color="#52514e", lw=0.8); a_.set_xticks(range(3)); a_.set_xticklabels(["A after B", "B after B", "C after B"])
        a_.set_title("M2 drop-off slope after the odd one (log R)"); a_.set_ylabel("slope per position")
        for n in NETS_3:
            a_.plot([], [], "o", color=COL[n], label=n)
        a_.legend(frameon=False, fontsize=7.5)
        a_ = ax[1, 1]
        for c, ls in (("A", "-"), ("B", "--"), ("C", ":")):
            for n in ("A2b",):
                err(a_, ["A", "B", "C"].index(c), S["ep"][f"{c}|{n}"]["err_post1"], COL[n], fmt="o", ms=6)
        d = S["ep"]["A|N0"]["err_post1"]
        a_.set_xticks(range(3)); a_.set_xticklabels(["A returns", "B repeats", "C new"])
        a_.set_title("M3 total error at first post-B tone (A2b)"); a_.set_ylabel("PE+ plus PE- spikes")
        a_ = ax[1, 2]
        xs = np.arange(1, cfg["m"] + 1)
        for c, col in (("A", "#6b6a66"), ("C", "#2a78d6"), ("cycABC", "#1baf7a"), ("random", "#eb6834")):
            band(a_, xs, S["ep"][f"{c}|A2b"]["err_post"], col, label=c)
        a_.axhline(0, color="#52514e", lw=0.8); a_.set_xlabel("position after the odd one")
        a_.set_title("M5 total error by continuation (A2b)"); a_.set_ylabel("PE+ plus PE- spikes"); a_.legend(frameon=False, fontsize=7.5)
    if "oneshot" in S:
        a_ = ax[2, 0]
        for n in NETS_MAIN:
            band(a_, np.arange(1, cfg["pairs"] + 1), S["oneshot"][n]["curve"], COL[n], label=n)
        a_.axhline(1, color="#52514e", lw=0.8, ls=":"); a_.set_xlabel("pair number (8 s apart)")
        a_.set_title("One-shot: positive error at B / first pair"); a_.legend(frameon=False, fontsize=7.5)
    if "buildup" in S:
        a_ = ax[2, 1]
        for n in NETS_3:
            band(a_, [1, 2, 4, 8], [S["buildup"][n]["by_n"][str(k)] for k in (1, 2, 4, 8)], COL[n], label=n)
        a_.set_xscale("log", base=2); a_.set_xticks([1, 2, 4, 8]); a_.set_xticklabels(["1", "2", "4", "8"])
        a_.set_xlabel("regular tones before the omission"); a_.set_title("Timing: negative error at omission vs regularity")
        a_.legend(frameon=False, fontsize=7.5)
    if "jitter" in S:
        a_ = ax[2, 2]
        js = sorted(S["jitter"].keys(), key=float)
        for n in NETS_3:
            band(a_, [float(j) for j in js], [S["jitter"][j][n]["omit_R"] for j in js], COL[n], label=n)
        a_.axhline(0, color="#52514e", lw=0.8); a_.set_xlabel("timing jitter (fraction of the interval)")
        a_.set_title("Timing: omission response vs jitter"); a_.legend(frameon=False, fontsize=7.5)
    mode = "quick" if cfg["seeds"] <= 5 else "full"
    fig.suptitle(f"Tier 2 ({cfg['seeds']} seeds, mean and 95% CI, {mode} run)", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.text(0.01, 0.005, "Simplified spiking model. Says nothing about real brains or clinical use.", fontsize=7.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.015, 1, 0.97))
    fig.savefig(path, dpi=140)
    plt.close(fig)


def fmt(d):
    if not isinstance(d, dict) or "mean" not in d:
        return str(d)
    if not np.isfinite(d["mean"]):
        return "n/a"
    return f"{d['mean']:.2f} [{d['lo']:.2f}, {d['hi']:.2f}]" if np.isfinite(d["lo"]) else f"{d['mean']:.2f}"


def table_md(S, cfg):
    L = [f"# Tier 2 summary ({cfg['seeds']} seeds)", "", "Mean [95% CI over seeds]; R = E + PE+ + PE- spikes in 0-180 ms, baseline-corrected.", ""]
    if "omit" in S:
        L += ["## T1 omission", "", "| net | omitted slot R | tone present R | pass | CI half-width / tone | PE- at omission | PE- at omission (quiet baseline) | PE- at present tone (quiet baseline) | post-omission tone minus tone |", "|---|---|---|---|---|---|---|---|---|"]
        for n in NETS_MAIN:
            d = S["omit"][n]
            L.append(f"| {n} | {fmt(d['omit_R'])} | {fmt(d['pres_R'])} | {d['pass_']} | {d['halfwidth_over_tone']:.3f} | {fmt(d['omit_PEm'])} | {fmt(d['PEm_q'])} | {fmt(d['PEm_q_pres'])} | {fmt(d['post_minus_pres'])} |")
    if "aba" in S:
        L += ["", "## T2 unexpected repeat (A B A B A A)", "", "| net | repeated minus regular | regular R | pass | adaptation signature (repeat smaller) |", "|---|---|---|---|---|"]
        for n in NETS_MAIN:
            d = S["aba"][n]
            L.append(f"| {n} | {fmt(d['diff'])} | {fmt(d['reg_R'])} | {d['pass_']} | {d['adaptation_signature']} |")
    if "ep" in S:
        L += ["", "## M1 / M2 / M3 / M5 (episodes)", "", "| continuation | net | M1 post1 - pre1 (E only: see M1 table) | slope after B | slope initial run | total error post1 | gate 1 s after | r_inf | lambda | fit failures |", "|---|---|---|---|---|---|---|---|---|---|"]
        for k, v in S["ep"].items():
            c, n = k.split("|")
            L.append(f"| {c} | {n} | {fmt(v['m1'])} | {fmt(v['slope_post'])} | {fmt(v['slope_init'])} | {fmt(v['err_post1'])} | {fmt(v['gate_1s'])} | {fmt(v['r_inf'])} | {fmt(v['lam'])} | {v['fit_failures']} |")
        L += ["", "M1 sensory-only (E cells) post1 - pre1, continuation A: " + "; ".join(f"{n}: {fmt(S['ep'][f'A|{n}']['m1_sensory'])}" for n in ('N0', 'B', 'A1', 'A2b'))]
        L += ["", "M1 minus N0 (difference of differences): " + "; ".join(f"{c}/{n}: {fmt(S['ep'][f'{c}|{n}']['m1_minus_N0'])}" for c in ("A",) for n in ("B", "A2b"))]
    if "oneshot" in S:
        L += ["", "## One-shot", "", "| net | first pair with PE+ < half of pair 1 (censored at pairs+1) | PE+ pair 2 / pair 1 | P spikes before B, late pairs |", "|---|---|---|---|"]
        for n in NETS_MAIN:
            d = S["oneshot"][n]
            L.append(f"| {n} | {fmt(d['first_below_half'])} | {fmt(d['frac_pair2'])} | {fmt(d['P_pre_late'])} |")
    if "buildup" in S:
        L += ["", "## Regularity buildup (PE- at the omitted slot by number of regular tones)", "", "| net | n=1 | n=2 | n=4 | n=8 | slope per doubling |", "|---|---|---|---|---|---|"]
        for n in NETS_3:
            d = S["buildup"][n]
            L.append(f"| {n} | " + " | ".join(fmt(d['by_n'][str(k)]) for k in (1, 2, 4, 8)) + f" | {fmt(d['slope'])} |")
    if "jitter" in S:
        L += ["", "## Timing jitter (omission R)", "", "| jitter | " + " | ".join(NETS_3) + " |", "|---|---|---|---|"]
        for j in sorted(S["jitter"], key=float):
            L.append(f"| {j} | " + " | ".join(fmt(S['jitter'][j][n]['omit_R']) for n in NETS_3) + " |")
    if "decomp" in S:
        L += ["", "## M6 decomposition (oddball p = 0.25 vs controls, normalised)", "", "| net | DEV | STD | CTR cascade | CTR many | iMM | iRS | iPE (cascade) | iPE (many) |", "|---|---|---|---|---|---|---|---|---|"]
        for n in NETS_3:
            d = S["decomp"][n]
            L.append(f"| {n} | {fmt(d['dev'])} | {fmt(d['std'])} | {fmt(d['cascade'])} | {fmt(d['many'])} | {fmt(d['iMM_cascade'])} | {fmt(d['iRS_cascade'])} | {fmt(d['iPE_cascade'])} | {fmt(d['iPE_many'])} |")
    if "random" in S:
        L += ["", "## M6 random context: total error per slot", "", "| net | first half | second half | R second half |", "|---|---|---|---|"]
        for n in NETS_3:
            d = S["random"][n]
            L.append(f"| {n} | {fmt(d['err_first'])} | {fmt(d['err_second'])} | {fmt(d['R_second'])} |")
    if "ablation" in S:
        L += ["", "## Ablation (components T, E, L, G, C)", "", "| components | omission R | pass | repeat-minus-regular | pass |", "|---|---|---|---|---|"]
        for k, v in S["ablation"].items():
            if k.startswith("_"):
                continue
            L.append(f"| {k} | {fmt(v['omit'])} | {v['pass_omit']} | {fmt(v['aba'])} | {v['pass_aba']} |")
        L.append(f"\nSmallest subsets passing both: {S['ablation']['_smallest_passing_both']}")
    if "long" in S:
        L += ["", f"## Long training ({cfg['long']} slots, analysed from {cfg['long_from']}): fairness check for the slow core", "", "| net | omission R | PE- at omission (quiet baseline) | pass | repeat minus regular | pass |", "|---|---|---|---|---|---|"]
        for n, d in S["long"].items():
            L.append(f"| {n} | {fmt(d['omit'])} | {fmt(d['omit_PEm_q'])} | {d['pass_omit']} | {fmt(d['aba'])} | {d['pass_aba']} |")
    if "robust" in S:
        r = S["robust"]
        L += ["", "## Robustness (A2b, random constants)", "", f"{r['n_draws']} draws: omission {r['frac_omit']:.2f}, repeat {r['frac_aba']:.2f}, both {r['frac_both']:.2f}. {r['note']}"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--only", nargs="*", default=None, choices=SUITES)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--plot-only", action="store_true")
    ap.add_argument("--seeds", type=int, default=None)
    args = ap.parse_args()
    cfg = settings(args.quick)
    if args.seeds:
        cfg["seeds"] = args.seeds
    tag = "quick" if args.quick else "full"
    suites = args.only or SUITES
    cache = ROOT / "results" / "raw" / f"tier2_{tag}"
    specs = list({spec_key(s): s for su in suites for s in specs_for(su, cfg)}.values())
    res = run_specs(specs, cache, jobs=0 if args.plot_only else args.jobs)
    get = lambda s: res[spec_key(s)]
    S = {su: AGG[su](cfg, get) for su in suites}
    out = ROOT / "results"
    (out / f"tier2_summary_{tag}.json").write_text(json.dumps(dict(config=cfg, summary=S), indent=1, default=lambda o: bool(o) if isinstance(o, (np.bool_,)) else float(o)))
    (out / f"tier2_summary_{tag}.md").write_text(table_md(S, cfg))
    plot_main(S, cfg, out / f"fig2_tier2_{tag}.png")
    print(table_md(S, cfg))


if __name__ == "__main__":
    main()
