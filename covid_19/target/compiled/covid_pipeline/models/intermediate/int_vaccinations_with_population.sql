-- Intermediate: CDC vaccinations enriched with Census population
-- Takes the latest vaccination snapshot per county (max date),
-- joins population for coverage rate calculations.
-- Used by: mart_vaccination_vs_cases

with vaccinations as (
    select
        county_fips,
        state_abbrev,
        county_name,
        vaccination_date,
        dose1_cumulative,
        series_complete_cumulative,
        booster_cumulative,
        census2019_pop,
        -- Rank to get the most recent snapshot per county
        row_number() over (
            partition by county_fips
            order by vaccination_date desc
        ) as rn
    from COVID_DB.STAGING.stg_vaccinations
),

latest as (
    select * from vaccinations where rn = 1
),

population as (
    select county_fips, population
    from COVID_DB.STAGING.stg_population
),

joined as (
    select
        v.county_fips,
        v.state_abbrev,
        v.county_name,
        v.vaccination_date                as latest_vaccination_date,
        v.dose1_cumulative,
        v.series_complete_cumulative,
        v.booster_cumulative,
        coalesce(p.population, v.census2019_pop) as population,

        -- Coverage rates (cap at 100% to handle reporting artifacts)
        least(
            round(v.series_complete_cumulative * 100.0 / nullif(coalesce(p.population, v.census2019_pop), 0), 2),
            100
        ) as pct_series_complete,

        least(
            round(v.booster_cumulative * 100.0 / nullif(coalesce(p.population, v.census2019_pop), 0), 2),
            100
        ) as pct_boosted

    from latest v
    left join population p on v.county_fips = p.county_fips
)

select * from joined