import sys
sys.path.insert(0, ".")

from unittest.mock import patch, MagicMock
from ingestion.news_scraper import _clean_html, _article_id, scrape_all


def test_clean_html_strips_tags():
    assert _clean_html("<b>Hello</b> <i>World</i>") == "Hello World"


def test_clean_html_empty():
    assert _clean_html("") == ""
    assert _clean_html(None) == ""


def test_article_id_is_64_chars():
    from datetime import datetime, timezone
    dt = datetime(2026, 4, 22, tzinfo=timezone.utc)
    aid = _article_id("https://example.com/article", dt)
    assert len(aid) == 64


def test_article_id_deterministic():
    from datetime import datetime, timezone
    dt = datetime(2026, 4, 22, tzinfo=timezone.utc)
    assert _article_id("https://a.com", dt) == _article_id("https://a.com", dt)


def test_scrape_all_returns_list():
    mock_entry = MagicMock()
    mock_entry.title = "Kenya economy grows"
    mock_entry.summary = "GDP rose 5%"
    mock_entry.link = "https://bda.com/article"
    mock_entry.published_parsed = (2026, 4, 22, 8, 0, 0, 0, 0, 0)
    mock_entry.updated_parsed = None

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]

    with patch("ingestion.news_scraper.feedparser.parse", return_value=mock_feed):
        results = scrape_all()

    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0]["title"] == "Kenya economy grows"
    assert results[0]["source"] in ("business_daily", "standard_media")
