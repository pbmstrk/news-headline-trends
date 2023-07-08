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
to 2022. A simple tokenization was used to process the headlines: all non-letter
characters were removed, and the headlines were split on whitespace. 
While this approach introduces some level of noise, it does not obscure some
distinct patterns. For example, a surge in news coverage related to Japan can be 
observed during the Tōhoku earthquake and tsunami, as well as a notable increase in 
headlines concerning Afghanistan during the time of the US withdrawal."""

layout = dcc.Markdown(OVERVIEW)
