# Novelty check for Mechanism A (deeper pass, 2026-11-01)

Deepens `docs/PRIOR_ART.md` section 13. Produced by an automated literature search (about 30 web searches).

## Read this first: what the verification levels mean here

- **FULL**: full text read. **ABSTRACT**: abstract or bibliographic record seen on a publisher, PubMed, PMC or
  arXiv page. **SEARCH**: seen only in a web-search result summary.
- **Every source below is SEARCH level.** Fetching pages was impossible in this session: `pmc.ncbi.nlm.nih.gov`,
  `pubmed.ncbi.nlm.nih.gov`, `papers.nips.cc`, `proceedings.neurips.cc` and `doaj.org` all failed DNS resolution
  through the network proxy. To get ABSTRACT or FULL level, those hosts have to be allowed in the session's network
  settings. No page was opened, so no level has been upgraded.
- Bibliographic details (volume, pages, DOI) were cross-checked by running separate searches whenever possible. Where
  sources disagreed, the conflict is reported and not resolved from memory.
- **Not finding something is not evidence that it does not exist.** This was about 30 searches, not a systematic
  review. Query lists are given so the gaps can be re-searched.

**Update 2026-11-02.** The references used in the paper were re-checked with site-restricted searches of the publishers'
own pages (PLOS, MIT Press, Springer, Wiley, J Neurosci, ScienceDirect, NeurIPS). Titles, authors, volumes and DOIs match
the entries in `paper/paper.md`, which now marks them \[P\]. Yu & Dayan (2002): the paper's own PDF lists **Yu first**;
the NeurIPS index page lists Dayan first; the paper cites it as on the PDF. Publisher pages still cannot be opened
directly from this environment.

## 1. Verdict

**Clear precedent exists for:**
- **(i) surprise-gated learning rate**, the gate's first function. Normative and Bayesian versions include Dayan & Yu
  (NIPS 2002), Faraji, Preuschoff & Gerstner (2014 poster; 2018 *Neural Computation*), Liakoni et al. (2021
  *Neural Computation*), and hierarchical-Gaussian-filter and Bayesian models of the MMN (Lieder et al. 2013). In a
  **spiking network**, Barry & Gerstner (2024, *PLoS Comput Biol*) use a three-factor rule gated by a surprise signal
  taken from an excitation-inhibition imbalance. They explicitly relate that signal to the MMN, but they test rule
  switching, not oddball or omission paradigms.
- **Multiple simultaneous predictions** in sequence networks: Hawkins & Ahmad (2016), and its spiking implementation
  by Bouhadjar et al. (2022). There are also **competing candidate interpretations of a sound sequence** in which
  wrong predictors are discarded (the CHAINS model: Mill et al. 2013; Schröger et al. 2014). Particle-filter and
  change-point learners (Liakoni et al. 2021) likewise keep several hypotheses and reweight them after surprise.
- **Spiking or network models that produce omission responses and the unexpected-repeat (ABAB→AA) MMN**: besides
  Wacongne 2012, Chien, Maess & Knösche (2019), Eissa et al. (2025/2026), the Duet model (Meng et al. 2025) and
  Asabuki, Gillon & Clopath (2025) all cover parts of this (details in section 5).

**No precedent found in this search for:**
- **(ii) post-surprise sensory gain**: a gate that raises sensory input gain so the tone after a deviant gets a
  larger response. The empirical picture is mixed and mostly negative at the ERP level. Rosburg & Mager (2021) found
  no N1 enhancement for standards after deviants, and Coy et al. (2024) found no MMN-like effect for standards after
  deviants. The one positive hit is that the first standard after a deviant was "slightly larger" in intracellular
  recordings (Hershenhoren et al. 2014), and a recurrent model attributes this to resource recovery, i.e.
  adaptation (Yarden & Nelken 2017). So an amplified post-deviant tone **is not an established empirical effect**,
  and the paper should not present it as one.
