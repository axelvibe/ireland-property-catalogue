# AGENT 05 — THE MANAGER

> Pipeline position: **5 of 5** · Input: all four prior handoffs · Output: executive summary

---

## Identity

| Field | Value |
|---|---|
| **Role** | Chief of staff & orchestrator |
| **Personality** | Strategic, accountable, calm under pressure. Reviews everything, accepts nothing unproven. |
| **Domain expertise** | Operations, quality assurance, strategy, stakeholder communication, value delivery. |
| **System prompt (operational)** | You are the Manager of the Ireland Property Catalogue, a five-agent AI organisation. You oversee the entire chain: you verify each agent's output, ensure strategic alignment, sign off the product, and publish the plan. You produce the Executive Summary. You never declare victory without a live, verifiable artefact. |

## The chain — verified end to end

| # | Agent | Deliverable | Status |
|---|---|---|---|
| 1 | Researcher | Research Brief — affordability gap, CSO/PSRA evidence, opportunity | ✅ Accepted |
| 2 | Designer | Design Spec — F1–F9, hybrid engine, visual system, failure modes | ✅ Accepted |
| 3 | Maker | `index.html` single-file product + `tools/telegram_bot.py` bridge | ✅ Accepted |
| 4 | Communicator | Brand, tagline, launch copy, 90-day GTM | ✅ Accepted |
| 5 | Manager | This executive summary + live deployment | ✅ In progress |

## Quality review (what I checked before signing off)

1. **Verdict integrity** — the verdict is computed locally from a transparent reference dataset; the AI cannot hallucinate a verdict. PASS.
2. **Transparency** — every analysis card shows the asking price, the reference price, the difference, the county trend, and a "source: CSO/PSRA reference" note. PASS.
3. **Graceful degradation** — tested paths for: no price, unknown county, AI unreachable, geocoding down. No dead-ends. PASS.
4. **Safety** — user input is rendered as text (XSS-safe); no secrets in git history beyond the intended demo keys; no server-side code to misconfigure. PASS.
5. **Honest-claims positioning** — the regulatory story is real and embedded in the product: *"we deliberately anchor consumer-facing claims to official statistics, not self-reported listing data."* PASS.
6. **Known limitation, documented** — API keys are visible in source (inherent to static hosting). Rotation + server proxy scheduled; acceptable for demonstration, MUST fix before scaling. OPEN.

## Executive summary — Ireland Property Catalogue

**Mission.** Help Irish home buyers answer one question honestly: *"Is this asking price reasonable?"*

**Product.** A free, single-file chatbot ("Eabha") hosted on GitHub Pages. Paste any live listing (e.g. from a Telegram channel) and receive an instant, transparent verdict — **in line with, above, or below market** — backed by official CSO RPPI price-index data and PSRA actual-sale evidence. AI adds plain-English interpretation on top of deterministically-computed facts, never replacing them.

**Why now.** Decades-high demand, chronic supply shortage, and first-time buyers facing opaque, self-reported asking prices — while the authoritative government data sits unused in hard-to-use portals. Nobody else positions as the *official-data reality check*.

**Differentiation.** Not another listings site. A truth engine layered on top of listings, deliberately anchored to official statistics — an honest, defensible regulatory story and a genuine trust moat.

**Delivery.** Hosted live and accessible at the URL below, backed by the OpenAI API (analysis), Google Geocoding (area validation), and a Telegram bridge script for channel-based use.

## KPIs (first 90 days)

- **Activation:** ≥60% of visitors send at least one listing within 5 minutes
- **Reality checks:** ≥200 asking prices analysed
- **Utility signal:** ≥40% of verdicts in the "in line / below" band (proves real usefulness, not doom-scrolling)
- **Uptime:** ≥99.5% (static hosting makes this easy)
- **Referral:** 1 auctioneer partner by day 60

## Next actions (this sprint)

1. ✅ Deploy to GitHub Pages → live URL verified
2. ➡️ Run the Communicator's launch plan (thread + 5 community answers)
3. ➡️ Update the county reference dataset with fresh CSO/PSRA figures (Researcher, monthly)
4. ➡️ Replace embedded keys with a proxy before real-user scaling
5. ➡️ Activate `tools/telegram_bot.py` for the channel

## Handoff artefact

This Executive Summary + a live, verifiable deployment at the GitHub Pages URL published in the README.
