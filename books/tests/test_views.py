import pytest
from decimal import Decimal
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from books.models import Book, Cover

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email="admin@example.com",
        password="adminpass123",
        is_staff=True,
        is_superuser=True,
    )


@pytest.fixture
def regular_user(db):
    return User.objects.create_user(
        email="user@example.com",
        password="userpass123",
        is_staff=False,
        is_superuser=False,
    )


@pytest.fixture
def book(db):
    return Book.objects.create(
        title="Dune",
        author="Frank Herbert",
        cover=Cover.SOFT,
        inventory=3,
        daily_fee=Decimal("2.50"),
    )


@pytest.mark.django_db
def test_list_books_is_public(api_client, book):
    url = reverse("books:book-list")
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert len(resp.data) >= 1


@pytest.mark.django_db
def test_retrieve_book_is_public(api_client, book):
    url = reverse("books:book-detail", args=[book.id])
    resp = api_client.get(url)
    assert resp.status_code == 200
    assert resp.data["id"] == book.id


@pytest.mark.django_db
def test_create_book_requires_admin(api_client, regular_user):
    url = reverse("books:book-list")
    payload = {
        "title": "The Shining",
        "author": "Stephen King",
        "cover": Cover.HARD,
        "inventory": 5,
        "daily_fee": "1.99",
    }
    resp_anon = api_client.post(url, payload, format="json")
    assert resp_anon.status_code in (401, 403)

    api_client.force_authenticate(user=regular_user)
    resp_user = api_client.post(url, payload, format="json")
    assert resp_user.status_code == 403


@pytest.mark.django_db
def test_create_book_admin_ok(api_client, admin_user):
    url = reverse("books:book-list")
    payload = {
        "title": "It",
        "author": "Stephen King",
        "cover": Cover.SOFT,
        "inventory": 2,
        "daily_fee": "1.50",
    }
    api_client.force_authenticate(user=admin_user)
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == 201
    assert resp.data["title"] == "It"


@pytest.mark.django_db
def test_update_book_admin_only(api_client, admin_user, regular_user, book):
    url = reverse("books:book-detail", args=[book.id])
    payload = {"inventory": 10}

    api_client.force_authenticate(user=regular_user)
    resp_user = api_client.patch(url, payload, format="json")
    assert resp_user.status_code == 403

    api_client.force_authenticate(user=admin_user)
    resp_admin = api_client.patch(url, payload, format="json")
    assert resp_admin.status_code == 200
    assert resp_admin.data["inventory"] == 10


@pytest.mark.django_db
def test_delete_book_admin_only(api_client, admin_user, regular_user, book):
    url = reverse("books:book-detail", args=[book.id])

    api_client.force_authenticate(user=regular_user)
    resp_user = api_client.delete(url)
    assert resp_user.status_code == 403

    api_client.force_authenticate(user=admin_user)
    resp_admin = api_client.delete(url)
    assert resp_admin.status_code == 204


@pytest.mark.django_db
def test_filter_search_ordering(api_client, db):
    Book.objects.create(
        title="The Shining",
        author="Stephen King",
        cover=Cover.HARD,
        inventory=5,
        daily_fee=Decimal("1.99"),
    )
    Book.objects.create(
        title="Doctor Sleep",
        author="Stephen King",
        cover=Cover.SOFT,
        inventory=1,
        daily_fee=Decimal("2.50"),
    )
    Book.objects.create(
        title="Dune",
        author="Frank Herbert",
        cover=Cover.SOFT,
        inventory=3,
        daily_fee=Decimal("2.00"),
    )

    base = reverse("books:book-list")

    resp_cover = api_client.get(base, {"cover": Cover.SOFT})
    assert resp_cover.status_code == 200
    assert all(item["cover"] == Cover.SOFT for item in resp_cover.data)

    resp_author_icontains = api_client.get(base, {"author__icontains": "king"})
    assert resp_author_icontains.status_code == 200
    assert all("king" in item["author"].lower() for item in resp_author_icontains.data)

    resp_search = api_client.get(base, {"search": "dune"})
    assert resp_search.status_code == 200
    assert any(item["title"].lower() == "dune" for item in resp_search.data)

    resp_order = api_client.get(base, {"ordering": "-daily_fee"})
    assert resp_order.status_code == 200
    fees = [Decimal(str(item["daily_fee"])) for item in resp_order.data]
    assert fees == sorted(fees, reverse=True)
