"""Stage 5: Trend and Correlation — implements 09_ETL_AND_ANALYSIS_ENGINE.md
(Stage 5) exactly as 04_STATISTICAL_ANALYSIS_PLAN.md specifies.

Core (04): simple linear trend (year -> metric) and Pearson correlation
(environment -> metric), with Spearman as a secondary non-linearity check.

NOT done, per 04's explicit exclusions: no multiple/multi-variable regression,
no multiple-comparison correction (e.g. Bonferroni), no residual diagnostics.

This module also holds the figure-/table-data BUILDERS so the notebooks contain
no metric logic (11_CODE_STRUCTURE.md): each builder consumes the cleaned Stage
1-4 frames and returns a ready-to-plot / ready-to-save object.
"""

import numpy as np
import pandas as pd
from scipy import stats

from . import validation as V
from .migration_metrics import CONFIRMATION_COUNT

# Single significance threshold, used everywhere — 04 "Hypothesis Testing".
ALPHA = 0.05

# |r| at/above this is called "strong", below is "weak" (when significant).
# A reporting convention for 01_RESEARCH_METHODOLOGY.md's interpretation bands;
# it is NOT a second significance threshold.
STRONG_CORRELATION_ABS_R = 0.5

_SCI_TO_COMMON = {s["scientific"]: s["common"] for s in V.STUDY_SPECIES}
_SCI_TO_HABITAT = {s["scientific"]: s["habitat"] for s in V.STUDY_SPECIES}


def common_name(scientific):
    """Common name for a study-species scientific name (01_RESEARCH_METHODOLOGY.md)."""
    return _SCI_TO_COMMON.get(scientific, scientific)


def habitat_of(scientific):
    """Habitat category ('wetland' | 'grassland_dryland') for the H3 grouping."""
    return _SCI_TO_HABITAT.get(scientific)


# --------------------------------------------------------------------------- #
# Core statistics (04 Trend + Correlation)
# --------------------------------------------------------------------------- #

def linear_trend(years, values):
    """Simple linear regression year -> metric — 04 "Trend Analysis" / 09 Stage 5.
    Returns slope (units/year), intercept, r_squared, p_value, n. Needs at least
    2 points with variation in x; otherwise the stats are None."""
    x = pd.to_numeric(pd.Series(list(years)), errors="coerce")
    y = pd.to_numeric(pd.Series(list(values)), errors="coerce")
    mask = x.notna() & y.notna()
    x, y = x[mask], y[mask]
    n = int(len(x))
    if n < 2 or x.nunique() < 2:
        return {"slope": None, "intercept": None, "r_squared": None,
                "p_value": None, "n": n}
    res = stats.linregress(x, y)
    return {"slope": float(res.slope), "intercept": float(res.intercept),
            "r_squared": float(res.rvalue ** 2), "p_value": float(res.pvalue), "n": n}


def correlation(x, y):
    """Pearson correlation — 04 "Correlation Analysis" / 09 Stage 5.
    Returns r, p_value, n. None when < 2 points or no variation."""
    xv, yv, n = _aligned(x, y)
    if n < 2 or xv.nunique() < 2 or yv.nunique() < 2:
        return {"r": None, "p_value": None, "n": n}
    r, p = stats.pearsonr(xv, yv)
    return {"r": float(r), "p_value": float(p), "n": n}


def spearman_correlation(x, y):
    """Spearman rank correlation — 04: secondary check to report when a scatter
    looks clearly non-linear. Returns rho, p_value, n."""
    xv, yv, n = _aligned(x, y)
    if n < 2 or xv.nunique() < 2 or yv.nunique() < 2:
        return {"rho": None, "p_value": None, "n": n}
    rho, p = stats.spearmanr(xv, yv)
    return {"rho": float(rho), "p_value": float(p), "n": n}


def is_significant(p_value):
    """Significant at alpha = 0.05 (04)."""
    return p_value is not None and p_value < ALPHA


