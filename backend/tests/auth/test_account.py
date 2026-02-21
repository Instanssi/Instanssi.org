import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_login_page_renders(page_client):
    """Test that the allauth login page renders successfully."""
    response = page_client.get(reverse("account_login"))
    assert response.status_code == status.HTTP_200_OK


def test_signup_page_renders(page_client):
    """Test that the allauth signup page renders successfully."""
    response = page_client.get(reverse("account_signup"))
    assert response.status_code == status.HTTP_200_OK


def test_headless_config_endpoint(headless_client):
    """Test that the allauth headless config endpoint returns provider info."""
    response = headless_client.get("/api/v2/allauth/browser/v1/config")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "data" in data
    assert "account" in data["data"]


def test_headless_login(headless_client, base_user, password):
    """Test login via the allauth headless API."""
    response = headless_client.post(
        "/api/v2/allauth/browser/v1/auth/login",
        {"email": base_user.email, "password": password},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


def test_headless_login_wrong_password(headless_client, base_user):
    """Test login with wrong password via the allauth headless API."""
    response = headless_client.post(
        "/api/v2/allauth/browser/v1/auth/login",
        {"email": base_user.email, "password": "wrong"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_headless_session_check_unauthenticated(headless_client):
    """Test session check when not authenticated."""
    response = headless_client.get("/api/v2/allauth/browser/v1/auth/session")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_headless_session_check_authenticated(headless_client, base_user, password):
    """Test session check when authenticated via headless login."""
    headless_client.post(
        "/api/v2/allauth/browser/v1/auth/login",
        {"email": base_user.email, "password": password},
        format="json",
    )
    response = headless_client.get("/api/v2/allauth/browser/v1/auth/session")
    assert response.status_code == status.HTTP_200_OK


def test_headless_logout(headless_client, base_user, password):
    """Test logout via the allauth headless API."""
    # Login via headless API to establish proper allauth session
    login_response = headless_client.post(
        "/api/v2/allauth/browser/v1/auth/login",
        {"email": base_user.email, "password": password},
        format="json",
    )
    assert login_response.status_code == status.HTTP_200_OK
    # DELETE session returns 401 (confirms session is now destroyed)
    response = headless_client.delete("/api/v2/allauth/browser/v1/auth/session")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    # Verify session stays cleared
    response = headless_client.get("/api/v2/allauth/browser/v1/auth/session")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
