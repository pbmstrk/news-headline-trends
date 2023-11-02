(ns nytdata.utils.date-test
  (:require [clojure.test :refer :all]
            [nytdata.utils.date :refer :all])
  (:import (java.time YearMonth LocalDate)))

(deftest format-year-month-test
  (is (= "2022-10" (YearMonth->string (YearMonth/of 2022 10))))
  (is (= "2022-01" (YearMonth->string (YearMonth/of 2022 01)))))

(deftest parse-year-month-test
  (is (= (YearMonth/of 2022 10) (string->YearMonth "2022-10")))
  (is (= (YearMonth/of 2022 1) (string->YearMonth "2022-01"))))

(deftest add-month-test
  (is (= "2022-11" (add-month "2022-10")))
  (is (= "2022-01" (add-month "2021-12")))
  (is (nil? (add-month nil))))

(deftest year-month-sequence-test
  (with-redefs [current-date (fn [] (LocalDate/of 2022 7 25))]
    (is (= ["2022-04" "2022-05" "2022-06"]
           (year-month-sequence "2022-04"))))
  (is (= ["2022-12" "2023-01" "2023-02"]
         (year-month-sequence "2022-12" "2023-02"))))
