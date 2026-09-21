from rest_framework import serializers


class AvailabilityQuerySerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    date = serializers.DateField()
    
    
    
class AppointmentCreateSerializer(serializers.Serializer):
    service_id = serializers.IntegerField()
    staff_id = serializers.IntegerField()
    date = serializers.DateField()
    start_time = serializers.TimeField()