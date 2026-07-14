"""Hand-computed tests for Stage 2 (observer_effort) and Stage 3 (migration_metrics).

Each test uses a tiny, hand-built input whose correct answer can be worked out by
hand, then asserts the function returns exactly that. This is more trustworthy
than checking against the large synthetic file. Metric sections refer to
02_METRICS_METHODOLOGY.md.
"""

import pandas as pd

from src import migration_metrics as M
from src import observer_effort as E


# --------------------------------------------------------------------------- #
# Sec 1: First Arrival (confirmed = 2nd independent obs; raw = earliest)
# --------------------------------------------------------------------------- #

def test_confirmed_arrival_uses_second_observation():
    dates = ["2015-11-05", "2015-11-10", "2015-12-01"]  # earliest -> latest
    confirmed, raw, low = M.confirmed_arrival(dates)
    assert pd.Timestamp(confirmed) == pd.Timestamp("2015-11-10")  # 2nd earliest
    assert pd.Timestamp(raw) == pd.Timestamp("2015-11-05")        # literal earliest
    assert low is False


def test_confirmed_arrival_out_of_order_input():
    # Order of input must not matter; the function sorts.
    dates = ["2015-12-01", "2015-11-05", "2015-11-10"]
    confirmed, raw, _ = M.confirmed_arrival(dates)
    assert pd.Timestamp(confirmed) == pd.Timestamp("2015-11-10")
    assert pd.Timestamp(raw) == pd.Timestamp("2015-11-05")


def test_single_observation_is_low_confidence():
    confirmed, raw, low = M.confirmed_arrival(["2016-01-03"])
    assert pd.Timestamp(confirmed) == pd.Timestamp("2016-01-03")
    assert pd.Timestamp(raw) == pd.Timestamp("2016-01-03")
    assert low is True  # fewer than 2 observations (sec 1)


def test_zero_observations_flagged_low_confidence():
    confirmed, raw, low = M.confirmed_arrival([])
    assert confirmed is None and raw is None and low is True


def test_exactly_two_observations_are_low_confidence():
    # With only 2 obs the confirmed arrival/departure windows cross; the
    # species-year is flagged low_confidence (research decision, extends sec 1).
    confirmed, raw, low = M.confirmed_arrival(["2015-11-05", "2015-12-01"])
    assert pd.Timestamp(confirmed) == pd.Timestamp("2015-12-01")  # 2nd = d2
    assert pd.Timestamp(raw) == pd.Timestamp("2015-11-05")        # earliest = d1
    assert low is True


def test_three_observations_are_confident():
    _, _, low = M.confirmed_arrival(["2015-11-05", "2015-11-10", "2015-12-01"])
    assert low is False  # >= 3 obs -> arrival/departure do not cross


def test_two_observation_year_has_null_duration_and_low_confidence():
    # End-to-end: a species-year with exactly 2 complete-checklist observations
    # must come out low_confidence with wintering_duration_days undefined (None).
    checklists = pd.DataFrame({
        "SAMPLING EVENT IDENTIFIER": ["c1", "c2"],
        "year": [2015, 2015],
        "iso_week": [44, 48],
        "is_complete_for_effort": [True, True],
    })
    observations = pd.DataFrame({
        "SAMPLING EVENT IDENTIFIER": ["c1", "c2"],
        "SCIENTIFIC NAME": ["Anas acuta", "Anas acuta"],
        "year": [2015, 2015],
        "iso_week": [44, 48],
        "OBSERVATION DATE": ["2015-11-01", "2015-12-01"],
        "OBSERVATION COUNT": [5, 5],
        "LATITUDE": [22.0, 23.0],
        "LONGITUDE": [70.0, 71.0],
        "is_complete_for_effort": [True, True],
    })
    out = M.compute_migration_metrics(
        observations, checklists, species=["Anas acuta"], years=[2015]
    )
    row = out.iloc[0]
    assert row["n_obs"] == 2
    assert row["low_confidence"] is True or row["low_confidence"] == True  # noqa: E712
    assert pd.isna(row["wintering_duration_days"])
    assert row["first_arrival"] == "2015-12-01"    # confirmed = 2nd obs
    assert row["last_departure"] == "2015-11-01"   # confirmed = 2nd-from-latest


# --------------------------------------------------------------------------- #
# Sec 2: Last Departure (confirmed = 2nd from the latest; raw = latest)
# --------------------------------------------------------------------------- #

def test_confirmed_departure_uses_second_from_latest():
    dates = ["2015-11-05", "2015-11-10", "2015-12-01"]
    confirmed, raw, low = M.confirmed_departure(dates)
    assert pd.Timestamp(confirmed) == pd.Timestamp("2015-11-10")  # 2nd latest
    assert pd.Timestamp(raw) == pd.Timestamp("2015-12-01")        # literal latest
    assert low is False


