select
    pulse_date,
    cbr_rate,
    usd_kes_mean,
    eur_kes_mean,
    gbp_kes_mean
from MART_ECONOMIC_PULSE
order by pulse_date desc
