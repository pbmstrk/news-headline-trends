with processed_headlines as (

    select regexp_replace(headline, '[\d\W_]', ' ', 'g').trim() as processed_headline,
    *
    from {{ ref('stg_nytdata') }}
    where section_name <> 'Archives'
),
word_array as (
    select string_split_regex(processed_headline, '\s+') as words, 
    *
    from processed_headlines
    where processed_headline <> ''
)
select unnest(words).lower() as word,
    *
    from word_array
