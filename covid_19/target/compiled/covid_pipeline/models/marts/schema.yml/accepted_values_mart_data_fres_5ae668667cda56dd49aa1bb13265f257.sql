
    
    

with all_values as (

    select
        freshness_status as value_field,
        count(*) as n_records

    from COVID_DB.MARTS.mart_data_freshness
    group by freshness_status

)

select *
from all_values
where value_field not in (
    'Fresh','Recent','Stale','Very Stale'
)


