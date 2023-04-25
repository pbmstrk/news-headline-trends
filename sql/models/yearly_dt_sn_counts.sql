with stg as (
    select document_type, section_name, extract('year' from pub_date) as yr, count(*) as num_articles 
    from {{ ref('stg_nytdata') }} 
    where extract('year' from pub_date) >= (select min(extract('year' from pub_date)) from {{ ref('stg_nytdata') }} where document_type = 'multimedia')
    and section_name <> 'Multimedia/Photos'
    group by 1, 2, 3  
)
select * from stg where document_type = 'multimedia' or document_type = 'article'
order by yr