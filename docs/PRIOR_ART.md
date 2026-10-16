# Prior art: adaptation vs. prediction error in oddball paradigms

Status: **DRAFT, incomplete, awaiting review.** No modelling has been done yet.

## How this file was produced, and what that means for trust

The environment this was written in blocks direct access to publisher and
repository hosts (jneurosci.org, unicog.org, pmc.ncbi.nlm.nih.gov, nature.com,
doi.org, hal.science, biorxiv.org, journals.plos.org, Crossref, OpenAlex were all
refused). **No full text of any paper below was read.**

What *was* available is a web search tool that returns result pages
(titles, URLs) plus short summaries of what those pages say, mostly abstracts
and repository records. Every entry is therefore tagged with a verification
level:

| Level | Meaning |
|---|---|
| **FULL** | Full text read, including methods. *(No entry has this level yet.)* |
| **ABSTRACT** | Bibliographic record and abstract-level claims seen in search results from the publisher, PubMed Central, or an institutional repository. Claims are limited to what the abstract says. |
| **SECONDARY** | The claim was seen only in another paper's description of this work. Treat as unverified until promoted. |

Nothing in this file was written from memory. Where my memory suggested a
detail that I could not find in a retrieved source, I left the detail out.

**Before this repo is made public, every entry relied on for a modelling
decision must be promoted to FULL.** That needs either network access to the
hosts above or the PDFs placed in the repo by hand (see "What I need" at the end).

---

## 1. Wacongne, Changeux & Dehaene (2012), *J Neurosci* 32(11):3665–3678

"A Neuronal Model of Predictive Coding Accounting for the Mismatch Negativity."
DOI 10.1523/JNEUROSCI.5003-11.2012. Open copies are listed at
jneurosci.org, unicog.org and HAL (cea-00842907).

**Verification: ABSTRACT** (plus some SECONDARY detail, marked).

What the abstract-level sources state:
- They build a spiking network model **without synaptic habituation** that
  implements predictive coding, and argue that the MMN reflects active
  prediction rather than passive synaptic habituation.
- They list the model's predictions: a frequency-dependent response to rare
  deviants; **a response to unexpected repeats in alternating sequences
  (ABABAA…)**; **a lack of sensitivity to the global sequence context**; **a
  response to sound omission**; and sensitivity of the MMN to NMDA-receptor
  antagonists.
- They ran a new MEG experiment in healthy participants that they report
  supports the prediction account.
- On omission, a search summary of the full text says the authors state that the
  omission response "does not have exactly the same computational significance
  as the classic oddball MMN." *(SECONDARY: quoted in a search summary, not
  checked against the PDF.)*

Mechanism details, all **SECONDARY** and **not yet trustworthy enough to
implement from**:
- Layer-4 prediction-error activity = thalamic input minus a prediction
  arriving from supragranular layers, with the sign flipped by inhibitory
  interneurons.
- Associations are learned with an NMDA-dependent STDP rule. One survey says
  STDP shapes "memory neuron → prediction neuron" synapses and most other
  weights are random.
- One survey (Predictive Coding with Spiking Neural Networks: a Survey,
  arXiv:2409.05386) says the network uses **Izhikevich neurons, not LIF**,
  with an added NMDA current. This matters for the "replication"
  (Mechanism B), which you asked to build from LIF neurons.

**Important nuance for Experiment 2.** In the abstract, "a lack of
consideration of the global sequence context" is a prediction **of their
own model**: a limitation they predict, not a test that adaptation fails.
So the abstract-level evidence names **omission** and **ABABAA repeats** as
the phenomena their model produces. It does **not**, at this level, say in so
many words that "adaptation alone fails these tests". That is an inference
from their framing (a model *without* habituation that explains them). I
want to confirm the exact wording in the full text before the README says
"adaptation alone is claimed to fail X".

## 2. Parras, Nieto-Diego, Carbajal, Valdés-Baizabal, Escera & Malmierca (2017), *Nat Commun* 8:2148

"Neurons along the auditory pathway exhibit a hierarchical organization of
prediction error." DOI 10.1038/s41467-017-02038-6. PMID 29247159, PMC5732270.

**Verification: ABSTRACT** for the main claims; **SECONDARY** for the index
definitions (taken from later papers that use the same method).

**Note: this is an empirical study, not a review.** The brief calls it "the
review by Parras et al. (2017)". The review by the same group that sets out
the methodology is probably Carbajal & Malmierca (2018), entry 3. I have kept
both. Please confirm which one you meant.

What the abstract-level sources state:
- Single-unit recordings in anaesthetised rats and awake mice, with sequences
  designed to separate prediction error from repetition suppression.
