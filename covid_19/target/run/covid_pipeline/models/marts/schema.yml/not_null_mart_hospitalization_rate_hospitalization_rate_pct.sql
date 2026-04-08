
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select hospitalization_rate_pct
from COVID_DB.MARTS.mart_hospitalization_rate
where hospitalization_rate_pct is null



  
  
      
    ) dbt_internal_test