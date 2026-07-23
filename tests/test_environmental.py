"""Tests for src/environmental_data.py that need NO GEE: the critical unit
conversions (the known silent bugs), mock determinism, the never-drop / coverage
behavior. Metric/unit refs are 03_ENVIRONMENTAL_FRAMEWORK.md.
"""

import pandas as pd

from src import environmental_data as ENV


# --------------------------------------------------------------------------- #
# Unit conversions — the "known silent bug" guards
# --------------------------------------------------------------------------- #

def test_kelvin_to_celsius():
    assert ENV.kelvin_to_celsius(273.15) == 0.0
    assert ENV.kelvin_to_celsius(295.15) == 22.0   # ~typical Gujarat winter day
    assert ENV.kelvin_to_celsius(None) is None


def test_meters_to_mm():
    assert ENV.meters_to_mm(0.012) == 12.0
    assert ENV.meters_to_mm(None) is None


def test_scale_ndvi():
    assert abs(ENV.scale_ndvi(6000) - 0.6) < 1e-9
    assert ENV.scale_ndvi(None) is None


# --------------------------------------------------------------------------- #
# Mock mode — deterministic, plausible, clearly fake
# --------------------------------------------------------------------------- #

def test_mock_winter_values_are_deterministic_and_plausible():
    a = ENV.get_winter_temp_rainfall(2015, mock=True)
    b = ENV.get_winter_temp_rainfall(2015, mock=True)
    assert a == b  # deterministic
    assert 15.0 <= a["mean_winter_temperature_c"] <= 30.0   # plausible Celsius
    assert 0.0 <= a["total_winter_rainfall_mm"] <= 200.0    # plausible mm
    ndvi = ENV.get_winter_ndvi(2015, mock=True)
    assert -0.2 <= ndvi <= 1.0                              # valid NDVI range


def test_mock_annual_table_tagged_fake():
    annual = ENV.build_annual_environmental(years=[2010, 2011], mock=True)
    assert list(annual.columns) == [
        "year", "mean_winter_temperature", "total_winter_rainfall",
        "total_monsoon_rainfall", "mean_winter_ndvi", "env_source",
    ]
    assert (annual["env_source"] == ENV.MOCK_TAG).all()  # labelled fake


# --------------------------------------------------------------------------- #
# Matching join — never drops a bird row; coverage reporter
# --------------------------------------------------------------------------- #

def _tiny_obs():
    return pd.DataFrame({
        "SAMPLING EVENT IDENTIFIER": ["c1", "c2", "c3"],
        "OBSERVATION DATE": ["2015-11-20", "2015-12-05", "2016-01-09"],
        "LATITUDE": [22.5, 23.1, 21.9],
        "LONGITUDE": [70.1, 72.4, 71.0],
    })


def test_match_never_drops_rows_and_reports_full_mock_coverage():
    obs = _tiny_obs()
    matched, log = ENV.match_environmental_to_observations(obs, mock=True)
    assert len(matched) == len(obs)                 # 03: never drop the bird obs
    assert log["n_observations"] == 3
    for var in ("temperature", "rainfall", "ndvi"):
        assert matched[var].notna().all()           # mock fills every row
    assert (matched["env_source"] == ENV.MOCK_TAG).all()
    rep = ENV.coverage_report(matched)
    assert rep["temperature"]["pct"] == 100.0
    assert rep["ndvi"]["pct"] == 100.0


def test_coverage_reporter_counts_nulls():
    matched = pd.DataFrame({
        "temperature": [1.0, None, 3.0, 4.0],  # 3 of 4 non-null
        "rainfall": [1.0, 2.0, 3.0, 4.0],
        "ndvi": [None, None, 0.3, 0.4],        # 2 of 4 non-null
    })
    rep = ENV.coverage_report(matched)
    assert rep["temperature"]["matched"] == 3 and rep["temperature"]["pct"] == 75.0
    assert rep["ndvi"]["matched"] == 2 and rep["ndvi"]["pct"] == 50.0
