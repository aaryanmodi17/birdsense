# METRICS_METHODOLOGY.md

Version 2.0 — Scoped Edition

## Purpose

Every metric used in BirdSense, with an exact, unambiguous calculation
method. No metric should ever be computed a different way in different
parts of the code — if you need to change a definition, change it here
first, then update the code and every figure/table that uses it.

These definitions carry forward the conflict resolution already done in
the original (v1) document set — see `14_SCOPE_AND_ASSUMPTIONS.md` for
what changed.

---

## 1. First Arrival Date (Confirmed)

**Definition:** The date of the **2nd independent complete-checklist
observation** of the species in a given year (not the single earliest
record).

**Why not the literal earliest record?** A single early vagrant or
misidentified record can distort the metric by weeks. Requiring 2
independent confirmations is a simple, defensible way to guard against
this — standard practice in phenology research, though the specific
threshold (N=2) is a judgment call, not a universal standard. Document
this choice explicitly in the paper.

**Low-confidence flag:** If a species-year has fewer than 2 total
observations, use the single available date and flag it `low_confidence
= True`. Report low-confidence years separately, don't silently include
them as equal-weight data points in the trend line.

**Raw Arrival (diagnostic only):** The literal single earliest
observation, stored separately as `raw_first_arrival`. Used only in the
observer-bias figure (see `08_FIGURE_TABLE_PLAN.md`), never as the
primary metric or in hypothesis testing.

---

## 2. Last Departure Date (Confirmed)

Mirrors First Arrival: date of the **2nd independent complete-checklist
observation counting backward from the latest**. Same low-confidence
rule. Raw version stored as `raw_last_departure`, diagnostic only.

---

## 3. Peak Migration Week

**Definition:** The ISO week with the highest **weekly detection rate**:

    Weekly Detection Rate =
    Complete checklists in that week reporting the species
    /
    Total complete checklists in that week (all species)

**Why not raw counts?** Detection rate corrects for the same
observer-growth problem described in `01_RESEARCH_METHODOLOGY.md`. A
week with more raw sightings might just be a week with more birders out,
not more birds. Ties broken by raw summed count, then earliest week
number.

**Raw Peak Week (diagnostic only):** Week with maximum summed raw
observation count, stored separately. Not used as a primary metric.

---

## 4. Wintering Duration

    Wintering Duration = Confirmed Departure − Confirmed Arrival (days)

---

## 5. Geographic Centroid

Weighted average location for a species-year:

    centroid_latitude  = Σ(latitude × observation_count) / Σ(observation_count)
    centroid_longitude = Σ(longitude × observation_count) / Σ(observation_count)

Used for H3 (habitat comparison) — a category-level average shift, not
just per-species.

---

## 6. Detection Rate (Observer Effort — Primary Metric)

    Detection Rate = Complete checklists reporting the species
                      / Total complete checklists (species-year)

This is the project's core effort-correction tool. Used to compute Peak
Week and reported alongside every migration-timing trend as context.

---

## 7. Observation Density

    Observation Density = Total individuals recorded / Total complete checklists

Secondary abundance indicator, reported but not central to hypothesis
testing.

---

## 8. Trend (per metric, per species)

For each of Arrival, Departure, Peak Week, Duration, across 2010–2025:

1. Plot the annual confirmed value.
2. Fit a simple linear regression (year → metric).
3. Report slope (change per year), R², and p-value.
4. Note any years flagged `low_confidence`.

This is a simple linear trend, not a multi-variable regression. That's a
deliberate scope decision — see `04_STATISTICAL_ANALYSIS_PLAN.md`.

---

## 9. Correlation (H1)

Pearson correlation between mean winter temperature (or rainfall) and
confirmed arrival date, per species, across 2010–2025. Report
coefficient and p-value. Use Spearman as a secondary check if the
relationship looks non-linear when plotted.

---

## Metric Summary Table

| Metric | Formula Location | Primary or Diagnostic |
|---|---|---|
| First Arrival (confirmed) | Sec 1 | Primary |
| Raw Arrival | Sec 1 | Diagnostic only |
| Last Departure (confirmed) | Sec 2 | Primary |
| Raw Departure | Sec 2 | Diagnostic only |
| Peak Week (detection-rate) | Sec 3 | Primary |
| Raw Peak Week | Sec 3 | Diagnostic only |
| Wintering Duration | Sec 4 | Primary |
| Geographic Centroid | Sec 5 | Primary (H3 only) |
| Detection Rate | Sec 6 | Primary |
| Observation Density | Sec 7 | Secondary |

---

## Acceptance Criteria

Every metric must:

- Have this exact written definition, referenced by section number in
  code comments.
- Produce the same output on the same input, every time (deterministic).
- Never be recalculated a different way anywhere else in the codebase.
