
drop schema if exists raw_data cascade;
create schema if not exists raw_data;

create table if not exists raw_data.nytdata as (
    select headline.main as headline,
    pub_date,
    document_type,
    news_desk, 
    type_of_material,
    word_count, 
    web_url, 
    source,
    section_name,
    filename
    from read_parquet('.data/*.parquet', union_by_name=true, filename=true)
);

create table if not exists raw_data.allow_words as (
    select allow_word from read_csv_auto('allow_words.csv', header=true)
);