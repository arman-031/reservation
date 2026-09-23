from rest_framework import serializers

from .models import Appointment


class AvailabilityQuerySerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    date = serializers.DateField()


class AppointmentCreateSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    date = serializers.DateField()
    start_time = serializers.TimeField()


class AppointmentSerializer(serializers.ModelSerializer):
    service = serializers.CharField(
        source="service.name",
        read_only=True,
    )
    staff = serializers.CharField(
        source="staff.name",
        read_only=True,
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "service",
            "staff",
            "date",
            "start_time",
            "status",
            "created_at",
        )
        read_only_fields = fields