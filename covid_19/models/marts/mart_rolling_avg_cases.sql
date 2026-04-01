-- Mart: 3-month rolling average of new COVID-19 cases by state
-- Note: CDC cases data is monthly. 
--       Rolling average approximates 7-day trends at monthly granularity.

with monthly_cases as (
    select
        state_fips,
        case_month,
        sum(total_cases) as monthly_cases
    from {{ ref('int_cases_with_population') }}
    group by state_fips, case_month
),

rolling_avg as (
    select
        state_fips,
        case_month,
        monthly_cases,
        round(
            avg(monthly_cases) over (
                partition by state_fips
                order by case_month
                rows between 2 preceding and current row
            ),
            2
        ) as rolling_3mo_avg_cases
    from monthly_cases
)

select *
from rolling_avg
order by state_fips, case_month
