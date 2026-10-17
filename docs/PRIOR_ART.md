# Prior art: adaptation vs. prediction error in oddball paradigms

Status: **DRAFT, partly upgraded to full text (2026-10-17).** No modelling has been done yet.

Update: the user added PDFs to `docs/`. Wacongne 2012 and Carbajal & Malmierca 2018 were read in
full (entries 1 and 3). Yarden & Nelken 2017 is present but not yet read (entry 7). The Ruhnau 2012
file is a saved web page with the abstract and introduction only (entry 4). **Parras 2017 was added later and read (entry 2).** Three uploaded files are unrelated to this project (see the end of this file).

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
DOI 10.1523/JNEUROSCI.5003-11.2012. File: `docs/papers/wacongne2012.pdf` (local only, not in git).

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

"Neurons along the auditory pathway exhibit a hierarchical organization of prediction error."
DOI 10.1038/s41467-017-02038-6. File: `docs/papers/parras2017.pdf` (local only, not in git).

**Verification: FULL** (Results, Table 1, Methods "Experimental design" and "Statistical analysis" read;
the Discussion and the supplementary figures were not read closely).

**This is an empirical study, not a review.** The review of the same method is entry 3.

### Design (Methods)
- Single-neuron recordings: 210 neurons in anaesthetised rats (inferior colliculus, medial geniculate
  body, auditory cortex; lemniscal and non-lemniscal divisions), confirmed in awake mice.
- **10 tones** per neuron. Every sequence is **400 tones**, at a **constant** presentation rate:
  **3 Hz for cortex, 4 Hz for IC and MGB** (SOA about 333 ms and 250 ms). No jitter.
- **Oddball**: standard **90%**, deviant **10%** (pseudorandom). The first 10 tones are standards and at
  least 3 standards precede each deviant. Ascending and descending versions.
- **Many-standards**: the 10 tones in random order, each equally often, **"a single tone was never
  repeated"**.
- **Cascade**: the same 10 tones in ascending or descending order, compared with the matching
  oddball direction.
- In every condition the target tone is played **40 times** in 400 (same overall rate). The tone just
  before a deviant is the same in the oddball and the cascade. Every tone serves as deviant, standard and
  control for the same neuron.
- Pauses of about 30 s between sequences; sequence order randomised.

### Measures and indices (Methods and Results)
- Response = area under the smoothed spike-density curve above baseline, **0-180 ms** after onset
  ("baseline-corrected spike count"). Baseline = mean rate in the **75 ms before onset**. Only the **last
  standard before each deviant** is analysed. Only excitatory responses are analysed.
- **Normalisation**: Euclidean norm per neuron-tone, N = sqrt(DEV² + STD² + CTR²). Each response is
  divided by N, so normalised responses lie in 0-1.
- **iMM = DEV - STD**, **iRS = CTR - STD**, **iPE = DEV - CTR**, all on normalised responses, each in
  [-1, +1], and **iMM = iRS + iPE**. They state iMM is "quantitatively equivalent" to the usual SSA index
  (shown in their Supplementary Fig. 2, not read). A normalised difference of this kind is **not**
  numerically identical to (d - s)/(d + s), so we will report both and say which is which.
- Results with cascade and many-standards controls were "largely comparable"; they report cascade.

### Results (medians, rat, cascade control; Table 1)
| Station | iMM | iRS | iPE |
|---|---|---|---|
| IC lemniscal | 0.14 | 0.22 | -0.08 |
| IC non-lemniscal | 0.49 | 0.46 | 0.03 |
| MGB lemniscal | 0.34 | 0.46 | -0.12 |
| MGB non-lemniscal | 0.52 | 0.46 | 0.06 |
| AC lemniscal | 0.50 | 0.39 | 0.11 |
| AC non-lemniscal | 0.60 | 0.33 | 0.27 |

- Most of the deviant-versus-standard difference in subcortical and lemniscal stations is repetition
  suppression. Prediction error is near zero or negative there and grows toward cortex and toward
  non-lemniscal divisions. They write that "prediction error accounted for around two thirds of the iMM"
  in the strongest condition (this sentence sits next to a subset analysis; check the exact subset before
  quoting).
- Ascending deviants at low intensity show larger iPE.
- A positive iPE is read as predictive activity. The authors also note limitations (not read in full).

### What this means for our model
- **The deviant probability is 10%**, not 20%, and the timing is **isochronous**. Both support the
  matched 10% default and the fixed-interval primary design in `PLAN.md`.
