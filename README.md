# News Headline Trends

[**news-headline-trends**](https://news-headline-trends.vercel.app) visualizes data related to word occurences in New York Times headlines. 

The app consists of the two mains features:
1. **Word occurence visualisation**: View line graphs displaying the number of headlines containing the selected keywords over time.
2. **Headline sampling**: Headlines that contain a given keyword can be sampled by clicking on a trace in the graph.

## Local setup and usage

### Prerequisites

1. Sign up for an API key on the [New York Times Developer Network](https://developer.nytimes.com)

### Database setup

2. Create a PostgreSQL database.

3. Set up the required database objects (like tables, views, etc.) by running: 

```bash 
psql {db-connection-string} -f sql-scripts/setup.sql 
```

### Data loading

4. Navigate to the `nytdata-clj` directory.

5. Set the environment variables `nyt_api_key` and `jdbc_database_url` for the Clojure script.

6. Run the Clojure script to fetch and load data. You can use either `clj`:

```bash 
clj -M -m nytdata.main
```

Or Docker:

```bash
docker build -t nytdata-clj .
docker run  --rm --env-file {env-file} nytdata-clj
```

### API setup

7. Install the requirements using `pip install -r api/requirements.txt` (the use of a virtual environment is recommended). Then set the `DATABASE_URL` environment variable.

8. Start the API by running

```bash
uvicorn main:app
```

### Running the app

9. Navigate to the frontend directory and install the dependencies by running `npm install`.

10. Set the `VITE_API_URL` environment variable.

10. Launch the development server,

```bash
npm run dev
```