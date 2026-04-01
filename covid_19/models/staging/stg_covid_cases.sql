with source as (
    select * from {{ source('raw', 'raw_covid_cases') }}
),

cleaned as (
    select
        -- FIPS normalization for joins
        lpad(state_fips_code, 2, '0') || lpad(county_fips_code, 3, '0') as county_fips,
        lpad(state_fips_code, 2, '0')                                    as state_fips,

        -- Date normalization
        try_to_date(case_month, 'YYYY-MM')                                 as case_month,

        -- Demographics
        nullif(trim(age_group), '')      as age_group,
        nullif(trim(sex), '')            as sex,
        nullif(trim(race), '')           as race,
        nullif(trim(ethnicity), '')      as ethnicity,

        -- Outcomes
        nullif(trim(current_status), '') as outcome,
        nullif(trim(hosp_yn), '')        as hospitalization,

        -- Flags
        case when lower(current_status) = 'death' then 1 else 0 end as is_death,
        case when lower(hosp_yn) in ('yes','y') then 1 else 0 end as is_hospitalized,

        current_timestamp() as _loaded_at
    from source
    where state_fips_code is not null
      and case_month is not null
)

select * from cleaned
