from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


def _compound_to_label(compound: float) -> str:
    if compound >= 0.05:
        return "positive"
    elif compound <= -0.05:
        return "negative"
    return "neutral"


def score(texts: list[str]) -> list[dict]:
    analyzer = _get_analyzer()
    results = []
    for text in texts:
        vs = analyzer.polarity_scores(text)
        label = _compound_to_label(vs["compound"])
        confidence = abs(vs["compound"])
        results.append({
            "label": label,
            "positive": vs["pos"],
            "negative": vs["neg"],
            "neutral": vs["neu"],
            "confidence": confidence,
        })
    return results
