from django.db import models


class PickupPoint(models.Model):
    """Where members collect their box on pickup day."""

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    pickup_day = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class BoxOffer(models.Model):
    """One week's produce box. The farm packs a fixed number of boxes each week."""

    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        OPEN = "open", "Open for pre-orders"
        CLOSED = "closed", "Closed"

    week = models.CharField(max_length=10, unique=True)  # ISO week, e.g. 2026-W45
    name = models.CharField(max_length=100)
    contents = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    boxes_total = models.PositiveIntegerField()
    boxes_left = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UPCOMING)
    pickup_points = models.ManyToManyField(PickupPoint, related_name="offers")

    class Meta:
        ordering = ["-week"]

    def __str__(self):
        return f"{self.week} {self.name}"

    def is_open(self):
        return self.status == self.Status.OPEN
