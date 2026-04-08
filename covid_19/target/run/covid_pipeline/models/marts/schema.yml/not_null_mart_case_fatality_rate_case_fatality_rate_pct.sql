
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select case_fatality_rate_pct
from COVID_DB.MARTS.mart_case_fatality_rate
where case_fatality_rate_pct is null



  
  
      
    ) dbt_internal_test