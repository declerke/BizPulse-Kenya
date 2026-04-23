with source as (
    select * from {{ source('raw', 'RAW_CBK_RATES') }}
),

cleaned as (
    select
        id,
        rate_date,
        trim(rate_type) as rate_type,
        rate_value,
        ingested_at
    from source
    where rate_value > 0
      and rate_type is not null
)

select * from cleaned
