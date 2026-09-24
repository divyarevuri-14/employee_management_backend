from django.urls import path

from .views import (
    EmployeeListCreateAPIView,
    EmployeeDetailAPIView,
    EmployeeDetailsView,
)


urlpatterns = [
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
]