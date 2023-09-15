# News Headline Trends

[**news-headline-trends**](https://news-headline-trends.fly.dev) is a [Dash](https://dash.plotly.com) application that visualizes and analyzes data related to word occurences in New York Times headlines. 

The app consists of the two mains features:
1. **Word occurence visualisation**: View line graphs displaying the number of headlines containing the selected keywords over time.
2. **Headline sampling**: Headlines that contain a given keyword can be sampled by clicking on a trace in the graph.

## Setup and Usage

### Prerequisites

1. Sign up for an API key on the [New York Times Developer Network](https://developer.nytimes.com)
2. Create a Postgres database (locally or in the cloud)

> The Clojure code used to fetch data from the API requires two environment variables to be set: `nyt_api_key` and `database_url`.

### Load data

4. Create the tables in the database using the [setup.sql](sql-scripts/setup.sql) script. If you're using `psql` run:

```bash 
psql {db-connection-string} -f sql-scripts/setup.sql 
```

5. Run the Clojure script to load the data (the code can be run using either `clj` or Docker). Navigate to the `nytdata-clj` directory and run:

Using `clj`:

```bash 
clj -M -m nytdata.main
```

Using Docker:

```
docker build -t nytdata-clj .
docker run  --rm --env-file {env-file} nytdata-clj
```

### Run the app

6. Run the app by either running the Python script directly (`python app/app.py`) or building and running the Docker container.


> The app requires the `DATABASE_URL` environment variable to be set.
