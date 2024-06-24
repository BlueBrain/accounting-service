SHELL := /bin/bash

# export variables to both build and run recipes for automatic rebuilding when pdm.lock is modified
build run: export ENVIRONMENT ?= dev
build run: export APP_NAME := accounting-service
build run: export APP_VERSION := $(shell git describe --abbrev --dirty --always --tags)
build run: export COMMIT_SHA := $(shell git rev-parse HEAD)

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
	docker compose --progress=tty up --watch --remove-orphans

kill:  ## Take down the application
	docker compose down --remove-orphans

.PHONY: tests
tests: build  ## Run tests in the app container
	docker compose run --rm app sh -c "\
		alembic downgrade base && alembic upgrade head && \
	    python -m pytest -vv --cov=app tests && \
		python -m coverage xml && \
		python -m coverage html"

migration: build  ## Create the alembic migration
	docker compose run --rm app sh -c "\
		alembic upgrade head && alembic revision --autogenerate"

sh: build  ## Run a shell in the app container
	docker compose run --rm app bash
