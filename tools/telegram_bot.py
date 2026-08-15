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

import csv
import io
import re
import time
import requests

try:
    from datetime import datetime, timedelta
    HAVE_DATETIME = True
except Exception:
    HAVE_DATETIME = False

# ----------------------------- CONFIG ----------------------------------
TELEGRAM_TOKEN = "8907857522:AAEuTdqhKRaQZqJQj7oRocgnhIjzYb94ztQ"
GEMINI_API_KEY = "AQ.Ab8RN6K1gAihniibBmmXejYhyBUo7a7Oi_1q-uqteEpH596XgA"
GEMINI_MODEL = "gemini-2.5-flash"
POLL_INTERVAL = 2
LIVE_TTL_SECONDS = 6 * 60 * 60  # refresh CSO/PSRA live data every 6h

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# --------------------------- LIVE DATA CACHE ----------------------------
CSO_URL = ("https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API."
           "ReadDataset/HPM09/JSON-stat/2.0/en")
PSRA_URL = ("https://www.propertypriceregister.ie/website/npsra/ppr/npsra-ppr.nsf/"
            "Downloads/PPR-{year}-{county}.csv/%24FILE/PPR-{year}-{county}.csv")
# county -> HPM09 C02803V03373 region code
CSO_REGIONS = {
    "Dublin": "06", "Cork": "19", "Kerry": "19",
    "Cavan": "21", "Donegal": "21", "Leitrim": "21", "Monaghan": "21", "Sligo": "21",
    "Laois": "14", "Longford": "14", "Offaly": "14", "Westmeath": "14",
    "Galway": "15", "Mayo": "15", "Roscommon": "15",
    "Kildare": "22", "Louth": "22", "Meath": "22", "Wicklow": "22",
    "Clare": "23", "Limerick": "23", "Tipperary": "23",
    "Carlow": "24", "Kilkenny": "24", "Waterford": "24", "Wexford": "24",
}

_cache = {}

def _fresh(name, ttl=LIVE_TTL_SECONDS):
    ent = _cache.get(name)
    if ent and HAVE_DATETIME:
        return (datetime.now() - ent["ts"]) < timedelta(seconds=ttl)
    return ent is not None

def cso_trends():
    """Return {month:'202605', regions:{code:yoy}} or None. Cached 6h."""
    if not _fresh("cso"):
        try:
            r = requests.get(CSO_URL, timeout=25)
            r.raise_for_status()
            d = r.json()
            dims = d.get("dimension", {})
            keys = lambda o: o if isinstance(o, list) else list(o.keys())
            stats, months = keys(dims["STATISTIC"]["category"]["index"]), \
                            keys(dims["TLIST(M1)"]["category"]["index"])
            regions = keys(dims["C02803V03373"]["category"]["index"])
            s_idx, s_yoy = stats.index("HPM09C01"), stats.index("HPM09C04")
            vals = d["value"]
            M, R = len(months), len(regions)
            def pos(s, m, r): return vals[s * M * R + m * R + r]
            out = {regions[r]: pos(s_yoy, M - 1, r) for r in range(R)}
            _cache["cso"] = {"month": months[M - 1], "regions": out,
                             "ts": datetime.now()}
        except Exception:
            return _cache.get("cso", {}).get("regions") and _cache["cso"] or None
    return _cache.get("cso")

def trend_for(county):
    """Live YoY % for a county, falling back to the embedded value."""
    cso = cso_trends()
    if cso:
        code = CSO_REGIONS.get(county)
        if code and code in cso["regions"]:
            return cso["regions"][code], cso["month"], True
    return COUNTIES[county][1], None, False

