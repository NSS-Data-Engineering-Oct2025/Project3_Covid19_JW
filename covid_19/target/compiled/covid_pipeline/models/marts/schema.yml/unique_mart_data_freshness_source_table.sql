
    
    

select
    source_table as unique_field,
    count(*) as n_records

from COVID_DB.MARTS.mart_data_freshness
where source_table is not null
group by source_table
having count(*) > 1


