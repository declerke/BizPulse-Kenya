import os
import hashlib
from datetime import date, datetime, timezone, timedelta

from groq import Groq

MODEL = "llama-3.1-8b-instant"


def _build_prompt(
    sentiment_summary: dict,
    top_headlines: list[str],
    cbk_data: dict,
) -> str:
    pos = sentiment_summary.get("positive_count", 0)
    neg = sentiment_summary.get("negative_count", 0)
    neu = sentiment_summary.get("neutral_count", 0)
    total = pos + neg + neu or 1
    label_counts = {"positive_count": pos, "negative_count": neg, "neutral_count": neu}
    dominant = max(label_counts, key=label_counts.get).replace("_count", "")

    headlines_text = "\n".join(f"- {h}" for h in top_headlines[:10])
    cbr = cbk_data.get("cbr_rate", "N/A")
    usd = cbk_data.get("usd_kes", "N/A")
    eur = cbk_data.get("eur_kes", "N/A")
    gbp = cbk_data.get("gbp_kes", "N/A")

    return f"""You are a senior Kenya business intelligence analyst. Write a concise weekly economic briefing (3–4 paragraphs) based on the data below.

SENTIMENT DATA (this week):
- Positive articles: {pos} ({round(pos/total*100)}%)
- Negative articles: {neg} ({round(neg/total*100)}%)
- Neutral articles: {neu} ({round(neu/total*100)}%)
- Overall tone: {dominant}

TOP HEADLINES THIS WEEK:
{headlines_text}

CBK ECONOMIC INDICATORS:
- Central Bank Rate: {cbr}%
- USD/KES: {usd}
- EUR/KES: {eur}
- GBP/KES: {gbp}

Write the briefing in a professional tone. Lead with the dominant sentiment driver, then cover the CBK indicators, then close with a forward-looking outlook for Kenya's business environment. Do not use bullet points — flowing paragraphs only."""


def generate(
    sentiment_summary: dict,
    top_headlines: list[str],
    cbk_data: dict,
) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    prompt = _build_prompt(sentiment_summary, top_headlines, cbk_data)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=600,
    )

    briefing_text = response.choices[0].message.content.strip()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    return {
        "id": hashlib.sha256(f"{week_start}:{briefing_text[:50]}".encode()).hexdigest()[:64],
        "week_start": week_start,
        "briefing_text": briefing_text,
        "model_used": MODEL,
        "generated_at": datetime.now(timezone.utc),
    }
