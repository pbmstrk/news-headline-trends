#!/bin/bash

# Load environment variables from .env file
set -a
source ../.env
set +a

# Construct the JDBC URL
JDBC_DATABASE_URL="jdbc:postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/nytdata"

docker run --network=nytdata_default --rm -e jdbc_database_url="$JDBC_DATABASE_URL" -e nyt_api_key="$nyt_api_key" nytdata-load