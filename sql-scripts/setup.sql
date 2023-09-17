create table if not exists headlines (
    uri text not null,
    headline text not null,
    year_month text not null,
    section_name text not null,
    textsearchable_index_col tsvector generated always as (to_tsvector('simple', lower(headline))) stored,
    PRIMARY KEY (uri)
);

create index textsearch_idx on headlines using GIN (textsearchable_index_col);

create materialized view monthly_content_counts_vw as (
    select year_month, section_name, count(*) as num_articles
    from headlines
    group by year_month, section_name
);

create table if not exists process_log (
    year_month text unique not null,
    num integer not null check (num > 0)
);