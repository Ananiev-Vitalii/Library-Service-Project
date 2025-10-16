from __future__ import annotations

from django.db import models
from django.conf import settings
from django.db.models import Q, F


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        "books.Book",
        on_delete=models.PROTECT,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    class Meta:
        ordering = ["-borrow_date", "id"]
        indexes = [
            models.Index(fields=["borrow_date"]),
            models.Index(fields=["expected_return_date"]),
            models.Index(fields=["actual_return_date"]),
            models.Index(fields=["user"]),
            models.Index(fields=["book"]),
        ]
        constraints = [
            models.CheckConstraint(
                name="bor_expected_gt_borrow",
                condition=Q(expected_return_date__gt=F("borrow_date")),
            ),
            models.CheckConstraint(
                name="bor_actual_null_or_gte_borrow",
                condition=Q(actual_return_date__isnull=True)
                | Q(actual_return_date__gte=F("borrow_date")),
            ),
        ]

    def __str__(self) -> str:
        return (
            f"{self.book.title} — {self.borrow_date} -> "
            f"exp: {self.expected_return_date} (user: {self.user.email})"
        )
