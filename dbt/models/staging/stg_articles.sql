with source as (
    select * from {{ source('raw', 'RAW_ARTICLES') }}
),

cleaned as (
    select
        id,
        trim(title)                                         as title,
        trim(coalesce(summary, ''))                         as summary,
        link,
        convert_timezone('Africa/Nairobi', published_at)   as published_at_eat,
        date(convert_timezone('Africa/Nairobi', published_at)) as article_date,
        source,
        ingested_at
    from source
    where title is not null
      and length(trim(title)) > 5
)

select * from cleaned
