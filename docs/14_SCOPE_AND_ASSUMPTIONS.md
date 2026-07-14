# SCOPE_AND_ASSUMPTIONS.md

Version 2.0

## Purpose

A single reference for what changed between the original v1 BirdSense
document set (production research-platform scope) and this v2 scoped
edition, and which decisions in v2 are assumptions that should be
confirmed with a mentor rather than treated as settled.

---

## What Changed and Why

| Area | v1 (Original) | v2 (This Set) | Why |
|---|---|---|---|
| Infrastructure | PostgreSQL+PostGIS, FastAPI, Next.js, Docker, CI/CD | SQLite (optional) + Python/pandas + Jupyter | v1 scoped for a production platform team; this is one independent researcher building solo with mentor and AI support |
| Species | 11 (equal treatment) | 12 (11 quantitative + 1 qualitative) | Added Dalmatian Pelican as a deliberate case study rather than forcing it through a trend pipeline its data can't support |
| Study period | "20 years" | 2010–2025 (16 years) | Actual checklist-volume data showed pre-2010 too sparse |
| Environmental variables | 5 (temp, rainfall, NDVI, land cover, surface water) | 3 (temp, rainfall, NDVI) | Land cover only had 2 snapshots; surface water supported a cut hypothesis |
| Hypotheses | 5 | 3 | Timeline; the 2 cut hypotheses supported the 2 cut variables anyway |
| Statistics | Multiple linear regression, residual diagnostics, multiple-comparison correction | Pearson correlation + simple linear trend | Appropriately scoped confidence for the sample size and timeline; avoids presenting more statistical sophistication than is actually there |
| Validation | 7-level formal scientific validation framework | Cleaning-rule validation report + personal field-knowledge sanity check | The researcher's own birding expertise is a legitimate substitute for formal expert review at this scope |
| Arrival/Departure metric | Naive earliest/latest record (later corrected to Nth-observation rule during v1 conflict resolution) | Same Nth-observation (N=2) rule, carried forward unchanged | This fix was already correct; no reason to redo it |
| Peak Week metric | Raw summed count (later corrected to detection-rate-weighted) | Same detection-rate-weighted definition, carried forward unchanged | Same as above |

---

## Assumptions Requiring Sign-Off

**1. Habitat category grouping (H3)** — see `01_RESEARCH_METHODOLOGY.md`.
Wetland-dependent: Pintail, Shoveler, Garganey, Wigeon, Pochard, Greylag
Goose, Greater Flamingo, Great White Pelican. Grassland/dryland: Bar-
headed Goose, Common Crane, Demoiselle Crane. This is a reasonable
default based on the "Primary Habitat" column in the researcher's own
species table, but wasn't explicitly confirmed — check with a mentor,
especially for Bar-headed Goose (uses both lakes and grasslands per the
original table) and Greylag Goose (wetland-associated but also grazes
on agricultural land).

**2. Dalmatian Pelican exclusion threshold** — "fewer than 8 of 16 years
with 2+ observations" is a starting rule, not validated against the
actual incoming species-specific data yet. Re-check once that data
arrives; adjust if the real sparsity pattern looks different.

**3. N=2 confirmation threshold for arrival/departure** — inherited from
v1's conflict resolution as "a working default... should be reviewed
against published phenology methodology." That review has still not
happened. Fine to proceed with N=2 for now; worth a specific mentor
conversation if time allows, since it's the one number in the whole
project's methodology that isn't derived from the data itself.

**4. Winter-season window (Nov–Feb)** for temperature/rainfall
aggregation — a reasonable default for Gujarat's wintering waterbirds,
but not independently verified against each species' actual typical
residence period. Species with notably different confirmed
arrival/departure windows (per the computed metrics) may need a
species-specific season window rather than one fixed Nov–Feb window for
everyone.

---

## What Was Deliberately NOT Carried Forward from v1

- `migration_hotspots`, `import_batches`, `environmental_snapshot` as
  separate database tables — unnecessary complexity at this scale.
- The OpenAPI spec, JSON schemas, REST API design entirely — no API is
  being built.
- The React component library, wireframes, dashboard design tokens —
  the dashboard is a stretch goal only; if built, keep it simple
  (Streamlit, not a custom frontend).
- Formal state machines for ETL/report pipelines — appropriate for a
  multi-user production system with retry logic, not a notebook a
  single researcher re-runs.

---

## How to Use This Document

If a decision anywhere else in this document set seems surprising or
under-justified, check here first — it's either explained in the
"What Changed and Why" table, or flagged as an open assumption above.
If it's neither, that's a gap worth raising with a mentor rather than
guessing.
