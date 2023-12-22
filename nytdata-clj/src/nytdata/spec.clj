(ns nytdata.spec
  (:require [nytdata.main :as m]
            [clojure.spec.alpha :as s]))

; fields in nested structure
(s/def :doc/uri string?)
(s/def :doc.headline/main string?)
(s/def :doc/pub_date string?)
(s/def :doc/web_url string?)
(s/def :doc/section_name string?)

; structures
(s/def :doc/headline (s/keys :req-un [:doc.headline/main]))
(s/def :docs/doc (s/keys :req-un [:doc/uri :doc/headline :doc/pub_date :doc/web_url :doc/section_name]))
(s/def :response/docs (s/coll-of :docs/doc))
(s/def :body/response (s/keys :req-un [:response/docs]))
(s/def :response-map/body (s/keys :req-un [:body/response]))
(s/def :response-map/response-map (s/keys :req-un [:response-map/body]))

(s/fdef m/extract-articles-from-response
        :args (s/cat :response :response-map/response-map)
        :ret :response/docs)