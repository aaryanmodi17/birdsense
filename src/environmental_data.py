"""Stage 4: Environmental Data — implements 09_ETL_AND_ANALYSIS_ENGINE.md (Stage 4)
and the variables + matching rule in 03_ENVIRONMENTAL_FRAMEWORK.md.

Two products:
  1. Per-observation join: temperature (deg C), rainfall (mm), and NDVI matched to
     each bird observation by date + location, using the matching-priority rule
     (03 "Spatial/Temporal Matching Rule"): exact date/cell -> nearest within a
     window -> NULL + log. The bird observation is NEVER dropped, only the
     missing environmental field.
  2. Annual winter aggregates (environmental_annual): per-year winter (Nov-Feb)
     mean temperature, total rainfall, and mean NDVI over Gujarat, for the H1
     correlation analysis (Stage 4: "store annual winter means separately").

MOCK MODE: pass mock=True to get plausible FAKE values (deterministic) so the
whole pipeline can run end-to-end before GEE is authenticated. Mock values are
NOT REAL and must never appear in the paper; matched output is tagged
env_source='MOCK-FAKE'. Switch mock off with mock=False (needs authenticated GEE
-- see scripts/test_gee_5points.py header for the auth steps).

ERA5 COLLECTION: uses `ECMWF/ERA5/HOURLY`, aggregated to daily (daily MEAN 2 m
temperature, daily SUMMED precipitation) and then to the winter season. The docs'
original `ECMWF/ERA5/DAILY` is frozen at 2020-07 and cannot cover 2010-2025;
ERA5-Land was rejected because it masks open water (nulls coastal/marine waterbird
locations). Resolution is unchanged (~25-30 km ERA5 grid). See
03_ENVIRONMENTAL_FRAMEWORK.md and 09_ETL_AND_ANALYSIS_ENGINE.md Stage 4.

CRITICAL UNITS (silent-bug guards -- see the pure converters below):
  - ERA5 `temperature_2m` is in KELVIN  -> Celsius  (subtract 273.15).
    Skipping this yields temps around 295 instead of ~22 -- the known silent bug.
  - ERA5 `total_precipitation` is in METERS       -> millimetres (x1000).
  - MODIS MOD13Q1 `NDVI` is a scaled integer      -> NDVI (x0.0001).
"""

import zlib

import pandas as pd

from . import validation as V

# ERA5 via GEE — 09 Stage 4 / 03 Var 1 & 2. HOURLY (1943->present) aggregated to
# daily; chosen because ECMWF/ERA5/DAILY is frozen at 2020-07 (can't cover the
# study period) and ERA5-Land masks open water. Same ~25-30 km ERA5 grid.
ERA5_COLLECTION = "ECMWF/ERA5/HOURLY"
ERA5_TEMP_BAND = "temperature_2m"             # KELVIN; daily/seasonal MEAN
ERA5_PRECIP_BAND = "total_precipitation"      # METERS; daily/seasonal SUM
MODIS_NDVI_COLLECTION = "MODIS/061/MOD13Q1"   # 09 Stage 4 / 03 Var 3

KELVIN_TO_CELSIUS = 273.15   # ERA5 temperature offset (K -> C)
METERS_TO_MM = 1000.0        # ERA5 precipitation (m -> mm)
NDVI_SCALE = 0.0001          # MODIS MOD13Q1 NDVI scale factor
ERA5_WINDOW_DAYS = 3         # 03 matching rule: +/- 3 days for ERA5
NDVI_COMPOSITE_DAYS = 8      # 03: nearest 16-day composite (half-window = 8 days)
ERA5_SCALE_M = 27830         # ~0.25 deg in metres (ERA5 grid), for reduceRegion

STUDY_YEARS = list(range(V.STUDY_PERIOD_START, V.STUDY_PERIOD_END + 1))
BBOX = V.GUJARAT_BBOX        # matching region (03 uses nearest grid cell)

