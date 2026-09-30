from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Admin access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "ADMIN"
        )


class IsHR(BasePermission):
    message = "HR access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "HR"
        )


class IsManager(BasePermission):
    message = "Manager access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "MANAGER"
        )


class IsEmployee(BasePermission):
    message = "Employee access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role == "EMPLOYEE"
        )


class IsAdminOrHR(BasePermission):
    message = "Admin or HR access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role in [
                "ADMIN",
                "HR",
            ]
        )


class IsAdminHROrManager(BasePermission):
    message = "Admin, HR, or Manager access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "profile")
            and request.user.profile.role in [
                "ADMIN",
                "HR",
                "MANAGER",
            ]
        )