import logging

from rest_framework import viewsets, status
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated

from employees.models import Employee, EmployeeTransfer
from employees.serializers import (
    EmployeeSerializer,
    EmployeeTransferSerializer,
)
from employees.services.employee_transfer_service import (
    EmployeeTransferService,
)
from employees.services.cache_service import (
    invalidate_department_employee_summary,
)

from employees.permissions import (
    IsAdmin,
    IsAdminOrHR,
    IsAdminHROrManager,
)

logger = logging.getLogger("employees")


# ============================================================
# EMPLOYEE LIST + CREATE
# ============================================================

class EmployeeListCreateAPIView(ListCreateAPIView):

    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAdminHROrManager()]

        if self.request.method == "POST":
            return [IsAdminOrHR()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):

        serializer.save()
        invalidate_department_employee_summary()


# ============================================================
# EMPLOYEE DETAIL
# ============================================================

class EmployeeDetailAPIView(RetrieveUpdateDestroyAPIView):

    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = "id"

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAdminHROrManager()]

        if self.request.method in ["PUT", "PATCH"]:
            return [IsAdminOrHR()]

        if self.request.method == "DELETE":
            return [IsAdmin()]

        return [IsAuthenticated()]

    def perform_update(self, serializer):

        serializer.save()
        invalidate_department_employee_summary()

    def perform_destroy(self, instance):

        instance.delete()
        invalidate_department_employee_summary()


# ============================================================
# EMPLOYEE DETAILS / QUERY OPTIMIZATION API
# ============================================================

class EmployeeDetailsView(APIView):

    permission_classes = [IsAdminHROrManager]

    def get(self, request):

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
                        "emergency_contact": (
                            employee.profile.emergency_contact
                        ),
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


# ============================================================
# EMPLOYEE VIEWSET
# ============================================================

class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all().order_by("id")
    serializer_class = EmployeeSerializer

    def get_permissions(self):

        if self.action in ["list", "retrieve"]:
            return [IsAdminHROrManager()]

        if self.action == "create":
            return [IsAdminOrHR()]

        if self.action in ["update", "partial_update"]:
            return [IsAdminOrHR()]

        if self.action == "destroy":
            return [IsAdmin()]

        return [IsAuthenticated()]

    def perform_create(self, serializer):

        serializer.save()
        invalidate_department_employee_summary()

    def perform_update(self, serializer):

        serializer.save()
        invalidate_department_employee_summary()

    def perform_destroy(self, instance):

        instance.delete()
        invalidate_department_employee_summary()


# ============================================================
# EMPLOYEE TRANSFER
# ============================================================

class EmployeeTransferView(APIView):

    permission_classes = [IsAdminOrHR]

    def post(self, request, employee_id):

        to_department = request.data.get("to_department")
        reason = request.data.get("reason")

        if not to_department:
            return Response(
                {"error": "to_department is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not reason or not reason.strip():
            return Response(
                {"error": "Transfer reason is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            transfer = EmployeeTransferService.transfer_employee(
                employee_id=employee_id,
                to_department_id=to_department,
                reason=reason,
                transferred_by=request.user
            )

            # Invalidate summary after successful transfer
            invalidate_department_employee_summary()

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
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            logger.exception("Employee transfer failed")

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ============================================================
# EMPLOYEE TRANSFER HISTORY
# ============================================================

class EmployeeTransferHistoryView(APIView):

    permission_classes = [IsAdminHROrManager]

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


# ============================================================
# MY PROFILE
# ============================================================

class MyProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        if not hasattr(user, "profile"):
            return Response(
                {"error": "User profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.profile.role,
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# HEALTH CHECK
# ============================================================

def health_check(request):

    return JsonResponse({
        "status": "ok"
    })