# --------------------------------------------------------------------------- #
# Sec 4: Wintering Duration = departure - arrival (days)
# --------------------------------------------------------------------------- #

def test_wintering_duration_days():
    assert M.wintering_duration("2015-11-10", "2015-12-10") == 30
    assert M.wintering_duration(None, "2015-12-10") is None


# --------------------------------------------------------------------------- #
# Sec 5: Geographic Centroid (observation-count-weighted mean location)
# --------------------------------------------------------------------------- #

def test_centroid_weighted_by_observation_count():
    df = pd.DataFrame({
        "LATITUDE": [22.0, 24.0],
        "LONGITUDE": [70.0, 72.0],
        "OBSERVATION COUNT": [1, 3],  # weights 1 and 3
    })
    lat, lon = M.centroid(df)
    # lat = (22*1 + 24*3)/4 = 23.5 ; lon = (70*1 + 72*3)/4 = 71.5
    assert lat == 23.5
    assert lon == 71.5


def test_centroid_missing_count_defaults_to_weight_one():
    df = pd.DataFrame({
        "LATITUDE": [20.0, 24.0],
        "LONGITUDE": [68.0, 72.0],
        "OBSERVATION COUNT": [None, None],  # both default to weight 1 -> plain mean
    })
    lat, lon = M.centroid(df)
    assert lat == 22.0 and lon == 70.0


# --------------------------------------------------------------------------- #
# Sec 3: Peak Week (highest weekly detection rate; ties -> raw count -> earliest)
# --------------------------------------------------------------------------- #

def test_peak_week_and_tie_break_by_raw_count():
    # Week 45: 2 checklists report the species out of 10 complete -> rate 0.20
    # Week 46: 1 checklist reports the species out of 5 complete  -> rate 0.20 (tie)
    # Raw summed counts: week 45 = 3+4 = 7, week 46 = 20  -> tie broken toward 46.
    species_year_obs = pd.DataFrame({
        "iso_week": [45, 45, 46],
        "SAMPLING EVENT IDENTIFIER": ["A", "B", "C"],
        "OBSERVATION COUNT": [3, 4, 20],
    })
    complete_by_week = pd.Series({45: 10, 46: 5})
    peak, rate, raw_peak = M.peak_week(species_year_obs, complete_by_week)
    assert peak == 46          # tie on rate, week 46 has the higher raw count
    assert rate == 0.20
    assert raw_peak == 46      # week of max summed raw count


def test_peak_week_picks_highest_rate_not_highest_count():
    # Week 1: 1/2 = 0.50 rate, raw count 5.  Week 2: 3/100 = 0.03 rate, raw 300.
    # Detection rate must win over raw count for the PRIMARY peak.
    species_year_obs = pd.DataFrame({
        "iso_week": [1, 2],
        "SAMPLING EVENT IDENTIFIER": ["A", "B"],
        "OBSERVATION COUNT": [5, 300],
    })
    complete_by_week = pd.Series({1: 2, 2: 100})
    peak, rate, raw_peak = M.peak_week(species_year_obs, complete_by_week)
    assert peak == 1           # highest detection rate
    assert rate == 0.5
    assert raw_peak == 2       # diagnostic raw peak follows the raw count


# --------------------------------------------------------------------------- #
# Sec 6/7 + Rules 3/4: Detection rate & density exclude Incidental/incomplete
# --------------------------------------------------------------------------- #

def test_detection_rate_and_density_exclude_incidental():
    # c1, c2: complete & non-Incidental (effort-eligible). c3: Incidental (excluded).
    checklists = pd.DataFrame({
        "SAMPLING EVENT IDENTIFIER": ["c1", "c2", "c3"],
        "year": [2015, 2015, 2015],
        "is_complete_for_effort": [True, True, False],
    })
    # Species seen on c1 (count 5, complete) and on c3 (count 2, Incidental).
    observations = pd.DataFrame({
        "SAMPLING EVENT IDENTIFIER": ["c1", "c3"],
        "SCIENTIFIC NAME": ["Anas acuta", "Anas acuta"],
        "year": [2015, 2015],
        "OBSERVATION COUNT": [5, 2],
        "is_complete_for_effort": [True, False],
    })
    out = E.compute_observer_effort(
        observations, checklists, species=["Anas acuta"], years=[2015]
    )
    row = out.iloc[0]
    assert row["total_complete_checklists"] == 2   # c1, c2 (c3 Incidental excluded)
    assert row["observed_checklists"] == 1         # only c1 (c3 excluded)
    assert row["detection_rate"] == 0.5            # 1 / 2
    assert row["observation_density"] == 2.5       # 5 individuals / 2 complete
