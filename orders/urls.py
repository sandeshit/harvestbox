from django.urls import path

from . import views

urlpatterns = [
    path("offers/<int:offer_id>/orders/", views.place_order),
    path("offers/<int:offer_id>/orders/list/", views.OfferOrders.as_view()),
]
