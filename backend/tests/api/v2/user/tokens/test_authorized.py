"""Tests for authorized access to tokens endpoint."""

from datetime import datetime, timedelta, timezone

import pytest
from knox.crypto import create_token_string, hash_token
from knox.models import AuthToken
from knox.settings import CONSTANTS

BASE_URL = "/api/v2/tokens/"


class TestTokensList:
    """Tests for listing tokens."""

    @pytest.mark.django_db
    def test_list_own_tokens(self, staff_api_client, staff_auth_token, staff_user):
        """Test that users can list their own tokens."""
        result = staff_api_client.get(BASE_URL)
        assert result.status_code == 200
        assert len(result.data) == 1
        assert result.data[0]["pk"] == str(staff_auth_token.pk)
        assert result.data[0]["token_key"] == staff_auth_token.token_key
        assert result.data[0]["user"] == staff_user.id

    @pytest.mark.django_db
    def test_user_cannot_see_others_tokens(self, staff_api_client, staff_auth_token, other_user_auth_token):
        """Test that users cannot see other users' tokens."""
        result = staff_api_client.get(BASE_URL)
        assert result.status_code == 200
        # Should only see their own token, not the other user's token
        assert len(result.data) == 1
        assert result.data[0]["pk"] == str(staff_auth_token.pk)

    @pytest.mark.django_db
    def test_empty_list_when_no_tokens(self, staff_api_client):
        """Test that empty list is returned when user has no tokens."""
        result = staff_api_client.get(BASE_URL)
        assert result.status_code == 200
        assert len(result.data) == 0
        assert result.data == []


class TestTokensCreate:
    """Tests for creating tokens."""

    @pytest.mark.django_db
    def test_create_token(self, staff_api_client):
        """Test creating a new token."""
        expiry = datetime.now(timezone.utc) + timedelta(days=30)
        result = staff_api_client.post(
            f"{BASE_URL}create/",
            {"expiry": expiry.isoformat()},
        )
        assert result.status_code == 201
        assert "token" in result.data
        assert "pk" in result.data
        assert "token_key" in result.data
        # The full token should be 64 characters
        assert len(result.data["token"]) == 64

    @pytest.mark.django_db
    def test_create_token_stores_in_database(self, staff_api_client, staff_user):
        """Test that created token is stored in database."""
        expiry = datetime.now(timezone.utc) + timedelta(days=30)
        result = staff_api_client.post(
            f"{BASE_URL}create/",
            {"expiry": expiry.isoformat()},
        )
        assert result.status_code == 201
        # Verify token was stored
        token = AuthToken.objects.get(pk=result.data["pk"])
        assert token.user == staff_user
        assert token.token_key == result.data["token_key"]

    @pytest.mark.django_db
    def test_create_token_requires_expiry(self, staff_api_client):
        """Test that expiry field is required."""
        result = staff_api_client.post(f"{BASE_URL}create/", {})
        assert result.status_code == 400
        assert "expiry" in result.data

    @pytest.mark.django_db
    def test_create_token_expiry_must_be_future(self, staff_api_client):
        """Test that expiry must be in the future."""
        expiry = datetime.now(timezone.utc) - timedelta(days=1)
        result = staff_api_client.post(
            f"{BASE_URL}create/",
            {"expiry": expiry.isoformat()},
        )
        assert result.status_code == 400
        assert "expiry" in result.data


class TestTokensDelete:
    """Tests for deleting tokens."""

    @pytest.mark.django_db
    def test_delete_own_token(self, staff_api_client, staff_auth_token):
        """Test that users can delete their own tokens."""
        result = staff_api_client.delete(f"{BASE_URL}{staff_auth_token.pk}/")
        assert result.status_code == 204
        assert not AuthToken.objects.filter(pk=staff_auth_token.pk).exists()

    @pytest.mark.django_db
    def test_user_cannot_delete_others_token(self, staff_api_client, other_user_auth_token):
        """Test that users cannot delete other users' tokens."""
        result = staff_api_client.delete(f"{BASE_URL}{other_user_auth_token.pk}/")
        assert result.status_code == 404
        # Token should still exist
        assert AuthToken.objects.filter(pk=other_user_auth_token.pk).exists()

    @pytest.mark.django_db
    def test_delete_nonexistent_token(self, staff_api_client):
        """Test deleting a token that doesn't exist."""
        result = staff_api_client.delete(f"{BASE_URL}nonexistent-pk/")
        assert result.status_code == 404


class TestTokenOrdering:
    """Tests for token ordering."""

    @pytest.mark.django_db
    def test_tokens_ordered_by_created_desc_default(self, staff_api_client, staff_user):
        """Test that tokens are ordered by created date descending by default."""
        # Create tokens with slight delay to ensure different timestamps
        token1_string = create_token_string()
        token1 = AuthToken(
            user=staff_user,
            digest=hash_token(token1_string),
            token_key=token1_string[: CONSTANTS.TOKEN_KEY_LENGTH],
            expiry=datetime.now(timezone.utc) + timedelta(days=7),
        )
        token1.save()

        token2_string = create_token_string()
        token2 = AuthToken(
            user=staff_user,
            digest=hash_token(token2_string),
            token_key=token2_string[: CONSTANTS.TOKEN_KEY_LENGTH],
            expiry=datetime.now(timezone.utc) + timedelta(days=7),
        )
        token2.save()

        result = staff_api_client.get(BASE_URL)
        assert result.status_code == 200
        # Most recently created should be first (descending order)
        assert result.data[0]["pk"] == str(token2.pk)
        assert result.data[1]["pk"] == str(token1.pk)
