# More watchers, not earlier birds: growth in observer effort generates spurious migration‑phenology trends in citizen‑science data for Gujarat's wintering waterbirds (2010–2025)

**Author:** [Your Name]¹  
**Mentorship:** data‑science/analytics mentors, TOPS Technologies²  
¹ Independent researcher, Gujarat, India · ² Ahmedabad, India  
*Corresponding author:* [your email]

*Implementation note:* the analysis pipeline was implemented with AI‑assisted coding (Claude, Anthropic) under the author's direction; all research questions, species and variable selection, and interpretation are the author's own (see Acknowledgements/Disclosure).

---

## Abstract

Citizen‑science platforms such as eBird are increasingly used as evidence that climate change is advancing bird‑migration timing. Using the complete eBird Basic Dataset for the Indian state of Gujarat (v1.16; 244,752 checklists; 2010–2025) and 12 wintering waterbird species, we test whether apparent changes in migration timing and abundance survive correction for observer effort. Over the study period, complete‑checklist effort grew ~303‑fold (and 4.2‑fold in the last five years alone). A naïve confirmed‑arrival metric shows a statistically significant advance ("earlier arrival") in **all 12 species** (slopes −0.4 to −1.6 days yr⁻¹; p < 0.05). This signal **vanishes completely (0/12)** when the timing metric is made effort‑robust (detection‑rate‑weighted peak week) and again (0/12) when a calendar‑boundary artifact is removed by a migration‑year reframing. The apparent advance is an artifact: arrival date is inversely tied to effort and, by 2021–2025, is **saturated at January 1 in all 12 species** — a signature no biological trend would produce. An apparent statewide abundance decline in Northern Pintail (detection rate 0.19→0.07) similarly disappears at fixed, consistently‑birded hotspots. Winter temperature itself showed **no significant trend** over the window (p = 0.39), so there was no warming exposure to invoke. We conclude that most apparent "change" in this rapidly growing citizen‑science record reflects the growth of observation, not the birds, and we describe diagnostics (effort‑robust metrics, calendar‑saturation checks, fixed‑location controls) to distinguish real signals from sampling artifacts.

**Keywords:** citizen science; eBird; observer effort; migration phenology; sampling bias; waterbirds; Gujarat; detection rate

---

## 1. Introduction

Migratory birds are widely treated as sensitive indicators of climate change, and a large literature reports advances in migration timing consistent with warming. Citizen‑science platforms, above all eBird (Sullivan et al., 2014), have made it possible to study these questions at continental scales, and validation work shows eBird can approximate migration phenology when compared with independent measures such as weather radar (Haas et al., 2022). At the same time, a persistent methodological concern is that eBird is *semi‑structured*: sampling effort and observer behaviour vary enormously in space and time, and can generate patterns that mimic ecological change (Callaghan et al., 2021; Johnston et al., 2021).

This tension matters because the naïve pipeline — "download eBird, compute arrival dates by year, fit a trend" — is easy, intuitive, and increasingly common, yet it does not, by itself, separate a change in the *birds* from a change in the *birdwatchers*. Here we ask a deliberately simple question for a well‑defined regional system: **do apparent changes in the migration timing and abundance of Gujarat's wintering waterbirds survive correction for the explosive growth of observer effort?** We use only correlation and linear‑trend analysis (no multiple regression), which we argue is the honest analytical ceiling for a presence‑only, single‑region dataset of this length. Our aim is not to overturn the climate‑phenology literature (which is dominated by *breeding*‑ground studies and structured data), but to show, with a clean worked example, how far a naïve citizen‑science analysis can mislead — and how to catch it.

## 2. Materials and Methods

