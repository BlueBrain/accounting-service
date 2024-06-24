ARG PYTHON_BASE=3.12
ARG ENVIRONMENT

# build stage
FROM python:$PYTHON_BASE AS builder
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]
ARG ENVIRONMENT
ARG PDM_VERSION=2.15.4
ENV \
    PDM_CHECK_UPDATE=false \
    PDM_NO_EDITABLE=true \
    PDM_NO_SELF=true
WORKDIR /code
RUN pip install --no-cache-dir pdm==${PDM_VERSION}
COPY pyproject.toml pdm.lock ./
RUN \
    if ! [[ "${ENVIRONMENT}" =~ ^(dev|prod)$ ]]; then echo "Invalid ENVIRONMENT"; exit 1; fi && \
    pdm venv create --with-pip && pdm install --check --${ENVIRONMENT}

# run stage
FROM python:$PYTHON_BASE
RUN useradd -ms /bin/sh -u 1001 app
USER app
WORKDIR /code
ENV PATH="/code/.venv/bin:$PATH"
COPY --chown=app:app --from=builder /code/.venv/ .venv/
COPY --chown=app:app alembic.ini docker-cmd.sh pyproject.toml ./
COPY --chown=app:app alembic/ alembic/
COPY --chown=app:app app/ app/

ARG ENVIRONMENT
ARG APP_NAME
ARG APP_VERSION
ARG COMMIT_SHA
ENV ENVIRONMENT=${ENVIRONMENT}
ENV APP_NAME=${APP_NAME}
ENV APP_VERSION=${APP_VERSION}
ENV COMMIT_SHA=${COMMIT_SHA}

STOPSIGNAL SIGINT
CMD ["./docker-cmd.sh"]
