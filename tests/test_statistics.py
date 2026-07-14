"""Hand-computed tests for src/statistics.py core functions (04_STATISTICAL_
ANALYSIS_PLAN.md). Small inputs with answers worked out by hand."""

import pandas as pd

from src import statistics as S


def test_alpha_is_single_constant():
    assert S.ALPHA == 0.05


def test_linear_trend_on_perfect_line():
    # y = 2*year - 4000 exactly -> slope 2, R^2 = 1, p ~ 0.
    years = [2010, 2011, 2012, 2013, 2014]
    values = [2 * y - 4000 for y in years]
    tr = S.linear_trend(years, values)
    assert abs(tr["slope"] - 2.0) < 1e-9
    assert abs(tr["r_squared"] - 1.0) < 1e-9
    assert tr["p_value"] < 0.05
    assert tr["n"] == 5


def test_linear_trend_too_few_points():
    tr = S.linear_trend([2010], [5])
    assert tr["slope"] is None and tr["n"] == 1


def test_correlation_perfect_positive():
    c = S.correlation([1, 2, 3, 4], [2, 4, 6, 8])
    assert abs(c["r"] - 1.0) < 1e-9
    assert c["p_value"] < 0.05
    assert c["n"] == 4


def test_correlation_drops_unpaired_nans():
    c = S.correlation([1, 2, 3, None], [2, 4, 6, 8])
    assert c["n"] == 3  # the (None, 8) pair is dropped


def test_spearman_monotonic_nonlinear():
    # Monotonic but non-linear -> Spearman rho = 1.
    c = S.spearman_correlation([1, 2, 3, 4], [1, 8, 27, 64])
    assert abs(c["rho"] - 1.0) < 1e-9


def test_is_significant_uses_alpha():
    assert S.is_significant(0.049) is True
    assert S.is_significant(0.05) is False
    assert S.is_significant(None) is False


def test_interpret_correlation_bands():
    assert S.interpret_correlation(0.8, 0.01) == "strong"   # significant, |r|>=0.5
    assert S.interpret_correlation(0.3, 0.01) == "weak"     # significant, small
    assert S.interpret_correlation(0.9, 0.20) == "none"     # not significant


def _tiny_metrics():
    return pd.DataFrame({
        "species": ["Anas acuta"] * 4,
        "year": [2010, 2011, 2012, 2013],
        "first_arrival": ["2010-01-05", "2011-01-06", "2012-01-07", "2013-01-08"],
        "peak_week": [2, 3, 4, 5],
        "low_confidence": [False] * 4,
        "n_obs": [10] * 4,
    })


def test_temperature_correlation_peak_week_numeric_path():
    # peak_week 2..5 rises with temp 20..23 -> Pearson r = +1 (numeric metric).
    annual = pd.DataFrame({"year": [2010, 2011, 2012, 2013],
                           "mean_winter_temperature": [20.0, 21.0, 22.0, 23.0]})
    out = S.build_temperature_correlation(_tiny_metrics(), annual, "peak_week", is_date=False)
    row = out.iloc[0]
    assert abs(row["pearson_r"] - 1.0) < 1e-9
    assert row["n_years"] == 4


def test_h2_comparison_has_arrival_and_peakweek_columns():
    out = S.build_h2_comparison(_tiny_metrics())
    assert {"arrival_slope_days_per_yr", "peakweek_slope_weeks_per_yr",
            "arrival_p", "peakweek_p"} <= set(out.columns)
    # peak_week increases by 1/year -> slope 1.0 week/year.
    assert abs(out.iloc[0]["peakweek_slope_weeks_per_yr"] - 1.0) < 1e-9


def test_effort_vs_arrival_correlation_detects_confound():
    # Arrival day-of-year rises lockstep with effort -> r = +1 (perfect confound).
    metrics = _tiny_metrics()
    effort = pd.DataFrame({"species": ["Anas acuta"] * 4, "year": [2010, 2011, 2012, 2013],
                           "total_complete_checklists": [100, 200, 300, 400]})
    out = S.effort_vs_arrival_correlation(metrics, effort)
    assert abs(out.iloc[0]["effort_vs_arrival_r"] - 1.0) < 1e-9


def test_date_to_day_of_year_preserves_index():
    # Regression guard: must preserve the input index so column assignment aligns.
    s = pd.Series(["2015-01-01", "2015-12-31"], index=[7, 42])
    doy = S.date_to_day_of_year(s)
    assert list(doy.index) == [7, 42]
    assert doy.loc[7] == 1 and doy.loc[42] == 365
