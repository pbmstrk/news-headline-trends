FROM clojure:temurin-17-tools-deps AS build

WORKDIR /

COPY src ./src
COPY deps.edn deps.edn
COPY build.clj build.clj 

RUN clj -T:build uber

FROM eclipse-temurin:17

WORKDIR /

COPY --from=build target/nytdata-standalone.jar /

COPY root.crt* /root/.postgresql/root.crt

ENTRYPOINT ["java", "-jar", "nytdata-standalone.jar"]