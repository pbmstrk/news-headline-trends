create table if not exists headlines (
    uri text not null,
    headline text not null,
    year_month text not null,
    section_name text not null,
    PRIMARY KEY (uri)
);

create table if not exists allowed_words (
    allowed_word text not null
);

\copy allowed_words from 'allowed_words.csv' WITH DELIMITER ',' CSV HEADER;

create materialized view monthly_content_counts_vw as (
    select year_month, section_name, count(*) as num_articles
    from headlines
    group by year_month, section_name
);


create materialized view word_headlines_vw as (
    with processed_headlines as (
        select 
            lower(trim(regexp_replace(headline, '[\d\W_]', ' ', 'g'))) as processed_headline,
            *
        from headlines
        where section_name <> 'Archives'
    ),
    word_array as (
        select 
            regexp_split_to_array(processed_headline, '\s+') as words,
            *
        from processed_headlines
        where processed_headline <> ''
    ),
    unnested_table as (
        select 
            unnest(words) as word,
            *
        from word_array
    )
    select 
        word,
        year_month,
        headline
        from unnested_table
        where exists (select 1 from allowed_words where allowed_word = word)
);

create table if not exists process_log (
    year_month text unique not null,
    num integer not null check (num > 0)
);