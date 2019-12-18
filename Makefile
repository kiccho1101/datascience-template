#!make

jupyter:
	open $$(docker-compose exec jupyter jupyter notebook list | grep token |  sed -E 's/(token=.*) :: \/app/\1/')

token:
	docker-compose exec jupyter jupyter notebook list

pgweb:
	export $$(egrep -v '^#' .env | xargs) \
	&& open http://$${PGWEB_USER}:$${PGWEB_PASSWORD}@localhost:$${PGWEB_PORT}

run:
	docker-compose exec jupyter $(filter-out $@,$(MAKECMDGOALS))

main:
	docker-compose exec jupyter python src/main.py $(filter-out $@,$(MAKECMDGOALS))

shell:
	docker-compose exec jupyter /bin/bash

init_db:
	docker-compose exec jupyter python src/main.py init_db

kfold:
	docker-compose exec jupyter python src/main.py kfold $(filter-out $@,$(MAKECMDGOALS))

feature:
	docker-compose exec jupyter python src/main.py feature $(filter-out $@,$(MAKECMDGOALS))

cv:
	docker-compose exec jupyter python src/main.py cv $(filter-out $@,$(MAKECMDGOALS))

predict:
	docker-compose exec jupyter python src/main.py predict $(filter-out $@,$(MAKECMDGOALS))

format:
	pipenv run black src/
