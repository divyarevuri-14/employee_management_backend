from django.db.models import Q
from employees.models import Employee

backend_or_data = Employee.objects.filter(
    Q(department_fk__name="Backend") |
    Q(department_fk__name="Data")
)