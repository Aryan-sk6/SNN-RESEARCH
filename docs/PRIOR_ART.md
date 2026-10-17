# Prior art: adaptation vs. prediction error in oddball paradigms

Status: **DRAFT, partly upgraded to full text (2026-10-17).** No modelling has been done yet.

Update: the user added PDFs to `docs/`. Wacongne 2012 and Carbajal & Malmierca 2018 were read in
full (entries 1 and 3). Yarden & Nelken 2017 is present but not yet read (entry 7). The Ruhnau 2012
file is a saved web page with the abstract and introduction only (entry 4). **Parras 2017 is still
missing.** Three uploaded files are unrelated to this project (see the end of this file).

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
| **FULL** | Full text read, including methods. *(Entries 1 and 3.)* |
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
DOI 10.1523/JNEUROSCI.5003-11.2012. File: `docs/3665.full.pdf`.

**Verification: FULL** (text extracted from the PDF and read: Methods, Results, start of Discussion;
the last pages of the Discussion and the references were not read closely).

### What the model is (Methods, p. 3666-3667)
- Spiking network of **Izhikevich** neurons (not LIF), regular-spiking excitatory and fast-spiking
  inhibitory. AMPA, NMDA and GABA synapses after Brunel & Wang (2001).
- Per tone column: input (thalamic), **prediction-error** (layer 4) and **predictive**
  (supragranular) populations, each of **40 neurons**, plus interneurons. A **delay-line memory**
  per frequency (400 excitatory + 100 inhibitory neurons) holds the identity and elapsed time of
  past tones; its trace "abruptly vanishes after 400 ms" by assumption.
- Prediction-error neurons get excitation from the thalamus and inhibition (via interneurons)
  from the predictive population. They fire when input is not cancelled. Their activity feeds
  back to the predictive population.
- **Only plasticity**: STDP (NMDA-dependent, plus a small depression on every presynaptic spike)
  on synapses from memory neurons to predictive neurons. Parameters given: cp = 60, tau_p = 30 ms,
  cd = 100, Th = 2.5. They write that the qualitative results were "largely independent of the
  fine tuning of the parameters".
- **No synaptic habituation**: "devoid of synaptic habituation".
- Tone input: extra current 1.9 into the thalamic subpopulation. Noise currents on all populations.
  Each condition on 5-10 freshly generated networks.
- Their "MMN" is a **proxy**: difference in summed synaptic currents received by a layer (sMMN),
  not a spike-count difference.

### Paradigms simulated and what they show
| Paradigm | Setup in the paper | Result they report |
|---|---|---|
| Oddball, deviant probability | 2000 tones, deviants 5/10/20/30%, **SOA 200 ms**, two non-overlapping tones | sMMN grows as deviants get rarer |
| Alternation (ABABA...) | A and B alternate, **150 ms**; rare B replaced by A; 1500 alternating pairs in Methods (ISI 200 ms) | the unexpected repeat gives an sMMN: the network "learns to predict that after an A comes a B at 150 ms" |
| Global context | 150 sequences of AAAAB, ISI 150 ms, 70% AAAAB, 20% AAAAA, 10% AAAA, SOA between sequences 1.2 s | final B still gives an MMN although the sequence is predictable: the model is blind to the global rule, as in Bekinschtein 2009 |
| Omission | pairs AB, ISI 150 ms, pairs 500 ms apart; 10% omit B; compared with **A alone in a block where A is the only stimulus** | response to the missing B. The paper says this "reflects solely a predictive component and not a prediction error per se" and predicts it should resist NMDA blockade once transitions are learned |
| Duration / ISI | 150 vs 200 ms sounds | "predictions that are focused in time fail to cancel incoming inputs that are shifted in time", so timing deviants also give a response |

### What it says about adaptation / habituation
- May & Tiitinen (2010) are cited as arguing synaptic habituation suffices. For the alternation
  case the paper says May & Tiitinen explain it by **higher-order neurons habituating to the AB
  pair as a whole**.
- The alternation result is described as "counter-intuitive for habituation models": a simple
  stimulus-specific habituation account predicts a **smaller** response to the repeated tone, not
  a larger one.
- Their own test: pairs AB 200 ms apart, **more than 10 s** between pairs, rare AA pairs. Habituation
  predicts a reduced response to the second A; their model predicts an MMN. Five participants,
  MEG, all showed the MMN-like effect; the BA vs BB controls showed no significant difference.
  **Caveat:** n = 5 and the controls' trend is discussed by the authors themselves.
- They state the two hypotheses "are not logically exclusive" and that habituation may contribute.
  So the paper does **not** claim habituation is absent in real brains.
- Not found in the paper: any statement that adaptation fails the omission test. That is **our**
  logical point (no input, so no evoked response), plus the omission literature they cite.

### Directly relevant to the user's timing point
- Page 3671: the model "predicts that the MMN should reappear as soon as the temporal prediction
  of B is made impossible, either by spacing the B presentations beyond the capacity of the memory
  neurons, or by making B appear at irregular time intervals".
