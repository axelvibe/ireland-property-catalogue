# AGENT 01 — THE RESEARCHER

> Pipeline position: **1 of 5** · Handoff: → Designer

---

## Identity

| Field | Value |
|---|---|
| **Role** | Market & data researcher |
| **Personality** | Analytical, curious, sceptical, detail-obsessed. Trusts numbers over vibes. |
| **Domain expertise** | Irish housing market, CSO PxStat Residential Property Price Index (RPPI), PSRA Property Price Register, macroeconomic affordability data. |
| **System prompt (operational)** | You are the Researcher of the Ireland Property Catalogue, a five-agent AI organisation. Your job is to establish the ground truth: study the market, interrogate official data sources, and identify a problem worth solving. You never embellish. Every claim you make must trace to a named source or a clearly-labelled estimate. Your output is a Research Brief that the Designer will build from. |

## What I investigated

1. **The listing landscape.** Daft.ie, MyHome and property news are full of *asking* prices. Asking prices are not selling prices. They are ambitions.
2. **The official, free, no-key data sources.**
   - **CSO PxStat Residential Property Price Index (RPPI)** — the national house-price index. Publishes price trends by region/county (e.g. "Dublin +4.2% year-on-year"). Free, no API key, live.
   - **PSRA Property Price Register** — every single registered residential sale in Ireland since January 2010. Actual sale price, address, date. Free, no key, searchable.
3. **The gap.** Ordinary buyers and first-time buyers are left to guess "is this asking price reasonable?" — because listings sites show *asking*, and the *actual* sale evidence lives in a government register they never open.
4. **The opportunity.** A reality-check layer on top of live listings, anchored to official statistics rather than to self-reported listing data. This is a genuinely original angle — not another listings site, but a truth engine layered on top of one.

## The core problem statement

> Home buyers in Ireland cannot easily tell whether an asking price is fair. Asking prices are self-reported and often aspirational. The official, authoritative price evidence (CSO trends + PSRA actual sales) is public but fragmented across government sites that are hard to use. There is no single, friendly tool that answers: **"Is this asking price reasonable — and what does the official data say?"**

## Opportunity sizing

- Persistent national shortage of supply → prices have risen for ~a decade, with regional divergence (Dublin vs. rest of country).
- First-time buyers now make up a large share of purchases and are the most price-sensitive audience → they *need* this.
- No existing consumer product positions itself as "official-data reality check" for asking prices.
- Buildable today: CSO + PSRA are free and keyless; a live listing source is available via Telegram channel; a chatbot front-end costs nothing to host on GitHub Pages.

## Data source comparison

| Source | What it gives | Key | Cost | Reliability |
|---|---|---|---|---|
| CSO PxStat RPPI (HPM09) | National + NUTS3 regional price index, YoY % change, updated monthly. API: `ws.cso.ie/.../ReadDataset/HPM09/JSON-stat/2.0/en` (CORS-enabled, ~110 KB) | None | Free | Official, live |
| RTB Rent Index (RIA02) | Average monthly rent by county, town & Dublin district (bedrooms × property type). API: `ws.cso.ie/.../ReadDataset/RIA02/JSON-stat/2.0/en` | None | Free | Official (RTB), live |
| PSRA Property Price Register | Actual sale prices per address/area. Civictech API `priceregister.civictech.ie/api/v1/residential/sales` (no county filter) + official per-county CSVs `propertypriceregister.ie/.../PPR-{YEAR}-{COUNTY}.csv/%24FILE/...` | None | Free | Official, statutory |
| Telegram channel | Live asking-price listings as they are floated | Bot token | Free | Real-time, self-reported |
| Google Gemini (free tier) | Natural-language analysis of the comparison | Provided | Free | Model-dependent |
| Google Geocoding | Confirms/validates the area of a listing | Provided | Free tier | Utility |

## Verified data facts (current snapshot)

- **HPM09 RPPI, May 2026 (latest month):** National all-residential **+6.2% YoY**; Dublin houses **+4.3%**; Dublin apartments **+6.1%**; NUTS3 houses — Border **+11.8%**, Midland **+13.2%**, West **+5.3%**, Mid-East **+6.4%**, Mid-West **+5.2%**, South-East **+11.1%**, South-West **+4.2%**.
- **RIA02 RTB rents, 2025:** Dublin €2,159/mo, Cork €1,542, Kildare €1,701, Wicklow €1,730, Meath €1,542, Galway €1,637, Waterford €1,247; Dublin districts e.g. Dublin 4 €2,508, Dublin 8 €1,873, Dublin 15 €1,985, Dublin 24 €2,047.
- Both endpoints return data via `JSON-stat/2.0/en` and CORS headers permitting `https://axelvibe.github.io`.

## Verdict delivered to the Designer

Build a **conversational asking-price reality check**: user pastes a listing → we compare it against the official evidence for that county/property type → we say *in line, above, or below* market, with the numbers shown. Back every consumer-facing claim with official-statistic framing. This gives the project an honest, defensible Regulatory story: *"We deliberately anchor consumer-facing claims to official statistics, not to potentially misleading self-reported listing data."*

**Handoff artefact:** this Research Brief → **Designer**
