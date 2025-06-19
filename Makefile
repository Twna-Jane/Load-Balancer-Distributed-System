
# Makefile for Load-Balancer

.PHONY: all help build_task1 run_task1 build_task2 run_task2 build_task3 run_task3 analyze_task4 up down restart logs test clean

help:
	@echo "Usage:"
	@echo "  make build_task1     - Build Task 1 Docker container (Server only)"
	@echo "  make run_task1       - Run Task 1 server"
	@echo "  make build_task2     - Build Task 2 Load Balancer and Servers"
	@echo "  make run_task2       - Run Task 2 with docker-compose"
	@echo "  make build_task3     - Build Task 3 final implementation"
	@echo "  make run_task3       - Run Task 3 final implementation"
	@echo "  make analyze_task4   - Run analysis in TASK_4"
	@echo "  make up              - Start all containers"
	@echo "  make down            - Stop and remove all containers"
	@echo "  make restart         - Restart all containers"
	@echo "  make logs            - View logs from Task 2 containers"
	@echo "  make test            - Run test requests to load balancer"
	@echo "  make clean           - Remove containers and prune system"

build_task1:
	docker build -t task1-server -f TASK_1/Dockerfile TASK_1

run_task1:
	python TASK_1/server.py

build_task2:
	docker-compose -f TASK_2/docker-compose.yml build

run_task2:
	docker-compose -f TASK_2/docker-compose.yml up -d

build_task3:
	docker-compose -f TASK_3/docker-compose.yml build

run_task3:
	docker-compose -f TASK_3/docker-compose.yml up -d

analyze_task4:
	jupyter notebook TASK_4/analysis.ipynb

up: run_task2

down:
	docker-compose -f TASK_2/docker-compose.yml down

restart: down up

logs:
	docker-compose -f TASK_2/docker-compose.yml logs -f

test:
	curl http://localhost:6000/request/123 || true
	curl http://localhost:6000/request/456 || true
	curl http://localhost:6000/request/789 || true

clean:
	docker-compose -f TASK_2/docker-compose.yml down -v
	docker system prune -af --volumes
