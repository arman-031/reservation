from django.urls import path

from .views import (
    StaffDetailAPIView,
    StaffListAPIView,
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
]