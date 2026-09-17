
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Employee


class EmployeeViewSetTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.active_employee = Employee.objects.create(
            employee_code="TEST001",
            first_name="Divya",
            last_name="Test",
            email="divya_test@example.com",
            department="Backend",
            designation="Python Developer",
            salary=Decimal("80000.00"),
            joining_date="2024-01-01",
            is_active=True,
        )

        cls.inactive_employee = Employee.objects.create(
            employee_code="TEST002",
            first_name="Ravi",
            last_name="Test",
            email="ravi_test@example.com",
            department="HR",
            designation="HR Executive",
            salary=Decimal("40000.00"),
            joining_date="2024-02-01",
            is_active=False,
        )

    def test_active_endpoint_returns_only_active_employees(self):
        response = self.client.get(
            "/api/v1/employees/active/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            all(
                employee["is_active"] is True
                for employee in response.data
            )
        )

    def test_department_filter(self):
        response = self.client.get(
            "/api/v1/employees/",
            {"department": "Backend"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            all(
                employee["department"] == "Backend"
                for employee in response.data
            )
        )

    def test_search_by_first_name(self):
        response = self.client.get(
            "/api/v1/employees/",
            {"search": "Divya"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(
            any(
                employee["first_name"] == "Divya"
                for employee in response.data
            )
        )

    def test_ordering_by_salary_descending(self):
        response = self.client.get(
            "/api/v1/employees/",
            {"ordering": "-salary"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        salaries = [
            Decimal(str(employee["salary"]))
            for employee in response.data
        ]

        self.assertEqual(salaries, sorted(salaries, reverse=True))