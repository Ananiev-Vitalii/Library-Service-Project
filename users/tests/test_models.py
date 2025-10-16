import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_user_manager_creates_user_with_email_as_username_field():
    user = User.objects.create_user(email="mgr@example.com", password="StrongPass123")
    assert user.email == "mgr@example.com"
    assert not hasattr(user, "username") or getattr(user, "username", None) in (
        None,
        "",
    )


@pytest.mark.django_db
def test_user_manager_creates_superuser_with_flags():
    su = User.objects.create_superuser(
        email="admin@example.com", password="StrongPass123"
    )
    assert su.is_staff is True
    assert su.is_superuser is True
