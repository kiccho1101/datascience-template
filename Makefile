jupyter:
	docker-compose up -d jupyter

token:
	docker-compose exec jupyter jupyter notebook list

run:
	docker-compose exec jupyter $(filter-out $@,$(MAKECMDGOALS))

main:
	docker-compose exec jupyter python src/main.py $(filter-out $@,$(MAKECMDGOALS))

shell:
	docker-compose exec jupyter /bin/bash
