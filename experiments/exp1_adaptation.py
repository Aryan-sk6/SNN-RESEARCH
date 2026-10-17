"""Experiment 1: what does adaptation alone explain?

    python experiments/exp1_adaptation.py            # 20 seeds, 400 trials (hours; resumable)
    python experiments/exp1_adaptation.py --quick    # 5 seeds, 120 trials, reduced sweeps (minutes)
    python experiments/exp1_adaptation.py --plot-only

Design, measures and predictions were fixed first in docs/PREREGISTRATION.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from snn_oddball import analysis as A          # noqa: E402
from snn_oddball.runner import run_specs, spec_key   # noqa: E402
from snn_oddball.stats import mean_ci          # noqa: E402

D_CH = 6                      # target (deviant) channel; standard channel is D_CH - gap
ISI = [300.0, 500.0]          # silent gap between pulses, ms (brief: 300-500)
MAIN = dict(gap=3, p=0.1)


def settings(quick: bool):
    if quick:
        return dict(n_trials=120, seeds=5, main_adapts=["none", "sfa", "std"], sweep_adapts=["sfa", "std"],
                    gaps=[1, 6], ps=[0.2], n_omit=60)
    return dict(n_trials=400, seeds=20, main_adapts=["none", "sfa", "std", "both"], sweep_adapts=["sfa", "std"],
                gaps=[1, 2, 4, 6], ps=[0.05, 0.2, 0.3], n_omit=200)


def configs(cfg):
    """(adapt, gap, p, with_controls) tuples."""
    out = [(a, MAIN["gap"], MAIN["p"], True) for a in cfg["main_adapts"]]
    for a in cfg["sweep_adapts"]:
        out += [(a, g, MAIN["p"], False) for g in cfg["gaps"]]
        out += [(a, MAIN["gap"], p, p in (0.2,)) for p in cfg["ps"]]
    return out


def odd_specs(adapt, gap, p, seed, n_trials):
    ms = 2 if p >= 0.25 else 3          # min standards before each deviant (3 cannot fit at p >= 0.25)
    base = dict(kind="odd", adapt=adapt, seed=seed, n_trials=n_trials, isi=ISI, p_dev=p, min_std=ms)
    return (dict(base, std=D_CH - gap, dev=D_CH), dict(base, std=D_CH, dev=D_CH - gap))


def ctrl_specs(adapt, p, seed, n_trials):
    n = int(round(1 / p))
    return {s: dict(kind="ctrl", style=s, adapt=adapt, seed=seed, n_trials=n_trials, isi=ISI, target=D_CH,
                    n_tones=n) for s in ("many", "cascade")}


def omit_spec(adapt, seed, n_slots):
    return dict(kind="omit", adapt=adapt, seed=seed, n_trials=n_slots, isi=400.0, tone=D_CH, p_omit=0.2)


def all_specs(cfg):
    sp = []
    for seed in range(cfg["seeds"]):
        for a, g, p, ctl in configs(cfg):
            sp += list(odd_specs(a, g, p, seed, cfg["n_trials"]))
            if ctl:
                sp += list(ctrl_specs(a, p, seed, cfg["n_trials"]).values())
        for a in cfg["main_adapts"]:
            sp.append(omit_spec(a, seed, cfg["n_omit"]))
    return list({spec_key(s): s for s in sp}.values())


def ci_dict(vals):
    m, lo, hi, n, nn = mean_ci(vals)
    return dict(mean=m, lo=lo, hi=hi, n=n, n_nan=nn)


def aggregate(cfg, res):
    get = lambda s: res[spec_key(s)]
    clip = lambda v: max(0.0, v)
    out = {"odd": {}, "omit": {}}
    for a, g, p, ctl in configs(cfg):
        rows = []
        for seed in range(cfg["seeds"]):
            sa, sb = odd_specs(a, g, p, seed, cfg["n_trials"])
            ra, rb = get(sa), get(sb)
            D = clip(ra["dev"]) + clip(rb["dev"])
            S = clip(ra["std"]) + clip(rb["std"])
            row = dict(ssa=A.ssa_index(D, S), dev=clip(ra["dev"]), std=clip(rb["std"]),
                       dev_raw=ra["dev"], std_raw=rb["std"])
            if ctl:
                for style, cs in ctrl_specs(a, p, seed, cfg["n_trials"]).items():
                    c = clip(get(cs)["ctr"])
                    row[f"ctr_{style}"] = c
                    for norm in (True, False):
                        d = A.decompose(row["dev"], row["std"], c, normalise=norm)
                        for k, v in d.items():
                            row[f"{k}_{style}_{'norm' if norm else 'raw'}"] = v
            rows.append(row)
        keys = rows[0].keys()
        out["odd"][f"{a}|gap{g}|p{p}"] = dict(adapt=a, gap=g, p=p,
                                              **{k: ci_dict([r[k] for r in rows]) for k in keys})
    for a in cfg["main_adapts"]:
        rows = [get(omit_spec(a, s, cfg["n_omit"])) for s in range(cfg["seeds"])]
        tone = ci_dict([r["tone"] for r in rows])
        om = ci_dict([r["omit"] for r in rows])
        half = (om["hi"] - om["lo"]) / 2 if np.isfinite(om["hi"]) else float("nan")
        out["omit"][a] = dict(tone=tone, omit=om, omit_win=ci_dict([r["omit_win"] for r in rows]),
                              omit_base=ci_dict([r["omit_base"] for r in rows]),
                              ci_halfwidth_over_tone=half / tone["mean"] if tone["mean"] else float("nan"))
    return out


# ---------------------------------------------------------------------------------------------- plots
COL = {"none": "#6b6a66", "sfa": "#2a78d6", "std": "#eb6834", "both": "#1baf7a"}   # fixed order, validated
NAME = {"none": "no adaptation", "sfa": "spike-freq. adaptation", "std": "short-term depression",
        "both": "both"}


def plot(summary, cfg, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b",
                         "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.titlesize": 10,
                         "axes.titleweight": "bold", "axes.titlelocation": "left"})
    fig, ax = plt.subplots(2, 3, figsize=(13.5, 7.6), facecolor="#fcfcfb")
    for a_ in ax.ravel():
        a_.set_facecolor("#fcfcfb"); a_.grid(axis="y", color="#e6e5e1", lw=0.6); a_.set_axisbelow(True)
    odd, om = summary["odd"], summary["omit"]
    mk = lambda a, g=MAIN["gap"], p=MAIN["p"]: odd.get(f"{a}|gap{g}|p{p}")
    main = [a for a in cfg["main_adapts"] if mk(a)]

    def pt(axx, x, d, c, **kw):
        axx.errorbar(x, d["mean"], yerr=[[d["mean"] - d["lo"]], [d["hi"] - d["mean"]]] if np.isfinite(d["lo"]) else None,
                     color=c, capsize=3, lw=1.4, **kw)

    # (a) SSA index, main condition
    a_ = ax[0, 0]
    for i, a in enumerate(main):
        pt(a_, i, mk(a)["ssa"], COL[a], fmt="o", ms=7)
    a_.axhline(0, color="#52514e", lw=0.8)
    a_.set_xticks(range(len(main))); a_.set_xticklabels([NAME[a].replace(" ", "\n", 1) for a in main], fontsize=8)
    a_.set_ylabel("SSA index (D - S)/(D + S)"); a_.set_title("a  SSA index, p = 0.1, gap = 3")

    # (b) decomposition (normalised, cascade control)
    a_ = ax[0, 1]
    marks = {"iMM": ("o", "iMM  deviant - standard"), "iRS": ("s", "iRS  control - standard"),
             "iPE": ("D", "iPE  deviant - control")}
    for r, a in enumerate(main):
        for j, (k, (m, _)) in enumerate(marks.items()):
            d = mk(a)[f"{k}_cascade_norm"]
            pt(a_, d["mean"], dict(mean=r + (j - 1) * 0.22, lo=r + (j - 1) * 0.22, hi=r + (j - 1) * 0.22), COL[a])
            if np.isfinite(d["lo"]):
                a_.errorbar(d["mean"], r + (j - 1) * 0.22, xerr=[[d["mean"] - d["lo"]], [d["hi"] - d["mean"]]],
                            color=COL[a], capsize=3, lw=1.4, fmt=m, ms=6)
            else:
                a_.plot(d["mean"], r + (j - 1) * 0.22, m, color=COL[a], ms=6)
    a_.axvline(0, color="#52514e", lw=0.8)
    a_.set_yticks(range(len(main))); a_.set_yticklabels([NAME[a].replace(" ", "\n", 1) for a in main], fontsize=8)
    a_.invert_yaxis(); a_.set_xlabel("normalised index (cascade control)")
    a_.set_title("b  Decomposition: iMM = iRS + iPE")
    for k, (m, lab) in marks.items():
        a_.plot([], [], m, color="#52514e", ms=6, label=lab)
    a_.legend(frameon=False, fontsize=7.5, loc="lower right")

    # (c) omission
    a_ = ax[0, 2]
    for i, a in enumerate(main):
        o = om[a]
        a_.bar(i, o["tone"]["mean"], width=0.55, color=COL[a], alpha=0.28, linewidth=0)
        pt(a_, i, o["omit"], COL[a], fmt="o", ms=7)
    a_.axhline(0, color="#52514e", lw=0.8)
    a_.set_xticks(range(len(main))); a_.set_xticklabels([NAME[a].replace(" ", "\n", 1) for a in main], fontsize=8)
    a_.set_ylabel("baseline-corrected spikes (10 cells, 0-180 ms)")
    a_.set_title("c  Omission: pale bar = tone present, dot = omitted")

    def lines(axx, xs, getter, ylab, title, xlab, xmain):
        for a in cfg["sweep_adapts"]:
            pts = [(x, getter(a, x)) for x in xs]
            pts = [(x, d) for x, d in pts if d is not None]
            pts.sort(key=lambda t: t[0])
            if not pts:
                continue
            x = np.array([q[0] for q in pts]); m = np.array([q[1]["mean"] for q in pts])
            lo = np.array([q[1]["lo"] for q in pts]); hi = np.array([q[1]["hi"] for q in pts])
            if np.isfinite(lo).all():
                axx.fill_between(x, lo, hi, color=COL[a], alpha=0.18, lw=0)
            axx.plot(x, m, "-o", color=COL[a], lw=1.6, ms=5, label=NAME[a])
        axx.axhline(0, color="#52514e", lw=0.8); axx.set_xlabel(xlab); axx.set_ylabel(ylab)
        axx.set_title(title); axx.legend(frameon=False, fontsize=8)

    gaps = sorted(set(cfg["gaps"] + [MAIN["gap"]]))
    ps = sorted(set(cfg["ps"] + [MAIN["p"]]))
    lines(ax[1, 0], gaps, lambda a, g: (mk(a, g=g) or {}).get("ssa"), "SSA index",
          "d  SSA vs frequency gap", "gap between standard and deviant (channels)", MAIN["gap"])
    lines(ax[1, 1], ps, lambda a, p: (mk(a, p=p) or {}).get("ssa"), "SSA index",
          "e  SSA vs deviant probability", "deviant probability", MAIN["p"])
    lines(ax[1, 2], gaps, lambda a, g: (mk(a, g=g) or {}).get("iPE_cascade_norm"), "iPE (normalised, cascade)",
          "f  Prediction-error index vs gap (p = 0.1)", "gap between standard and deviant (channels)", MAIN["gap"])
    mode = "quick" if cfg["seeds"] <= 5 else "full"
    fig.suptitle(f"Experiment 1: adaptation alone ({cfg['seeds']} seeds, {cfg['n_trials']} trials; mean and 95% CI; "
                 f"{mode} run)", x=0.01, ha="left", fontsize=11, fontweight="bold")
    fig.text(0.01, 0.005, "Simplified spiking model. Says nothing about real brains or clinical use.",
             fontsize=7.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(path, dpi=150)
    plt.close(fig)


def table_md(summary, cfg):
    f = lambda d: "n/a" if not np.isfinite(d["mean"]) else (f"{d['mean']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}]"
                                                           if np.isfinite(d["lo"]) else f"{d['mean']:.3f}")
    L = [f"# Experiment 1 summary ({cfg['seeds']} seeds, {cfg['n_trials']} trials)", "",
         "Mean [95% CI over seeds]. Responses are baseline-corrected spike counts (10 cells, 0-180 ms).", "",
         "## Main condition (gap 3, p = 0.1)", "",
         "| adaptation | SSA | DEV | STD | CTR cascade | CTR many | iMM | iRS | iPE (cascade) | iPE (many) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for a in cfg["main_adapts"]:
        d = summary["odd"][f"{a}|gap{MAIN['gap']}|p{MAIN['p']}"]
        L.append(f"| {a} | {f(d['ssa'])} | {f(d['dev'])} | {f(d['std'])} | {f(d['ctr_cascade'])} | {f(d['ctr_many'])} | "
                 f"{f(d['iMM_cascade_norm'])} | {f(d['iRS_cascade_norm'])} | {f(d['iPE_cascade_norm'])} | {f(d['iPE_many_norm'])} |")
    L += ["", "NaN seeds in the SSA index (D + S = 0): " +
          ", ".join(f"{a}: {summary['odd'][f'{a}|gap{MAIN['gap']}|p{MAIN['p']}']['ssa']['n_nan']}" for a in cfg["main_adapts"]),
          "", "## Omission check", "",
          "| adaptation | tone present | omitted slot (vs baseline) | window count | baseline count (75 ms) | CI half-width / tone |", "|---|---|---|---|---|---|"]
    for a in cfg["main_adapts"]:
        o = summary["omit"][a]
        L.append(f"| {a} | {f(o['tone'])} | {f(o['omit'])} | {f(o['omit_win'])} | {f(o['omit_base'])} | "
                 f"{o['ci_halfwidth_over_tone']:.3f} |")
    L += ["", "## Sweeps (SSA index, iPE cascade normalised)", "", "| condition | gap | p | SSA | iPE (cascade) |", "|---|---|---|---|---|"]
    for k, d in summary["odd"].items():
        ip = f(d["iPE_cascade_norm"]) if "iPE_cascade_norm" in d else "-"
        L.append(f"| {d['adapt']} | {d['gap']} | {d['p']} | {f(d['ssa'])} | {ip} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--seeds", type=int, default=None)
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--plot-only", action="store_true")
    args = ap.parse_args()
    cfg = settings(args.quick)
    if args.seeds:
        cfg["seeds"] = args.seeds
    tag = "quick" if args.quick else "full"
    cache = ROOT / "results" / "raw" / f"exp1_{tag}"
    specs = all_specs(cfg)
    res = run_specs(specs, cache, jobs=args.jobs) if not args.plot_only else run_specs(specs, cache, jobs=0)
    summary = aggregate(cfg, res)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / f"exp1_summary_{tag}.json").write_text(json.dumps(dict(config=cfg, summary=summary), indent=1,
                                                                default=float))
    (out / f"exp1_summary_{tag}.md").write_text(table_md(summary, cfg))
    plot(summary, cfg, out / f"fig1_adaptation_{tag}.png")
    print(table_md(summary, cfg))
    print(f"wrote results/fig1_adaptation_{tag}.png")


if __name__ == "__main__":
    main()
