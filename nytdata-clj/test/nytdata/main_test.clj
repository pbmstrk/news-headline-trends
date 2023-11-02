(ns nytdata.main-test
  (:require [clj-http.client]
            [clojure.test :refer :all]
            [nytdata.main :refer :all]))

(declare thrown?)

(deftest construct-nyt-api-url-test
  (is (= "https://api.nytimes.com/svc/archive/v1/2023/9.json"
         (construct-nyt-api-url "2023-09")))
  (is (thrown? AssertionError (construct-nyt-api-url nil))))

(deftest extract-articles-from-response-test
  (is (= [:hit1 :hit2]
         (extract-articles-from-response {:body {:response {:docs [:hit1 :hit2]}}}))))

(deftest extract-metadata-test
  (is (= ["uri" "headline" "pub_date" "web_url" "section_name"]
         (extract-metadata {:uri          "uri"
                            :headline     {:main "headline"}
                            :pub_date     "pub_date"
                            :web_url      "web_url"
                            :section_name "section_name"}))))

(deftest fetch-nyt-data-for-month-test
  (with-redefs [clj-http.client/get (fn [_ _] {:status 200 :body {:response {:docs [:hit1 :hit2]}}})]
    (let [result (fetch-nyt-data-for-month "2022-01" "api-key")]
      (is (= [:hit1 :hit2] result))))
  (with-redefs [clj-http.client/get (fn [_ _] {:status 404})]
    (is (thrown? Exception (fetch-nyt-data-for-month "2022-01" "api-key")))))

(deftest get-start-date-test
  (is (= "2020-01" (get-start-date ["-s" "2020-01"] cli-options))))