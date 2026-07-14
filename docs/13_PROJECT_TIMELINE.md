# PROJECT_TIMELINE.md

Version 2.0

## Purpose

A phased development plan. Structured in relative phases rather than
calendar dates, so it can be followed at whatever pace fits — the
sequencing and gates matter more than the specific duration of each
phase.

---

| Phase | Focus |
|---|---|
| 1 | Finalize species/habitat grouping with mentor. Get the species-specific Gujarat EBD extract cleaned. Build & test the filtering pipeline (`05_DATA_VALIDATION_PLAN.md` rules 1–8). |
| 2 | Compute detection rate + confirmed arrival/departure/peak week for all 11 quantitative species. Sanity-check outputs against personal field knowledge. |
| 3 | Set up GEE calls for ERA5 (temperature, rainfall) and MODIS NDVI. Join to observations. |
| 4 | Run correlation (H1) and trend (H2, H3) analysis. Generate Figures 1–8. |
| 5 | Dalmatian Pelican case study (Figure 9). **Freeze the pipeline — no further code changes after this phase.** |
| 6 | Write the paper, Sections 1–11, using `10_PAPER_OUTLINE.md`. |
| 7 | Mentor review. Write Discussion/Limitations/Future Work. Polish figures and tables. |
| 8 | Final proofread and review pass. |

---

## Milestones to Check In With Mentors

- End of Phase 1: cleaning pipeline runs, validation report numbers
  look sane.
- End of Phase 2: migration metrics computed for all species, at least
  one sanity-checked against personal experience.
- End of Phase 3: environmental data successfully joined, coverage
  percentage reported.
- End of Phase 4: all figures generated, hypothesis results drafted.
- End of Phase 5: pipeline frozen — this is a hard gate, not a
  suggestion. Freezing the pipeline before writing the paper avoids the
  common failure mode of still revising the analysis while trying to
  describe it in prose, which tends to produce inconsistencies between
  the code and the paper.

---

## If Time Is Constrained

Cut in this order, not randomly:
1. Drop the Streamlit dashboard stretch goal (it was never required).
2. Reduce Figure 8 (centroid map) to 2–3 species instead of all.
3. Shorten the Discussion's literature comparison.
4. Do not cut: Table 6 (Hypothesis Evaluation), the Dalmatian Pelican
   case study, or the Limitations section — these are the parts that
   make the paper honest and complete, not optional polish.
