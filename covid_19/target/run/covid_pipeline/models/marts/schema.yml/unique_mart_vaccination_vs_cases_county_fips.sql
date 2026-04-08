
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    county_fips as unique_field,
    count(*) as n_records

from COVID_DB.MARTS.mart_vaccination_vs_cases
where county_fips is not null
group by county_fips
having count(*) > 1



  
  
      
    ) dbt_internal_test