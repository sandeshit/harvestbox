from rest_framework import serializers

from .models import BoxOffer, PickupPoint


class PickupPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupPoint
        fields = ["code", "name", "pickup_day"]


class BoxOfferSerializer(serializers.ModelSerializer):
    pickup_points = PickupPointSerializer(many=True, read_only=True)

    class Meta:
        model = BoxOffer
        fields = ["id", "week", "name", "contents", "price", "boxes_total", "boxes_left", "status", "pickup_points"]
