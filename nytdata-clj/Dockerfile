FROM clojure

WORKDIR /nytdata 

COPY resources ./resources
COPY src ./src 
COPY deps.edn deps.edn
COPY build.clj build.clj 

RUN clj -T:build uber

CMD ["java", "-jar", "target/nytdata-standalone.jar"]