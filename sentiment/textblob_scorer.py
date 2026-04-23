from textblob import TextBlob


def _polarity_to_label(polarity: float) -> str:
    if polarity > 0.05:
        return "positive"
    elif polarity < -0.05:
        return "negative"
    return "neutral"


def score(texts: list[str]) -> list[dict]:
    results = []
    for text in texts:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        label = _polarity_to_label(polarity)
        pos = max(polarity, 0.0)
        neg = abs(min(polarity, 0.0))
        neutral = 1.0 - pos - neg
        results.append({
            "label": label,
            "positive": round(pos, 4),
            "negative": round(neg, 4),
            "neutral": round(max(neutral, 0.0), 4),
            "confidence": abs(polarity),
        })
    return results