- **(iii) a surprise opening specific, structured candidate predictions** ("the erring tone repeats", "the earlier
  tone returns", "something new") in a spiking oddball/MMN model.
- **The combination of (i), (ii) and (iii) in one model** tested on oddball, unexpected-repeat and omission
  paradigms. Nearest neighbours: Barry & Gerstner 2024 has (i) in spikes but no oddball or omission tests;
  Wacongne 2012 has the paradigms but no gate.

**Omission versus timing jitter.** This is reported in a 2026 review (Yaron et al., *Eur J Neurosci*), and
possibly in Peters et al. (2026, *Nat Commun*); both are SEARCH level. Andreou, Griffiths & Chait (2015) show
weaker timing-pattern learning for non-isochronous sequences. A model *result* that omission responses shrink with
jitter is therefore a reproduction of a reported empirical trend, not a new prediction.

**Recommended wording for the paper:**
> "Surprise-modulated learning rates are well established (Dayan & Yu, 2002; Faraji et al., 2018; Liakoni et al.,
> 2021), including in a spiking network with a three-factor rule (Barry & Gerstner, 2024), and multiple simultaneous
> sequence predictions have been modelled before (Hawkins & Ahmad, 2016; Bouhadjar et al., 2022; Mill et al., 2013).
> To our search (about 30 queries, not a systematic review), a spiking model in which a single mismatch gate jointly
> boosts plasticity, raises sensory gain and opens several candidate predictions has not been tested on oddball,
> unexpected-repetition and omission paradigms. We present this combination, not its parts, as the contribution."

Do **not** claim novelty for the surprise-gated learning rate, the omission-jitter dependence, or "multiple
hypotheses" in general. Do not describe post-deviant sensitisation as a known neural phenomenon; describe it as a
model prediction that ERP data so far do not clearly support.

## 2. Findings by question

### Q1. Surprise or mismatch-gated plasticity (learning-rate boost after surprise)

- **Barry, M. L. L. R. & Gerstner, W. (2024).** Fast adaptation to rule switching using neuronal surprise.
  *PLoS Comput Biol* 20(2): e1011839. doi:10.1371/journal.pcbi.1011839; PMC10906910; PMID 38377112; bioRxiv
  preprint 10.1101/2022.09.13.507727. **SEARCH.** A self-supervised spiking network (SpikeSuM). Surprise is
  extracted from an increase in activity after an excitation-inhibition imbalance, and it gates a three-factor
  rule that raises plasticity at surprising moments. A multi-module version resists overwriting old rules. The
  authors relate the signal to the MMN, but the tasks are rule switching, not oddball or omission. This is the
  **closest precedent for gate function (i)**.
- **Faraji, M. J., Preuschoff, K. & Gerstner, W. (2014).** Neuromodulation by surprise: a biologically plausible
  model of the learning rate dynamics. *BMC Neuroscience* 15(Suppl 1): P159. doi:10.1186/1471-2202-15-S1-P159;
  PMC4125082. **SEARCH.** **This is a conference poster abstract (CNS 2014), not a full paper.** It proposes
  learning-rate dynamics driven by surprise and uncertainty, tested on reversal, dynamic decision-making and dynamic
  clustering tasks.
- **Faraji, M. J., Preuschoff, K. & Gerstner, W. (2018).** Balancing new against old information: the role of
  puzzlement surprise in learning. *Neural Computation* 30(1): 34–83. doi:10.1162/NECO_a_01025; arXiv:1606.05642
  (preprint title "…the role of surprise in learning"). **SEARCH.** The full paper behind the poster. It defines a
  surprise measure (likelihood plus belief entropy) and the SMiLe rule, which adjusts the balance between new and
  old information. **Cite this rather than, or as well as, the 2014 poster.**
- **Dayan, P. & Yu, A. J. (2002/2003).** Expected and unexpected uncertainty: ACh and NE in the neocortex.
  *Advances in Neural Information Processing Systems 15*, pp. 173–180. **SEARCH.** Proposes that NE signals
  unexpected uncertainty, meaning bottom-up input diverging sharply from top-down interpretations, and that this
  influences inference and plasticity. See section 3 for the author-order conflict.
