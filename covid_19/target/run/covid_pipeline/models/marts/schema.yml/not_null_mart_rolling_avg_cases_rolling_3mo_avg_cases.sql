
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select rolling_3mo_avg_cases
from COVID_DB.MARTS.mart_rolling_avg_cases
where rolling_3mo_avg_cases is null



  
  
      
    ) dbt_internal_test