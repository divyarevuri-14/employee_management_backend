from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


# ============================================================
# DEPARTMENT
# ============================================================

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# ============================================================
# PROJECT
# ============================================================

class Project(models.Model):
    name = models.CharField(max_length=200)
    project_code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    client_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.project_code})"


# ============================================================
# EMPLOYEE
# ============================================================

class Employee(models.Model):
    employee_code = models.CharField(max_length=20, unique=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15)

    # OLD FIELD - keep temporarily
    department = models.CharField(max_length=100)

    # NEW FOREIGN KEY
    department_fk = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees",
        null=True,
        blank=True
    )

    designation = models.CharField(max_length=100)

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    joining_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    projects = models.ManyToManyField(
        Project,
        related_name="employees",
        blank=True
    )

    def __str__(self):
        return (
            f"{self.employee_code} - "
            f"{self.first_name} {self.last_name}"
        )


# ============================================================
# EMPLOYEE PROFILE
# ============================================================

class EmployeeProfile(models.Model):
    employee = models.OneToOneField(
        Employee,
        on_delete=models.CASCADE,
        related_name="profile",
        null=True,
        blank=True
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    address = models.TextField(
        blank=True
    )

    emergency_contact = models.CharField(
        max_length=15,
        blank=True
    )

    blood_group = models.CharField(
        max_length=5,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="employee_profiles/",
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.employee.employee_code} Profile"


# ============================================================
# EMPLOYEE TRANSFER
# ============================================================

class EmployeeTransfer(models.Model):

    class TransferStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        COMPLETED = "COMPLETED", "Completed"

    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="transfers"
    )

    from_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="transfers_from"
    )

    to_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="transfers_to"
    )

    reason = models.TextField()

    transferred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="employee_transfers"
    )

    transferred_at = models.DateTimeField(
        auto_now_add=True
    )

    status = models.CharField(
        max_length=20,
        choices=TransferStatus.choices,
        default=TransferStatus.PENDING
    )

    def __str__(self):
        return (
            f"{self.employee.employee_code} - "
            f"{self.from_department.name} to "
            f"{self.to_department.name}"
        )


# ============================================================
# USER PROFILE / RBAC
# ============================================================

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("HR", "HR"),
        ("MANAGER", "Manager"),
        ("EMPLOYEE", "Employee"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="EMPLOYEE"
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ============================================================
# EMPLOYEE AUDIT
# ============================================================

class EmployeeAudit(models.Model):

    ACTION_CREATED = "CREATED"
    ACTION_UPDATED = "UPDATED"

    ACTION_CHOICES = [
        (ACTION_CREATED, "Created"),
        (ACTION_UPDATED, "Updated"),
    ]

    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )

    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
    )

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_audits",
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.employee.employee_code} - {self.action}"


# ============================================================
# NOTIFICATION
# ADV-003 — Email & Notification Service
# ============================================================

class Notification(models.Model):

    class NotificationType(models.TextChoices):
        WELCOME = "WELCOME", "Welcome"
        GENERAL = "GENERAL", "General"

    class NotificationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        FAILED = "FAILED", "Failed"

    # User who receives the notification
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    # Employee related to this notification
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="notifications",
        null=True,
        blank=True
    )

    # Notification heading
    title = models.CharField(
        max_length=255
    )

    # Notification message
    message = models.TextField()

    # Notification category
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )

    # Email/notification processing status
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING
    )

    # Stores failure reason if notification fails
    error_message = models.TextField(
        blank=True,
        null=True
    )

    # Read/unread state
    is_read = models.BooleanField(
        default=False
    )

    # Time when notification was read
    read_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Notification creation time
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # Last update time
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.recipient.username} - "
            f"{self.title} - "
            f"{self.status}"
        )

