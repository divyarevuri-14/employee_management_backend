from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path(
        "admin/",
        admin.site.urls,
    ),

    # Authentication APIs
    path(
        "api/v1/auth/",
        include("authentication.api.urls"),
    ),

    # Employee APIs
    path(
        "api/v1/",
        include("employees.api.urls"),
    ),

    # Router APIs
    path(
        "api/v1/",
        include("employees.routers"),
    ),
]