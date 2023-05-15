select year_month, section_name, count(*) as num_articles
from {{ ref('stg_nytdata') }}
group by 1, 2