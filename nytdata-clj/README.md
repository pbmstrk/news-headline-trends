# nytdata-clj 

Fetch articles from NYT and load into Postgres database. 

## Usage

<details>
  <summary>Required environment variables</summary>

- `jdbc_database_url`: URL of Postgres database
- `nyt_api_key`: API key obtained from the NYT Developer Network 
</details>

<br>

The `-main` function in `nytdata.main` fetches any new articles from the endpoint. The following logic is used to determine the first month: If a custom start date is configured (using the `-s` flag), fetch articles from that date onwards. Otherwise, check whether any articles exist in the database and start from the most recent unprocessed month. The default is `1997-01`.


The script can be run either using `clj` or docker.

**Examples**:

Using `clj`:

```bash 
# load any new articles or all articles from 1997-01 onwards.
clj -M -m nytdata.main 
```

```bash 
# load articles from 2023-01 onwards.
clj -M -m nytdata.main -s 2023-01
```

Using docker:

```bash
docker build -t nytdata-load .
docker run --env-file {ENV_FILE} nytdata-load
```

> [!NOTE]
> Ensure that the appropriate objects have been created in the database before running the script. See [setup.sql](../sql-scripts/setup.sql) for details.





## Validating the response from NYT endpoint 

Specs describing the response object from the NYT endpoint are defined in the [`nytdata.spec`](src/nytdata/spec.clj) namespace. These specs can be used to generate or validate a response. 

To generate:

```clojure
(require '[clojure.spec.gen.alpha :as gen])

; generate a dummy response object based on the spec definitions.
(gen/generate (s/gen ::response-map))
```

To validate:
```clojure
(require '[clojure.spec.test.alpha :as stest])

; validate that the response from endpoint is valid according to the spec definitions.
(s/valid? ::response-map (fetch-nyt-data-for-month "2021-10" api-key))

; check the extract function
(stest/check `extract-articles-from-response {:clojure.spec.test.check/opts  {:num-tests 1}})
```