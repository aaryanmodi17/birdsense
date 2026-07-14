"""Stage 2: Observer Effort — implements 09_ETL_AND_ANALYSIS_ENGINE.md (Stage 2).

Computes, per species per year (2010-2025):
  - total_complete_checklists  (effort denominator)
  - observed_checklists        (complete checklists reporting the species)
  - detection_rate             (02_METRICS_METHODOLOGY.md sec 6, PRIMARY metric)
  - observation_density        (02_METRICS_METHODOLOGY.md sec 7, secondary)

The effort denominator uses ONLY complete, non-Incidental checklists. Rather than
re-deriving "complete" here (Validation Rules 3 & 4), this stage reuses the
`is_complete_for_effort` flag produced once in Stage 1 (src/load_and_clean.py) —
so completeness is never computed two different ways.
"""

import pandas as pd

from . import validation as V

SEI = "SAMPLING EVENT IDENTIFIER"
STUDY_YEARS = list(range(V.STUDY_PERIOD_START, V.STUDY_PERIOD_END + 1))


def detection_rate(observed_checklists, total_complete_checklists):
    """Detection Rate — 02_METRICS_METHODOLOGY.md sec 6:
    complete checklists reporting the species / total complete checklists.
    Returns None when there are no complete checklists (undefined)."""
    if not total_complete_checklists:
        return None
    return observed_checklists / total_complete_checklists


def observation_density(total_individuals, total_complete_checklists):
    """Observation Density — 02_METRICS_METHODOLOGY.md sec 7:
    total individuals recorded / total complete checklists.
    (Individuals are counted on complete checklists, consistent with the
    effort denominator.) Returns None when there are no complete checklists."""
    if not total_complete_checklists:
        return None
    return total_individuals / total_complete_checklists


def compute_observer_effort(observations, checklists,
                            species=V.STUDY_SPECIES_SCIENTIFIC, years=STUDY_YEARS):
    """Stage 2 over the full species x year grid (09_ETL_AND_ANALYSIS_ENGINE.md).

    `observations` and `checklists` are the cleaned Stage 1 frames carrying the
    `is_complete_for_effort` flag, `year`, and eBird columns. Returns one row per
    species-year (missing species-years yield 0 observed, detection_rate 0)."""
    complete_chk = checklists[checklists["is_complete_for_effort"].eq(True)]
    total_by_year = complete_chk.groupby("year")[SEI].nunique()

    obs_c = observations[observations["is_complete_for_effort"].eq(True)].copy()
    obs_c["_count"] = pd.to_numeric(obs_c["OBSERVATION COUNT"], errors="coerce")
    grp = obs_c.groupby(["SCIENTIFIC NAME", "year"])
    observed_by_sy = grp[SEI].nunique()
    individuals_by_sy = grp["_count"].sum(min_count=1)

    rows = []
    for sci in species:
        for year in years:
            total = int(total_by_year.get(year, 0))
            observed = int(observed_by_sy.get((sci, year), 0))
            individuals = individuals_by_sy.get((sci, year), 0.0)
            if pd.isna(individuals):
                individuals = 0.0
            rows.append({
                "species": sci,
                "year": year,
                "total_complete_checklists": total,
                "observed_checklists": observed,
                "detection_rate": detection_rate(observed, total),
                "observation_density": observation_density(float(individuals), total),
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from . import load_and_clean
    result = load_and_clean.run_stage1()
    effort = compute_observer_effort(result.clean_observations, result.clean_checklists)
    pd.set_option("display.max_rows", 200)
    pd.set_option("display.width", 160)
    print(effort.to_string(index=False))
