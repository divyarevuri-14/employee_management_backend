from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from employees.models import Employee
from employees.serializers import EmployeeSerializer


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