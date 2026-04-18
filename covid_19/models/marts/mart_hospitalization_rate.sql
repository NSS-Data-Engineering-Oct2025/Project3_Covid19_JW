-- Mart: Hospitalization Rate by State and Month
-- Custom metric: what percentage of confirmed cases required hospitalization?
-- Rationale: CFR shows who died, but hospitalization rate shows healthcare system burden.
-- A region with high hospitalization rate signals stress on hospital capacity even
-- if the fatality rate is low (e.g. due to better ICU care).

with base as (
    select
        state_fips,
        case_month,
        sum(total_cases)            as total_cases,
        sum(total_hospitalizations) as total_hospitalizations,
        sum(total_deaths)           as total_deaths
    from {{ ref('int_cases_with_population') }}
    where total_cases > 0
    group by 1, 2
),

with_rate as (
    select
        state_fips,
        case_month,
        total_cases,
        total_hospitalizations,
        total_deaths,
        round(
            100.0 * total_hospitalizations / nullif(total_cases, 0),
            4
        ) as hospitalization_rate_pct
    from base
)

select
    state_fips,
    case_month,
    total_cases,
    total_hospitalizations,
    total_deaths,
    hospitalization_rate_pct
from with_rate
order by state_fips, case_month
