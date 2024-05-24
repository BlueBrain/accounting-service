FROM python:3.12
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

ARG INSTALL_DEBUG_TOOLS
RUN \
    if [[ "${INSTALL_DEBUG_TOOLS}" == "true" ]]; then \
        SYSTEM_DEBUG_TOOLS="vim less curl jq htop strace net-tools iproute2" && \
        PYTHON_DEBUG_TOOLS="py-spy memory-profiler" && \
        echo "Installing tools for profiling and inspection..." && \
        apt-get update && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ${SYSTEM_DEBUG_TOOLS} && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/* && \
        pip install --no-cache-dir --upgrade ${PYTHON_DEBUG_TOOLS} ; \
    fi

RUN useradd -ms /bin/sh -u 1001 app
ENV PATH="${PATH}:/home/app/.local/bin"
USER app

WORKDIR /src
COPY --chown=app:app requirements.txt .
COPY --chown=app:app docker-entrypoint.sh .

RUN \
    pip install --user --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir --upgrade -r requirements.txt

COPY --chown=app:app ./src/app app

ARG APP_NAME
ARG APP_VERSION
ARG COMMIT_SHA
ENV APP_NAME=${APP_NAME}
ENV APP_VERSION=${APP_VERSION}
ENV COMMIT_SHA=${COMMIT_SHA}

ENTRYPOINT ["./docker-entrypoint.sh"]
