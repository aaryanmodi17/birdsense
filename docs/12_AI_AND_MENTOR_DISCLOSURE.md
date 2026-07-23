# AI_AND_MENTOR_DISCLOSURE.md

Version 2.0

## Purpose

A short, honest, reusable statement of how this project was built —
for the paper's Methods/Acknowledgments section, for the repository
README, and for the researcher to have a consistent, accurate answer
ready whenever asked about the project.

---

## Methodology Statement

> This project's implementation used AI-assisted coding (Claude, by
> Anthropic) for writing and debugging the Python data pipeline and
> statistical analysis code, guided throughout by the researcher's own
> research design decisions. Technical mentorship was provided by
> data-science and analytics mentors. The research
> question, hypotheses, species and variable selection, and
> interpretation of results — including the decision to treat Dalmatian
> Pelican as a qualitative case study due to insufficient data for
> quantitative trend analysis — were the researcher's own, informed by
> [N] years of personal eBird contribution and field experience in
> Gujarat.

---

## What Was the Researcher's Own Contribution (be specific, not vague)

These are the actual judgment calls made over the course of this
project, not generic claims:

- Identified the real-world observation (city growth, changing weather
  patterns potentially affecting bird patterns) that motivated the
  research question.
- Selected the 12 study species based on personal field knowledge of
  which species have reliable long-term Gujarat records.
- Flagged that ESA WorldCover's 2-snapshot limitation made it unsuitable
  for a 16-year trend, before that gap was independently confirmed.
- Flagged that Dalmatian Pelican's known rarity/irregular occurrence
  would likely break a quantitative trend metric — later confirmed by
  the data itself.
- Made the informed choice to scope the study period to 2010–2025 based
  on actual checklist-volume evidence, rather than an arbitrary "20
  years."
- Defined the habitat-category grouping for H3, the project's most
  original analytical angle.
- Personally validates computed migration metrics against direct field
  experience (see `05_DATA_VALIDATION_PLAN.md`'s sanity-check step) — a
  validation method unavailable to someone building the same pipeline
  without hands-on birding experience in the study region.

---

## What to Avoid Saying

- "I coded this entirely myself" — not accurate, and checkable.
- Implying the AI made scientific decisions (hypothesis choice, species
  selection, interpretation) — it didn't; the researcher did, with AI as
  an implementation tool.
- Overstating the statistical sophistication (e.g., calling the
  correlation/trend analysis a "regression model" or implying formal
  multi-hypothesis correction was used, when it wasn't — see
  `04_STATISTICAL_ANALYSIS_PLAN.md`'s explicit list of what was NOT
  done).

---

## Practical Checklist

- [ ] Be able to explain, without notes, what every function in `src/`
      does and why — not memorized, genuinely understood.
- [ ] Be able to explain why 2010–2025 was chosen, why N=2 confirmation
      was used for arrival/departure, and why 3 hypotheses/3 variables
      instead of the original 5/5 — all real, defensible scope
      decisions, not arbitrary cuts.
- [ ] Include this disclosure (or a version of it) in the repository
      README and the paper's Methods/Acknowledgments section, so the
      AI-assisted implementation and mentor support are documented
      wherever the code or paper are shared.
