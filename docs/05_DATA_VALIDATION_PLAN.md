# DATA_VALIDATION_PLAN.md

Version 2.0 — Scoped Edition

## Purpose

Cleaning and exclusion rules, informed directly by inspecting the
researcher's actual Gujarat eBird sampling-event extract
(`ebd_IN-GJ_unv_smp_relMay-2026_sampling.txt`, 244,752 checklists).
These are concrete, not hypothetical.

---

## Rule 1: Drop `Historical` observation type

**Finding:** The sample data contains records with `OBSERVATION TYPE =
Historical` and implausible dates (e.g. `1800-02-01`, `1885-10-24`,
`1898-12-16`). These are retrospective/mass-uploaded records, not
real-time field observations, and are not reliable for a timing
analysis.

**Rule:** Drop all rows where `OBSERVATION TYPE == "Historical"` before
any other processing.

---

## Rule 2: Restrict to study period

**Finding:** Checklist volume before 2010 is under 1,500/year — too
sparse for reliable annual metrics (see `01_RESEARCH_METHODOLOGY.md`).

**Rule:** Drop all rows where `OBSERVATION DATE` year is before 2010 or
after 2025.

---

## Rule 3: Exclude `Incidental` checklists from effort denominators

**Finding:** eBird's own convention treats `Incidental` checklists as
not representing a genuine, systematic search effort, regardless of the
`ALL SPECIES REPORTED` flag value.

**Rule:** When computing detection rate or observation density
denominators (total complete checklists), exclude rows where
`PROTOCOL NAME == "Incidental"`, even if `ALL SPECIES REPORTED == 1`.
Incidental records may still be used for raw sighting exploration, just
not in the effort-corrected metrics.

---

## Rule 4: Complete checklist filter

**Rule:** For all effort-based calculations, only use checklists where
`ALL SPECIES REPORTED == 1` (after Rule 3's Incidental exclusion). In the
sample data, 207,892 of 244,752 checklists (85%) meet this bar — a
healthy base.

---

## Rule 5: Geographic filter

**Rule:** `STATE == "Gujarat"`. Already true of the state-level extract;
re-verify if merging with the species-specific global download, which
will include many non-Gujarat records that must be filtered out before
use in the core analysis (see `06_DATA_SOURCES.md`).

---

## Rule 6: Species name standardization

**Rule:** Match on `SCIENTIFIC NAME`, not `COMMON NAME` (common names can
have regional variants). Cross-check every study species' scientific
name against eBird/Clements taxonomy before filtering, since taxonomic
splits/lumps can silently drop records under an outdated name.

---

## Rule 7: Duplicate records

**Rule:** Deduplicate by `SAMPLING EVENT IDENTIFIER` + species. If the
same checklist appears twice (e.g., shared checklists from group
outings), keep one.

---

## Rule 8: Coordinate validation

**Rule:** Reject rows with missing or clearly invalid latitude/longitude
(outside Gujarat's rough bounding box: lat 20–24.7°N, lon 68–74.5°E).

---

## Validation Report (generate this every run)

After cleaning, log and report:

- Total raw checklists: 244,752 (this extract)
- Dropped: Historical type, pre-2010/post-2025, invalid coordinates —
  report the count for each rule separately
- Remaining checklists, and remaining complete checklists
- Per-species: total confirmed observations per year, flagging any
  species-year with fewer than 2 (triggers `low_confidence` per
  `02_METRICS_METHODOLOGY.md`)

This becomes the "Data Quality" table/section in the paper (Table 4 in
`08_FIGURE_TABLE_PLAN.md`).

---

## Sanity-Check Step (replaces the original 7-level formal validation framework)

The original v1 spec had a formal 7-level scientific validation
framework appropriate for a PhD-level research platform. At this scope,
replace it with one practical step:

**After computing migration metrics for each species, the researcher
personally reviews the results against their own birding experience**
— does the computed arrival date for a familiar species/hotspot roughly
match what they've observed in the field? Document any
surprises or mismatches explicitly in the paper's Validation/Limitations
section; this is a legitimate and honest substitute for formal expert
review at this scope, and it's a genuine strength specific to this
researcher's project.

---

## Acceptance Criteria

- Every exclusion rule is logged with a count, not applied silently.
- The validation report numbers appear in the paper.
- The researcher can explain, for each rule, what would go wrong if it
  were skipped.
