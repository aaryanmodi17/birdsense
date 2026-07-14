"""Validation rules — implements 05_DATA_VALIDATION_PLAN.md (Rules 1-8).

Each rule is a small, pure function that takes a pandas DataFrame and returns a
result; drop-rules return ``(kept_df, n_dropped)`` so the caller can LOG THE
COUNT REMOVED BY EACH RULE (05_DATA_VALIDATION_PLAN.md acceptance criteria:
"Every exclusion rule is logged with a count, not applied silently").

Rules 1, 2, 5, 6, 7, 8 remove rows. Rules 3 and 4 do NOT remove rows: per the
doc they govern the *effort denominator* only (Incidental records "may still be
used for raw sighting exploration, just not in the effort-corrected metrics"),
so they are expressed as flags/masks and consumed in Stage 2.
"""

import pandas as pd

# Gujarat rough bounding box — 05_DATA_VALIDATION_PLAN.md Rule 8.
GUJARAT_BBOX = {"lat_min": 20.0, "lat_max": 24.7, "lon_min": 68.0, "lon_max": 74.5}

# Canonical study-species table — 01_RESEARCH_METHODOLOGY.md. Single source of
# truth for the species identity + H3 habitat grouping (07_DATABASE_SCHEMA.md:
# species.habitat_category). Habitat values: 'wetland' | 'grassland_dryland'.
# Rule 6 matches on SCIENTIFIC NAME, never COMMON NAME.
HABITAT_WETLAND = "wetland"
HABITAT_DRYLAND = "grassland_dryland"

STUDY_SPECIES = [
    {"common": "Northern Pintail",   "scientific": "Anas acuta",            "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Northern Shoveler",  "scientific": "Spatula clypeata",      "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Garganey",           "scientific": "Spatula querquedula",   "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Eurasian Wigeon",    "scientific": "Mareca penelope",       "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Common Pochard",     "scientific": "Aythya ferina",         "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Bar-headed Goose",   "scientific": "Anser indicus",         "habitat": HABITAT_DRYLAND, "analysis": "full"},
    {"common": "Greylag Goose",      "scientific": "Anser anser",           "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Common Crane",       "scientific": "Grus grus",             "habitat": HABITAT_DRYLAND, "analysis": "full"},
    # 05 Rule 6 taxonomy reconciliation: the May 2026 eBird release (v1.16) uses
    # 'Grus virgo' for Demoiselle Crane; doc 01 lists the synonym 'Anthropoides
    # virgo', which matches 0 records in the real data. Using the eBird name keeps
    # the ~8k Gujarat records (a core H3 grassland/dryland species).
    {"common": "Demoiselle Crane",   "scientific": "Grus virgo",            "habitat": HABITAT_DRYLAND, "analysis": "full"},
    {"common": "Greater Flamingo",   "scientific": "Phoenicopterus roseus", "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Great White Pelican","scientific": "Pelecanus onocrotalus", "habitat": HABITAT_WETLAND, "analysis": "full"},
    {"common": "Dalmatian Pelican",  "scientific": "Pelecanus crispus",     "habitat": HABITAT_WETLAND, "analysis": "case_study"},
]

# Ordered scientific-name list, derived from the table above (single source).
STUDY_SPECIES_SCIENTIFIC = [s["scientific"] for s in STUDY_SPECIES]

STUDY_PERIOD_START = 2010
STUDY_PERIOD_END = 2025


def _norm(series):
    """Lower-cased, stripped string view of a column (robust to whitespace/case)."""
    return series.astype("string").str.strip().str.casefold()


def rule_1_drop_historical(df, obs_type_col="OBSERVATION TYPE"):
    """Rule 1 (05_DATA_VALIDATION_PLAN.md): drop OBSERVATION TYPE == 'Historical'.

    Applied before any other processing. Returns (kept_df, n_dropped).
    """
    drop_mask = _norm(df[obs_type_col]) == "historical"
    return df.loc[~drop_mask].copy(), int(drop_mask.sum())


