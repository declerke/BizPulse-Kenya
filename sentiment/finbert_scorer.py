from transformers import pipeline

_pipe = None


def _get_pipe():
    global _pipe
    if _pipe is None:
        _pipe = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            device=-1,
            top_k=None,
        )
    return _pipe


def score(texts: list[str]) -> list[dict]:
    pipe = _get_pipe()
    results = []
    for text in texts:
        text = text[:512]
        try:
            preds = pipe(text)[0]
            scores = {p["label"].lower(): p["score"] for p in preds}
            label = max(scores, key=scores.get)
            results.append({
                "label": label,
                "positive": scores.get("positive", 0.0),
                "negative": scores.get("negative", 0.0),
                "neutral": scores.get("neutral", 0.0),
                "confidence": scores[label],
            })
        except Exception:
            results.append({"label": "neutral", "positive": 0.0, "negative": 0.0, "neutral": 1.0, "confidence": 1.0})
    return results
