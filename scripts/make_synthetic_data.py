"""
================================================================================
  THIS IS SYNTHETIC TEST DATA, NOT REAL.

  The files this script produces are randomly generated. Every number in them
  is meaningless and MUST NEVER appear in the paper or be treated as a finding.
  Their only purpose is to give the cleaning / ETL pipeline realistic-shaped
  input to run against, and to deliberately plant records that the validation
  rules must catch, so we can prove cleaning works.
================================================================================

make_synthetic_data.py

Generates two tab-delimited files imitating the eBird Basic Dataset (EBD)
format, per the May 2026 EBD v1.16 layout the researcher's real files use:

  data/raw/ebird_sampling_gujarat.txt      (checklist / sampling-event metadata)
  data/raw/ebird_observations_gujarat.txt  (species observation records)

This is test tooling, NOT part of the analysis pipeline (11_CODE_STRUCTURE.md)
and it implements no metric. It intentionally seeds records that each rule in
05_DATA_VALIDATION_PLAN.md is supposed to reject, and uses the 12 study species
and scientific names from 01_RESEARCH_METHODOLOGY.md.

Reproducible: fixed random seed. Re-running reproduces byte-identical files.
"""

import itertools
import os
import random
from datetime import date, timedelta

import pandas as pd

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

SEED = 20260714
random.seed(SEED)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(REPO_ROOT, "data", "raw")

STUDY_YEARS = list(range(2010, 2026))  # 2010-2025 inclusive = 16 years

# Gujarat rough bounding box - 05_DATA_VALIDATION_PLAN.md Rule 8.
GJ_LAT_MIN, GJ_LAT_MAX = 20.0, 24.7
GJ_LON_MIN, GJ_LON_MAX = 68.0, 74.5

# 12 study species (common name, scientific name) - 01_RESEARCH_METHODOLOGY.md.
SPECIES = [
    ("Northern Pintail", "Anas acuta"),
    ("Northern Shoveler", "Spatula clypeata"),
    ("Garganey", "Spatula querquedula"),
    ("Eurasian Wigeon", "Mareca penelope"),
    ("Common Pochard", "Aythya ferina"),
    ("Bar-headed Goose", "Anser indicus"),
    ("Greylag Goose", "Anser anser"),
    ("Common Crane", "Grus grus"),
    ("Demoiselle Crane", "Anthropoides virgo"),
    ("Greater Flamingo", "Phoenicopterus roseus"),
    ("Great White Pelican", "Pelecanus onocrotalus"),
    ("Dalmatian Pelican", "Pelecanus crispus"),  # deliberately sparse (see below)
]

DALMATIAN_COMMON = "Dalmatian Pelican"
DALMATIAN_SCI = "Pelecanus crispus"

# Dalmatian Pelican: present in fewer than 8 of the 16 study years, to exercise
# the <8-years exclusion / low_confidence logic (01_RESEARCH_METHODOLOGY.md,
# 02_METRICS_METHODOLOGY.md sec 1). Here: 5 of 16 years.
DALMATIAN_YEARS = [2011, 2014, 2017, 2021, 2024]

# Plausible Gujarat waterbird localities (cosmetic only).
LOCALITIES = [
    "Nal Sarovar Bird Sanctuary", "Little Rann of Kutch", "Thol Lake",
    "Khijadiya Bird Sanctuary", "Great Rann of Kutch", "Nalsarovar",
    "Porbandar Bird Sanctuary", "Gosabara Wetland", "Wadhwana Wetland",
    "Vinchhiya", "Jamnagar Coast", "Velavadar",
]

# Checklist volume grows ~30x from 2010 to 2025 (01_RESEARCH_METHODOLOGY.md:
# citizen-science participation grew ~30x). Geometric growth base -> ~30x.
BASE_2010 = 120
GROWTH = 30 ** (1 / 15)  # so year 2025 (index 15) ~= 30 * base
YEAR_COUNTS = {y: round(BASE_2010 * GROWTH ** (y - 2010)) for y in STUDY_YEARS}

# How many "bad" records of each kind to plant (each targets a specific rule).
N_HISTORICAL = 8    # Rule 1: OBSERVATION TYPE == "Historical" (pre-1900 dates)
N_PRE_2010 = 10     # Rule 2: OBSERVATION DATE year < 2010
N_POST_2025 = 6     # Rule 2: OBSERVATION DATE year > 2025
N_INCIDENTAL = 15   # Rule 3: PROTOCOL NAME == "Incidental"
N_INCIDENTAL_ALL_REPORTED = 9   # ...of those, this many have ALL SPECIES REPORTED == 1
N_OUT_OF_BBOX = 12  # Rule 8: coordinates outside the Gujarat bounding box
N_DUPLICATE_OBS = 10  # Rule 7: exact duplicate (SAMPLING EVENT IDENTIFIER + species)

