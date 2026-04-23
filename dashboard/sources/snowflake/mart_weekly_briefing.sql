select
    week_start,
    briefing_text,
    model_used,
    generated_at
from MART_WEEKLY_BRIEFING
order by generated_at desc
