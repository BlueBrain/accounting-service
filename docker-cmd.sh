#!/bin/bash
set -ex -o pipefail

# ensure that the database is up to date
alembic upgrade head

# use exec to replace the shell and ensure that SIGINT is sent to the app
exec python -m app
