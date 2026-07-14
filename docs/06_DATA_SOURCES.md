# DATA_SOURCES.md

Version 2.0 — Scoped Edition

## Purpose

Every dataset used, how it's accessed, and its cost (all $0 — see
below).

---

## 1. eBird Basic Dataset (EBD) — Gujarat, all species

**Status:** Already obtained and inspected (sampling-event file,
244,752 checklists).

**Contains:** Checklist-level metadata — effort, duration, complete/
incomplete flag, protocol type. Does NOT contain species-level
observation counts on its own.

**Cost:** Free.

**Use:** Denominator for detection rate / observation density (Rules 3–4
in `05_DATA_VALIDATION_PLAN.md`).

---

## 2. eBird Basic Dataset — species-observation file, Gujarat

**Status:** Requested, larger "actual" Gujarat file, in progress.

**Contains:** Species-level sighting records — the actual counts per
checklist per species. Must be joined to the sampling-event file on
`SAMPLING EVENT IDENTIFIER` to compute anything.

**Cost:** Free.

**Use:** Core observation data for all migration metrics.

---

## 3. eBird — species-specific, global extent

**Status:** Requested, in progress.

**Contains:** Global sightings for the 12 study species, not restricted
to Gujarat.

**Cost:** Free.

**Use:** Background/context only — e.g., a short "global range and
flyway context" paragraph in the paper's Introduction, or a sanity check
that Gujarat arrival timing looks reasonable against the species'
broader wintering range. **Not** part of the core Gujarat trend analysis
— do not merge this into the main pipeline; keep it as a separate,
smaller, exploratory notebook section.

---

## 4. ERA5 Reanalysis (temperature, rainfall)

**Access:** Google Earth Engine, `ECMWF/ERA5` collection (researcher
already has GEE access).

**Cost:** Free — noncommercial/academic use.

**Note on quotas:** As of April 2026, GEE's free "Community" tier has a
monthly compute quota. This project's scale (a few years × a few
variables × Gujarat only) is well within it. No action needed unless
GEE itself flags a quota warning.

---

## 5. MODIS NDVI (MOD13Q1)

**Access:** Google Earth Engine, same account.

**Cost:** Free.

---

## Datasets Explicitly Not Used (see `03_ENVIRONMENTAL_FRAMEWORK.md`)

- ESA WorldCover — only 2 annual snapshots, can't show a 16-year trend
- JRC Global Surface Water — supported a hypothesis (H4) that was cut
  from scope

---

## Cost Summary

| Dataset | Cost |
|---|---|
| eBird (all 3 extracts) | $0 |
| ERA5 via GEE | $0 |
| MODIS NDVI via GEE | $0 |
| **Total** | **$0** |

---

## Directory Layout for Raw Data

    data/
      raw/
        ebird_sampling_gujarat.txt       (checklist metadata, have)
        ebird_observations_gujarat.txt   (species records, incoming)
        ebird_species_global/            (context only, incoming)
      processed/
        cleaned_observations.csv
        migration_metrics.csv
        environmental_data.csv
      exports/
        figures/
        tables/
