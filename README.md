# Harvestbox

Weekly produce-box pre-orders for the Hollow Creek farm co-op. The farm packs a fixed
number of boxes each week (100 at the moment). Pre-orders open when the weekly email goes
out, and members order through the co-op's web shop, which calls this API. Members collect
their box on Friday or Saturday at one of three pickup points.

## Running it

Everything runs in Docker Compose:

| Service | What it is |
|---|---|
| `db` | PostgreSQL 17 |
| `api` | Django REST API on gunicorn, 4 workers × 16 threads |
| `tools` | One-off containers for commands (migrations, sample data, scripts, tests) |

```
docker compose up -d --build
docker compose run --rm tools python manage.py migrate
docker compose run --rm tools python manage.py load_sample_data
```

The project folder is mounted into the containers, so after a code change run
`docker compose restart api`.

## Scripts

| Script | What it does |
|---|---|
| `./reset-offer.sh` | Clears the open week's pre-orders and puts all its boxes back |
| `./burst.sh <label>` | Pre-orders opening: 300 members order the open week's box at the same moment. Prints a summary and saves it to `results/burst-<label>.txt` |
| `./test.sh` | Runs the ordering tests |

## API

| Endpoint | |
|---|---|
| `GET /api/offers/?status=open` | Weekly box offers, with boxes left and pickup points |
| `GET /api/offers/<id>/` | One week's offer |
| `POST /api/offers/<id>/orders/` | `{"member": "HC-0042", "pickup_point": "MARKET"}` → 201 confirmed, 409 sold out or not open |
| `GET /api/offers/<id>/orders/list/` | The week's packing list |
