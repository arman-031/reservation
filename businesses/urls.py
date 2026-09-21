from django.urls import path

from .views import (
    StaffDetailAPIView,
    StaffListAPIView,
    WorkingHoursDetailAPIView,
    WorkingHoursListAPIView,
)

urlpatterns = [
    path(
        "api/businesses/<int:business_id>/staff/",
        StaffListAPIView.as_view(),
    ),
    path(
        "api/businesses/<int:business_id>/staff/<int:staff_id>/",
        StaffDetailAPIView.as_view(),
    ),
    path(
        "api/businesses/<int:business_id>/working-hours/",
        WorkingHoursListAPIView.as_view(),
    ),
    path(
        "api/businesses/<int:business_id>/working-hours/<int:day_of_week>/",
        WorkingHoursDetailAPIView.as_view(),
    ),
]