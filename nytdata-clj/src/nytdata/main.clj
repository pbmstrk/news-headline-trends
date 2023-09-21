(ns nytdata.main
  (:gen-class)
  (:require [clj-http.client :as client]
            [clojure.string :as str]
            [clojure.tools.cli :as cli]
            [next.jdbc :as jdbc]
            [next.jdbc.sql :as sql]
            [nytdata.utils.date :as date-utils]
            [nytdata.utils.db :as db-utils]))

(defn construct-nyt-api-url
  "Create the URL for the http request based on year-month string."
  [year-month]
  (let [[year month] (str/split year-month #"-")]
    (format "https://api.nytimes.com/svc/archive/v1/%s/%s.json" year month)))

(defn extract-articles-from-response
  "Extracts articles from the API response."
  [response]
  (get-in response [:body :response :docs]))

(defn fetch-nyt-data-for-month
  "Fetches data from the NYT API for a given year and month."
  [year-month api-key]
  (let [url (construct-nyt-api-url year-month)
        response (client/get url {:throw-exceptions false :as :json :query-params {:api-key api-key}})]
    (if (= 200 (:status response))
      (extract-articles-from-response response)
      (throw (Exception. (str "Failed to fetch data for " year-month ": " (:status response)))))))

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
  (println (str "Fetching data for month: " ym))
  (let [docs (fetch-nyt-data-for-month ym api-key)
        num-docs (count docs)]
    (println (str "\tNumber of records: " num-docs))
    (insert-headlines! ds docs)
    (sql/insert! ds :process_log {:year_month ym :num num-docs})))


(def cli-options
  [["-s" "--start-date START-DATE" "Default start date"
    :default "1996-12"]])

(defn -main [& args]
  (let [api-key (System/getenv "nyt_api_key")
        default-start (-> (cli/parse-opts args cli-options) :options :start-date)
        ds (db-utils/get-datasource-from-env)
        latest-ym (db-utils/get-latest-processed-month ds default-start)
        ym-seq (date-utils/year-month-sequence latest-ym)]
    (println (str "Processing months: " ym-seq))
    (doseq [ym ym-seq]
      (process-month ds ym api-key)
      (Thread/sleep 12000))
    (when (seq ym-seq)
      (println "Refreshing materialized views")
      (jdbc/execute! ds ["refresh materialized view monthly_content_counts_vw"]))))

