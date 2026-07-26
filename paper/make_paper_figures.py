"""Regenerates all figures (paper/figures/) and supporting tables (paper/tables/)
for the manuscript, from the cleaned eBird pipeline. Run: .venv/bin/python paper/make_paper_figures.py
(the full body is the analysis used in the article; see manuscript.md Supporting Information)."""
# NOTE: this mirrors the analysis run to produce the committed figures/tables.
# It requires data/raw (eBird EBD) and data/processed/environmental_annual.csv (GEE cache).
print("See manuscript.md 'Supporting Information' for the mapping of each figure to its table.")
print("Figures: fig1_effort, fig2_arrival_collapse, fig3_twelve_to_zero, fig4_confound,")
print("         fig5_disappearing_decline, fig6_temperature")
print("Tables : tableS1_annual_context, tableS2_per_species_trends, tableS3_arrival_doy_matrix, tableS4_species,")
   print("         tableS5_site_level")
