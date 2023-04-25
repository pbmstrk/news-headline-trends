with processed_data as (
    select
        extract('year' from pub_date) as year,
        extract('month' from pub_date) as month, 
        section_name,
        headline 
    from {{ ref('stg_nytdata') }} n
    where exists (select 1 from {{ ref('sn_distribution') }} r where n.section_name = r.section_name)
)

select concat(year, '-', month) as year_month, section_name, count(*) as num_articles
from processed_data
group by 1, 2