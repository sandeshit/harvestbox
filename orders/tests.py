import threading
from datetime import date

from django.db import connection
from django.test import Client, TransactionTestCase

from boxes.models import BoxOffer, PickupPoint
from orders.models import Member


class ParallelPreOrdersTest(TransactionTestCase):
    """Many members order at the same moment; the API must never confirm more boxes than exist."""

    BOXES = 3
    MEMBERS = 20

    def setUp(self):
        market = PickupPoint.objects.create(code="MARKET", name="Market stall", pickup_day="Saturday")
        self.offer = BoxOffer.objects.create(
            week="2026-W45", name="Test box", contents="Kale", price=28,
            boxes_total=self.BOXES, boxes_left=self.BOXES, status=BoxOffer.Status.OPEN,
        )
        self.offer.pickup_points.add(market)
        for i in range(self.MEMBERS):
            Member.objects.create(number=f"T-{i:04d}", name=f"Member {i}", joined_on=date(2026, 1, 1))

    def test_never_confirms_more_orders_than_boxes(self):
        start_together = threading.Barrier(self.MEMBERS)
        statuses = []

        def member_orders(i):
            start_together.wait()
            response = Client().post(
                f"/api/offers/{self.offer.pk}/orders/",
                {"member": f"T-{i:04d}", "pickup_point": "MARKET"},
                content_type="application/json",
            )
            statuses.append(response.status_code)
            connection.close()

        threads = [threading.Thread(target=member_orders, args=(i,)) for i in range(self.MEMBERS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.offer.refresh_from_db()
        self.assertEqual(statuses.count(201), self.BOXES)
        self.assertEqual(statuses.count(409), self.MEMBERS - self.BOXES)
        self.assertEqual(self.offer.orders.count(), self.BOXES)
        self.assertEqual(self.offer.boxes_left, 0)
