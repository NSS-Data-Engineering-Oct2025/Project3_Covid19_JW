
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    source_table as unique_field,
    count(*) as n_records

from COVID_DB.MARTS.mart_data_freshness
where source_table is not null
group by source_table
having count(*) > 1



  
  
      
    ) dbt_internal_test