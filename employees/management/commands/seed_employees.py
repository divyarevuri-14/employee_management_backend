from django.core.management.base import BaseCommand
from employees.models import Employee


class Command(BaseCommand):
    help = "Seed sample employee records into the database"

    def handle(self, *args, **options):
        employees = [
            {
                "employee_code": "EMP001",
                "first_name": "Ravi",
                "last_name": "Kumar",
                "email": "ravi.kumar@example.com",
                "phone": "9876543210",
                "department": "IT",
                "designation": "Software Engineer",
                "salary": 50000,
                "joining_date": "2025-01-10",
            },
            {
                "employee_code": "EMP002",
                "first_name": "Sita",
                "last_name": "Reddy",
                "email": "sita.reddy@example.com",
                "phone": "9876543211",
                "department": "HR",
                "designation": "HR Executive",
                "salary": 45000,
                "joining_date": "2025-03-15",
            },
            {
                "employee_code": "EMP003",
                "first_name": "Arjun",
                "last_name": "Varma",
                "email": "arjun.varma@example.com",
                "phone": "9876543212",
                "department": "Finance",
                "designation": "Financial Analyst",
                "salary": 55000,
                "joining_date": "2024-06-20",
            },
        ]

        created_count = 0
        skipped_count = 0

        for employee_data in employees:
            employee, created = Employee.objects.get_or_create(
                employee_code=employee_data["employee_code"],
                defaults=employee_data,
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created employee: {employee.employee_code}"
                    )
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipped employee: {employee.employee_code} already exists"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding completed. Created: {created_count}, "
                f"Skipped: {skipped_count}"
            )
        )