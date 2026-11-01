from django.urls import path

from . import views

urlpatterns = [
    path("offers/", views.BoxOfferList.as_view()),
    path("offers/<int:pk>/", views.BoxOfferDetail.as_view()),
]