### 2.1 Study area and species
The study area is the state of Gujarat, western India, a globally important wintering region for Palearctic waterbirds. We analysed 12 focal species spanning wetland‑dependent and grassland/dryland guilds (Table S4): Northern Pintail *Anas acuta*, Northern Shoveler *Spatula clypeata*, Garganey *Spatula querquedula*, Eurasian Wigeon *Mareca penelope*, Common Pochard *Aythya ferina*, Bar‑headed Goose *Anser indicus*, Greylag Goose *Anser anser*, Common Crane *Grus grus*, Demoiselle Crane *Grus virgo*, Greater Flamingo *Phoenicopterus roseus*, Great White Pelican *Pelecanus onocrotalus*, and Dalmatian Pelican *Pelecanus crispus*. All are wintering visitors to the region (they breed in Central Asia/Siberia), so the study concerns their non‑breeding phenology and occurrence.

### 2.2 Data and cleaning
We used the complete eBird Basic Dataset for Gujarat (release v1.16, May 2026): 244,752 checklists and ~5.3 million observation records across 546 species. Cleaning followed eight documented, individually‑logged rules (no silent exclusions): removal of "Historical" records (16,186 checklists) and records outside 2010–2025 (25,189), a Gujarat spatial filter, species matching on **scientific name** against the current eBird/Clements taxonomy, deduplication, and a coordinate bounding‑box check. A taxonomy reconciliation was required for Demoiselle Crane, which the current eBird taxonomy lists as *Grus virgo* (the older synonym *Anthropoides virgo* returns zero records and would have silently dropped ~8,300 observations — an instance of the very bias this paper concerns). After cleaning, 203,364 checklists remained usable; effort‑based analyses used **complete, non‑Incidental checklists** ("effort‑eligible").

### 2.3 Metrics
We computed, per species per year: (i) **detection rate** — the fraction of complete checklists reporting the species — the primary effort‑corrected occurrence metric; (ii) **confirmed arrival** — the date of the 2nd independent complete‑checklist record in the calendar year (a robustness rule against single vagrants); and (iii) **detection‑rate‑weighted peak week** — the ISO week with the highest weekly detection rate (species‑reporting complete checklists ÷ total complete checklists that week). Because the ISO‑week calendar splits the Nov–Feb winter at the December/January boundary (week 52↔1), we also computed peak week on a **migration‑year frame** (season starting 1 July), which renders the winter contiguous. For regression, date metrics were expressed as day‑of‑year.

### 2.4 Environmental covariates (Google Earth Engine)
Winter (Nov–Feb) mean temperature and total precipitation, and pre‑winter monsoon (Jun–Sep) precipitation, were extracted from ERA5 hourly reanalysis (Hersbach et al., 2020), aggregated to daily then seasonal values (temperature: mean; precipitation: sum). We used `ECMWF/ERA5/HOURLY` because the aggregated `ECMWF/ERA5/DAILY` product ends in 2020; ERA5‑Land was rejected because it masks open water and would null coastal/marine sites. Vegetation was indexed by MODIS MOD13Q1 NDVI (Didan, 2015); urbanization by VIIRS night‑time lights; surface‑water extent by the JRC Global Surface Water dataset (Pekel et al., 2016). All were accessed via Google Earth Engine (Gorelick et al., 2017).

### 2.5 Statistics
We used ordinary least‑squares linear trend (year → metric) and Pearson correlation (Spearman as a secondary non‑linearity check), with significance at α = 0.05. We deliberately did **not** use multiple regression or occupancy modelling; this keeps the analysis interpretable for a single‑region, presence‑only dataset, and we treat the absence of occupancy modelling as an explicit limitation (Section 5).

### 2.6 Reproducibility
The full pipeline (loading, cleaning, metrics, statistics, figure generation) is implemented in Python with unit tests and is publicly archived (Data & Code Availability). Every figure and table in this paper is regenerable from the raw data by re‑running the pipeline.

## 3. Results

### 3.1 Observer effort grew explosively — and is still accelerating
Effort‑eligible complete checklists rose from **133 (2010) to 40,288 (2025)**, a ~303‑fold increase; growth has not plateaued, with a further **4.2‑fold rise in the last five years** alone (2020→2025) (Figure 1; Table S1).

### 3.2 A naïve arrival metric shows a universal "earlier‑arrival" trend
Fitting a linear trend to confirmed arrival day‑of‑year yields a statistically significant advance in **all 12 species** (slopes −0.4 to −1.6 days yr⁻¹; all p < 0.05; Figure 2; Table S2). Read naïvely, this is a strong, taxon‑wide "climate signal."

