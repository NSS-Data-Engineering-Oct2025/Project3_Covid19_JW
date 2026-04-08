-- Mart: Data freshness report by source
-- Shows when each source was last loaded by reading _loaded_at from staging views.
-- Staging models add current_timestamp() as _loaded_at on every dbt run.

with freshness as (
    select
        'raw_covid_cases'    as source_table,
        'CDC SODA n8mc-b4w4' as source_name,
        max(_loaded_at)      as last_loaded_at
    from COVID_DB.STAGING.stg_covid_cases

    union all

    select
        'raw_vaccinations'   as source_table,
        'CDC SODA 8xkx-amqh' as source_name,
        max(_loaded_at)      as last_loaded_at
    from COVID_DB.STAGING.stg_vaccinations

    union all

    select
        'raw_population'     as source_table,
        'US Census PEP 2023' as source_name,
        max(_loaded_at)      as last_loaded_at
    from COVID_DB.STAGING.stg_population
)

select
    source_table,
    source_name,
    last_loaded_at,
    datediff('hour', last_loaded_at, current_timestamp())  as hours_since_load,
    case
        when datediff('day', last_loaded_at, current_timestamp()) <= 1  then 'Fresh'
        when datediff('day', last_loaded_at, current_timestamp()) <= 7  then 'Recent'
        when datediff('day', last_loaded_at, current_timestamp()) <= 30 then 'Stale'
        else 'Very Stale'
    end as freshness_status

from freshness
order by source_table