def interpret_correlation(r, p_value):
    """Map an (r, p) pair to 01_RESEARCH_METHODOLOGY.md's evidence bands:
    'none' (not significant), 'weak' (significant, small effect), 'strong'
    (significant, |r| >= STRONG_CORRELATION_ABS_R)."""
    if not is_significant(p_value) or r is None:
        return "none"
    return "strong" if abs(r) >= STRONG_CORRELATION_ABS_R else "weak"


def _aligned(x, y):
    xs = pd.to_numeric(pd.Series(list(x)), errors="coerce").reset_index(drop=True)
    ys = pd.to_numeric(pd.Series(list(y)), errors="coerce").reset_index(drop=True)
    mask = xs.notna() & ys.notna()
    return xs[mask], ys[mask], int(mask.sum())


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #

def date_to_day_of_year(dates):
    """Numeric encoding of a date-valued metric for regression: day-of-year
    (1-366) within the calendar year. This matches the calendar-year framing of
    the arrival/departure metrics (02_METRICS_METHODOLOGY.md); slopes are then in
    days/year. Returns a float Series (NaN for missing). Preserves the input
    index so the result can be assigned straight back onto a DataFrame column."""
    s = dates if isinstance(dates, pd.Series) else pd.Series(list(dates))
    return pd.to_datetime(s, errors="coerce").dt.dayofyear


def _doy_to_label(doy):
    """Format a mean day-of-year back to a 'DD Mon' label (non-leap reference)."""
    if doy is None or pd.isna(doy):
        return None
    return (pd.Timestamp("2001-01-01") + pd.Timedelta(days=float(doy) - 1)).strftime("%d %b")


def _confident(metrics_df):
    """Species-years usable for trends: exclude low_confidence (02 sec 1: never
    include low_confidence years as equal-weight points in a trend line)."""
    return metrics_df[~metrics_df["low_confidence"].astype(bool)].copy()


def _species_order(metrics_df):
    present = set(metrics_df["species"])
    return [s for s in V.STUDY_SPECIES_SCIENTIFIC if s in present]


# --------------------------------------------------------------------------- #
# Trend / correlation builders (per species; H2, H3, H1)
# --------------------------------------------------------------------------- #

def species_metric_trend(metrics_df, metric_col, is_date=True):
    """Per-species linear trend of `metric_col` vs year (H2). Date metrics are
    encoded as day-of-year. Excludes low_confidence years. Returns a DataFrame
    with slope/intercept/r_squared/p_value/n per species."""
    rows = []
    conf = _confident(metrics_df)
    for sci in _species_order(metrics_df):
        g = conf[conf["species"] == sci]
        values = date_to_day_of_year(g[metric_col]) if is_date else pd.to_numeric(
            g[metric_col], errors="coerce")
        rows.append({"species": sci, "common": _SCI_TO_COMMON.get(sci, sci),
                     "habitat": _SCI_TO_HABITAT.get(sci), **linear_trend(g["year"], values)})
    return pd.DataFrame(rows)


def build_migration_summary(metrics_df):
    """Table 4 — per species: mean arrival date + arrival trend (slope, p) and
    mean departure date + departure trend (08_FIGURE_TABLE_PLAN.md)."""
    conf = _confident(metrics_df)
    arr = species_metric_trend(metrics_df, "first_arrival").set_index("species")
    dep = species_metric_trend(metrics_df, "last_departure").set_index("species")
    rows = []
    for sci in _species_order(metrics_df):
        g = conf[conf["species"] == sci]
        mean_arr = date_to_day_of_year(g["first_arrival"]).mean()
        mean_dep = date_to_day_of_year(g["last_departure"]).mean()
        rows.append({
            "common_name": _SCI_TO_COMMON.get(sci, sci),
            "scientific_name": sci,
            "mean_arrival_date": _doy_to_label(mean_arr),
            "arrival_slope_days_per_year": _round(arr.loc[sci, "slope"]),
            "arrival_p_value": _round(arr.loc[sci, "p_value"], 4),
            "mean_departure_date": _doy_to_label(mean_dep),
            "departure_slope_days_per_year": _round(dep.loc[sci, "slope"]),
            "departure_p_value": _round(dep.loc[sci, "p_value"], 4),
        })
    return pd.DataFrame(rows)