- Prediction-error signals are organised hierarchically. They are present in
  the inferior colliculus and medial geniculate body and grow towards auditory
  cortex (and from lemniscal to non-lemniscal divisions).
- The effects hold across species and across anaesthesia vs. wakefulness.

The control and decomposition methodology (**SECONDARY**: from later papers
that apply the Parras et al. method; to verify):
- Two controls: **many-standards** (the same 10 tones as the cascade, in
  random order, each equiprobable) and **cascade** (the 10 tones in a regular
  ascending or descending order). Later papers describe the cascade as an
  improvement that controls for refractoriness *and* for the regularity of
  the sequence.
- Indices, computed on normalised responses (DEV, STD, CTR):
  - iMM = DEV − STD (index of neuronal mismatch; analogous to the SSA index)
  - iRS = CTR − STD (index of repetition suppression)
  - iPE = DEV − CTR (index of prediction error)
  - so iMM = iRS + iPE, and each index lies in [−1, 1].
- **Not yet verified:** the exact normalisation (I have not seen the
  formula), the oddball deviant probability they used, and their SOA. I will
  not guess these.

## 3. Carbajal & Malmierca (2018), *Trends in Hearing* 22

"The Neuronal Basis of Predictive Coding Along the Auditory Pathway: From the
Subcortical Roots to Cortical Deviance Detection." DOI
10.1177/2331216518784822, PMC6053868. A review.

**Verification: ABSTRACT.**
- Uses predictive coding to connect SSA and MMN research. Proposes splitting
  deviance detection into **repetition suppression** and **prediction
  error**, using the **many-standards** and **cascade** controls from MMN
  research.
- Describes gradients of increasing deviance detection from subcortical to
  cortical stations and from lemniscal to non-lemniscal divisions. Also covers
  neuromodulation and microcircuits.
- Concludes that SSA and MMN are likely the micro- and macroscopic signs of
  the same deviance-detection mechanism. Both are affected by NMDA-receptor
  manipulation.

## 4. Ruhnau, Herrmann & Schröger (2012), *Clin Neurophysiol* 123(3):507–512

"Finding the right control: The mismatch negativity under investigation."
DOI 10.1016/j.clinph.2011.07.035.

**Verification: ABSTRACT.**
- The standard-minus-deviant MMN subtraction can be biased by differences in
  N1 refractoriness. The earlier "random/equiprobable" control (attributed to
  Schröger & Wolff) is argued to *overestimate* the N1 to the deviant.
- They propose a **cascade** (regular ascending/descending sequence) as the
  control. This is the origin of the cascade control that Parras et al. use
  for single units.

## 5. May & Tiitinen (2010), *Psychophysiology* 47(1):66–122

"Mismatch negativity (MMN), the deviance-elicited auditory deflection,
explained."

**Verification: ABSTRACT.**
- The opposing, adaptation-only position: the MMN may not need a memory or
  comparison process. It may instead be fresh-afferent activity of cortical
  neurons under non-uniform adaptation, i.e. a latency- and amplitude-modulated
  N1.
- This is the main "adaptation explains it" reference our Experiment 1 tests.

## 6. Mill, Coath, Wennekers & Denham (2011), *PLoS Comput Biol* 7(8):e1002117

"A Neurocomputational Model of Stimulus-Specific Adaptation to Oddball and
Markov Sequences." PMC3158038.

**Verification: ABSTRACT.**
- A spiking model in which SSA emerges from **depressing synapses** carrying
  feature-specific input. It needs only a few homogeneously connected
  populations and no feature maps. Tuned to awake rat auditory cortex SSA.
- Generalises the oddball paradigm to Markov chains, which vary probability
  and switching rate separately. Predicts stronger SSA at higher switching
  rates.
- Argues that cascades of depressing synapses can tell a *novel* tone from a
  merely *rare* one.
- Closest prior spiking model to our Experiment 1, Mechanism (b).

## 7. Yarden & Nelken (2017), *PLoS Comput Biol* 13(3):e1005437

"Stimulus-specific adaptation in a recurrent network model of primary
auditory cortex." PMC5367837.

**Verification: ABSTRACT.**
- Most earlier SSA models used depression in *feedforward* thalamocortical
  synapses. Here depression in *recurrent intracortical* synapses produces
  population spikes. SSA appears when deviants, but not standards, trigger
  one. Feedforward depression widens the parameter range for SSA.
- Reports that SSA depends on frequency difference, deviant probability, ISI
  and input amplitude. These are the sweep variables we plan to use, so this
  is the comparison for our sweeps.

## 8. Seay, Natan, Geffen & Buonomano (2020), *J Neurosci* 40:9210–9223

"Differential Short-Term Plasticity of PV and SST Neurons Accounts for
Adaptation and Facilitation of Cortical Neurons to Auditory Tones."

