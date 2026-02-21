from datetime import datetime, timedelta, timezone
from typing import Any, Generator

from knox.crypto import create_token_string, hash_token
from knox.models import AuthToken
from knox.settings import CONSTANTS
from pytest import fixture
from rest_framework.test import APIClient


@fixture
def api_client() -> APIClient:
    """Use this to test Django rest framework pages"""
    return APIClient()


@fixture
def auth_client(api_client, base_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(email=base_user.email, password=password)
    yield api_client
    api_client.logout()


@fixture
def user_api_client(api_client, normal_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(email=normal_user.email, password=password)
    yield api_client
    api_client.logout()


@fixture
def staff_api_client(api_client, staff_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(email=staff_user.email, password=password)
    yield api_client
    api_client.logout()


@fixture
def super_api_client(api_client, super_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(email=super_user.email, password=password)
    yield api_client
    api_client.logout()


@fixture
def staff_auth_token(staff_user) -> AuthToken:
    """Create a token for the staff_user."""
    token_string = create_token_string()
    token = AuthToken(
        user=staff_user,
        digest=hash_token(token_string),
        token_key=token_string[: CONSTANTS.TOKEN_KEY_LENGTH],
        expiry=datetime.now(timezone.utc) + timedelta(days=7),
    )
    token.save()
    return token


@fixture
def other_user_auth_token(base_user) -> AuthToken:
    """Create a token for base_user (for testing isolation)."""
    token_string = create_token_string()
    token = AuthToken(
        user=base_user,
        digest=hash_token(token_string),
        token_key=token_string[: CONSTANTS.TOKEN_KEY_LENGTH],
        expiry=datetime.now(timezone.utc) + timedelta(days=7),
    )
    token.save()
    return token
