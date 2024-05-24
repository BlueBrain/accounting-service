# accounting-service

## Description

This service is composed by:

-   `accounting-service`: main service, listening on port 8900.

## Local build and deployment

To build and start the Docker image locally, you can execute:

```bash
tox -e build-image,run-image
```

Possible tox environments (run `tox list` for the full list):

```
# build-image          -> Build a local docker image
# run-image            -> Run a local docker image previously built
# logs-image           -> Tail the logs of a local docker container
```

## Remote deployment

To make a release, build and publish the Docker image to the registry, you need to:

-   push a tag to the main branch using git, or
-   create a release through the GitHub UI.

The format of the tag should be `YYYY.MM.DD`, where:

-   `YYYY` is the full year (2024, 2025 ...)
-   `MM` is the short month, not zero-padded (1, 2 ... 11, 12)
-   `DD` is any incremental number, not zero-padded (it doesn't need to be the day number)

The new Docker images are automatically deployed after a few minutes.

See also the configuration files at <https://bbpgitlab.epfl.ch/project/sbo/k8s>.

## Documentation

The API documentation is available locally at <https://127.0.0.1:8900/docs> after the local deployment.
