from django.contrib import admin
from borrowings.models import Borrowing


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "user",
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
    )

    list_filter = (
        "borrow_date",
        "expected_return_date",
        "actual_return_date",
        "user",
        "book",
    )

    search_fields = (
        "book__title",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    date_hierarchy = "borrow_date"
    ordering = ("-borrow_date", "id")
    list_select_related = ("book", "user")
    autocomplete_fields = ("book", "user")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "book",
                    "user",
                    ("borrow_date", "expected_return_date", "actual_return_date"),
                )
            },
        ),
    )
