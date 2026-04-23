import os
import sys
import snowflake.connector
from datetime import datetime, timedelta

from airflow.sdk import dag, task

sys.path.insert(0, "/opt/airflow")


@dag(
    dag_id="bizpulse_kenya",
    schedule="0 6 * * *",
    start_date=datetime(2026, 4, 22),
    catchup=False,
    tags=["bizpulse", "kenya", "sentiment"],
    default_args={"retries": 1, "retry_delay": timedelta(minutes=3)},
)
def bizpulse_kenya():

    @task()
    def scrape_news() -> list[dict]:
        from ingestion.news_scraper import scrape_all
        articles = scrape_all()
        print(f"Scraped {len(articles)} articles")
        for a in articles:
            a["published_at"] = a["published_at"].isoformat()
        return articles

    @task()
    def scrape_cbk() -> dict:
        from ingestion.cbk_scraper import scrape_forex, scrape_interest_rates
        forex = scrape_forex()
        rates = scrape_interest_rates()
        for r in forex:
            r["rate_date"] = r["rate_date"].isoformat()
        for r in rates:
            r["rate_date"] = r["rate_date"].isoformat()
        return {"forex": forex, "rates": rates}

    @task()
    def load_raw_to_snowflake(articles: list[dict], cbk_data: dict) -> dict:
        from datetime import datetime, timezone
        from ingestion.snowflake_loader import load_articles, load_forex, load_rates

        for a in articles:
            a["published_at"] = datetime.fromisoformat(a["published_at"])
        from datetime import date
        for r in cbk_data["forex"]:
            r["rate_date"] = date.fromisoformat(r["rate_date"])
        for r in cbk_data["rates"]:
            r["rate_date"] = date.fromisoformat(r["rate_date"])

        n_articles = load_articles(articles)
        n_forex = load_forex(cbk_data["forex"])
        n_rates = load_rates(cbk_data["rates"])
        print(f"Loaded: {n_articles} articles, {n_forex} forex, {n_rates} rates")
        return {"articles": n_articles, "forex": n_forex, "rates": n_rates}

    @task()
    def run_sentiment_experiments(articles: list[dict]) -> dict:
        from sentiment.experiment_runner import run_experiments
        texts = [f"{a['title']}. {a.get('summary', '')}" for a in articles]
        if not texts:
            return {"champion": "finbert", "results": [], "run_ids": {}}
        result = run_experiments(texts)
        serializable_results = [
            {k: v for k, v in r.items()} for r in (result["results"] or [])
        ]
        return {
            "champion": result["champion"],
            "results": serializable_results,
            "run_ids": result["run_ids"],
        }

    @task()
    def dbt_run() -> str:
        import subprocess
        result = subprocess.run(
            ["dbt", "run", "--project-dir", "/opt/airflow/dbt",
             "--profiles-dir", "/opt/airflow/dbt"],
            capture_output=True, text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        return "dbt run complete"

    @task()
    def dbt_test() -> str:
        import subprocess
        result = subprocess.run(
            ["dbt", "test", "--project-dir", "/opt/airflow/dbt",
             "--profiles-dir", "/opt/airflow/dbt"],
            capture_output=True, text=True,
        )
        print(result.stdout)
        if result.returncode != 0:
            raise RuntimeError(result.stderr)
        return "dbt test complete"

    @task()
    def generate_briefing(articles: list[dict], sentiment_data: dict, cbk_data: dict) -> str:
        from briefing.generator import generate
        from ingestion.snowflake_loader import _get_conn

        sentiment_summary = {"positive_count": 0, "negative_count": 0, "neutral_count": 0}
        for r in sentiment_data.get("results", []):
            label = r.get("label", "neutral")
            if label in sentiment_summary:
                sentiment_summary[f"{label}_count"] += 1

        top_headlines = [a["title"] for a in articles[:10]]

        cbk_summary = {}
        for r in cbk_data.get("rates", []):
            if "Central Bank" in r.get("rate_type", ""):
                cbk_summary["cbr_rate"] = r["rate_value"]
        for r in cbk_data.get("forex", []):
            pair = r.get("currency_pair", "")
            if "USD" in pair:
                cbk_summary["usd_kes"] = r.get("mean_rate")
            elif "EUR" in pair:
                cbk_summary["eur_kes"] = r.get("mean_rate")
            elif "GBP" in pair:
                cbk_summary["gbp_kes"] = r.get("mean_rate")

        briefing = generate(sentiment_summary, top_headlines, cbk_summary)

        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            MERGE INTO BIZPULSE.MART.MART_WEEKLY_BRIEFING t
            USING (SELECT %s AS id) s ON t.id = s.id
            WHEN NOT MATCHED THEN INSERT
                (id, week_start, briefing_text, model_used)
            VALUES (%s, %s, %s, %s)
            """,
            (briefing["id"], briefing["id"], briefing["week_start"],
             briefing["briefing_text"], briefing["model_used"]),
        )
        cur.close()
        conn.close()
        return briefing["briefing_text"][:200]

    @task()
    def write_sentiment_mart(articles: list[dict], sentiment_data: dict) -> str:
        from datetime import date
        from ingestion.snowflake_loader import _get_conn

        results = sentiment_data.get("results", [])
        if not results or not articles:
            return "no sentiment data"

        today = date.today().isoformat()
        source_buckets: dict[str, dict] = {}
        for a, r in zip(articles, results):
            src = a.get("source", "unknown")
            if src not in source_buckets:
                source_buckets[src] = {"pos": 0, "neg": 0, "neu": 0, "conf": 0.0, "n": 0}
            b = source_buckets[src]
            label = r.get("label", "neutral")
            if label == "positive":
                b["pos"] += 1
            elif label == "negative":
                b["neg"] += 1
            else:
                b["neu"] += 1
            b["conf"] += r.get("confidence", 0.0)
            b["n"] += 1

        conn = _get_conn()
        cur = conn.cursor()
        for src, b in source_buckets.items():
            avg_conf = round(b["conf"] / b["n"], 4) if b["n"] else 0.0
            total = b["pos"] + b["neg"] + b["neu"]
            cur.execute(
                """
                MERGE INTO BIZPULSE.MART.MART_SENTIMENT_DAILY t
                USING (SELECT %s AS sentiment_date, %s AS source) s
                    ON t.sentiment_date = s.sentiment_date AND t.source = s.source
                WHEN MATCHED THEN UPDATE SET
                    positive_count = %s, negative_count = %s, neutral_count = %s,
                    total_articles = %s, avg_confidence = %s, loaded_at = CURRENT_TIMESTAMP()
                WHEN NOT MATCHED THEN INSERT
                    (sentiment_date, source, positive_count, negative_count, neutral_count,
                     total_articles, avg_confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (today, src,
                 b["pos"], b["neg"], b["neu"], total, avg_conf,
                 today, src, b["pos"], b["neg"], b["neu"], total, avg_conf),
            )
        cur.close()
        conn.close()
        total_written = sum(b["n"] for b in source_buckets.values())
        print(f"Wrote sentiment mart: {total_written} articles across {len(source_buckets)} sources")
        return f"{total_written} articles written"

    @task()
    def log_summary(load_counts: dict, sentiment_data: dict, briefing_preview: str):
        results = sentiment_data.get("results", [])
        pos = sum(1 for r in results if r.get("label") == "positive")
        neg = sum(1 for r in results if r.get("label") == "negative")
        neu = sum(1 for r in results if r.get("label") == "neutral")
        print("=" * 60)
        print("BizPulse Kenya — Daily Run Summary")
        print(f"  Articles loaded : {load_counts.get('articles', 0)}")
        print(f"  Forex records   : {load_counts.get('forex', 0)}")
        print(f"  Rate records    : {load_counts.get('rates', 0)}")
        print(f"  Sentiment       : {pos} pos / {neg} neg / {neu} neu")
        print(f"  Briefing preview: {briefing_preview}...")
        print("=" * 60)

    articles = scrape_news()
    cbk_data = scrape_cbk()
    load_counts = load_raw_to_snowflake(articles, cbk_data)
    sentiment_data = run_sentiment_experiments(articles)
    sentiment_mart_status = write_sentiment_mart(articles, sentiment_data)
    dbt_run_status = dbt_run()
    dbt_test_status = dbt_test()
    briefing_preview = generate_briefing(articles, sentiment_data, cbk_data)
    log_summary(load_counts, sentiment_data, briefing_preview)

    load_counts >> dbt_run_status >> dbt_test_status
    sentiment_mart_status >> dbt_run_status


bizpulse_kenya()
