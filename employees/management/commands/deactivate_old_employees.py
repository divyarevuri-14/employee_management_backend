from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from employees.models import Employee


class Command(BaseCommand):
    help = "Deactivate employees whose joining date is more than 2 years old"

    def handle(self, *args, **options):
        cutoff_date = date.today() - relativedelta(years=2)

        employees = Employee.objects.filter(
            joining_date__lt=cutoff_date,
            is_active=True,
        )

        count = employees.update(is_active=False)

        self.stdout.write(
            self.style.SUCCESS(
                f"Deactivated {count} old employee(s). "
                f"Rule: joining date before {cutoff_date}."
            )
        )