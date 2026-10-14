import csv
import logging
import os
import smtplib

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, OperationalError, transaction

from .models import Employee


logger = logging.getLogger(__name__)


# ============================================================
# 1. SEND WELCOME EMAIL
# ============================================================

@shared_task(
    bind=True,
    autoretry_for=(OperationalError, smtplib.SMTPException, OSError),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
    soft_time_limit=60,
    time_limit=75,
)
def send_welcome_email(self, employee_id):
    """Send a welcome email to an employee."""

    logger.info(
        "Welcome email task started: employee_id=%s",
        employee_id,
    )

    try:
        employee = Employee.objects.get(id=employee_id)

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

    except Employee.DoesNotExist:
        logger.error(
            "Employee not found: employee_id=%s",
            employee_id,
        )
        raise

    except Exception:
        logger.exception(
            "Welcome email task failed: employee_id=%s",
            employee_id,
        )
        raise


# ============================================================
# 2. GENERATE EMPLOYEE REPORT
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
def generate_employee_report(self):
    """Generate an employee CSV report."""

    logger.info("Employee report generation started")

    temp_path = None

    try:
        employees = Employee.objects.select_related(
            "department_fk"
        ).all()

        employee_count = employees.count()

        reports_dir = os.path.join(
            settings.MEDIA_ROOT,
            "reports",
        )
        os.makedirs(reports_dir, exist_ok=True)

        file_path = os.path.join(
            reports_dir,
            "employee_report.csv",
        )
        temp_path = file_path + ".tmp"

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

            for employee in employees:
                if employee.department_fk:
                    department_name = str(
                        employee.department_fk
                    )
                else:
                    department_name = employee.department

                writer.writerow([
                    employee.employee_code,
                    employee.first_name,
                    employee.last_name,
                    employee.email,
                    employee.phone,
                    department_name,
                    employee.designation,
                    employee.salary,
                    employee.joining_date,
                    employee.is_active,
                ])

        # Replace the old report only after the new report is ready.
        os.replace(temp_path, file_path)

        logger.info(
            "Employee report generated: count=%s, file=%s",
            employee_count,
            file_path,
        )

        return {
            "status": "success",
            "employee_count": employee_count,
            "file_path": file_path,
            "message": "Employee report generated successfully",
        }

    except OperationalError:
        logger.exception(
            "Temporary database error during report generation"
        )
        raise

    except Exception:
        logger.exception("Employee report generation failed")
        raise

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


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
def process_employee_csv(self, file_path):
    """
    Import employees from a CSV file.

    Existing employee codes or emails are skipped.
    Reprocessing the same file should not create duplicates.
    """

    logger.info(
        "CSV processing started: file=%s",
        file_path,
    )

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        processed_rows = 0
        skipped_rows = 0

        required_headers = {
            "employee_code",
            "first_name",
            "last_name",
            "email",
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

            # Normalize headers so spaces do not break row.get().
            reader.fieldnames = [
                header.strip() if header else header
                for header in reader.fieldnames
            ]

            actual_headers = set(reader.fieldnames)
            missing_headers = required_headers - actual_headers

            if missing_headers:
                raise ValueError(
                    "Missing required headers: "
                    + ", ".join(sorted(missing_headers))
                )

            for row in reader:
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

                # Skip rows with missing required values.
                if not all([
                    employee_code,
                    first_name,
                    last_name,
                    email,
                ]):
                    logger.warning(
                        "Skipping row with missing required fields"
                    )
                    skipped_rows += 1
                    continue

                # Check both unique fields and log the exact reason.
                code_exists = Employee.objects.filter(
                    employee_code=employee_code
                ).exists()

                email_exists = Employee.objects.filter(
                    email=email
                ).exists()

                if code_exists or email_exists:
                    logger.warning(
                        "Duplicate employee skipped: "
                        "code=%s, email=%s, "
                        "code_exists=%s, email_exists=%s",
                        employee_code,
                        email,
                        code_exists,
                        email_exists,
                    )
                    skipped_rows += 1
                    continue

                try:
                    with transaction.atomic():
                        Employee.objects.create(
                            employee_code=employee_code,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            phone=(
                                row.get("phone") or ""
                            ).strip(),
                            department=(
                                row.get("department") or ""
                            ).strip(),
                            designation=(
                                row.get("designation") or ""
                            ).strip(),
                            salary=(
                                row.get("salary") or 0
                            ),
                            joining_date=(
                                row.get("joining_date") or None
                            ),
                            is_active=True,
                        )

                    processed_rows += 1

                    logger.info(
                        "Employee created successfully: code=%s",
                        employee_code,
                    )

                except IntegrityError:
                    # A concurrent task may have inserted a duplicate.
                    # Verify the cause before treating it as a duplicate.
                    duplicate_now = (
                        Employee.objects.filter(
                            employee_code=employee_code
                        ).exists()
                        or Employee.objects.filter(
                            email=email
                        ).exists()
                    )

                    if not duplicate_now:
                        raise

                    logger.warning(
                        "Concurrent duplicate skipped: code=%s",
                        employee_code,
                    )
                    skipped_rows += 1

        logger.info(
            "CSV processing completed: "
            "processed=%s, skipped=%s, file=%s",
            processed_rows,
            skipped_rows,
            file_path,
        )

        return {
            "status": "success",
            "file_path": file_path,
            "processed_rows": processed_rows,
            "skipped_rows": skipped_rows,
            "message": "CSV processed successfully",
        }

    except SoftTimeLimitExceeded:
        logger.exception(
            "CSV task exceeded soft time limit: %s",
            file_path,
        )
        raise

    except OperationalError:
        logger.exception(
            "Database operation failed during CSV processing: %s",
            file_path,
        )
        raise

    except Exception:
        logger.exception(
            "CSV processing failed: file=%s",
            file_path,
        )
        raise
