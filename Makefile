# Makefile - sql-artifacts Docker Dev Commands

COMPOSE = docker compose
SERVICE = dev

.PHONY: up down build logs shell test restart clean help

## Start containers in background
up:
	docker compose --profile dev up -d

## Stop and remove containers
down:
	docker compose down

## Rebuild and start containers
restart:
	$(COMPOSE) down
	$(COMPOSE) --profile dev up -d --build

## Build containers without running
build:
	$(COMPOSE) build

## Follow logs for all services
logs:
	$(COMPOSE) logs -f

## Enter shell inside dev container
shell:
	$(COMPOSE) exec $(SERVICE) bash

test:
	docker compose run --rm test-runner poetry run pytest

coverage:
	docker compose run --rm test-runner poetry run pytest \
		--cov=src \
		--cov-report=term-missing

ci-test:
	docker compose --profile test up --abort-on-container-exit --exit-code-from test-runner


## Clean containers + volumes
clean:
	$(COMPOSE) down --volumes

## Print help message
help:
	@echo ""
	@echo "Common Make targets:"
	@echo "  make up       - Start containers in background"
	@echo "  make down     - Stop containers"
	@echo "  make build    - Build containers"
	@echo "  make restart  - Rebuild and restart containers"
	@echo "  make logs     - Follow logs"
	@echo "  make shell    - Open bash in dev container"
	@echo "  make test     - Run pytest"
	@echo "  make clean    - Stop and remove containers and volumes"
	@echo "  make help     - Show this help message"
	@echo ""

# 🌳 Show project structure
tree:
	@tree -a --prune -I "*~|__pycache__|*.bak|.git|*_cache"
