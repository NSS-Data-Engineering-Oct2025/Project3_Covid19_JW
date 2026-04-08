-- Intermediate: CDC cases enriched with Census population
-- Aggregates case counts to monthly county level, then joins population.
-- Used by: mart_cases_per_100k, mart_case_fatality_rate, mart_rolling_avg_cases

with cases as (
    select
        county_fips,
        state_fips,
        case_month,
        count(*)        as total_cases,
        sum(is_death)   as total_deaths,
        sum(is_hospitalized) as total_hospitalizations
    from COVID_DB.STAGING.stg_covid_cases
    group by 1, 2, 3
),

population as (
    select
        county_fips,
        county_name,
        population
    from COVID_DB.STAGING.stg_population
),

joined as (
    select
        c.county_fips,
        c.state_fips,
        c.case_month,
        c.total_cases,
        c.total_deaths,
        c.total_hospitalizations,
        p.county_name,
        p.population
    from cases c
    left join population p
        on c.county_fips = p.county_fips
)

select * from joined