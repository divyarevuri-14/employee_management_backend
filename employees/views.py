from rest_framework import viewsets
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all().order_by("id")

    serializer_class = EmployeeSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department",
        "designation",
    ]

    ordering_fields = [
        "id",
        "first_name",
        "salary",
        "joining_date",
        "created_at",
    ]

    ordering = [
        "id",
    ]

    @action(
        detail=False,
        methods=["get"],
        url_path="active"
    )
    def active_employees(self, request):

        active_employees = self.get_queryset().filter(
            is_active=True
        )

        serializer = self.get_serializer(
            active_employees,
            many=True
        )

        return Response(serializer.data)