import os
import io
import pandas as pd
from sqlalchemy import create_engine, text, Connection, Engine
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import redis


r = redis.Redis.from_url(
    os.getenv("REDIS_URL")
)


# Constants
ORIGINS = [
    "http://localhost:5173",
    "https://news-headline-trends.vercel.app"
]
SQL_HEADLINES_QUERY = """
    select 
        headline, web_url,
        to_char(cast(pub_date as timestamp), 'yyyy-mm-dd') as pub_date
    from headlines
    where textsearchable_index_col @@ to_tsquery('simple', :keyword) and year_month = :year_month;
"""
SQL_FULL_TEXT_SEARCH = """
    select year_month, count(headline) as num_headlines
    from headlines
    where textsearchable_index_col @@ to_tsquery('simple', :word)
    group by year_month;
"""


class MissingEnvVar(Exception):
    pass


def fetch_database_url():
    """Fetches the database URL from the DATABASE_URL environment variable.
    If the URL starts with 'postgres://', it replaces this with 'postgresql://'."""
    database_url = os.getenv("DATABASE_URL")
    if database_url is None:
        raise MissingEnvVar("DATABASE_URL environment variable does not exist.")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://",  "postgresql://", 1)
    return database_url


def execute_query(connection, sql, **query_params):
    """Executes an SQL query and returns the result as a DataFrame."""
    query = text(sql).bindparams(**query_params)
    return pd.read_sql(query, connection)
    
def create_db_engine() -> Engine:
    db_url = fetch_database_url()
    return create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=[],
)


engine = create_db_engine()

def get_connection():
    with engine.connect() as connection:
        yield connection

@app.get("/samples")
@limiter.limit("300/minute")
def get_sample(request: Request, year_month: str, keyword: str, connection: Connection = Depends(get_connection)):
    """Retrieve a sample of headlines from the database based on a given year-month and keyword.

    The function searches the headlines database for records that match the specified `year_month` 
    and contain the `keyword`. It then randomly selects a sample of the results, with a maximum 
    of 5 records. If there are fewer than 5 records, it returns all of them."""
    result = execute_query(
        connection, SQL_HEADLINES_QUERY, keyword=keyword, year_month=year_month
    )
    sample = result.sample(min(5, result.shape[0]))

    return sample.to_dict("records")

def query_occurrences(keyword: str, connection: Connection) -> pd.DataFrame:
    """Query occurrences for a given keyword and add keyword as a column."""

    cache_key = f"occurrences:{keyword}"
    cached_result = r.get(cache_key)
    if cached_result:
        decoded_result = cached_result.decode('utf-8') 
        result = pd.read_json(io.StringIO(decoded_result), orient='split')
    else:
        result = execute_query(connection, SQL_FULL_TEXT_SEARCH, word=keyword)
        r.set(cache_key, result.to_json(orient='split'), ex=60*60)
    return (result, keyword)

def fill_missing_months(df: pd.DataFrame, date_range: list[str]) -> pd.DataFrame:
    """Fill missing months in a DataFrame with zero."""
    return (
        df.set_index('year_month')
        .reindex(date_range, fill_value=0)
        .rename_axis("year_month")
        .reset_index()
    )


@app.get("/occurrences")
@limiter.limit("300/minute")
def get_occurences(request: Request, keywords: str, connection: Connection = Depends(get_connection)):
    tags = keywords.split(",")
    df_list = [query_occurrences(tag, connection) for tag in tags]
    result_df = pd.concat([df[0] for df in df_list])

    # Create a full date range for the combined result
    full_date_range = pd.date_range(
        start=result_df["year_month"].min(),
        end=result_df["year_month"].max(),
        freq="MS"
    ).strftime("%Y-%m")

    # Fill missing months for each word
    filled_dfs = [(fill_missing_months(df, full_date_range), keyword) for (df, keyword) in df_list]

    # Transform data for the response
    result = []
    for df, keyword in filled_dfs:
        data = []
        for date, count in zip(df["year_month"], df["num_headlines"]):
            data.append({"x": date, "y": count})
        result.append({"id": keyword, "data": data})

    return result