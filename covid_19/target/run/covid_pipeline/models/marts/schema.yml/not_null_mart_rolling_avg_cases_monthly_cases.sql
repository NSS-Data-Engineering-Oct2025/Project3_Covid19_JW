
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select monthly_cases
from COVID_DB.MARTS.mart_rolling_avg_cases
where monthly_cases is null



  
  
      
    ) dbt_internal_test