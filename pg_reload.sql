create table if not exists monthly_content_counts (
    year_month text,
    section_name text,
    num_articles integer not null check (num_articles >= 0),
    PRIMARY KEY (year_month, section_name)
);

create table if not exists word_headlines (
    word text not null,
    year_month text not null,
    headline text not null
);

truncate monthly_content_counts, word_headlines;

\copy monthly_content_counts from 'data/monthly_content_counts.csv' delimiter ',' csv
\copy word_headlines from 'data/word_headlines.csv' delimiter ',' csv