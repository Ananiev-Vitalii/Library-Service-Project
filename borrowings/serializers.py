from __future__ import annotations

from typing import Any, Dict
from django.utils import timezone
from rest_framework import serializers

from borrowings.models import Borrowing
from books.models import Book
from books.serializers import BookSerializer


class BorrowingReadSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
            "book",
            "user_id",
        ]
        read_only_fields = fields

    def get_is_active(self, obj: Borrowing) -> bool:
        return obj.actual_return_date is None


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["book", "expected_return_date"]

    def validate_book(self, book: Book) -> Book:
        if book.inventory <= 0:
            raise serializers.ValidationError("Book is out of stock.")
        return book

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        today = timezone.now().date()
        if attrs["expected_return_date"] <= today:
            raise serializers.ValidationError(
                {"expected_return_date": "Expected return date must be in the future."}
            )
        return attrs

    def create(self, validated_data: Dict[str, Any]) -> Borrowing:
        request = self.context["request"]
        borrowing = Borrowing.objects.create(
            user=request.user,
            borrow_date=timezone.now().date(),
            actual_return_date=None,
            **validated_data,
        )
        return borrowing
