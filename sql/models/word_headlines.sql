{{ config(materialized='table') }}

select word, 
year_month,
headline,
from {{ ref('words') }} 
where exists (select 1 from {{ source('raw_data', 'allow_words') }}  where allow_word = word)



