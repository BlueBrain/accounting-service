SHELL := /bin/bash

export ENVIRONMENT ?= dev
export APP_NAME := accounting-service
export APP_VERSION := $(shell git describe --abbrev --dirty --always --tags)
export COMMIT_SHA := $(shell git rev-parse HEAD)

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-23s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies into .venv
	pdm install --no-self

compile-deps:  ## Create or update the lock file, without upgrading the version of the dependencies
	pdm lock --update-reuse

upgrade-deps:  ## Create or update the lock file, using the latest version of the dependencies
	pdm lock

check-deps:  ## Check that the dependencies in the existing lock file are valid
	pdm lock --check

format:  # Run formatters
	pdm run ruff format
	pdm run ruff check --fix

lint:  ## Run linters
	pdm run ruff format --check
	pdm run ruff check
	pdm run mypy app

build:  ## Build the docker images
	docker compose --progress=plain build

run: build  ## Run the application in docker
	docker compose --progress=tty up app --watch --remove-orphans

kill:  ## Take down the application
	docker compose down --remove-orphans

test: build  ## Run tests in the app container
	docker compose run --rm test

test-local:  ## Run tests locally
	# faster, but it requires a test db already running
	export DB_HOST=127.0.0.1 DB_PORT=5434 && \
	pdm run python -m pytest -vv --cov=app tests

migration: build  ## Create the alembic migration
	docker compose run --rm migration

config:  ## Show the docker-compose configuration in the current environment
	docker compose config

sh: build  ## Run a shell in the app container
	docker compose run --rm app bash
