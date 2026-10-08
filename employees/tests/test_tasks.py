from unittest.mock import patch

from django.test import TestCase

from employees.models import Employee
from employees.tasks import (
    send_welcome_email,
    generate_employee_report,
    process_employee_csv,
)


class CeleryTaskTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.employee = Employee.objects.create(
            employee_code="TEST001",
            first_name="Test",
            last_name="Employee",
            email="test@example.com",
            phone="9876543210",
            department="IT",
            designation="Developer",
            salary=50000,
            joining_date="2026-10-08",
            is_active=True,
        )

    # ========================================================
    # WELCOME EMAIL TASK
    # ========================================================

    @patch("employees.tasks.send_mail")
    def test_send_welcome_email(self, mock_send_mail):
        result = send_welcome_email.apply(
            args=[self.employee.id]
        ).get()

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["employee_id"],
            self.employee.id,
        )

        mock_send_mail.assert_called_once()

    # ========================================================
    # EMPLOYEE REPORT TASK
    # ========================================================

    @patch("employees.tasks.time.sleep")
    def test_generate_employee_report(self, mock_sleep):
        result = generate_employee_report.apply().get()

        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(
            result["employee_count"],
            1,
        )

    # ========================================================
    # CSV PROCESSING TASK
    # ========================================================

    @patch("employees.tasks.time.sleep")
    def test_process_employee_csv(self, mock_sleep):
        file_path = "employees.csv"

        result = process_employee_csv.apply(
            args=[file_path]
        ).get()

        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["file_path"],
            file_path,
        )