def psra_sales(county, year=None, limit=5):
    """Actual PSRA sales in a county for the given year (default: this year).
    Uses the official per-county CSV. Returns list of dicts or None."""
    year = year or (datetime.now().year if HAVE_DATETIME else 2026)
    key = f"psra:{county}:{year}"
    if not _fresh(key):
        rows = None
        try:
            r = requests.get(PSRA_URL.format(year=year, county=county),
                             timeout=40,
                             headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            parsed = list(csv.DictReader(io.StringIO(r.content.decode("cp1252", "replace"))))
            rows = parsed[:60]
        except Exception:
            rows = None
        _cache[key] = {"rows": rows, "ts": datetime.now()}
    ent = _cache.get(key)
    if not ent or not ent["rows"]:
        return None
    return ent["rows"][:limit]

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

# --------------------- TYPE / BED BANDS & DUBLIN AREAS -------------------
TYPE_FACTORS = {
    "Detached": 1.18, "Semi-detached": 1.02, "Terraced / townhouse": 0.86,
    "Apartment / flat": 0.82, "Bungalow": 1.06, "Studio": 0.58, "Maisonette": 0.78,
}
BED_FACTORS = {1: 0.70, 2: 0.88, 3: 1.00, 4: 1.20, 5: 1.42, 6: 1.60}
DUBLIN_POSTAL_SALE = {
    "D1": 375000, "D2": 525000, "D3": 460000, "D4": 850000, "D5": 445000,
    "D6": 720000, "D6W": 620000, "D7": 485000, "D8": 430000, "D9": 520000,
    "D10": 355000, "D11": 385000, "D12": 450000, "D13": 515000, "D14": 610000,
    "D15": 465000, "D16": 575000, "D17": 385000, "D18": 620000, "D20": 420000,
    "D22": 395000, "D24": 405000,
}
DUBLIN_POSTAL_RENT = {
    "D1": 2065, "D2": 2247, "D3": 1889, "D4": 2508, "D5": 2282,
    "D6": 1976, "D6W": 2324, "D7": 1926, "D8": 1873, "D9": 2054,
    "D10": 1802, "D11": 1934, "D12": 2081, "D13": 2111, "D14": 2802,
    "D15": 1985, "D16": 2269, "D17": 1828, "D18": 2509, "D20": 1976,
    "D22": 1862, "D24": 2047,
}
RTB_RENTS = {
    "Carlow": 1316, "Cavan": 1095, "Clare": 1170, "Cork": 1542, "Donegal": 977,
    "Dublin": 2159, "Galway": 1637, "Kerry": 1182, "Kildare": 1701,
    "Kilkenny": 1207, "Laois": 1235, "Leitrim": 992, "Limerick": 1619,
    "Longford": 1120, "Louth": 1433, "Mayo": 1117, "Meath": 1542,
    "Monaghan": 1028, "Offaly": 1198, "Roscommon": 1092, "Sligo": 1156,
    "Tipperary": 1078, "Waterford": 1247, "Westmeath": 1257, "Wexford": 1179,
    "Wicklow": 1730,
}

def shape_typical(base, type_label, beds):
    f = 1.0
    if type_label and type_label in TYPE_FACTORS:
        f *= TYPE_FACTORS[type_label]
    if beds and beds in BED_FACTORS:
        f *= BED_FACTORS[beds]
    return round(base * f)

def extract_dublin_postal(text):
    m = re.search(r"\bDublin\s?(6\s?W|6w|\d{1,2})\b|\bD\s?(6\s?W|6w|\d{1,2})\b", text, re.I)
    if m:
        raw = (m.group(1) or m.group(2) or "").upper().replace(" ", "")
        key = "D6W" if raw == "6W" else "D" + str(int(raw))
        if key in DUBLIN_POSTAL_SALE:
            return key
    return None

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
def extract_type_label(text):
    pats = [
        (r"semi[\s-]?detached|semi[\s-]?d\b|semi\b", "Semi-detached"),
        (r"\bdetached\b", "Detached"),
        (r"terrace\w*|townhouse|town[\s-]?house", "Terraced / townhouse"),
        (r"\bapartment\w*|\bflat\b|\bduplex\b", "Apartment / flat"),
        (r"\bbungalow\b", "Bungalow"),
        (r"\bstudio\b", "Studio"),
        (r"\bmaisonette\b", "Maisonette"),
    ]
    for pat, label in pats:
        if re.search(pat, text, re.I):
            return label
    return None

def extract_beds(text):
    m = re.search(r"(\d)\s*-?\s*(?:bed(?:room)?s?)", text, re.I)
    if m:
        return int(m.group(1))
    return None

def extract_rent(text):
    m = re.search(r"\u20ac?\s*([\d][\d,.]*)\s*(k|thousand)?\s*(?:per\s*)?(?:month|mth|pm|pcm|/mo)\b", text, re.I)
    if m:
        n = float(m.group(1).replace(",", ""))
        if (m.group(2) or "").lower().startswith("k") or "thousand" in (m.group(2) or ""):
            n *= 1000
        return n
    m = re.search(r"(rent|renting|letting)\w*[^\u20ac\d]*\u20ac?\s*([\d][\d,.]*)\s*(k|thousand)?", text, re.I)
    if m:
        n = float(m.group(2).replace(",", ""))
        if (m.group(3) or "").lower().startswith("k") or "thousand" in (m.group(3) or ""):
            n *= 1000
        return n
    return None

def is_rental(text):
    return bool(re.search(r"rent(?:al|ing|s)?|letting|landlord|lease|pcm\b|per month|tenant", text, re.I))

def extract_income(text):
    m = re.search(r"(income|salary|earn(?:ing|s)?|take[\s-]?home)\w*[^\u20ac\d]*\u20ac?\s*([\d][\d,.]*)\s*(k|thousand)?", text, re.I)
    if m:
        n = float(m.group(2).replace(",", ""))
        if (m.group(3) or "").lower().startswith("k"):
            n *= 1000
        return n
    m = re.search(r"\u20ac?\s*([\d][\d,.]*)\s*(k|thousand)?\s*(?:per\s*)?(?:year|annum|annual)\b", text, re.I)
    if m:
        n = float(m.group(1).replace(",", ""))
        if (m.group(2) or "").lower().startswith("k"):
            n *= 1000
        return n
    return None

def stamp_duty(price):
    return round(min(price, 1000000) * 0.01 + max(price - 1000000, 0) * 0.02)

def mortgage_monthly(price, deposit, years=30, rate=3.9):
    p = max(price - deposit, 0)
    r = rate / 100 / 12
    n = years * 12
    if p <= 0:
        return 0.0
    if r == 0:
        return p / n
    return p * r / (1 - (1 + r) ** -n)

def analyse(text):
    asking, county = extract_price(text), extract_county(text)
    rent = extract_rent(text)
    income = extract_income(text)
    postal = extract_dublin_postal(text) if county == "Dublin" else None
    type_label, beds = extract_type_label(text), extract_beds(text)

    # Affordability mode
    if income and re.search(r"afford|budget|can i|buy|mortgage", text, re.I):
        deposit = 0
        m = re.search(r"(deposit|saved|savings|cash|down[\s-]?payment)\w*[^\u20ac\d]*\u20ac?\s*([\d][\d,.]*)\s*(k|thousand)?", text, re.I)
        if m:
            deposit = float(m.group(2).replace(",", ""))
            if (m.group(3) or "").lower().startswith("k"):
                deposit *= 1000
        ceiling = income * 4
        lines = [f"💶 Affordability check (30-yr fix @ ~3.9%)",
                 f"Gross income: {fmt(income)}/yr  ·  Deposit: {fmt(deposit)}",
                 f"4× income ceiling (most lenders): {fmt(ceiling)}",
                 f"Max realistic budget: ~{fmt(ceiling + deposit)}",
                 f"Stamp duty on {fmt(ceiling)}: {fmt(stamp_duty(ceiling))}",
                 f"Est. monthly mortgage: {fmt(mortgage_monthly(ceiling, deposit))}",
                 "First-time buyers can push to 4.5×; get a lender's approval-in-principle before bidding."]
        return "\n".join(lines)

    # Rental mode
    if is_rental(text) and county:
        rtb_ref = DUBLIN_POSTAL_RENT.get(postal or "", RTB_RENTS.get(county))
        place = f"Dublin {postal[1:]}" if postal else county
        lines = [f"🏢 Rent reality check · {place}",
                 f"RTB average rent (2025 Rent Index): {fmt(rtb_ref)}/mo"]
        if rent:
            rel = rent / rtb_ref
            verdict = ("ABOVE RTB AVERAGE" if rel > 1.1 else
                       "BELOW RTB AVERAGE" if rel < 0.9 else
                       "IN LINE WITH RTB AVERAGE")
            lines += [f"Advertised: {fmt(rent)}/mo  ({'+' if rel > 1 else ''}{(rel - 1) * 100:.1f}% vs average)",
                      f"Verdict: {verdict}"]
        lines.append("Rents in Rent Pressure Zones are capped at CPI-linked increases; every tenancy must be registered with the RTB.")
        return "\n".join(lines)

    if not county:
        return ("I couldn't pin down a county there. Try something like "
                "\u201c3-bed semi-d, Waterford, asking \u20ac310,000\u201d.")
    if not asking:
        return f"I can see this is in {county}, but I need the asking price to compare it against the market."
    base = DUBLIN_POSTAL_SALE.get(postal or "", COUNTIES[county][0])
    typical = shape_typical(base, type_label, beds)
    label, diff = verdict_for(asking, typical)
    trend, month, live = trend_for(county)
    trend_txt = (f"{'+' if trend >= 0 else ''}{trend:.1f}% YoY (live CSO RPPI, "
                 f"{month[:4]}-{month[4:]})" if live else
                 f"{'+' if trend >= 0 else ''}{trend}% YoY (CSO/PSRA reference)")
    shape_note = f" · {beds}-bed {type_label.lower()}" if beds and type_label else \
                 f" · {type_label.lower()}" if type_label else ""
    head_line = f"🏠 Listing in Dublin {postal[1:]}" if postal else f"🏠 Listing in {county}"
    lines = [
        head_line,
        f"Asked: {fmt(asking)}  vs  typical {fmt(typical)} for this shape  ({'+' if diff > 0 else ''}{diff:.1f}%)",
        f"Verdict: {label}",
        f"📈 {county} trend: {trend_txt}",
        "Always confirm against the PSRA Property Price Register for exact sales.",
    ]
    sales = psra_sales(county)
    if sales:
        lines.append("")
        lines.append("🟢 Actual PSRA sales in the area (recent):")
        for s in sales:
            price = s.get("Price (\u20ac)", "").replace("\u20ac", "").replace(",", "")
            try:
                price_num = float(price)
            except Exception:
                price_num = None
            addr = (s.get("Address", "") or "")[:60]
            date = (s.get("Date of Sale (dd/mm/yyyy)", "") or "")[:10]
            tag = s.get("Description of Property", "") or ""
            if price_num is not None and price_num <= asking * 1.25:
                lines.append(f"  • {date}  {addr}\n    Sold {fmt(price_num)} · {tag[:34]}")
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