- **Liakoni, Modirshanechi, Gerstner & Brea (2021).** Learning in volatile environments with the
  Bayes factor surprise. *Neural Computation* 33(2): 269–340. arXiv:1907.02936. **SEARCH.** Surprise modulates the
  rate of adaptation, and one of the derived algorithms is a particle filter. Also relevant to Q3.
- **Lieder, Daunizeau, Garrido, Friston & Stephan (2013).** Modelling trial-by-trial
  changes in the mismatch negativity. *PLoS Comput Biol* 9(2): e1002911. PMC3578779. **SEARCH.** Bayesian and
  free-energy learning models explained single-trial MMN better than change-detection or adaptation models (roving
  oddball, 8 participants).
- **Charlton et al. (2025)**, *Imaging Neuroscience* (UCL Discovery eprint 10205184; first author's initials and
  co-authors not seen). **SEARCH.** Fits a hierarchical Gaussian filter to EEG in an oddball task with stable and
  volatile phases; the MMN was smaller in volatile phases. In the HGF, the precision ratio acts as a trial-by-trial
  learning rate.

Queries (Q1): "Barry Gerstner 2024 PLoS Computational Biology surprise three-factor learning spiking network";
"surprise-gated plasticity and gain modulation spiking network oddball omission mismatch negativity model learning
rate boost after deviant"; "model oddball one-shot or rapid learning after surprise … roving paradigm neural model";
plus the bibliographic queries in section 3. **No hit** for a spiking model that boosts the learning rate after a
deviant *in an oddball or omission paradigm*.

### Q2. Post-surprise sensitisation (the tone after a deviant)

- **Hershenhoren, I., Taaseh, N., Antunes, F. M. & Nelken, I. (2014).** Intracellular correlates of
  stimulus-specific adaptation. *J Neurosci* 34(9): 3303–3319. doi:10.1523/JNEUROSCI.2166-13.2014. **SEARCH.**
  According to the search summary, the response to the first standard after a deviant was "slightly larger" than to
  the next few standards (rat A1, intracellular). A small effect.
- **Yarden, T. S. & Nelken, I. (2017).** *PLoS Comput Biol* 13(3): e1005437 (already cited). **SEARCH** for this
  point. In their model, resources in the standard column are higher after a deviant, which can allow a population
  spike to the next standard. This is an **adaptation-recovery** explanation of a post-deviant boost, so it is a
  competing account for the post-deviant effect in A.
- **Rosburg & Mager (2021).** *Hearing Research* 400: 108140 (title not seen). **SEARCH.** There was no N1
  difference between standards after small deviants and standards after standards, only a small late MMN-like
  response. Favours the refractoriness account over dishabituation. Follow-up: Rosburg, Weigl & Mager (2022),
  *Int J Psychophysiol* 174, found no N1 dishabituation after novel sounds (**SEARCH**).
- **Coy, N., Bendixen, A., Grimm, S., Roeber, U. & Schröger, E. (2024).** Conditional deviant repetition in the
  oddball paradigm modulates processing at the level of P3a but not MMN. *Psychophysiology* 61(6): e14545.
  doi:10.1111/psyp.14545. **SEARCH.** Found no MMN-like activity for standards after deviants when the repetition
  rule was broken versus followed. It notes that the post-deviant standards usually excluded from analysis can show
  MMN-like responses from differential adaptation.
- **Gain modulation by neuromodulators** (search summary of a dopamine/inferior colliculus study, rat): dopamine
  *reduced* responses to unexpected input. **SEARCH**, authors not seen; listed only to show that this search found
  no evidence for surprise-*raised* sensory gain.

Queries (Q2): "post-deviant standard enhanced response after deviant oddball 'first standard after deviant' MMN";
"stimulus-specific adaptation response to standard immediately following deviant enhanced single neurons auditory
cortex"; "enhanced N1 … standard tone following deviant post-deviant sensitization EEG oddball rebound"; "Hearing
Research 2021 N1 standards after small deviants dishabituation"; "surprise increases sensory gain after prediction
error neuromodulation norepinephrine … auditory". **No hit** for a model in which surprise raises sensory gain
to produce a larger post-deviant response.

