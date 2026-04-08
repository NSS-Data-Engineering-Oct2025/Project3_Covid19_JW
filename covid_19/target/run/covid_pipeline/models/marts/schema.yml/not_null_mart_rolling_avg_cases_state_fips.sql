
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select state_fips
from COVID_DB.MARTS.mart_rolling_avg_cases
where state_fips is null



  
  
      
    ) dbt_internal_test