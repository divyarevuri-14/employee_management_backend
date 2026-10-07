from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from employees.models import Employee, Notification


class NotificationService:
    """
    Reusable service for creating notifications
    and sending employee-related emails.
    """

    @staticmethod
    def send_welcome_notification(
        employee: Employee,
        recipient
    ):
        """
        Create a welcome notification and send welcome email.

        employee:
            Employee who is receiving the welcome notification.

        recipient:
            Django User who owns the notification.
        """

        # --------------------------------------------------------
        # 1. Validate notification recipient
        # --------------------------------------------------------

        if recipient is None:
            raise ValueError(
                "Notification recipient is required."
            )

        # --------------------------------------------------------
        # 2. Validate employee email
        # --------------------------------------------------------

        if not employee.email:

            return Notification.objects.create(
                recipient=recipient,
                employee=employee,
                title="Welcome Notification",
                message=(
                    f"Welcome {employee.first_name} "
                    f"{employee.last_name}."
                ),
                notification_type=(
                    Notification.NotificationType.WELCOME
                ),
                status=(
                    Notification.NotificationStatus.FAILED
                ),
                error_message=(
                    "Employee email address is missing."
                ),
            )

        # --------------------------------------------------------
        # 3. Check duplicate successful notification
        # --------------------------------------------------------

        existing_notification = Notification.objects.filter(
            recipient=recipient,
            employee=employee,
            notification_type=(
                Notification.NotificationType.WELCOME
            ),
            status=(
                Notification.NotificationStatus.SENT
            ),
        ).first()

        if existing_notification:
            return existing_notification

        # --------------------------------------------------------
        # 4. Create pending notification
        # --------------------------------------------------------

        notification = Notification.objects.create(
            recipient=recipient,
            employee=employee,
            title="Welcome to the Organization",
            message=(
                f"Welcome {employee.first_name} "
                f"{employee.last_name}!"
            ),
            notification_type=(
                Notification.NotificationType.WELCOME
            ),
            status=(
                Notification.NotificationStatus.PENDING
            ),
        )

        # --------------------------------------------------------
        # 5. Render email template
        # --------------------------------------------------------

        try:

            html_content = render_to_string(
                "emails/welcome_employee.html",
                {
                    "employee": employee,
                },
            )

            # ----------------------------------------------------
            # 6. Create email
            # ----------------------------------------------------

            email = EmailMultiAlternatives(
                subject="Welcome to the Organization",
                body=(
                    f"Welcome {employee.first_name} "
                    f"{employee.last_name}!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[employee.email],
            )

            email.attach_alternative(
                html_content,
                "text/html",
            )

            # ----------------------------------------------------
            # 7. Send email
            # ----------------------------------------------------

            email.send(fail_silently=False)

            # ----------------------------------------------------
            # 8. Mark notification as SENT
            # ----------------------------------------------------

            notification.status = (
                Notification.NotificationStatus.SENT
            )

            notification.error_message = None

            notification.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

        except Exception as exc:

            # ----------------------------------------------------
            # 9. Record failed notification
            # ----------------------------------------------------

            notification.status = (
                Notification.NotificationStatus.FAILED
            )

            notification.error_message = str(exc)

            notification.save(
                update_fields=[
                    "status",
                    "error_message",
                    "updated_at",
                ]
            )

        return notification

