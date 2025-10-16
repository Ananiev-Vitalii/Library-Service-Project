from decimal import Decimal
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from books.models import Book


class BookSerializer(serializers.ModelSerializer):
    daily_fee = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        min_value=Decimal("0.01"),
        coerce_to_string=False,
        style={"input_type": "number"},
    )

    class Meta:
        model = Book
        fields = ["id", "title", "author", "cover", "inventory", "daily_fee"]
        read_only_fields = ["id"]
        validators = [
            UniqueTogetherValidator(
                queryset=Book.objects.all(),
                fields=["title", "author", "cover"],
                message=(
                    "A book with the combination of this title+author+cover already "
                    "exists."
                ),
            )
        ]

    @staticmethod
    def validate_inventory(value: int) -> int:
        if value < 1:
            raise serializers.ValidationError("Inventory must be at least 1.")
        return value

    @staticmethod
    def validate_daily_fee(value: Decimal) -> Decimal:
        if value <= 0:
            raise serializers.ValidationError("Daily fee must be greater than 0.")
        return value
