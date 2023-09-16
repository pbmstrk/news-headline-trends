FROM clojure

WORKDIR /nytdata 

COPY src ./src
COPY deps.edn deps.edn
COPY build.clj build.clj 

RUN clj -T:build uber

ENTRYPOINT ["java", "-jar", "target/nytdata-standalone.jar"]