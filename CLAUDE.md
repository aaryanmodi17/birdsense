# CLAUDE.md — BirdSense

## Source of truth (applies to every session)

The folder `docs/` contains the project's markdown specification documents.
**Treat every document in `docs/` as the SOURCE OF TRUTH.**

- Never invent a metric, rule, threshold, or column that isn't in the docs.
- If two docs conflict, `00_PROJECT_CHARTER.md` wins; if the conflict isn't
  resolved there, STOP and ask the researcher rather than picking one.
- If a spec is ambiguous, ask the researcher before coding.
- Every function written must cite the doc section it implements in a comment
  (e.g. `implements 02_METRICS_METHODOLOGY.md sec 1`).

## Pipeline stages (summary of `docs/09_ETL_AND_ANALYSIS_ENGINE.md`)

The full data pipeline, source-of-truth in `09_ETL_AND_ANALYSIS_ENGINE.md`:

1. **Stage 1 — Load and Filter** (`src/load_and_clean.py`): load the raw EBD
   sampling + observations files (tab-delimited), apply validation Rules
   1, 2, 5, 6, 7, 8 from `05_DATA_VALIDATION_PLAN.md`, merge on
   `SAMPLING EVENT IDENTIFIER`, derive `year`, `month`, `iso_week`.
2. **Stage 2 — Observer Effort** (`src/observer_effort.py`): per species per
   year (2010–2025), compute `total_complete_checklists`,
   `observed_checklists`, `detection_rate`, `observation_density`.
3. **Stage 3 — Migration Metrics** (`src/migration_metrics.py`): confirmed
   arrival/departure, detection-rate-weighted peak week, wintering duration,
   geographic centroid.
4. **Stage 4 — Environmental Data** (`src/environmental_data.py`): pull and
   join temperature + rainfall (ERA5) and NDVI (MODIS) via Google Earth
   Engine; store annual winter means for correlation.
5. **Stage 5 — Trend and Correlation** (`src/statistics.py`): linear trend
   (`stats.linregress`) and Pearson correlation, applied per
   `04_STATISTICAL_ANALYSIS_PLAN.md`.

Then: evaluate hypotheses (H1–H3) and generate the figures/tables in
`08_FIGURE_TABLE_PLAN.md`.

Validation rules (`05_DATA_VALIDATION_PLAN.md`) are applied throughout; every
rejection is logged with a count — never silent. No metric is computed more
than one way in the codebase (reusable logic lives in `src/`, per
`11_CODE_STRUCTURE.md`).
