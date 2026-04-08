
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select source_table
from COVID_DB.MARTS.mart_data_freshness
where source_table is null



  
  
      
    ) dbt_internal_test