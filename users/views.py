from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from users.serializers import UserRegisterSerializer, UserMeSerializer

User = get_user_model()


class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)


class UserMeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> User:
        return self.request.user
