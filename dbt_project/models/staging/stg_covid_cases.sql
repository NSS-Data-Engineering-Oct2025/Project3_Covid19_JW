-- Staging: CDC COVID-19 cases
-- Light cleaning only — no business logic here.
-- One row per case record from the CDC SODA API.

with source as (
    select * from {{ source('raw', 'raw_covid_cases') }}
),

cleaned as (
    select
        -- Build a 5-digit FIPS key for joining
        lpad(state_fips_code, 2, '0') || lpad(county_fips_code, 3, '0') as county_fips,
        lpad(state_fips_code, 2, '0')                                    as state_fips,

        -- Normalize month to a proper date (first day of the month)
        try_to_date(case_month, 'YYYY-MM')                               as case_month,

        -- Demographic fields
        nullif(trim(age_group), '')    as age_group,
        nullif(trim(sex), '')          as sex,
        nullif(trim(race), '')         as race,
        nullif(trim(ethnicity), '')    as ethnicity,

        -- Outcome fields
        nullif(trim(outcome), '')         as outcome,
        nullif(trim(hospitalization), '') as hospitalization,

        -- Derived flags for easier aggregation
        case when lower(outcome) = 'death' then 1 else 0 end         as is_death,
        case when lower(hospitalization) = 'yes' then 1 else 0 end   as is_hospitalized,

        current_timestamp() as _loaded_at

    from source
    where state_fips_code is not null
      and case_month is not null
)

select * from cleaned