MOCK_TAG = "MOCK-FAKE"
GEE_TAG = "GEE"


# --------------------------------------------------------------------------- #
# Pure unit converters — the "known silent bug" guards. Tested directly.
# --------------------------------------------------------------------------- #

def kelvin_to_celsius(kelvin):
    """ERA5 `mean_2m_air_temperature` is in KELVIN; convert to Celsius.
    THIS IS THE KNOWN SILENT BUG if skipped (03 Var 1)."""
    return None if kelvin is None else kelvin - KELVIN_TO_CELSIUS


def meters_to_mm(meters):
    """ERA5 `total_precipitation` is in METERS; convert to millimetres (03 Var 2)."""
    return None if meters is None else meters * METERS_TO_MM


def scale_ndvi(raw_ndvi):
    """MODIS MOD13Q1 `NDVI` is a scaled integer; multiply by 0.0001 (03 Var 3)."""
    return None if raw_ndvi is None else raw_ndvi * NDVI_SCALE


# --------------------------------------------------------------------------- #
# Deterministic mock generators — plausible FAKE values (not real).
# --------------------------------------------------------------------------- #

def _rng(*parts):
    """Deterministic per-input RNG (crc32 seed) — reproducible fake values."""
    import random
    return random.Random(zlib.crc32("|".join(str(p) for p in parts).encode()))


def _mock_winter_temp_rainfall(year):
    r = _rng("winter_tr", year)  # FAKE: plausible Gujarat winter values
    return {"mean_winter_temperature_c": round(r.uniform(20.0, 26.0), 2),
            "total_winter_rainfall_mm": round(r.uniform(5.0, 60.0), 1)}


def _mock_winter_ndvi(year):
    return round(_rng("winter_ndvi", year).uniform(0.15, 0.55), 3)  # FAKE


def _mock_point_temp_rainfall(lat, lon, date):
    r = _rng("pt_tr", round(lat, 3), round(lon, 3), date)  # FAKE
    return {"temperature_c": round(r.uniform(18.0, 28.0), 2),
            "rainfall_mm": round(r.uniform(0.0, 8.0), 2), "status": "mock"}


def _mock_point_ndvi(lat, lon, date):
    r = _rng("pt_ndvi", round(lat, 3), round(lon, 3), date)  # FAKE
    return {"ndvi": round(r.uniform(0.10, 0.70), 3), "status": "mock"}


# --------------------------------------------------------------------------- #
# Google Earth Engine access (lazy import/init so mock mode needs no auth).
# --------------------------------------------------------------------------- #

def _ensure_ee(project=None):
    import os

    import ee
    if project is None:
        project = os.environ.get("EARTHENGINE_PROJECT")  # e.g. birdsense-502407
    try:
        ee.Number(1).getInfo()          # already initialised?
    except Exception:
        ee.Initialize(project=project)  # requires prior `earthengine authenticate`
    return ee


def _winter_window(year):
    """Nov 1 of `year` through the end of Feb of `year+1`. GEE filterDate end is
    EXCLUSIVE, so Mar 1 is used to include all of February (handles leap years).
    (03 Var 1/2: winter season = Nov-Feb.)"""
    return f"{year}-11-01", f"{year + 1}-03-01"


def _region(ee):
    return ee.Geometry.Rectangle(
        [BBOX["lon_min"], BBOX["lat_min"], BBOX["lon_max"], BBOX["lat_max"]]
    )


