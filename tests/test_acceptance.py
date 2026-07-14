"""Acceptance tests — encode the docs' "Acceptance Criteria" as automated checks.

Each test cites the doc whose acceptance criterion it enforces. Criteria that
cannot be automated (e.g. "matches the researcher's field experience") are listed
in scripts/audit_report.py's manual checklist, not here.
"""

import ast
import glob
import json
import os
from collections import Counter

import pandas as pd
import pytest

from src import load_and_clean, observer_effort, migration_metrics
from src import environmental_data as ENV
from src import statistics as S
from src import validation as V
from src.migration_metrics import CONFIRMATION_COUNT

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_DIR = os.path.join(REPO_ROOT, "src")
RAW_DIR = os.path.join(REPO_ROOT, "data", "raw")


# --------------------------------------------------------------------------- #
# Shared pipeline fixture (module scope) — runs the pipeline on the REAL eBird
# data in data/raw.
# --------------------------------------------------------------------------- #

@pytest.fixture(scope="module")
def pipeline():
    s1 = load_and_clean.run_stage1(RAW_DIR)
    metrics = migration_metrics.compute_migration_metrics(
        s1.clean_observations, s1.clean_checklists)
    effort = observer_effort.compute_observer_effort(
        s1.clean_observations, s1.clean_checklists)
    annual = ENV.build_annual_environmental(mock=True)
    return {"s1": s1, "metrics": metrics, "effort": effort, "annual": annual}


def _src_defs():
    """Counter of top-level function names defined across src/*.py."""
    counts = Counter()
    for path in glob.glob(os.path.join(SRC_DIR, "*.py")):
        tree = ast.parse(open(path).read())
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                counts[node.name] += 1
    return counts


# --------------------------------------------------------------------------- #
# 04_STATISTICAL_ANALYSIS_PLAN.md — r in [-1,1], p in [0,1], number + p-value
# --------------------------------------------------------------------------- #

def test_correlation_r_and_p_in_range(pipeline):
    """04 acceptance: every reported statistic has a number AND a p-value; r and
    p must be valid (r in [-1,1], p in [0,1])."""
    corr = S.build_correlation_table(pipeline["metrics"], pipeline["annual"])
    r = corr["pearson_r"].dropna()
    p = corr["p_value"].dropna()
    rho = corr["spearman_rho"].dropna()
    assert ((r >= -1) & (r <= 1)).all()
    assert ((p >= 0) & (p <= 1)).all()
    assert ((rho >= -1) & (rho <= 1)).all()
    # Never a number without its p-value: r present <=> p present, per species.
    both = corr[["pearson_r", "p_value"]].notna()
    assert (both["pearson_r"] == both["p_value"]).all()


def test_trend_stats_in_range(pipeline):
    """04 acceptance: trend R^2 in [0,1], p in [0,1]."""
    for col in ("first_arrival", "last_departure"):
        tr = S.species_metric_trend(pipeline["metrics"], col)
        r2 = tr["r_squared"].dropna()
        p = tr["p_value"].dropna()
        assert ((r2 >= 0) & (r2 <= 1)).all()
        assert ((p >= 0) & (p <= 1)).all()
        assert (tr["slope"].notna() == tr["p_value"].notna()).all()  # number + p


def test_no_forbidden_statistical_methods():
    """04 "What Is Explicitly NOT Done": no multiple regression / ML libraries."""
    forbidden = ("statsmodels", "sklearn", "scikit", "torch", "tensorflow")
    for path in glob.glob(os.path.join(SRC_DIR, "*.py")):
        text = open(path).read().lower()
        for name in forbidden:
            assert name not in text, f"{name} imported in {os.path.basename(path)}"


# --------------------------------------------------------------------------- #
# 05_DATA_VALIDATION_PLAN.md — every rule logs a count (no silent drops)
# --------------------------------------------------------------------------- #

def test_every_validation_rule_logs_a_count(pipeline):
    """05 acceptance: every exclusion rule is logged with a count, not silent."""
    s1 = pipeline["s1"]
    for report in (s1.checklists_report, s1.observations_report):
        assert report.drops, "no rule drops logged"
        for label, count in report.drops.items():
            assert isinstance(count, int), f"{label} count not an int"
    # The six drop-rules of Stage 1 are all represented on the observations frame.
    for rule in ("Rule 1", "Rule 2", "Rule 5", "Rule 6", "Rule 7", "Rule 8"):
        assert any(rule in k for k in s1.observations_report.drops), f"{rule} missing"


