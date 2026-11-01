import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from boxes.models import BoxOffer, PickupPoint
from orders.models import Member, Order

FIRST = ["Ana", "Ben", "Chloe", "Dev", "Ella", "Farid", "Grace", "Hugo", "Ines", "Jonah", "Kira", "Liam",
         "Maya", "Nico", "Olive", "Priya", "Quinn", "Rosa", "Sami", "Tess", "Umar", "Vera", "Wes", "Yara", "Zane"]
LAST = ["Abbott", "Brook", "Castillo", "Dunn", "Ellis", "Fenwick", "Garza", "Holt", "Iyer", "Jensen",
        "Kowal", "Lindqvist", "Moreau", "Nakamura", "Okafor", "Patel", "Reyes", "Silva", "Tran", "Vance"]

PICKUP_POINTS = [
    ("FARM", "Farm gate shop", "Friday"),
    ("MARKET", "Saturday farmers' market stall", "Saturday"),
    ("LIBRARY", "Eastside library lobby", "Friday"),
]

WEEKS = [
    ("2026-W40", "Early autumn box", "Carrots, kale, beetroot, apples, potatoes, onions, a bunch of parsley", "closed"),
    ("2026-W41", "Harvest box", "Squash, leeks, potatoes, pears, spinach, garlic, a bunch of thyme", "closed"),
    ("2026-W42", "Root box", "Parsnips, carrots, celeriac, red onions, apples, cavolo nero", "closed"),
    ("2026-W43", "Squash and greens box", "Butternut squash, chard, potatoes, shallots, pears, rocket", "closed"),
    ("2026-W44", "Late autumn box", "Leeks, beetroot, savoy cabbage, potatoes, apples, a bunch of sage", "closed"),
    ("2026-W45", "First frost box", "Brussels sprouts, carrots, kale, potatoes, onions, pears, a bunch of rosemary", "open"),
    ("2026-W46", "Winter roots box", "Swede, parsnips, red cabbage, potatoes, garlic, apples", "upcoming"),
]


class Command(BaseCommand):
    help = "Reset the database to the sample members, weekly offers and past orders."

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(45)
        with connection.cursor() as cursor:
            cursor.execute(
                "TRUNCATE orders_order, orders_member, boxes_boxoffer_pickup_points, boxes_boxoffer, "
                "boxes_pickuppoint RESTART IDENTITY CASCADE"
            )

        points = [PickupPoint.objects.create(code=c, name=n, pickup_day=d) for c, n, d in PICKUP_POINTS]

        members = Member.objects.bulk_create([
            Member(
                number=f"HC-{i:04d}",
                name=f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                joined_on=date(2023, 3, 1) + timedelta(days=rng.randrange(1300)),
            )
            for i in range(1, 421)
        ])

        for week, name, contents, status in WEEKS:
            offer = BoxOffer.objects.create(
                week=week, name=name, contents=contents, price=Decimal("28.00"),
                boxes_total=100, boxes_left=100, status=status,
            )
            offer.pickup_points.set(points)
            if status == "closed":
                sold = rng.randint(94, 100)
                buyers = rng.sample(members, sold)
                Order.objects.bulk_create([Order(offer=offer, member=m, pickup_point=rng.choice(points)) for m in buyers])
                offer.boxes_left = 100 - sold
                offer.save(update_fields=["boxes_left"])

        self.stdout.write(f"Loaded {len(points)} pickup points, {len(members)} members, {len(WEEKS)} weekly offers "
                          f"and {Order.objects.count()} past orders.")
