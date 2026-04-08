
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select severity_index
from COVID_DB.MARTS.mart_severity_index
where severity_index is null



  
  
      
    ) dbt_internal_test