- A purely feedforward adaptation network should give iPE close to 0 (as seen at IC lemniscal) *if* the
  control matches the refractory state. That is a testable reference, not a proven outcome.
- The cell-level iPE here is a population-median effect. It does not show that omission or ABABAA
  responses exist in those neurons. It is evidence about the oddball decomposition only.

## 3. Carbajal & Malmierca (2018), *Trends in Hearing* 22

"The Neuronal Basis of Predictive Coding Along the Auditory Pathway: From the Subcortical Roots to
Cortical Deviance Detection." DOI 10.1177/2331216518784822. File: `docs/papers/carbajal_malmierca2018.pdf` (local only).
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
DOI 10.1016/j.clinph.2011.07.035. File: `docs/papers/ruhnau2012_webpage.rtf` (local only) (a saved web page).

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
auditory cortex." PMC5367837. File: `docs/papers/yarden_nelken2017.pdf` (local only) (received, not yet read).

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

## 11. Random vs regular contexts and uncertainty (search-level only, NOT read; added 2026-10-17)

Provenance: web-search result summaries only. No full text or even full abstract was read, authors are
not all shown, and details below are what the search summaries said. Use as pointers, not as citations,
until each is retrieved and read.
- Deviants in patterned sequences gave larger EEG responses than the same deviants in random sequences, and
  violations in a volatile, random context were considered less surprising
  ([Enhanced deviant responses in patterned relative to random sound sequences](https://sciencedirect.com/science/article/pii/S0010945218302843?via=ihub%3D)).
- A search summary attributes to Garrido, Sahani and Dolan (2013) MEG responses to probe tones that depended
  on the mean and variance of the frequency context (larger in a low-variance context). Unverified.
- Sustained and evoked responses can go in opposite directions: a 2024 MEG study reports a larger sustained
  response for regular sequences and stronger single-tone evoked responses for random ones
  ([J Neurosci 2024](https://www.jneurosci.org/content/44/14/e1894232024)).
- Brain responses to complex acoustic patterns show ideal-observer-like sensitivity
  ([PNAS](https://www.pnas.org/doi/10.1073/pnas.1508523113)). An ideal observer detects a regular-to-random
  change at once but needs time to tell a real pattern from chance in the other direction
  ([PMC2488380](https://pmc.ncbi.nlm.nih.gov/articles/PMC2488380),
  [PMC6672364](https://pmc.ncbi.nlm.nih.gov/articles/PMC6672364)).
- Reduced prediction-error responses in high-uncertainty musical contexts
  ([Cortex](https://www.sciencedirect.com/science/article/abs/pii/S0010945219302412)); a caveat in the same
  summary is that pitch-interval size and low-level adaptation may explain part of it.
- Theory side: predictive-coding accounts say error is scaled by the **precision** of the prediction, so more
  variable contexts give lower precision and smaller mismatch responses; precision and error are hard to
  separate in the MMN ([editorial](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9069060/)). Acetylcholine
  has been reported to raise the gain of prediction-error responses in rat auditory cortex (same search,
  not verified).
- Open issue in this literature: how much is genuine probabilistic prediction and how much is low-level
  adaptation. That is the question this repo asks in miniature.

## 12. What the brain treats as a prediction error (search-level only, NOT read; added 2026-10-17)

Provenance: web-search result summaries. None of these was opened in full. They are pointers, not citations.
- **Error is carried by neurons, in two signs.** Two-photon imaging in mouse posterior parietal cortex
  found separate positive and negative error neurons in layer 2/3 (stronger or weaker than expected
  stimuli); positive error responses grew with stimulus variability while negative ones shrank
  ([PMC12484734](https://pmc.ncbi.nlm.nih.gov/articles/PMC12484734/)). A preprint reports that the two signs
  map onto transcriptionally distinct layer 2/3 cell types, and cautions that a mismatch response alone does
  not prove a neuron is an error-coding cell
  ([bioRxiv](https://www.biorxiv.org/content/10.1101/2022.07.20.500837v1.full)).
- **Canonical proposal:** error in superficial (layer 2/3) pyramidal cells, predictions in deep-layer cells.
  Reviews note the evidence is limited, that error units are hard to identify because the predictions are
  unknown, and that some implementations use one neuron with a separate apical-dendrite compartment holding
  the error instead of separate error neurons
  ([review](https://arxiv.org/pdf/2107.12979)).
- **Circuit implementation (theory):** in an uncertainty-modulated model, layer 2/3 cells represent positive
  or negative error, SST interneurons do the **subtractive** comparison between prediction and input, and PV
  interneurons act **divisively** in a variance-related way
  ([eLife reviewed preprint](https://elifesciences.org/reviewed-preprints/95127v2/reviews)). A 2025 spiking
  model with two-compartment pyramidal cells and PV, SST and VIP interneurons gets sign-specific errors with
  fixed weights ([bioRxiv](https://www.biorxiv.org/content/10.1101/2025.11.01.686040v1.full)).
- **Omission = negative error.** A 2025 PLOS Biology study found rat auditory-cortex neurons that respond to
  omissions in a predictable sequence, growing with evidence ([PMC12212881](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12212881/)),
  and a 2026 mouse study reports omission responses time-locked to the expected onset
  ([DOAJ](https://doaj.org/article/6b3fff0f47fd4ed899cb44f4f9aae85e)). In rats they are reported largely absent
  under anaesthesia ([ELSC summary](https://elsc.huji.ac.il/research-and-facilities/publications/paper-of-the-month/paper-of-the-month-august-2023-nelkens-lab)),
  which matters for the anaesthetised Parras recordings.
- A 2025 preprint, the "Duet" model, uses both positive and negative error neurons and reports that oddball
  deviance detection depends on both ([bioRxiv](https://www.biorxiv.org/content/10.1101/2025.07.12.664417.full.pdf));
  a review of omission models is [PMC8844463](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8844463/).
Summary: the brain does not compute a probability difference; error appears as the **firing of specific
neurons that carry a signed difference between predicted and actual activity**, scaled by uncertainty.

## 13. Novelty check, first pass (search-level only; added 2026-10-17)

One or two searches per idea. **Not finding something in a search is not evidence that it does not exist.**
- **"Surprise increases plasticity" already exists.** Barry & Gerstner (PLOS Comput Biol, 2024 per the
  search summary) present a spiking network in which a mismatch-derived surprise signal gates a three-factor
  learning rule and raises plasticity after surprise
  ([PMC10906910](https://pmc.ncbi.nlm.nih.gov/articles/PMC10906910)); Faraji, Preuschoff & Gerstner (2014) set
  learning rates from surprise and uncertainty
  ([PMC4125082](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4125082/)); Yu & Dayan (NeurIPS 2002) link
  norepinephrine to unexpected uncertainty and learning-rate changes
  ([paper](https://papers.neurips.cc/paper_files/paper/2002/file/758a06618c69880a6cee5314ee42d52f-Paper.pdf)).
  So the "high-plasticity state after a mismatch" part of A2/A2b has precedent. Whatever is new has to be
  in the specifics: the many-candidate sequence hypotheses, and their use for the oddball, omission and
  post-oddball tone.
- **Post-deviant tone:** no direct hit. Related, and about the *deviant's own* response, not the tone after
  it: a study in awake freely moving rats reports deviant responses larger than control-condition responses
  ([PMC5991388](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5991388/)); the same search also summarised a
  mouse whole-cell study (source link not shown in the result) with a late component 200-400 ms after the tone
  linked to deviance detection and MMN, and a proposed two-phase activation (adapted circuit reactivated,
  then delayed reverberating activity). The field is divided on how much is true deviance detection vs
  adaptation.
- **Multi-candidate spiking model:** no exact match. Nearest: Wacongne 2012 and the Duet model above.
- **Timing and omission:** omission responses are time-locked to the expected onset, but no search hit tested
  jittered timing directly.
- **Ideal-observer comparison, precision and uncertainty:** exists (entry 11).
Net: the building blocks are published; a specific combination may still be new. Verify with deeper searches
before writing "novel".

## 14. How concepts are represented: distributed ensembles, sparse cells, overlap (search-level only; added 2026-10-17)

Provenance: search summaries only, not opened in full. The owner also supplied a pasted explanation of population
coding (links to a course page, a Medium post, a YouTube video and an MIT news item); those are **not** used as
sources here. The pasted text says there are "two primary theories" but only describes the first.
- **Both a distributed and a sparse picture have support.** Sparse, selective responses are reported in human
  medial temporal lobe neurons, with the debate being whether they are single "concept" cells or a sparse
  population code. A two-population model fits MTL data better than a single sparsity level, with a large majority of
  neurons almost silent ([arXiv:1411.3917](https://arxiv.org/pdf/1411.3917),
  [arXiv:1508.04241](https://ar5iv.arxiv.org/html/1508.04241)). A 7T fMRI thesis reports evidence for distributed
  category representations ([Radboud thesis](https://theses.ubn.ru.nl/bitstreams/c919bbb0-b10b-4971-8952-a4f25fbc38b5/download));
  the retrieved text was truncated. A cited caveat: the specificity of a neuron for a stimulus can never be proven
  ([Reddy & Kanwisher](https://web-mit-edu.ezproxyberklee.flo.org/bcs/nklab/media/pdfs/Reddy.kanwisher.CON2006.pdf)).
- **Linking by overlap.** A 2024 Nature Reviews Neuroscience review (per the summary) says memories formed close in
  time recruit partly the same neurons, which links them while they stay separable, via different dendritic and
  synaptic allocation ([engram linking review](https://read.qxmd.com/read/38664582/engram-mechanisms-of-memory-linking-and-identity)).
  A recurrent-network model (Delamare, Tome, Clopath) reports overlaps in hippocampus and amygdala support
  linking, with inhibition driving competition for allocation
  ([paper](https://research-explorer.ista.ac.at/download/17092/17095/2024_JourNeuroscience_Delamare.pdf)).
- **Too much overlap merges memories.** A review of shared concept cells and a FENS abstract on attractor models
  say overlap supports associative recall only within a critical range; beyond it memories become inseparable
  ([FENS abstract, not peer-reviewed](https://world-wide.org/fens-26/dynamic-attractor-model-overlapping-45c5d27d)).
Relevance: overlap-based "leakage" between linked memories (`THEORY_NOTES.md` sections 11-12) is an established kind
of mechanism; what is untested here is its interaction with adaptation and surprise.

## Summary table: which tests is adaptation alone said to fail?

| Test | Who frames it as beyond adaptation | Level | Our expectation for a feedforward adaptation-only net |
|---|---|---|---|
| Deviant > standard (oddball) | Not claimed to fail: May & Tiitinen, Mill et al. and Yarden & Nelken all produce SSA from adaptation | ABSTRACT | Pass |
| Deviant > cascade control (iPE > 0) | Parras 2017: median iPE about 0 or negative in lemniscal IC and MGB, positive in cortex (0.11 lemniscal, 0.27 non-lemniscal) | FULL | Unclear. To be measured, not assumed. |
| Omission response | Wacongne 2012 (model produces it from learned *predictive* currents, not from error). Eissa 2025 (needs rhythmic input). The claim that adaptation fails here is our own logical point, not stated in Wacongne 2012. | FULL / ABSTRACT | No input, so no evoked response. Null expected. |
| Unexpected repeat in ABAB…AA | Wacongne 2012 (model produces it; paper says habituation predicts a *smaller* response; May & Tiitinen rescue it with higher-order pair-habituating neurons) | FULL | Expected fail. A feedforward adaptation net should respond *less* to the repeated A. |
| Global context (local–global) | Wacongne 2012: its own model is **blind** to global regularities, as in Bekinschtein 2009 (AAAAB). Not a failure of adaptation. | FULL | Out of scope for Experiment 2 as specified. Noted only. |

## Not included, and why

- Anything I remembered but could not find in a retrieved source (e.g.
  specific parameter values of the Wacongne model, Parras's SOA, deviant
  probability and normalisation formula). Left out on purpose.
- The Garagnani, Lieder et al. and Schröger & Wolff original papers:
  mentioned only in passing in search results. Not retrieved, so left out.

## Uploaded files that were removed

Three uploaded PDFs unrelated to this project (an amygdala-cortex fear-memory preprint, "The Dragon
Hatchling", and an ecosystems paper) were deleted from the repo at the owner's request. They were
never used or cited. The relevant papers are kept locally in `docs/papers/`, which is git-ignored.
Note: the PDFs remain in the git history of commit `5700556` on branch `step0-prior-art`.

## What I need to finish Step 0 properly (superseded, see top; kept for the record)

1. Either allow these hosts in the environment's network settings
   (`www.jneurosci.org`, `www.unicog.org`, `pmc.ncbi.nlm.nih.gov`,
   `www.ncbi.nlm.nih.gov`, `hal.science`, `www.nature.com`,
   `www.biorxiv.org`, `journals.plos.org`), or put the PDFs in `docs/papers/`
   (not committed to the public repo if licensing is unclear).
2. Then I will read the Wacongne 2012 Methods and Parras 2017 Methods in full
   and promote entries 1–2 to FULL. **Mechanism B cannot be implemented
   honestly from abstract-level information.**
