-- Mart: Vaccination coverage vs case rate by county
-- Joins the latest vaccination snapshot with cumulative case counts.
-- Includes robust per-100k metrics and filters unknown counties.

with cases_cumulative as (
    select
        county_fips,
        sum(total_cases)  as total_cases,
        sum(total_deaths) as total_deaths,
        max(population)   as population
    from {{ ref('int_cases_with_population') }}
    group by 1
),

latest_vaccinations as (
    select *
    from (
        select *,
               row_number() over (partition by county_fips order by latest_vaccination_date desc) as rn
        from {{ ref('int_vaccinations_with_population') }}
    ) t
    where rn = 1
      and county_fips not in ('00000', 'UNK')
)

select
    v.county_fips,
    v.state_abbrev,
    v.county_name,
    v.latest_vaccination_date,
    v.pct_series_complete,
    v.pct_boosted,
    v.series_complete_cumulative,
    v.booster_cumulative,
    c.total_cases,
    c.total_deaths,
    c.population,
    round(c.total_cases * 100000.0 / nullif(c.population, 0), 2) as cumulative_cases_per_100k,
    round(c.total_deaths * 100000.0 / nullif(c.population, 0), 2) as deaths_per_100k

from latest_vaccinations v
left join cases_cumulative c on v.county_fips = c.county_fips

order by v.state_abbrev, v.county_fips
