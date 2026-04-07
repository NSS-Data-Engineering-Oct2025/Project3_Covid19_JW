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

        -- Geographic fields
        nullif(trim(res_state), '')   as res_state,
        nullif(trim(res_county), '')  as res_county,

        -- Demographics
        nullif(trim(age_group), '')      as age_group,
        nullif(trim(sex), '')            as sex,
        nullif(trim(race), '')           as race,
        nullif(trim(ethnicity), '')      as ethnicity,

        -- Outcomes
        nullif(trim(current_status), '') as current_status,
        nullif(trim(symptom_status), '')             as symptom_status,
        nullif(trim(hosp_yn), '')        as hosp_yn,
        nullif(trim(icu_yn), '')                     as icu_yn,
        nullif(trim(death_yn), '')                   as death_yn,
        nullif(trim(underlying_conditions_yn), '')   as underlying_conditions_yn,
        
        -- Flags
        case when lower(death_yn) = 'yes' then 1 else 0 end as is_death,
        case when lower(hosp_yn) in ('yes') then 1 else 0 end as is_hospitalized,
        case when lower(icu_yn) in ('yes') then 1 else 0 end as is_icu,

        current_timestamp() as _loaded_at
    from source
    where state_fips_code is not null
      and case_month is not null
)

select * from cleaned
