#!/usr/bin/env bash
# Clears this week's pre-orders and puts all the boxes back.
set -euo pipefail
cd "$(dirname "$0")"
docker compose run --rm --no-deps tools python manage.py reset_offer
