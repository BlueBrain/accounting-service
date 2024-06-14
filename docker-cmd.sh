#!/bin/bash
set -ex -o pipefail

alembic upgrade head
python -m app
