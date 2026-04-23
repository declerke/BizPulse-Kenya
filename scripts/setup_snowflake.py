"""Run once before docker-compose up to create Snowflake database and tables."""
import os
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

DDL = """
CREATE DATABASE IF NOT EXISTS BIZPULSE;

CREATE SCHEMA IF NOT EXISTS BIZPULSE.RAW;
CREATE SCHEMA IF NOT EXISTS BIZPULSE.STAGING;
CREATE SCHEMA IF NOT EXISTS BIZPULSE.MART;

CREATE TABLE IF NOT EXISTS BIZPULSE.RAW.RAW_ARTICLES (
    id              VARCHAR(64) PRIMARY KEY,
    title           TEXT NOT NULL,
    summary         TEXT,
    link            TEXT,
    published_at    TIMESTAMP_TZ,
    source          VARCHAR(50),
    ingested_at     TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS BIZPULSE.RAW.RAW_CBK_FOREX (
    id              VARCHAR(64) PRIMARY KEY,
    rate_date       DATE NOT NULL,
    currency_pair   VARCHAR(10) NOT NULL,
    buying_rate     FLOAT,
    selling_rate    FLOAT,
    mean_rate       FLOAT,
    ingested_at     TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS BIZPULSE.RAW.RAW_CBK_RATES (
    id              VARCHAR(64) PRIMARY KEY,
    rate_date       DATE NOT NULL,
    rate_type       VARCHAR(50) NOT NULL,
    rate_value      FLOAT NOT NULL,
    ingested_at     TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS BIZPULSE.MART.MART_WEEKLY_BRIEFING (
    id              VARCHAR(64) PRIMARY KEY,
    week_start      DATE NOT NULL,
    briefing_text   TEXT NOT NULL,
    model_used      VARCHAR(100),
    generated_at    TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);

CREATE TABLE IF NOT EXISTS BIZPULSE.MART.MART_SENTIMENT_DAILY (
    sentiment_date  DATE NOT NULL,
    source          VARCHAR(50),
    positive_count  INT,
    negative_count  INT,
    neutral_count   INT,
    total_articles  INT,
    avg_confidence  FLOAT,
    loaded_at       TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (sentiment_date, source)
);

CREATE TABLE IF NOT EXISTS BIZPULSE.MART.MART_ECONOMIC_PULSE (
    pulse_date      DATE PRIMARY KEY,
    cbr_rate        FLOAT,
    usd_kes_mean    FLOAT,
    eur_kes_mean    FLOAT,
    gbp_kes_mean    FLOAT,
    overall_sentiment VARCHAR(20),
    loaded_at       TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP()
);
"""

def main():
    conn = snowflake.connector.connect(
        account=os.environ.get("SNOWFLAKE_ACCOUNT", "HFWPAZW-WC65846"),
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        role=os.environ["SNOWFLAKE_ROLE"],
    )
    cur = conn.cursor()
    for statement in [s.strip() for s in DDL.split(";") if s.strip()]:
        print(f"Executing: {statement[:60]}...")
        cur.execute(statement)
    cur.close()
    conn.close()
    print("\nSnowflake setup complete. BIZPULSE database and all tables created.")

if __name__ == "__main__":
    main()