### 3.3 The trend is an artifact of observer growth
The same species analysed with the **effort‑robust** detection‑rate‑weighted peak week show **0/12** significant trends; removing the December/January calendar‑boundary artifact via the migration‑year frame again yields **0/12** (Figure 3; Table S2). The mechanism is direct: confirmed arrival is inversely related to annual effort — as checklists multiply, a January‑1 record of a common wintering species becomes near‑certain, so the "2nd record of the year" slides earlier every year regardless of the birds (Figure 4). By 2021–2025, arrival day‑of‑year is **saturated at January 1 in all 12 species** (Table S3): the metric has hit the calendar floor and flat‑lined. This saturation at an artificial boundary is a diagnostic fingerprint of a sampling artifact — a genuine phenological trend has no reason to pile up at, and stop dead on, January 1.

### 3.4 An apparent abundance decline is also an artifact
Northern Pintail's Gujarat‑wide detection rate fell from 0.19 (2010) to 0.07 (2025), superficially a steep decline. However, at a fixed, consistently‑birded hotspot (Nal Sarovar) the species' detection rate is essentially flat (Figure 5). The statewide "decline" reflects **denominator inflation**: as eBird spread into checklists in non‑Pintail habitat, the fraction of all checklists reporting the species fell without any change where the species actually occurs.

### 3.5 There is no climatic driver to invoke
Winter mean temperature showed **no significant trend** across 2010–2025 (slope +0.02 °C yr⁻¹; p = 0.39; range ~1.3 °C; Figure 6). Winter and monsoon rainfall likewise showed no significant trend (Table S1). Thus, even setting aside the artifacts above, the local exposure variable most often invoked (warming) did not measurably change in the study window.

### 3.6 What survives correction
At fixed hotspots, effort‑corrected waterbird abundance was largely **stable** (few species with significant trends), i.e. no detectable change — a conclusion we can state with confidence rather than by omission. Two positive results are worth noting: Bar‑headed Goose detection rate at Thol Lake increased (~+82% over the period; p ≈ 0.01), a candidate real signal consistent with the species' documented regional expansion; and Dalmatian Pelican, often assumed too rare for quantitative treatment, was in fact well represented (12,444 records; confirmed in all 16 study years), overturning a common working assumption.

### 3.7 Urbanization is measurable but its impact is structurally hidden
Night‑time lights roughly doubled at focal wetlands over the decade (urbanization is real and measurable), yet effort‑corrected bird trends at those sites did not decline, and comparisons of protected vs. unprotected surviving wetlands showed no difference in trends. Crucially, an analysis targeting wetlands *lost* to urbanization found no signal for a structural reason: a wetland destroyed by development also stops being birded, so habitat loss and observation loss are confounded in presence‑only data (a survivorship bias that no filtering resolves). We therefore report urbanization impact as **undetectable with this data type**, not as absent.

## 4. Discussion

Across four independent lines of inquiry — migration timing, abundance, climate/rainfall association, and urbanization — the recurring result is the same: apparent "change" in Gujarat's eBird waterbird record is largely a function of a ~300‑fold growth in observation rather than of the birds. The central finding is quantitatively stark (12/12 → 0/12) and mechanistically transparent. Two features make it a useful cautionary example. First, the confound is *directional and predictable*: any metric whose value depends on how many checklists were submitted (naïve arrival dates; statewide detection‑rate denominators) will trend with effort. Second, the arrival metric exhibits a **saturation fingerprint** — it advances until it hits the January‑1 calendar floor and then flat‑lines — which distinguishes an artifact from biology and, importantly, warns that a naïve analyst inspecting only recent years would wrongly infer "stable timing" from a degenerate metric.

