
    
    

select
    county_fips as unique_field,
    count(*) as n_records

from COVID_DB.MARTS.mart_severity_index
where county_fips is not null
group by county_fips
having count(*) > 1


