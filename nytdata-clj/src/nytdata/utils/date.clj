(ns nytdata.utils.date
  (:import (java.time LocalDate YearMonth)
           (java.time.format DateTimeFormatter)))

(defn format-year-month
  "Convert a YearMonth instance to a string, optionally using a provided pattern."
  ([year-month] (format-year-month year-month (DateTimeFormatter/ofPattern "yyyy-M")))
  ([year-month pattern] (.format year-month pattern)))

(defn parse-year-month
  "Parse a month string into a YearMonth instance, optionally using a provided pattern."
  ([month-string] (parse-year-month month-string (DateTimeFormatter/ofPattern "yyyy-M")))
  ([month-string pattern] (YearMonth/parse month-string pattern)))

(defn add-month
  "Increment the provided month string by one month."
  [month]
  (when month
    (-> (parse-year-month month)
        (.plusMonths 1)
        format-year-month)))

(defn current-date []
  (LocalDate/now))

(defn year-month-sequence
  "Calculate a sequence of year-month strings from the given start-month
   up to the end-month or last completed month."
  ([start-month] (year-month-sequence start-month (-> (current-date) (.minusMonths 1) (format-year-month))))
  ([start-month end-month] (->> (iterate #(.plusMonths % 1) (parse-year-month start-month))
                                (take-while #(not (.isAfter % (parse-year-month end-month))))
                                (map #(.format % (DateTimeFormatter/ofPattern "yyyy-M")))
                                (into []))))