### Q3. Several simultaneous candidate hypotheses opened by surprise

- **Hawkins & Ahmad (2016).** Why neurons have thousands of synapses, a theory of sequence memory in
  neocortex. *Front Neural Circuits* 10: 23. doi:10.3389/fncir.2016.00023; arXiv:1511.00083. **SEARCH.** In this
  sequence-memory network, dendritic pattern matches depolarise cells as predictions, and the network makes
  "multiple simultaneous predictions" for ambiguous input. The predictions are not opened by surprise, but the
  general idea of several predictions held at once is precedented.
- **Bouhadjar, Wouters, Diesmann & Tetzlaff (2022).** Sequence learning, prediction, and replay in
  networks of spiking neurons. *PLoS Comput Biol* (June 2022). PMC9273101; arXiv:2111.03456. **SEARCH.** A spiking,
  continuous-time version of HTM temporal memory with sequence prediction and **mismatch detection**. The companion
  paper "Coherent noise enables probabilistic sequence replay in spiking neuronal networks" (2022; venue not seen)
  handles ambiguous cues. The closest spiking precedent for holding several next-element candidates.
- **Mill, R. W., Bőhm, T. M., Bendixen, A., Winkler, I. & Denham, S. L. (2013).** Modelling the emergence and
  dynamics of perceptual organisation in auditory streaming. *PLoS Comput Biol* 9(3): e1002925. **SEARCH.** The
  CHAINS model: competing predictors of a sound sequence, where a chain that makes a wrong prediction fails and
  several incompatible organisations coexist. Conceptually close to "candidate predictions", applied to auditory
  streaming rather than the MMN. Related: Schröger, Bendixen, Denham, Mill, Bőhm & Winkler (2014), *Brain
  Topography* 27, "Predictive regularity representations in violation detection…" (**SEARCH**, title incomplete).
- **Liakoni et al. (2021)** (Q1): a particle filter keeps several weighted hypotheses, with surprise-controlled
  reweighting. Normative, not spiking.
- **Maheu, M., Dehaene, S. & Meyniel, F. (2019).** Brain signatures of a multiscale process of sequence learning in
  humans. *eLife* 8: e41541. PMC6361584. **SEARCH.** MEG responses were modelled as surprise under several learning
  models: early waves tracked item frequency (linked to habituation), later waves tracked recent transition
  probabilities. Relevant as an ideal-observer benchmark, not as a multiple-hypothesis model.

Queries (Q3): "neural network model surprise opens multiple competing hypotheses next sequence element oddball
mismatch negativity spiking"; "Bayesian observer oddball sequences change-point volatility learning rate mismatch
negativity hierarchical Gaussian filter model"; "Maheu Dehaene Meyniel 2019 …"; "CHAINS model competing
interpretations…"; "Bouhadjar … multiple predictions ambiguous"; "Hawkins Ahmad 2016 … multiple simultaneous
predictions". **No hit** for a spiking oddball/MMN model in which a mismatch *opens* specific, structured candidates
(repeat-the-erring-tone, return-of-earlier-tone, something-new).

### Q4. Omission responses and timing jitter

- **Yaron et al. (2026).** "Nothing" really matters: what omission responses reveal about the predictive brain.
  *Eur J Neurosci*. doi:10.1111/ejn.70566 (DOI taken from the Wiley URL; co-authors not seen; two searches for the
  bibliographic record failed). **SEARCH.** The search summary attributes to this review the statement that
  "jittering stimulus timing while preserving average rate dramatically reduces omission signals", and that the
  omission paradigm needs a "when" prediction to reveal what was expected. **The most direct hit for Q4**, but it is
  a review: the primary studies behind the statement were not identified.
