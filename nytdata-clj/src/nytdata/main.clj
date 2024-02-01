(ns nytdata.main
  (:gen-class)
  (:require [clj-http.client :as client]
            [clojure.string :as str]
            [clojure.tools.cli :as cli]
            [next.jdbc :as jdbc]
            [next.jdbc.sql :as sql]
            [nytdata.utils.date :as date-utils]
            [nytdata.utils.db :as db-utils]
            [taoensso.timbre :as log]))

(defn construct-nyt-api-url
  "Create the URL for the http request based on year-month string."
  [year-month]
  (assert (some? year-month))
  (let [[year month] (str/split (date-utils/padded-month->month year-month) #"-")]
    (format "https://api.nytimes.com/svc/archive/v1/%s/%s.json" year month)))

(defn fetch-nyt-data-for-month
  "Fetches data from the NYT API for a given year and month."
  [year-month api-key]
  (let [url (construct-nyt-api-url year-month)
        response (client/get url {:throw-exceptions false :as :json :query-params {:api-key api-key}})]
    (if (= 200 (:status response))
      response
      (throw (Exception. (str "Failed to fetch data for " year-month ": " (:status response)))))))

(defn extract-articles-from-response
  "Extracts articles from the API response."
  [response]
  (get-in response [:body :response :docs]))

(defn extract-metadata [doc]
  ((juxt :uri
         (comp :main :headline)
         :pub_date
         :web_url
         :section_name)
   doc))

(defn insert-headlines!
  [ds docs]
  (let [query "INSERT INTO headlines (uri, headline, pub_date, web_url, section_name) VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING"]
    (jdbc/execute-batch! ds query (map extract-metadata docs) {})))

(defn process-month [ds ym api-key]
  (log/info "Fetching data for month: " ym)
  (let [docs (-> (fetch-nyt-data-for-month ym api-key)
                 extract-articles-from-response)
        num-docs (count docs)]
    (log/info "Number of records: " num-docs)
    (insert-headlines! ds docs)
    (sql/insert! ds :process_log {:year_month ym :num num-docs})))

(def cli-options
  [["-s" "--start-date START-DATE" "Default start date"]])

(defn get-start-date
  "Extracts the start date from the provided command line arguments."
  [args cli-options]
  (get-in (cli/parse-opts args cli-options) [:options :start-date]))

(defn -main [& args]
  (let [api-key (System/getenv "nyt_api_key")
        ds (db-utils/get-datasource-from-env)
        default-start "1997-01"
        arg-start (get-start-date args cli-options)
        last-processed-month (db-utils/get-latest-processed-month ds)
        start-month (or
                      arg-start
                      (date-utils/add-month last-processed-month)
                      default-start)
        ym-seq (date-utils/year-month-sequence start-month)]
    (log/info "Processing months: " ym-seq)
    (doseq [ym ym-seq]
      (process-month ds ym api-key)
      (Thread/sleep 12000))))

