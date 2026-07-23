# PROJECT CHARTER

# BirdSense: Migration Timing of Wintering Waterbirds in Gujarat

Version 2.0 — Independent Research Edition

## What this document is

This is the top-level definition of the project. Every other document
in this set exists to support this one. If anything elsewhere conflicts
with this document, this document wins.

This supersedes the original `BirdSense_AI_Engineering_Charter.txt` and
`BirdSense_Master_Project_Definition.docx`, which described a
production-grade research-platform build (PostgreSQL+PostGIS, FastAPI,
Next.js, Docker, formal multi-level validation). That version was scoped
for a professional engineering team over months. **This version is
scoped for one independent researcher, with mentor support and
AI-assisted coding.**

---

## Who this is for

An experienced Gujarat eBirder conducting an independent research
project, motivated by firsthand field observations that the city is
expanding and local weather patterns are shifting, and a wish to check
whether those changes actually show up in the region's long-term bird
migration data. The project is:

- Built with AI-assisted coding (Claude), under the researcher's own
  research direction and with mentor support from data-science and
  analytics mentors.
- Owned scientifically by the researcher: research question, hypotheses,
  species selection, and interpretation of results are the researcher's
  own decisions, informed by their personal field expertise as an active
  eBirder in Gujarat.
- Honestly documented: any public repository or write-up should disclose
  AI-assisted implementation and mentor guidance. See
  `12_AI_AND_MENTOR_DISCLOSURE.md`.

---

## Research Question

> Have migration timing and spatial distribution of selected wintering
> waterbirds in Gujarat changed between 2010 and 2025, and are those
> changes associated with temperature, rainfall, or vegetation/habitat
> trends — after correcting for the substantial rise in eBird observer
> activity over the same period?

---

## Why 2010–2025, not "20 years"

The researcher's own Gujarat eBird sampling-event extract shows checklist
volume was under 1,500/year before 2010 and grew roughly 30x by 2025
(1,477 in 2010 to 45,635 in 2025). Data before 2010 is too sparse to
support reliable annual metrics. Using the honestly-supportable window
is a methodological strength to state explicitly in the paper, not a
weakness to hide.

---

## Hypotheses (3, down from the original 5)

**H1.** Warmer winters are associated with earlier arrival dates.

**H2.** Migration timing (arrival, departure, peak week) has measurably
changed over the 2010–2025 study period.

**H3.** Wetland-dependent species show different migration-timing trend
patterns than grassland/dryland-associated species.

H3 is the project's most original contribution — it only makes sense to
test because the researcher has real field knowledge of habitat use across
these species. It should be central to the paper's narrative, not a
minor addendum.

Rejected from scope: rainfall-residence-duration hypothesis, NDVI-occurrence
hypothesis, wetland-change-hotspot-selection hypothesis. Not because
they're uninteresting, but because 3 hypotheses × 3 variables × 12
species is already a full scope for the timeline. List these explicitly
in the paper's Future Work section.

---

## Study Design

- **Study area:** Gujarat, India
- **Study period:** 2010–2025 (16 years)
- **Unit of analysis:** Species × Year
- **Species:** 12 total — 11 with full quantitative trend analysis, 1
  (Dalmatian Pelican) as a qualitative case study due to sparse records
- **Independent variables:** Mean temperature, rainfall, NDVI
- **Dependent variables:** First arrival (confirmed), last departure
  (confirmed), peak migration week (detection-rate-weighted), wintering
  duration, geographic centroid

See `01_RESEARCH_METHODOLOGY.md` for full detail.

---

## Explicitly Out of Scope

- Real-time prediction or forecasting
- Machine learning models of any kind
- Formal multiple regression with residual diagnostics (a correlation
  coefficient + linear trend + p-value is the ceiling of statistical
  complexity for this scope)
- Land cover (ESA WorldCover) and surface water (JRC) as standalone
  variables — NDVI substitutes as the habitat/vegetation proxy
- Production infrastructure: no PostgreSQL, no FastAPI backend, no
  Next.js frontend, no Docker, no CI/CD, no authentication
- A public-facing dashboard is a stretch goal only, attempted after the
  paper is complete, never a blocking dependency

---

## Deliverables

1. A written research paper (see `10_PAPER_OUTLINE.md`)
2. A reproducible analysis: Jupyter notebook(s) + a small set of Python
   modules, runnable by anyone with the raw data
3. A set of publication-quality figures and tables (see
   `08_FIGURE_TABLE_PLAN.md`)
4. (Stretch, post-paper) A simple Streamlit dashboard

---

## Definition of Done

The project is complete when:

- Every hypothesis (H1–H3) has been evaluated with a clear
  supported/not-supported/inconclusive conclusion, honestly reported
  even if the answer is "no meaningful association."
- Every figure and table in `08_FIGURE_TABLE_PLAN.md` exists and is
  reproducible by re-running the notebook.
- The Dalmatian Pelican case study is written.
- The paper follows the structure in `10_PAPER_OUTLINE.md` and the
  researcher can explain every methodological decision in it, including
  the ones AI helped implement.
- The AI/mentor disclosure is accurate and included.

---

## Document Set

| Doc | Purpose |
|---|---|
| 00_PROJECT_CHARTER.md | This document |
| 01_RESEARCH_METHODOLOGY.md | Study design, workflow |
| 02_METRICS_METHODOLOGY.md | Every metric: definition, formula, threshold |
| 03_ENVIRONMENTAL_FRAMEWORK.md | Temperature, rainfall, NDVI: why and how |
| 04_STATISTICAL_ANALYSIS_PLAN.md | Correlation, trend, hypothesis testing |
| 05_DATA_VALIDATION_PLAN.md | Cleaning rules, exclusions, sanity checks |
| 06_DATA_SOURCES.md | eBird, ERA5, MODIS access details |
| 07_DATABASE_SCHEMA.md | SQLite schema |
| 08_FIGURE_TABLE_PLAN.md | Every figure/table required |
| 09_ETL_AND_ANALYSIS_ENGINE.md | Algorithms and pipeline steps |
| 10_PAPER_OUTLINE.md | Section-by-section paper structure |
| 11_CODE_STRUCTURE.md | Folder layout, module responsibilities |
| 12_AI_AND_MENTOR_DISCLOSURE.md | Honest-authorship framing |
| 13_PROJECT_TIMELINE.md | Project development phases |
| 14_SCOPE_AND_ASSUMPTIONS.md | What changed from v1, and open judgment calls |
