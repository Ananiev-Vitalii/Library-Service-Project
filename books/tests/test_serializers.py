import pytest
from decimal import Decimal
from books.serializers import BookSerializer
from books.models import Book, Cover


@pytest.mark.django_db
def test_serializer_valid_data():
    data = {
        "title": "The Shining",
        "author": "Stephen King",
        "cover": Cover.HARD,
        "inventory": 5,
        "daily_fee": "1.99",
    }
    s = BookSerializer(data=data)
    assert s.is_valid(), s.errors
    instance = s.save()
    assert isinstance(instance, Book)
    assert instance.daily_fee == Decimal("1.99")


@pytest.mark.django_db
def test_serializer_inventory_must_be_at_least_one():
    data = {
        "title": "Zero Inv",
        "author": "A",
        "cover": Cover.SOFT,
        "inventory": 0,
        "daily_fee": "1.00",
    }
    s = BookSerializer(data=data)
    assert not s.is_valid()
    assert "inventory" in s.errors


@pytest.mark.django_db
def test_serializer_daily_fee_must_be_positive():
    data = {
        "title": "Zero Fee",
        "author": "B",
        "cover": Cover.HARD,
        "inventory": 1,
        "daily_fee": "0.00",
    }
    s = BookSerializer(data=data)
    assert not s.is_valid()
    assert "daily_fee" in s.errors


@pytest.mark.django_db
def test_serializer_unique_together_title_author_cover():
    Book.objects.create(
        title="Dune",
        author="Frank Herbert",
        cover=Cover.SOFT,
        inventory=2,
        daily_fee=Decimal("2.50"),
    )

    dup = {
        "title": "Dune",
        "author": "Frank Herbert",
        "cover": Cover.SOFT,
        "inventory": 1,
        "daily_fee": "2.50",
    }
    s = BookSerializer(data=dup)
    assert not s.is_valid()
    errs = s.errors
    assert ("non_field_errors" in errs) or ("__all__" in errs)
