from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser, AllowAny, BasePermission
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiExample,
)

from books.models import Book
from books.serializers import BookSerializer


@extend_schema_view(
    list=extend_schema(
        summary="List books",
        description=(
            "Returns a list of books.\n\n"
            "- Public endpoint (no authentication required)\n"
            "- Supports filtering, search, and ordering\n"
        ),
        tags=["Books"],
        parameters=[
            OpenApiParameter(
                name="cover",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by cover type. Allowed values: `"HARD"`, `"SOFT"`.',
                required=False,
            ),
            OpenApiParameter(
                name="author",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Exact match by author (e.g., `?author=Stephen King`).",
                required=False,
            ),
            OpenApiParameter(
                name="author__icontains",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Case-insensitive substring search by author.",
                required=False,
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search across `title`, `author` (e.g., `?search=king`).",
                required=False,
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Order by: `title`, `author`, `inventory`, `daily_fee`.\n"
                    "Use `-` for descending (e.g., `?ordering=title`, `?ordering=-daily_fee`)."
                ),
                required=False,
            ),
        ],
        responses={200: BookSerializer(many=True)},
        examples=[
            OpenApiExample(
                "List response",
                summary="Example 200 response",
                value=[
                    {
                        "id": 1,
                        "title": "The Shining",
                        "author": "Stephen King",
                        "cover": "HARD",
                        "inventory": 5,
                        "daily_fee": 1.99,
                    }
                ],
                response_only=True,
            )
        ],
    ),
    retrieve=extend_schema(
        summary="Retrieve book",
        description="Returns detailed information about a single book. Public endpoint.",
        tags=["Books"],
        responses={200: BookSerializer},
        examples=[
            OpenApiExample(
                "Detail response",
                value={
                    "id": 1,
                    "title": "The Shining",
                    "author": "Stephen King",
                    "cover": "HARD",
                    "inventory": 5,
                    "daily_fee": 1.99,
                },
                response_only=True,
            )
        ],
    ),
    create=extend_schema(
        summary="Create book",
        description="Creates a new book. Admins only.",
        tags=["Books"],
        request=BookSerializer,
        responses={201: BookSerializer, 400: {"description": "Validation error"}},
        examples=[
            OpenApiExample(
                "Create payload",
                value={
                    "title": "Dune",
                    "author": "Frank Herbert",
                    "cover": "SOFT",
                    "inventory": 3,
                    "daily_fee": 2.50,
                },
                request_only=True,
            )
        ],
    ),
    update=extend_schema(
        summary="Update book",
        description="Fully updates a book. Admins only.",
        tags=["Books"],
        request=BookSerializer,
        responses={200: BookSerializer, 400: {"description": "Validation error"}},
    ),
    partial_update=extend_schema(
        summary="Partial update book",
        description="Partially updates a book. Admins only.",
        tags=["Books"],
        request=BookSerializer,
        responses={200: BookSerializer, 400: {"description": "Validation error"}},
    ),
    destroy=extend_schema(
        summary="Delete book",
        description="Deletes a book. Admins only.",
        tags=["Books"],
        responses={204: None},
    ),
)
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
