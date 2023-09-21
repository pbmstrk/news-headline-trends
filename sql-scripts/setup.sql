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

CREATE MATERIALIZED VIEW monthly_content_counts_vw AS (
  SELECT
    year_month,
    section_name,
    count(*) AS num_articles
  FROM headlines
  GROUP BY year_month, section_name
);

CREATE TABLE IF NOT EXISTS process_log (
  year_month text UNIQUE NOT NULL,
  num integer NOT NULL CHECK (num > 0)
);

CREATE OR REPLACE FUNCTION convert_to_hyperlink(label text, destination text)
RETURNS text AS $$
BEGIN
    RETURN '<a href="' || destination || '" target="_blank">' || label || '</a>';
END;
$$ LANGUAGE plpgsql;