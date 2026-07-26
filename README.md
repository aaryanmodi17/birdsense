# BirdSense

**Has migration timing of wintering waterbirds in Gujarat changed from 2010–2025?
A reproducible, effort-corrected analysis of 16 years of eBird data against
temperature, rainfall and vegetation trends.**

---

## The headline finding

Twelve of twelve waterbird species appear to be arriving in Gujarat earlier every
year, with statistically significant trends of −0.4 to −1.6 days per year.

**That signal is an artifact.** It vanishes completely — 12 species down to 0 —
the moment the timing metric is made robust to observer effort, and it stays at 0
after a calendar-boundary correction. Over the same period, eBird complete-checklist
effort in Gujarat grew roughly **303-fold** (133 checklists in 2010 → 40,288 in 2025).
More people looking earlier in the season finds birds earlier in the season.

The giveaway: by 2021–2025 the naive "first arrival" date is pinned at **January 1
in all twelve species**. The metric has hit the calendar floor and flat-lined — a
signature no biological trend could produce. Meanwhile winter temperature itself
showed **no significant trend** across the window (slope +0.02 °C/yr, p = 0.39), so
there was no warming exposure to invoke in the first place.

This repository is the full pipeline, statistics and manuscript behind that result,
plus the diagnostics needed to tell a real phenological signal from a sampling
artifact in any rapidly-growing citizen-science dataset.

---

## Research question

> Have migration timing and spatial distribution of selected wintering waterbirds in
> Gujarat changed between 2010 and 2025, and are those changes associated with
> temperature, rainfall, or vegetation/habitat trends — after correcting for the
> substantial rise in eBird observer activity over the same period?

### Hypotheses and outcomes

| | Hypothesis | Outcome |
|---|---|---|
| **H1** | Warmer winters are associated with earlier arrival dates | **Inconclusive / not supported** — 1/12 species significant on the naive metric (Garganey, r = −0.514, p = 0.042), **0/12** on the effort-robust metric. Winter temperature had no significant trend to begin with (p = 0.39). |
| **H2** | Migration timing has measurably changed over 2010–2025 | **Supported on the naive metric (12/12), then collapses to 0/12.** Confirmed-arrival slopes −0.404 to −1.644 days/yr, all p < 0.05; on detection-rate-weighted peak week, 0/12; after the migration-year reframe, 0/12 again. |
| **H3** | Wetland-dependent species show different timing trends than grassland/dryland species | **Not supported** — the two guilds move together (wetland −0.698 vs grassland/dryland −0.975 days/yr, same sign, difference < 1 day/yr), and both are measured on the effort-contaminated metric anyway. |

### Two artifacts, one real signal — and a lesson about the fix itself

- **The vanishing advance.** Arrival date is inversely correlated with observer effort
  in all 12 species (r = −0.396 to −0.545; significant in 3/12), and saturates at
  January 1 by 2021.
- **The disappearing decline — and its hidden twin.** Northern Pintail's statewide
  detection rate falls 0.19 → 0.07. At Nal Sarovar, a fixed hotspot, the naive
  all-years trend looks flat (p = 0.975) — but that "flat" reading is itself an
  artifact of near-zero samples in 2010–2013 (as few as 2–6 checklists/year, where
  a single sighting swings the rate from 0.000 to 0.500). Restricted to years with
  ≥20 checklists, Nal Sarovar actually **declines** (winter slope −0.024/yr,
  p = 0.039), tracking the statewide pattern rather than contradicting it.
- **No candidate real signal survives.** Bar-headed Goose detection rate at Thol Lake
  appeared to rise ~82% (p ≈ 0.01) under the naive all-years fit — but this is driven
  by the same sparse-early-years problem. Restricted to ≥20-checklist years, the trend
  is not significant (+0.006/yr, p = 0.49). Once sample size is accounted for, **no
  species in this dataset shows a site-level abundance trend that is both significant
  and robust** — the fixed-site "control" needed its own effort correction, the same
  lesson the paper applies everywhere else.

