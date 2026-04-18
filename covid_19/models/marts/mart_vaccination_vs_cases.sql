-- Mart: Vaccination coverage vs case rate by county
-- Joins the latest vaccination snapshot with cumulative case counts.
-- Enables correlation analysis: do more-vaccinated counties show fewer cases?

with cases_cumulative as (
    select
        county_fips,
        sum(total_cases)  as total_cases,
        sum(total_deaths) as total_deaths,
        max(population)   as population
    from {{ ref('int_cases_with_population') }}
    group by 1
),

vaccinations as (
    select
        county_fips,
        state_abbrev,
        county_name,
        latest_vaccination_date,
        pct_series_complete,
        pct_boosted
    from {{ ref('int_vaccinations_with_population') }}
)

select
    v.county_fips,
    v.state_abbrev,
    v.county_name,
    v.latest_vaccination_date,
    v.pct_series_complete,
    v.pct_boosted,
    c.total_cases,
    c.total_deaths,
    c.population,
    round(
        c.total_cases * 100000.0 / nullif(c.population, 0),
        2
    ) as cumulative_cases_per_100k

from vaccinations v
left join cases_cumulative c on v.county_fips = c.county_fips
order by v.state_abbrev, v.county_fips
