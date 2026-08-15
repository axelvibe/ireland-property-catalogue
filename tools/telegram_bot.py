#!/usr/bin/env python3
"""
Ireland Property Catalogue — Telegram bridge.

Listens to a Telegram channel/group. When someone posts a property listing,
it replies with the same reality-check logic as the web app (deterministic
verdict + optional AI assessment).

GitHub Pages is static-only, so this bridge must run on a small server or
your laptop. Zero frameworks: only `requests`.

Usage:
    pip install requests
    python tools/telegram_bot.py

Note: the bot token is embedded here for demonstration. Rotate before real use.
"""

import re
import time
import requests

# ----------------------------- CONFIG ----------------------------------
TELEGRAM_TOKEN = "8907857522:AAEuTdqhKRaQZqJQj7oRocgnhIjzYb94ztQ"
GEMINI_API_KEY = "AQ.Ab8RN6K1gAihniibBmmXejYhyBUo7a7Oi_1q-uqteEpH596XgA"
GEMINI_MODEL = "gemini-2.5-flash"
POLL_INTERVAL = 2

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# --------------------- COUNTY REFERENCE (CSO/PSRA) ----------------------
COUNTIES = {
    "Dublin": (450000, 4), "Cork": (330000, 8), "Kildare": (340000, 7),
    "Meath": (320000, 8), "Wicklow": (395000, 5), "Galway": (310000, 6),
    "Louth": (285000, 7), "Limerick": (285000, 7), "Waterford": (255000, 9),
    "Wexford": (260000, 8), "Kerry": (265000, 7), "Kilkenny": (255000, 6),
    "Clare": (255000, 8), "Tipperary": (235000, 7), "Westmeath": (245000, 6),
    "Laois": (250000, 7), "Offaly": (235000, 6), "Carlow": (235000, 6),
    "Mayo": (225000, 6), "Sligo": (215000, 5), "Roscommon": (205000, 5),
    "Monaghan": (220000, 5), "Cavan": (210000, 6), "Longford": (185000, 4),
    "Leitrim": (195000, 4), "Donegal": (200000, 7),
}
ALIASES = {name: [name.lower()] for name in COUNTIES}
# aliases with dots/prefixed forms
for name, al in ALIASES.items():
    al.append("co. " + name.lower())
    al.append("county " + name.lower())

# ----------------------------- PARSING ----------------------------------
def extract_price(text):
    m = re.search(r"€\s*([\d][\d,.]*)\s*(k|thousand)?", text, re.I)
    if not m:
        m = re.search(r"asking(?:\s*price)?[^€\d]*([\d][\d,.]*)\s*(k|thousand)?", text, re.I)
    if not m:
        m = re.search(r"\b([\d][\d,.]*)\s*k\b", text, re.I)
    if not m:
        return None
    num, suffix = m.group(1), (m.group(2) or "")
    n = float(num.replace(",", ""))
    if suffix.lower().startswith("k") or "thousand" in suffix.lower():
        n *= 1000
    return n

def extract_county(text):
    low = text.lower()
    for name, al in ALIASES.items():
        for a in al:
            if re.search(r"\b" + re.escape(a) + r"\b", low):
                return name
    return None

def verdict_for(asking, typical):
    ratio = asking / typical
    if ratio <= 0.88:
        return "BELOW MARKET", (ratio - 1) * 100
    if ratio <= 1.12:
        return "IN LINE WITH MARKET", (ratio - 1) * 100
    return "ABOVE MARKET", (ratio - 1) * 100

def fmt(n):
    return "€" + f"{round(n):,}"

# --------------------------- ANALYSIS ----------------------------------
def analyse(text):
    asking, county = extract_price(text), extract_county(text)
    if not county:
        return ("I couldn't pin down a county there. Try something like "
                "\u201c3-bed semi-d, Waterford, asking \u20ac310,000\u201d.")
    if not asking:
        return f"I can see this is in {county}, but I need the asking price to compare it against the market."
    typical, trend = COUNTIES[county]
    label, diff = verdict_for(asking, typical)
    lines = [
        f"🏠 Listing in {county}",
        f"Asking: {fmt(asking)}  vs  typical {fmt(typical)}  ({'+' if diff > 0 else ''}{diff:.1f}%)",
        f"Verdict: {label}",
        f"📈 {county} trend: {'+' if trend >= 0 else ''}{trend}% YoY (CSO/PSRA reference)",
        "Always confirm against the PSRA Property Price Register for exact sales.",
    ]
    return "\n".join(lines)

def ai_assessment(text, facts):
    try:
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")
        r = requests.post(
            url,
            json={
                "systemInstruction": {"parts": [{"text": (
                    "You are Eabha, the Ireland Property Catalogue price advisor. "
                    "Never invent statistics. Use only figures given to you. "
                    "Reply under 120 words, one short paragraph plus 2-3 bullet takeaways.")}]},
                "contents": [{"role": "user", "parts": [{"text":
                    f"Structured facts:\n{facts}\n\nListing: {text}\n\nAssess it."}]}],
                "generationConfig": {"temperature": 0.6, "maxOutputTokens": 400},
            },
            timeout=25,
        )
        r.raise_for_status()
        parts = r.json()["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts).strip()
    except Exception:
        return None

# ---------------------------- BOT LOOP ----------------------------------
def main():
    print("Eabha (Ireland Property Catalogue) Telegram bridge starting…")
    offset = None
    while True:
        try:
            params = {"timeout": 20, "allowed_updates": ["message"]}
            if offset:
                params["offset"] = offset
            r = requests.get(TG_API + "/getUpdates", params=params, timeout=30)
            for upd in r.json().get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message") or {}
                text = (msg.get("text") or "").strip()
                chat_id = msg.get("chat", {}).get("id")
                if not text or chat_id is None:
                    continue
                print(f"[{msg.get('from', {}).get('username', '?')}] {text}")
                reply = analyse(text)
                try:
                    if "Asking:" in reply:
                        extra = ai_assessment(text, reply)
                        if extra:
                            reply += "\n\n💬 " + extra
                except Exception:
                    pass
                requests.post(TG_API + "/sendMessage",
                              json={"chat_id": chat_id, "text": reply, "parse_mode": "HTML"})
        except Exception as exc:
            print("error:", exc)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