# --------------------------------------------------------------------------- #
# 02_METRICS_METHODOLOGY.md — raw peak distinct, one implementation, determinism
# --------------------------------------------------------------------------- #

def test_peak_week_and_raw_peak_week_not_all_identical(pipeline):
    """02 sec 3: raw_peak_week is a distinct diagnostic from the detection-rate
    peak_week -- they must not be identical across all species-years."""
    m = pipeline["metrics"].dropna(subset=["peak_week", "raw_peak_week"])
    assert (m["peak_week"] != m["raw_peak_week"]).any()


def test_each_metric_has_exactly_one_implementation():
    """02 acceptance ("never recalculated a different way") / 09 acceptance
    ("no metric computed more than one way"): each metric function is defined
    exactly once across src/."""
    defs = _src_defs()
    for fn in ("confirmed_arrival", "confirmed_departure", "peak_week",
               "wintering_duration", "centroid", "detection_rate",
               "observation_density", "linear_trend", "correlation"):
        assert defs.get(fn, 0) == 1, f"{fn} defined {defs.get(fn,0)} times (want 1)"


def test_confirmation_count_defined_once():
    """02 sec 1: N=2 confirmation threshold is a single named constant."""
    hits = 0
    for path in glob.glob(os.path.join(SRC_DIR, "*.py")):
        for line in open(path):
            if line.lstrip().startswith("CONFIRMATION_COUNT ="):
                hits += 1
    assert hits == 1 and CONFIRMATION_COUNT == 2


def test_metrics_are_deterministic(pipeline):
    """02 acceptance: same output on the same input, every time."""
    s1 = pipeline["s1"]
    again = migration_metrics.compute_migration_metrics(
        s1.clean_observations, s1.clean_checklists)
    pd.testing.assert_frame_equal(pipeline["metrics"], again)


def test_metric_functions_cite_doc_section():
    """02 acceptance / 09 acceptance: every metric function's docstring references
    the corresponding 02_METRICS_METHODOLOGY.md section. (The Stage-3 orchestrator
    cites 09 instead; only the metric functions themselves are checked here.)"""
    metric_fns = {"confirmed_arrival", "confirmed_departure", "peak_week",
                  "wintering_duration", "centroid"}
    tree = ast.parse(open(os.path.join(SRC_DIR, "migration_metrics.py")).read())
    seen = set()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in metric_fns:
            doc = ast.get_docstring(node) or ""
            assert "02_METRICS_METHODOLOGY.md" in doc, f"{node.name} lacks citation"
            seen.add(node.name)
    assert seen == metric_fns, f"missing metric functions: {metric_fns - seen}"


# --------------------------------------------------------------------------- #
# 02 sec 1 — low_confidence whenever a species-year has fewer than 2 obs
# --------------------------------------------------------------------------- #

def test_low_confidence_when_fewer_than_two_observations(pipeline):
    """02 sec 1: any species-year with fewer than 2 observations is low_confidence
    (this project extends the flag to < 3; the doc floor of < 2 must hold)."""
    m = pipeline["metrics"]
    assert m.loc[m["n_obs"] < 2, "low_confidence"].all()
    # And a well-sampled year (>= 3 obs) is not flagged.
    assert not m.loc[m["n_obs"] >= 3, "low_confidence"].any()


# --------------------------------------------------------------------------- #
# 09 / 11 — pipeline runs on data/raw and reproduces outputs
# --------------------------------------------------------------------------- #

def test_pipeline_reproducible_on_raw():
    """09 acceptance: running the pipeline on raw data reproduces every output
    with no manual intervention; 11 acceptance: reproducible from data/raw."""
    a = load_and_clean.run_stage1(RAW_DIR)
    b = load_and_clean.run_stage1(RAW_DIR)
    assert a.clean_observations.shape == b.clean_observations.shape
    ma = migration_metrics.compute_migration_metrics(a.clean_observations, a.clean_checklists)
    mb = migration_metrics.compute_migration_metrics(b.clean_observations, b.clean_checklists)
    pd.testing.assert_frame_equal(ma, mb)


# --------------------------------------------------------------------------- #
# 03_ENVIRONMENTAL_FRAMEWORK.md — coverage reported, obs never dropped
# --------------------------------------------------------------------------- #

