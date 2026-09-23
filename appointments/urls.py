from django.urls import path

from .views import (
    AppointmentCancelAPIView,
    AppointmentCreateAPIView,
    AppointmentListAPIView,
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
    path(
        "api/appointments/list/",
        AppointmentListAPIView.as_view(),
        name="appointment-list",
    ),
    path(
    "api/appointments/<int:appointment_id>/cancel/",
    AppointmentCancelAPIView.as_view(),
    name="appointment-cancel",
    ),
]