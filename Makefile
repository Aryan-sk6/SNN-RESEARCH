# One command per task. `make quick` runs a small version of every experiment (5 seeds).
PY := .venv/bin/python

setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	.venv/bin/pip install -e .

test:
	$(PY) -m pytest -q

fig1:
	$(PY) experiments/exp1_adaptation.py

fig1-quick:
	$(PY) experiments/exp1_adaptation.py --quick

quick: test fig1-quick

.PHONY: setup test fig1 fig1-quick quick
