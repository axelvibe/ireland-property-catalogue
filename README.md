# 🇮🇪 Ireland Property Catalogue

**The asking-price reality check.** Paste any live Irish property listing and get an instant, transparent verdict — **in line with, above, or below the real market** — anchored to official government data (CSO PxStat RPPI price index + PSRA Property Price Register of actual sales), not self-reported listing hype.

## 🔗 Live

**Hosted & accessible at:** https://axelvibe.github.io/ireland-property-catalogue/

## What it does

1. Paste a listing — e.g. `3-bed semi-d, Waterford, asking €310,000` (straight from your Telegram channel) — or just ask *"What's the market like in Dublin?"*
2. The engine extracts price, beds, property type and county, then compares the asking price against the official reference price for that county.
3. You get a verdict card (below / in line / above market, with the numbers shown) plus a plain-English assessment from the AI advisor **Eabha**.

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
- **Hybrid engine:** verdicts are computed **deterministically in the browser** from an embedded county reference dataset (distilled CSO/PSRA figures, all 26 counties). The OpenAI model (`gpt-4o-mini`) only writes plain-English interpretation on top of the computed facts — it never decides the verdict.
- **Graceful degradation:** if the AI or Geocoding APIs are unreachable, the verdict and a locally-generated assessment still work.
- **Services:** OpenAI (analysis), Google Geocoding (area validation), Telegram (listing source).

## ⚠️ Important: API keys & security

This static site calls OpenAI and Google APIs directly from the browser, so the keys in `CONFIG` inside `index.html` are **visible to anyone who views the page source**. This is fine for a hosted demonstration, but **before real users or any public promotion, rotate those keys and proxy the API calls through a small server** (see Roadmap).

## Telegram bridge

GitHub Pages is static-only, so a live *polling* Telegram bot needs a small server. Run the included bridge anywhere (laptop or free host):

```bash
pip install requests
python tools/telegram_bot.py
```

It listens to your channel, and when someone posts a listing it replies with the same reality-check logic (its own copy of the engine, so no server dependency on the web app).

## Roadmap

- [x] Single-file chatbot deployed to GitHub Pages
- [ ] Fresh CSO/PSRA figures monthly (Researcher)
- [ ] Rotate keys + server proxy before scaling
- [ ] Live Telegram bot hosting
- [ ] Auctioneer "official-data partner" pilot
