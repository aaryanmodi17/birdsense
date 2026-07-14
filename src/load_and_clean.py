"""Stage 1: Load and Filter — implements 09_ETL_AND_ANALYSIS_ENGINE.md (Stage 1).

Steps (per the doc):
  1. Load both raw EBD files as pandas DataFrames (tab-delimited).
  2. Apply Rules 1, 2, 5, 6, 7, 8 from 05_DATA_VALIDATION_PLAN.md.
  3. Merge species observations with checklist metadata on SAMPLING EVENT IDENTIFIER.
  4. Derive year, month, iso_week from OBSERVATION DATE.

Every dropped record is counted per rule and surfaced in a ValidationReport, per
05_DATA_VALIDATION_PLAN.md's acceptance criteria ("logged with a count, not
applied silently"). Rules 3/4 (effort denominator) are applied to the checklist
frame as flags — they do not drop rows here (that belongs to Stage 2).
"""

import os
from dataclasses import dataclass, field

import pandas as pd

from . import validation as V

SEI = "SAMPLING EVENT IDENTIFIER"

_DEFAULT_RAW_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw"
)


@dataclass
class ValidationReport:
    """Per-rule drop counts + running totals for one frame (checklists or obs)."""

    frame_name: str
    initial_rows: int
    drops: dict = field(default_factory=dict)   # {"Rule 1: ...": n_dropped}
    final_rows: int = 0
    notes: list = field(default_factory=list)

    def total_dropped(self):
        return sum(self.drops.values())


@dataclass
class Stage1Result:
    clean_observations: pd.DataFrame
    clean_checklists: pd.DataFrame
    observations_report: ValidationReport
    checklists_report: ValidationReport
    effort: dict                       # Rule 3/4 summary (denominator eligibility)
    report_text: str


def load_raw(raw_dir=_DEFAULT_RAW_DIR):
    """Step 1: load the sampling-event and observation files (tab-delimited)."""
    sampling = pd.read_csv(
        os.path.join(raw_dir, "ebird_sampling_gujarat.txt"), sep="\t", dtype=str
    )
    observations = pd.read_csv(
        os.path.join(raw_dir, "ebird_observations_gujarat.txt"), sep="\t", dtype=str
    )
    return sampling, observations


def derive_date_parts(df, date_col="OBSERVATION DATE"):
    """Step 4: derive year, month, iso_week from OBSERVATION DATE
    (09_ETL_AND_ANALYSIS_ENGINE.md Stage 1, step 4)."""
    dt = pd.to_datetime(df[date_col], errors="coerce")
    out = df.copy()
    out["year"] = dt.dt.year.astype("Int64")
    out["month"] = dt.dt.month.astype("Int64")
    out["iso_week"] = dt.dt.isocalendar().week.astype("Int64")
    return out


def _clean_observations(obs):
    """Apply Rules 1, 2, 5, 6, 8, 7 to the species-observation frame (Stage 1)."""
    report = ValidationReport("observations", initial_rows=len(obs))
    obs, report.drops["Rule 1 (Historical type)"] = V.rule_1_drop_historical(obs)
    obs, report.drops["Rule 2 (outside 2010-2025)"] = V.rule_2_restrict_study_period(obs)
    obs, report.drops["Rule 5 (STATE != Gujarat)"] = V.rule_5_state_filter(obs)
    obs, report.drops["Rule 6 (non-study species)"] = V.rule_6_study_species(obs)
    obs, report.drops["Rule 8 (coords outside bbox)"] = V.rule_8_coordinate_filter(obs)
    # Rule 7 last, so we dedup only rows that survived every other rule.
    obs, report.drops["Rule 7 (duplicate SEI+species)"] = V.rule_7_deduplicate(
        obs, keys=(SEI, "SCIENTIFIC NAME")
    )
    report.final_rows = len(obs)
    return obs, report


