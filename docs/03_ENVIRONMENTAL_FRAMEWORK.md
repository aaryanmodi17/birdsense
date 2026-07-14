# ENVIRONMENTAL_FRAMEWORK.md

Version 2.0 — Scoped Edition (3 variables, down from 5)

## Purpose

Defines the environmental variables used, why each was chosen, and how
each is joined to bird observations.

---

## Variable 1: Temperature

**Why:** One of the strongest known drivers of migration timing (H1
directly tests this).

**Dataset:** ERA5 Reanalysis (ECMWF), accessed via Google Earth Engine —
specifically the **`ECMWF/ERA5/HOURLY`** collection, aggregated hourly → daily
(daily **mean** 2 m temperature) → winter-season mean. *Why this collection:*
the aggregated `ECMWF/ERA5/DAILY` is frozen at 2020-07 and cannot cover the
2010–2025 study period; ERA5-Land was rejected because it masks open water and
nulls coastal/marine waterbird locations (e.g. Gulf of Kutch). `ECMWF/ERA5/HOURLY`
covers the full period at the same ERA5 grid and retains over-water cells.

**Variable used:** Mean daily temperature, aggregated to a winter-season
mean (Nov–Feb) per year for correlation with arrival date.

**Spatial resolution:** ~25–30 km grid. Each observation is matched to
the nearest grid cell by latitude/longitude.

**Temporal resolution:** Hourly, aggregated to daily then to the winter season.

**Limitation to state in the paper:** Regional grid average, not
microclimate at the exact wetland — real but coarse.

---

## Variable 2: Rainfall

**Why:** Affects wetland extent and water availability, which
plausibly influences winter residence — supports discussion even though
the rainfall-residence hypothesis itself was cut from the core 3 (see
`00_PROJECT_CHARTER.md`); rainfall is kept as a variable for exploratory
correlation and future-work discussion.

**Dataset:** ERA5 precipitation from the same `ECMWF/ERA5/HOURLY` collection as
temperature, aggregated hourly → daily (daily **sum**) → winter-season total.

**Variable used:** Total winter-season rainfall (Nov–Feb) per year.

**Spatial/temporal resolution:** Same as temperature.

---

## Variable 3: NDVI (Vegetation / Habitat Proxy)

**Why:** Proxy for vegetation productivity and, at a rough level,
habitat/land-use change — this variable does the job originally assigned
to ESA WorldCover, which was cut because it only has two annual
snapshots (2020, 2021) and cannot show a 16-year trend. NDVI has
continuous data back to 2000.

**Dataset:** MODIS MOD13Q1, via Google Earth Engine.

**Variable used:** NDVI value at each observation's location, nearest
16-day composite to the observation date. Also aggregated to an annual
winter-season mean per location cluster, for the urbanization/habitat
discussion thread.

**Spatial resolution:** 250 m.

**Temporal resolution:** 16-day composites.

**Limitation to state in the paper:** NDVI reflects vegetation, not
urbanization directly — a declining NDVI trend near a hotspot is
suggestive of habitat change but is not itself proof of urban expansion.
Frame conclusions here cautiously, as "consistent with," not "confirms."

---

## Variables Explicitly Cut from Scope

| Variable | Original Purpose | Why Cut |
|---|---|---|
| ESA WorldCover (land cover) | Habitat classification | Only 2 snapshots (2020/2021); can't show a 16-year trend |
| JRC Global Surface Water | Wetland extent | Supported H4 (wetland-change/hotspot), which was cut from the 3 core hypotheses |

Both can be reintroduced in a future version if the project continues
past the current scope — mention this in the paper's Future Work
section.

---

## Spatial/Temporal Matching Rule

Priority order:
1. Exact observation date + nearest grid cell/composite.
2. If unavailable, nearest date within a reasonable window (±3 days for
   ERA5, nearest 16-day composite for NDVI).
3. If still unavailable, store NULL and log it — do not drop the bird
   observation, only the missing environmental field.

---

## Acceptance Criteria

- Every observation used in H1 has a temperature and rainfall value, or
  a logged reason why not.
- NDVI coverage is reported as a percentage of observations successfully
  matched, in the Data Quality section of the paper.
