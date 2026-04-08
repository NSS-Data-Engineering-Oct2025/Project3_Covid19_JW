-- Custom test: case fatality rate must be between 0% and 100%.
-- Values outside this range indicate bad case or death counts.
-- Returns rows that FAIL the test (dbt expects 0 rows for a passing test).

select
    state_fips,
    case_month,
    total_cases,
    total_deaths,
    case_fatality_rate_pct
from COVID_DB.MARTS.mart_case_fatality_rate
where case_fatality_rate_pct < 0
   or case_fatality_rate_pct > 100