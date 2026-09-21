from django.urls import path

from .views import AvailabilityAPIView
from .views import (
    AppointmentCreateAPIView,
    AvailabilityAPIView,
)

urlpatterns = [
    path(
        "api/businesses/<int:business_id>/available-slots/",
        AvailabilityAPIView.as_view(),
        name="available-slots",
    ),
    path(
        "api/appointments/",
        AppointmentCreateAPIView.as_view(),
        name="appointment-create",
    ),
]