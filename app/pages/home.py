import os

import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
from dash import (Input, Output, State, callback, dash_table, dcc, exceptions,
                  html, no_update)
from sqlalchemy import create_engine, text
import dash_cool_components

dash.register_page(__name__, path="/")

# CONSTANTS
DEFAULT_KEYWORDS = ["japan", "afghanistan"]

# SQL QUERIES
SQL_CONTENT_QUERY = "select * from monthly_content_counts_vw;"
SQL_HEADLINES_QUERY = """
    select headline from headlines
    where textsearchable_index_col @@ to_tsquery('simple', :keyword) and year_month = :year_month;
"""
SQL_FULL_TEXT_SEARCH = """
    select year_month, count(headline) as num_headlines
    from headlines
    where textsearchable_index_col @@ to_tsquery('simple', :word)
    group by year_month;
"""

# INTRODUCTORY TEXT
WORD_COUNTS_TEXT = """
#### What is the NYT writing about?

Use the input box below to view the occurences of different words over the 
past 25 years. By clicking on a trace in the graph, headlines containing the given word
during that timeperiod can be sampled.

*Note: Sample search terms have been pre-loaded, adding terms to the input box will reset these.
Any multi-word search terms will be ignored.*
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
    dash_cool_components.TagInput(
        id="word-tags",
        wrapperStyle={
            'position':'relative',
            'padding': '0px',
            'transform':'translate(0,0)',
            'left': 0,
            'box-sizing': 'border-box',
            'background-color': '#fff',
            'border-color': '#d9d9d9',
            'box-shadow': 'none',
        },
        inputStyle={
            'background-color': '#fff',
            'border': '1px solid #ccc'
        },
        placeholder="Enter search terms..",
        tagStyle={
            'display': 'inline-block',
            'font-family': 'Roboto,Arial,sans-serif',
            'background-color': 'rgba(0,126,255,.08)',
            'color': '#007eff',
            'border-bottom-right-radius': '2px',
            'border-top-right-radius': '2px',
            'font-size': '1rem',
            'padding': '2px 5px'
        },
        tagDeleteStyle = {
            'color': '#007eff'
        },
        value=[{"index": 0, "displayValue": "trump"}, {"index": 1, "displayValue": "obama"}]
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
    Output("word-tags", "value"),
    Input("word-tags", "value")
)
def update_tags(value):
    return [tag for tag in value if len(tag["displayValue"].split(" ")) == 1]


@callback(
    Output("word-counts", "figure"), 
    Input("word-tags", "value")
)
def update_keyword_monthly(value):
    """Updates the keyword figure showing the monthly count of headlines containing each
    keyword. If no value is selected in the dropdown, it returns `dash.no_update` to 
    prevent updating the figure."""

    if not value:
        return no_update

    tags = [e['displayValue'] for e in value]

    df_list = []
    for word in tags:
        if len(word.split(" ")) > 1:
            continue
        result = execute_query(engine, SQL_FULL_TEXT_SEARCH, word=word)
        result['word'] = word
        df_list.append(result)
    result_df = pd.concat(df_list)

    if result_df.empty:
        raise exceptions.PreventUpdate("No matching headlines found!")

    full_date_range = pd.date_range(
        start=result_df["year_month"].min(),
        end=result_df["year_month"].max(),
        freq="MS"
    ).strftime("%Y-%m")

    dff = result_df.set_index("year_month").groupby("word").apply(
        lambda g: (
            g.reindex(full_date_range, fill_value=0)
            .rename_axis("year_month"))
    )[["num_headlines"]].reset_index()
    
    fig = px.line(
        dff,
        x="year_month",
        y="num_headlines",
        color="word",
        title="Number of headlines containing keyword",
        labels={
            "year_month": "Month", 
            "num_headlines": "Number of headlines",
            "word": "Word"
        },
        line_shape="spline",
        color_discrete_sequence=px.colors.qualitative.Bold,
        category_orders={"word": tags},
        render_mode="svg")
    fig.update_traces(
        hovertemplate="<br>".join(["Month: %{x|%B %Y}", "Number of occurrences: %{y}"])
    )
    fig.update_yaxes(rangemode="tozero")
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
        hovertemplate="<br>".join(["Month: %{x|%B %Y}", "Number of articles: %{y}"]),
        line={"width": 2.5, "color": "#1B4D3E"},
    )

    fig.update_layout(margin={"l": 60, "r": 60, "t": 60, "b": 60}, hovermode="x")
    fig.update_yaxes(rangemode="tozero")
    return fig
