
  
    

create or replace transient table COVID_DB.MARTS.mart_case_fatality_rate
    
    
    
    as (-- Mart: Case fatality rate (CFR) by state and month
-- CFR = deaths / confirmed_cases × 100
-- Highlights regional healthcare capacity differences over time.

with base as (
    select
        state_fips,
        case_month,
        sum(total_cases)  as total_cases,
        sum(total_deaths) as total_deaths
    from COVID_DB.INTERMEDIATE.int_cases_with_population
    group by 1, 2
)

select
    state_fips,
    case_month,
    total_cases,
    total_deaths,
    round(
        total_deaths * 100.0 / nullif(total_cases, 0),
        4
    ) as case_fatality_rate_pct
from base
order by state_fips, case_month
    )
;


  