from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from businesses.models import Business
from .models import Service
from .permissions import IsBusinessOwner
from .serializers import ServiceSerializer


class ServiceListAPIView(APIView):
    def get(self, request, business_id):
        services = Service.objects.filter(
            business_id=business_id
        )

        serializer = ServiceSerializer(
            services,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request, business_id):
        self.permission_classes = [IsBusinessOwner]
        self.check_permissions(request)

        business = get_object_or_404(
            Business,
            id=business_id,
            owner=request.user,
        )

        serializer = ServiceSerializer(
            data=request.data,
            context={"business": business},
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=201,
            )

        return Response(
            serializer.errors,
            status=400,
        )