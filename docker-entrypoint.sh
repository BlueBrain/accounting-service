#!/bin/bash
set -e -o errexit

#alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8900 --proxy-headers --log-config app/data/logging.yaml
