import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_register_creates_user_and_default_workspace():
    client = APIClient()
    response = client.post(
        "/api/v1/identity/register/",
        {"email": "pytest-user@scicreate.com", "password": "a-strong-password-1", "display_name": "Pytest User"},
        format="json",
    )
    assert response.status_code == 201
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_duplicate_email_registration_rejected():
    client = APIClient()
    payload = {"email": "dupe@scicreate.com", "password": "a-strong-password-1"}
    first = client.post("/api/v1/identity/register/", payload, format="json")
    assert first.status_code == 201

    second = client.post("/api/v1/identity/register/", payload, format="json")
    assert second.status_code == 400


@pytest.mark.django_db
def test_login_and_me_endpoint():
    client = APIClient()
    client.post(
        "/api/v1/identity/register/",
        {"email": "login-test@scicreate.com", "password": "a-strong-password-1"},
        format="json",
    )

    login_response = client.post(
        "/api/v1/identity/login/",
        {"email": "login-test@scicreate.com", "password": "a-strong-password-1"},
        format="json",
    )
    assert login_response.status_code == 200
    access_token = login_response.data["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    me_response = client.get("/api/v1/identity/me/")
    assert me_response.status_code == 200
    assert me_response.data["user"]["email"] == "login-test@scicreate.com"
    assert len(me_response.data["workspaces"]) == 1


@pytest.mark.django_db
def test_health_endpoint():
    client = APIClient()
    response = client.get("/api/v1/system/health/")
    assert response.status_code == 200
    assert response.data["status"] == "ok"
