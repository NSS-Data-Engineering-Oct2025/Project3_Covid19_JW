
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select case_month
from COVID_DB.MARTS.mart_cases_per_100k
where case_month is null



  
  
      
    ) dbt_internal_test