def rule_2_restrict_study_period(df, date_col="OBSERVATION DATE",
                                 start=STUDY_PERIOD_START, end=STUDY_PERIOD_END):
    """Rule 2 (05_DATA_VALIDATION_PLAN.md): drop OBSERVATION DATE year < 2010 or
    > 2025 (and unparseable dates). Returns (kept_df, n_dropped).
    """
    years = pd.to_datetime(df[date_col], errors="coerce").dt.year
    drop_mask = years.isna() | (years < start) | (years > end)
    return df.loc[~drop_mask].copy(), int(drop_mask.sum())


def rule_3_flag_incidental(df, protocol_col="PROTOCOL NAME"):
    """Rule 3 (05_DATA_VALIDATION_PLAN.md): mark Incidental checklists as excluded
    from effort denominators — even when ALL SPECIES REPORTED == 1. Does NOT drop
    rows. Returns (df_with_'_is_incidental'_column, n_incidental).
    """
    is_incidental = _norm(df[protocol_col]) == "incidental"
    out = df.copy()
    out["_is_incidental"] = is_incidental.fillna(False).to_numpy()
    return out, int(is_incidental.sum())


def rule_4_complete_checklist_mask(df, all_reported_col="ALL SPECIES REPORTED"):
    """Rule 4 (05_DATA_VALIDATION_PLAN.md): a complete checklist has
    ALL SPECIES REPORTED == 1. Used for effort calculations only (does NOT drop
    rows). Returns a boolean Series aligned to df.
    """
    return _norm(df[all_reported_col]).isin(["1", "1.0", "true"]).fillna(False)


def rule_5_state_filter(df, state_col="STATE", state="Gujarat"):
    """Rule 5 (05_DATA_VALIDATION_PLAN.md): keep only STATE == 'Gujarat'.

    Returns (kept_df, n_dropped).
    """
    drop_mask = _norm(df[state_col]) != state.casefold()
    return df.loc[~drop_mask].copy(), int(drop_mask.sum())


def rule_6_study_species(df, sci_col="SCIENTIFIC NAME",
                         species=STUDY_SPECIES_SCIENTIFIC):
    """Rule 6 (05_DATA_VALIDATION_PLAN.md): match on SCIENTIFIC NAME (NOT COMMON
    NAME); keep only the 12 study species. Returns (kept_df, n_dropped).
    """
    canon = {s.casefold() for s in species}
    drop_mask = ~_norm(df[sci_col]).isin(canon)
    return df.loc[~drop_mask].copy(), int(drop_mask.sum())


def rule_7_deduplicate(df, keys=("SAMPLING EVENT IDENTIFIER", "SCIENTIFIC NAME")):
    """Rule 7 (05_DATA_VALIDATION_PLAN.md): deduplicate by SAMPLING EVENT
    IDENTIFIER + species; keep one. (For the checklist frame, pass keys with just
    the SAMPLING EVENT IDENTIFIER.) Returns (kept_df, n_dropped).
    """
    before = len(df)
    out = df.drop_duplicates(subset=list(keys), keep="first").copy()
    return out, before - len(out)


def rule_8_coordinate_filter(df, lat_col="LATITUDE", lon_col="LONGITUDE",
                             bbox=GUJARAT_BBOX):
    """Rule 8 (05_DATA_VALIDATION_PLAN.md): reject rows with missing or invalid
    lat/lon outside Gujarat's bounding box (lat 20-24.7 N, lon 68-74.5 E).
    Returns (kept_df, n_dropped).
    """
    lat = pd.to_numeric(df[lat_col], errors="coerce")
    lon = pd.to_numeric(df[lon_col], errors="coerce")
    inside = (
        lat.between(bbox["lat_min"], bbox["lat_max"])
        & lon.between(bbox["lon_min"], bbox["lon_max"])
    )
    drop_mask = ~inside  # NaN coordinates are not "inside" -> dropped
    return df.loc[~drop_mask].copy(), int(drop_mask.sum())
