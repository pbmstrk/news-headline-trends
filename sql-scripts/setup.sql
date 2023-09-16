create table if not exists monthly_content_counts (
    year_month text,
    section_name text,
    num_articles integer not null check (num_articles >= 0),
    PRIMARY KEY (year_month, section_name)
);

create table if not exists word_headlines (
    uri text not null,
    word_index integer not null,
    word text not null,
    year_month text not null,
    headline text not null,
    PRIMARY KEY (uri, word_index)
);

create table if not exists process_log (
    year_month text unique not null,
    num integer not null check (num > 0)
);