- **Peters, J., Cai, Z., van Veghel, M., Knoben, A., Simon, M., Arends, S., Battaglia, F. P. & Englitz, B. (2026).**
  The representation of omitted sounds in the mouse auditory cortex. *Nat Commun* 17: 2107.
  doi:10.1038/s41467-026-68847-w; PMID 41605943. **SEARCH.** Omission responses were time-locked to the expected
  onset, located in layers 1–4 of the temporal association area, and kept rising until the next stimulus. A search
  snippet from the article PDF says omission-response size was "sensitive to the regularity of the sequence on the
  level of the temporal spacing", with a reduction rather than loss expected. **It is unclear from the snippet
  whether this is the paper's own manipulation or a cited result. Check before citing it for jitter.** Author lists
  differ slightly between records.
- **Andreou, Griffiths & Chait (2015).** Sensitivity to the temporal structure of rapid sound
  sequences – an MEG study. *NeuroImage* 110: 194–204. doi:10.1016/j.neuroimage.2015.01.052; PMC4389832.
  **SEARCH** (author initials not seen in results). Measured offset responses as the first
  missing expected tone. Offset latencies were much longer for non-isochronous regular sequences than for
  isochronous ones, i.e. timing was learned worse, and timing was not learned precisely when ignored. The nearest
  primary evidence on timing regularity and the detection of a missing tone.
- **SanMiguel et al. (2013).** "I know what is missing here: electrophysiological prediction error signals
  elicited by omissions of predicted 'what' but not 'when'." PMC3725431; PMID 23908618 (venue not seen). **SEARCH.**
  Omissions produced a response only when sound identity was predictable. No marker of a purely temporal violation
  was found.
- Counter-evidence noted by the search summary: an older loudness-summation study found an omission MMN with random
  SOA (PMID 16629681). **SEARCH**, details not seen. So "jitter abolishes omission responses" is too strong; "jitter
  reduces them" is the defensible statement.

Queries (Q4): "omission response temporal jitter predictability reduced omission MMN irregular stimulus onset
asynchrony"; "omission responses temporally jittered sequences MEG EEG 'temporal jitter'…"; "omission evoked
response isochronous versus jittered sequences 'when' prediction 'what' prediction"; plus the Peters and Yaron
bibliographic queries. **No hit** for a *spiking model* that varies jitter and reports the omission response.

### Q5. Models producing the unexpected-repeat (ABAB→AA) and omission responses, other than Wacongne 2012

- **Chien, V. S. C., Maess, B. & Knösche, T. R. (2019).** A generic deviance detection principle for cortical On/Off
  responses, omission response, and mismatch negativity. *Biol Cybern* 113(5–6): 475–494.
  doi:10.1007/s00422-019-00804-x; PMC6848254; bioRxiv 10.1101/582437. **SEARCH.** Reciprocally coupled neural masses
  act as a change detector and reproduce On/Off responses, the omission response and the MMN. A rate (neural-mass)
  model; an alternation-repeat test was not seen in the summary.
- **Eissa et al. (2025 preprint; *Eur J Neurosci* 2026, doi:10.1111/ejn.70453; PMC12621899/PMC13004757).** Already
  in PRIOR_ART section 9. **SEARCH** here. An integrate-and-fire model of frequency, omission, duration and
  inverse-duration deviants, with schizophrenia-related manipulations.
- **Meng, J. H., Ross, J. M., Hamm, J. P. & Wang, X.-J. (2025).** Duet model unifies diverse neuroscience experimental
  findings on predictive coding. bioRxiv 10.1101/2025.07.12.664417 (preprint). **SEARCH.** A model with positive and
  negative prediction-error neurons, focused on omission. It predicts negative-error neurons in the oddball
  paradigm and reports confirming them in data. Closest to A's two-sign error populations.
- **Asabuki, T., Gillon, C. J. & Clopath, C. (2025).** Learning predictive signals within a local recurrent circuit.
  *PNAS* 122(27): e2414674122. doi:10.1073/pnas.2414674122; PMID 40591603. **SEARCH.** A recurrent spiking network
  with local plasticity learns predictive and mismatch signals; framed with oddball/MMN. Omission coverage was not
  confirmed.
