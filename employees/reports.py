from django.db.models import Count, Avg, Max, Sum, Min
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Employee, Department, Project


class DepartmentSummaryView(APIView):

    def get(self, request):
        departments = Department.objects.annotate(
            employee_count=Count("employees"),
            average_salary=Avg("employees__salary"),
            maximum_salary=Max("employees__salary")
        )

        data = []

        for department in departments:
            data.append({
                "department": department.name,
                "employee_count": department.employee_count,
                "average_salary": department.average_salary,
                "maximum_salary": department.maximum_salary
            })

        return Response(data)


class ProjectSummaryView(APIView):

    def get(self, request):
        projects = Project.objects.annotate(
            employee_count=Count(
                "employees",
                distinct=True
            )
        )

        data = []

        for project in projects:
            data.append({
                "project": project.name,
                "employee_count": project.employee_count
            })

        return Response(data)


class SalarySummaryView(APIView):

    def get(self, request):

        summary = Employee.objects.aggregate(
            total_employees=Count("id"),
            average_salary=Avg("salary"),
            maximum_salary=Max("salary"),
            minimum_salary=Min("salary"),
            total_salary_expenditure=Sum("salary")
        )

        return Response(summary)