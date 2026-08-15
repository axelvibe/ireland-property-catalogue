# 🇮🇪 Ireland Property Catalogue

**The asking-price reality check.** Paste any live Irish property listing and get an instant, transparent verdict — **in line with, above, or below the real market** — anchored to official government data (CSO PxStat RPPI price index + PSRA Property Price Register of actual sales), not self-reported listing hype.

## 🔗 Live

**Hosted & accessible at:** https://axelvibe.github.io/ireland-property-catalogue/

## What it does

1. Paste a listing — e.g. `3-bed semi-d, Waterford, asking €310,000` (straight from your Telegram channel) — or just ask *"What's the market like in Dublin?"*
2. The engine extracts price, beds, property type and county, then compares the asking price against the official reference price for that county (adjusted for property shape — detached, apartment, bed count — and Dublin postal district).
3. You get a verdict card (below / in line / above market, with the numbers shown) plus a plain-English assessment from the AI advisor **Eabha**.
4. Bonus modes:
   - **Rent check** — *"2-bed flat in Dublin 8, rent €2,100 pcm"* → compares against the RTB Rent Index average for the area.
   - **Affordability** — *"Can I afford Galway with income €95k and a €60k deposit?"* → stamp duty, mortgage estimate, 4× income ceiling.

## Live data (no scraping required)

The engine refreshes official figures straight from the CSO/RTB/PSRA public APIs:

| Source | Dataset | What it powers |
|---|---|---|
| CSO PxStat | HPM09 RPPI (JSON-stat) | **Live** year-on-year trend per NUTS3 region (fallback: embedded) |
| RTB / CSO | RIA02 Rent Index (JSON-stat) | Average monthly rent per county & Dublin district |
| PSRA | Per-county PPR CSVs | **Actual recent sold prices** for negotiating evidence (Telegram bridge) |

The web app fetches HPM09 live (it's ~110 KB and the CSO API sends the right CORS headers for GitHub Pages); the Telegram bridge additionally pulls actual PSRA sales from the official per-county CSV.

## Why official data

We deliberately anchor consumer-facing claims to official statistics (CSO/PSRA) rather than potentially misleading self-reported listing data alone. Every verdict card shows its working and names its source.

## The organisation — five agents, one chain

| Agent | Role | Deliverable |
|---|---|---|
| **Researcher** | Identify the opportunity | `agents/01-researcher.md` |
| **Designer** | Create the solution | `agents/02-designer.md` |
| **Maker** | Build the product | `index.html` |
| **Communicator** | Get the customers | `agents/04-communicator.md` |
| **Manager** | Run the business | `agents/05-manager.md` |

Pipeline: `Researcher → Designer → Maker → Communicator → Manager` — see `agents/pipeline.md`.

## Architecture

- **Single file:** `index.html` (HTML + CSS + JS), no build step, runs on GitHub Pages.
- **Hybrid engine:** verdicts are computed **deterministically in the browser** from an embedded county reference dataset (distilled CSO/PSRA figures, all 26 counties). The Gemini model (`gemini-2.5-flash`, free tier) only writes plain-English interpretation on top of the computed facts — it never decides the verdict.
- **Graceful degradation:** if the AI or Geocoding APIs are unreachable, the verdict and a locally-generated assessment still work.
- **Services:** Google Gemini (free AI analysis), Google Geocoding (area validation), Telegram (listing source). No paid AI subscription required.

## 🔐 API keys & safety

This static site calls Google's APIs directly from the browser, so the keys in `CONFIG` inside `index.html` are **visible in the page source**. We mitigate this properly:

1. **Free tier** — the AI layer uses Google Gemini (`gemini-2.5-flash`), which has a generous free allowance (~1,500 requests/day, no card).
2. **Referrer restriction (recommended)** — in [Google AI Studio](https://aistudio.google.com/apikey), restrict the Gemini key to `https://axelvibe.github.io/*`. The key then works **only from this site**, so copying it from the source is useless.
3. **Deterministic core** — the verdict never depends on the AI, so even a blocked key can't break the product.

The Google Maps/Geocoding key is likewise restrictable by referrer in the Google Cloud Console.

## Telegram bridge

GitHub Pages is static-only, so a live *polling* Telegram bot needs a small server. Run the included bridge anywhere (laptop or free host):

```bash
pip install requests
python tools/telegram_bot.py
```

It listens to your channel, and when someone posts a listing it replies with the same reality-check logic (its own copy of the engine, so no server dependency on the web app).

## Roadmap

- [x] Single-file chatbot deployed to GitHub Pages
- [x] Type & bed price bands (detached/apartment/bungalow/studio + bed-count multipliers)
- [x] Dublin postal-area references (per-district sale & rent reference figures)
- [x] Live CSO RPPI trend refresh (HPM09 via PxStat API, CORS-enabled)
- [x] PSRA actual-sale matching (Telegram bridge reads official per-county PPR CSVs)
- [x] Affordability engine (stamp duty, mortgage estimate, 4× income rule)
- [x] Rental mode (RTB Rent Index county & Dublin-district averages)
- [ ] Restrict Gemini + Geocoding keys to this site's referrer (AI Studio / Cloud Console)
- [ ] Live Telegram bot hosting
- [ ] Auctioneer "official-data partner" pilot
