select 
document_type,
count(*) as num_articles
from {{ ref('stg_nytdata') }}
group by 1