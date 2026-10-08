import csv
import logging
import os
import time

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

from .models import Employee


logger = logging.getLogger(__name__)


# ============================================================
# 1. SEND WELCOME EMAIL
# ============================================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def send_welcome_email(self, employee_id):
    """
    Send welcome email asynchronously to an employee.
    """

    logger.info(
        "Welcome email task started for employee_id=%s",
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
            "Welcome email sent successfully for employee_id=%s",
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

    except Exception as exc:
        logger.error(
            "Welcome email task failed for employee_id=%s: %s",
            employee_id,
            exc,
        )
        raise


# ============================================================
# 2. GENERATE EMPLOYEE REPORT
# ============================================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def generate_employee_report(self):
    """
    Generate employee report as a CSV file asynchronously.
    """

    logger.info("Employee report generation started")

    try:
        employees = Employee.objects.all()

        employee_count = employees.count()

        # Create reports directory
        reports_dir = os.path.join(
            settings.MEDIA_ROOT,
            "reports",
        )

        os.makedirs(
            reports_dir,
            exist_ok=True,
        )

        # Report file path
        file_name = "employee_report.csv"

        file_path = os.path.join(
            reports_dir,
            file_name,
        )

        # Generate CSV report
        with open(
            file_path,
            "w",
            newline="",
            encoding="utf-8",
        ) as csv_file:

            writer = csv.writer(csv_file)

            # CSV header
            writer.writerow(
                [
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
                ]
            )

            # Employee data
            for employee in employees:

                # Use ForeignKey department if available
                if employee.department_fk:
                    department_name = str(
                        employee.department_fk
                    )
                else:
                    department_name = employee.department

                writer.writerow(
                    [
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
                    ]
                )

        # Simulate long-running processing
        time.sleep(5)

        logger.info(
            "Employee report generated successfully. "
            "Total employees=%s, file=%s",
            employee_count,
            file_path,
        )

        return {
            "status": "success",
            "employee_count": employee_count,
            "file_path": file_path,
            "message": "Employee report generated successfully",
        }

    except Exception as exc:
        logger.error(
            "Employee report generation failed: %s",
            exc,
        )
        raise


# ============================================================
# 3. PROCESS EMPLOYEE CSV
# ============================================================

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def process_employee_csv(self, file_path):
    """
    Process employee CSV file asynchronously.
    """

    logger.info(
        "CSV processing started for file=%s",
        file_path,
    )

    try:
        # Check whether file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(
                f"CSV file not found: {file_path}"
            )

        processed_rows = 0
        skipped_rows = 0

        # Required CSV columns
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
            encoding="utf-8",
        ) as csv_file:

            reader = csv.DictReader(csv_file)

            # Validate headers
            if not reader.fieldnames:
                raise ValueError(
                    "CSV file does not contain headers"
                )

            actual_headers = {
                header.strip()
                for header in reader.fieldnames
                if header
            }

            missing_headers = (
                required_headers - actual_headers
            )

            if missing_headers:
                raise ValueError(
                    f"Missing required headers: "
                    f"{', '.join(sorted(missing_headers))}"
                )

            # Process rows
            for row in reader:

                employee_code = (
                    row.get("employee_code", "").strip()
                )

                first_name = (
                    row.get("first_name", "").strip()
                )

                last_name = (
                    row.get("last_name", "").strip()
                )

                email = (
                    row.get("email", "").strip()
                )

                # Validate required values
                if not all(
                    [
                        employee_code,
                        first_name,
                        last_name,
                        email,
                    ]
                ):
                    skipped_rows += 1
                    continue

                # Avoid duplicate employee records
                if Employee.objects.filter(
                    employee_code=employee_code
                ).exists():
                    skipped_rows += 1
                    continue

                # Create employee
                Employee.objects.create(
                    employee_code=employee_code,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=row.get("phone", "").strip(),
                    department=row.get(
                        "department",
                        "",
                    ).strip(),
                    designation=row.get(
                        "designation",
                        "",
                    ).strip(),
                    salary=row.get(
                        "salary",
                        0,
                    ) or 0,
                    joining_date=row.get(
                        "joining_date"
                    ),
                    is_active=True,
                )

                processed_rows += 1

        logger.info(
            "CSV processed successfully. "
            "Processed=%s, Skipped=%s, File=%s",
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

    except Exception as exc:
        logger.error(
            "CSV processing failed for file=%s: %s",
            file_path,
            exc,
        )
        raise