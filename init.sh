#!/usr/bin/env bash

export $(egrep -v '^#' .env | xargs)

# Initialize PostgreSQL data
docker-compose stop postgres
rm -rf postgres/data
docker-compose up -d postgres

until docker-compose exec postgres /usr/bin/pg_isready
do
  echo "Waiting for PostgreSQL to..."
  sleep 1
done

# Start up pgweb
docker-compose up -d pgweb

# Start up jupyter
docker-compose up -d jupyter

# Run init python script
docker-compose exec jupyter python src/main.py init_db

# Open pgweb
open http://${PGWEB_USER}:${PGWEB_PASSWORD}@localhost:${PGWEB_PORT}

# Open jupyter notebook
open $(docker-compose exec jupyter jupyter notebook list | grep token |  sed -E 's/(token=.*) :: \/app/\1/')