- Caution: in this model a **change** of timing after a regular rhythm is itself an error (see the
  duration/ISI row). Irregular timing removes the sharp prediction, but a sudden shift away from
  an established rhythm still counts. This should be tested, not assumed.

### Implications for Mechanism B (the replication)
- A faithful replication needs Izhikevich neurons, NMDA synapses, a delay-line memory and STDP.
  Our LIF network with 10 channels will be a **loose** replication. Every departure must be listed.
- Their omission control is a *different block* (A alone), which differs from our plan to compare
  omission with baseline. Both comparisons should be reported.

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

"The Neuronal Basis of Predictive Coding Along the Auditory Pathway: From the Subcortical Roots to
Cortical Deviance Detection." DOI 10.1177/2331216518784822. File: `docs/carbajal-malmierca-2018-...pdf`.
A review.

**Verification: FULL for the control and decomposition logic (Figure 1 and the section on controls
were read); the neurochemistry sections were not read.**
- SSA is "quantified as the index of change in the firing rate of a neuron in response to a deviant
  stimulus when compared with its response to that same stimulus played as a standard".
- The oddball "confounds the effects of adaptation and expectation" (citing Ruhnau 2012).
- A control must (1) not repeat the target tone, and (2) account for the general state of
  refractoriness. A "deviant-alone" control (standards muted) is **not** a valid benchmark.
- **Many-standards**: target tone in a random succession of several equiprobable tones, each with
  "the same probability of appearance as the deviant of the oddball sequence". The paper warns it
  "might be somewhat conservative" about prediction error, because random sequences may still
  generate prediction error and so overestimate repetition suppression.
- **Cascade**: control tones in an organised ascending or descending frequency succession; each
  direction is compared with the matching oddball direction. It also controls cross-frequency
  adaptation and pitch-glide effects.
- Decomposition (Figure 1c caption): control minus standard = **repetition suppression**;
  deviant minus control, "if positive", = **prediction error**.
- Figure 5 caption: indices are computed from **normalised** responses, relative to the control
  baseline. The normalisation formula is not given in this review.
- Conclusion: SSA and MMN are likely micro and macro manifestations of one deviance-detection
  mechanism.

**This matters for our controls.** The many-standards definition fixes the control tone probability
equal to the oddball **deviant probability**. So a 20% deviant calls for a control of five equiprobable
tones, and a 10-tone cascade or many-standards sequence matches a 10% deviant. This supports the
matched-probability default in `PLAN.md`.

## 4. Ruhnau, Herrmann & Schröger (2012), *Clin Neurophysiol* 123(3):507–512

"Finding the right control: The mismatch negativity under investigation."
DOI 10.1016/j.clinph.2011.07.035. File: `docs/Some paper.rtf` (a saved web page).

**Verification: ABSTRACT** (the file holds the abstract, highlights and the start of the introduction only).
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
auditory cortex." PMC5367837. File: `docs/file-2.pdf` (received, not yet read).

**Verification: ABSTRACT** (full text now available locally, still to be read).
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
| Omission response | Wacongne 2012 (model produces it from learned *predictive* currents, not from error). Eissa 2025 (needs rhythmic input). The claim that adaptation fails here is our own logical point, not stated in Wacongne 2012. | FULL / ABSTRACT | No input, so no evoked response. Null expected. |
| Unexpected repeat in ABAB…AA | Wacongne 2012 (model produces it; paper says habituation predicts a *smaller* response; May & Tiitinen rescue it with higher-order pair-habituating neurons) | FULL | Expected fail. A feedforward adaptation net should respond *less* to the repeated A. |
| Global context (local–global) | Wacongne 2012: its own model is **blind** to global regularities, as in Bekinschtein 2009 (AAAAB). Not a failure of adaptation. | FULL | Out of scope for Experiment 2 as specified. Noted only. |

## Not included, and why

- Anything I remembered but could not find in a retrieved source (e.g.
  specific parameter values of the Wacongne model, Parras's SOA, deviant
  probability and normalisation formula). Left out on purpose.
- The Garagnani, Lieder et al. and Schröger & Wolff original papers:
  mentioned only in passing in search results. Not retrieved, so left out.

## Files uploaded that are not part of this project

`docs/2025.01.15.633190v1.full.pdf` (an amygdala-cortex fear-memory preprint),
`docs/2509.26507v1.pdf` (The Dragon Hatchling) and `docs/file.pdf` (Dynamic Phenotypic Clustering in
Noisy Ecosystems) do not relate to oddball or SSA modelling and are **not used or cited**.

## What I need to finish Step 0 properly (superseded, see top; kept for the record)

1. Either allow these hosts in the environment's network settings
   (`www.jneurosci.org`, `www.unicog.org`, `pmc.ncbi.nlm.nih.gov`,
   `www.ncbi.nlm.nih.gov`, `hal.science`, `www.nature.com`,
   `www.biorxiv.org`, `journals.plos.org`), or put the PDFs in `docs/papers/`
   (not committed to the public repo if licensing is unclear).
2. Then I will read the Wacongne 2012 Methods and Parras 2017 Methods in full
   and promote entries 1–2 to FULL. **Mechanism B cannot be implemented
   honestly from abstract-level information.**
