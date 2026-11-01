"""Pre-orders opening: many members order the open week's box at the same moment.

Starts one thread per member, holds them all at a barrier, then releases every order at once
against the API, like the rush when the weekly email goes out. Prints a summary.
"""
import argparse
import json
import threading
import time
import urllib.error
import urllib.request
from collections import Counter

API = "http://api:8000/api"
PICKUP_POINTS = ["FARM", "MARKET", "LIBRARY"]


def get(path):
    with urllib.request.urlopen(f"{API}{path}", timeout=30) as response:
        return json.load(response)


def place(offer_id, member, pickup_point):
    body = json.dumps({"member": member, "pickup_point": pickup_point}).encode()
    request = urllib.request.Request(
        f"{API}/offers/{offer_id}/orders/", data=body, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except OSError as error:
        return type(error).__name__


def wait_for_api(seconds=20):
    """After `docker compose restart api` the workers take a moment to start."""
    for _ in range(seconds * 2):
        try:
            return get("/offers/?status=open")
        except OSError:
            time.sleep(0.5)
    raise SystemExit("The API is not answering. Is the stack running? (docker compose up -d)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--orders", type=int, default=300)
    args = parser.parse_args()

    offer = wait_for_api()[0]
    already = len(get(f"/offers/{offer['id']}/orders/list/"))
    if already or offer["boxes_left"] != offer["boxes_total"]:
        raise SystemExit(f"{offer['week']} already has {already} orders. Run ./reset-offer.sh first.")

    print(f"Week {offer['week']} \"{offer['name']}\": {offer['boxes_total']} boxes available")
    print(f"Sending {args.orders} pre-orders at the same moment, one per member ...")

    barrier = threading.Barrier(args.orders)
    results = []
    lock = threading.Lock()

    def member_orders(i):
        member, pickup = f"HC-{i:04d}", PICKUP_POINTS[i % 3]
        barrier.wait()
        status = place(offer["id"], member, pickup)
        with lock:
            results.append(status)

    threads = [threading.Thread(target=member_orders, args=(i,)) for i in range(1, args.orders + 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    codes = Counter(results)
    offer = get(f"/offers/{offer['id']}/")
    in_db = len(get(f"/offers/{offer['id']}/orders/list/"))
    other = sum(n for code, n in codes.items() if code not in (201, 409))

    print()
    print(f"Confirmed (201)            {codes[201]:>4}")
    print(f"Refused, sold out (409)    {codes[409]:>4}")
    print(f"Errors                     {other:>4}")
    print(f"Orders in the database     {in_db:>4}")
    print(f"Boxes packed this week     {offer['boxes_total']:>4}")
    print(f"Boxes left on the offer    {offer['boxes_left']:>4}")
    print()
    if in_db > offer["boxes_total"]:
        print(f"OVERSOLD - {in_db - offer['boxes_total']} confirmed orders have no box")
    elif other:
        print(f"FAILED - {other} orders got an error instead of an answer")
    elif in_db + offer["boxes_left"] != offer["boxes_total"]:
        print("MISMATCH - orders and boxes left don't add up to the boxes packed")
    else:
        print(f"OK - {in_db} orders for {offer['boxes_total']} boxes, every other member was told it's sold out")


if __name__ == "__main__":
    main()
