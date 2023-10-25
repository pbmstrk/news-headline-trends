(ns nytdata.utils.db-test
  (:require [clojure.test :refer :all]
            [nytdata.utils.db :refer :all]
            [next.jdbc.sql :as sql]))

(deftest get-latest-processed-month-test
  (with-redefs [sql/query (fn [_ _] [{:max 1}])]
    (is (= 1 (get-latest-processed-month "ds"))))
  (with-redefs [sql/query (fn [_ _] [])]
    (is (nil? (get-latest-processed-month "ds")))))