def get_winter_temp_rainfall(year, mock=False, project=None):
    """Annual winter mean temperature (deg C) & total rainfall (mm) over Gujarat
    — 03 Var 1 & 2 / 09 Stage 4 `get_winter_temp_rainfall`."""
    if mock:
        return _mock_winter_temp_rainfall(year)
    ee = _ensure_ee(project)
    start, end = _winter_window(year)
    col = ee.ImageCollection(ERA5_COLLECTION).filterDate(start, end)
    region = _region(ee)
    # ERA5/HOURLY -> season: MEAN of every hourly temperature over the winter;
    # SUM of every hourly precipitation (total winter rainfall). Then the spatial
    # mean over Gujarat.
    temp_k = (col.select(ERA5_TEMP_BAND).mean()
              .reduceRegion(ee.Reducer.mean(), region, ERA5_SCALE_M)
              .get(ERA5_TEMP_BAND).getInfo())
    rain_m = (col.select(ERA5_PRECIP_BAND).sum()
              .reduceRegion(ee.Reducer.mean(), region, ERA5_SCALE_M)
              .get(ERA5_PRECIP_BAND).getInfo())
    return {
        "mean_winter_temperature_c": kelvin_to_celsius(temp_k),  # KELVIN -> C
        "total_winter_rainfall_mm": meters_to_mm(rain_m),        # METERS -> mm
    }


def get_winter_ndvi(year, mock=False, project=None):
    """Annual winter mean NDVI over Gujarat — 03 Var 3 (annual winter mean)."""
    if mock:
        return _mock_winter_ndvi(year)
    ee = _ensure_ee(project)
    start, end = _winter_window(year)
    raw = (ee.ImageCollection(MODIS_NDVI_COLLECTION).filterDate(start, end)
           .select("NDVI").mean()
           .reduceRegion(ee.Reducer.mean(), _region(ee), 250)
           .get("NDVI").getInfo())
    return scale_ndvi(raw)  # MODIS scale x0.0001


def _monsoon_window(year):
    """SW monsoon Jun 1 - Sep 30 of `year` (end exclusive -> Oct 1). This is the
    rain that fills Gujarat's wetlands BEFORE the Nov-Feb wintering season that
    starts that November — mechanistically the relevant water input for
    waterbirds, unlike the near-dry winter rainfall (implements
    03_ENVIRONMENTAL_FRAMEWORK.md Variable 2b, exploratory)."""
    return f"{year}-06-01", f"{year}-10-01"


def get_monsoon_rainfall(year, mock=False, project=None):
    """Total SW-monsoon (Jun-Sep) rainfall (mm) over Gujarat for `year` — ERA5/
    HOURLY total_precipitation summed. Precedes and plausibly drives the wetland
    extent birds encounter that winter (implements
    03_ENVIRONMENTAL_FRAMEWORK.md Variable 2b, exploratory)."""
    if mock:
        return round(_rng("monsoon", year).uniform(300.0, 1200.0), 1)  # FAKE
    ee = _ensure_ee(project)
    start, end = _monsoon_window(year)
    rain_m = (ee.ImageCollection(ERA5_COLLECTION).filterDate(start, end)
              .select(ERA5_PRECIP_BAND).sum()
              .reduceRegion(ee.Reducer.mean(), _region(ee), ERA5_SCALE_M)
              .get(ERA5_PRECIP_BAND).getInfo())
    return meters_to_mm(rain_m)  # METERS -> mm


def _era5_day(col_day, point, ee):
    """Aggregate one day's ERA5/HOURLY images at a point: daily MEAN temperature
    (deg C) and daily SUMMED precipitation (mm). Returns (temp_c, rain_mm) or
    (None, None) if the day has no image at that cell."""
    try:
        tk = (col_day.select(ERA5_TEMP_BAND).mean()
              .reduceRegion(ee.Reducer.first(), point, ERA5_SCALE_M)
              .get(ERA5_TEMP_BAND).getInfo())
        rm = (col_day.select(ERA5_PRECIP_BAND).sum()
              .reduceRegion(ee.Reducer.first(), point, ERA5_SCALE_M)
              .get(ERA5_PRECIP_BAND).getInfo())
    except Exception:
        return None, None
    if tk is None:
        return None, None
    return kelvin_to_celsius(tk), meters_to_mm(rm)


