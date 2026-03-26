-- Staging: CDC COVID-19 vaccinations by county
-- Light cleaning only — cast types, normalize FIPS, drop junk rows.

with source as (
    select * from {{ source('raw', 'raw_vaccinations') }}
),

cleaned as (
    select
        lpad(fips, 5, '0')                    as county_fips,
        nullif(trim(recip_county), '')         as county_name,
        upper(trim(recip_state))               as state_abbrev,
        try_to_date(date)                      as vaccination_date,

        try_to_number(administered_dose1_recip)  as dose1_cumulative,
        try_to_number(series_complete_yes)        as series_complete_cumulative,
        try_to_number(booster_doses)              as booster_cumulative,
        try_to_number(census2019)                 as census2019_pop,

        current_timestamp() as _loaded_at

    from source
    where fips is not null
      and fips not in ('UNK', 'UNKNOWN', '')
      and date is not null
)

select * from cleaned