- **van Driel, K., Rudelt, L., Priesemann, V. & Mikulasch, F. A. (2023).** Prediction mismatch responses arise as
  corrections of a predictive spiking code. bioRxiv 10.1101/2023.11.16.567335 (preprint). **SEARCH.** Mismatch
  responses emerge in an efficient spiking code in which spikes predict the upcoming input. An alternative account
  with no separate error units.
- Already cited: Mill, Coath, Wennekers & Denham (2011) and Yarden & Nelken (2017), both adaptation-based.

Queries (Q5): "spiking network model mismatch negativity omission unexpected repetition predictive coding (not
Wacongne) local global paradigm model"; "computational model reproduces omission response and alternation deviance
(ABAB repetition) mismatch negativity network model 2018-2025"; plus bibliographic queries. **No hit** for a
post-2012 spiking model shown to reproduce the ABAB→AA repetition MMN; this search may have missed one.

### Q6. Anything combining (1)+(2)+(3) for oddball, MMN or omission

**Nothing found.** The nearest works each have one or two parts:

| Work | (i) surprise-gated learning | (ii) post-surprise gain | (iii) candidate predictions | oddball / omission tests | spiking |
|---|---|---|---|---|---|
| Wacongne et al. 2012 | no (STDP-like learning, no gate) | no | no | yes / yes (incl. ABAB→AA) | yes |
| Barry & Gerstner 2024 | **yes** | no | no (multi-module memory) | no (rule switching; MMN discussed) | yes |
| Liakoni et al. 2021 | **yes** | no | **yes** (particle filter) | no | no |
| Lieder et al. 2013; HGF work | **yes** (Bayesian) | no | no | MMN data | no |
| Hawkins & Ahmad 2016; Bouhadjar et al. 2022 | no | no | **yes** (not surprise-opened) | mismatch detection, no MMN tests | Bouhadjar: yes |
| Mill et al. 2013 (CHAINS) | no | no | **yes** (competing predictors) | streaming, not MMN | no |
| Duet (Meng et al. 2025) | not seen | not seen | no | omission focus | not seen |

Queries (Q6): "surprise-gated plasticity and gain modulation spiking network oddball omission mismatch negativity
model learning rate boost after deviant" (extended); "neural network model surprise opens multiple competing
hypotheses…" (extended). Table cells are from search summaries only. "not seen" means the summary did not say.

## 3. Completed references (the three marked "to be completed")

All **SEARCH** level; consistent across several independent index records found by search, but no page was opened.

1. **Barry, M. L. L. R., & Gerstner, W. (2024).** Fast adaptation to rule switching using neuronal surprise.
   *PLoS Computational Biology*, 20(2), e1011839. https://doi.org/10.1371/journal.pcbi.1011839 (PMC10906910;
   PMID 38377112). Published February 2024. Conflict: one EPFL Infoscience record lists Abigail Morrison as an
   author, but PMC, DOAJ and MEDLINE records list only Barry and Gerstner, and a search summary gives Morrison as the
   **editor**. Use Barry & Gerstner.
2. **Faraji, M. J., Preuschoff, K., & Gerstner, W. (2014).** Neuromodulation by surprise: a biologically plausible
   model of the learning rate dynamics. *BMC Neuroscience*, 15(Suppl 1), P159.
   https://doi.org/10.1186/1471-2202-15-S1-P159 (PMC4125082). **This is a poster abstract.** Add or substitute
   the full paper: **Faraji, M. J., Preuschoff, K., & Gerstner, W. (2018).** Balancing new against old
   information: the role of puzzlement surprise in learning. *Neural Computation*, 30(1), 34–83.
   https://doi.org/10.1162/NECO_a_01025. (The paper's current "Faraji, M." should become "Faraji, M. J.", per the
   search records.)
