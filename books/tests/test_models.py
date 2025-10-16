import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from books.models import Book, Cover


@pytest.fixture
def make_book(db):
    def _make_book(**overrides):
        data = {
            "title": "Dune",
            "author": "Frank Herbert",
            "cover": Cover.SOFT,
            "inventory": 3,
            "daily_fee": Decimal("1.50"),
        }
        data.update(overrides)
        return Book.objects.create(**data)

    return _make_book


@pytest.mark.django_db
def test_book_str(make_book):
    b = make_book()
    assert str(b) == "Dune — Frank Herbert"


@pytest.mark.django_db
def test_inventory_check_constraint():
    b = Book(
        title="Bad Inv",
        author="X",
        cover=Cover.HARD,
        inventory=0,
        daily_fee=Decimal("1.00"),
    )
    with pytest.raises(ValidationError):
        b.full_clean()


@pytest.mark.django_db
def test_daily_fee_check_constraint():
    b = Book(
        title="Zero fee",
        author="Y",
        cover=Cover.SOFT,
        inventory=1,
        daily_fee=Decimal("0.00"),
    )
    with pytest.raises(ValidationError):
        b.full_clean()
