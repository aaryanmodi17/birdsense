"""Eyeball test: pull ERA5 temp/rainfall and MODIS NDVI for 5 known Gujarat
locations/dates and PRINT the raw values (and unit-converted values) so you can
sanity-check units BEFORE wiring anything into the pipeline.

This makes REAL Google Earth Engine calls. It is NOT part of the pipeline and is
intentionally tiny (5 points). Compare, for each point:
  - ERA5 temperature RAW should be ~290-300 (KELVIN); converted ~17-27 (Celsius).
  - ERA5 rainfall  RAW is in METERS (tiny, e.g. 0.000x); converted x1000 = mm.
  - MODIS NDVI     RAW is a scaled integer (e.g. 3000-7000); converted x0.0001.

=============================================================================
 HOW TO AUTHENTICATE GOOGLE EARTH ENGINE BEFORE RUNNING THIS SCRIPT
=============================================================================
 1. You need a Google account with Earth Engine access, and a Google Cloud
    project with the Earth Engine API enabled. Sign up (free for academic/
    non-commercial use) at https://earthengine.google.com/ and note the Cloud
    PROJECT ID it gives you.

 2. earthengine-api is already installed in the repo venv. Authenticate ONCE
    (opens a browser; stores a token under ~/.config/earthengine/):

        .venv/bin/earthengine authenticate

    (Equivalently, from Python: .venv/bin/python -c "import ee; ee.Authenticate()")

 3. Tell this script your project id, EITHER by editing EE_PROJECT below OR by
    exporting an env var:

        export EARTHENGINE_PROJECT=your-gcp-project-id

 4. Run it:

        .venv/bin/python scripts/test_gee_5points.py
=============================================================================
"""

import os
from datetime import datetime, timedelta

import ee

# Set your Google Cloud project id here or via the EARTHENGINE_PROJECT env var.
EE_PROJECT = os.environ.get("EARTHENGINE_PROJECT", "your-gcp-project-id")

ERA5_COLLECTION = "ECMWF/ERA5/HOURLY"   # aggregated to daily (mean temp, sum precip)
MODIS_NDVI_COLLECTION = "MODIS/061/MOD13Q1"

# (name, latitude, longitude, winter date) — 5 known Gujarat wetlands.
POINTS = [
    ("Nal Sarovar",          22.7900, 72.0300, "2020-01-15"),
    ("Little Rann of Kutch", 23.3000, 71.0000, "2020-01-15"),
    ("Khijadiya",            22.5200, 70.1500, "2019-12-20"),
    ("Thol Lake",            23.1300, 72.4000, "2021-01-10"),
    ("Great Rann of Kutch",  23.9000, 70.9000, "2018-02-05"),
]


def _era5_point(point, date):
    """ERA5/HOURLY aggregated over the day at the point: returns
    (daily_mean_kelvin, daily_summed_meters)."""
    d = datetime.fromisoformat(date)
    nxt = (d + timedelta(days=1)).strftime("%Y-%m-%d")
    day = ee.ImageCollection(ERA5_COLLECTION).filterDate(date, nxt).filterBounds(point)
    temp_k = (day.select("temperature_2m").mean()
              .reduceRegion(ee.Reducer.first(), point, 27830).get("temperature_2m").getInfo())
    rain_m = (day.select("total_precipitation").sum()
              .reduceRegion(ee.Reducer.first(), point, 27830).get("total_precipitation").getInfo())
    return temp_k, rain_m


def _modis_ndvi_point(point, date):
    """Nearest 16-day MOD13Q1 composite (+/-8 days) at the point: raw integer."""
    d = datetime.fromisoformat(date)
    lo = (d - timedelta(days=8)).strftime("%Y-%m-%d")
    hi = (d + timedelta(days=8)).strftime("%Y-%m-%d")
    img = (ee.ImageCollection(MODIS_NDVI_COLLECTION)
           .filterDate(lo, hi).filterBounds(point).first())
    return img.select("NDVI").reduceRegion(ee.Reducer.first(), point, 250).get("NDVI").getInfo()


def main():
    ee.Initialize(project=EE_PROJECT)
    print(f"GEE initialised (project={EE_PROJECT}). Pulling 5 points...\n")
    for name, lat, lon, date in POINTS:
        point = ee.Geometry.Point([lon, lat])
        temp_k, rain_m = _era5_point(point, date)
        ndvi_raw = _modis_ndvi_point(point, date)

        temp_c = None if temp_k is None else temp_k - 273.15   # KELVIN -> Celsius
        rain_mm = None if rain_m is None else rain_m * 1000.0  # METERS -> mm
        ndvi = None if ndvi_raw is None else ndvi_raw * 0.0001  # MODIS scale

        print(f"{name}  ({lat}, {lon})  {date}")
        print(f"   ERA5 temp : raw = {temp_k} K   ->  {temp_c:.2f} C"
              if temp_k is not None else "   ERA5 temp : raw = None")
        print(f"   ERA5 rain : raw = {rain_m} m   ->  {rain_mm:.3f} mm"
              if rain_m is not None else "   ERA5 rain : raw = None")
        print(f"   MODIS NDVI: raw = {ndvi_raw}      ->  {ndvi:.3f}"
              if ndvi_raw is not None else "   MODIS NDVI: raw = None")
        print()


if __name__ == "__main__":
    main()
