#!/bin/bash
set -ex -o pipefail

alembic upgrade head
uvicorn \
  --host=0.0.0.0 \
  --proxy-headers \
  --log-config=app/data/logging.yaml \
  app.application:app
