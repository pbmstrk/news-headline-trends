# NYT-Trends

**nyt-trends** is a [Dash](https://dash.plotly.com) application that visualizes and analyzes data related to word occurences in New York Times headlines. 

The app consists of the two mains features:
1. **Word occurence visualisation**: View line graphs displaying the number of headlines containing the selected keywords over time.
2. **Headline sampling**: Headline that contain a given keyword can be sampled by clicking on a trace in the graph.

## Setup and Usage

To set up the app following these setups:

1. Install [`duckdb`](https://duckdb.org/#quickinstall). On MacOS the `duckdb` executable can be installed using Homebrew:
`brew install duckdb`

2. Install the `nytarchive` package by running 

```
cd nytarchive
pip install --editable .
```

3. Run the `setup.sh` script. This script  pulls the necessary data from the NYT API, performs data transformation, and exports the data for the app to use.

4. Install the app prerequisties by running, 
`pip install -r app/requirements.txt` 

5. Run the application  by running the Python script (`python app/app.py`) or by building and running the Docker container.

