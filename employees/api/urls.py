from django.urls import path

from employees.api.views import (
    EmployeeListCreateAPIView,
    EmployeeDetailAPIView,
    EmployeeDetailsView,
    EmployeeTransferView,
    EmployeeTransferHistoryView,
    MyProfileView,
)

urlpatterns = [

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

    # Logged-in user's profile
    path(
        "profile/me/",
        MyProfileView.as_view(),
        name="my-profile",
    ),
]