# ETL_AND_ANALYSIS_ENGINE.md

Version 2.0 — Scoped Edition

## Purpose

The complete data pipeline and analysis algorithms in one document —
combines what v1 split into ETL_PIPELINE.md, MIGRATION_ENGINE.md,
OBSERVER_EFFORT.md, and ENVIRONMENT_ENGINE.md, since at this scale one
researcher maintaining one notebook doesn't need four separate specs.

---

## Pipeline Overview

    Load raw EBD files (sampling + observations)
          |
    Apply validation/exclusion rules (05_DATA_VALIDATION_PLAN.md)
          |
    Merge species observations with checklist metadata
          |
    Compute observer effort per species/year
          |
    Compute migration metrics per species/year
          |
    Pull & join environmental data (GEE)
          |
    Run correlation + trend analysis
          |
    Evaluate hypotheses, generate figures/tables

---

## Stage 1: Load and Filter

Input: `ebird_sampling_gujarat.txt`, `ebird_observations_gujarat.txt`

1. Load both as pandas DataFrames (tab-delimited).
2. Apply Rules 1, 2, 5, 6, 7, 8 from `05_DATA_VALIDATION_PLAN.md`.
3. Merge on `SAMPLING EVENT IDENTIFIER`.
4. Derive `year`, `month`, `iso_week` from `OBSERVATION DATE`.

---

## Stage 2: Observer Effort

For each species, for each year 2010–2025:

```python
complete = checklists[
    (checklists["all_species_reported"] == 1) &
    (checklists["protocol_name"] != "Incidental")
]

total_complete_checklists = complete["checklist_id"].nunique()

observed_checklists = complete[
    complete["checklist_id"].isin(
        observations[observations["species_id"] == species_id]["checklist_id"]
    )
]["checklist_id"].nunique()

detection_rate = observed_checklists / total_complete_checklists if total_complete_checklists else None
```

Store: `total_complete_checklists`, `observed_checklists`,
`detection_rate`, `observation_density` (per
`02_METRICS_METHODOLOGY.md` sec 7).

---

## Stage 3: Migration Metrics

### Arrival / Departure (confirmed)

```python
CONFIRMATION_COUNT = 2  # see 02_METRICS_METHODOLOGY.md sec 1 for rationale

def confirmed_arrival(species_year_obs):
    obs = (
        species_year_obs
        .drop_duplicates("checklist_id")
        .dropna(subset=["observation_date"])
        .sort_values("observation_date")
    )
    if obs.empty:
        return None, None, None

    raw_first = obs.iloc[0]["observation_date"]

    if len(obs) < CONFIRMATION_COUNT:
        return raw_first, raw_first, True   # (confirmed, raw, low_confidence)

    confirmed = obs.iloc[CONFIRMATION_COUNT - 1]["observation_date"]
    return confirmed, raw_first, False

# departure: same logic, sort descending, symmetric naming
```

### Peak Week (detection-rate-weighted)

```python
def peak_week(species_year_obs, complete_checklists_by_week):
    observed_by_week = (
        species_year_obs[species_year_obs["complete_checklist"] == 1]
        .drop_duplicates("checklist_id")
        .groupby("iso_week")["checklist_id"].nunique()
    )
    weekly_rate = (observed_by_week / complete_checklists_by_week).fillna(0)

    if weekly_rate.empty:
        return None, None, None

    peak = weekly_rate.idxmax()
    rate = weekly_rate.max()

    raw_weekly = species_year_obs.groupby("iso_week")["observation_count"].sum()
    raw_peak = raw_weekly.idxmax() if not raw_weekly.empty else None

    return peak, rate, raw_peak
```

### Duration

```python
duration_days = (confirmed_departure - confirmed_arrival).days
```

### Centroid

```python
def centroid(species_year_obs):
    weights = species_year_obs["observation_count"].fillna(1)
    lat = (species_year_obs["latitude"] * weights).sum() / weights.sum()
    lon = (species_year_obs["longitude"] * weights).sum() / weights.sum()
    return lat, lon
```

---

## Stage 4: Environmental Data (via Google Earth Engine)

For temperature and rainfall (ERA5):

```python
import ee
ee.Initialize()

era5 = ee.ImageCollection("ECMWF/ERA5/DAILY")

def get_winter_temp_rainfall(year):
    winter = era5.filterDate(f"{year}-11-01", f"{year+1}-02-28")
    # reduce over Gujarat region, extract mean_2m_air_temperature and total_precipitation
    ...
```

For NDVI (MODIS):

```python
modis = ee.ImageCollection("MODIS/061/MOD13Q1")

def get_ndvi(latitude, longitude, date):
    point = ee.Geometry.Point([longitude, latitude])
    composite = modis.filterDate(date - timedelta(days=8), date + timedelta(days=8)) \
                      .filterBounds(point) \
                      .first()
    return composite.select("NDVI").reduceRegion(...)
```

(Exact GEE syntax to be finalized during Week 5–6 implementation — this
is the algorithm shape, not copy-paste-ready code. A mentor session is
a good place to firm up the GEE calls specifically.)

Join to `observations` by nearest date/location per
`03_ENVIRONMENTAL_FRAMEWORK.md`'s matching rule. Store annual winter
means separately in `environmental_annual` for the correlation analysis.

---

## Stage 5: Trend and Correlation

```python
from scipy import stats

def linear_trend(years, values):
    slope, intercept, r, p, stderr = stats.linregress(years, values)
    return {"slope": slope, "r_squared": r**2, "p_value": p}

def correlation(x, y):
    r, p = stats.pearsonr(x, y)
    return {"r": r, "p_value": p}
```

Applied per `04_STATISTICAL_ANALYSIS_PLAN.md`.

---

## Validation Rules (applied throughout)

Reject/flag per `05_DATA_VALIDATION_PLAN.md`. Every rejection is logged
with a count — never silent.

---

## Performance Expectations

At this scale (a few hundred thousand checklist rows, 12 species, 16
years), the entire pipeline should run in well under a minute on a
laptop. If it's slower, something is likely wrong (e.g., a non-vectorized
loop over all rows) — flag it to a mentor rather than assuming it's
normal.

---

## Acceptance Criteria

- Running the notebook top-to-bottom on raw data reproduces every table
  and figure with no manual intervention.
- Every function here has a docstring referencing the corresponding
  section of `02_METRICS_METHODOLOGY.md`.
- No metric is computed more than one way in the codebase.
