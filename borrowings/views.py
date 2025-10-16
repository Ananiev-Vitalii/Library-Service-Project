from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from django.db.models import QuerySet
from typing import Any, Optional, Type
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, serializers
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiResponse,
)

from borrowings.models import Borrowing
from borrowings.serializers import BorrowingReadSerializer, BorrowingCreateSerializer
from books.models import Book


@extend_schema_view(
    list=extend_schema(
        summary="List borrowings",
        description="Returns borrowings. Non-admins see only their own. "
        "Admins see all or a specific user via user_id.",
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by active borrowings (true/false)",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Admin-only: filter by user id",
            ),
        ],
        responses={200: BorrowingReadSerializer},
        tags=["Borrowings"],
    ),
    retrieve=extend_schema(
        summary="Retrieve borrowing",
        responses={
            200: BorrowingReadSerializer,
            404: OpenApiResponse(description="Not found"),
        },
        tags=["Borrowings"],
    ),
    create=extend_schema(
        summary="Create borrowing",
        description="Creates a borrowing, attaches current user,"
        " and decreases book inventory by 1.",
        request=BorrowingCreateSerializer,
        responses={
            201: BorrowingReadSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Book not found"),
        },
        tags=["Borrowings"],
    ),
)
class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self) -> Type[serializers.Serializer]:
        if self.action in ["list", "retrieve"]:
            return BorrowingReadSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingReadSerializer

    def get_queryset(self) -> QuerySet[Borrowing]:
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_staff:
            qs = qs.filter(user=user)

        user_id = self.request.query_params.get("user_id")
        if user_id and user.is_staff:
            qs = qs.filter(user_id=user_id)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            active = is_active.lower() in {"1", "true", "yes", "y"}
            if active:
                qs = qs.filter(actual_return_date__isnull=True)
            else:
                qs = qs.filter(actual_return_date__isnull=False)

        return qs.order_by("-borrow_date", "id")

    @transaction.atomic
    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        book_id = request.data.get("book")
        if not book_id:
            return Response({"detail": "Field 'book' is required."}, status=400)

        book = Book.objects.select_for_update().filter(id=book_id).first()
        if not book:
            return Response({"detail": "Book not found."}, status=404)
        if book.inventory <= 0:
            return Response({"detail": "Book is out of stock."}, status=400)

        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        borrowing = serializer.save()
        book.inventory -= 1
        book.save(update_fields=["inventory"])

        read = BorrowingReadSerializer(borrowing, context={"request": request})
        headers = self.get_success_headers(read.data)
        return Response(read.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["POST"], url_path="return")
    @transaction.atomic
    def return_borrowing(
        self, request: Request, pk: Optional[int | str] = None
    ) -> Response:
        borrowing = get_object_or_404(
            Borrowing.objects.select_related("book").select_for_update(), pk=pk
        )

        if not request.user.is_staff and borrowing.user_id != request.user.id:
            return Response({"detail": "Forbidden."}, status=403)

        if borrowing.actual_return_date is not None:
            return Response({"detail": "Already returned."}, status=400)

        borrowing.actual_return_date = timezone.now().date()
        borrowing.save(update_fields=["actual_return_date"])

        book = borrowing.book
        book.inventory += 1
        book.save(update_fields=["inventory"])

        data = BorrowingReadSerializer(borrowing, context={"request": request}).data
        return Response(data, status=200)
