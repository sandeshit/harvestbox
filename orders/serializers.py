from rest_framework import serializers

from .models import Order


class PlaceOrderSerializer(serializers.Serializer):
    member = serializers.CharField()
    pickup_point = serializers.CharField()


class OrderSerializer(serializers.ModelSerializer):
    week = serializers.CharField(source="offer.week")
    member = serializers.CharField(source="member.number")
    pickup_point = serializers.CharField(source="pickup_point.code")

    class Meta:
        model = Order
        fields = ["id", "week", "member", "pickup_point", "created_at"]
