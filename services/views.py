from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from businesses.models import Business
from .models import Service
from common.permissions import IsBusinessOwner
from .serializers import ServiceSerializer


class ServiceListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsBusinessOwner()]

        return []

    def get(self, request, business_id):
        services = Service.objects.filter(
            business_id=business_id,
            is_active=True,
        )
        serializer = ServiceSerializer(services, many=True)

        return Response(serializer.data)

    def post(self, request, business_id):
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


class ServiceDetailAPIView(APIView):
    permission_classes = [IsBusinessOwner]

    def patch(self, request, business_id, service_id):
        service = get_object_or_404(
            Service,
            id=service_id,
            business_id=business_id,
            business__owner=request.user,
        )

        serializer = ServiceSerializer(
            service,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=400,
        )