from django.urls import path

from .views import employee_detail, employee_list


urlpatterns = [
    path(
        "employees/",
        employee_list,
        name="employee-list",
    ),
    path(
        "employees/<int:id>/",
        employee_detail,
        name="employee-detail",
    ),
]