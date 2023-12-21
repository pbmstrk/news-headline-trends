(ns nytdata.spec
  (:require [nytdata.main :as m]
            [clojure.spec.alpha :as s]))

; fields in nested structure
(s/def ::m/uri string?)
(s/def ::m/main string?)
(s/def ::m/pub_date string?)
(s/def ::m/web_url string?)
(s/def ::m/section_name string?)

; structures
(s/def ::m/headline (s/keys :req-un [::m/main]))
(s/def ::m/doc (s/keys :req-un [::m/uri ::m/headline ::m/pub_date ::m/web_url ::m/section_name]))
(s/def ::m/docs (s/coll-of ::m/doc))
(s/def ::m/response (s/keys :req-un [::m/docs]))
(s/def ::m/body (s/keys :req-un [::m/response]))
(s/def ::m/response-map (s/keys :req-un [::m/body]))

(s/fdef m/extract-articles-from-response
        :args (s/cat :response ::response-map)
        :ret ::m/docs)




