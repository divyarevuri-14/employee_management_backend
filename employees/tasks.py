import csv
import logging
import os
import smtplib
import time
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, OperationalError, transaction

from .models import Employee


logger = logging.getLogger("employees")


# ============================================================
# COMMON TASK EXECUTION LOGGING
# ============================================================

def log_task_execution(task_func):
    """Log task start, completion, failures, and execution duration."""

    @wraps(task_func)
    def wrapper(*args, **kwargs):
        task_name = task_func.__name__
        started = time.perf_counter()

        logger.info("Task started: %s", task_name)

        try:
            result = task_func(*args, **kwargs)

            duration = time.perf_counter() - started

            logger.info(
                "Task completed: %s | duration=%.2f seconds",
                task_name,
                duration,
            )

            return result

        except Exception:
            duration = time.perf_counter() - started

            logger.exception(
                "Task failed: %s | duration=%.2f seconds",
                task_name,
                duration,
            )

            raise

    return wrapper


# ============================================================
# COMMON VALIDATION
# ============================================================

def validate_positive_integer(value, field_name):
    """Validate an integer task argument."""

    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise ValueError(
            f"{field_name} must be a positive integer"
        )


def validate_csv_path(file_path):
    """Validate the CSV file path supplied to the task."""

    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError(
            "file_path must be a non-empty string"
        )

    file_path = os.path.abspath(file_path.strip())

    if not file_path.lower().endswith(".csv"):
        raise ValueError(
            "Only CSV files are supported"
        )

    if not os.path.isfile(file_path):
        raise FileNotFoundError(
            f"CSV file not found: {file_path}"
        )

    return file_path


# ============================================================
# 1. SEND WELCOME EMAIL
# ============================================================

