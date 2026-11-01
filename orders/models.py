from django.db import models

from boxes.models import BoxOffer, PickupPoint


class Member(models.Model):
    """A co-op member who can pre-order boxes."""

    number = models.CharField(max_length=10, unique=True)  # e.g. HC-0042
    name = models.CharField(max_length=100)
    joined_on = models.DateField()

    def __str__(self):
        return self.number


class Order(models.Model):
    offer = models.ForeignKey(BoxOffer, on_delete=models.PROTECT, related_name="orders")
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="orders")
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.PROTECT, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Order {self.pk} ({self.offer.week}, {self.member.number})"
