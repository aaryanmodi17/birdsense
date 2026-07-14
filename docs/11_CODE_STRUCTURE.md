# CODE_STRUCTURE.md

Version 2.0 — Scoped Edition

## Purpose

Folder layout for the actual code. Deliberately small — no backend,
frontend, Docker, or deployment directories.

---

## Repository Layout

```
birdsense/
├── README.md
├── data/
│   ├── raw/                    (not committed to git — large files)
│   │   ├── ebird_sampling_gujarat.txt
│   │   ├── ebird_observations_gujarat.txt
│   │   └── ebird_species_global/
│   └── processed/
│       ├── cleaned_observations.csv
│       ├── migration_metrics.csv
│       └── environmental_data.csv
│
├── src/
│   ├── __init__.py
│   ├── load_and_clean.py       (Stage 1: 09_ETL_AND_ANALYSIS_ENGINE.md)
│   ├── observer_effort.py      (Stage 2)
│   ├── migration_metrics.py    (Stage 3)
│   ├── environmental_data.py   (Stage 4, GEE calls)
│   ├── statistics.py           (Stage 5: trend + correlation)
│   └── validation.py           (05_DATA_VALIDATION_PLAN.md rules)
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_observer_effort.ipynb
│   ├── 03_migration_metrics.ipynb
│   ├── 04_environmental_join.ipynb
│   ├── 05_statistics_and_hypotheses.ipynb
│   └── 06_figures_and_tables.ipynb
│
├── outputs/
│   ├── figures/                (Figure 1-9, as PNG/SVG)
│   └── tables/                 (Table 1-6, as CSV + Markdown)
│
├── paper/
│   └── birdsense_paper.md      (or .docx — matches 10_PAPER_OUTLINE.md)
│
├── docs/                       (this entire document set)
│
└── requirements.txt
```

---

## Why Notebooks + `src/`, Not Just Notebooks

Splitting reusable logic into `src/` modules (imported into notebooks)
rather than writing everything inline in notebook cells keeps the
notebooks readable as a narrative — each one tells a clear step of the
story — while keeping the actual calculation logic in one place per
`02_METRICS_METHODOLOGY.md`'s acceptance criterion ("never computed a
different way in different parts of the codebase"). This also makes it
easier for a mentor to review specific logic without hunting through
notebook cells.

---

## Minimum Dependencies

```
pandas
numpy
scipy
matplotlib
seaborn
earthengine-api
geopandas       (only if Figure 1/8 maps need it; optional otherwise)
folium           (optional, for interactive map export)
jupyter
```

No FastAPI, no SQLAlchemy, no Next.js, no Docker.

---

## Stretch Goal (post-paper): Streamlit Dashboard

If time remains after the paper is complete:

```
dashboard/
└── app.py    (reads outputs/tables/*.csv, renders with Streamlit)
```

Do not start this before the paper and figures are done — it competes
for the same time and isn't required for the core research deliverable.

---

## Acceptance Criteria

- Anyone (mentor, technically-inclined reader) can
  clone the repo, run `pip install -r requirements.txt`, run the
  notebooks in order, and reproduce every output.
- No notebook cell contains a metric calculation that duplicates logic
  already in `src/`.
