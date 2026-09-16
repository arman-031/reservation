from rest_framework import serializers

from services.models import Service
from .models import Staff


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