def _clean_checklists(chk):
    """Apply the checklist-level rules (1, 2, 5, 8, 7) to the sampling frame, then
    flag effort eligibility via Rules 3 and 4. Rule 6 is N/A (no species column).
    """
    report = ValidationReport("checklists", initial_rows=len(chk))
    chk, report.drops["Rule 1 (Historical type)"] = V.rule_1_drop_historical(chk)
    chk, report.drops["Rule 2 (outside 2010-2025)"] = V.rule_2_restrict_study_period(chk)
    chk, report.drops["Rule 5 (STATE != Gujarat)"] = V.rule_5_state_filter(chk)
    chk, report.drops["Rule 8 (coords outside bbox)"] = V.rule_8_coordinate_filter(chk)
    chk, report.drops["Rule 7 (duplicate SEI)"] = V.rule_7_deduplicate(chk, keys=(SEI,))
    report.final_rows = len(chk)

    # Rules 3 & 4: effort-denominator eligibility (flags, not drops).
    chk, n_incidental = V.rule_3_flag_incidental(chk)
    complete_mask = V.rule_4_complete_checklist_mask(chk)
    chk["is_complete_for_effort"] = (complete_mask & ~chk["_is_incidental"]).to_numpy()
    chk = chk.drop(columns=["_is_incidental"])

    effort = {
        "rule_3_incidental_excluded": n_incidental,
        "rule_4_incomplete": int((~complete_mask).sum()),
        "effort_eligible_checklists": int(chk["is_complete_for_effort"].sum()),
    }
    return chk, report, effort


def _render_report(obs_report, chk_report, effort, n_orphans):
    lines = []
    bar = "=" * 74
    lines.append(bar)
    lines.append(" STAGE 1 VALIDATION REPORT  (05_DATA_VALIDATION_PLAN.md)")
    lines.append(bar)
    for rep in (chk_report, obs_report):
        lines.append(f"\n {rep.frame_name.upper()}  (raw rows: {rep.initial_rows:,})")
        for label, n in rep.drops.items():
            lines.append(f"   - dropped {n:>6,}   {label}")
        lines.append(f"   {'':>15}  ------")
        lines.append(f"   total dropped {rep.total_dropped():>6,}")
        lines.append(f"   remaining     {rep.final_rows:>6,}")
    lines.append("\n EFFORT DENOMINATOR (Rules 3 & 4 — flags, not row drops)")
    lines.append(f"   Rule 3: Incidental checklists excluded : "
                 f"{effort['rule_3_incidental_excluded']:,}")
    lines.append(f"   Rule 4: incomplete checklists          : "
                 f"{effort['rule_4_incomplete']:,}")
    lines.append(f"   effort-eligible complete checklists    : "
                 f"{effort['effort_eligible_checklists']:,}")
    lines.append(f"\n MERGE (on {SEI})")
    lines.append(f"   observations with no surviving checklist match: {n_orphans:,}")
    lines.append(bar)
    return "\n".join(lines)


def run_stage1(raw_dir=_DEFAULT_RAW_DIR):
    """Run Stage 1 end-to-end and return a Stage1Result.

    Implements 09_ETL_AND_ANALYSIS_ENGINE.md Stage 1 (load -> validate -> merge ->
    derive date parts) using the rules in 05_DATA_VALIDATION_PLAN.md.
    """
    sampling, observations = load_raw(raw_dir)

    clean_chk, chk_report, effort = _clean_checklists(sampling)
    clean_obs, obs_report = _clean_observations(observations)

    # Step 4: derive year/month/iso_week on both frames.
    clean_chk = derive_date_parts(clean_chk)
    clean_obs = derive_date_parts(clean_obs)

    # Step 3: merge species observations with checklist metadata on SEI. Attach
    # the effort-eligibility flag so downstream effort work (Stage 2) can use it.
    eff_flags = clean_chk[[SEI, "is_complete_for_effort"]]
    merged = clean_obs.merge(eff_flags, on=SEI, how="left")
    n_orphans = int(merged["is_complete_for_effort"].isna().sum())
    if n_orphans:
        obs_report.notes.append(
            f"{n_orphans} observations had no surviving checklist after cleaning"
        )

    report_text = _render_report(obs_report, chk_report, effort, n_orphans)
    return Stage1Result(
        clean_observations=merged,
        clean_checklists=clean_chk,
        observations_report=obs_report,
        checklists_report=chk_report,
        effort=effort,
        report_text=report_text,
    )


if __name__ == "__main__":
    result = run_stage1()
    print(result.report_text)
