
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select freshness_status
from COVID_DB.MARTS.mart_data_freshness
where freshness_status is null



  
  
      
    ) dbt_internal_test