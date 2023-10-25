(ns nytdata.utils.date-test
  (:require [clojure.test :refer :all]
            [nytdata.utils.date :refer :all])
  (:import (java.time YearMonth LocalDate)))

(deftest format-year-month-test
  (is (= "2022-10" (format-year-month (YearMonth/of 2022 10))))
  (is (= "2022-1" (format-year-month (YearMonth/of 2022 01)))))

(deftest parse-year-month-test
  (is (= (YearMonth/of 2022 10) (parse-year-month "2022-10")))
  (is (= (YearMonth/of 2022 1) (parse-year-month "2022-1"))))

(deftest add-month-test
  (is (= "2022-11" (add-month "2022-10")))
  (is (= "2022-1" (add-month "2021-12")))
  (is (nil? (add-month nil))))

(deftest year-month-sequence-test
  (with-redefs [current-date (fn [] (LocalDate/of 2022 7 25))]
    (is (= ["2022-4" "2022-5" "2022-6"]
           (year-month-sequence "2022-4"))))
  (is (= ["2022-12" "2023-1" "2023-2"]
         (year-month-sequence "2022-12" "2023-2"))))
