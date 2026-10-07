from django.urls import path

from employees.api.views import (
    EmployeeListCreateAPIView,
    EmployeeDetailAPIView,
    EmployeeDetailsView,
    EmployeeTransferView,
    EmployeeTransferHistoryView,
    MyProfileView,
    health_check,
)

from employees.views import (
    NotificationListView,
    NotificationMarkReadView,
)


urlpatterns = [

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    path(
        "health/",
        health_check,
        name="health-check",
    ),


    # ========================================================
    # EMPLOYEE APIs
    # ========================================================

    # Employee list and create
    path(
        "employees/",
        EmployeeListCreateAPIView.as_view(),
        name="employee-list-create",
    ),

    # Employee detail
    path(
        "employees/<int:id>/",
        EmployeeDetailAPIView.as_view(),
        name="employee-detail",
    ),

    # Optimized employee details
    path(
        "employees/details/",
        EmployeeDetailsView.as_view(),
        name="employee-details",
    ),


    # ========================================================
    # EMPLOYEE TRANSFER APIs
    # ========================================================

    # Employee transfer
    path(
        "employees/<int:employee_id>/transfer/",
        EmployeeTransferView.as_view(),
        name="employee-transfer",
    ),

    # Employee transfer history
    path(
        "employees/<int:employee_id>/transfers/",
        EmployeeTransferHistoryView.as_view(),
        name="employee-transfer-history",
    ),


    # ========================================================
    # PROFILE API
    # ========================================================

    # Logged-in user's profile
    path(
        "profile/me/",
        MyProfileView.as_view(),
        name="my-profile",
    ),


    # ========================================================
    # NOTIFICATION APIs
    # ADV-003 — Email & Notification Service
    # ========================================================

    # List notifications for logged-in user
    path(
        "notifications/",
        NotificationListView.as_view(),
        name="notification-list",
    ),

    # Mark notification as read
    path(
        "notifications/<int:notification_id>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-mark-read",
    ),
]

