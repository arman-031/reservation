from rest_framework import serializers

from services.models import Service
from .models import Staff, WorkingHours


class StaffSerializer(serializers.ModelSerializer):
    service_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Staff
        fields = (
            "id",
            "name",
            "phone",
            "is_active",
            "service_ids",
        )

    def validate_service_ids(self, value):
        business = self.context["business"]

        services = Service.objects.filter(
            id__in=value,
            business=business,
        )

        if services.count() != len(value):
            raise serializers.ValidationError(
                "One or more services are invalid."
            )

        return value

    def create(self, validated_data):
        service_ids = validated_data.pop("service_ids", None)

        staff = Staff.objects.create(
            **validated_data,
        )

        if service_ids is not None:
            staff.services.set(service_ids)

        return staff

    def update(self, instance, validated_data):
        service_ids = validated_data.pop("service_ids", None)

        instance = super().update(
            instance,
            validated_data,
        )

        if service_ids is not None:
            instance.services.set(service_ids)

        return instance


    class WorkingHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHours
        fields = (
            "id",
            "day_of_week",
            "opening_time",
            "closing_time",
            "is_closed",
        )

    def validate(self, attrs):
        is_closed = attrs.get(
            "is_closed",
            self.instance.is_closed if self.instance else False,
        )
        opening_time = attrs.get(
            "opening_time",
            self.instance.opening_time if self.instance else None,
        )
        closing_time = attrs.get(
            "closing_time",
            self.instance.closing_time if self.instance else None,
        )

        if is_closed:
            return attrs

        if opening_time is None or closing_time is None:
            raise serializers.ValidationError(
                "Opening and closing times are required when the business is open."
            )

        if opening_time >= closing_time:
            raise serializers.ValidationError(
                "Opening time must be before closing time."
            )

        return attrs