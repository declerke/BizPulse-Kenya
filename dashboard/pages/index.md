# BizPulse Kenya — Sentiment Dashboard

```sql daily_sentiment
select
    sentiment_date,
    source,
    total_articles,
    positive_count,
    negative_count,
    neutral_count
from snowflake.mart_sentiment_daily
order by sentiment_date desc
limit 90
```

```sql sentiment_totals
select
    sum(positive_count)     as total_positive,
    sum(negative_count)     as total_negative,
    sum(neutral_count)      as total_neutral,
    sum(total_articles)     as grand_total
from snowflake.mart_sentiment_daily
where sentiment_date >= current_date - interval '7 days'
```

<BigValue
  data={sentiment_totals}
  value=total_positive
  title="Positive Articles (7d)"
/>

<BigValue
  data={sentiment_totals}
  value=total_negative
  title="Negative Articles (7d)"
/>

<BigValue
  data={sentiment_totals}
  value=grand_total
  title="Total Articles (7d)"
/>

## Daily Article Volume by Source

<BarChart
  data={daily_sentiment}
  x=sentiment_date
  y=total_articles
  series=source
  title="Articles per Day by Source"
  xAxisTitle="Date"
  yAxisTitle="Article Count"
/>

## Sentiment Trend

<LineChart
  data={daily_sentiment}
  x=sentiment_date
  y={["positive_count", "negative_count", "neutral_count"]}
  title="Daily Sentiment Breakdown"
  xAxisTitle="Date"
  yAxisTitle="Article Count"
/>
