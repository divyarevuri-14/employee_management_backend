from django.urls import path

from .views import (
    EmployeeListCreateAPIView,
    EmployeeDetailAPIView,
    EmployeeDetailsView,
    EmployeeTransferView,
    EmployeeTransferHistoryView,
)


urlpatterns = [
    # Employee APIs
    path(
        "employees/details/",
        EmployeeDetailsView.as_view(),
        name="employee-details",
    ),

    path(
        "employees/",
        EmployeeListCreateAPIView.as_view(),
        name="employee-list-create",
    ),

    path(
        "employees/<int:id>/",
        EmployeeDetailAPIView.as_view(),
        name="employee-detail",
    ),

    # Employee Transfer
    path(
        "employees/<int:employee_id>/transfer/",
        EmployeeTransferView.as_view(),
        name="employee-transfer",
    ),

    path(
        "employees/<int:employee_id>/transfer-history/",
        EmployeeTransferHistoryView.as_view(),
        name="employee-transfer-history",
    ),
]