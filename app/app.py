import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from dash import Dash, Input, Output, callback, dash_table, dcc, exceptions, html
from dash_bootstrap_templates import load_figure_template


def load_data(parquet_file, dir_path="assets/"):
    """Load data from a parquet file located in a directory and
    return it as a pandas DataFrame."""
    return pd.read_parquet(dir_path + parquet_file)


def convert_to_datetime(df, col_name, format):
    """Converts a column in a Pandas DataFrame to datetime object."""
    df[col_name] = pd.to_datetime(df[col_name], format=format, utc=True).dt.date
    return df


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "News Trends: NYT"
server = app.server
load_figure_template("BOOTSTRAP")

# data
content_monthly = load_data("monthly_content_counts.parquet")
content_monthly = convert_to_datetime(content_monthly, "year_month", "%Y-%m")

dt_distribution = load_data("dt_distribution.parquet")

mm_yearly = load_data("yearly_multimedia_proportion.parquet")
mm_yearly = convert_to_datetime(mm_yearly, "yr", "%Y")

mm_prop_sec = load_data("multimedia_proportion_section.parquet").iloc[:10, :]

dt_counts_by_sec_yearly = load_data("yearly_dt_sn_counts.parquet")
dt_counts_by_sec_yearly = convert_to_datetime(
    dt_counts_by_sec_yearly, "yr", "%Y"
).sort_values(by="yr")

section_monthly = load_data("monthly_section_counts.parquet")
section_monthly = convert_to_datetime(section_monthly, "year_month", "%Y-%m")


def blank_fig():
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)

    return fig


def multimedia_growth():
    fig = px.line(
        mm_yearly,
        x="yr",
        y="proportion",
        line_shape="spline",
        title="Growth of multimedia content",
        labels={"yr": "Year", "proportion": "Proportion of multimedia content"},
    )
    fig.update_traces(hovertemplate="<br>".join(["Year: %{x}", "Proportion: %{y}"]))
    fig.update_layout(margin=dict(l=60, r=60, t=60, b=60), hovermode="x")
    fig.update_yaxes(rangemode="tozero")
    return fig


def volume_section():
    dff = section_monthly.groupby("section_name", as_index=False).agg(
        num_articles=("num_articles", "sum")
    )

    fig = px.bar(
        dff,
        x="section_name",
        y="num_articles",
        title="Total volume per section",
        labels={"section_name": "Section Name", "num_articles": "Number of articles"},
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    fig.update_layout(margin=dict(l=60, r=60, t=60, b=60))
    return fig


app.layout = dbc.Container(
    html.Div(
        children=[
            html.H1(
                children="Historical News Trends: New York Times",
                style={"textAlign": "left", "font-weight": "bold"},
            ),
            html.Hr(),
            html.H2(
                children="Investigating historical article metadata and trends.",
                style={"textAlign": "left"},
            ),
            html.H3(children="Data overview", style={"textAlign": "left"}),
            dcc.Markdown(
                """
        The [Archive API](https://developer.nytimes.com/docs/archive-product/1/overview), 
        available through [New York Times Developer Network](https://developer.nytimes.com), 
        enables users to access  metadata for all articles published by the NYT, 
        going back to 1851. This API returns a multitude of metadata fields related to a given 
        article, which can be used to analyze how the newspaper's news coverage has evolved 
        over time. 
        A couple fields returned by the API are explained in more detail below. 
        For the full documentation, view the complete
        [article schema](https://developer.nytimes.com/docs/archive-product/1/types/Article).

        - `section_name`: The section of the newspaper that the article 
        appeared in (e.g. New York, Sports, World, ...). The section can also be seen in the URL
        of an article. In general URLs follow the following pattern:
        `https://www.nytimes.com/[year]/[month]/[day]/[section]`.
        - `document_type`: The type of content. This field only has four 
        different values: `article`, `multimedia`, `audio` and `audiocontainer`.

        These fields or dimensions can be analyzed to detect trends or pattern in the coverage
        of the NYT. The data time-period spans 1997 (the year after NYT launched a 
        [website](https://www.nytimes.com/1996/01/22/business/the-new-york-times-introduces-a-web-site.html))
        to 2022."""
            ),
            html.H3(children="Content volume", style={"textAlign": "left"}),
            dcc.Markdown(
                """
        The chart below illustrates the volume of content published by the NYT on a monthly 
        basis over the past 25 years. Two distinct spikes in volume are noticeable:
        - In 2006, there was a noticeable increase in content published across various 
        sections (such as Business Day, New York, and Opinion). These spikes are 
        apparent when examining the volume of each individual sections.
        - In 2009, there was a significant spike in volume that was largely driven by an 
        increase in blog content. This spike disappears when blog content is excluded.

        To view the chart excluding blog content, click the checkbox below."""
            ),
            dmc.Checkbox(id="exclude-blog", label="Exclude blog content."),
            dcc.Graph(figure={}, id="content-volume"),
            html.H3("Content Type"),
            dcc.Markdown(
                """
        As mentioned earlier, The New York Times classifies the published 
        documents into four categories:  `article`, `multimedia`, `audio` and `audiocontainer`.
        Of these four, articles make up the vast majority of content."""
            ),
            dash_table.DataTable(
                dt_distribution.rename(
                    columns={"document_type": "Document Type", "num_articles": "Volume"}
                ).to_dict("records"),
                style_table={"margin-bottom": "20px"},
            ),
            dcc.Markdown(
                """
        During the last two decades, the percentage of alternative content types, like videos 
        and slideshows, has increased to approximately 10% of the total content published."""
            ),
            dcc.Graph(figure=multimedia_growth()),
            dcc.Markdown(
                """ 
        Some sections have experienced a more significant growth rate than others. For 
        instance, Fashion & Style and Real Estate are particularly suitable for displaying 
        alternative content formats, such as slideshows. To explore the multimedia content 
        proportion for each section, choose the desired section name from the dropdown 
        menu below."""
            ),
            dcc.Dropdown(
                mm_prop_sec["section_name"].tolist(),
                mm_prop_sec["section_name"].tolist()[0],
                id="section-dropdown",
            ),
            dcc.Graph(figure={}, id="section-multimedia"),
            html.H3("Section Name"),
            dcc.Markdown(
                """
        The volume of content not only varies by document type but also section. The following 
        chart displays the amount of content published in each section and the yearly counts."""
            ),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(figure=volume_section(), id="section-bar-chart")),
                    dbc.Col(dcc.Graph(figure=blank_fig(), id="section-growth")),
                ]
            ),
        ],
        style={"margin-top": "15px"},
    )
)


