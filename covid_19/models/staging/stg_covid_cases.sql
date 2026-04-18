-- Staging: CDC COVID-19 cases
-- Light cleaning only — no business logic here.
-- Column names mapped from actual RAW_COVID_CASES schema (verified 2026-03-31).

with source as (
    select
        case_month,
        state_fips_code,
        county_fips_code,
        res_state,
        res_county,
        age_group,
        sex,
        race,
        ethnicity,
        current_status,
        symptom_status,
        hosp_yn,
        icu_yn,
        death_yn,
        underlying_conditions_yn
    from {{ source('raw', 'raw_covid_cases') }}
),

cleaned as (
    select
        -- Build a 5-digit FIPS key for joining
        lpad(state_fips_code, 2, '0') || lpad(county_fips_code, 3, '0') as county_fips,
        lpad(state_fips_code, 2, '0')                                    as state_fips,

        -- Normalize month to a proper date (first day of the month)
        try_to_date(case_month, 'YYYY-MM')                               as case_month,

        -- Geographic fields
        nullif(trim(res_state), '')   as res_state,
        nullif(trim(res_county), '')  as res_county,

        -- Demographic fields
        nullif(trim(age_group), '')   as age_group,
        nullif(trim(sex), '')         as sex,
        nullif(trim(race), '')        as race,
        nullif(trim(ethnicity), '')   as ethnicity,

        -- Clinical status fields
        nullif(trim(current_status), '')             as current_status,
        nullif(trim(symptom_status), '')             as symptom_status,
        nullif(trim(hosp_yn), '')                    as hosp_yn,
        nullif(trim(icu_yn), '')                     as icu_yn,
        nullif(trim(death_yn), '')                   as death_yn,
        nullif(trim(underlying_conditions_yn), '')   as underlying_conditions_yn,

        -- Derived binary flags for easier aggregation in intermediate/marts
        case when upper(death_yn) = 'YES' then 1 else 0 end   as is_death,
        case when upper(hosp_yn)  = 'YES' then 1 else 0 end   as is_hospitalized,
        case when upper(icu_yn)   = 'YES' then 1 else 0 end   as is_icu,

        current_timestamp() as _loaded_at

    from source
    where state_fips_code is not null
      and case_month is not null
)

select
    county_fips,
    state_fips,
    case_month,
    res_state,
    res_county,
    age_group,
    sex,
    race,
    ethnicity,
    current_status,
    symptom_status,
    hosp_yn,
    icu_yn,
    death_yn,
    underlying_conditions_yn,
    is_death,
    is_hospitalized,
    is_icu,
    _loaded_at
from cleaned
