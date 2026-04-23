import sys
sys.path.insert(0, ".")

from sentiment.vader_scorer import score as vader_score
from sentiment.textblob_scorer import score as textblob_score

POSITIVE_TEXT = "Kenya economy surges with record GDP growth and strong investor confidence."
NEGATIVE_TEXT = "Shilling crashes to historic low as inflation spirals and investors flee."
NEUTRAL_TEXT = "The Central Bank of Kenya held its monthly policy meeting today."


def test_vader_positive():
    results = vader_score([POSITIVE_TEXT])
    assert results[0]["label"] == "positive"
    assert results[0]["positive"] > 0


def test_vader_negative():
    results = vader_score([NEGATIVE_TEXT])
    assert results[0]["label"] in ("negative", "neutral")


def test_vader_returns_all_keys():
    results = vader_score([NEUTRAL_TEXT])
    assert {"label", "positive", "negative", "neutral", "confidence"} == set(results[0].keys())


def test_textblob_positive():
    results = textblob_score([POSITIVE_TEXT])
    assert results[0]["label"] in ("positive", "neutral")


def test_textblob_returns_all_keys():
    results = textblob_score([NEUTRAL_TEXT])
    assert {"label", "positive", "negative", "neutral", "confidence"} == set(results[0].keys())


def test_vader_batch():
    texts = [POSITIVE_TEXT, NEGATIVE_TEXT, NEUTRAL_TEXT]
    results = vader_score(texts)
    assert len(results) == 3


def test_textblob_batch():
    texts = [POSITIVE_TEXT, NEGATIVE_TEXT, NEUTRAL_TEXT]
    results = textblob_score(texts)
    assert len(results) == 3
