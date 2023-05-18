# clean up
rm nytdata.duckdb

source .venv/bin/activate
load-archive-data 1997 2023

duckdb nytdata.duckdb < sql/setup.sql
dbt run --project-dir sql/
duckdb nytdata.duckdb < sql/export.sql 