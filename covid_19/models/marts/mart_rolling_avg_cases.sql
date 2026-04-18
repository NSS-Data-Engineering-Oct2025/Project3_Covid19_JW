-- Mart: 7-day rolling average of new cases (approximated at monthly granularity)
-- Note: CDC cases data is monthly. We compute a 3-month rolling average as a
-- reasonable proxy — document this in the dashboard.

with monthly as (
    select
        state_fips,
        case_month,
        sum(total_cases) as monthly_cases
    from {{ ref('int_cases_with_population') }}
    group by 1, 2
),

rolling as (
    select
        state_fips,
        case_month,
        monthly_cases,
        avg(monthly_cases) over (
            partition by state_fips
            order by case_month
            rows between 2 preceding and current row
        ) as rolling_3mo_avg_cases
    from monthly
)

select
    state_fips,
    case_month,
    monthly_cases,
    rolling_3mo_avg_cases
from rolling
order by state_fips, case_month
