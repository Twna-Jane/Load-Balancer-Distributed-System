# Makefile for Load-Balancer

.PHONY: all help build up down restart logs test clean analyze

help:
	@echo "Usage:"
	@echo "  make build         - Build all Docker containers"
	@echo "  make up            - Start all containers"
	@echo "  make down          - Stop and remove all containers"
	@echo "  make restart       - Restart all containers"
	@echo "  make logs          - View logs from all containers"
	@echo "  make test          - Run test requests to load balancer"
	@echo "  make analyze       - Run analysis notebook"
	@echo "  make clean         - Remove containers and prune system"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

test:
	curl http://localhost:5000/rep || true
	curl http://localhost:5000/add -X POST -H 'Content-Type: application/json' -d '{"n":1}' || true
	curl http://localhost:5000/rm -X DELETE -H 'Content-Type: application/json' -d '{"n":1}' || true

analyze:
	jupyter notebook analysis/analysis.ipynb

clean:
	docker-compose down -v
	docker system prune -af --volumes
