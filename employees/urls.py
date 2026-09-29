from django.urls import path

from .views import (
    EmployeeTransferView,
    EmployeeTransferHistoryView,
)


urlpatterns = [
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