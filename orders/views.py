from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from boxes.models import BoxOffer

from .models import Member, Order
from .serializers import OrderSerializer, PlaceOrderSerializer


@api_view(["POST"])
def place_order(request, offer_id):
    """POST /api/offers/<id>/orders/  {"member": "HC-0042", "pickup_point": "MARKET"}"""
    data = PlaceOrderSerializer(data=request.data)
    data.is_valid(raise_exception=True)
    member = get_object_or_404(Member, number=data.validated_data["member"])

    offer = get_object_or_404(BoxOffer, pk=offer_id)
    if not offer.is_open():
        return Response({"detail": "Pre-orders for this week are not open."}, status=409)
    pickup_point = get_object_or_404(offer.pickup_points, code=data.validated_data["pickup_point"])
    if offer.boxes_left < 1:
        return Response({"detail": "Sold out for this week."}, status=409)

    offer.boxes_left -= 1
    offer.save(update_fields=["boxes_left"])
    order = Order.objects.create(offer=offer, member=member, pickup_point=pickup_point)
    return Response(OrderSerializer(order).data, status=201)


class OfferOrders(ListAPIView):
    """GET /api/offers/<id>/orders/list/  the packing list for one week"""

    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(offer_id=self.kwargs["offer_id"]).select_related("offer", "member", "pickup_point")