3. **Expected and unexpected uncertainty: ACh and NE in the neocortex.** In S. Becker, S. Thrun & K. Obermayer
   (Eds.), *Advances in Neural Information Processing Systems 15* (pp. 173–180). MIT Press. Conference 2002; the
   MIT Press volume is dated 2003 in some indexes. Authors: **Angela J. Yu and Peter Dayan, order unresolved.** Two
   search summaries say the official NeurIPS listing puts **Dayan first**, and the mlanthology slug is
   "dayan2002neurips-expected". Another repository record lists Yu first. The pages (173–180) come from the NeurIPS
   metadata as quoted in a search summary. The editors (Becker, Thrun, Obermayer) were *not* confirmed by any
   result. **Before citing, open the PDF or `…-Metadata.json` at proceedings.neurips.cc to fix the author order and
   the editors.** If it is Dayan first, the in-text citation should be "Dayan & Yu (2002)".

## 4. Most important new citations to add (all SEARCH level)

- Faraji, M. J., Preuschoff, K., & Gerstner, W. (2018). Balancing new against old information: the role of
  puzzlement surprise in learning. *Neural Computation*, 30(1), 34–83. doi:10.1162/NECO_a_01025 \[SEARCH\]
- Liakoni, Modirshanechi, Gerstner, & Brea (2021). Learning in volatile environments with the Bayes
  factor surprise. *Neural Computation*, 33(2), 269–340. (arXiv:1907.02936) \[SEARCH\]
- Lieder, Daunizeau, Garrido, Friston, & Stephan (2013). Modelling trial-by-trial
  changes in the mismatch negativity. *PLoS Computational Biology*, 9(2), e1002911. \[SEARCH\]
- Bouhadjar, Wouters, Diesmann, & Tetzlaff (2022). Sequence learning, prediction, and replay in
  networks of spiking neurons. *PLoS Computational Biology* (2022; volume and article number not seen; PMC9273101).
  \[SEARCH\]
- Mill, R. W., Bőhm, T. M., Bendixen, A., Winkler, I., & Denham, S. L. (2013). Modelling the emergence and dynamics of
  perceptual organisation in auditory streaming. *PLoS Computational Biology*, 9(3), e1002925. \[SEARCH\]
- Chien, V. S. C., Maess, B., & Knösche, T. R. (2019). A generic deviance detection principle for cortical On/Off
  responses, omission response, and mismatch negativity. *Biological Cybernetics*, 113(5–6), 475–494.
  doi:10.1007/s00422-019-00804-x \[SEARCH\]
- Coy, N., Bendixen, A., Grimm, S., Roeber, U., & Schröger, E. (2024). Conditional deviant repetition in the oddball
  paradigm modulates processing at the level of P3a but not MMN. *Psychophysiology*, 61(6), e14545.
  doi:10.1111/psyp.14545 \[SEARCH\]; together with Hershenhoren, I., Taaseh, N., Antunes, F. M., & Nelken, I. (2014).
  Intracellular correlates of stimulus-specific adaptation. *Journal of Neuroscience*, 34(9), 3303–3319.
  doi:10.1523/JNEUROSCI.2166-13.2014 \[SEARCH\]. These are for the post-deviant discussion.
- Andreou, Griffiths, & Chait (2015). Sensitivity to the temporal structure of rapid sound
  sequences – an MEG study. *NeuroImage*, 110, 194–204. doi:10.1016/j.neuroimage.2015.01.052 \[SEARCH; author initials not seen\]. For the timing-jitter result. Add Yaron et al. (2026, *Eur J Neurosci*,
  doi:10.1111/ejn.70566) only after its author list is retrieved.

Also worth considering: Meng, Ross, Hamm & Wang (2025, bioRxiv, Duet model) and Asabuki, Gillon & Clopath (2025,
*PNAS* 122(27): e2414674122), both on positive and negative error and spiking mismatch learning; Hawkins & Ahmad
(2016, *Front Neural Circuits* 10:23).

*Note on author names: initials are given only where a search result showed them (Barry, Faraji, Coy et al.,
Hershenhoren et al., Chien et al., Mill et al. 2013, Meng et al., Asabuki et al., van Driel et al., Peters et al.).
For the others, surnames only were confirmed; add initials from the publisher page before submission.*
