from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from boxes.models import BoxOffer


class Command(BaseCommand):
    help = "Clear the orders on the week that is open for pre-orders and put all its boxes back."

    @transaction.atomic
    def handle(self, *args, **options):
        offer = BoxOffer.objects.filter(status=BoxOffer.Status.OPEN).first()
        if offer is None:
            raise CommandError("No week is open for pre-orders.")
        deleted, _ = offer.orders.all().delete()
        offer.boxes_left = offer.boxes_total
        offer.save(update_fields=["boxes_left"])
        self.stdout.write(f"Reset {offer.week} \"{offer.name}\": removed {deleted} orders, "
                          f"{offer.boxes_left} of {offer.boxes_total} boxes available.")
