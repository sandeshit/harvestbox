#!/usr/bin/env bash
# Runs the ordering tests against a throwaway test database.
set -euo pipefail
cd "$(dirname "$0")"
docker compose run --rm --no-deps tools python manage.py test orders -v 2
