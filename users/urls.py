from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from users.views import UserRegisterView, UserMeView

app_name = "users"

urlpatterns = [
    path("users/", UserRegisterView.as_view(), name="users-register"),
    path("users/me/", UserMeView.as_view(), name="users-me"),
    path("users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("users/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
