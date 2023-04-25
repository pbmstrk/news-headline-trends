with stg as (
    select document_type, extract('year' from pub_date) as yr, count(*) as num_articles 
    from {{ ref('stg_nytdata') }} 
    group by 1, 2  
),
yr_totals as (
select *, sum(num_articles) over(partition by yr) as year_sum, num_articles::real/year_sum::real as proportion from stg
)

select * from yr_totals where document_type = 'multimedia' 
order by yr