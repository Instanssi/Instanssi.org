from typing import Any, Generator

from pytest import fixture
from rest_framework.test import APIClient


@fixture
def api_client() -> APIClient:
    """Use this to test Django rest framework pages"""
    return APIClient()


@fixture
def auth_client(api_client, base_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(username=base_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def user_api_client(api_client, normal_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(username=normal_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def staff_api_client(api_client, staff_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(username=staff_user.username, password=password)
    yield api_client
    api_client.logout()


@fixture
def super_api_client(api_client, super_user, password) -> Generator[APIClient, Any, None]:
    api_client.login(username=super_user.username, password=password)
    yield api_client
    api_client.logout()