The observer‑effort problem is, of course, known in principle (Callaghan et al., 2021; Johnston et al., 2021; Thrikkadeeri & Viswanathan, 2024). Our contribution is (i) to demonstrate it with unusual clarity in a specific, well‑studied regional avifauna, (ii) to document the calendar‑saturation signature, and (iii) to provide a simple, reproducible battery of diagnostics — effort‑robust ratio metrics, migration‑year framing to remove calendar artifacts, and fixed‑location controls to remove spatial‑spread artifacts — that non‑specialists can apply before reading trends off citizen‑science data.

What can be concluded positively is modest but honest: for these 12 species over 2010–2025, we find **no detectable change in migration timing or in abundance at consistently‑monitored sites** once effort is accounted for; local winter climate did not measurably warm; and surviving wetlands are, so far, retaining their waterbird value.

## 5. Limitations

We flag these openly. (1) The confirmed‑arrival metric is a *naïve* choice for a wintering (non‑breeding) region and is used here precisely to demonstrate how such metrics fail — a careful phenologist would not adopt it. (2) The field‑standard remedy for detection bias is **occupancy/detection modelling** with effort covariates; we used ratio‑based correction for interpretability, and an occupancy‑model treatment is the natural next step. (3) The data are presence‑only, not standardized counts; questions such as wetland‑loss impact require structured programmes (e.g. the Asian Waterbird Census). (4) The 16‑year window and single region limit statistical power and generality. (5) Analyses are correlational; no causal claims are made.

## 6. Conclusion

Rapidly growing citizen‑science archives are transformative, but their growth is itself a powerful confound. In Gujarat's wintering waterbirds, a compelling "earlier‑arrival" signal (12/12 species) and an apparent abundance decline both dissolve under straightforward effort correction, and the local climate exposure did not change. The practical message is not that eBird is unreliable, but that naïve trend extraction from it is — and that a small set of diagnostics reliably separates real ecological signals from the footprint of the observers. We recommend that regional citizen‑science phenology analyses report an effort curve, use effort‑robust metrics, and test for calendar saturation and spatial‑spread artifacts before interpreting trends.

## Data and Code Availability
Raw data are freely available from eBird (ebird.org; Gujarat EBD, release relMay‑2026) under eBird's terms of use. All analysis code, tests, and figure‑generation scripts are archived at [GitHub/Zenodo DOI — insert]. Environmental covariates are public via Google Earth Engine.

## Acknowledgements and Disclosure
The author designed the study, selected species and variables, and interpreted all results, drawing on field experience as an active Gujarat eBirder. Technical mentorship was provided by data‑science/analytics mentors at TOPS Technologies. The analysis pipeline was implemented with AI‑assisted coding (Claude, Anthropic); the AI served as an implementation and debugging tool, not as a source of scientific judgement. We thank the eBird programme and its thousands of Gujarat contributors, whose effort — the very subject of this paper — makes such analysis possible.

## References
*(Verify each DOI before submission; landmark data/method papers are cited by their standard references.)*

