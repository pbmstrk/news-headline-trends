(ns nytdata.utils.date
  (:import (java.time LocalDate YearMonth)
           (java.time.format DateTimeFormatter)))

(defn year-month-sequence
  "Calculate a sequence of year-month strings from the given start-date up to the last completed month."
  [start-date]
  (let [start-ym (-> (YearMonth/parse start-date
                                  (DateTimeFormatter/ofPattern "yyyy-M"))
                     (.plusMonths 1))
        current-ym (-> (LocalDate/now)
                       (.minusMonths 1)                     ;; Go back one month to get the last complete month
                       (YearMonth/from))]
    (->> (iterate #(.plusMonths % 1) start-ym)
         (take-while #(not (.isAfter % current-ym)))
         (map #(.format % (DateTimeFormatter/ofPattern "yyyy-M")))
         (into []))))

(defn extract-year-month-from-timestamp [timestamp]
  (subs timestamp 0 7))

(defn convert-date-format [ym]
  (let [date (YearMonth/parse ym (DateTimeFormatter/ofPattern "yyyy-M"))]
    (.format date (DateTimeFormatter/ofPattern "yyyy-MM"))))