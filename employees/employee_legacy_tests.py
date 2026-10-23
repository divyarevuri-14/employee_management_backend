import csv
import tempfile
from datetime import date
from pathlib import Path

from django.test import TestCase

from employees.models import Employee
from employees.services.employee_csv_service import EmployeeCSVService


class EmployeeCSVServiceTestCase(TestCase):
    """
    Test cases for Employee CSV import service.
    """

    def create_csv(self, content):
        """
        Create a temporary CSV file for testing.
        """
        temp_file = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
            encoding="utf-8",
            newline="",
        )

        temp_file.write(content)
        temp_file.close()

        return temp_file.name

    def tearDown(self):
        """
        Clean up temporary CSV files.
        """
        for file_path in getattr(self, "_temp_files", []):
            path = Path(file_path)

            if path.exists():
                path.unlink()

        super().tearDown()

    def register_temp_file(self, file_path):
        """
        Register temporary file for cleanup.
        """
        if not hasattr(self, "_temp_files"):
            self._temp_files = []

        self._temp_files.append(file_path)

    # ---------------------------------------------------------
    # 1. Valid CSV
    # ---------------------------------------------------------

    def test_valid_csv_import(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST001,Ravi,Kumar,ravi_test@example.com,9876500001,IT,Developer,50000,2025-01-10
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["failed"], 0)

        employee = Employee.objects.get(
            employee_code="TEST001"
        )

        self.assertEqual(employee.first_name, "Ravi")
        self.assertEqual(employee.email, "ravi_test@example.com")
        self.assertEqual(employee.department, "IT")

    # ---------------------------------------------------------
    # 2. Empty CSV
    # ---------------------------------------------------------

    def test_empty_csv(self):
        csv_content = ""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["skipped"], 0)

        self.assertTrue(
            any(
                "Missing required columns" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 3. Missing headers
    # ---------------------------------------------------------

    def test_missing_headers(self):
        csv_content = """employee_code,first_name,last_name
TEST002,Ravi,Kumar
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["failed"], 0)

        self.assertTrue(
            any(
                "Missing required columns" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 4. Duplicate employee code
    # ---------------------------------------------------------

    def test_duplicate_employee_code(self):
        Employee.objects.create(
            employee_code="TEST003",
            first_name="Existing",
            last_name="Employee",
            email="existing@example.com",
            phone="9876500003",
            department="IT",
            designation="Developer",
            salary=50000,
            joining_date=date(2025, 1, 1),
        )

        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST003,Ravi,Kumar,ravi003@example.com,9876500004,IT,Developer,50000,2025-01-10
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(result["failed"], 0)

        self.assertTrue(
            any(
                "duplicate employee_code" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 5. Duplicate email
    # ---------------------------------------------------------

    def test_duplicate_email(self):
        Employee.objects.create(
            employee_code="TEST004",
            first_name="Existing",
            last_name="Employee",
            email="duplicate@example.com",
            phone="9876500004",
            department="HR",
            designation="HR Executive",
            salary=45000,
            joining_date=date(2025, 1, 1),
        )

        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST005,Sita,Reddy,duplicate@example.com,9876500005,HR,HR Executive,45000,2025-02-15
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(result["failed"], 0)

        self.assertTrue(
            any(
                "duplicate email" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 6. Invalid email
    # ---------------------------------------------------------

    def test_invalid_email(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST006,Arjun,Varma,invalid-email,9876500006,Finance,Analyst,55000,2025-03-20
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertTrue(
            any(
                "invalid email" in error
                for error in result["errors"]
            )
        )

        self.assertFalse(
            Employee.objects.filter(
                employee_code="TEST006"
            ).exists()
        )

    # ---------------------------------------------------------
    # 7. Invalid salary
    # ---------------------------------------------------------

    def test_invalid_salary(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST007,John,Smith,john007@example.com,9876500007,IT,Developer,abc,2025-04-10
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertTrue(
            any(
                "invalid salary" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 8. Negative salary
    # ---------------------------------------------------------

    def test_negative_salary(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST008,John,Smith,john008@example.com,9876500008,IT,Developer,-5000,2025-04-10
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertTrue(
            any(
                "salary cannot be negative" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 9. Invalid joining date
    # ---------------------------------------------------------

    def test_invalid_joining_date(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST009,John,Smith,john009@example.com,9876500009,IT,Developer,50000,10-04-2025
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertTrue(
            any(
                "invalid joining_date" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 10. Malformed row
    # ---------------------------------------------------------

    def test_malformed_row(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST010,Ravi
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertTrue(
            any(
                "last_name is required" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 11. Repeat execution
    # ---------------------------------------------------------

    def test_repeat_execution(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST011,Ravi,Kumar,ravi011@example.com,9876500011,IT,Developer,50000,2025-01-10
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        first_result = EmployeeCSVService.import_csv(
            file_path
        )

        second_result = EmployeeCSVService.import_csv(
            file_path
        )

        self.assertEqual(
            first_result["successful"],
            1,
        )

        self.assertEqual(
            second_result["successful"],
            0,
        )

        self.assertEqual(
            second_result["skipped"],
            1,
        )

        self.assertEqual(
            Employee.objects.filter(
                employee_code="TEST011"
            ).count(),
            1,
        )

    # ---------------------------------------------------------
    # 12. File not found
    # ---------------------------------------------------------

    def test_file_not_found(self):
        file_path = "file_that_does_not_exist.csv"

        result = EmployeeCSVService.import_csv(
            file_path
        )

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["skipped"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertTrue(
            any(
                "File not found" in error
                for error in result["errors"]
            )
        )

    # ---------------------------------------------------------
    # 13. Extra columns / malformed CSV
    # ---------------------------------------------------------

    def test_extra_columns(self):
        csv_content = """employee_code,first_name,last_name,email,phone,department,designation,salary,joining_date
TEST012,Ravi,Kumar,ravi012@example.com,9876500012,IT,Developer,50000,2025-01-10,EXTRA
"""

        file_path = self.create_csv(csv_content)
        self.register_temp_file(file_path)

        result = EmployeeCSVService.import_csv(file_path)

        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)

        self.assertTrue(
            any(
                "extra columns detected" in error
                for error in result["errors"]
            )
        )