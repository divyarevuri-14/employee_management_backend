import csv

from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = "Export employee records to a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            required=True,
            help="Output CSV file path",
        )

    def handle(self, *args, **options):
        output_file = options["output"]

        employees = Employee.objects.all().order_by("employee_code")

        fieldnames = [
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "phone",
            "department",
            "designation",
            "salary",
            "joining_date",
            "is_active",
        ]

        with open(
            output_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.DictWriter(
                csv_file,
                fieldnames=fieldnames,
            )

            writer.writeheader()

            for employee in employees:
                writer.writerow(
                    {
                        "employee_code": employee.employee_code,
                        "first_name": employee.first_name,
                        "last_name": employee.last_name,
                        "email": employee.email,
                        "phone": employee.phone,
                        "department": employee.department,
                        "designation": employee.designation,
                        "salary": employee.salary,
                        "joining_date": employee.joining_date,
                        "is_active": employee.is_active,
                    }
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully exported {employees.count()} "
                f"employee(s) to {output_file}"
            )
        )