# PAPER_OUTLINE.md

Version 2.0 — Scoped Edition

## Purpose

Section-by-section structure for the final paper, trimmed from the
original v1 RESEARCH_PAPER_BLUEPRINT.docx (16 sections plus appendices)
to what fits this project's scope.

---

## Title

Working title: something concrete, not generic — e.g. "Migration Timing
Shifts in Wintering Waterbirds of Gujarat, 2010–2025: An Observer-Effort-
Corrected Analysis." Finalize after results are in; the real finding
often makes a better title than a pre-written one.

## Abstract (200–250 words, write last)

Background, question, method in one sentence, key finding for each of
H1–H3, one-sentence conclusion.

## 1. Introduction

Migration ecology basics, Gujarat's role in the Central Asian Flyway,
why citizen-science data (eBird) is valuable but needs effort
correction, the gap this project addresses. Include 1–2 sentences of
personal framing — why you, as a birder, noticed this and wanted to
check it against data. That personal thread is a genuine strength of
the paper; don't strip it out to sound more "formal."

## 2. Research Question and Hypotheses

State the question and H1–H3 exactly as in `00_PROJECT_CHARTER.md`.

## 3. Study Area

Gujarat, key wetlands (Nal Sarovar, Little Rann of Kutch, others you
know personally), Central Asian Flyway context. Figure 1.

## 4. Study Species

Table 1. Brief note on why these 12, and the habitat-category grouping
used for H3.

## 5. Data Sources

Table 2. eBird + ERA5 + MODIS, briefly.

## 6. Methodology

Summarize the pipeline: cleaning rules, observer-effort correction,
confirmed arrival/departure logic, detection-rate-weighted peak week,
correlation/trend approach. This section can be relatively short in the
paper body — point to an appendix or the code repository for full
detail rather than reproducing all of `02`–`04` here verbatim.

## 7. Results — Data Quality and Observer Effort

Table 3, Figure 2. This is where the 30x growth number lands — it's a
genuinely striking, real statistic.

## 8. Results — Migration Timing Trends (H2)

Figures 3, 4, 5. Table 4.

## 9. Results — Environmental Correlation (H1)

Figure 6. Table 5.

## 10. Results — Habitat Category Comparison (H3)

Figure 7, Figure 8. This is the section to spend the most narrative
effort on — it's the project's original contribution.

## 11. Dalmatian Pelican Case Study

Figure 9. Short, qualitative, honest about data limits.

## 12. Discussion

Interpret H1–H3 together (Table 6). Compare briefly to published
migration-ecology literature if time allows (not required at this
scope, but strengthens the paper). Discuss what surprised you, if
anything, relative to your own field experience.

## 13. Limitations

From `01_RESEARCH_METHODOLOGY.md`'s Limitations section — state them
plainly, don't bury them in a single vague sentence.

## 14. Future Work

The cut hypotheses (rainfall-residence, NDVI-occurrence,
wetland-hotspot), the cut variables (land cover, surface water), formal
regression as a next step, extending past 2025.

## 15. Conclusion

Answer the research question directly, in plain language.

## References

Consistent citation style. Include eBird, ERA5, MODIS as data citations,
plus any ecology literature referenced in the Discussion.

## Appendix

Full metric definitions (point to `02_METRICS_METHODOLOGY.md`), full
data validation report, methodology notes on AI-assisted implementation
(see `12_AI_AND_MENTOR_DISCLOSURE.md`).

---

## What Changed from v1's 16-Section Blueprint

- Removed separate "Results" sections for each individual environmental
  variable (Temperature Trends, Rainfall Trends, NDVI Trends as
  standalone sections) — folded into Sections 8–10, since 3 hypotheses
  don't need that much separate scaffolding.
- Removed the standalone "Validation" chapter — folded into Methodology
  and Limitations, since the formal 7-level validation framework was
  cut from scope (`05_DATA_VALIDATION_PLAN.md`).
- Kept the personal/narrative framing explicit in Section 1 and 12,
  which the original platform-oriented blueprint didn't emphasize.

---

## Acceptance Criteria

- Every section references a specific figure/table, not a vague
  description.
- Table 6 (Hypothesis Evaluation) and the Conclusion agree with each
  other — don't let the prose overstate what the table shows.
