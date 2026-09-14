from rest_framework import serializers

from .models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "duration",
            "price",
            "is_active",
        )

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Duration must be greater than zero."
            )

        return value

    def create(self, validated_data):
        business = self.context["business"]

        return Service.objects.create(
            business=business,
            **validated_data,
        )