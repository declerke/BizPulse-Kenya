select
    sentiment_date,
    source,
    total_articles,
    positive_count,
    negative_count,
    neutral_count
from MART_SENTIMENT_DAILY
order by sentiment_date desc