# Out-of-bbox coordinate points (real cities / just-outside points).
OUT_OF_BBOX_POINTS = [
    (28.6139, 77.2090),  # Delhi
    (19.0760, 72.8777),  # Mumbai
    (13.0827, 80.2707),  # Chennai
    (26.9124, 75.7873),  # Jaipur       (lat > 24.7)
    (23.2599, 77.4126),  # Bhopal       (lon > 74.5)
    (24.5000, 66.9700),  # Arabian Sea  (lon < 68)
    (25.8000, 71.0000),  # N. Rajasthan (lat > 24.7)
    (21.1702, 75.0000),  # (lon > 74.5)
]

SAMPLING_COLS = [
    "SAMPLING EVENT IDENTIFIER", "OBSERVATION TYPE", "OBSERVATION DATE",
    "ALL SPECIES REPORTED", "PROTOCOL NAME", "STATE",
    "LATITUDE", "LONGITUDE", "LOCALITY",
]

OBS_COLS = [
    "GLOBAL UNIQUE IDENTIFIER", "SAMPLING EVENT IDENTIFIER", "OBSERVATION TYPE",
    "OBSERVATION DATE", "COMMON NAME", "SCIENTIFIC NAME", "OBSERVATION COUNT",
    "ALL SPECIES REPORTED", "PROTOCOL NAME", "STATE",
    "LATITUDE", "LONGITUDE", "LOCALITY",
]

# --------------------------------------------------------------------------- #
# Row builders
# --------------------------------------------------------------------------- #

sampling_rows = []
obs_rows = []
_sei_counter = itertools.count(1)
_guid_counter = itertools.count(1)


def new_sei():
    return f"S{next(_sei_counter):09d}"


def new_guid():
    return f"URN:CornellLabOfOrnithology:EBIRD:OBS{next(_guid_counter):09d}"


def add_checklist(d, lat, lon, protocol, all_reported, obs_type, state, locality):
    """Append one sampling-event (checklist) row; return its shared metadata."""
    sei = new_sei()
    meta = {
        "SAMPLING EVENT IDENTIFIER": sei,
        "OBSERVATION TYPE": obs_type,
        "OBSERVATION DATE": d.isoformat(),
        "ALL SPECIES REPORTED": all_reported,
        "PROTOCOL NAME": protocol,
        "STATE": state,
        "LATITUDE": round(lat, 6),
        "LONGITUDE": round(lon, 6),
        "LOCALITY": locality,
    }
    sampling_rows.append(dict(meta))
    meta["_date_obj"] = d
    return meta


def add_observation(meta, common, sci, count):
    """Append one species-observation row that inherits its checklist metadata."""
    obs_rows.append({
        "GLOBAL UNIQUE IDENTIFIER": new_guid(),
        "SAMPLING EVENT IDENTIFIER": meta["SAMPLING EVENT IDENTIFIER"],
        "OBSERVATION TYPE": meta["OBSERVATION TYPE"],
        "OBSERVATION DATE": meta["OBSERVATION DATE"],
        "COMMON NAME": common,
        "SCIENTIFIC NAME": sci,
        "OBSERVATION COUNT": count,
        "ALL SPECIES REPORTED": meta["ALL SPECIES REPORTED"],
        "PROTOCOL NAME": meta["PROTOCOL NAME"],
        "STATE": meta["STATE"],
        "LATITUDE": meta["LATITUDE"],
        "LONGITUDE": meta["LONGITUDE"],
        "LOCALITY": meta["LOCALITY"],
    })


def random_date_in_year(y):
    start = date(y, 1, 1)
    span = (date(y, 12, 31) - start).days
    return start + timedelta(days=random.randint(0, span))


def gj_point():
    return (random.uniform(GJ_LAT_MIN, GJ_LAT_MAX),
            random.uniform(GJ_LON_MIN, GJ_LON_MAX))


def random_count():
    r = random.random()
    if r < 0.60:
        return random.randint(1, 5)
    if r < 0.90:
        return random.randint(6, 40)
    return random.randint(41, 400)


def month_factor(m):
    """Seasonal detection weight: winter high, shoulder medium, off-season low."""
    if m in (11, 12, 1, 2):
        return 1.0
    if m in (10, 3):
        return 0.30
    return 0.03


# Per-species base winter detection rate (fixed by seed). Dalmatian is planted
# separately, so it is not given a probabilistic rate here.
species_winter_rate = {
    sci: round(random.uniform(0.06, 0.22), 3)
    for _c, sci in SPECIES if sci != DALMATIAN_SCI
}


