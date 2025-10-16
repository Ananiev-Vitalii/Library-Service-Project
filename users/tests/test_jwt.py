import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
API_PREFIX = "/api/v1"


@pytest.mark.django_db
def test_obtain_token_with_email_and_password():
    User.objects.create_user(email="u@example.com", password="StrongPass123")
    client = APIClient()
    resp = client.post(
        f"{API_PREFIX}/users/token/",
        {"email": "u@example.com", "password": "StrongPass123"},
        format="json",
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access" in data and "refresh" in data


@pytest.mark.django_db
def test_obtain_token_wrong_credentials_401():
    User.objects.create_user(email="u2@example.com", password="StrongPass123")
    client = APIClient()
    resp = client.post(
        f"{API_PREFIX}/users/token/",
        {"email": "u2@example.com", "password": "wrong"},
        format="json",
    )
    assert resp.status_code in (400, 401)


@pytest.mark.django_db
def test_refresh_token_returns_new_access():
    User.objects.create_user(email="u3@example.com", password="StrongPass123")
    client = APIClient()
    obtain = client.post(
        f"{API_PREFIX}/users/token/",
        {"email": "u3@example.com", "password": "StrongPass123"},
        format="json",
    )
    refresh = obtain.json()["refresh"]
    resp = client.post(
        f"{API_PREFIX}/users/token/refresh/",
        {"refresh": refresh},
        format="json",
    )
    assert resp.status_code == 200
    assert "access" in resp.json()
