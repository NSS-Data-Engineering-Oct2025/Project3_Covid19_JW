
  
    

create or replace transient table COVID_DB.MARTS.mart_cases_per_100k
    
    
    
    as (-- Mart: Cases per 100k population by county and month
-- Normalizes case counts for fair comparison across counties of different sizes.

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
from COVID_DB.INTERMEDIATE.int_cases_with_population
where population is not null
order by state_fips, county_fips, case_month
    )
;


  