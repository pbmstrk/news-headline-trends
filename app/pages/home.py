import os

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import (Input, Output, State, callback, dash_table, dcc, exceptions,
                  html, no_update)
from sqlalchemy import create_engine, text

dash.register_page(__name__, path="/")

# CONSTANTS
DEFAULT_KEYWORDS = ["japan", "afghanistan"]

# SQL QUERIES
SQL_CONTENT_QUERY = "select * from monthly_content_counts;"
SQL_UNIQUE_WORDS_QUERY = "select distinct word from word_headlines order by word;"
SQL_KEYWORD_QUERY = """
    select word, year_month, count(headline) as num_words
    from word_headlines
    where word in :wordlist
    group by year_month, word;
"""
SQL_HEADLINES_QUERY = """
    select headline from word_headlines
    where word = :keyword and year_month = :year_month;
"""

# INTRODUCTORY TEXT
WORD_COUNTS_TEXT = """
#### What is the NYT writing about?

Use the multi-select dropdown below to view the occurences of different words over the 
past 25 years. By clicking on a trace in the graph, headlines containing the given word 
during that timeperiod can be sampled.
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


def execute_query(engine, sql, **query_params):
    """Executes an SQL query and returns the result as a DataFrame."""
    query = text(sql).bindparams(**query_params)
    with engine.connect() as con:
        return pd.read_sql(query, con)

# Initialize DB and load data
db_url = fetch_database_url()
engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)

# Load and preprocess data
content_monthly = execute_query(engine, SQL_CONTENT_QUERY)
unique_words = execute_query(engine, SQL_UNIQUE_WORDS_QUERY)["word"].tolist()

total_volume = html.Div(
    [
        dbc.Button(
            id="collapse-button",
            className="mb-3",
            color="light",
            n_clicks=0
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([
                dmc.Checkbox(id="exclude-blog", label="Exclude blog content."),
                dcc.Graph(id="content-volume"),
            ])),
            id="collapse",
            is_open=False
        )
    ]
)

layout = html.Div(children=[
    dcc.Markdown(WORD_COUNTS_TEXT),
    dcc.Dropdown(
        unique_words,
        multi=True,
        id="word-dropdown",
        value=DEFAULT_KEYWORDS
    ),
    dcc.Graph(id="word-counts"),
    dcc.Markdown(id="table-intro"),
    dash_table.DataTable(
        [],
        id="example-headlines",
        style_cell={'textAlign': 'left'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        style_as_list_view=True,
        style_table={"margin-bottom": "20px"}),
    total_volume
])

@callback(
    Output("word-counts", "figure"), 
    Input("word-dropdown", "value")
)
def update_keyword_monthly(value):
    """Updates the keyword figure showing the monthly count of headlines containing each
    keyword. If no value is selected in the dropdown, it returns `dash.no_update` to 
    prevent updating the figure."""

    if not value:
        return no_update
    result_df = execute_query(engine, SQL_KEYWORD_QUERY, wordlist=tuple(value))
    dff = result_df.groupby("word").apply(
        lambda g: (
            g.set_index("year_month")
            .reindex(
                pd.date_range(
                    g["year_month"].min(), 
                    g["year_month"].max(), 
                    freq="M").strftime("%Y-%m")
                )
            .rename_axis("year_month")
            .fillna({"num_words": 0}))
    )[["num_words"]].reset_index()
    
    fig = px.line(
        dff,
        x="year_month",
        y="num_words",
        color="word",
        title="Number of headlines containing keyword",
        labels={
            "year_month": "Month", 
            "num_words": "Number of occurrences", 
            "word": "Word"
        },
        line_shape="spline",
        color_discrete_sequence=px.colors.qualitative.Bold,
        render_mode="svg")
    fig.update_traces(
        hovertemplate="<br>".join(["Month: %{x}", "Number of occurrences: %{y}"])
    )
    return fig


@callback(
    [Output("example-headlines", "data"), Output("table-intro", "children")],
    [Input("word-counts", "clickData")],
    [State("word-counts", "figure")]
)
def update_stories(clickData, figure):
    """Updates the table displaying example headlines and its introduction 
    based on click data."""

    if clickData is None:
        raise exceptions.PreventUpdate
    curve_number = clickData["points"][0]["curveNumber"]
    keyword = figure["data"][curve_number]["name"]
    x_axis_click = clickData["points"][0]["x"]
    result = execute_query(
        engine, SQL_HEADLINES_QUERY, keyword=keyword, year_month=x_axis_click[:-3]
    )
    sample = result.sample(min(5, result.shape[0]))

    text = f"Example headlines containing: **{keyword}**"
    return [sample.to_dict("records"), text]


@callback(
    [Output("collapse", "is_open"), Output("collapse-button", "children")],
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    """Toggles the open state of a collapsible element and updates its button text."""

    text = {True: "Hide total volume published", False: "See total volume published"}
    if n:
        return not is_open, text[(not is_open)]
    return is_open, text[is_open]

@callback(
    Output("content-volume", "figure"), 
    Input("exclude-blog", "checked")
)
def exclude_blog_checkbox(checked):
    """Updates line graph with the number of articles per month, based on whether
    the "exclude-blog" checkbox is checked."""

    # filter the DataFrame based on the checkbox value
    if checked:
        mask = content_monthly["section_name"] != "Blogs"
    else:
        mask = content_monthly["section_name"].notnull()
    dff = (
        content_monthly.loc[mask]
        .groupby("year_month", as_index=False)
        .agg(num_articles=("num_articles", "sum"))
    )

    fig = px.line(
        dff,
        x="year_month",
        y="num_articles",
        title="Number of articles",
        labels={"year_month": "Month", "num_articles": "Number of articles"},
    )

    fig.update_traces(
        hovertemplate="<br>".join(["Month: %{x}", "Number of articles: %{y}"]),
        line={"width": 2.5, "color": "#1B4D3E"},
    )

    fig.update_layout(margin={"l": 60, "r": 60, "t": 60, "b": 60}, hovermode="x")
    fig.update_yaxes(rangemode="tozero")
    return fig
