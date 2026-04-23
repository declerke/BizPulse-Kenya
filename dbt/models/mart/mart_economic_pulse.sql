{{
  config(
    materialized='table',
    unique_key='pulse_date'
  )
}}

with forex as (
    select * from {{ ref('stg_forex') }}
),

rates as (
    select * from {{ ref('stg_rates') }}
),

forex_pivoted as (
    select
        rate_date                                                   as pulse_date,
        max(case when currency_pair = 'USD/KES' then mean_rate end) as usd_kes_mean,
        max(case when currency_pair = 'EUR/KES' then mean_rate end) as eur_kes_mean,
        max(case when currency_pair = 'GBP/KES' then mean_rate end) as gbp_kes_mean
    from forex
    group by rate_date
),

cbr as (
    select
        rate_date,
        max(rate_value) as cbr_rate
    from rates
    where lower(rate_type) like '%central bank%'
    group by rate_date
)

select
    coalesce(f.pulse_date, c.rate_date)     as pulse_date,
    c.cbr_rate,
    f.usd_kes_mean,
    f.eur_kes_mean,
    f.gbp_kes_mean,
    current_timestamp()                     as loaded_at
from forex_pivoted f
full outer join cbr c on f.pulse_date = c.rate_date
