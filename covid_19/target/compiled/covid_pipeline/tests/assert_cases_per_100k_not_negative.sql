-- Custom test: cases_per_100k should never be negative.
-- A negative value would indicate a data error in case counts or population.
-- Returns rows that FAIL the test (dbt expects 0 rows for a passing test).

select
    county_fips,
    county_name,
    case_month,
    cases_per_100k
from COVID_DB.MARTS.mart_cases_per_100k
where cases_per_100k < 0