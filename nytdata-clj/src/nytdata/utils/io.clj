(ns nytdata.utils.io
  (:require [clojure.java.io :as io]))

(defn read-resource-file [file_name]
  (let [resource-url (io/resource file_name)]
    (when resource-url
      (slurp resource-url))))
