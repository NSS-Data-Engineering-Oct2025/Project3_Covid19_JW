-- Mart: Severity Index by County
-- Custom metric: composite score combining hospitalization rate, ICU rate, and CFR.
-- Rationale: a single number that helps public health officials rank counties by
-- overall disease severity — useful for resource allocation and early warning.
--
-- Formula:
--   severity_index = (hosp_rate * 0.4) + (icu_rate * 0.4) + (cfr * 0.2)
-- Weights reflect that ICU burden and hospitalization are the strongest signals
-- of healthcare system stress, while CFR can lag due to reporting delays.

with base as (
    select
        county_fips,
        state_fips,
        county_name,
        sum(total_cases)            as total_cases,
        sum(total_hospitalizations) as total_hospitalizations,
        sum(total_icu)              as total_icu_cases,
        sum(total_deaths)           as total_deaths
    from {{ ref('int_cases_with_population') }}
    where total_cases > 0
    group by 1, 2, 3
),

with_rates as (
    select
        county_fips,
        state_fips,
        county_name,
        total_cases,
        total_hospitalizations,
        total_icu_cases,
        total_deaths,
        round(100.0 * total_hospitalizations / nullif(total_cases, 0), 4) as hosp_rate_pct,
        round(100.0 * total_icu_cases        / nullif(total_cases, 0), 4) as icu_rate_pct,
        round(100.0 * total_deaths           / nullif(total_cases, 0), 4) as cfr_pct
    from base
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
    from with_rates
)

select * from with_index
order by severity_index desc
