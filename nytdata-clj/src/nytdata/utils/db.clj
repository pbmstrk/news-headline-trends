(ns nytdata.utils.db
  (:require [next.jdbc :as jdbc]
            [next.jdbc.sql :as sql]))

(defn get-datasource-from-env []
  (let [database-url (str "jdbc:" (System/getenv "database_url"))]
    (jdbc/get-datasource database-url)))

(def DEFAULT-START-DATE "2019-12")

(defn get-latest-processed-month [ds]
  (let [record (sql/query ds ["select max(year_month) from process_log"])]
    (if-let [ym (-> record first :max)]
      ym
      DEFAULT-START-DATE)))