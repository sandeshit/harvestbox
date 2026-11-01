from django.urls import include, path

urlpatterns = [
    path("api/", include("boxes.urls")),
    path("api/", include("orders.urls")),
]
