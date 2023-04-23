# NYTArchive

NYTArchive is a Python package for interacting with the New York Times Archive API. It allows you to easily load data from the archive and save it to local parquet files.

## Getting Started

### Installing 

Install the package locally using, 

```
pip install .
```

### Usage 

```
from nyt_archive import NYTArchive

nyt = NYTArchive(api_key=YOUR_API_KEY)
data = nyt.load_data(year=2022, month=1)
```