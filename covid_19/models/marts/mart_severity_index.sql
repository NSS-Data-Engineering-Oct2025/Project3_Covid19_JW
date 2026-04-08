-- Mart: Severity Index by County
-- Custom metric: composite score combining hospitalization rate, ICU rate, and CFR.
-- Rationale: a single number that helps public health officials rank counties by
-- overall disease severity — useful for resource allocation and early warning.
--
-- Formula:
--   severity_index = (hosp_rate * 0.4) + (icu_rate * 0.4) + (cfr * 0.2)
-- Weights reflect that ICU burden and hospitalization are the strongest signals
-- of healthcare system stress, while CFR can lag due to reporting delays.

with cases_agg as (
    select
        county_fips,
        state_fips,
        county_name,
        sum(total_cases)            as total_cases,
        sum(total_hospitalizations) as total_hospitalizations,
        sum(total_deaths)           as total_deaths
    from {{ ref('int_cases_with_population') }}
    where total_cases > 0
    group by 1, 2, 3
),

icu_agg as (
    select
        county_fips,
        sum(is_icu) as total_icu_cases
    from {{ ref('stg_covid_cases') }}
    group by 1
),

joined as (
    select
        c.county_fips,
        c.state_fips,
        c.county_name,
        c.total_cases,
        c.total_hospitalizations,
        c.total_deaths,
        coalesce(i.total_icu_cases, 0) as total_icu_cases,

        round(100.0 * c.total_hospitalizations / nullif(c.total_cases, 0), 4) as hosp_rate_pct,
        round(100.0 * i.total_icu_cases        / nullif(c.total_cases, 0), 4) as icu_rate_pct,
        round(100.0 * c.total_deaths           / nullif(c.total_cases, 0), 4) as cfr_pct
    from cases_agg c
    left join icu_agg i on c.county_fips = i.county_fips
),

with_index as (
    select
        *,
        round(
            (coalesce(hosp_rate_pct, 0) * 0.4)
            + (coalesce(icu_rate_pct, 0) * 0.4)
            + (coalesce(cfr_pct, 0) * 0.2),
            4
        ) as severity_index
    from joined
)

select * from with_index
order by severity_index desc
