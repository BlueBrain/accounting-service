# accounting-service

## Description

This service is composed by:

-   `accounting-service`: main service.

## Local build and deployment

Valid `make` targets:

```
help                    Show this help
install                 Install dependencies into .venv
compile-deps            Create or update the lock file, without upgrading the version of the dependencies
upgrade-deps            Create or update the lock file, using the latest version of the dependencies
check-deps              Check that the dependencies in the existing lock file are valid
lint                    Run linters
build                   Build the docker images
run                     Run the application in docker
kill                    Take down the application
tests                   Run tests in the app container
migration               Create the alembic migration
sh                      Run a shell in the app container
```

To build and start the Docker images locally, you can execute:

```bash
make run
```


## Remote deployment

To make a release, build and publish the Docker image to the registry, you need to:

-   push a tag to the main branch using git, or
-   create a release through the GitHub UI.

The format of the tag should be `YYYY.MM.DD`, where:

-   `YYYY` is the full year (2024, 2025 ...)
-   `MM` is the short month, not zero-padded (1, 2 ... 11, 12)
-   `DD` is any incremental number, not zero-padded (it doesn't need to be the day number)


## Documentation

The API documentation is available locally at <http://127.0.0.1:8100/docs> after the local deployment.
