CREATE TABLE IF NOT EXISTS headlines (
  uri text NOT NULL,
  headline text NOT NULL,
  pub_date text NOT NULL,
  web_url text NOT NULL,
  section_name text NOT NULL,
  textsearchable_index_col tsvector GENERATED ALWAYS AS (
    to_tsvector('simple', lower(headline))
  ) STORED,
  year_month text GENERATED ALWAYS AS (
    substring(pub_date, 1, 7)
  ) STORED,
  PRIMARY KEY (uri)
);

CREATE INDEX textsearch_idx ON headlines USING gin (textsearchable_index_col);

CREATE TABLE IF NOT EXISTS process_log (
  year_month text UNIQUE NOT NULL,
  num integer NOT NULL CHECK (num > 0)
);