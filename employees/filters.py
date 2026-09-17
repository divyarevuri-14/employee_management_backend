
import django_filters

from .models import Employee


class EmployeeFilter(django_filters.FilterSet):
    min_salary = django_filters.NumberFilter(
        field_name="salary",
        lookup_expr="gte"
    )

    max_salary = django_filters.NumberFilter(
        field_name="salary",
        lookup_expr="lte"
    )

    class Meta:
        model = Employee
        fields = [
            "department",
            "is_active",
            "salary",
        ]