(ns nytdata.utils.date
  (:import (java.time LocalDate YearMonth)
           (java.time.format DateTimeFormatter)))

(defn YearMonth->string
  [year-month] (.format year-month (DateTimeFormatter/ofPattern "yyyy-MM")))

(defn string->YearMonth
  [month-string] (YearMonth/parse month-string (DateTimeFormatter/ofPattern "yyyy-MM")))

(defn padded-month->month
  "Convert yyyy-MM representation to yyyy-M"
  [month]
  (.format (string->YearMonth month) (DateTimeFormatter/ofPattern "yyyy-M")))

(defn add-month
  "Increment the provided month string by one month."
  ([month] (when month
             (-> (string->YearMonth month)
                 (.plusMonths 1)
                 YearMonth->string))))

(defn current-date []
  (LocalDate/now))

(defn year-month-sequence
  "Calculate a sequence of year-month strings from the given start-month
   up to the end-month or last completed month."
  ([start-month] (year-month-sequence start-month (-> (current-date) (.minusMonths 1) YearMonth->string)))
  ([start-month end-month] (->> (iterate #(.plusMonths % 1) (string->YearMonth start-month))
                                (take-while #(not (.isAfter % (string->YearMonth end-month))))
                                (map YearMonth->string)
                                (into []))))