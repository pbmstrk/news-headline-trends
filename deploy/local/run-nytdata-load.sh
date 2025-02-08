#!/bin/bash
echo "Loading environment variables"
set -a
source .env
set +a

echo "Building Docker image..."
docker build --quiet -t nytdata-load ../../nytdata-clj

if [[ $? -ne 0 ]]; then
    echo "Docker build failed, exiting."
    exit 1
fi
echo "Docker image built successfully."

DATABASE_CONTAINER_STATUS=$(docker container inspect -f '{{.State.Status}}' local-db-1 2> /dev/null) 

if [[ "$DATABASE_CONTAINER_STATUS" != "running" ]]; then 
    echo "Container local-db-1 is not running (status: '$DATABASE_CONTAINER_STATUS'). Exiting."
    exit 1
fi

if ! docker network inspect local_nytdata > /dev/null 2>&1; then 
    echo "Network local_nytdata does not exist. Exiting."
    exit 1
fi

JDBC_DATABASE_URL="jdbc:postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/nytdata"

docker run --network=local_nytdata --rm -e jdbc_database_url="$JDBC_DATABASE_URL" -e nyt_api_key="$nyt_api_key" nytdata-load