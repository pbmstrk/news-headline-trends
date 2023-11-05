FROM golang:1.21 as build 

WORKDIR /app 

COPY go.mod go.sum ./ 
RUN go mod download 

COPY main.go ./

RUN CGO_ENABLED=0 GOOS=linux go build -o /nytdata-api main.go

FROM alpine:latest as build-release-stage 

WORKDIR /

COPY --from=build /nytdata-api /nytdata-api

EXPOSE 8050

CMD ["/nytdata-api"]