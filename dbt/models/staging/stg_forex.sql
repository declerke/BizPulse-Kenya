with source as (
    select * from {{ source('raw', 'RAW_CBK_FOREX') }}
),

cleaned as (
    select
        id,
        rate_date,
        currency_pair,
        buying_rate,
        selling_rate,
        coalesce(mean_rate, (buying_rate + selling_rate) / 2) as mean_rate,
        ingested_at
    from source
    where currency_pair is not null
      and (buying_rate is not null or selling_rate is not null)
)

select * from cleaned
