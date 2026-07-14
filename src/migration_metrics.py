"""Stage 3: Migration Metrics — implements 09_ETL_AND_ANALYSIS_ENGINE.md (Stage 3).

Per species per year, computes:
  - first_arrival / raw_first_arrival        (02_METRICS_METHODOLOGY.md sec 1)
  - last_departure / raw_last_departure      (02_METRICS_METHODOLOGY.md sec 2)
  - peak_week / peak_detection_rate / raw_peak_week   (sec 3)
  - wintering_duration_days                  (sec 4)
  - centroid_latitude / centroid_longitude   (sec 5)
  - low_confidence flag                      (sec 1)

Each species-year is computed over its COMPLETE-checklist observations (sec 1/2
define arrival/departure as the "2nd independent complete-checklist observation";
the flag `is_complete_for_effort` is produced once in Stage 1). Every metric has
exactly one implementation here (02_METRICS_METHODOLOGY.md acceptance criteria).
"""

import pandas as pd

from . import validation as V

SEI = "SAMPLING EVENT IDENTIFIER"
STUDY_YEARS = list(range(V.STUDY_PERIOD_START, V.STUDY_PERIOD_END + 1))

# The single, canonical confirmation threshold — 02_METRICS_METHODOLOGY.md sec 1.
# Defined exactly once; every arrival/departure calculation uses this constant.
CONFIRMATION_COUNT = 2

# A confirmed arrival (2nd observation from the start) and confirmed departure
# (2nd from the end) only stay well-separated (non-crossing) when there are at
# least CONFIRMATION_COUNT + 1 observations. With exactly 2, the two coincide on
# a crossing and departure precedes arrival, giving a negative/invalid duration.
# Such species-years are therefore flagged low_confidence and their wintering
# duration is left undefined. This extends 02_METRICS_METHODOLOGY.md sec 1's
# "< 2 observations" low_confidence rule per researcher decision (2026-07-14).
MIN_OBS_FOR_CONFIDENT_TIMING = CONFIRMATION_COUNT + 1


def _confirmed_endpoint(dates, ascending):
    """Shared engine for confirmed arrival (ascending) and departure (descending)
    — 02_METRICS_METHODOLOGY.md sec 1 & 2. `dates` is one date per independent
    complete checklist. Returns (confirmed, raw, low_confidence).

    - >= CONFIRMATION_COUNT obs: confirmed = the CONFIRMATION_COUNT-th date,
      raw = the single most-extreme date.
    - exactly 1 obs: confirmed = raw = the single date (sec 1).
    - 0 obs: (None, None).
    low_confidence is True whenever there are fewer than
    MIN_OBS_FOR_CONFIDENT_TIMING observations (see constant above).
    """
    s = pd.to_datetime(pd.Series(list(dates)), errors="coerce").dropna()
    s = s.sort_values(ascending=ascending).reset_index(drop=True)
    n = len(s)
    low_confidence = n < MIN_OBS_FOR_CONFIDENT_TIMING
    if n == 0:
        return None, None, low_confidence
    raw = s.iloc[0]
    if n < CONFIRMATION_COUNT:
        return raw, raw, low_confidence
    return s.iloc[CONFIRMATION_COUNT - 1], raw, low_confidence


def confirmed_arrival(dates):
    """First Arrival — 02_METRICS_METHODOLOGY.md sec 1: date of the 2nd
    independent complete-checklist observation. Returns
    (first_arrival, raw_first_arrival, low_confidence)."""
    return _confirmed_endpoint(dates, ascending=True)


def confirmed_departure(dates):
    """Last Departure — 02_METRICS_METHODOLOGY.md sec 2: the 2nd independent
    complete-checklist observation counting backward from the latest. Returns
    (last_departure, raw_last_departure, low_confidence)."""
    return _confirmed_endpoint(dates, ascending=False)


def wintering_duration(first_arrival, last_departure):
    """Wintering Duration — 02_METRICS_METHODOLOGY.md sec 4:
    Confirmed Departure - Confirmed Arrival (days). None if either is missing."""
    if first_arrival is None or last_departure is None:
        return None
    return int((pd.Timestamp(last_departure) - pd.Timestamp(first_arrival)).days)


