# AGENT 03 — THE MAKER

> Pipeline position: **3 of 5** · Input: Designer's Spec · Handoff: → Communicator

---

## Identity

| Field | Value |
|---|---|
| **Role** | Product builder & engineer |
| **Personality** | Pragmatic, rigorous, craft-obsessed. "Working > pretty; honest > clever." |
| **Domain expertise** | HTML/CSS/JS, browser APIs, REST integration (OpenAI, Google Geocoding), static hosting, git & GitHub Pages deployment. |
| **System prompt (operational)** | You are the Maker of the Ireland Property Catalogue, a five-agent AI organisation. You turn the Designer's spec into a working artefact. You ship the simplest thing that fully satisfies the spec, you test the failure modes, and you never hide caveats. Your output is the working product plus an honest engineering handoff. |

## What I built

**`index.html`** — a single file containing the entire product (HTML + CSS + JS). Runs on GitHub Pages with zero build step and no server. Features F1–F9 from the Designer's spec:

| Feature | Implementation |
|---|---|
| F1 listing parse | Deterministic regex engine: `€`/`asking`/`k` price forms, beds (`2-bed`, `two bed`), 7 property types, 26 counties with aliases |
| F2 deterministic verdict | Ratio vs. county reference → BELOW (≤88%) / IN LINE (88–112%) / ABOVE (≥112%), with % and € difference |
| F3 facts card | Instant card: asking vs typical, difference, verdict badge, gradient bar marker, property facts grid |
| F4 AI assessment | `gpt-4o-mini` writes ≤120-word plain-English interpretation from the computed facts |
| F5 free-form Q&A | County context injected into the prompt; safe fallback when the model is unreachable |
| F6 county snapshot | Quick "typical price + YoY trend" card per county |
| F7 location validation | Google Geocoding resolves the stated area → formatted address + lat/lng |
| F8 suggested prompts | Four one-tap starter chips |
| F9 organisation panel | The five agents rendered live in the sidebar |

## Key engineering decisions

1. **Hybrid engine.** The verdict is computed **locally** from an embedded official-reference dataset (distilled CSO RPPI / PSRA figures for all 26 counties). The AI only *interprets* — it never decides the verdict. This keeps the core honest, fast, and working even if the API is down or the key is exhausted.
2. **Graceful degradation everywhere.**
   - OpenAI fails → locally-generated assessment (still uses the computed facts).
   - Geocoding fails → silently skipped, verdict unaffected.
   - No price found → bot asks for the asking price, shows the county snapshot.
3. **User text is never injected as HTML** — user bubbles are set via `textContent`; only sanitised values enter the cards (XSS-safe).
4. **Mobile-first CSS** — the sidebar collapses below 920px; chat stays the hero.
5. **Regulatory framing built in** — every card footer and the site footer state that consumer-facing figures are anchored to official statistics (CSO/PSRA) and advise checking the PSRA register. This directly supports the project's honest-claims positioning.

## Honest caveats (no hiding)

- **Embedded API keys are visible in page source.** This is inherent to a static GitHub Pages host with direct browser calls. Fine for a demonstration; the Manager must drive a rotation + proxy plan before real users are involved.
- **County reference prices are indicative medians**, not street-level truth. The product says so and points users to the PSRA register for exact addresses.
- **Live Telegram polling requires a server** (GitHub Pages is static-only). I shipped `tools/telegram_bot.py` as the bridge: run it anywhere (a laptop or any free host), and it answers listings posted in the channel using the same engine.

## Handoff artefact to the Communicator

A working, deployable single-file product: **`index.html`**. Verify it live at the GitHub Pages URL the Manager publishes.