def build_temperature_correlation(metrics_df, annual_env, metric_col="first_arrival",
                                  is_date=True):
    """H1 (04) — per species Pearson correlation of winter mean temperature vs a
    timing metric. `metric_col` is 'first_arrival' (date -> day-of-year;
    effort-sensitive) or 'peak_week' (numeric ISO week, detection-rate-weighted ->
    effort-robust). Spearman is the secondary check. Excludes low_confidence
    years. One implementation for both metrics."""
    conf = _confident(metrics_df)
    temp_by_year = annual_env.set_index("year")["mean_winter_temperature"]
    rows = []
    for sci in _species_order(metrics_df):
        g = conf[conf["species"] == sci].copy()
        g["_metric"] = (date_to_day_of_year(g[metric_col]) if is_date
                        else pd.to_numeric(g[metric_col], errors="coerce"))
        g["_temp"] = g["year"].map(temp_by_year)
        pear = correlation(g["_temp"], g["_metric"])
        spear = spearman_correlation(g["_temp"], g["_metric"])
        rows.append({
            "common_name": _SCI_TO_COMMON.get(sci, sci),
            "scientific_name": sci,
            "n_years": pear["n"],
            "pearson_r": _round(pear["r"], 3),
            "p_value": _round(pear["p_value"], 4),
            "spearman_rho": _round(spear["rho"], 3),
            "interpretation": interpret_correlation(pear["r"], pear["p_value"]),
        })
    return pd.DataFrame(rows)


def build_correlation_table(metrics_df, annual_env):
    """Table 5 (H1) — temperature vs confirmed arrival (day-of-year). Delegates to
    build_temperature_correlation so the correlation is defined exactly once."""
    return build_temperature_correlation(metrics_df, annual_env, "first_arrival", True)


# --------------------------------------------------------------------------- #
# Effort-robustness comparison — quantify how much of H1/H2 is observer artifact
# (04: correlation + linear trend only; no multiple regression)
# --------------------------------------------------------------------------- #

def effort_vs_arrival_correlation(metrics_df, effort_df):
    """Effort-confound DIAGNOSTIC (04 correlation, not a hypothesis test): per
    species, Pearson r between annual observer effort (total complete checklists)
    and confirmed first-arrival day-of-year. A strong correlation means the
    arrival metric tracks effort, not phenology."""
    conf = _confident(metrics_df)
    eff = effort_df[["species", "year", "total_complete_checklists"]]
    rows = []
    for sci in _species_order(metrics_df):
        g = conf[conf["species"] == sci].merge(eff, on=["species", "year"], how="left")
        arrival = date_to_day_of_year(g["first_arrival"])
        c = correlation(g["total_complete_checklists"], arrival)
        rows.append({
            "common_name": _SCI_TO_COMMON.get(sci, sci),
            "scientific_name": sci,
            "n_years": c["n"],
            "effort_vs_arrival_r": _round(c["r"], 3),
            "p_value": _round(c["p_value"], 4),
            "interpretation": interpret_correlation(c["r"], c["p_value"]),
        })
    return pd.DataFrame(rows)


def build_h1_comparison(metrics_df, annual_env):
    """H1 side by side: temperature-vs-arrival (effort-sensitive) next to
    temperature-vs-peak-week (detection-rate-weighted, effort-robust), per species."""
    arr = build_temperature_correlation(metrics_df, annual_env, "first_arrival", True)
    pk = build_temperature_correlation(metrics_df, annual_env, "peak_week", False)
    out = arr[["common_name", "scientific_name", "pearson_r", "p_value", "interpretation"]].rename(
        columns={"pearson_r": "temp_vs_arrival_r", "p_value": "arrival_p",
                 "interpretation": "arrival_evidence"})
    out = out.merge(
        pk[["scientific_name", "pearson_r", "p_value", "interpretation"]].rename(
            columns={"pearson_r": "temp_vs_peakweek_r", "p_value": "peakweek_p",
                     "interpretation": "peakweek_evidence"}),
        on="scientific_name")
    return out


