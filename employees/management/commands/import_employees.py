from django.core.management.base import BaseCommand

from employees.services.employee_csv_service import (
    EmployeeCSVService,
)


class Command(BaseCommand):
    help = "Import employees from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument(
            "file",
            type=str,
            help="Path to the CSV file",
        )

    def handle(self, *args, **options):
        file_path = options["file"]

        result = EmployeeCSVService.import_csv(
            file_path
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Successful: {result['successful']}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Skipped: {result['skipped']}"
            )
        )

        self.stdout.write(
            self.style.ERROR(
                f"Failed: {result['failed']}"
            )
        )

        if result["errors"]:
            self.stdout.write("\nDetails:")

            for error in result["errors"]:
                self.stdout.write(
                    f"- {error}"
                )