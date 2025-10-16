import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()
API_PREFIX = "/api/v1"


def auth_header(token: str) -> dict:
    return {"HTTP_AUTHORIZE": f"Bearer {token}"}


@pytest.mark.django_db
def test_me_requires_auth():
    client = APIClient()
    resp = client.get(f"{API_PREFIX}/users/me/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_me_get_and_update_profile():
    user = User.objects.create_user(email="me@example.com", password="StrongPass123")
    client = APIClient()
    obtain = client.post(
        f"{API_PREFIX}/users/token/",
        {"email": "me@example.com", "password": "StrongPass123"},
        format="json",
    )
    access = obtain.json()["access"]
    resp_get = client.get(f"{API_PREFIX}/users/me/", **auth_header(access))
    assert resp_get.status_code == 200
    assert resp_get.json()["email"] == "me@example.com"
    resp_patch = client.patch(
        f"{API_PREFIX}/users/me/",
        {"first_name": "NewName"},
        format="json",
        **auth_header(access),
    )
    assert resp_patch.status_code == 200
    assert resp_patch.json()["first_name"] == "NewName"
    resp_pwd = client.patch(
        f"{API_PREFIX}/users/me/",
        {"password": "NewPass12345"},
        format="json",
        **auth_header(access),
    )
    assert resp_pwd.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewPass12345")
