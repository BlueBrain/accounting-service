SHELL := /bin/bash
SERVICE_NAME := accounting-service
HELP_TEMPLATE := \033[36m%-23s\033[0m %s

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(HELP_TEMPLATE)\n", $$1, $$2}'
	@tox list|grep -v __internal__|grep -E '^[a-zA-Z_-]+ .*?-> .*$$'|awk 'BEGIN {FS = " .*?-> "}; {printf "$(HELP_TEMPLATE)\n", $$1, $$2}'

build-image:  ## Build the local docker images
	VERSION=$(shell tox run -qq -e version) && \
	COMMIT_SHA=$(shell git rev-parse HEAD) && \
	docker compose --progress=plain build \
		--build-arg APP_NAME=$(SERVICE_NAME):local \
		--build-arg APP_VERSION=$$VERSION \
		--build-arg COMMIT_SHA=$$COMMIT_SHA \
		--build-arg INSTALL_DEBUG_TOOLS=true

run-image: build-image  ## Run the local docker images
	docker compose --progress=tty up --watch --remove-orphans

compile-deps:  ## Create or update requirements.txt, without upgrading the version of the dependencies
	tox exec -e pip-tools -- python -m piptools compile

upgrade-deps:  ## Create or update requirements.txt, using the latest version of the dependencies
	tox exec -e pip-tools -- python -m piptools compile --upgrade

check-deps:  ## Check that the dependencies in the existing requirements.txt are valid
	diff --ignore-blank-lines \
	<(grep -vE "^ *\#" requirements.txt) \
	<(tox exec -qq -e pip-tools -- python -m piptools compile -q -o - | grep -vE "^ *\#")

clean:  ## Delete tox environments and temporary files
	rm -rf .tox
	find . -type d -name '*.egg-info' -print0 | xargs -0 rm -rf

.DEFAULT:  # Run tox by default for any unknown target
	tox run -e $@ $(OPTIONS)
