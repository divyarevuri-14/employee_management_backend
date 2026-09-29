from django.urls import path

from .views import RegistrationView, LoginView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    # User Registration
    path(
        "register/",
        RegistrationView.as_view(),
        name="register",
    ),

    # Existing Login
    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    # JWT Token
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),

    # JWT Token Refresh
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
]