def test_environmental_coverage_reported_and_no_obs_dropped(pipeline):
    """03 acceptance: NDVI coverage reported as a %, and observations are never
    dropped (missing env -> NULL + log, only the field is lost)."""
    # Sample the (large, real) observations frame; this checks the mechanism.
    sample = pipeline["s1"].clean_observations.head(500)
    matched, log = ENV.match_environmental_to_observations(sample, mock=True)
    assert len(matched) == len(sample)  # never dropped
    rep = ENV.coverage_report(matched)
    assert rep["ndvi"]["pct"] is not None                          # coverage reported
    assert "ndvi" in log and "null_count" in log["ndvi"]           # NULLs logged


# --------------------------------------------------------------------------- #
# 07_DATABASE_SCHEMA.md — outputs carry the schema's columns
# --------------------------------------------------------------------------- #

def test_migration_metrics_has_schema_columns(pipeline):
    """07 acceptance: the schema can be populated from the cleaned outputs -- the
    migration_metrics output carries every migration_metrics column."""
    expected = {"first_arrival", "raw_first_arrival", "last_departure",
                "raw_last_departure", "peak_week", "peak_detection_rate",
                "raw_peak_week", "wintering_duration_days", "centroid_latitude",
                "centroid_longitude", "low_confidence"}
    assert expected.issubset(set(pipeline["metrics"].columns))


# --------------------------------------------------------------------------- #
# 11_CODE_STRUCTURE.md — requirements = Minimum Dependencies; no metric logic
#                        in notebooks
# --------------------------------------------------------------------------- #

def test_requirements_is_exactly_minimum_dependencies():
    """11 "Minimum Dependencies" (and 14: no production infra deps)."""
    expected = {"pandas", "numpy", "scipy", "matplotlib", "seaborn",
                "earthengine-api", "geopandas", "folium", "jupyter"}
    got = set()
    for line in open(os.path.join(REPO_ROOT, "requirements.txt")):
        line = line.split("#", 1)[0].strip()
        if line:
            got.add(line.split()[0].lower())
    assert got == expected
    forbidden = {"fastapi", "sqlalchemy", "next.js", "docker", "flask", "django"}
    assert not (got & forbidden)


def test_notebooks_contain_no_metric_logic():
    """11 acceptance: no notebook cell contains a metric calculation that
    duplicates src/ logic (metrics/stats are imported, not re-defined)."""
    banned_defs = ("def confirmed_arrival", "def confirmed_departure",
                   "def peak_week", "def centroid", "def linear_trend",
                   "def correlation", "def detection_rate")
    banned_calls = ("linregress(", "pearsonr(", "spearmanr(")
    nbs = glob.glob(os.path.join(REPO_ROOT, "notebooks", "*.ipynb"))
    assert nbs, "no notebooks found"
    for path in nbs:
        nb = json.load(open(path))
        for cell in nb.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            src = "".join(cell.get("source", []))
            for tok in banned_defs + banned_calls:
                assert tok not in src, f"{os.path.basename(path)} contains '{tok}'"


# --------------------------------------------------------------------------- #
# 01_RESEARCH_METHODOLOGY.md — 12 species, 2010-2025
# --------------------------------------------------------------------------- #

def test_twelve_study_species_and_study_period():
    """01: 12 study species; study period 2010-2025 (16 years)."""
    assert len(V.STUDY_SPECIES) == 12
    assert len(set(V.STUDY_SPECIES_SCIENTIFIC)) == 12
    assert (V.STUDY_PERIOD_START, V.STUDY_PERIOD_END) == (2010, 2025)


def test_all_twelve_species_present_in_metrics(pipeline):
    """01: all 12 study species are analysed. (On the real May-2026 data the
    Dalmatian Pelican is well-sampled, unlike doc 01's sparse-case-study working
    assumption -- a finding to raise with the researcher, not an error.)"""
    assert set(pipeline["metrics"]["species"]) == set(V.STUDY_SPECIES_SCIENTIFIC)


# --------------------------------------------------------------------------- #
# 00 / 12 — AI & mentor disclosure present in the README
# --------------------------------------------------------------------------- #

def test_readme_includes_ai_and_mentor_disclosure():
    """00 Definition of Done / 12 Practical Checklist: the AI-assisted
    implementation and mentor support are disclosed in the README."""
    readme = open(os.path.join(REPO_ROOT, "README.md")).read().lower()
    assert "ai-assisted" in readme or "ai & mentor" in readme
    assert "mentor" in readme and "claude" in readme
