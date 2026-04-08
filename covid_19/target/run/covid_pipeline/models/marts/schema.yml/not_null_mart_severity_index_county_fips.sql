
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select county_fips
from COVID_DB.MARTS.mart_severity_index
where county_fips is null



  
  
      
    ) dbt_internal_test