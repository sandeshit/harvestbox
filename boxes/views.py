from rest_framework import generics

from .models import BoxOffer
from .serializers import BoxOfferSerializer


class BoxOfferList(generics.ListAPIView):
    """GET /api/offers/?status=open"""

    serializer_class = BoxOfferSerializer

    def get_queryset(self):
        offers = BoxOffer.objects.prefetch_related("pickup_points")
        status = self.request.query_params.get("status")
        return offers.filter(status=status) if status else offers


class BoxOfferDetail(generics.RetrieveAPIView):
    """GET /api/offers/<id>/"""

    queryset = BoxOffer.objects.prefetch_related("pickup_points")
    serializer_class = BoxOfferSerializer