def random_species(k=None):
    """Pick 1-2 study species (excluding Dalmatian) for planted bad checklists."""
    k = k or random.randint(1, 2)
    pool = [(c, s) for c, s in SPECIES if s != DALMATIAN_SCI]
    return random.sample(pool, k)


# --------------------------------------------------------------------------- #
# 1. Clean, valid data (skip Dalmatian here; planted deterministically below)
# --------------------------------------------------------------------------- #

clean_checklists_by_year = {y: [] for y in STUDY_YEARS}
n_clean_checklists = 0

for y in STUDY_YEARS:
    for _ in range(YEAR_COUNTS[y]):
        d = random_date_in_year(y)
        lat, lon = gj_point()
        all_reported = 1 if random.random() < 0.85 else 0  # ~85% complete (Rule 4)
        protocol = random.choices(
            ["Traveling", "Stationary", "Area"], weights=[0.60, 0.35, 0.05]
        )[0]
        locality = random.choice(LOCALITIES)
        meta = add_checklist(d, lat, lon, protocol, all_reported,
                             "eBird", "Gujarat", locality)
        clean_checklists_by_year[y].append(meta)
        n_clean_checklists += 1

        mf = month_factor(d.month)
        for common, sci in SPECIES:
            if sci == DALMATIAN_SCI:
                continue
            if random.random() < species_winter_rate[sci] * mf:
                add_observation(meta, common, sci, random_count())

# --------------------------------------------------------------------------- #
# 2. Dalmatian Pelican - deterministically sparse (present in 5 of 16 years)
# --------------------------------------------------------------------------- #

dalmatian_obs_per_year = {}
for y in DALMATIAN_YEARS:
    winter_checklists = [m for m in clean_checklists_by_year[y]
                         if m["_date_obj"].month in (11, 12, 1, 2)]
    picks = winter_checklists or clean_checklists_by_year[y]
    n = random.choice([1, 1, 2, 3])  # some years get a single obs -> low_confidence
    n = min(n, len(picks))
    for meta in random.sample(picks, n):
        add_observation(meta, DALMATIAN_COMMON, DALMATIAN_SCI, random.randint(1, 4))
    dalmatian_obs_per_year[y] = n

n_clean_obs = len(obs_rows)  # boundary: everything above is clean, in-range data

# --------------------------------------------------------------------------- #
# 3. Planted "bad" records - each targets a specific validation rule
# --------------------------------------------------------------------------- #

# Rule 1: Historical observation type, implausible pre-1900 dates.
historical_seed_dates = [date(1800, 2, 1), date(1885, 10, 24), date(1898, 12, 16)]
n_historical_obs = 0
for i in range(N_HISTORICAL):
    d = (historical_seed_dates[i] if i < len(historical_seed_dates)
         else date(random.randint(1850, 1899), random.randint(1, 12),
                   random.randint(1, 28)))
    lat, lon = gj_point()
    meta = add_checklist(d, lat, lon, "Traveling", 1, "Historical",
                         "Gujarat", random.choice(LOCALITIES))
    for common, sci in random_species():
        add_observation(meta, common, sci, random_count())
        n_historical_obs += 1

# Rule 2: pre-2010 rows (valid in every other respect).
n_pre2010_obs = 0
for _ in range(N_PRE_2010):
    d = random_date_in_year(random.randint(2005, 2009))
    lat, lon = gj_point()
    meta = add_checklist(d, lat, lon, "Stationary", 1, "eBird",
                         "Gujarat", random.choice(LOCALITIES))
    for common, sci in random_species():
        add_observation(meta, common, sci, random_count())
        n_pre2010_obs += 1

# Rule 2: post-2025 rows.
n_post2025_obs = 0
for _ in range(N_POST_2025):
    d = random_date_in_year(random.randint(2026, 2027))
    lat, lon = gj_point()
    meta = add_checklist(d, lat, lon, "Traveling", 1, "eBird",
                         "Gujarat", random.choice(LOCALITIES))
    for common, sci in random_species():
        add_observation(meta, common, sci, random_count())
        n_post2025_obs += 1

# Rule 3: Incidental protocol (some WITH all-species-reported == 1, to prove the
# exclusion applies even then). In-range, in-Gujarat, valid coords otherwise.
n_incidental_obs = 0
for i in range(N_INCIDENTAL):
    d = random_date_in_year(random.choice(STUDY_YEARS))
    lat, lon = gj_point()
    all_reported = 1 if i < N_INCIDENTAL_ALL_REPORTED else 0
    meta = add_checklist(d, lat, lon, "Incidental", all_reported, "eBird",
                         "Gujarat", random.choice(LOCALITIES))
    for common, sci in random_species(1):
        add_observation(meta, common, sci, random_count())
        n_incidental_obs += 1

