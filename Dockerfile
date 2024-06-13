ARG PYTHON_BASE=3.12-slim
ARG ENVIRONMENT="prod"

# build stage
FROM python:$PYTHON_BASE AS builder
ARG ENVIRONMENT
ENV \
    PDM_CHECK_UPDATE=false \
    PDM_NO_EDITABLE=true \
    PDM_NO_SELF=true
WORKDIR /code
RUN pip install --no-cache-dir pdm
COPY pyproject.toml pdm.lock ./
RUN pdm venv create && pdm install --check --${ENVIRONMENT}

# run stage
FROM python:$PYTHON_BASE
RUN useradd -ms /bin/sh -u 1001 app
USER app
WORKDIR /code
COPY --from=builder /code/.venv/ .venv
ENV PATH="/code/.venv/bin:$PATH"
COPY --chown=app:app alembic.ini pyproject.toml ./
COPY --chown=app:app alembic/ alembic
COPY --chown=app:app app/ app
COPY --chown=app:app tests/ tests

ARG ENVIRONMENT
ARG APP_NAME
ARG APP_VERSION
ARG COMMIT_SHA
ENV ENVIRONMENT=${ENVIRONMENT}
ENV APP_NAME=${APP_NAME}
ENV APP_VERSION=${APP_VERSION}
ENV COMMIT_SHA=${COMMIT_SHA}

CMD ["python", "-m", "app"]
