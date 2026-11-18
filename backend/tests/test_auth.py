"""
Unit-тесты для модуля авторизации и пользователей LitHub (apps.users).
"""
import pytest
from rest_framework import status


@pytest.mark.django_db
def test_register_user_success(api_client):
    """Проверяет регистрацию нового читателя LitHub и получение токена."""
    payload = {
        "username": "new_student",
        "email": "student@lithub.local",
        "password": "secret123",
        "password_confirm": "secret123",
    }
    response = api_client.post("/api/v1/auth/register/", payload, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "token" in response.data
    assert response.data["user"]["username"] == "new_student"
    assert response.data["user"]["role"] == "reader"


@pytest.mark.django_db
def test_login_by_username_and_email(api_client, reader_user):
    """Проверяет вход в LitHub по логину и по email."""
    resp_username = api_client.post(
        "/api/v1/auth/login/",
        {"username": "test_reader", "password": "password123"},
        format="json",
    )
    assert resp_username.status_code == status.HTTP_200_OK
    assert "token" in resp_username.data

    resp_email = api_client.post(
        "/api/v1/auth/login/",
        {"username": "reader@lithub.local", "password": "password123"},
        format="json",
    )
    assert resp_email.status_code == status.HTTP_200_OK
    assert resp_email.data["token"] == resp_username.data["token"]


@pytest.mark.django_db
def test_me_and_logout_flow(reader_client):
    """Проверяет получение профиля /api/v1/auth/me/ и выход /logout/."""
    me_response = reader_client.get("/api/v1/auth/me/")
    assert me_response.status_code == status.HTTP_200_OK
    assert me_response.data["username"] == "test_reader"

    logout_response = reader_client.post("/api/v1/auth/logout/")
    assert logout_response.status_code == status.HTTP_200_OK

    me_after_logout = reader_client.get("/api/v1/auth/me/")
    assert me_after_logout.status_code == status.HTTP_401_UNAUTHORIZED
