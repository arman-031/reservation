from django.contrib import admin
from django.urls import path
from services.views import ServiceListAPIView


urlpatterns = [
   path(
    "api/businesses/<int:business_id>/services/",
    ServiceListAPIView.as_view(),
),
]