- Callaghan, C. T., Poore, A. G. B., Hofmann, M., Roberts, C. J., & Pereira, H. M. (2021). Large‑bodied birds are over‑represented in unstructured citizen science data. *Scientific Reports*, 11, 19073. https://doi.org/10.1038/s41598-021-98584-7
- Didan, K. (2015). *MOD13Q1 MODIS/Terra Vegetation Indices 16‑Day L3 Global 250 m*. NASA LP DAAC. https://doi.org/10.5067/MODIS/MOD13Q1.006
- Gorelick, N., Hancher, M., Dixon, M., Ilyushchenko, S., Thau, D., & Moore, R. (2017). Google Earth Engine: Planetary‑scale geospatial analysis for everyone. *Remote Sensing of Environment*, 202, 18–27. https://doi.org/10.1016/j.rse.2017.06.031
- Haas, E. K., La Sorte, F. A., McCaslin, H. M., Belotti, M. C., & Horton, K. G. (2022). The correlation between eBird community science and weather‑surveillance‑radar‑based estimates of migration phenology. *Global Ecology and Biogeography*, 31, 2219–2230. https://doi.org/10.1111/geb.13567
- Hersbach, H., et al. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146, 1999–2049. https://doi.org/10.1002/qj.3803
- Johnston, A., Hochachka, W. M., Strimas‑Mackey, M. E., et al. (2021). Analytical guidelines to increase the value of community science data: An example using eBird data to estimate species distributions. *Methods in Ecology and Evolution*, 12, 1372–1385. https://doi.org/10.1111/2041-210X.13684
- Pekel, J.‑F., Cottam, A., Gorelick, N., & Belward, A. S. (2016). High‑resolution mapping of global surface water and its long‑term changes. *Nature*, 540, 418–422. https://doi.org/10.1038/nature20584
- Ramesh, V., Gupte, P. R., Tingley, M. W., Robin, V. V., & DeFries, R. (2022). Using citizen science to parse climatic and land‑cover influences on bird occupancy in a tropical biodiversity hotspot. *Ecography*, 2022, e06075. https://doi.org/10.1111/ecog.06075
- Robertson, E. P., La Sorte, F. A., Mays, J. D., et al. (2024). Decoupling of bird migration from the changing phenology of spring green‑up. *PNAS*, 121, e2308433121. https://doi.org/10.1073/pnas.2308433121
- Sullivan, B. L., Aycrigg, J. L., Barry, J. H., et al. (2014). The eBird enterprise: An integrated approach to development and application of citizen science. *Biological Conservation*, 169, 31–40. https://doi.org/10.1016/j.biocon.2013.11.003
- Thrikkadeeri, K., & Viswanathan, A. (2024). Despite short‑lived changes, the COVID‑19 pandemic had minimal large‑scale impact on citizen‑science participation in India. *Ornithological Applications*, 126, duae024. https://doi.org/10.1093/ornithapp/duae024

---

## Supporting Information — figures, and how they were prepared

All figures are generated by `paper/make_paper_figures.py` from the cleaned data; the underlying numbers are provided as CSVs in `paper/tables/`.

**Figures (in `paper/figures/`)**
- **Figure 1** `fig1_effort.png` — annual effort‑eligible complete checklists (log scale). *Prepared from:* Table S1, column `complete_checklists`.
- **Figure 2** `fig2_arrival_collapse.png` — confirmed‑arrival day‑of‑year vs year, per species, with OLS trend line; dotted line marks the Jan‑1 floor. *Prepared from:* per‑species (year, arrival day‑of‑year) pairs; trend statistics in Table S2.
- **Figure 3** `fig3_twelve_to_zero.png` — count of species with a significant "earlier" trend under three metrics (naïve arrival; effort‑robust calendar peak week; effort+wrap‑robust migration‑year peak week). *Prepared from:* Table S2 (p‑value columns; counts of p < 0.05).
- **Figure 4** `fig4_confound.png` — confirmed‑arrival day‑of‑year vs annual effort (log), all species‑years pooled. *Prepared from:* Table S1 (`complete_checklists`) joined to per‑species arrival day‑of‑year (Table S3).
- **Figure 5** `fig5_disappearing_decline.png` — Northern Pintail detection rate: Gujarat‑wide vs fixed hotspot (Nal Sarovar, 10 km). *Prepared from:* statewide detection rate (observer‑effort table) and hotspot detection rate (checklists/records within 10 km of 22.79 N, 72.03 E).
- **Figure 6** `fig6_temperature.png` — winter mean temperature by year with OLS trend (n.s.). *Prepared from:* Table S1 (`mean_winter_temperature`).

**Supporting tables (in `paper/tables/`)**
- **Table S1** `tableS1_annual_context.csv` — per year: complete checklists, winter temperature, winter rainfall, monsoon rainfall, winter NDVI.
- **Table S2** `tableS2_per_species_trends.csv` — per species: naïve arrival trend (slope, R², p, significance) and peak‑week trends on the calendar and migration‑year frames (slope, p). *This is the core evidence table for the 12→0 result.*
- **Table S3** `tableS3_arrival_doy_matrix.csv` — species × year matrix of confirmed‑arrival day‑of‑year (shows the slide to, and saturation at, Jan 1).
- **Table S4** `tableS4_species.csv` — the 12 study species: habitat guild, record count, and confirmed years (out of 16).
