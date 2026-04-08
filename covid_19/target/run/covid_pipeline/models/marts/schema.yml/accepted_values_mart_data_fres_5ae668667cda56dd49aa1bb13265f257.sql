
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

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



  
  
      
    ) dbt_internal_test