select 
section_name,
count(*) as num_articles
from {{ ref('stg_nytdata') }}
group by 1
having num_articles > 25000
order by 2 desc