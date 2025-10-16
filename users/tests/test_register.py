import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
API_PREFIX = "/api/v1"


@pytest.mark.django_db
def test_register_creates_user_and_hashes_password():
    client = APIClient()
    payload = {
        "email": "alice@example.com",
        "first_name": "Alice",
        "last_name": "Wonder",
        "password": "StrongPass123",
    }
    resp = client.post(f"{API_PREFIX}/users/", payload, format="json")
    assert resp.status_code == 201
    user = User.objects.get(email="alice@example.com")
    assert user.password != payload["password"]
    assert user.check_password(payload["password"])


@pytest.mark.django_db
def test_register_disallows_setting_is_staff():
    client = APIClient()
    payload = {
        "email": "bob@example.com",
        "first_name": "Bob",
        "last_name": "Builder",
        "password": "StrongPass123",
        "is_staff": True,
    }
    resp = client.post(f"{API_PREFIX}/users/", payload, format="json")
    assert resp.status_code == 201
    user = User.objects.get(email="bob@example.com")
    assert user.is_staff is False


@pytest.mark.django_db
def test_register_min_password_length():
    client = APIClient()
    payload = {
        "email": "short@example.com",
        "first_name": "Short",
        "last_name": "Pass",
        "password": "1234567",
    }
    resp = client.post(f"{API_PREFIX}/users/", payload, format="json")
    assert resp.status_code == 400


@pytest.mark.django_db
def test_register_duplicate_email_400():
    User.objects.create_user(email="dupe@example.com", password="StrongPass123")
    client = APIClient()
    payload = {
        "email": "dupe@example.com",
        "first_name": "Dupe",
        "last_name": "Case",
        "password": "StrongPass123",
    }
    resp = client.post(f"{API_PREFIX}/users/", payload, format="json")
    assert resp.status_code == 400
