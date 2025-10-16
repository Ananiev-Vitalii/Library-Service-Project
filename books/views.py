from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser, AllowAny, BasePermission

from books.models import Book
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "author"]
    ordering_fields = ["title", "author", "inventory", "daily_fee"]
    ordering = ["title", "author"]

    filterset_fields = {
        "cover": ["exact"],
        "author": ["exact", "icontains"],
    }

    def get_permissions(self) -> list[BasePermission]:
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAdminUser()]
