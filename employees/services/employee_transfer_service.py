from django.db import transaction

from employees.models import (
    Employee,
    Department,
    EmployeeTransfer,
)


class EmployeeTransferService:

    @staticmethod
    @transaction.atomic
    def transfer_employee(
        employee_id,
        to_department_id,
        reason,
        transferred_by
    ):

        # 1. Find employee
        try:
            employee = Employee.objects.select_related(
                "department_fk"
            ).get(id=employee_id)
        except Employee.DoesNotExist:
            raise ValueError("Employee does not exist.")

        # 2. Check employee is active
        if not employee.is_active:
            raise ValueError(
                "Inactive employee cannot be transferred."
            )

        # 3. Check reason
        if not reason or not reason.strip():
            raise ValueError(
                "Transfer reason is required."
            )

        # 4. Find target department
        try:
            target_department = Department.objects.get(
                id=to_department_id,
                is_active=True
            )
        except Department.DoesNotExist:
            raise ValueError(
                "Target department does not exist."
            )

        # 5. Check current department
        current_department = employee.department_fk

        if current_department is None:
            raise ValueError(
                "Employee does not have a current department."
            )

        # 6. Prevent same department transfer
        if current_department.id == target_department.id:
            raise ValueError(
                "Employee is already in this department."
            )

        # 7. Create transfer history
        transfer = EmployeeTransfer.objects.create(
            employee=employee,
            from_department=current_department,
            to_department=target_department,
            reason=reason,
            transferred_by=transferred_by,
            status=EmployeeTransfer.TransferStatus.COMPLETED
        )

        # 8. Update employee department
        employee.department_fk = target_department

        employee.save(
            update_fields=[
                "department_fk",
                "updated_at"
            ]
        )

        # 9. Return transfer record
        return transfer