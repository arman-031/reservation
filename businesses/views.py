from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Business, Staff
from common.permissions import IsBusinessOwner
from .serializers import StaffSerializer


class StaffListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsBusinessOwner()]

        return []

    def get(self, request, business_id):
        staff_members = Staff.objects.filter(
            business_id=business_id,
            is_active=True,
        )

        serializer = StaffSerializer(
            staff_members,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request, business_id):
        business = get_object_or_404(
            Business,
            id=business_id,
            owner=request.user,
        )

        serializer = StaffSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            staff = serializer.save(
                business=business,
            )

            return Response(
                StaffSerializer(staff).data,
                status=201,
            )

        return Response(
            serializer.errors,
            status=400,
        )


class StaffDetailAPIView(APIView):
    permission_classes = [IsBusinessOwner]

    def patch(self, request, business_id, staff_id):
        staff = get_object_or_404(
            Staff,
            id=staff_id,
            business_id=business_id,
            business__owner=request.user,
        )

        serializer = StaffSerializer(
            staff,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
            )

        return Response(
            serializer.errors,
            status=400,
        )