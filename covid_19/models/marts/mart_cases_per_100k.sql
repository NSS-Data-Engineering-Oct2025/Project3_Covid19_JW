-- Mart: Cases per 100k population by county and month
-- Normalizes case counts for fair comparison across counties of different sizes.

with cases_normalized as (
    select
        county_fips,
        county_name,
        state_fips,
        case_month,
        total_cases,
        population,
        round(
            total_cases * 100000.0 / nullif(population, 0),
            2
        ) as cases_per_100k
    from {{ ref('int_cases_with_population') }}
    where population is not null
)

select *
from cases_normalized
order by state_fips, county_fips, case_month
