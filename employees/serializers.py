from rest_framework import serializers

from employees.models import (
    Employee,
    EmployeeTransfer,
    Notification,
)


# ============================================================
# EMPLOYEE SERIALIZER
# ============================================================

class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee

        fields = [
            "id",
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
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_employee_code(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Employee code cannot be empty."
            )

        return value

    def validate_email(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Email cannot be empty."
            )

        return value

    def validate_phone(self, value):
        value = value.strip()

        if not value.isdigit():
            raise serializers.ValidationError(
                "Phone must contain only digits."
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                "Phone must contain exactly 10 digits."
            )

        return value

    def validate_salary(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Salary cannot be negative."
            )

        return value


# ============================================================
# EMPLOYEE TRANSFER SERIALIZER
# ============================================================

class EmployeeTransferSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmployeeTransfer

        fields = [
            "id",
            "employee",
            "from_department",
            "to_department",
            "reason",
            "transferred_by",
            "transferred_at",
            "status",
        ]

        read_only_fields = [
            "id",
            "employee",
            "from_department",
            "transferred_by",
            "transferred_at",
            "status",
        ]


# ============================================================
# NOTIFICATION SERIALIZER
# ADV-003 — Email & Notification Service
# ============================================================

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification

        fields = [
            "id",
            "employee",
            "title",
            "message",
            "notification_type",
            "status",
            "is_read",
            "read_at",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "created_at",
            "read_at",
        ]

