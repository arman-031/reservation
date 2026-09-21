from django.shortcuts import get_object_or_404
    )


class WorkingHoursListAPIView(APIView):
from .models import Business, Staff, WorkingHours
from common.permissions import IsBusinessOwner
from .serializers import StaffSerializer, WorkingHoursSerializer


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
            context={"business": business},
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
            context={
                "business": staff.business,
            },
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
        
        

class WorkingHoursListAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsBusinessOwner()]

        return []

    def get(self, request, business_id):
        working_hours = WorkingHours.objects.filter(
            business_id=business_id,
        ).order_by("day_of_week")

        serializer = WorkingHoursSerializer(
            working_hours,
            many=True,
        )

        return Response(serializer.data)

    def post(self, request, business_id):
        business = get_object_or_404(
            Business,
            id=business_id,
            owner=request.user,
        )

        serializer = WorkingHoursSerializer(
            data=request.data,
        )

        if serializer.is_valid():
            day_of_week = serializer.validated_data["day_of_week"]

            if WorkingHours.objects.filter(
                business=business,
                day_of_week=day_of_week,
            ).exists():
                return Response(
                    {
                        "detail": "Working hours for this day already exist."
                    },
                    status=400,
                )

            working_hours = serializer.save(
                business=business,
            )

            return Response(
                WorkingHoursSerializer(working_hours).data,
                status=201,
            )

        return Response(
            serializer.errors,
            status=400,
        )



    class WorkingHoursDetailAPIView(APIView):
    permission_classes = [IsBusinessOwner]

    def patch(self, request, business_id, day_of_week):
        working_hours = get_object_or_404(
            WorkingHours,
            business_id=business_id,
            day_of_week=day_of_week,
            business__owner=request.user,
        )

        serializer = WorkingHoursSerializer(
            working_hours,
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