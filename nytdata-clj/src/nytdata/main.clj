(ns nytdata.main
  (:gen-class)
  (:require [clj-http.client :as client]
            [clojure.string :as str]
            [next.jdbc :as jdbc]
            [next.jdbc.sql :as sql]
            [nytdata.utils.date :as date-utils]
            [nytdata.utils.db :as db-utils]))

(def parameterized-url
  "https://api.nytimes.com/svc/archive/v1/%s/%s.json")
(def api-key
  (System/getenv "nyt_api_key"))

(defn construct-nyt-api-url
  "Create the URL for the http request based on a parameterized URL and year-month string."
  [url year-month]
  (let [[year month] (str/split year-month #"-")]
    (format url year month)))

(defn extract-articles-from-response
  "Extracts articles from the API response."
  [response]
  (get-in response [:body :response :docs]))

(defn fetch-nyt-data-for-month
  "Fetches data from the NYT API for a given year and month."
  [year-month]
  (let [url (construct-nyt-api-url parameterized-url year-month)
        response (client/get url {:throw-exceptions false :as :json :query-params {"api-key" api-key}})]
    (if (= 200 (:status response))
      (extract-articles-from-response response)
      (throw (Exception. (str "Failed to fetch data for " year-month ": " (:status response)))))))

(defn extract-metadata [doc]
  ((juxt :uri
         (comp :main :headline)
         (comp (partial date-utils/extract-year-month-from-timestamp) :pub_date)
         :section_name)
   doc))

(defn insert-headlines!
  [ds docs]
  (let [query "INSERT INTO headlines (uri, headline, year_month, section_name) VALUES (?, ?, ?, ?) ON CONFLICT DO NOTHING"]
    (jdbc/execute-batch! ds query (map extract-metadata docs) {})))

(defn process-month [ds ym]
  (println (str "Fetching data for month: " ym))
  (let [docs (fetch-nyt-data-for-month ym)
        num-docs (count docs)]
    (println (str "\tNumber of records: " num-docs))
    (insert-headlines! ds docs)
    (sql/insert! ds :process_log {:year_month ym :num num-docs})))

(defn -main []
  (let [ds (db-utils/get-datasource-from-env)
        latest-ym (db-utils/get-latest-processed-month ds)
        ym-seq (date-utils/year-month-sequence latest-ym)]
    (println (str "Processing months: " ym-seq))
    (doseq [ym ym-seq]
      (process-month ds ym)
      (Thread/sleep 12000))
    (when (seq ym-seq)
      (println "Refreshing materialized views")
      (jdbc/execute! ds ["refresh materialized view monthly_content_counts_vw"])
      (jdbc/execute! ds ["refresh materialized view word_headlines_vw"]))))

