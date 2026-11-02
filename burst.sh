#!/usr/bin/env bash
# Pre-orders opening: 300 members order this week's box at the same moment.
#   ./burst.sh before     prints the summary and saves it to results/burst-before.txt
set -euo pipefail
cd "$(dirname "$0")"
label="${1:?usage: ./burst.sh <label>}"
docker compose run --rm --no-deps tools python tools/order_burst.py | tee "results/burst-$label.txt"
