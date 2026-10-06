import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction

from employees.models import Employee


class EmployeeCSVService:
    """
    Reusable service for importing employee data from CSV files.
    """

    REQUIRED_COLUMNS = [
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "phone",
        "department",
        "designation",
        "salary",
        "joining_date",
    ]

    @classmethod
    def validate_headers(cls, headers):
        """
        Validate required CSV headers.
        """

        if not headers:
            return ["CSV file is empty or has no headers."]

        headers = [
            header.strip()
            for header in headers
            if header
        ]

        missing_columns = [
            column
            for column in cls.REQUIRED_COLUMNS
            if column not in headers
        ]

        return missing_columns

    @classmethod
    def validate_row(cls, row, row_number):
        """
        Validate a single CSV row.

        Returns:
            List of validation errors.
        """

        errors = []

        # --------------------------------------------------
        # Required field validation
        # --------------------------------------------------

        for column in cls.REQUIRED_COLUMNS:
            value = row.get(column)

            if value is None or not str(value).strip():
                errors.append(
                    f"{column} is required"
                )

        # Stop further validation if required fields are missing.
        if errors:
            return [
                f"Row {row_number}: {', '.join(errors)}"
            ]

        # --------------------------------------------------
        # Email validation
        # --------------------------------------------------

        email = str(
            row.get("email", "")
        ).strip()

        try:
            validate_email(email)
        except ValidationError:
            errors.append("invalid email")

        # --------------------------------------------------
        # Salary validation
        # --------------------------------------------------

        salary = str(
            row.get("salary", "")
        ).strip()

        try:
            salary_value = Decimal(salary)

            if salary_value < 0:
                errors.append(
                    "salary cannot be negative"
                )

        except (
            InvalidOperation,
            ValueError,
        ):
            errors.append("invalid salary")

        # --------------------------------------------------
        # Joining date validation
        # --------------------------------------------------

        joining_date = str(
            row.get("joining_date", "")
        ).strip()

        try:
            datetime.strptime(
                joining_date,
                "%Y-%m-%d",
            ).date()

        except ValueError:
            errors.append(
                "invalid joining_date; "
                "expected YYYY-MM-DD"
            )

        # --------------------------------------------------
        # Return errors
        # --------------------------------------------------

        if errors:
            return [
                f"Row {row_number}: "
                f"{', '.join(errors)}"
            ]

        return []

    @classmethod
    def import_csv(cls, file_path):
        """
        Import employees from a CSV file.

        Returns:
            Dictionary containing:

            successful:
                Number of successfully imported rows.

            skipped:
                Number of duplicate rows skipped.

            failed:
                Number of invalid/failed rows.

            errors:
                Detailed validation and processing errors.
        """

        successful_count = 0
        skipped_count = 0
        failed_count = 0
        errors = []

        # ==================================================
        # Open CSV file
        # ==================================================

        try:
            with open(
                file_path,
                "r",
                newline="",
                encoding="utf-8-sig",
            ) as csv_file:

                reader = csv.DictReader(
                    csv_file
                )

                headers = reader.fieldnames or []

                # ------------------------------------------
                # Validate headers
                # ------------------------------------------

                missing_columns = cls.validate_headers(
                    headers
                )

                if missing_columns:
                    return {
                        "successful": 0,
                        "skipped": 0,
                        "failed": 0,
                        "errors": [
                            "Missing required columns: "
                            + ", ".join(
                                missing_columns
                            )
                        ],
                    }

                # ==========================================
                # Process rows
                # ==========================================

                for row_number, row in enumerate(
                    reader,
                    start=2,
                ):

                    # --------------------------------------
                    # Detect malformed rows
                    # --------------------------------------

                    if None in row:
                        failed_count += 1

                        errors.append(
                            f"Row {row_number}: "
                            "malformed row - "
                            "extra columns detected"
                        )

                        continue

                    # --------------------------------------
                    # Validate row
                    # --------------------------------------

                    row_errors = cls.validate_row(
                        row,
                        row_number,
                    )

                    if row_errors:
                        failed_count += 1
                        errors.extend(row_errors)
                        continue

                    # --------------------------------------
                    # Clean values
                    # --------------------------------------

                    employee_code = str(
                        row["employee_code"]
                    ).strip()

                    first_name = str(
                        row["first_name"]
                    ).strip()

                    last_name = str(
                        row["last_name"]
                    ).strip()

                    email = str(
                        row["email"]
                    ).strip()

                    phone = str(
                        row["phone"]
                    ).strip()

                    department = str(
                        row["department"]
                    ).strip()

                    designation = str(
                        row["designation"]
                    ).strip()

                    salary = Decimal(
                        str(
                            row["salary"]
                        ).strip()
                    )

                    joining_date = datetime.strptime(
                        str(
                            row["joining_date"]
                        ).strip(),
                        "%Y-%m-%d",
                    ).date()

                    # --------------------------------------
                    # Duplicate employee code
                    # --------------------------------------

                    if Employee.objects.filter(
                        employee_code=employee_code
                    ).exists():

                        skipped_count += 1

                        errors.append(
                            f"Row {row_number}: "
                            f"duplicate employee_code "
                            f"{employee_code}"
                        )

                        continue

                    # --------------------------------------
                    # Duplicate email
                    # --------------------------------------

                    if Employee.objects.filter(
                        email=email
                    ).exists():

                        skipped_count += 1

                        errors.append(
                            f"Row {row_number}: "
                            f"duplicate email "
                            f"{email}"
                        )

                        continue

                    # ======================================
                    # Create employee
                    # ======================================

                    try:
                        with transaction.atomic():

                            Employee.objects.create(
                                employee_code=employee_code,
                                first_name=first_name,
                                last_name=last_name,
                                email=email,
                                phone=phone,
                                department=department,
                                designation=designation,
                                salary=salary,
                                joining_date=joining_date,
                            )

                        successful_count += 1

                    except Exception as exc:
                        failed_count += 1

                        errors.append(
                            f"Row {row_number}: "
                            f"failed to import - {exc}"
                        )

        # ==================================================
        # File errors
        # ==================================================

        except FileNotFoundError:

            failed_count += 1

            errors.append(
                f"File not found: {file_path}"
            )

        except PermissionError:

            failed_count += 1

            errors.append(
                f"Permission denied: {file_path}"
            )

        except UnicodeDecodeError:

            failed_count += 1

            errors.append(
                "Unable to read CSV file. "
                "Please use UTF-8 encoding."
            )

        except csv.Error as exc:

            failed_count += 1

            errors.append(
                f"CSV parsing error: {exc}"
            )

        # ==================================================
        # Return import report
        # ==================================================

        return {
            "successful": successful_count,
            "skipped": skipped_count,
            "failed": failed_count,
            "errors": errors,
        }