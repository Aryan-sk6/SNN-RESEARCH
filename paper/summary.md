---
title: "Surprise-gated learning in a spiking network: one-page summary"
author: "Aryan Karjagi"
date: "November 2026"
---

**The question.** When we hear a rare tone among frequent ones, neurons fire more. Is that just tired neurons
(adaptation), or is the brain learning what to expect and signalling surprise (prediction error)? I also wanted to
know what is the *smallest* piece of machinery that turns a network that only adapts into one that learns
expectations quickly.

**What I built.** An open, fully reproducible spiking neural network (120 neurons, Brian2) in which every mechanism can
be switched on and off on its own:
- two kinds of adaptation;
- a predictive-coding core with learned predictions and error neurons;
- my proposal, a **surprise gate**. After a prediction error it briefly speeds up learning, raises sensory gain and
  opens several candidate guesses about what comes next.

I wrote down every prediction and pass rule before running each experiment (pre-registration), ran 20 random seeds per
condition, and published every result, including the predictions that failed. The repository has 50+ unit tests,
one command per figure, and cached, resumable runs.

**What I found.**
1. **Adaptation is not enough.** Adaptation alone reproduces the familiar "bigger response to the rare tone", but
   all of it is repetition suppression. The prediction-error component is zero, and there is no response at all to a
   *missing* tone. This holds even when adaptation is made 10 times slower.
2. **Surprise gating buys speed, not new abilities.** Two tests separate adaptation from expectation: an unexpected
   repeat (ABAB**AA**) and a missing tone. Adaptation gets the repeat backwards (−2.8 spikes). The surprise gate gets
   it right after normal training (+7.6 [4.0, 11.2]). The plain predictive core also gets there, but only with about 3
   times more training. Ablations show that passing both tests needs prediction-error neurons, learning and the gate together.
3. **Honest limits.** One-shot learning, a predicted drop-off ordering and "accepting randomness" were *not*
   supported. [RETUNE RESULT: one sentence on whether the effects survive slower adaptation after re-tuning.]

**Why it matters for AI.** Standard training treats each example in much the same way, whether or not it was surprising. This model
is a small worked example of a different rule: **learn fast exactly when the world surprises you, and keep a few
competing hypotheses open while you do**. That is the core of sample-efficient, continual learning: adapt to a change
in a handful of examples without overwriting everything else. The failures are informative too. The gate alone never
stops reacting to pure noise, so a system also needs a sense of how predictable its input is (precision) before it
can tell surprise from randomness. That is the next step I am building.

**What this shows about how I work.** I take an idea of my own, turn it into a mechanism that can fail, test it against
strong baselines, and report it straight, including when it does not work.

*Paper (8 pages) and code:* github.com/Aryan-sk6/SNNresearch, `paper/paper.pdf`.