---

## Study design

- **Study area:** Gujarat, India (bounding box 20–24.7 °N, 68–74.5 °E)
- **Study period:** 2010–2025 (16 years). Pre-2010 eBird volume in Gujarat is under
  1,500 checklists/year — too sparse for reliable annual metrics. Using the
  honestly-supportable window is stated as a methodological strength, not hidden.
- **Unit of analysis:** species × year (192 rows: 12 species × 16 years)
- **Winter season:** November–February
- **Statistical ceiling:** Pearson correlation + simple linear trend, α = 0.05.
  Deliberately no machine learning, no multiple regression, no forecasting.

### The 12 study species

Habitat guild drives the H3 grouping and is the project's most original analytical
angle. Guild assignment lives in exactly one place, `src/validation.py:STUDY_SPECIES`.

| # | Common name | Scientific name | Guild | Records |
|---|---|---|---|---|
| 1 | Northern Pintail | *Anas acuta* | wetland | 14,085 |
| 2 | Northern Shoveler | *Spatula clypeata* | wetland | 23,229 |
| 3 | Garganey | *Spatula querquedula* | wetland | 9,945 |
| 4 | Eurasian Wigeon | *Mareca penelope* | wetland | 10,242 |
| 5 | Common Pochard | *Aythya ferina* | wetland | 8,807 |
| 6 | Bar-headed Goose | *Anser indicus* | grassland/dryland | 6,418 |
| 7 | Greylag Goose | *Anser anser* | wetland | 12,095 |
| 8 | Common Crane | *Grus grus* | grassland/dryland | 20,211 |
| 9 | Demoiselle Crane | *Grus virgo* | grassland/dryland | 6,732 |
| 10 | Greater Flamingo | *Phoenicopterus roseus* | wetland | 17,937 |
| 11 | Great White Pelican | *Pelecanus onocrotalus* | wetland | 12,759 |
| 12 | Dalmatian Pelican | *Pelecanus crispus* | wetland | 12,444 |

All twelve are confirmed in all 16 of 16 study years.

> **Taxonomy trap worth knowing about.** Demoiselle Crane is ***Grus virgo*** in the
> current eBird/Clements taxonomy. The older synonym *Anthropoides virgo* — which is
> what the project's own methodology doc lists — matches **zero** records in the
> May-2026 release and would have silently dropped ~8,300 observations. This is
> exactly the failure mode validation Rule 6 exists to catch.

> **Dalmatian Pelican was designed as a sparse qualitative case study** on the
> assumption it was too rare for quantitative treatment. The real data overturns
> that: it is well represented (12,444 records, confirmed correct) and confirmed in
> all 16 years, and it behaves like the other eleven (naive arrival slope −0.674
> days/yr, p = 0.0009; effort-robust peak week not significant). Its "earlier
> arrival" is the same artifact.

---

## Quick start

```bash
git clone <this-repo> && cd birdsense
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

You also need the raw eBird data (see [Data](#data) below) placed at:

```
data/raw/ebird_sampling_gujarat.txt      # checklist-level metadata (~26 MB)
data/raw/ebird_observations_gujarat.txt  # species observations (~34 MB)
```

Both must be **tab-delimited**. Neither is committed — they are gitignored.

Then, in order of increasing effort:

```bash
# One-screen PASS/FAIL audit of the whole pipeline against the docs
.venv/bin/python scripts/audit_report.py

# The test suite (52 tests)
.venv/bin/python -m pytest tests/ -q

# Individual pipeline stages, each with a runnable CLI
.venv/bin/python -m src.load_and_clean       # Stage 1 + validation report
.venv/bin/python -m src.observer_effort      # Stage 2
.venv/bin/python -m src.migration_metrics    # Stage 3 (writes data/processed/)
.venv/bin/python -m src.environmental_data   # Stage 4 (MOCK demo only)