# Rule 8: coordinates outside the Gujarat bounding box. STATE deliberately left
# as "Gujarat" (mislabeled) so ONLY the coordinate rule catches these.
n_outbbox_obs = 0
for i in range(N_OUT_OF_BBOX):
    d = random_date_in_year(random.choice(STUDY_YEARS))
    lat, lon = OUT_OF_BBOX_POINTS[i % len(OUT_OF_BBOX_POINTS)]
    meta = add_checklist(d, lat, lon, "Traveling", 1, "eBird",
                         "Gujarat", random.choice(LOCALITIES))
    for common, sci in random_species(1):
        add_observation(meta, common, sci, random_count())
        n_outbbox_obs += 1

# Rule 7: exact duplicate observation rows (same SAMPLING EVENT IDENTIFIER +
# species), imitating shared group-outing checklists. Copied from clean rows.
duplicate_sources = random.sample(range(n_clean_obs), N_DUPLICATE_OBS)
for idx in duplicate_sources:
    obs_rows.append(dict(obs_rows[idx]))  # byte-exact duplicate (same GUID)

# --------------------------------------------------------------------------- #
# 4. Write files (tab-delimited, no index)
# --------------------------------------------------------------------------- #

os.makedirs(RAW_DIR, exist_ok=True)
sampling_path = os.path.join(RAW_DIR, "ebird_sampling_gujarat.txt")
obs_path = os.path.join(RAW_DIR, "ebird_observations_gujarat.txt")

pd.DataFrame(sampling_rows, columns=SAMPLING_COLS).to_csv(
    sampling_path, sep="\t", index=False)
pd.DataFrame(obs_rows, columns=OBS_COLS).to_csv(
    obs_path, sep="\t", index=False)

# --------------------------------------------------------------------------- #
# 5. Summary - exactly what cleaning should remove
# --------------------------------------------------------------------------- #

total_checklists = len(sampling_rows)
total_obs = len(obs_rows)
n_planted_bad_checklists = (N_HISTORICAL + N_PRE_2010 + N_POST_2025
                            + N_INCIDENTAL + N_OUT_OF_BBOX)

bar = "=" * 78
print(bar)
print(" SYNTHETIC eBird TEST DATA GENERATED  --  NOT REAL, numbers are meaningless")
print(bar)
print(f" Random seed              : {SEED} (output is reproducible)")
print(f" Sampling file            : {sampling_path}")
print(f" Observations file        : {obs_path}")
print()
print(" FILE ROW COUNTS (excluding header)")
print(f"   sampling-event rows (checklists) : {total_checklists:>7,}")
print(f"   species-observation rows         : {total_obs:>7,}")
print()
print(" CLEAN / VALID DATA")
print(f"   valid in-Gujarat 2010-2025 checklists : {n_clean_checklists:>7,}")
print(f"   valid species-observation rows        : {n_clean_obs:>7,}")
print("   per-year checklist volume (shows ~30x growth):")
for y in STUDY_YEARS:
    n = YEAR_COUNTS[y]
    print(f"      {y}: {n:>5,}  " + "#" * max(1, n // 60))
print()
print(" PLANTED BAD RECORDS - cleaning MUST remove/flag these")
print(f"   [Rule 1] Historical type (pre-1900 dates):")
print(f"            {N_HISTORICAL} checklists, {n_historical_obs} observation rows")
print(f"   [Rule 2] pre-2010 (2005-2009):")
print(f"            {N_PRE_2010} checklists, {n_pre2010_obs} observation rows")
print(f"   [Rule 2] post-2025 (2026-2027):")
print(f"            {N_POST_2025} checklists, {n_post2025_obs} observation rows")
print(f"   [Rule 3] Incidental protocol:")
print(f"            {N_INCIDENTAL} checklists "
      f"({N_INCIDENTAL_ALL_REPORTED} with ALL SPECIES REPORTED==1), "
      f"{n_incidental_obs} observation rows")
print(f"   [Rule 8] coordinates outside Gujarat bbox (STATE mislabeled 'Gujarat'):")
print(f"            {N_OUT_OF_BBOX} checklists, {n_outbbox_obs} observation rows")
print(f"   [Rule 7] exact duplicate (SEI + species) observation rows:")
print(f"            {N_DUPLICATE_OBS} extra copies of clean rows")
print()
print(f"   total planted bad checklists : {n_planted_bad_checklists}")
print(f"   total planted duplicate obs  : {N_DUPLICATE_OBS}")
print()
print(" SPARSE SPECIES (low_confidence / <8-year exclusion test)")
print(f"   Dalmatian Pelican (Pelecanus crispus) present in "
      f"{len(DALMATIAN_YEARS)} of 16 years (<8):")
for y in DALMATIAN_YEARS:
    print(f"      {y}: {dalmatian_obs_per_year[y]} observation(s)")
print(bar)
