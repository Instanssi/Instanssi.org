import pytest
from allauth.account.models import EmailAddress
from django.test import Client

from Instanssi.users.models import User


@pytest.fixture
def user(db) -> User:
    user = User.objects.create_user(username="testuser", password="testpass123", email="test@example.com")
    EmailAddress.objects.create(user=user, email="test@example.com", verified=True, primary=True)
    return user


@pytest.fixture
def auth_client(user) -> Client:
    client = Client()
    client.login(username="testuser", password="testpass123")
    return client