def build_h2_comparison(metrics_df):
    """H2 side by side: confirmed-arrival trend (effort-sensitive) next to
    detection-rate-weighted peak-week trend (effort-robust), per species."""
    arr = species_metric_trend(metrics_df, "first_arrival", is_date=True)
    pk = species_metric_trend(metrics_df, "peak_week", is_date=False)
    out = arr[["common", "species", "slope", "p_value"]].rename(
        columns={"common": "common_name", "species": "scientific_name",
                 "slope": "arrival_slope_days_per_yr", "p_value": "arrival_p"})
    out = out.merge(
        pk[["species", "slope", "p_value"]].rename(
            columns={"species": "scientific_name",
                     "slope": "peakweek_slope_weeks_per_yr", "p_value": "peakweek_p"}),
        on="scientific_name")
    for c in ("arrival_slope_days_per_yr", "peakweek_slope_weeks_per_yr"):
        out[c] = out[c].apply(lambda v: _round(v, 3))
    for c in ("arrival_p", "peakweek_p"):
        out[c] = out[c].apply(lambda v: _round(v, 4))
    return out


def habitat_category_trends(metrics_df):
    """H3 / Figure 7 — annual mean confirmed-arrival day-of-year for each habitat
    category (wetland vs grassland/dryland), plus each category's linear trend.
    Returns (per_year_df, trends_dict)."""
    conf = _confident(metrics_df).copy()
    conf["arrival_doy"] = date_to_day_of_year(conf["first_arrival"])
    conf["habitat"] = conf["species"].map(_SCI_TO_HABITAT)
    per_year = (conf.dropna(subset=["arrival_doy"])
                .groupby(["habitat", "year"])["arrival_doy"].mean().reset_index())
    trends = {}
    for habitat, g in per_year.groupby("habitat"):
        trends[habitat] = linear_trend(g["year"], g["arrival_doy"])
    return per_year, trends


# --------------------------------------------------------------------------- #
# Descriptive / reference table builders (Tables 1-3)
# --------------------------------------------------------------------------- #

def build_species_table(metrics_df):
    """Table 1 — common name, scientific name, habitat category, and total
    confirmed species-years (a confirmed arrival needs >= CONFIRMATION_COUNT
    independent observations)."""
    confirmed_years = (metrics_df[metrics_df["n_obs"] >= CONFIRMATION_COUNT]
                       .groupby("species")["year"].nunique())
    rows = []
    for s in V.STUDY_SPECIES:
        rows.append({
            "common_name": s["common"],
            "scientific_name": s["scientific"],
            "habitat_category": s["habitat"],
            "analysis_type": s["analysis"],
            "confirmed_species_years_out_of_16": int(confirmed_years.get(s["scientific"], 0)),
        })
    return pd.DataFrame(rows)


def build_data_sources_table():
    """Table 2 — static reference from 06_DATA_SOURCES.md (all cost $0)."""
    return pd.DataFrame([
        {"dataset": "eBird Basic Dataset (sampling + observations), Gujarat",
         "provider": "Cornell Lab of Ornithology", "years_covered": "2010-2025",
         "resolution": "checklist-level", "cost_usd": 0},
        {"dataset": "ERA5 Reanalysis (temperature, rainfall)",
         "provider": "ECMWF via Google Earth Engine", "years_covered": "2010-2025",
         "resolution": "~25-30 km, daily", "cost_usd": 0},
        {"dataset": "MODIS MOD13Q1 (NDVI)",
         "provider": "NASA via Google Earth Engine", "years_covered": "2010-2025",
         "resolution": "250 m, 16-day", "cost_usd": 0},
    ])


