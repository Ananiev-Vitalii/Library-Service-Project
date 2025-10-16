from django.contrib import admin
from books.models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "cover", "inventory", "daily_fee")
    list_display_links = ("id", "title")
    list_filter = ("cover", "author")
    search_fields = ("title", "author")
    ordering = ("title", "author")
