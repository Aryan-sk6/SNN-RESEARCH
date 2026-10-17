"""Run many block specs in parallel with an on-disk cache (re-running resumes where it stopped)."""

from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from .blocks import run_block


def spec_key(spec: dict) -> str:
    return hashlib.sha1(json.dumps(spec, sort_keys=True).encode()).hexdigest()[:16]


def _work(args):
    spec, path = args
    out = run_block(spec)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"spec": spec, "result": out}, f)
    os.replace(tmp, path)
    return spec_key(spec)


def run_specs(specs, cache_dir, jobs=1, verbose=True):
    """Return {spec_key: result}; computes only the specs that are not cached."""
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    todo = [(s, str(cache / f"{spec_key(s)}.json")) for s in specs if not (cache / f"{spec_key(s)}.json").exists()]
    if verbose:
        print(f"[runner] {len(specs)} blocks, {len(specs) - len(todo)} cached, {len(todo)} to run, jobs={jobs}",
              flush=True)
    t0 = time.time()
    if todo:
        if jobs <= 1:
            for k, a in enumerate(todo, 1):
                _work(a)
                if verbose:
                    print(f"[runner] {k}/{len(todo)} ({time.time() - t0:.0f}s)", flush=True)
        else:
            with ProcessPoolExecutor(max_workers=jobs, mp_context=mp.get_context("spawn")) as ex:
                futs = [ex.submit(_work, a) for a in todo]
                for k, f in enumerate(as_completed(futs), 1):
                    f.result()
                    if verbose and (k % 5 == 0 or k == len(todo)):
                        el = time.time() - t0
                        print(f"[runner] {k}/{len(todo)} done, {el:.0f}s elapsed, "
                              f"~{el / k * (len(todo) - k):.0f}s left", flush=True)
    out = {}
    for s in specs:
        with open(cache / f"{spec_key(s)}.json") as f:
            out[spec_key(s)] = json.load(f)["result"]
    return out
