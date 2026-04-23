import hashlib
import re
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime, timezone

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; BizPulseBot/1.0)"}
FOREX_URL = "https://www.centralbank.go.ke/cbk-indicative-rates/"
RATES_URL = "https://www.centralbank.go.ke/statistics/interest-rates/"

FOREX_PAIRS = {"USD", "EUR", "GBP", "JPY", "CNY"}


def _row_id(rate_date: date, key: str) -> str:
    return hashlib.sha256(f"{rate_date}:{key}".encode()).hexdigest()[:64]


def scrape_forex() -> list[dict]:
    resp = requests.get(FOREX_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    today = date.today()
    records = []

    table = soup.find("table")
    if not table:
        return records

    rows = table.find_all("tr")
    for row in rows[1:]:
        cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
        if len(cols) < 2:
            continue
        currency = cols[0].upper().strip()
        if currency not in FOREX_PAIRS:
            continue
        try:
            buying = float(re.sub(r"[^\d.]", "", cols[1])) if len(cols) > 1 else None
            selling = float(re.sub(r"[^\d.]", "", cols[2])) if len(cols) > 2 else None
            mean = float(re.sub(r"[^\d.]", "", cols[3])) if len(cols) > 3 else None
        except (ValueError, IndexError):
            buying, selling, mean = None, None, None

        pair = f"{currency}/KES"
        records.append({
            "id": _row_id(today, pair),
            "rate_date": today,
            "currency_pair": pair,
            "buying_rate": buying,
            "selling_rate": selling,
            "mean_rate": mean,
        })

    return records


def scrape_interest_rates() -> list[dict]:
    resp = requests.get(RATES_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    today = date.today()
    records = []

    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows[1:6]:
            cols = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cols) < 2:
                continue
            rate_type = cols[0].strip()
            try:
                rate_value = float(re.sub(r"[^\d.]", "", cols[1]))
            except (ValueError, IndexError):
                continue
            if not rate_type or rate_value == 0:
                continue
            records.append({
                "id": _row_id(today, rate_type),
                "rate_date": today,
                "rate_type": rate_type[:50],
                "rate_value": rate_value,
            })
        if records:
            break

    if not records:
        cbr_match = re.search(r"Central Bank Rate[^\d]*(\d+\.?\d*)", resp.text)
        if cbr_match:
            records.append({
                "id": _row_id(today, "Central Bank Rate"),
                "rate_date": today,
                "rate_type": "Central Bank Rate",
                "rate_value": float(cbr_match.group(1)),
            })

    return records


if __name__ == "__main__":
    forex = scrape_forex()
    rates = scrape_interest_rates()
    print(f"Forex records: {len(forex)}")
    for r in forex:
        print(f"  {r['currency_pair']}: mean={r['mean_rate']}")
    print(f"Rate records: {len(rates)}")
    for r in rates:
        print(f"  {r['rate_type']}: {r['rate_value']}")
