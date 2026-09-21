from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from businesses.models import Business, Staff
from services.models import Service

from .serializers import (
    AppointmentCreateSerializer,
    AvailabilityQuerySerializer,
)
from .services import (
    calculate_end_time,
    create_appointment,
    generate_slots,
    has_conflicting_appointment,
)


class AvailabilityAPIView(APIView):
    def get(self, request, business_id):
        serializer = AvailabilityQuerySerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        service_id = serializer.validated_data["service_id"]
        staff_id = serializer.validated_data["staff_id"]
        appointment_date = serializer.validated_data["date"]

        business = get_object_or_404(
            Business,
            id=business_id,
        )

        service = get_object_or_404(
            Service,
            id=service_id,
            business=business,
            is_active=True,
        )

        staff = get_object_or_404(
            Staff,
            id=staff_id,
            business=business,
            is_active=True,
        )

        if not staff.services.filter(id=service.id).exists():
            return Response(
                {
                    "detail": "Staff cannot perform this service.",
                },
                status=400,
            )

        working_hours = business.working_hours.filter(
            day_of_week=appointment_date.weekday(),
        ).first()

        if (
            working_hours is None
            or working_hours.is_closed
            or not working_hours.opening_time
            or not working_hours.closing_time
        ):
            return Response(
                {
                    "date": appointment_date,
                    "service": service.name,
                    "staff": staff.name,
                    "available_slots": [],
                }
            )

        slots = generate_slots(
            opening_time=working_hours.opening_time,
            closing_time=working_hours.closing_time,
            duration_minutes=service.duration,
        )

        available_slots = []

        for slot in slots:
            end_time = calculate_end_time(
                slot,
                service.duration,
            )

            if not has_conflicting_appointment(
                staff=staff,
                appointment_date=appointment_date,
                start_time=slot,
                end_time=end_time,
            ):
                available_slots.append(slot)

        return Response(
            {
                "date": appointment_date,
                "service": service.name,
                "staff": staff.name,
                "available_slots": available_slots,
            }
        )


class AppointmentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AppointmentCreateSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        service = get_object_or_404(
            Service,
            id=serializer.validated_data["service_id"],
            is_active=True,
        )

        staff = get_object_or_404(
            Staff,
            id=serializer.validated_data["staff_id"],
            business_id=service.business_id,
            is_active=True,
        )

        try:
            appointment = create_appointment(
                customer=request.user,
                service=service,
                staff=staff,
                appointment_date=serializer.validated_data["date"],
                start_time=serializer.validated_data["start_time"],
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=400,
            )

        return Response(
            {
                "id": appointment.id,
                "service": appointment.service.name,
                "staff": appointment.staff.name,
                "date": appointment.date,
                "start_time": appointment.start_time,
                "status": appointment.status,
            },
            status=201,
        )