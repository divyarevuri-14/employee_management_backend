from django.utils import timezone

from rest_framework import viewsets
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import Employee, Notification
from .serializers import (
    EmployeeSerializer,
    NotificationSerializer,
)


# ============================================================
# EMPLOYEE VIEWSET
# ============================================================

class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = Employee.objects.all().order_by("id")

    serializer_class = EmployeeSerializer

    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
    ]

    search_fields = [
        "employee_code",
        "first_name",
        "last_name",
        "email",
        "department",
        "designation",
    ]

    ordering_fields = [
        "id",
        "first_name",
        "salary",
        "joining_date",
        "created_at",
    ]

    ordering = [
        "id",
    ]

    @action(
        detail=False,
        methods=["get"],
        url_path="active"
    )
    def active_employees(self, request):

        active_employees = self.get_queryset().filter(
            is_active=True
        )

        serializer = self.get_serializer(
            active_employees,
            many=True
        )

        return Response(serializer.data)


# ============================================================
# NOTIFICATION APIs
# ADV-003 — Email & Notification Service
# ============================================================

class NotificationListView(APIView):
    """
    GET /api/v1/notifications/

    Returns notifications belonging to
    the currently authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        notifications = Notification.objects.filter(
            recipient=request.user
        ).order_by("-created_at")

        serializer = NotificationSerializer(
            notifications,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


# ============================================================
# MARK NOTIFICATION AS READ
# ============================================================

class NotificationMarkReadView(APIView):
    """
    PATCH /api/v1/notifications/<id>/read/

    Marks a notification as read.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):

        try:
            notification = Notification.objects.get(
                id=notification_id,
                recipient=request.user
            )

        except Notification.DoesNotExist:

            return Response(
                {
                    "detail": "Notification not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        notification.is_read = True
        notification.read_at = timezone.now()

        notification.save(
            update_fields=[
                "is_read",
                "read_at",
                "updated_at",
            ]
        )

        serializer = NotificationSerializer(
            notification
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
