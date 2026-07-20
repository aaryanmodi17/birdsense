# BirdSense — Plain‑English Summary of the Whole Research Effort

*A walkthrough of every experiment we ran, how we ran it, and what we found — written so anyone can follow it.*

## The big idea in one paragraph
I wanted to know whether climate change is changing how migratory waterbirds use Gujarat — are they arriving earlier, moving, or declining? I used 16 years of eBird data (birdwatchers' checklists) plus satellite climate and habitat data. The twist: I discovered that **almost every "change" I could find was really caused by the huge growth in the number of birdwatchers, not by the birds.** The main scientific contribution is a method to tell real change apart from this illusion — and an honest finding that, once corrected, there's no detectable change in these birds' timing or numbers, and the local climate didn't actually warm.

---

## Experiment 1 — Building a clean, trustworthy dataset
**What we wanted:** a reliable base to analyse.
**How we did it:** Downloaded the full eBird dataset for Gujarat — **244,752 checklists and ~5.3 million bird records across 546 species**. Wrote a cleaning pipeline with 8 rules that each *log how many records they remove* (nothing is dropped silently): remove old "Historical" mass‑uploads, keep 2010–2025, keep Gujarat, match species by scientific name, remove duplicates, remove bad GPS points.
**What we found / did:** ~203,000 usable checklists. We also caught a taxonomy trap: Demoiselle Crane is now *Grus virgo* in eBird, not the older *Anthropoides virgo* the plan used — using the old name would have silently deleted ~8,300 records. (A small but perfect example of the kind of hidden bias the whole project is about.)
**Why it matters:** Everything downstream is only as good as the cleaning. This is the unglamorous 80% of real data science.

## Experiment 2 — Measuring the birdwatching explosion
**What we wanted:** to quantify how much observer effort grew.
**How we did it:** Counted complete, serious checklists per year.
**What we found:** From **133 checklists in 2010 to 40,288 in 2025 — a 303× increase.** And it hasn't slowed: it grew **4.2× in just the last five years.** (Figure 1)
**Why it matters:** This growth is the hidden force behind almost every "trend" we later found.

## Experiment 3 — The exciting (but false) result: "birds are arriving earlier"
**What we wanted:** to test if arrival timing has shifted.
**How we did it:** For each species each year, took the "confirmed arrival" (2nd sighting of the year, to avoid one‑off flukes) and fit a trend line.
**What we found:** **All 12 species show a statistically significant "earlier arrival."** (Figure 2) If we'd stopped here, we'd have published a textbook climate‑change story.
**Why it matters:** This is exactly the result many people report from eBird — and it's a trap.

## Experiment 4 — Stress‑testing it: is it real, or just more watchers?
**What we wanted:** to check whether the "earlier arrival" survives correction for effort.
**How we did it:** Re‑ran the analysis using an **effort‑robust metric** — the "peak week," measured as the *fraction* of checklists reporting the bird (a fraction cancels out the growing number of checklists). 
**What we found:** The signal **completely vanished — 0 of 12 species** (Figure 3). We also found *why*: with 40,000 checklists, there's almost always a January‑1 sighting of a common bird, so the "2nd sighting of the year" gets pushed to early January purely because more people are looking. Arrival date drops as effort rises (Figure 4).
**Why it matters:** This is the heart of the paper — the flashy result was an illusion created by the observers.

## Experiment 5 — Fixing a hidden calendar glitch (Dec/Jan wrap)
**What we wanted:** to make sure the "peak week" test wasn't itself distorted.
**How we did it:** Noticed that the calendar splits winter at Dec 31/Jan 1 (week 52 vs week 1 look 51 weeks apart though they're days apart). Rebuilt the "peak week" on a **migration year starting July 1**, so winter is one continuous block.
**What we found:** The two split clusters merged into one (verified on Greylag & Bar‑headed Goose), and the timing signal was **still 0 of 12.** The correction didn't rescue any hidden signal.
**Why it matters:** Shows we ruled out an alternative explanation instead of stopping at a convenient answer.

## Experiment 6 — The "last 5 years" check (does the illusion fade?)
**What we wanted:** maybe effort growth was a 15‑year thing and recent data is cleaner?
**How we did it:** Repeated the checks on 2021–2025 only.
**What we found:** Effort was **still exploding (4.2× in 5 years)**, and arrival is now **stuck at January 1 for all 12 species** — it hit the calendar floor and flat‑lined. So the naïve metric isn't trustworthy in recent years either; it's *degenerate* (carries no information).
**Why it matters:** A "saturation at the calendar floor" is a fingerprint of an artifact — a real biological trend wouldn't pile up on Jan 1 and stop.

## Experiment 7 — A second illusion: the "disappearing decline"
**What we wanted:** to check an apparent population crash in Northern Pintail (detection dropped 0.19 → 0.07).
**How we did it:** Compared the statewide number to the *same bird at one fixed, always‑watched lake* (Nal Sarovar).
**What we found:** At the fixed lake, Pintail is **flat** (Figure 5). The statewide "decline" was caused by birdwatchers spreading into places pintails don't live, diluting the average — not by fewer birds.
**Why it matters:** A second, independent worked example of the same lesson.

## Experiment 8 — Did the weather actually change?
**What we wanted:** to test the assumed cause (warming).
**How we did it:** Pulled winter temperature and rainfall from ERA5 satellite reanalysis (via Google Earth Engine) for every year.
**What we found:** **Winter temperature did not significantly change** (Figure 6, p = 0.39; total range ~1.3 °C). Rainfall didn't either.
**Why it matters:** You can't blame warming for a bird change if the warming didn't happen in your window. This is a crucial honesty point.

## Experiment 9 — The three original hypotheses (H1–H3)
- **H1 (warmer winters → earlier arrival):** Not supported — no association, and no warming to test.
- **H2 (timing changed):** Only in the naïve (artifact) metric; not in the robust one.
- **H3 (wetland vs dryland species differ):** No meaningful difference.

## Experiment 10 — Rainfall, monsoon, and wetland water
**What we wanted:** does rain drive the birds?
**How we did it:** Tested winter rain, then the **monsoon (Jun–Sep) rain** that actually fills wetlands, and JRC satellite **water‑extent** at two major lakes.
**What we found:** No consistent signal statewide. One interesting hint: at Thol Lake, ducks were *less* detected in wet years (they may spread out when water is everywhere; concentrate in dry years) — suggestive, not proven. Lake water extent did **not** predict bird numbers.
**Why it matters:** Shows we tested the mechanistically‑correct variable (monsoon, not winter rain) and still found no clean effect.

## Experiment 11 — Urbanization, tested four ways
**What we wanted:** the original motivation — is the city expansion hurting the birds?
**How we did it:** (a) NDVI vegetation trend; (b) **night‑time lights** (the standard urbanization measure) at the wetlands; (c) protected vs. unprotected wetlands; (d) a "**lost‑wetlands**" test using satellite water‑loss + rising lights.
**What we found:** Urbanization is **real and measurable** — night lights roughly *doubled* at the wetlands. But we could **not** show an impact on the birds. The deepest reason (the "lost‑wetlands" test) is a catch‑22: when a wetland is destroyed, the birdwatchers leave too, so the destroyed sites simply vanish from the data. This is a **structural blind spot of citizen‑science data**, not a lack of trying.
**Why it matters:** An honest, sophisticated conclusion: we can measure urbanization, but presence‑only data cannot prove its impact — you'd need standardized counts (like the Asian Waterbird Census).

## Experiment 12 — Rare birds and cyclones (exploratory only)
**What we wanted:** do storms blow rare seabirds into Gujarat?
**How we did it:** Found 79 genuinely rare species; extracted 64 seabird‑vagrant records; tested each against satellite wind, matched to the same place/season in other years.
**What we found:** Vagrant days were windier than normal (17/21, p = 0.004), and frigatebirds appeared 2 days after Cyclone Tauktae (wind 19.8 vs ~4.6 m/s). **But** this is confounded (birders go looking after storms) and based on few events — so it's *suggestive, not conclusive*. We deliberately left it out of the main paper as future work.
**Why it matters:** Shows the discipline to *not* publish an exciting‑but‑shaky result.

## What we CAN say with confidence (the honest positives)
- After correcting for effort, there is **no detectable change** in these 12 species' migration timing or abundance, 2010–2025 — a clean, defensible baseline.
- Local winter climate **did not measurably warm** in the window.
- Surviving, well‑watched wetlands are **holding their waterbird value**.
- Two concrete findings: **Bar‑headed Goose is increasing at Thol Lake** (+82%), and **Dalmatian Pelican is not rare here** (12,444 records; present all 16 years) — correcting a common assumption.

## The one‑sentence takeaway
> **Most of the "change" you'd naïvely read out of 16 years of Gujarat eBird data is really the explosive growth of birdwatching, not the birds — and here is the method that tells the two apart.**