@shared_task(
    bind=True,
    autoretry_for=(
        OperationalError,
        smtplib.SMTPException,
        OSError,
    ),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    soft_time_limit=60,
    time_limit=75,
)
@log_task_execution
def send_welcome_email(self, employee_id):
    """Send a welcome email to an existing employee."""

    validate_positive_integer(
        employee_id,
        "employee_id",
    )

    try:
        employee = Employee.objects.get(pk=employee_id)

    except Employee.DoesNotExist:
        logger.error(
            "Employee not found; welcome email not sent: id=%s",
            employee_id,
        )

        return {
            "status": "failed",
            "employee_id": employee_id,
            "message": "Employee not found",
        }

    send_mail(
        subject="Welcome to the Company",
        message=(
            f"Hello {employee.first_name},\n\n"
            "Welcome to the company!\n"
            "We are happy to have you with us."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[employee.email],
        fail_silently=False,
    )

    logger.info(
        "Welcome email sent: employee_id=%s",
        employee_id,
    )

    return {
        "status": "success",
        "employee_id": employee_id,
        "message": "Welcome email sent successfully",
    }


# ============================================================
# 2. GENERATE DAILY EMPLOYEE REPORT
# ============================================================

@shared_task(
    bind=True,
    name="employees.tasks.generate_daily_employee_report",
    autoretry_for=(OperationalError, OSError),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=60,
    time_limit=75,
)
@log_task_execution
def generate_daily_employee_report(self):
    """Generate an employee CSV report safely."""

    reports_dir = os.path.join(
        settings.MEDIA_ROOT,
        "reports",
    )

    os.makedirs(
        reports_dir,
        exist_ok=True,
    )

    final_path = os.path.join(
        reports_dir,
        "employee_report.csv",
    )

    task_id = self.request.id or "local"

    temp_path = (
        f"{final_path}.{task_id}.tmp"
    )

    try:
        employees = Employee.objects.select_related(
            "department_fk"
        ).all()

        employee_count = employees.count()

        with open(
            temp_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.writer(csv_file)

            writer.writerow([
                "Employee Code",
                "First Name",
                "Last Name",
                "Email",
                "Phone",
                "Department",
                "Designation",
                "Salary",
                "Joining Date",
                "Active",
            ])

            for employee in employees.iterator():

                department = getattr(
                    employee,
                    "department_fk",
                    None,
                )

                department_name = (
                    str(department)
                    if department
                    else getattr(
                        employee,
                        "department",
                        "",
                    )
                )

                writer.writerow([
                    employee.employee_code,
                    employee.first_name,
                    employee.last_name,
                    employee.email,
                    employee.phone,
                    department_name,
                    getattr(
                        employee,
                        "designation",
                        "",
                    ),
                    employee.salary,
                    employee.joining_date,
                    employee.is_active,
                ])

        # Replace the report only after successful generation.
        os.replace(
            temp_path,
            final_path,
        )

        logger.info(
            "Employee report generated: count=%s, file=%s",
            employee_count,
            final_path,
        )

        return {
            "status": "success",
            "employee_count": employee_count,
            "file_path": final_path,
            "message": "Daily employee report generated",
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# Backward compatibility for existing imports.
generate_employee_report = generate_daily_employee_report


# ============================================================
# 3. PROCESS EMPLOYEE CSV
# ============================================================

@shared_task(
    bind=True,
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=60,
    time_limit=75,
)
@log_task_execution
def process_employee_csv(self, file_path):
    """
    Import employee data from a CSV file.

    Existing employee codes and emails are skipped.
    Invalid rows are skipped and logged.
    Database uniqueness constraints protect against
    concurrent duplicate inserts.
    """

    file_path = validate_csv_path(file_path)

    processed_rows = 0
    skipped_rows = 0

    required_headers = {
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "joining_date",
    }

    with open(
        file_path,
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        if not reader.fieldnames:
            raise ValueError(
                "CSV file does not contain headers"
            )

        reader.fieldnames = [
            header.strip() if header else header
            for header in reader.fieldnames
        ]

        if len(reader.fieldnames) != len(
            set(reader.fieldnames)
        ):
            raise ValueError(
                "CSV contains duplicate column headers"
            )

        missing_headers = (
            required_headers - set(reader.fieldnames)
        )

        if missing_headers:
            raise ValueError(
                "Missing required CSV headers: "
                + ", ".join(sorted(missing_headers))
            )

        for line_number, row in enumerate(
            reader,
            start=2,
        ):

            employee_code = (
                row.get("employee_code") or ""
            ).strip()

            first_name = (
                row.get("first_name") or ""
            ).strip()

            last_name = (
                row.get("last_name") or ""
            ).strip()

            email = (
                row.get("email") or ""
            ).strip()

            joining_date_text = (
                row.get("joining_date") or ""
            ).strip()

            # Validate required values.
            if not all([
                employee_code,
                first_name,
                last_name,
                email,
                joining_date_text,
            ]):
                logger.warning(
                    "Skipping CSV line %s: missing required values",
                    line_number,
                )

                skipped_rows += 1
                continue

            # Validate date and salary before database insertion.
            try:
                joining_date = date.fromisoformat(
                    joining_date_text
                )

                salary_text = (
                    row.get("salary") or "0"
                ).strip()

                salary = Decimal(salary_text)

                if not salary.is_finite() or salary < 0:
                    raise InvalidOperation(
                        "Salary must be a non-negative number"
                    )

            except (ValueError, InvalidOperation):
                logger.warning(
                    "Skipping CSV line %s: invalid date or salary",
                    line_number,
                )

                skipped_rows += 1
                continue

            try:
                with transaction.atomic():

                    # Idempotency: do not create an existing employee.
                    duplicate_exists = (
                        Employee.objects.filter(
                            employee_code=employee_code
                        ).exists()
                        or Employee.objects.filter(
                            email=email
                        ).exists()
                    )

                    if duplicate_exists:
                        logger.info(
                            "Duplicate employee skipped: "
                            "line=%s, code=%s",
                            line_number,
                            employee_code,
                        )

                        skipped_rows += 1
                        continue

                    employee_values = {
                        "employee_code": employee_code,
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone": (
                            row.get("phone") or ""
                        ).strip(),
                        "salary": salary,
                        "joining_date": joining_date,
                        "is_active": True,
                    }

                    # Support legacy text fields when present.
                    model_fields = {
                        field.name
                        for field in Employee._meta.get_fields()
                    }

                    if "department" in model_fields:
                        employee_values["department"] = (
                            row.get("department") or ""
                        ).strip()

                    if "designation" in model_fields:
                        employee_values["designation"] = (
                            row.get("designation") or ""
                        ).strip()

                    # Create one employee within a transaction.
                    Employee.objects.create(
                        **employee_values
                    )

                    processed_rows += 1

                    logger.info(
                        "Employee created from CSV: code=%s",
                        employee_code,
                    )

            except IntegrityError:
                # Atomic transaction has rolled back here.
                # Check if another task inserted the same employee.
                duplicate_now = (
                    Employee.objects.filter(
                        employee_code=employee_code
                    ).exists()
                    or Employee.objects.filter(
                        email=email
                    ).exists()
                )

                if duplicate_now:
                    logger.info(
                        "Concurrent duplicate skipped: code=%s",
                        employee_code,
                    )

                    skipped_rows += 1

                else:
                    # Do not hide unrelated database constraint errors.
                    raise

    logger.info(
        "CSV processing completed: processed=%s, skipped=%s",
        processed_rows,
        skipped_rows,
    )

    return {
        "status": "success",
        "file_path": file_path,
        "processed_rows": processed_rows,
        "skipped_rows": skipped_rows,
        "message": "CSV processed successfully",
    }


# ============================================================
# 4. INACTIVE EMPLOYEE MAINTENANCE
# ============================================================

@shared_task(
    bind=True,
    name="employees.tasks.run_inactive_employee_maintenance",
    autoretry_for=(OperationalError,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    acks_late=True,
    reject_on_worker_lost=True,
    soft_time_limit=60,
    time_limit=75,
)
@log_task_execution
def run_inactive_employee_maintenance(self):
    """Check inactive employee count without modifying records."""

    inactive_count = Employee.objects.filter(
        is_active=False
    ).count()

    logger.info(
        "Inactive employee maintenance completed: count=%s",
        inactive_count,
    )

    return {
        "status": "success",
        "inactive_employee_count": inactive_count,
        "message": "Inactive employee check completed",
    }