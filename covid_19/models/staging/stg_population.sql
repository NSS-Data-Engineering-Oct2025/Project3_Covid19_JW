with source as (
    select * from {{ source('raw', 'raw_population') }}
),

cleaned as (
    select
        -- FIPS normalization
        lpad(fips, 5, '0')      as county_fips,
        lpad(state, 2, '0')     as state_fips,

        -- Optional: 3-digit county code
        lpad(county, 3, '0')    as county_code,

        -- Cleaned name
        trim(name)               as county_name,

        -- Population numeric
        try_to_number(pop)       as population,

        current_timestamp()      as _loaded_at
    from source
    where fips is not null
      and pop is not null
)

select * from cleaned
