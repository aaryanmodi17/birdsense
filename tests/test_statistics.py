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


def test_date_to_day_of_year_preserves_index():
    # Regression guard: must preserve the input index so column assignment aligns.
    s = pd.Series(["2015-01-01", "2015-12-31"], index=[7, 42])
    doy = S.date_to_day_of_year(s)
    assert list(doy.index) == [7, 42]
    assert doy.loc[7] == 1 and doy.loc[42] == 365
