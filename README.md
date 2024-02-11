# News Headline Trends

[**news-headline-trends**](https://news-headline-trends.vercel.app) visualizes data related to word occurences in New York Times headlines. 

The app consists of the two mains features:
1. **Word occurence visualisation**: Interactive line graphs show the frequency of selected keywords in NYT headlines, which can be used to identify trends and patterns over different time periods.
2. **Headline sampling**: Headlines that contain a given keyword can be sampled by clicking on a trace in the graph.

**Technology stack**: PostgreSQL, Redis, React, Docker

## Setup

### Prerequisites


- Docker Compose: [Installation Guide](https://docs.docker.com/compose/install/)
- New York Times API Key: [Sign Up Here](https://developer.nytimes.com)


### Local setup

1. **Environment Setup**:

Create a `.env` file in the project root with the following variables:

- `POSTGRES_USER`: name of the user to connect to PostgreSQL database
- `POSTGRES_PASSWORD`: password for user
- `NYT_API_KEY`: API key obtained from the NYT Developer Network 

An example file,

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
NYT_API_KEY=newyorktimesapikey # replace with your API key
```

2. **Build and run containers:**

Execute the following command to build and run the application:

```bash
docker-compose up --build
```

3. **Data Loading:**

Use the [`run-nytdata-load.sh`](run-nytdata-load.sh) script to load NYT headlines into the database:

```bash
./run-nytdata-load.sh
```

After completing the setup, the application will be available at `http://localhost:80`.

## How is it deployed?

- Database: [Cockroach DB](https://www.cockroachlabs.com)
- React app: [Vercel](https://vercel.com)
- Redis: [Upstash](https://upstash.com)
- FastAPI: [Fly.io](https://fly.io)
- Data loading: [Cloud Run](https://cloud.google.com/run)