# The analysis notebooks
.venv/bin/jupyter notebook notebooks/05_statistics_and_hypotheses.ipynb
.venv/bin/jupyter notebook notebooks/06_figures_and_tables.ipynb
```

> Modules must be run with `python -m src.<module>`, not `python src/<module>.py` —
> intra-package imports are relative.

> `pytest` is intentionally **not** in `requirements.txt`. An acceptance test asserts
> the dependency set is exactly the nine packages the code structure doc specifies, so
> adding pytest there would fail the suite. Install it separately:
> `.venv/bin/pip install pytest`.

---

## Pipeline

Five stages. Every function cites the doc section it implements; no metric is
computed two different ways anywhere in the codebase (this is enforced by an
acceptance test, not just convention).

### Stage 1 — Load and filter · `src/load_and_clean.py`

Loads both tab-delimited EBD files, applies the row-dropping validation rules,
merges on `SAMPLING EVENT IDENTIFIER`, derives `year` / `month` / `iso_week`.
Returns a `Stage1Result` carrying the cleaned frames plus a `ValidationReport`
with a per-rule drop count — **every exclusion is logged with a count, never
applied silently.**

Real drop counts on the May-2026 release:

| Rule | What it rejects | Checklists | Observations |
|---|---|---|---|
| 1 | `OBSERVATION TYPE == "Historical"` (retrospective bulk uploads with implausible dates, e.g. 1800-02-01) | 16,186 | 9,707 |
| 2 | Date outside 2010–2025, or unparseable | 25,189 | 22,134 |
| 5 | `STATE != "Gujarat"` | 0 | 0 |
| 6 | Not one of the 12 study species (matched on `SCIENTIFIC NAME`, never common name) | n/a | 0 |
| 7 | Duplicate `SAMPLING EVENT IDENTIFIER` (+ species for observations) — shared/group checklists | 0 | 0 |
| 8 | Missing or out-of-bbox coordinates | 13 | 0 |

Rules 3 and 4 **do not drop rows** — they govern the effort denominator only:

- **Rule 3** flags `PROTOCOL NAME == "Incidental"` checklists for exclusion from
  detection-rate denominators, even when `ALL SPECIES REPORTED == 1`.
- **Rule 4** restricts the denominator to complete checklists.

Net: **244,752 raw checklists → 203,364 usable → 178,669 effort-eligible complete.**
Observations: 184,301 → 152,460.

### Stage 2 — Observer effort · `src/observer_effort.py`

Per species per year: `total_complete_checklists`, `observed_checklists`,
`detection_rate`, `observation_density`. Reuses Stage 1's `is_complete_for_effort`
flag rather than re-deriving Rules 3 and 4, so completeness is never defined twice.

```
detection_rate      = complete checklists reporting the species / total complete checklists
observation_density = total individuals recorded / total complete checklists
```

Detection rate is the **primary** effort-correction metric; density is secondary and
not central to hypothesis testing.

### Stage 3 — Migration metrics · `src/migration_metrics.py`

| Metric | Definition |
|---|---|
| `first_arrival` | Date of the **2nd** independent complete-checklist observation that year — not the single earliest record |
| `last_departure` | Date of the 2nd observation counting **backward** from the latest |
| `peak_week` | ISO week with the highest **weekly detection rate** (species-reporting checklists / all complete checklists that week). Ties broken by raw count, then earliest week |
| `wintering_duration_days` | `last_departure − first_arrival` |
| `centroid_latitude/longitude` | Observation-count-weighted mean location (missing counts weight 1) |
| `low_confidence` | Flag; see below |
| `raw_first_arrival`, `raw_last_departure`, `raw_peak_week` | **Diagnostic only** — never used in hypothesis testing. The raw-vs-confirmed gap is what Figure 3 exists to show |

The N=2 confirmation threshold is a deliberate judgment call, not a published
standard, and is the one number in the methodology not derived from the data itself.
It exists to stop a single vagrant or misidentification from setting a species' arrival date.

**`low_confidence` is set when a species-year has fewer than 3 observations** — this
extends the methodology doc's original "fewer than 2" rule. With exactly two
observations, confirmed arrival and confirmed departure are the same record or cross
over, producing a zero or negative wintering duration. Such species-years are flagged
and their duration left null; low-confidence years are excluded from every trend line
rather than silently included as equal-weight points.

**The migration-year reframe.** Calendar ISO weeks put late-December and early-January
observations ~51 weeks apart, even though they are days apart in the birds' season.
`migration_year_week()` re-anchors the year to **July 1**, making the Nov–Feb winter
contiguous. It reuses the same `peak_week()` engine — the metric is not reimplemented.
This is what turned the "near-significant" negative calendar peak-week slopes into
approximately zero, showing they were largely a wrap artifact. Covers 15 full winters
(2010–2024); the 2025 migration year's Jan–Feb 2026 tail falls outside the study window.

### Stage 4 — Environmental data · `src/environmental_data.py`

Pulls ERA5 climate and MODIS NDVI through Google Earth Engine.

| | Dataset | Band | Aggregation | Resolution |
|---|---|---|---|---|
| Temperature | `ECMWF/ERA5/HOURLY` | `temperature_2m` | hourly → daily **mean** → winter mean | ~25–30 km |
| Winter rainfall | `ECMWF/ERA5/HOURLY` | `total_precipitation` | hourly → daily **sum** → Nov–Feb total | ~25–30 km |
| Monsoon rainfall | `ECMWF/ERA5/HOURLY` | `total_precipitation` | Jun 1 – Sep 30 total (exploratory) | ~25–30 km |
| NDVI | `MODIS/061/MOD13Q1` | `NDVI` | nearest 16-day composite | 250 m |

`ECMWF/ERA5/DAILY` is **frozen at 2020-07** and cannot cover the study period;
ERA5-Land was rejected because it masks open water and nulls coastal waterbird
locations such as the Gulf of Kutch. Both were verified before the switch to `HOURLY`.

**Unit conversions are isolated as pure, separately-tested functions**, because each
is a known silent-bug source: Kelvin → °C (−273.15; skipping it yields ~295 instead
of ~22), metres → mm (×1000), MODIS scaled integer → NDVI (×0.0001).

**Matching rule** (never drops a bird observation, only the environmental field):
exact date and grid cell → nearest date within ±3 days for ERA5 / nearest 16-day
composite for NDVI → store NULL and log it. Coverage is reported as a percentage.

**Mock mode.** `mock=True` returns deterministic fake values so the pipeline runs
end-to-end before GEE is authenticated. Output is tagged `env_source='MOCK-FAKE'`,
files get `.MOCK.` in the name, and a warning prints. Mock values must never reach
the paper.

<details>
<summary><strong>Google Earth Engine authentication</strong></summary>

1. You need a Google account with Earth Engine access and a Google Cloud project
   with the Earth Engine API enabled. Sign up (free for academic/non-commercial) at
   <https://earthengine.google.com/> and note the Cloud **project ID**.
2. Authenticate once — opens a browser, stores a token under `~/.config/earthengine/`:
   ```bash
   .venv/bin/earthengine authenticate
   ```
3. Export the project id:
   ```bash
   export EARTHENGINE_PROJECT=your-gcp-project-id
   ```
4. Verify with the five-point eyeball test, which prints raw *and* converted values
   at five real Gujarat wetlands so you can sanity-check units before trusting them:
   ```bash
   .venv/bin/python scripts/test_gee_5points.py
   ```
   Expect ERA5 temperature ~290–300 K → ~17–27 °C, rainfall in metres (~0.000x) → mm,
   MODIS NDVI raw ~3000–7000 → 0.3–0.7.

`EARTHENGINE_PROJECT` is the only environment variable the codebase reads.
</details>

### Stage 5 — Trend and correlation · `src/statistics.py`

- **Trend (H2):** `scipy.stats.linregress`, year → metric, per species. Reports slope
  (days/year), R², p-value, n. Date metrics are converted to day-of-year so slopes
  are in days per year.
- **Correlation (H1):** `scipy.stats.pearsonr` between winter mean temperature and the
  timing metric. Spearman reported as a secondary non-linearity check.
- **α = 0.05**, defined once as a module constant and used everywhere.
- **Effort diagnostic:** `effort_vs_arrival_correlation()` correlates the arrival
  metric against checklist effort directly. A strong correlation means the metric
  tracks observation, not phenology. This is the function that exposed the artifact.
- **Side-by-side builders:** `build_h1_comparison` / `build_h2_comparison` present the
  effort-sensitive and effort-robust metrics together, so the collapse is visible
  rather than the naive result being quietly overwritten.
- **Site-level sample-size check:** fixed-hotspot abundance trends (Nal Sarovar,
  Thol Lake — see "Two artifacts, one real signal" above) are computed both on all
  available years and restricted to years with **≥20 site-level checklists**, using
  a 10 km radius around each hotspot's coordinates. The threshold was identified
  after inspecting the data — early years (2010–2013) had as few as 2–6 checklists
  per site-year — rather than set in advance; both the full-period and
  restricted-period results are reported for transparency. Full per-year figures
  are in `paper/tables/tableS5_site_level.csv`.

Explicitly **not** done, per the analysis plan: no multiple regression combining
temperature + rainfall + NDVI (underpowered at 16 points), no multiple-comparison
correction across the 12 species (stated as a limitation), no residual diagnostics.
An acceptance test enforces the absence of forbidden methods.

---

## Data

| Dataset | Provider | Coverage | Resolution | Cost |
|---|---|---|---|---|
| eBird Basic Dataset, Gujarat (`IN-GJ`, v1.16, relMay-2026) | Cornell Lab of Ornithology | 2010–2025 | checklist-level | $0 |
| ERA5 reanalysis (temperature, precipitation) | ECMWF via Google Earth Engine | 2010–2025 | ~25–30 km, hourly | $0 |
| MODIS MOD13Q1 (NDVI) | NASA via Google Earth Engine | 2010–2025 | 250 m, 16-day | $0 |

The raw extract is 244,752 checklists and ~5.3 million observation records across
546 species. Request the EBD from <https://ebird.org/data/download>; it is free for
research use but requires an approved access request.

`data/raw/` and `data/processed/` are gitignored. `data/processed/environmental_annual.csv`
is the cached real GEE output and the actual H1 input — **if it is absent, notebook 05
and the audit script silently fall back to mock values** labelled as such. Check the
provenance line before trusting any H1 number in a fresh clone.

Cut from scope: ESA WorldCover (only two annual snapshots, 2020 and 2021 — cannot
support a 16-year trend) and JRC Global Surface Water (supported a hypothesis that
was cut). NDVI substitutes as the habitat/vegetation proxy.

---

## Repository layout

```
├── src/                     Reusable logic — every metric defined exactly once
│   ├── validation.py        The 8 validation rules; species list; Gujarat bbox
│   ├── load_and_clean.py    Stage 1 + the validation report
│   ├── observer_effort.py   Stage 2 — detection rate, observation density
│   ├── migration_metrics.py Stage 3 — arrival, departure, peak week, centroid
│   ├── environmental_data.py Stage 4 — ERA5 + MODIS via GEE, mock mode
│   └── statistics.py        Stage 5 — trend, correlation, figure/table builders
├── notebooks/               Narrative analysis (see caveat below)
├── scripts/
│   ├── audit_report.py      PASS/FAIL audit against the docs' acceptance criteria
│   └── test_gee_5points.py  Real-GEE unit sanity check at 5 Gujarat wetlands
├── tests/                   52 tests
├── paper/
│   ├── manuscript.md        The actual paper (IMRaD, complete)
│   ├── research_summary_layman.md  Plain-English walkthrough, Experiments 1–12
│   ├── figures/             fig1–fig6 (committed)
│   └── tables/              tableS1–S5 (committed)
├── outputs/                 figures/ and tables/ from notebook 06 (gitignored)
├── docs/                    15 specification documents — the source of truth
└── data/                    raw/ and processed/ (both gitignored)
```

Notebooks hold **no metric logic** — an acceptance test scans every code cell for
metric definitions and for direct `linregress(` / `pearsonr(` / `spearmanr(` calls.
The calculation lives in `src/`; the notebooks tell the story.

### Figures and tables

Notebook 06 writes Figures 1–8 and Tables 1–5 to `outputs/`:

| | |
|---|---|
| Figure 1 | Study area — Gujarat with six wetland hotspots marked |
| Figure 2 | Observer effort growth 2010–2025 (the ~303× curve) |
| Figure 3 | Raw vs confirmed arrival, three focal species |
| Figure 4 | Arrival trend, 12-panel small multiples |
| Figure 5 | Departure trend, 12-panel small multiples |
| Figure 6 | Temperature vs arrival (H1) |
| Figure 7 | Habitat guild comparison (H3) |
| Figure 8 | Geographic centroid shift, three focal species |
| Table 1 | Study species |
| Table 2 | Data sources |
| Table 3 | Data quality / validation summary |
| Table 4 | Migration metrics summary |
| Table 5 | Correlation results (H1) |

The paper carries its own six figures and five supporting tables in `paper/`.

---

## Testing

```bash
.venv/bin/python -m pytest tests/ -q     # 52 tests
```

- **`test_acceptance.py` (18)** — encodes the docs' acceptance criteria as executable
  checks. It parses `src/*.py` with `ast` and the notebooks with `json` to assert
  structural properties: every metric has exactly one implementation, the confirmation
  threshold is defined once, every metric function cites its doc section, every
  validation rule logs a count, notebooks contain no metric logic, the dependency set
  is exactly the specified minimum, and the README carries the AI and mentor disclosure.
- **`test_metrics.py` (15)** — hand-computed tiny inputs for Stages 2–3, including
  tie-breaking, weighted centroids, and the low-confidence boundary cases.
- **`test_statistics.py` (12)** — trend and correlation behaviour, α, and the
  effort-confound diagnostic.
- **`test_environmental.py` (7)** — the unit conversions (the known silent bugs) and
  mock-mode tagging. No GEE calls.

The acceptance suite reads the real gitignored `data/raw/` files, so it needs the
~60 MB extract present to run.

---

## Known gaps

Stated plainly, because a repository that hides its incompleteness is worse than one
that documents it.

- **`notebooks/01`–`04` are empty stubs** (72 bytes, zero cells). Stages 1–4 exist
  only in `src/`, and notebooks 05 and 06 re-run them internally. "Run the notebooks
  in order 01 → 06" does not work; run 05 and 06.
- **`paper/make_paper_figures.py` is a stub** — four `print()` statements, no plotting
  code. The committed `paper/figures/` and `paper/tables/` **cannot be regenerated
  from it**, which contradicts the manuscript's reproducibility claim.
- **Figure 9 (Dalmatian Pelican case study) and Table 6 (Hypothesis Evaluation) are
  not implemented.** The audit script will always report them missing.
- **The per-observation environmental join is still mock.** Only the annual H1 table
  is real GEE data. The join makes two blocking GEE round-trips per observation with
  no batching or caching, which is impractical at eBird scale; it needs
  `ee.FeatureCollection` bulk sampling before it can run for real.
- **`src/statistics.py` shadows the standard-library `statistics` module.** Safe only
  because all intra-package imports are relative.
- **`build_data_quality_table` drops the observations Rule 7 count** — the checklist
  and observation frames use different Rule 7 labels, so that cell renders empty.
- **The peak-week frame comparison filters asymmetrically** — the migration-frame side
  sets `low_confidence = False` unconditionally while the calendar side is filtered.
- **GEE exceptions are swallowed silently** in the ERA5 and NDVI point lookups, so an
  auth or quota failure is indistinguishable from genuinely missing data.
- `paper/birdsense_paper.md` is an empty placeholder; `paper/manuscript.md` is the real paper.
- No SQLite database is built. The schema in `docs/07` is specified but all
  persistence is flat CSV — which the doc explicitly permits at this scale.

### Assumptions still awaiting sign-off

1. **Habitat guild assignment** for H3 — particularly Bar-headed Goose (uses both
   lakes and grasslands) and Greylag Goose (wetland-associated but grazes farmland).
2. **The N=2 confirmation threshold**, inherited as a working default and never
   reviewed against published phenology methodology.
3. **The Nov–Feb winter window**, applied uniformly and not verified against each
   species' actual residence period.
4. **The ≥20-checklist site-level sample-size threshold**, identified post hoc from
   the data rather than pre-registered — disclosed as such in the manuscript and
   here, not treated as a fixed standard.

### Limitations to carry into any write-up

Citizen-science observer bias is only partially correctable — that is the paper's
subject, not a footnote. Coverage is uneven across Gujarat's districts. ERA5's
~25–30 km grid is a regional average, not wetland microclimate. NDVI reflects
vegetation, not urbanization directly. No multiple-comparison correction was applied
across the 12 species. **Correlation does not imply causation** — the analysis uses
"associated with" and "consistent with" throughout, never "causes" or "proves."

---

## Documentation

`docs/` is the **source of truth**. Where code and docs disagree, the docs win, and
`00_PROJECT_CHARTER.md` wins over the rest.

| Doc | Purpose |
|---|---|
| `00_PROJECT_CHARTER.md` | Top-level definition; wins all conflicts |
| `01_RESEARCH_METHODOLOGY.md` | Study design and workflow |
| `02_METRICS_METHODOLOGY.md` | Every metric: definition, formula, threshold |
| `03_ENVIRONMENTAL_FRAMEWORK.md` | Temperature, rainfall, NDVI — why and how |
| `04_STATISTICAL_ANALYSIS_PLAN.md` | Correlation, trend, hypothesis testing |
| `05_DATA_VALIDATION_PLAN.md` | Cleaning rules, exclusions, sanity checks |
| `06_DATA_SOURCES.md` | eBird, ERA5, MODIS access details |
| `07_DATABASE_SCHEMA.md` | SQLite schema (optional at this scale) |
| `08_FIGURE_TABLE_PLAN.md` | Every figure and table required |
| `09_ETL_AND_ANALYSIS_ENGINE.md` | Algorithms and pipeline steps |
| `10_PAPER_OUTLINE.md` | Section-by-section paper structure |
| `11_CODE_STRUCTURE.md` | Folder layout, module responsibilities |
| `12_AI_AND_MENTOR_DISCLOSURE.md` | Honest-authorship framing |
| `13_PROJECT_TIMELINE.md` | Development phases |
| `14_SCOPE_AND_ASSUMPTIONS.md` | What changed from v1; open judgment calls |

---

## AI & mentor disclosure

This project's implementation used **AI-assisted coding (Claude, by Anthropic)** for
writing and debugging the Python data pipeline and statistical analysis code, guided
throughout by the researcher's own research design decisions. Technical mentorship was
provided by data-science and analytics mentors. The research question, hypotheses,
species and variable selection, and interpretation of results were the researcher's
own, informed by personal eBird contribution and field experience in Gujarat.

The AI served as an implementation and debugging tool, not as a source of scientific
judgement. See `docs/12_AI_AND_MENTOR_DISCLOSURE.md` for the full statement.

---

## Acknowledgements

The eBird programme and its thousands of Gujarat contributors, whose collective effort
— the very subject of this analysis — makes work like this possible.

---

## License

This project is licensed under the MIT License — see LICENSE for the full text. In short: anyone may use, copy, modify, and distribute this code (including commercially), provided the original copyright notice is retained; the software is provided "as is," without warranty. The underlying eBird, ERA5 and MODIS datasets carry their own separate terms of use and are not covered by this license.
