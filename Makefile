#!make

jupyter:
	open $$(docker-compose exec jupyter jupyter notebook list | grep token |  sed -E 's/(token=.*) :: \/app/\1/')

pgweb:
	export $$(egrep -v '^#' .env | xargs) \
	&& open http://$${PGWEB_USER}:$${PGWEB_PASSWORD}@localhost:$${PGWEB_PORT}

run:
	docker-compose exec jupyter $(filter-out $@,$(MAKECMDGOALS))

main:
	docker-compose exec jupyter python src/main.py $(filter-out $@,$(MAKECMDGOALS))

shell:
	docker-compose exec jupyter /bin/bash

