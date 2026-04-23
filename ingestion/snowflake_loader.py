import os
import snowflake.connector
from datetime import datetime, timezone


def _get_conn():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        role=os.environ["SNOWFLAKE_ROLE"],
    )


def load_articles(articles: list[dict]) -> int:
    if not articles:
        return 0
    conn = _get_conn()
    cur = conn.cursor()
    for a in articles:
        cur.execute(
            """
            MERGE INTO BIZPULSE.RAW.RAW_ARTICLES t
            USING (SELECT %s AS id) s ON t.id = s.id
            WHEN NOT MATCHED THEN INSERT
                (id, title, summary, link, published_at, source)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (a["id"], a["id"], a["title"], a.get("summary", ""),
             a.get("link", ""), a["published_at"], a["source"]),
        )
    cur.close()
    conn.close()
    return len(articles)


def load_forex(records: list[dict]) -> int:
    if not records:
        return 0
    conn = _get_conn()
    cur = conn.cursor()
    for r in records:
        cur.execute(
            """
            MERGE INTO BIZPULSE.RAW.RAW_CBK_FOREX t
            USING (SELECT %s AS id) s ON t.id = s.id
            WHEN NOT MATCHED THEN INSERT
                (id, rate_date, currency_pair, buying_rate, selling_rate, mean_rate)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (r["id"], r["id"], r["rate_date"], r["currency_pair"],
             r.get("buying_rate"), r.get("selling_rate"), r.get("mean_rate")),
        )
    cur.close()
    conn.close()
    return len(records)


def load_rates(records: list[dict]) -> int:
    if not records:
        return 0
    conn = _get_conn()
    cur = conn.cursor()
    for r in records:
        cur.execute(
            """
            MERGE INTO BIZPULSE.RAW.RAW_CBK_RATES t
            USING (SELECT %s AS id) s ON t.id = s.id
            WHEN NOT MATCHED THEN INSERT
                (id, rate_date, rate_type, rate_value)
            VALUES (%s, %s, %s, %s)
            """,
            (r["id"], r["id"], r["rate_date"], r["rate_type"], r["rate_value"]),
        )
    cur.close()
    conn.close()
    return len(records)
