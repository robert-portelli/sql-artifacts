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

## Test Course 02
test-c2:
	docker compose rm -fs test-db && docker compose run --rm -e LOG_LEVEL=DEBUG test-runner poetry run pytest --cov=src/sql_artifacts/course_02_intermediate_sql/ --cov-report=term tests/course_02_intermediate_sql/

## Test Course 02 CI
test-c2-ci:
	gh act -W .github/workflows/test_course_02_intermediate_sql.yaml -P ubuntu-latest=robertportelli/sql-artifacts

## Run tests (optionally specify a path with T=tests/...)
## Arguments:
##   T      - (Optional) Path to a specific test file. Defaults to `tests`.
##
## Examples:
##   make test
##   make test T=tests/course_02_intermediate_sql/test_loader.py
test:
	@echo "Running pytest on path: $${T:-tests}"
	docker compose rm -fs test-db
	docker compose run --rm test-runner \
		sh -c 'poetry run pytest --override-ini="addopts=" "$${T:-tests}"'

## Run tests (optionally specify a path with T=tests/...)
## Arguments:
##   T      - (Optional) Path to a specific test file or directory.
##
## Examples:
##   make test
##   make test T=tests/course_02_intermediate_sql/test_loader.py
test:
	@echo "Running tests at path: $${T:-tests}"
	docker compose rm -fs test-db
	docker compose run --rm test-runner \
		sh -c 'poetry run pytest $${T:-tests}'

## Run tests with live logging output (optionally specify LEVEL and T)
## Arguments:
##   LEVEL  - (Optional) Logging level (INFO, DEBUG, etc.). Defaults to INFO.
##   T      - (Optional) Path to a specific test file or directory.
##
## Examples:
##   make test-verbose LEVEL=DEBUG
##   make test-verbose LEVEL=INFO T=tests/course_02_intermediate_sql/test_loader.py
test-verbose:
	@echo "Running tests with LOG_LEVEL=$${LEVEL:-INFO} at path: $${T:-tests}"
	docker compose rm -fs test-db
	docker compose run --rm -e LOG_LEVEL=$${LEVEL:-INFO} test-runner \
		sh -c 'poetry run pytest -s $${T:-tests}'

## Run tests with code coverage and HTML output
## Arguments:
##   T      - (Optional) Path to a specific test file or directory.
##
## Examples:
##   make coverage
##   make coverage T=tests/unit/test_db_client.py
coverage:
	@echo "Running tests with coverage at path: $${T:-tests}"
	docker compose rm -fs test-db
	docker compose run --rm test-runner \
		sh -c 'poetry run pytest --cov=src --cov-report=term --cov-report=html:coverage_html $${T:-tests}'

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
