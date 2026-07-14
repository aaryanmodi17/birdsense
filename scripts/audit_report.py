"""One-screen PASS/FAIL audit of the BirdSense pipeline against the docs'
Acceptance Criteria. Runs the full pipeline on data/raw (synthetic) and reports:
validation drop-counts, environmental coverage %, low_confidence count, any r/p
out of range, and whether every Figure/Table in 08_FIGURE_TABLE_PLAN.md exists.

Each automated check cites the doc criterion it enforces. Criteria that cannot be
automated are printed as a manual checklist at the end.

Run:  .venv/bin/python scripts/audit_report.py
"""

import glob
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import pandas as pd  # noqa: E402

from src import load_and_clean, observer_effort, migration_metrics  # noqa: E402
from src import environmental_data as ENV  # noqa: E402
from src import statistics as S  # noqa: E402

FIG_DIR = os.path.join(REPO_ROOT, "outputs", "figures")
TAB_DIR = os.path.join(REPO_ROOT, "outputs", "tables")

_results = []  # (status, doc, message)


def record(status, doc, message):
    _results.append((status, doc, message))
    icon = {"PASS": "PASS", "FAIL": "FAIL", "INFO": "INFO"}[status]
    print(f"  [{icon}] ({doc}) {message}")


def main():
    bar = "=" * 78
    print(bar)
    print(" BirdSense PIPELINE AUDIT")
    print(" Bird data: REAL eBird EBD v1.16 (IN-GJ, May 2026) | Environment: MOCK (no GEE)")
    print(bar)

    # ----- run the full pipeline on data/raw -----
    s1 = load_and_clean.run_stage1()
    metrics = migration_metrics.compute_migration_metrics(
        s1.clean_observations, s1.clean_checklists)
    S.build_migration_summary(metrics)  # exercise trend builders
    annual = ENV.build_annual_environmental(mock=True)
    matched, env_log = ENV.match_environmental_to_observations(
        s1.clean_observations, mock=True)

    # ----- 1. Validation drop-counts (05_DATA_VALIDATION_PLAN.md) -----
    print("\n VALIDATION (05_DATA_VALIDATION_PLAN.md: every rule logged w/ a count)")
    obs_drops = s1.observations_report.drops
    all_counted = all(isinstance(v, int) for v in obs_drops.values()) and bool(obs_drops)
    detail = ", ".join(f"{k.split('(')[0].strip()}={v}" for k, v in obs_drops.items())
    record("PASS" if all_counted else "FAIL", "05", f"obs drops: {detail}")
    record("INFO", "05",
           f"raw obs {s1.observations_report.initial_rows} -> usable "
           f"{s1.observations_report.final_rows}; "
           f"effort-eligible checklists {s1.effort['effort_eligible_checklists']}")

    # ----- 2. Environmental coverage % (03_ENVIRONMENTAL_FRAMEWORK.md) -----
    print("\n ENVIRONMENT (03_ENVIRONMENTAL_FRAMEWORK.md: coverage %, never drop obs)")
    rep = ENV.coverage_report(matched)
    never_dropped = len(matched) == len(s1.clean_observations)
    cov = " | ".join(f"{v}={rep[v]['pct']:.1f}%" for v in ("temperature", "rainfall", "ndvi"))
    record("PASS" if never_dropped else "FAIL", "03",
           f"obs {len(matched)} (none dropped); coverage {cov}")
    record("INFO", "03", f"NULL-and-log counts: "
           + ", ".join(f"{v}={env_log[v]['null_count']}" for v in ("temperature", "rainfall", "ndvi"))
           + "  [MOCK env values -- FAKE]")

    # ----- 3. low_confidence species-years (02_METRICS_METHODOLOGY.md sec 1) -----
    print("\n METRICS (02_METRICS_METHODOLOGY.md)")
    n_low = int(metrics["low_confidence"].sum())
    lt2 = metrics[metrics["n_obs"] < 2]
    ok_low = bool(lt2["low_confidence"].all())
    record("PASS" if ok_low else "FAIL", "02 sec 1",
           f"low_confidence set for all species-years with < 2 obs "
           f"({n_low}/{len(metrics)} species-years low_confidence)")
    m2 = metrics.dropna(subset=["peak_week", "raw_peak_week"])
    distinct = bool((m2["peak_week"] != m2["raw_peak_week"]).any())
    record("PASS" if distinct else "FAIL", "02 sec 3",
           f"peak_week vs raw_peak_week differ on "
           f"{int((m2['peak_week'] != m2['raw_peak_week']).sum())}/{len(m2)} rows")

    # ----- 4. r/p in range (04_STATISTICAL_ANALYSIS_PLAN.md) -----
    print("\n STATISTICS (04_STATISTICAL_ANALYSIS_PLAN.md: r in [-1,1], p in [0,1])")
    corr = S.build_correlation_table(metrics, annual)
    arr = S.species_metric_trend(metrics, "first_arrival")
    dep = S.species_metric_trend(metrics, "last_departure")
    bad = 0
    r = corr["pearson_r"].dropna()
    bad += int(((r < -1) | (r > 1)).sum())
    for tbl, col, lo, hi in [(corr, "p_value", 0, 1), (arr, "p_value", 0, 1),
                             (dep, "p_value", 0, 1), (arr, "r_squared", 0, 1),
                             (dep, "r_squared", 0, 1)]:
        v = tbl[col].dropna()
        bad += int(((v < lo) | (v > hi)).sum())
    record("PASS" if bad == 0 else "FAIL", "04",
           f"{len(r)} correlations + {len(arr)+len(dep)} trends checked; "
           f"{bad} statistic(s) out of range")

    # ----- 5. Figures/Tables produced (08_FIGURE_TABLE_PLAN.md) -----
    print("\n DELIVERABLES (08_FIGURE_TABLE_PLAN.md: every figure/table produced)")
    figs_present = [n for n in range(1, 10)
                    if glob.glob(os.path.join(FIG_DIR, f"figure_{n:02d}_*"))]
    tabs_present = [n for n in range(1, 7)
                    if glob.glob(os.path.join(TAB_DIR, f"table_{n:02d}_*"))]
    figs_missing = [n for n in range(1, 10) if n not in figs_present]
    tabs_missing = [n for n in range(1, 7) if n not in tabs_present]
    record("PASS" if not figs_missing else "FAIL", "08",
           f"Figures present {figs_present}; MISSING {figs_missing or 'none'}")
    record("PASS" if not tabs_missing else "FAIL", "08",
           f"Tables present {tabs_present}; MISSING {tabs_missing or 'none'}")
    if figs_missing or tabs_missing:
        record("INFO", "08", "run notebook 06_figures_and_tables.ipynb to (re)generate; "
               "Figure 9 & Table 6 are not yet implemented")

    # ----- summary -----
    n_pass = sum(1 for s, _, _ in _results if s == "PASS")
    n_fail = sum(1 for s, _, _ in _results if s == "FAIL")
    print("\n" + bar)
    print(f" AUTOMATED RESULT: {n_pass} PASS, {n_fail} FAIL "
          f"({sum(1 for s,_,_ in _results if s=='INFO')} info)")
    print(bar)

    # ----- manual checklist (criteria that cannot be automated) -----
    print("\n MANUAL CHECKLIST -- acceptance criteria that CANNOT be automated:")
    for doc, item in [
        ("05", "Computed metrics match the researcher's own field experience (sanity-check step)."),
        ("05", "Researcher can explain, for each rule, what would go wrong if skipped."),
        ("00/10", "Paper is written and follows 10_PAPER_OUTLINE.md's structure."),
        ("10", "Every paper section references a specific figure/table (not vague)."),
        ("10", "Table 6 (Hypothesis Evaluation) and the Conclusion agree; prose not overstated."),
        ("08", "Every figure has units, a legend, and a caption with data source + period."),
        ("00", "Dalmatian Pelican qualitative case study is written (Figure 9)."),
        ("00/04", "Each hypothesis H1-H3 has an honest stated conclusion in the paper."),
        ("04", "Effect sizes stated in real-world units (days/weeks), not just jargon."),
        ("07", "Every schema column has a documented source (raw / derived / GEE)."),
        ("12", "Disclosure included in the paper's Methods/Acknowledgments, not just README."),
        ("02", "GEE env values validated against reality (currently MOCK/FAKE -- run 5-point test)."),
    ]:
        print(f"   [ ] ({doc}) {item}")
    print(bar)
    return 0


if __name__ == "__main__":
    sys.exit(main())
