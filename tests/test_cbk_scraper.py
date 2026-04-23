import sys
sys.path.insert(0, ".")

from unittest.mock import patch, MagicMock
from ingestion.cbk_scraper import scrape_forex, scrape_interest_rates

FOREX_HTML = """
<html><body>
<table>
  <tr><th>Currency</th><th>Buying</th><th>Selling</th><th>Mean</th></tr>
  <tr><td>USD</td><td>128.50</td><td>130.20</td><td>129.35</td></tr>
  <tr><td>EUR</td><td>138.10</td><td>140.00</td><td>139.05</td></tr>
  <tr><td>GBP</td><td>160.20</td><td>162.50</td><td>161.35</td></tr>
</table>
</body></html>
"""

RATES_HTML = """
<html><body>
<table>
  <tr><th>Rate Type</th><th>Value</th></tr>
  <tr><td>Central Bank Rate</td><td>8.75</td></tr>
  <tr><td>Interbank Rate</td><td>7.20</td></tr>
</table>
</body></html>
"""


def _mock_response(html: str):
    resp = MagicMock()
    resp.text = html
    resp.raise_for_status = MagicMock()
    return resp


def test_scrape_forex_returns_records():
    with patch("ingestion.cbk_scraper.requests.get", return_value=_mock_response(FOREX_HTML)):
        records = scrape_forex()
    assert len(records) >= 2
    pairs = {r["currency_pair"] for r in records}
    assert "USD/KES" in pairs


def test_scrape_forex_mean_rate():
    with patch("ingestion.cbk_scraper.requests.get", return_value=_mock_response(FOREX_HTML)):
        records = scrape_forex()
    usd = next(r for r in records if r["currency_pair"] == "USD/KES")
    assert usd["mean_rate"] == 129.35


def test_scrape_interest_rates():
    with patch("ingestion.cbk_scraper.requests.get", return_value=_mock_response(RATES_HTML)):
        records = scrape_interest_rates()
    assert len(records) >= 1
    cbr = next((r for r in records if "Central Bank" in r["rate_type"]), None)
    assert cbr is not None
    assert cbr["rate_value"] == 8.75
