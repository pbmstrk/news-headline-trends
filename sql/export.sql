copy monthly_content_counts to 'data/monthly_content_counts.parquet' (CODEC 'GZIP');
copy word_headlines to 'data/word_headlines.parquet';

copy monthly_content_counts to 'data/monthly_content_counts.csv';
copy word_headlines to 'data/word_headlines.csv';