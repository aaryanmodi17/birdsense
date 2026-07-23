# DATABASE_SCHEMA.md

Version 2.0 — Scoped Edition (SQLite, no PostGIS)

## Purpose

A flat, simple schema appropriate for a single-researcher project. No
spatial extension, no environmental-snapshot decoupling, no import-batch
formality — those existed in v1 for a multi-contributor production
system. Lat/lon are stored as plain columns; "spatial" here just means
"filter/group by two numbers," which pandas/SQLite handle fine at this
scale (a few hundred thousand rows, not millions).

If you'd rather skip a database file entirely and just use pandas
DataFrames + CSV files, that's also fine at this scale — this schema is
here in case a real SQLite file is useful for the mentor-facing part of
the project (e.g., a Streamlit stretch-goal dashboard later wants to
query a DB rather than reload CSVs).

---

## Tables

```sql
CREATE TABLE species (
    species_id INTEGER PRIMARY KEY,
    common_name TEXT NOT NULL,
    scientific_name TEXT UNIQUE NOT NULL,
    habitat_category TEXT NOT NULL   -- 'wetland' or 'grassland_dryland'
);

CREATE TABLE observations (
    observation_id TEXT PRIMARY KEY,     -- eBird's own observation ID
    checklist_id TEXT NOT NULL,          -- SAMPLING EVENT IDENTIFIER
    species_id INTEGER NOT NULL REFERENCES species(species_id),
    observation_date TEXT NOT NULL,      -- ISO 8601
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    iso_week INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    locality TEXT,
    observation_count INTEGER,
    protocol_name TEXT,
    complete_checklist INTEGER NOT NULL, -- 0/1, after Rule 3 exclusion applied
    temperature REAL,                    -- NULL if unmatched
    rainfall REAL,
    ndvi REAL
);

CREATE TABLE checklists (
    checklist_id TEXT PRIMARY KEY,
    observation_date TEXT NOT NULL,
    year INTEGER NOT NULL,
    iso_week INTEGER NOT NULL,
    latitude REAL,
    longitude REAL,
    protocol_name TEXT,
    all_species_reported INTEGER,        -- raw eBird flag
    is_complete_for_effort INTEGER       -- after Rule 3/4 exclusions
);

CREATE TABLE migration_metrics (
    species_id INTEGER NOT NULL REFERENCES species(species_id),
    year INTEGER NOT NULL,
    first_arrival TEXT,
    raw_first_arrival TEXT,
    last_departure TEXT,
    raw_last_departure TEXT,
    peak_week INTEGER,
    peak_detection_rate REAL,
    raw_peak_week INTEGER,
    wintering_duration_days INTEGER,
    centroid_latitude REAL,
    centroid_longitude REAL,
    low_confidence INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (species_id, year)
);

CREATE TABLE observer_effort (
    species_id INTEGER NOT NULL REFERENCES species(species_id),
    year INTEGER NOT NULL,
    total_complete_checklists INTEGER,
    observed_checklists INTEGER,
    detection_rate REAL,
    observation_density REAL,
    PRIMARY KEY (species_id, year)
);

CREATE TABLE environmental_annual (
    year INTEGER PRIMARY KEY,
    mean_winter_temperature REAL,
    total_winter_rainfall REAL,
    total_monsoon_rainfall REAL,
    mean_winter_ndvi REAL
);
```

---

## Notes

- `species.habitat_category` implements the H3 grouping from
  `01_RESEARCH_METHODOLOGY.md` — change it here in one place if the
  grouping is revised.
- `low_confidence` on `migration_metrics` implements the N<2
  fallback rule from `02_METRICS_METHODOLOGY.md` sec 1.
- No foreign key to a `locations` table — at this scale, storing
  lat/lon directly on `observations` is simpler and sufficient. If a
  future version needs deduplicated hotspot identity, add a
  `locations` table then.
- No `environmental_snapshot` decoupling table (v1 had one) — with 3
  variables and no multi-species-sharing-a-snapshot performance concern,
  storing temperature/rainfall/ndvi directly on `observations` is
  simpler and equally correct at this scale.

---

## Acceptance Criteria

- Schema can be created and populated from the cleaned CSV outputs of
  the ETL pipeline (`09_ETL_AND_ANALYSIS_ENGINE.md`) with a single
  script.
- Every column has a clear source: either a raw eBird field, a derived
  field with a documented formula, or a GEE-sourced environmental value.
