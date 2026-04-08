
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_cases
from COVID_DB.MARTS.mart_hospitalization_rate
where total_cases is null



  
  
      
    ) dbt_internal_test