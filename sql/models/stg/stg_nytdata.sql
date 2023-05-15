with stg_data as (select 
    headline,
    cast(pub_date as timestamp) as pub_date,
    document_type,
    news_desk,
    type_of_material,
    word_count,
    web_url,
    source,
    section_name, 
    filename
    from {{ source('raw_data', 'nytdata') }}
)

select *, 
concat(extract('year' from pub_date), '-', right('00' || cast(extract('month' from pub_date) as varchar), 2)) as year_month from stg_data
where extract('year' from pub_date) = cast(filename[7:10] as int)