(ns nytdata.main
  (:gen-class)
  (:require [cheshire.core :refer [parse-string]]
            [clj-http.client :as client]
            [clojure.string :as str]
            [next.jdbc.sql :as sql]
            [nytdata.utils.date :as date-utils]
            [nytdata.utils.db :as db-utils]
            [nytdata.utils.io :as io-utils]))


(def PARAMETERIZED-URL
  "https://api.nytimes.com/svc/archive/v1/%s/%s.json")
(def API-KEY
  (System/getenv "nyt_api_key"))
(def ALLOWED-WORDS
  (into #{} (str/split-lines (io-utils/read-resource-file "allow_words.txt"))))

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

(defn extract-section-and-date
  "Extracts section_name and publication date from a document."
  [doc]
  (let [section (get doc "section_name")
        year-month (date-utils/extract-year-month-from-timestamp (get doc "pub_date"))]
    {:section_name section :year_month year-month}))

(defn count-articles-by-section-and-date [coll]
  (->> coll
       (group-by (juxt :section_name :year_month))
       (map (fn [[[section-name year-month] entries]]
              {:section_name section-name
               :year_month   year-month
               :num_articles (count entries)}))
       (into [])))


(defn extract-counts [docs]
  (->> docs (map extract-section-and-date) count-articles-by-section-and-date))


(defn insert-counts
  "Inserts section counts into the monthly_content_counts table."
  [ds docs]
  (sql/insert-multi! ds :monthly_content_counts
                     (extract-counts docs) {:return-keys false}))

(defn extract-words [doc]
  (let [headline (str/lower-case (get-in doc ["headline" "main"]))
        pub-date (date-utils/extract-year-month-from-timestamp (get doc "pub_date"))
        cleaned-text (str/replace headline #"[\d\W_]" " ")
        words (str/split cleaned-text #"\s+")]
    (for [word words :when (ALLOWED-WORDS word)]
      {:word word :headline headline :year_month pub-date})))

(defn insert-words
  "Inserts words from docs' headlines into the word_headlines table."
  [ds docs]
  (sql/insert-multi! ds :word_headlines
                     (mapcat extract-words docs) {:return-keys false}))

(defn -main [& args]
  (let [ds (db-utils/get-datasource-from-env)
        latest-ym (db-utils/get-latest-processed-month ds)
        ym-seq (date-utils/year-month-sequence latest-ym)]
    (println (str "Processing months: " ym-seq))
    (doseq [ym ym-seq]
      (println (str "Fetching data for month: " ym))
      (let [docs (fetch-nyt-data-for-month ym)
            num-docs (count docs)]
        (println (str "\tNumber of records: " num-docs))
        (insert-words ds docs)
        (insert-counts ds docs)
        (sql/insert! ds :process_log {:year_month ym :num num-docs})
        (Thread/sleep 12000)))))
