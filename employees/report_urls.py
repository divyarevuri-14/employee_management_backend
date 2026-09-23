from django.urls import path

from .reports import (
    DepartmentSummaryView,
    ProjectSummaryView,
    SalarySummaryView,
)

urlpatterns = [
    path(
        "department-summary/",
        DepartmentSummaryView.as_view(),
        name="department-summary",
    ),
    path(
        "project-summary/",
        ProjectSummaryView.as_view(),
        name="project-summary",
    ),
    path(
        "salary-summary/",
        SalarySummaryView.as_view(),
        name="salary-summary",
    ),
]