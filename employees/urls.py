from django.urls import path
from .views import health_check, employee_list

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("employees/", employee_list, name="employee-list"),
]