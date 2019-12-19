#!/usr/bin/env bash

# Start PostgreSQL
docker-compose up -d postgres

until docker-compose exec postgres /usr/bin/pg_isready
do
  echo "Waiting for PostgreSQL to..."
  sleep 1
done

# Start up pgweb
docker-compose up -d pgweb jupyter
