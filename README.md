# BirdSense: Migration Timing of Wintering Waterbirds in Gujarat

**Research question:** Have migration timing and spatial distribution of selected
wintering waterbirds in Gujarat changed between 2010 and 2025, and are those
changes associated with temperature, rainfall, or vegetation/habitat trends —
after correcting for the substantial rise in eBird observer activity over the
same period?

## How to run

_Placeholder — to be filled in._

```
pip install -r requirements.txt
# then run the notebooks in notebooks/ in order (01 → 06)
```

## AI & mentor disclosure

This project's implementation used **AI-assisted coding (Claude, by Anthropic)**
for writing and debugging the Python data pipeline and statistical analysis code,
guided throughout by the researcher's own research design decisions. Technical
mentorship was provided by data-science/analytics mentors at **TOPS
Technologies**. The research question, hypotheses, species and variable
selection, and interpretation of results were the researcher's own. See
`docs/12_AI_AND_MENTOR_DISCLOSURE.md` for the full statement.

## Data note

The pipeline runs on the **real eBird Basic Dataset** for Gujarat (EBD v1.16,
May 2026 release), extracted to `data/raw/` (gitignored). The **environmental
variables (temperature, rainfall, NDVI) are still MOCK placeholders** until
Google Earth Engine is authenticated — so H1 / temperature results are not real
yet. See `scripts/test_gee_5points.py` for the GEE authentication steps.

See `docs/` for the full specification (source of truth).
