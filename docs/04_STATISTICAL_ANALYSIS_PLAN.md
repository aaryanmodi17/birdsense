# STATISTICAL_ANALYSIS_PLAN.md

Version 2.0 — Scoped Edition (correlation + linear trend, no multi-variable regression)

## Purpose

The complete statistical workflow. Deliberately simpler than a
full research-lab pipeline: this scope uses correlation and simple
linear trend analysis, not multiple regression with residual
diagnostics. That's a legitimate, explainable choice for this project's
scope — be ready to say so if asked, rather than presenting it as more
sophisticated than it is.

---

## Pipeline

    Raw Observations
          |
    Observer-Effort Correction (detection rate)
          |
    Migration Metrics (confirmed arrival/departure/peak/duration/centroid)
          |
    Trend Analysis (linear regression: year -> metric)
          |
    Correlation Analysis (Pearson: environment -> metric)
          |
    Hypothesis Evaluation (H1-H3)
          |
    Written Conclusions

---

## Trend Analysis (supports H2)

For each species, for each of {Arrival, Departure, Peak Week, Duration}:

- Simple linear regression: independent variable = year,
  dependent variable = the metric.
- Report: slope (change per year, e.g. "−0.8 days/year"), R², p-value.
- A species-level trend is "significant" if p < 0.05.
- Also compute the trend at the **habitat-category level** (average
  across wetland-dependent species vs. grassland/dryland species) —
  this is the core test for H3.

---

## Correlation Analysis (supports H1)

- Pearson correlation between winter-season mean temperature and
  confirmed arrival date, per species, 2010–2025.
- Also compute for rainfall, exploratory (not a core hypothesis).
- Report coefficient (r) and p-value for each.
- If a scatter plot looks clearly non-linear, also report Spearman
  rank correlation and note why.

---

## Hypothesis Testing

**Significance threshold:** α = 0.05, consistent across all tests.

For each hypothesis, report:

1. What was tested, and on what data.
2. The statistical result (r or slope, p-value).
3. Effect size in plain terms (e.g., "arrival shifted ~2 weeks earlier
   over 16 years").
4. Decision: Supported / Not Supported / Inconclusive.
5. One sentence on plausible ecological mechanism, without claiming
   proof.

**H1** (temperature → earlier arrival): Pearson correlation per species,
then summarized across species.

**H2** (timing has changed over the period): Species-level and
category-level linear trends, from the Trend Analysis section above.

**H3** (habitat categories differ): Compare the trend slopes between
wetland-dependent and grassland/dryland species. A meaningful difference
is one where the two groups' trend directions or magnitudes are visibly
different across most species in each group — this is a comparative,
largely descriptive analysis at this scope, not a formal
group-difference significance test (e.g. no t-test between groups is
required, though your mentor may suggest adding one if time allows).

---

## What Is Explicitly NOT Done (and why that's fine)

- No multiple linear regression combining temperature + rainfall + NDVI
  simultaneously. Reason: with ~16 data points per species per year,
  a 3-predictor regression is statistically underpowered and would be
  misleading to present with confidence intervals. Single-variable
  correlation is the honest ceiling here.
- No multiple-comparison correction (e.g., Bonferroni) across the 12
  species. Reason: this is exploratory/descriptive research at this
  scope, not a confirmatory clinical-trial-style study. State this
  explicitly as a limitation.
- No residual diagnostics, no confidence-interval plots beyond a basic
  trend line's shaded region (matplotlib/seaborn default is enough).

---

## Reproducibility

Every result must be regenerable by re-running the notebook top to
bottom on the raw data. Record in the notebook header: dataset version
(EBD release date), analysis date, Python/library versions.

---

## Acceptance Criteria

- Every hypothesis has a stated conclusion, even if "no meaningful
  association."
- Every reported statistic includes both the number (r, slope) and the
  p-value — never one without the other.
- Effect sizes are stated in real-world units (days, weeks), not just
  statistical jargon.
