import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Employee, EmployeeAudit


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Employee)
def employee_audit_signal(sender, instance, created, **kwargs):

    if created:
        action = EmployeeAudit.ACTION_CREATED
    else:
        action = EmployeeAudit.ACTION_UPDATED

    request = getattr(instance, "_audit_request", None)

    user = None

    if request:
        request_user = getattr(request, "user", None)

        if request_user and request_user.is_authenticated:
            user = request_user

    EmployeeAudit.objects.create(
        employee=instance,
        action=action,
        performed_by=user,
    )

    logger.info(
        "Employee audit created | employee=%s | action=%s | user=%s",
        instance.employee_code,
        action,
        user.username if user else "anonymous",
    )