# RESEARCH_METHODOLOGY.md

Version 2.0 — Scoped Edition

## Purpose

Defines how the research is conducted, from raw data to conclusions.
The software (`09_ETL_AND_ANALYSIS_ENGINE.md`) implements this
document — not the other way around.

---

## Research Philosophy

BirdSense evaluates **associations**, not causation. Every result is
reported as one of: strong evidence, weak/uncertain evidence, or no
meaningful association. A "no association" result is a valid, reportable
finding — do not discard or downplay it.

---

## Study Species (12 total)

| # | Common Name | Scientific Name | Habitat Category | Analysis Type |
|---|---|---|---|---|
| 1 | Northern Pintail | *Anas acuta* | Wetland-dependent | Full quantitative |
| 2 | Northern Shoveler | *Spatula clypeata* | Wetland-dependent | Full quantitative |
| 3 | Garganey | *Spatula querquedula* | Wetland-dependent | Full quantitative |
| 4 | Eurasian Wigeon | *Mareca penelope* | Wetland-dependent | Full quantitative |
| 5 | Common Pochard | *Aythya ferina* | Wetland-dependent | Full quantitative |
| 6 | Bar-headed Goose | *Anser indicus* | Grassland/dryland | Full quantitative |
| 7 | Greylag Goose | *Anser anser* | Wetland-dependent | Full quantitative |
| 8 | Common Crane | *Grus grus* | Grassland/dryland | Full quantitative |
| 9 | Demoiselle Crane | *Anthropoides virgo* | Grassland/dryland | Full quantitative |
| 10 | Greater Flamingo | *Phoenicopterus roseus* | Wetland-dependent | Full quantitative |
| 11 | Great White Pelican | *Pelecanus onocrotalus* | Wetland-dependent | Full quantitative |
| 12 | Dalmatian Pelican | *Pelecanus crispus* | Wetland-dependent | Qualitative case study only |

**Habitat category is an assumption pending your/mentor sign-off** — see
`14_SCOPE_AND_ASSUMPTIONS.md`. It is used only to group species for H3;
it does not affect any other calculation.

**Dalmatian Pelican exclusion rule:** included in raw data exploration
and reporting, but excluded from trend/correlation statistics if fewer
than 8 of the 16 study years have at least one confirmed observation
(2+ independent checklists). Verify this threshold against the actual
data in Week 1 — it is a working default, not a hard requirement.

---

## Study Period

**2010–2025** (16 years). See `00_PROJECT_CHARTER.md` for the data-driven
justification. Do not use pre-2010 records in any trend or correlation
calculation; they may be shown in a raw-data figure to illustrate the
observer-growth problem, clearly labeled as excluded from analysis.

---

## Data Sources

- eBird Basic Dataset (EBD) — Gujarat, species-filtered
- eBird sampling event data (checklist/effort metadata) — Gujarat
- ERA5 Reanalysis (temperature, rainfall) via Google Earth Engine
- MODIS NDVI (MOD13Q1) via Google Earth Engine

See `06_DATA_SOURCES.md` for access details.

---

## Data Processing Workflow

1. Load raw EBD species-observation file and sampling-event file.
2. Filter to the 12 study species.
3. Filter to Gujarat (state field).
4. Apply validation/exclusion rules (`05_DATA_VALIDATION_PLAN.md`):
   drop `Historical` observation type, drop pre-2010 records, exclude
   `Incidental` checklists from effort-denominator calculations.
5. Standardize dates, derive year/month/ISO week.
6. Merge species observations with checklist metadata on
   `SAMPLING EVENT IDENTIFIER`.
7. Compute observer-effort metrics (detection rate, observation density)
   per species/year.
8. Compute migration metrics per species/year (confirmed arrival,
   confirmed departure, detection-rate-weighted peak week, wintering
   duration, geographic centroid).
9. Pull environmental data (temperature, rainfall, NDVI) via GEE, joined
   to observations by location and date.
10. Run correlation and trend analysis.
11. Evaluate H1–H3.
12. Generate figures, tables, and the Dalmatian Pelican case study.

---

## Observer Bias

Citizen-science participation in Gujarat eBird grew roughly 30x from
2010 to 2025 (source: researcher's own sampling-event extract). BirdSense
therefore:

- Never uses raw annual observation/sighting counts as a primary metric.
- Uses detection rate (checklists reporting the species / total complete
  checklists) as the primary effort-corrected metric.
- Reports observer effort (total complete checklists per year) alongside
  every trend, so a reader can see the correction is real.

---

## Interpretation Rules

Every hypothesis conclusion is reported as one of:

- **Strong evidence of association** — consistent across the study
  period, statistically significant (p < 0.05), effect size discussed.
- **Weak/uncertain evidence** — statistically significant but small
  effect, or inconsistent across species within a category.
- **No meaningful association** — not statistically significant. Report
  this plainly; it's a legitimate finding.

No causal language. "Associated with," "consistent with," never "causes"
or "proves."

---

## Limitations (state these explicitly in the paper)

- Citizen-science observer bias, only partially correctable
- Uneven observer coverage across Gujarat's districts
- ERA5's ~25–30 km grid resolution vs. point observations
- N=2 confirmation threshold for arrival/departure is a judgment call,
  not a validated standard
- Correlation does not imply causation
- Small quantitative sample for Dalmatian Pelican (addressed via
  qualitative treatment, not hidden)