def build_data_quality_table(stage1_result):
    """Table 3 — checklists dropped by validation rule, final usable counts
    (08: pulls directly from the Stage 1 Validation Report)."""
    chk = stage1_result.checklists_report
    obs = stage1_result.observations_report
    rows = [{"stage": "raw", "rule": "loaded",
             "checklists": chk.initial_rows, "observations": obs.initial_rows}]
    for label in chk.drops:
        rows.append({"stage": "dropped", "rule": label,
                     "checklists": chk.drops.get(label, 0),
                     "observations": obs.drops.get(label, "")})
    # Rule 6 (non-study species) applies to observations only.
    if "Rule 6 (non-study species)" in obs.drops:
        rows.append({"stage": "dropped", "rule": "Rule 6 (non-study species)",
                     "checklists": "", "observations": obs.drops["Rule 6 (non-study species)"]})
    rows.append({"stage": "final", "rule": "usable after cleaning",
                 "checklists": chk.final_rows, "observations": obs.final_rows})
    rows.append({"stage": "effort", "rule": "effort-eligible complete checklists",
                 "checklists": stage1_result.effort["effort_eligible_checklists"],
                 "observations": ""})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Figure-data builders (Figures 2-8; plotting stays in the notebook)
# --------------------------------------------------------------------------- #

def annual_complete_checklists(checklists):
    """Figure 2 — annual count of effort-eligible complete checklists (the ~30x
    observer-growth curve)."""
    eligible = checklists[checklists["is_complete_for_effort"].eq(True)]
    series = eligible.groupby("year")["SAMPLING EVENT IDENTIFIER"].nunique()
    return series.rename("complete_checklists").reset_index()


def raw_vs_confirmed_arrival(metrics_df, species_list):
    """Figure 3 — raw single-earliest vs confirmed (2nd-obs) arrival day-of-year
    per year, for the given focal species."""
    g = metrics_df[metrics_df["species"].isin(species_list)].copy()
    g["raw_arrival_doy"] = date_to_day_of_year(g["raw_first_arrival"])
    g["confirmed_arrival_doy"] = date_to_day_of_year(g["first_arrival"])
    g["common_name"] = g["species"].map(_SCI_TO_COMMON)
    return g[["common_name", "species", "year", "raw_arrival_doy",
              "confirmed_arrival_doy", "low_confidence"]]


def species_series_with_trend(metrics_df, metric_col):
    """Figures 4 & 5 — for each species: the per-year metric (day-of-year) plus a
    fitted trend line (from confident years). Returns {scientific: {...}}."""
    conf = _confident(metrics_df)
    out = {}
    for sci in _species_order(metrics_df):
        g = conf[conf["species"] == sci].sort_values("year")
        years = g["year"].to_numpy()
        values = date_to_day_of_year(g[metric_col]).to_numpy()
        tr = linear_trend(years, values)
        out[sci] = {"common": _SCI_TO_COMMON.get(sci, sci), "years": years,
                    "values": values, "trend": tr}
    return out


def temp_vs_arrival_points(metrics_df, annual_env, species_list):
    """Figure 6 (H1) — per focal species: (winter temperature, arrival day-of-
    year) points plus Pearson r/p. Returns {scientific: {...}}."""
    conf = _confident(metrics_df)
    temp_by_year = annual_env.set_index("year")["mean_winter_temperature"]
    out = {}
    for sci in species_list:
        g = conf[conf["species"] == sci].copy()
        g["arrival_doy"] = date_to_day_of_year(g["first_arrival"])
        g["temp"] = g["year"].map(temp_by_year)
        g = g.dropna(subset=["arrival_doy", "temp"])
        out[sci] = {"common": _SCI_TO_COMMON.get(sci, sci),
                    "temp": g["temp"].to_numpy(), "arrival_doy": g["arrival_doy"].to_numpy(),
                    "corr": correlation(g["temp"], g["arrival_doy"])}
    return out


def centroid_track(metrics_df, species_list):
    """Figure 8 — annual geographic centroid (lat, lon) per year for focal
    species. Returns {scientific: DataFrame(year, lat, lon)}."""
    out = {}
    for sci in species_list:
        g = metrics_df[(metrics_df["species"] == sci)].dropna(
            subset=["centroid_latitude", "centroid_longitude"]).sort_values("year")
        out[sci] = g[["year", "centroid_latitude", "centroid_longitude"]].reset_index(drop=True)
    return out


def _round(value, ndigits=3):
    return None if value is None or pd.isna(value) else round(float(value), ndigits)
