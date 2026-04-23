# Economic Pulse — CBK Rates & Forex

```sql economic_pulse
select
    pulse_date,
    cbr_rate,
    usd_kes_mean,
    eur_kes_mean,
    gbp_kes_mean
from snowflake.mart_economic_pulse
order by pulse_date desc
limit 90
```

```sql latest_indicators
select
    cbr_rate,
    usd_kes_mean,
    eur_kes_mean,
    gbp_kes_mean,
    pulse_date
from snowflake.mart_economic_pulse
order by pulse_date desc
limit 1
```

<BigValue
  data={latest_indicators}
  value=cbr_rate
  title="Central Bank Rate (%)"
/>

<BigValue
  data={latest_indicators}
  value=usd_kes_mean
  title="USD/KES (Mean)"
/>

<BigValue
  data={latest_indicators}
  value=eur_kes_mean
  title="EUR/KES (Mean)"
/>

<BigValue
  data={latest_indicators}
  value=gbp_kes_mean
  title="GBP/KES (Mean)"
/>

## Forex Rate Trends

<LineChart
  data={economic_pulse}
  x=pulse_date
  y={["usd_kes_mean", "eur_kes_mean", "gbp_kes_mean"]}
  title="KES Exchange Rates Over Time"
  xAxisTitle="Date"
  yAxisTitle="KES Rate"
/>

## Central Bank Rate History

<AreaChart
  data={economic_pulse}
  x=pulse_date
  y=cbr_rate
  title="CBK Central Bank Rate (%)"
  xAxisTitle="Date"
  yAxisTitle="Rate (%)"
  fillColor="#2563eb"
/>