@callback(Output("content-volume", "figure"), Input("exclude-blog", "checked"))
def exclude_dead_checkbox(checked):
    if checked:
        mask = content_monthly["section_name"] != "Blogs"
        dff = content_monthly[mask].copy()
    else:
        dff = content_monthly
    dff = dff.groupby("year_month", as_index=False).agg(
        num_articles=("num_articles", "sum")
    )

    fig = px.line(
        dff,
        x="year_month",
        y="num_articles",
        title="Number of articles",
        labels={"year_month": "Month", "num_articles": "Number of articles"},
        line_shape="spline",
    )
    fig.update_traces(
        hovertemplate="<br>".join(["Month: %{x}", "Number of articles: %{y}"])
    )
    fig.update_layout(margin=dict(l=60, r=60, t=60, b=60), hovermode="x")
    fig.update_yaxes(rangemode="tozero")
    return fig


@callback(Output("section-multimedia", "figure"), Input("section-dropdown", "value"))
def section_multimedia(value):
    dff = dt_counts_by_sec_yearly[dt_counts_by_sec_yearly["section_name"] == value]
    fig = px.bar(
        dff,
        x="yr",
        y="num_articles",
        color="document_type",
        labels={
            "yr": "Year",
            "num_articles": "Volume",
            "document_type": "Document Type",
        },
    )
    fig.update_traces(hovertemplate="<br>".join(["Year: %{x}", "Volume: %{y}"]))
    fig.update_layout(margin=dict(l=60, r=60, t=60, b=60), hovermode="x")
    return fig


@callback(Output("section-growth", "figure"), Input("section-bar-chart", "clickData"))
def update_on_click(clickData):
    if not clickData:
        raise exceptions.PreventUpdate
    section = clickData["points"][0]["x"]
    dff = section_monthly[section_monthly["section_name"] == section].sort_values(
        "year_month"
    )
    fig = px.line(
        dff,
        x="year_month",
        y="num_articles",
        title=f"Number of articles: {section}",
        labels={"year_month": "Month", "num_articles": "Number of articles"},
        line_shape="spline",
    )
    fig.update_traces(
        hovertemplate="<br>".join(["Month: %{x}", "Number of articles: %{y}"])
    )
    fig.update_layout(margin=dict(l=60, r=60, t=60, b=60), hovermode="x")
    fig.update_yaxes(rangemode="tozero")
    return fig


@callback(
    Output("section-bar-chart", "figure"), Input("section-bar-chart", "clickData")
)
def highlight_bar(clickData):
    if not clickData:
        raise exceptions.PreventUpdate
    section = clickData["points"][0]["x"]
    fig = volume_section()
    fig["data"][0]["marker"]["color"] = [
        "red" if c == section else "#5769fe" for c in fig["data"][0]["x"]
    ]
    return fig


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port="8050")