**Verification: ABSTRACT (partial).**
- Pyramidal neurons in mouse auditory cortex show both adapting and
  facilitating responses to repeated tones. A reduced spiking model with
  cell-type-specific short-term plasticity (PV vs. SST) accounts for this.
  I did not see the model's detailed conclusions.

## 9. Eissa, …, Mäki-Marttunen (2025 preprint; *Eur J Neurosci* 2026)

"Computational modelling of novelty detection in the mismatch negativity
protocols and its impairments in schizophrenia." bioRxiv
10.1101/2025.09.30.679453, PMC12621899.

**Verification: ABSTRACT.**
- An integrate-and-fire network that detects four kinds of novelty,
  **including omission**. It uses **short-term depressing synapses plus inputs
  phase-locked to the rhythm of the stimulus sequence**.
- Directly relevant to Experiment 2. It is evidence that an omission response
  can come from adaptation **plus a timing/rhythm input**, without a learned
  prediction. A secondary description says omission MMN is hard for realistic
  spiking models because it seems to require activity "in the absence of
  sensory input".

## 10. Supporting empirical / review work (context only, ABSTRACT level)

- **Wacongne et al. (2011), *PNAS* 108(51):20754–20759**, "Evidence for a
  hierarchy of predictions and prediction errors in human cortex." The
  local–global paradigm with EEG/MEG, using mismatching and **omitted**
  stimuli. Higher-order (global) predictions cancel expected local
  mismatches. Background for the "global context" test.
- **Heilbron & Chait (2018; online 2017), *Neuroscience***, "Great
  expectations: Is there evidence for predictive coding in auditory cortex?"
  A critical review. Its sections include "Repetition suppression –
  adaptation or expectation?" and "Hearing silences: omission as a window into
  prediction". Conclusions not verified beyond the abstract.
- **Yaron et al. (2025), *PLoS Biol*, 10.1371/journal.pbio.3003242.**
  Single neurons in rat auditory cortex that respond to omissions in a
  predictable sequence, scaling with predictability. (Author list in the
  search metadata looked garbled. Verify before citing.)
- **Westerberg, Xiong, …, Bastos (preprint, 2024/2025)**, "Adaptation, not
  prediction, drives neuronal spiking responses in mammalian sensory cortex."
  Visual local/global oddballs in mice and monkeys. Local oddball responses
  largely fit adaptation-compatible accounts, and global oddball responses
  largely do not fit predictive coding. Date and DOI unverified, so
  **excluded from any claim** until verified.

## Summary table: which tests is adaptation alone said to fail?

| Test | Who frames it as beyond adaptation | Level | Our expectation for a feedforward adaptation-only net |
|---|---|---|---|
| Deviant > standard (oddball) | Not claimed to fail: May & Tiitinen, Mill et al. and Yarden & Nelken all produce SSA from adaptation | ABSTRACT | Pass |
| Deviant > cascade control (iPE > 0) | Parras et al. report iPE > 0 in data, which a pure refractoriness account would not predict | ABSTRACT/SECONDARY | Unclear. To be measured, not assumed. |
| Omission response | Wacongne 2012 (model produces it), Eissa 2025 (needs rhythmic input), Heilbron & Chait (omission as a window) | ABSTRACT | No input, so no evoked response. Null expected. |
| Unexpected repeat in ABAB…AA | Wacongne 2012 (model produces it) | ABSTRACT | Adaptation predicts the repeated A is *smaller*, not larger. Expected fail. |
| Global context (local–global) | Wacongne 2011 data. Wacongne 2012 predicts its *own* model is blind to it. | ABSTRACT | Out of scope for Experiment 2 as specified. Noted only. |

## Not included, and why

- Anything I remembered but could not find in a retrieved source (e.g.
  specific parameter values of the Wacongne model, Parras's SOA, deviant
  probability and normalisation formula). Left out on purpose.
- The Garagnani, Lieder et al. and Schröger & Wolff original papers:
  mentioned only in passing in search results. Not retrieved, so left out.

## What I need to finish Step 0 properly

1. Either allow these hosts in the environment's network settings
   (`www.jneurosci.org`, `www.unicog.org`, `pmc.ncbi.nlm.nih.gov`,
   `www.ncbi.nlm.nih.gov`, `hal.science`, `www.nature.com`,
   `www.biorxiv.org`, `journals.plos.org`), or put the PDFs in `docs/papers/`
   (not committed to the public repo if licensing is unclear).
2. Then I will read the Wacongne 2012 Methods and Parras 2017 Methods in full
   and promote entries 1–2 to FULL. **Mechanism B cannot be implemented
   honestly from abstract-level information.**
