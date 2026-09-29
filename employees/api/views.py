from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from employees.models import Employee, EmployeeTransfer
from employees.serializers import (
    EmployeeSerializer,
    EmployeeTransferSerializer,
)
from employees.services.employee_transfer_service import (
    EmployeeTransferService,
)


class EmployeeListCreateAPIView(ListCreateAPIView):
    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer


class EmployeeDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "id"


class EmployeeDetailsView(APIView):

    def get(self, request):

        # Optimized queryset:
        # select_related() for ForeignKey and OneToOne
        # prefetch_related() for ManyToMany
        employees = Employee.objects.select_related(
            "department_fk",
            "profile"
        ).prefetch_related(
            "projects"
        )

        data = []

        for employee in employees:

            employee_data = {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "first_name": employee.first_name,
                "last_name": employee.last_name,

                "department": (
                    employee.department_fk.name
                    if employee.department_fk
                    else None
                ),

                "profile": (
                    {
                        "date_of_birth": (
                            str(employee.profile.date_of_birth)
                            if employee.profile.date_of_birth
                            else None
                        ),
                        "address": employee.profile.address,
                        "emergency_contact": employee.profile.emergency_contact,
                        "blood_group": employee.profile.blood_group,
                    }
                    if hasattr(employee, "profile")
                    else None
                ),

                "projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "project_code": project.project_code,
                    }
                    for project in employee.projects.all()
                ],
            }

            data.append(employee_data)

        return Response(data)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer


class EmployeeTransferView(APIView):

    def post(self, request, employee_id):

        # Get data from request body
        to_department = request.data.get("to_department")
        reason = request.data.get("reason")

        # Validate target department
        if not to_department:
            return Response(
                {
                    "error": "to_department is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate reason
        if not reason or not reason.strip():
            return Response(
                {
                    "error": "Transfer reason is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            # Call transfer service
            transfer = EmployeeTransferService.transfer_employee(
                employee_id=employee_id,
                to_department_id=to_department,
                reason=reason,
                transferred_by=request.user
            )

            # Serialize transfer record
            serializer = EmployeeTransferSerializer(transfer)

            return Response(
                {
                    "message": "Employee transferred successfully.",
                    "transfer": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return Response(
                {
                    "error": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmployeeTransferHistoryView(APIView):

    def get(self, request, employee_id):

        transfers = (
            EmployeeTransfer.objects
            .filter(employee_id=employee_id)
            .select_related(
                "employee",
                "from_department",
                "to_department",
                "transferred_by",
            )
            .order_by("-transferred_at")
        )

        serializer = EmployeeTransferSerializer(
            transfers,
            many=True
        )

        return Response(serializer.data)