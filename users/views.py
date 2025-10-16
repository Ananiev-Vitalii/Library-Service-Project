from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from drf_spectacular.utils import extend_schema, OpenApiExample
from users.serializers import UserRegisterSerializer, UserMeSerializer

User = get_user_model()


@extend_schema(
    summary="Register a new user",
    description=(
        "Creates a new user account.\n\n"
        "- Public endpoint (no authentication required)\n"
        "- Returns the created user without the password field\n"
    ),
    operation_id="users_register",
    tags=["Users"],
    request=UserRegisterSerializer,
    responses={
        201: UserRegisterSerializer,
        400: {"description": "Validation error"},
    },
    examples=[
        OpenApiExample(
            "Signup payload",
            summary="Valid registration payload",
            value={
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Wonder",
                "password": "StrongPass123",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Created user response",
            summary="Response (201)",
            value={
                "id": 1,
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Wonder",
                "is_staff": False,
            },
            response_only=True,
        ),
    ],
)
class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)


@extend_schema(
    summary="Get/Update my profile",
    description=(
        "Retrieves and updates the profile of the authenticated user.\n\n"
        "- Requires JWT (header: `Authorize: Bearer <token>`)\n"
        "- Updatable fields: `first_name`, `last_name`, `password`\n"
        "- When `password` is provided, it is hashed server-side\n"
    ),
    operation_id="users_me",
    tags=["Users"],
    responses={
        200: UserMeSerializer,
        401: {"description": "Unauthorized"},
        400: {"description": "Validation error"},
    },
    examples=[
        OpenApiExample(
            "Profile response",
            summary="Response (200)",
            value={
                "id": 1,
                "email": "alice@example.com",
                "first_name": "Alice",
                "last_name": "Wonder",
                "is_staff": False,
            },
            response_only=True,
        ),
        OpenApiExample(
            "Partial update",
            summary="PATCH payload",
            value={"first_name": "Alicia"},
            request_only=True,
        ),
        OpenApiExample(
            "Change password",
            summary="PATCH payload (change password)",
            value={"password": "NewStrongPass123"},
            request_only=True,
        ),
    ],
)
class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> User:
        return self.request.user
