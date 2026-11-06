# SANS triage prototype (v0.1)

Synthetic astronaut cohort + rule-based SANS triage for the OSDR AI/ML AWG CDSS subgroup.
Synthetic data only. Not clinical guidance.

**What it does**
1. Makes 2,000 synthetic astronauts calibrated to published ISS SANS cohorts.
2. Simulates in-flight eye exams (FD10–R−30) with OCT and refraction noise.
3. Triages each exam into Tier 0–3 using NASA's SANS categories, with the reason for each tier.
4. Checks realism against the literature, tests noise and threshold sensitivity.
5. Exports blinded vignettes for clinician grading (Cohen's kappa).

**Run**
```bash
pip install -r requirements.txt
jupyter notebook notebooks/01_sans_triage_demo.ipynb
```
Or Colab: upload `notebooks/SANS_triage_prototype_colab.ipynb` → Run all.

**Files**
```
sans_cdss/parameters.py   every number + source + kind (reported / derived / assumption)
sans_cdss/generator.py    synthetic astronauts and exams
sans_cdss/triage.py       tier rules
sans_cdss/evaluate.py     checks
sans_cdss/vignettes.py    clinician packet
docs/                     variable list, pipeline + tier diagram, limitations
outputs/                  data, figures, provenance table
```

**Results (n = 2,000, seed 0)**
* Tiers: 18% / 43% / 36% / 3% (Tier 0 / 1 / 2 / 3).
* Prevalences within ~1 point of published (tuned).
* FD30 vs FD150 ΔTRT correlation 0.90 vs 0.89 published (Carter 2026, not tuned).
* ~15% of exams change tier on re-measurement, mostly near 20 µm.

**Main limitations:** small source cohorts, 23/55 parameters assumed, in-flight only, one eye. See `docs/PIPELINE.md`.

**Key sources:** Brunstetter 2023 (NASA HRP IWS); Gew 2026 (*Eye*); Carter 2026, Macias 2020, Pardon 2022, Ferguson 2023 (*JAMA Ophthalmol*); Valencia 2023; Greenwald 2021; Mader 2011; Zwart 2019; Brunstetter 2024.

Vishnu Avanthsa · code drafted with AI assistance, checked against the papers.
