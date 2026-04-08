-- Custom test: all case records must be from 2020 or later.
-- COVID-19 did not exist before 2020 — earlier dates indicate bad data.
-- Returns rows that FAIL the test (dbt expects 0 rows for a passing test).

select
    state_fips,
    case_month,
    total_cases
from {{ ref('int_cases_with_population') }}
where case_month < '2020-01-01'
