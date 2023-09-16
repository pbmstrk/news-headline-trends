(ns nytdata.main
  (:gen-class)
  (:require [cheshire.core :refer [parse-string]]
            [clj-http.client :as client]
            [clojure.string :as str]
            [next.jdbc :as jdbc]
            [next.jdbc.sql :as sql]
            [nytdata.utils.date :as date-utils]
            [nytdata.utils.db :as db-utils]))

(def PARAMETERIZED-URL
  "https://api.nytimes.com/svc/archive/v1/%s/%s.json")
(def API-KEY
  (System/getenv "nyt_api_key"))

(defn construct-nyt-api-url
  "Create the URL for the http request based on a parameterized URL and year-month string."
  [url year-month]
  (let [[year month] (str/split year-month #"-")]
    (format url year month)))

(defn extract-docs-from-response
  "Extracts 'docs' key from the API response."
  [response]
  (-> response
      :body
      parse-string
      (get-in ["response" "docs"])))

(defn fetch-nyt-data-for-month
  "Fetches data from the NYT API for a given year and month."
  [year-month]
  (let [url (construct-nyt-api-url PARAMETERIZED-URL year-month)
        response (client/get url {:throw-exceptions false :accept :json :query-params {"api-key" API-KEY}})]
    (if (= 200 (:status response))
      (extract-docs-from-response response)
      (throw (Exception. (str "Failed to fetch data for " year-month ": " (:status response)))))))

(defn extract-metadata [doc]
  (let [uri (get doc "uri")
        headline  (get-in doc ["headline" "main"])
        year_month (date-utils/extract-year-month-from-timestamp (get doc "pub_date"))
        section-name (get doc "section_name")]
    [uri headline year_month section-name]))

(defn insert-headlines!
  [ds docs]
  (jdbc/execute-batch! ds (str "INSERT INTO headlines (uri, headline, year_month, section_name)"
                               "VALUES (?, ?, ?, ?)"
                               "ON CONFLICT DO NOTHING")
                       (map extract-metadata docs) {}))

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

