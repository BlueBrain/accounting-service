# accounting-service

## Description

This service is composed by:

-   `accounting-service`: main service, listening on port 8900.

## Local build and deployment

Valid `make` targets:

```
help                    Show this help
build-image             Build the local docker images
run-image               Run the local docker images
compile-deps            Create or update requirements.txt, without upgrading the version of the dependencies
upgrade-deps            Create or update requirements.txt, using the latest version of the dependencies
check-deps              Check that the dependencies in the existing requirements.txt are valid
py                      Run tests and coverage
lint                    Check linting
format                  Format the code
version                 Print the version
```

To build and start the Docker images locally, you can execute:

```bash
make run-image
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

The API documentation is available locally at <https://127.0.0.1:8900/docs> after the local deployment.