def get_point_temp_rainfall(lat, lon, date, mock=False, project=None):
    """Per-observation ERA5 temperature (deg C) + rainfall (mm) for one location/
    date, applying the 03 matching rule: (1) exact date, else (2) nearest date
    within +/- ERA5_WINDOW_DAYS, else (3) NULL. Each candidate DAY is aggregated
    from ERA5/HOURLY (daily mean temp, daily summed precip). Returns a dict with a
    `status` of 'exact' | 'window' | 'null'."""
    if mock:
        return _mock_point_temp_rainfall(lat, lon, date)
    ee = _ensure_ee(project)
    point = ee.Geometry.Point([lon, lat])
    d = pd.Timestamp(date)
    # exact day first, then true nearest day within the window (+/-1, +/-2, +/-3).
    offsets = [0]
    for k in range(1, ERA5_WINDOW_DAYS + 1):
        offsets += [k, -k]
    for off in offsets:
        day = d + pd.Timedelta(days=off)
        start = day.strftime("%Y-%m-%d")
        end = (day + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        col_day = ee.ImageCollection(ERA5_COLLECTION).filterDate(start, end).filterBounds(point)
        temp_c, rain_mm = _era5_day(col_day, point, ee)
        if temp_c is not None:
            return {"temperature_c": temp_c, "rainfall_mm": rain_mm,
                    "status": "exact" if off == 0 else "window"}
    return {"temperature_c": None, "rainfall_mm": None, "status": "null"}  # Priority 3


def get_ndvi(lat, lon, date, mock=False, project=None):
    """Per-observation NDVI for one location/date — 09 Stage 4 `get_ndvi`, nearest
    16-day MOD13Q1 composite (03 matching rule). Returns dict with `status`."""
    if mock:
        return _mock_point_ndvi(lat, lon, date)
    ee = _ensure_ee(project)
    point = ee.Geometry.Point([lon, lat])
    d = pd.Timestamp(date)
    for status, win in [("exact", NDVI_COMPOSITE_DAYS), ("window", 2 * NDVI_COMPOSITE_DAYS)]:
        start = (d - pd.Timedelta(days=win)).strftime("%Y-%m-%d")
        end = (d + pd.Timedelta(days=win)).strftime("%Y-%m-%d")
        img = (ee.ImageCollection(MODIS_NDVI_COLLECTION)
               .filterDate(start, end).filterBounds(point).first())
        try:
            raw = (img.select("NDVI")
                   .reduceRegion(ee.Reducer.first(), point, 250).get("NDVI").getInfo())
        except Exception:
            raw = None
        if raw is not None:
            return {"ndvi": scale_ndvi(raw), "status": status}  # MODIS scale
    return {"ndvi": None, "status": "null"}


# --------------------------------------------------------------------------- #
# Per-observation join + coverage reporting
# --------------------------------------------------------------------------- #

def match_environmental_to_observations(observations, mock=False, project=None,
                                        lat_col="LATITUDE", lon_col="LONGITUDE",
                                        date_col="OBSERVATION DATE"):
    """Attach temperature (deg C), rainfall (mm) and NDVI to every observation via
    the 03 matching rule. NEVER drops a row; unmatched fields become NULL. Returns
    (observations_with_env, log). The `log` records the NULL count per variable
    (03: "store NULL and log it -- do not drop the bird observation")."""
    if mock:
        _warn_mock()
    out = observations.copy()

    temperatures, rainfalls, ndvis = [], [], []
    tr_status, ndvi_status = [], []
    for _, row in out.iterrows():
        lat, lon, date = float(row[lat_col]), float(row[lon_col]), row[date_col]
        tr = get_point_temp_rainfall(lat, lon, date, mock=mock, project=project)
        nd = get_ndvi(lat, lon, date, mock=mock, project=project)
        temperatures.append(tr["temperature_c"])
        rainfalls.append(tr["rainfall_mm"])
        ndvis.append(nd["ndvi"])
        tr_status.append(tr["status"])
        ndvi_status.append(nd["status"])

    out["temperature"] = temperatures  # deg C
    out["rainfall"] = rainfalls        # mm
    out["ndvi"] = ndvis                # scaled NDVI
    out["env_temp_match"] = tr_status
    out["env_ndvi_match"] = ndvi_status
    out["env_source"] = MOCK_TAG if mock else GEE_TAG

    log = {"n_observations": len(out)}
    for var in ("temperature", "rainfall", "ndvi"):
        log[var] = {"null_count": int(out[var].isna().sum())}
    return out, log


def coverage_report(matched, variables=("temperature", "rainfall", "ndvi")):
    """% of observations with a non-null value per environmental variable
    (03 acceptance criteria: NDVI coverage reported as a percentage)."""
    n = len(matched)
    report = {"n_observations": n}
    for var in variables:
        non_null = int(matched[var].notna().sum())
        report[var] = {"matched": non_null,
                       "pct": (100.0 * non_null / n) if n else None}
    return report


def render_coverage(report):
    lines = ["ENVIRONMENTAL COVERAGE (% of observations with a non-null value)",
             f"  observations: {report['n_observations']:,}"]
    for var in ("temperature", "rainfall", "ndvi"):
        info = report[var]
        pct = "n/a" if info["pct"] is None else f"{info['pct']:.1f}%"
        lines.append(f"  {var:<12}: {info['matched']:>7,} matched  ({pct})")
    return "\n".join(lines)


def build_annual_environmental(years=STUDY_YEARS, mock=False, project=None):
    """Annual winter environmental means (environmental_annual per 07_DATABASE_
    SCHEMA.md) for H1 correlation — one row per year."""
    if mock:
        _warn_mock()
    rows = []
    for year in years:
        tr = get_winter_temp_rainfall(year, mock=mock, project=project)
        rows.append({
            "year": year,
            "mean_winter_temperature": tr["mean_winter_temperature_c"],  # deg C
            "total_winter_rainfall": tr["total_winter_rainfall_mm"],     # mm (Nov-Feb)
            "total_monsoon_rainfall": get_monsoon_rainfall(year, mock=mock, project=project),  # mm (Jun-Sep)
            "mean_winter_ndvi": get_winter_ndvi(year, mock=mock, project=project),
        })
    df = pd.DataFrame(rows)
    df["env_source"] = MOCK_TAG if mock else GEE_TAG
    return df


_MOCK_WARNED = False


def _warn_mock():
    global _MOCK_WARNED
    if not _MOCK_WARNED:
        print("!! MOCK ENVIRONMENTAL DATA: values are FAKE (deterministic), NOT "
              "real GEE output. Never use in the paper. Set mock=False (with "
              "authenticated GEE) for real values.")
        _MOCK_WARNED = True


if __name__ == "__main__":
    import os

    from . import load_and_clean

    print("=" * 74)
    print(" STAGE 4 ENVIRONMENTAL — MOCK end-to-end demo (FAKE values)")
    print("=" * 74)
    stage1 = load_and_clean.run_stage1()
    obs = stage1.clean_observations

    matched, log = match_environmental_to_observations(obs, mock=True)
    print("\n" + render_coverage(coverage_report(matched)))
    print(f"\n NULL-and-log (never dropped): {log}")
    print(f" rows in  : {len(obs):,}   rows out : {len(matched):,}  "
          f"(equal -> no bird observation dropped)")

    annual = build_annual_environmental(mock=True)
    print("\n ANNUAL WINTER ENVIRONMENTAL (environmental_annual) — FAKE mock values:")
    print(annual.to_string(index=False))

    # Save to data/processed (gitignored); .MOCK. in the name flags it as fake.
    processed = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed"
    )
    os.makedirs(processed, exist_ok=True)
    matched.to_csv(os.path.join(processed, "observations_with_env.MOCK.csv"), index=False)
    annual.to_csv(os.path.join(processed, "environmental_annual.MOCK.csv"), index=False)
    print(f"\n wrote FAKE mock outputs under {processed} (gitignored)")
