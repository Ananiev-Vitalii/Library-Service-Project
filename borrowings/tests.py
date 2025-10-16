import pytest
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.reverse import reverse

User = get_user_model()


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(email="u1@example.com", password="pass")


@pytest.fixture
def user2(db):
    return User.objects.create_user(email="u2@example.com", password="pass")


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        email="admin@example.com", password="pass", is_staff=True
    )


@pytest.fixture
def book(db):
    from books.models import Book

    return Book.objects.create(
        title="T", author="A", cover="HARD", inventory=3, daily_fee="1.50"
    )


@pytest.fixture
def make_borrowing(db):
    def _make(user, book, days=3, returned=False):
        from borrowings.models import Borrowing

        b = Borrowing.objects.create(
            user=user,
            book=book,
            borrow_date=timezone.now().date(),
            expected_return_date=(timezone.now() + timedelta(days=days)).date(),
            actual_return_date=None,
        )
        if returned:
            b.actual_return_date = timezone.now().date()
            b.save(update_fields=["actual_return_date"])
        return b

    return _make


def auth(client, user):
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_auth_required_for_list(client):
    url = reverse("borrowings:borrowing-list")
    resp = client.get(url)
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_non_admin_sees_only_own(client, user, user2, book, make_borrowing):
    b1 = make_borrowing(user, book)
    make_borrowing(user2, book)
    url = reverse("borrowings:borrowing-list")
    resp = auth(client, user).get(url)
    ids = [x["id"] for x in resp.json()]
    assert resp.status_code == 200
    assert b1.id in ids


@pytest.mark.django_db
def test_admin_sees_all_and_filter_by_user_id(
    client, admin, user, user2, book, make_borrowing
):
    b1 = make_borrowing(user, book)
    b2 = make_borrowing(user2, book)
    url = reverse("borrowings:borrowing-list")
    c = auth(client, admin)
    resp_all = c.get(url)
    assert resp_all.status_code == 200
    assert {b1.id, b2.id}.issubset({x["id"] for x in resp_all.json()})
    resp_u1 = c.get(url, {"user_id": user.id})
    ids_u1 = [x["id"] for x in resp_u1.json()]
    assert b1.id in ids_u1 and b2.id not in ids_u1


@pytest.mark.django_db
def test_is_active_filter(client, user, book, make_borrowing):
    active = make_borrowing(user, book)
    returned = make_borrowing(user, book, returned=True)
    url = reverse("borrowings:borrowing-list")
    c = auth(client, user)
    resp_active = c.get(url, {"is_active": "true"})
    resp_closed = c.get(url, {"is_active": "false"})
    ids_active = [x["id"] for x in resp_active.json()]
    ids_closed = [x["id"] for x in resp_closed.json()]
    assert active.id in ids_active and returned.id not in ids_active
    assert returned.id in ids_closed and active.id not in ids_closed


@pytest.mark.django_db
def test_create_borrowing_attaches_user_and_decreases_inventory(client, user, book):
    url = reverse("borrowings:borrowing-list")
    payload = {
        "book": book.id,
        "expected_return_date": (timezone.now() + timedelta(days=5)).date().isoformat(),
    }
    c = auth(client, user)
    inv_before = book.inventory
    resp = c.post(url, payload, format="json")
    book.refresh_from_db()
    assert resp.status_code == 201
    assert resp.json()["book"]["id"] == book.id
    assert resp.json()["user_id"] == user.id
    assert book.inventory == inv_before - 1


@pytest.mark.django_db
def test_create_borrowing_fails_when_inventory_zero(client, user, book):
    book.inventory = 0
    book.save(update_fields=["inventory"])
    url = reverse("borrowings:borrowing-list")
    payload = {
        "book": book.id,
        "expected_return_date": (timezone.now() + timedelta(days=2)).date().isoformat(),
    }
    resp = auth(client, user).post(url, payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_create_borrowing_fails_when_expected_date_not_future(client, user, book):
    url = reverse("borrowings:borrowing-list")
    payload = {
        "book": book.id,
        "expected_return_date": timezone.now().date().isoformat(),
    }
    resp = auth(client, user).post(url, payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_retrieve_borrowing(client, user, book, make_borrowing):
    b = make_borrowing(user, book)
    url = reverse("borrowings:borrowing-detail", args=[b.id])
    resp = auth(client, user).get(url)
    assert resp.status_code == 200
    assert resp.json()["id"] == b.id


@pytest.mark.django_db
def test_return_borrowing_sets_date_and_increments_inventory(
    client, user, book, make_borrowing
):
    b = make_borrowing(user, book)
    inv_before = book.inventory
    url = reverse("borrowings:borrowing-return-borrowing", args=[b.id])
    resp = auth(client, user).post(url)
    book.refresh_from_db()
    assert resp.status_code == 200
    assert resp.json()["actual_return_date"] is not None
    assert book.inventory == inv_before + 1


@pytest.mark.django_db
def test_return_borrowing_cannot_twice(client, user, book, make_borrowing):
    b = make_borrowing(user, book)
    url = reverse("borrowings:borrowing-return-borrowing", args=[b.id])
    c = auth(client, user)
    first = c.post(url)
    second = c.post(url)
    assert first.status_code == 200
    assert second.status_code == 400


@pytest.mark.django_db
def test_return_borrowing_forbidden_for_other_user(
    client, user, user2, book, make_borrowing
):
    b = make_borrowing(user, book)
    url = reverse("borrowings:borrowing-return-borrowing", args=[b.id])
    resp = auth(client, user2).post(url)
    assert resp.status_code == 403
