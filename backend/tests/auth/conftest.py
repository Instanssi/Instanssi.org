from pytest import fixture
from rest_framework.test import APIClient


@fixture
def headless_client() -> APIClient:
    """API client for testing allauth headless endpoints."""
    return APIClient()
