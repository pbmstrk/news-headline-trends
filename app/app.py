import dash
import dash_bootstrap_components as dbc
from dash import Dash, html
from dash_bootstrap_templates import load_figure_template

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    use_pages=True,
)

app.title = "News Trends: NYT"
server = app.server
load_figure_template("BOOTSTRAP")

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(
            dbc.NavLink("About", href=dash.page_registry["pages.about"]["path"])
        ),
    ],
    brand="NYT: News Trends",
    brand_href=dash.page_registry["pages.home"]["path"],
    brand_style={"font-size": "1.75rem"},
    color="light",
    class_name="title",
)

footer = html.Footer(
    [
        html.Div(
            html.A(
                children=[html.Img(src="assets/poweredby_nytimes_150a.png")],
                href="https://developer.nytimes.com",
                target="_blank",
            ),
            style={"text-align": "left"},
        ),
        html.Div(
            html.A(
                children=[html.I(className="fa-brands fa-github icon"), "pbmstrk"],
                href="https://github.com/pbmstrk/nytdata",
                className="footer-link",
                target="_blank",
            ),
            style={"text-align": "right"},
        ),
    ],
    className="footer",
)

app.layout = html.Div(
    children=[
        navbar,
        dbc.Container(children=[dash.page_container, footer], className="container"),
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port="8050")
