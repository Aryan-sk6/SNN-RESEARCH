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

fig2:
	$(PY) experiments/exp2_tier2.py

fig2-quick:
	$(PY) experiments/exp2_tier2.py --quick

quick-all: test fig1-quick fig2-quick

.PHONY: fig2 fig2-quick quick-all
