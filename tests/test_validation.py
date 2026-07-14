"""Tests for src/validation.py + src/load_and_clean.py against the synthetic data.

Core assertion (per the task): the number of rows dropped by each rule equals the
number of "bad" rows the generator planted, read from synthetic_manifest.json so
nothing is hardcoded. Rules are 05_DATA_VALIDATION_PLAN.md 1-8.
"""

import pandas as pd

from src import validation as V


# --------------------------------------------------------------------------- #
# Per-rule drop counts on the OBSERVATION frame == planted bad rows (manifest)
# --------------------------------------------------------------------------- #

def test_rule_1_drops_all_historical(stage1, synthetic_manifest):
    planted = synthetic_manifest["planted_obs"]["rule_1_historical"]
    assert stage1.observations_report.drops["Rule 1 (Historical type)"] == planted


def test_rule_2_drops_out_of_period(stage1, synthetic_manifest):
    planted = synthetic_manifest["planted_obs"]["rule_2_total"]
    assert stage1.observations_report.drops["Rule 2 (outside 2010-2025)"] == planted


def test_rule_5_drops_non_gujarat(stage1, synthetic_manifest):
    planted = synthetic_manifest["planted_obs"]["rule_5_non_gujarat"]
    assert stage1.observations_report.drops["Rule 5 (STATE != Gujarat)"] == planted


def test_rule_6_drops_non_study_species(stage1, synthetic_manifest):
    planted = synthetic_manifest["planted_obs"]["rule_6_non_study_species"]
    assert stage1.observations_report.drops["Rule 6 (non-study species)"] == planted


def test_rule_7_drops_duplicates(stage1, synthetic_manifest):
    planted = synthetic_manifest["planted_obs"]["rule_7_duplicate"]
    assert stage1.observations_report.drops["Rule 7 (duplicate SEI+species)"] == planted


def test_rule_8_drops_out_of_bbox(stage1, synthetic_manifest):
    planted = synthetic_manifest["planted_obs"]["rule_8_out_of_bbox"]
    assert stage1.observations_report.drops["Rule 8 (coords outside bbox)"] == planted


# --------------------------------------------------------------------------- #
# Checklist-frame drop counts + Rule 3 effort exclusion == planted (manifest)
# --------------------------------------------------------------------------- #

def test_checklist_rule_2_drops_pre_and_post(stage1, synthetic_manifest):
    planted = (synthetic_manifest["planted_checklists"]["rule_2_pre2010"]
               + synthetic_manifest["planted_checklists"]["rule_2_post2025"])
    assert stage1.checklists_report.drops["Rule 2 (outside 2010-2025)"] == planted


def test_checklist_rule_5_and_8(stage1, synthetic_manifest):
    assert (stage1.checklists_report.drops["Rule 5 (STATE != Gujarat)"]
            == synthetic_manifest["planted_checklists"]["rule_5_non_gujarat"])
    assert (stage1.checklists_report.drops["Rule 8 (coords outside bbox)"]
            == synthetic_manifest["planted_checklists"]["rule_8_out_of_bbox"])


def test_rule_3_excludes_all_incidental_from_effort(stage1, synthetic_manifest):
    # Rule 3 does NOT drop rows; it excludes Incidental checklists from the effort
    # denominator, even when ALL SPECIES REPORTED == 1.
    planted = synthetic_manifest["planted_checklists"]["rule_3_incidental"]
    assert stage1.effort["rule_3_incidental_excluded"] == planted


# --------------------------------------------------------------------------- #
# Total accounting + the cleaned data actually passes every rule
# --------------------------------------------------------------------------- #

def test_observation_row_accounting(stage1):
    rep = stage1.observations_report
    assert rep.final_rows == rep.initial_rows - rep.total_dropped()
    assert len(stage1.clean_observations) == rep.final_rows


def test_clean_observations_satisfy_every_rule(stage1):
    obs = stage1.clean_observations
    # No Historical rows (Rule 1)
    assert not (obs["OBSERVATION TYPE"].str.casefold() == "historical").any()
    # All within study period (Rule 2)
    assert obs["year"].between(2010, 2025).all()
    # All in Gujarat (Rule 5)
    assert (obs["STATE"].str.casefold() == "gujarat").all()
    # Only study species, matched on scientific name (Rule 6)
    canon = {s.casefold() for s in V.STUDY_SPECIES_SCIENTIFIC}
    assert obs["SCIENTIFIC NAME"].str.strip().str.casefold().isin(canon).all()
    # Inside the bounding box (Rule 8)
    lat = pd.to_numeric(obs["LATITUDE"])
    lon = pd.to_numeric(obs["LONGITUDE"])
    assert lat.between(20.0, 24.7).all() and lon.between(68.0, 74.5).all()
    # No duplicate SEI + species (Rule 7)
    assert not obs.duplicated(
        subset=["SAMPLING EVENT IDENTIFIER", "SCIENTIFIC NAME"]).any()


def test_dalmatian_present_but_sparse(stage1, synthetic_manifest):
    obs = stage1.clean_observations
    dal_years = set(
        obs.loc[obs["SCIENTIFIC NAME"] == "Pelecanus crispus", "year"].dropna()
    )
    assert len(dal_years) == len(synthetic_manifest["dalmatian_years_present"])
    assert len(dal_years) < 8  # exercises the <8-year exclusion / low_confidence


def test_report_logs_a_count_for_every_rule(stage1):
    # Acceptance criterion: every exclusion rule is logged with a count.
    text = stage1.report_text
    for rule in ("Rule 1", "Rule 2", "Rule 5", "Rule 6", "Rule 7", "Rule 8"):
        assert rule in text
    assert "VALIDATION REPORT" in text


# --------------------------------------------------------------------------- #
# Rule 6 matches on SCIENTIFIC NAME, not COMMON NAME (05 Rule 6, unit-level)
# --------------------------------------------------------------------------- #

def test_rule_6_matches_scientific_name_not_common_name():
    df = pd.DataFrame({
        # Row A: right scientific name, garbled/regional common name -> KEEP.
        # Row B: a study-species COMMON name but a non-study SCIENTIFIC name -> DROP.
        "COMMON NAME": ["Pintail (regional variant)", "Northern Pintail"],
        "SCIENTIFIC NAME": ["Anas acuta", "Corvus splendens"],
    })
    kept, n_dropped = V.rule_6_study_species(df)
    assert n_dropped == 1
    assert kept["SCIENTIFIC NAME"].tolist() == ["Anas acuta"]


def test_rule_3_flags_incidental_even_when_all_species_reported():
    df = pd.DataFrame({
        "PROTOCOL NAME": ["Incidental", "Traveling"],
        "ALL SPECIES REPORTED": ["1", "1"],
    })
    flagged, n_incidental = V.rule_3_flag_incidental(df)
    complete = V.rule_4_complete_checklist_mask(df)
    eligible = complete & ~flagged["_is_incidental"]
    assert n_incidental == 1
    # The Incidental checklist is complete but must NOT be effort-eligible.
    assert eligible.tolist() == [False, True]
