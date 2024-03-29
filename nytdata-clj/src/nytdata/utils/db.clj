(ns nytdata.utils.db
  (:require [next.jdbc :as jdbc]
            [next.jdbc.sql :as sql]))

(defn get-datasource-from-env []
  (let [database-url  (System/getenv "jdbc_database_url")]
    (jdbc/get-datasource database-url)))

(defn get-latest-processed-month [ds]
  (let [record (sql/query ds ["select max(year_month) from process_log"])]
    (-> record first :max)))