def peak_week(species_year_obs, complete_checklists_by_week,
              week_col="iso_week", sei_col=SEI, count_col="OBSERVATION COUNT"):
    """Peak Migration Week — 02_METRICS_METHODOLOGY.md sec 3.

    Weekly detection rate = complete checklists reporting the species that week /
    total complete checklists that week. The peak is the week with the highest
    weekly detection rate; ties are broken by raw summed count, then earliest
    week. Returns (peak_week, peak_detection_rate, raw_peak_week). raw_peak_week
    (week of max summed raw count; earliest on ties) is diagnostic only.
    """
    if species_year_obs.empty or complete_checklists_by_week.empty:
        return None, None, None

    observed_by_week = (
        species_year_obs.drop_duplicates(sei_col)
        .groupby(week_col)[sei_col].nunique()
    )
    weekly_rate = (
        observed_by_week.reindex(complete_checklists_by_week.index, fill_value=0)
        / complete_checklists_by_week
    ).fillna(0.0)
    raw_weekly = (
        pd.to_numeric(species_year_obs[count_col], errors="coerce")
        .groupby(species_year_obs[week_col]).sum()
    )

    max_rate = weekly_rate.max()
    if max_rate <= 0:
        peak, rate = None, None
    else:
        tied = list(weekly_rate[weekly_rate == max_rate].index)
        # tie-break: highest raw summed count, then earliest week number
        best = sorted(tied, key=lambda w: (-float(raw_weekly.get(w, 0)), int(w)))[0]
        peak, rate = int(best), float(max_rate)

    if raw_weekly.empty or raw_weekly.max() <= 0:
        raw_peak = None
    else:
        raw_max = raw_weekly.max()
        raw_tied = list(raw_weekly[raw_weekly == raw_max].index)
        raw_peak = int(sorted(raw_tied, key=lambda w: int(w))[0])  # earliest on ties

    return peak, rate, raw_peak


def centroid(species_year_obs, lat_col="LATITUDE", lon_col="LONGITUDE",
             count_col="OBSERVATION COUNT"):
    """Geographic Centroid — 02_METRICS_METHODOLOGY.md sec 5: observation-count-
    weighted mean location. Missing counts default to weight 1 (per the doc).
    Returns (centroid_latitude, centroid_longitude)."""
    if species_year_obs.empty:
        return None, None
    lat = pd.to_numeric(species_year_obs[lat_col], errors="coerce")
    lon = pd.to_numeric(species_year_obs[lon_col], errors="coerce")
    weights = pd.to_numeric(species_year_obs[count_col], errors="coerce").fillna(1)
    total_weight = weights.sum()
    if not total_weight:
        return None, None
    return (lat * weights).sum() / total_weight, (lon * weights).sum() / total_weight


def _fmt_date(value):
    if value is None or pd.isna(value):
        return None
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def compute_migration_metrics(observations, checklists,
                              species=V.STUDY_SPECIES_SCIENTIFIC, years=STUDY_YEARS):
    """Stage 3 over the full species x year grid (09_ETL_AND_ANALYSIS_ENGINE.md).

    `observations`/`checklists` are the cleaned Stage 1 frames (carrying
    `is_complete_for_effort`, `year`, `iso_week`). One row per species-year."""
    obs_c = observations[observations["is_complete_for_effort"].eq(True)].copy()
    complete_chk = checklists[checklists["is_complete_for_effort"].eq(True)]
    # total complete checklists per (year, iso_week) — peak-week denominator.
    total_year_week = complete_chk.groupby(["year", "iso_week"])[SEI].nunique()

    rows = []
    for sci in species:
        sci_obs = obs_c[obs_c["SCIENTIFIC NAME"] == sci]
        for year in years:
            syo = sci_obs[sci_obs["year"] == year]
            # one observation per independent checklist (sec 1: "independent")
            dates = pd.to_datetime(
                syo.drop_duplicates(SEI)["OBSERVATION DATE"], errors="coerce"
            ).dropna()

            first_arrival, raw_first, low_conf = confirmed_arrival(dates)
            last_departure, raw_last, _ = confirmed_departure(dates)
            # Duration is only defined for well-separated (non-crossing) confirmed
            # dates, i.e. non-low_confidence species-years (>= 3 observations).
            duration = None if low_conf else wintering_duration(
                first_arrival, last_departure)

            if year in total_year_week.index.get_level_values(0):
                weekly_totals = total_year_week.xs(year, level=0)
            else:
                weekly_totals = pd.Series(dtype="int64")
            pk_week, pk_rate, raw_pk_week = peak_week(syo, weekly_totals)

            cen_lat, cen_lon = centroid(syo)

            rows.append({
                "species": sci,
                "year": year,
                "n_obs": len(dates),
                "first_arrival": _fmt_date(first_arrival),
                "raw_first_arrival": _fmt_date(raw_first),
                "last_departure": _fmt_date(last_departure),
                "raw_last_departure": _fmt_date(raw_last),
                "peak_week": pk_week,
                "peak_detection_rate": pk_rate,
                "raw_peak_week": raw_pk_week,
                "wintering_duration_days": duration,
                "centroid_latitude": cen_lat,
                "centroid_longitude": cen_lon,
                "low_confidence": low_conf,
            })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import os

    from . import load_and_clean

    result = load_and_clean.run_stage1()
    metrics = compute_migration_metrics(
        result.clean_observations, result.clean_checklists
    )

    # Save to data/processed (gitignored) — synthetic-derived, must not be
    # committed or used in the paper (07_DATABASE_SCHEMA.md / 11_CODE_STRUCTURE.md).
    processed = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed"
    )
    os.makedirs(processed, exist_ok=True)
    metrics.to_csv(os.path.join(processed, "migration_metrics.csv"), index=False)

    pd.set_option("display.max_rows", 300)
    pd.set_option("display.width", 200)
    print(metrics.to_string(index=False))
