-- Staging: US Census 2023 county population estimates
-- Static dataset — one row per county.

with source as (
    select * from COVID_DB.RAW.raw_population
),

cleaned as (
    select
        lpad(fips, 5, '0')          as county_fips,
        lpad(state, 2, '0')         as state_fips,
        lpad(county, 3, '0')        as county_code,
        trim(name)                   as county_name,
        try_to_number(pop)           as population,

        current_timestamp() as _loaded_at

    from source
    where fips is not null
      and pop is not null
)

select * from cleaned