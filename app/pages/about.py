import dash
from dash import dcc

dash.register_page(__name__)

OVERVIEW = """
#### API Introduction

The [Archive API](https://developer.nytimes.com/docs/archive-product/1/overview), 
available through [New York Times Developer Network](https://developer.nytimes.com), 
enables users to access  metadata for articles published by the NYT, 
going back to 1851. The API returns metadata fields related to a given 
article, which can be used to analyze how the newspaper's news coverage has evolved 
over time. For the full documentation, view the
[article schema](https://developer.nytimes.com/docs/archive-product/1/types/Article).

To use the API follow the [getting started guide](https://developer.nytimes.com/get-started).

#### Data and process overview

The data contains headlines from 1997 (the year after NYT launched a 
[website](https://www.nytimes.com/1996/01/22/business/the-new-york-times-introduces-a-web-site.html))
to 2022. Matching headlines for a search term are found using the
[full text feature](https://www.postgresql.org/docs/current/textsearch.html) in
PostgreSQL. While this approach may introduce some level of noise, it does not obscure
distinct patterns. For example, a surge in news coverage related to Japan can be
observed during the Tōhoku earthquake and tsunami, as well as a notable increase in 
headlines concerning Afghanistan throughout the US troop withdrawal."""

layout = dcc.Markdown(OVERVIEW)
