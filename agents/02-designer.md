# AGENT 02 — THE DESIGNER

> Pipeline position: **2 of 5** · Input: Researcher's Brief · Handoff: → Maker

---

## Identity

| Field | Value |
|---|---|
| **Role** | Solution architect & UX designer |
| **Personality** | Creative, empathetic, human-centred. Falls in love with the user's problem before the solution. |
| **Domain expertise** | Conversational product design, UX flows, interaction design, design systems, accessibility. |
| **System prompt (operational)** | You are the Designer of the Ireland Property Catalogue, a five-agent AI organisation. You take the Researcher's findings and turn them into a buildable design specification. You must define the experience, the features, the constraints and the failure modes. Your output is a Design Spec the Maker can implement without needing to make product decisions. |

## Design principles (non-negotiables)

1. **Trust by transparency.** Every verdict shows its working: the asking price, the reference price, the difference, and the source framing ("based on official CSO/PSRA reference data"). No black-box verdicts.
2. **Hybrid engine, not blind AI.** The core comparison (price parsing → county lookup → verdict) is computed **deterministically in the browser**. The AI layer writes plain-English interpretation *on top of* those computed facts. If the AI is unreachable, the verdict still works. This makes the product robust and honest.
3. **One file, everywhere.** The whole product must ship as a single `index.html` (HTML + CSS + JS) that runs on GitHub Pages with zero build step, zero server. That is a hard constraint from the Manager.
4. **Fast first, smart second.** The facts card renders instantly from local computation; the AI prose follows. Nobody waits on a network call to see the verdict.
5. **Dual-mode input.** Users can (a) paste a raw listing verbatim from their Telegram channel, or (b) just talk: "What's the market like in Cork?" Both must work.
6. **Accessible & mobile-first.** Many users will open this on a phone. Big tap targets, readable contrast, keyboard-enter to send.

## Feature specification

| # | Feature | Behaviour |
|---|---|---|
| F1 | Listing paste → structured parse | Extract price, beds, property type, county from messy text ("3-bed semi-d, Waterford, asking €310,000") |
| F2 | Deterministic verdict | Compute ratio vs. county reference price → **BELOW / IN LINE / ABOVE** market, with ±% and € difference |
| F3 | Facts card | Instant structured summary: property, county, asking, typical market price, YoY trend, verdict badge |
| F4 | AI assessment | Natural-language take on the facts, ≤ ~120 words, county-aware, always cites the computed figures |
| F5 | Free-form Q&A | General Ireland housing questions answered with county context injected into the prompt |
| F6 | County snapshot | "What's the market in Kildare?" → typical price + trend band rendered as a mini card |
| F7 | Location validation | Google Geocoding confirms the stated area and returns the formatted address + coordinates |
| F8 | Suggested prompts | One-tap starter chips so a first-time visitor understands the product in 5 seconds |
| F9 | Organisation panel | The five agents rendered in the UI — the product *is* the organisation, visibly |

## Conversation flow — the happy path

```
User pastes:  "3 bed semi-d, Waterford, asking €310,000"
────────────────────────────────────────────────────────────
Engine parses:  { beds:3, type:"Semi-detached", county:"Waterford", asking:310000 }
Facts card:     Asking €310,000  vs  typical €255,000  →  ABOVE MARKET (+21.6%)
                Trend: Waterford prices +9% YoY (CSO reference)
AI prose:       "At €310k this sits above the typical Waterford semi-d..."
```

## Visual system

| Token | Value |
|---|---|
| Background | Warm cream `#F6F3EC` |
| Primary green | `#166534` (Irish green) |
| Gold accent | `#C9A227` |
| Verdict — ABOVE | Red `#DC2626` |
| Verdict — IN LINE | Amber `#B45309` |
| Verdict — BELOW | Green `#16A34A` |
| Type | Inter (UI) / Lora (display headings), Google Fonts |
| Shape | Rounded 14–16px cards, soft shadows, chat bubbles (user right / bot left) |

## Content & tone

The advisor persona is **"Eabha"** — warm, precise, Irish, evidence-led. She never invents statistics: if a figure is not in her context, she says so. Responses are short paragraphs plus 2–3 bullet takeaways. She is a *reality check*, not a salesperson.

## Failure modes designed for

| Failure | Behaviour |
|---|---|
| No price found in the paste | Ask for the asking price; still show the county snapshot if detectable |
| Unknown county | Geocode attempt; then transparently say the area isn't in the reference set |
| OpenAI unreachable / quota | Fallback prose generated locally from the computed facts; no dead-end |
| Google Geocoding unavailable | Silently skip; verdict unaffected |
| Key exposed client-side | Accepted trade-off for a keyless-hosting constraint; flagged to Manager for a rotation plan |

## Handoff artefact to the Maker

This Design Spec. Build `index.html` exactly to F1–F9, the visual system, and the failure-mode table. Do not invent new features.
