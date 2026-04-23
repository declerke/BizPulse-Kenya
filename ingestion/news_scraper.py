import hashlib
import re
import feedparser
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

RSS_FEEDS = {
    "business_daily": "https://www.businessdailyafrica.com/service/rss/bd/1939132/feed.rss",
    "standard_media": "https://www.standardmedia.co.ke/rss/headlines.php",
}


def _clean_html(text: str) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", cleaned).strip()


def _parse_published(entry) -> datetime:
    for field in ("published_parsed", "updated_parsed"):
        t = getattr(entry, field, None)
        if t:
            return datetime(*t[:6], tzinfo=timezone.utc)
    for field in ("published", "updated"):
        raw = getattr(entry, field, None)
        if raw:
            try:
                return parsedate_to_datetime(raw)
            except Exception:
                pass
    return datetime.now(timezone.utc)


def _article_id(link: str, published: datetime) -> str:
    key = f"{link}:{published.isoformat()}"
    return hashlib.sha256(key.encode()).hexdigest()[:64]


def scrape_all() -> list[dict]:
    articles = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = _clean_html(getattr(entry, "title", "") or "")
            summary = _clean_html(getattr(entry, "summary", "") or "")
            link = getattr(entry, "link", "") or ""
            published = _parse_published(entry)
            if not title:
                continue
            articles.append({
                "id": _article_id(link, published),
                "title": title,
                "summary": summary[:2000],
                "link": link,
                "published_at": published,
                "source": source,
            })
    return articles


if __name__ == "__main__":
    results = scrape_all()
    print(f"Scraped {len(results)} articles")
    for a in results[:3]:
        print(f"  [{a['source']}] {a['title'][:80]}")
