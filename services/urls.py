from django.contrib import admin
from django.urls import path
from services.views import ServiceListAPIView

from services.views import (
    ServiceDetailAPIView,
    ServiceListAPIView,
)


urlpatterns = [
   path(
    "api/businesses/<int:business_id>/services/",
    ServiceListAPIView.as_view(),
),
path(
    "api/businesses/<int:business_id>/services/<int:service_id>/",
    ServiceDetailAPIView.as_view(),
),
]