import dash
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import (Input, Output, State, callback, dash_table, dcc,
                  exceptions, html, no_update)
import plotly.express as px
import pandas as pd
import duckdb

dash.register_page(__name__, path="/")

# Data loading and conversion functions
def load_data(parquet_file, dir_path="data/"):
    """Load data from a parquet file located in a directory and
    return it as a pandas DataFrame."""
    return pd.read_parquet(dir_path + parquet_file)

def convert_to_datetime(df, col_name, date_time_format):
    """Converts a column in a Pandas DataFrame to datetime object."""
    df[col_name] = pd.to_datetime(df[col_name], format=date_time_format, utc=True).dt.date
    return df

# Load and preprocess data
content_monthly = load_data("monthly_content_counts.parquet")
content_monthly = convert_to_datetime(content_monthly, "year_month", "%Y-%m")

unique_words = duckdb.sql(
    "select distinct word from 'data/word_headlines.parquet' order by 1"
).df()["word"].tolist()

WORD_COUNTS_TEXT = """
#### What is the NYT writing about?

Use the multi-select dropdown below to view the occurences of different words over the 
past 25 years. By clicking on a trace in the graph, headlines containing the given word 
during that timeperiod can be sampled.
"""

def process_str_for_sql(val):
    return f"'{val}'"


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
        value=["japan", "afghanistan"]
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

@callback(Output("word-counts", "figure"), Input("word-dropdown", "value"))
def update_keyword_monthly(value):
    if not value:
        return no_update
    qry = f"""
    select word, year_month, count(headline) as num_words
    from 'data/word_headlines.parquet'
    where word in ({','.join(map(process_str_for_sql, value))})
    group by year_month, word
    """
    result_df = duckdb.sql(qry).df()
    dff = convert_to_datetime(result_df, "year_month", "%Y-%m").sort_values("year_month")
   
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


@callback([Output("example-headlines", "data"),
Output("table-intro", "children")],
[Input("word-counts", "clickData")],
[State("word-counts", "figure")])
def update_stories(clickData, figure):
    """Update the displayed stories and table introduction based on click data."""
    if clickData is None:
        raise exceptions.PreventUpdate
    curve_number = clickData["points"][0]["curveNumber"]
    keyword = figure["data"][curve_number]["name"]
    x_axis_click = clickData["points"][0]["x"]
    qry = f"""select * from (select  headline from 'data/word_headlines.parquet'
    where word = {process_str_for_sql(keyword)} 
    and year_month = {process_str_for_sql(x_axis_click[:-3])})
    using sample 5"""
    sample = duckdb.sql(qry).df()

    text = f"Example headlines containing: **{keyword}**"
    return [sample.to_dict("records"), text]


@callback(
    [Output("collapse", "is_open"), Output("collapse-button", "children")],
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    text = {True: "Hide total volume published", False: "See total volume published"}
    if n:
        return not is_open, text[(not is_open)]
    return is_open, text[is_open]

@callback(Output("content-volume", "figure"), Input("exclude-blog", "checked"))
def exclude_blog_checkbox(checked):
    """Update line graph with the number of articles per month, based on whether
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
