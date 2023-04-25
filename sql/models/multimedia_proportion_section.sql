with stg as (
    select document_type, section_name, count(*) as num_articles 
    from {{ ref('stg_nytdata') }} 
     where extract('year' from pub_date) >= (select min(extract('year' from pub_date)) from {{ ref('stg_nytdata') }} where document_type = 'multimedia')
     and section_name <> 'Multimedia/Photos'
    group by 1, 2  
),
section_totals as (
select *, sum(num_articles) over(partition by section_name) as section_sum, num_articles::real/section_sum::real as proportion from stg
)

select section_name, section_sum, proportion from section_totals where document_type = 'multimedia' 
and section_sum > 10000
order by 3 desc