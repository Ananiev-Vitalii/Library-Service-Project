from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class Cover(models.TextChoices):
    HARD = "HARD", "HARD"
    SOFT = "SOFT", "SOFT"


class Book(models.Model):
    title = models.CharField(max_length=99)
    author = models.CharField(max_length=99)
    cover = models.CharField(max_length=10, choices=Cover.choices)
    inventory = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    daily_fee = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )

    class Meta:
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
            models.Index(fields=["cover"]),
        ]
        ordering = ["title", "author"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(inventory__gte=0),
                name="book_inventory_gte_0",
            ),
            models.CheckConstraint(
                condition=models.Q(daily_fee__gte=0),
                name="book_daily_fee_gte_0",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.title} — {self.author}"
