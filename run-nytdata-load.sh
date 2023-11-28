#!/bin/bash

echo "Loading environment variables"
set -a
source .env
set +a


# Build Docker Image
echo "Building Docker image..."
docker build -t nytdata-load nytdata-clj

# Check if Docker build was successful
if [ $? -ne 0 ]; then
    echo "Docker build failed, exiting."
    exit 1
fi
echo "Docker image built successfully."

# Construct the JDBC URL
JDBC_DATABASE_URL="jdbc:postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/nytdata"

docker run --network=nytdata_default --rm -e jdbc_database_url="$JDBC_DATABASE_URL" -e nyt_api_key="$nyt_api_key" nytdata-load