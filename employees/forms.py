from django import forms
from .models import Employee


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
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

    def clean_employee_code(self):
        employee_code = self.cleaned_data["employee_code"].strip()

        if not employee_code:
            raise forms.ValidationError(
                "Employee code is required."
            )

        queryset = Employee.objects.filter(
            employee_code__iexact=employee_code
        )

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Employee code already exists."
            )

        return employee_code

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if not email:
            raise forms.ValidationError(
                "Email is required."
            )

        queryset = Employee.objects.filter(
            email__iexact=email
        )

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError(
                "Email already exists."
            )

        return email

    def clean_salary(self):
        salary = self.cleaned_data["salary"]

        if salary < 0:
            raise forms.ValidationError(
                "Salary cannot be negative."
            )

        return salary