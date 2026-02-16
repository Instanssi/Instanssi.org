import pytest
from allauth.core.exceptions import ImmediateHttpResponse
from django.test import RequestFactory

from Instanssi.users.adapters import CustomAccountAdapter
from Instanssi.users.models import User


@pytest.mark.django_db
def test_system_user_blocked_by_account_adapter():
    user = User.objects.create_user(username="systembot", password="testpass123", is_system=True)
    adapter = CustomAccountAdapter()
    request = RequestFactory().get("/")
    with pytest.raises(ImmediateHttpResponse) as exc_info:
        adapter.pre_login(
            request,
            user,
            email_verification="mandatory",
            signal_kwargs={},
            email=None,
            signup=False,
            redirect_url="/",
        )
    assert exc_info.value.response.status_code == 403


@pytest.mark.django_db
def test_normal_user_passes_account_adapter():
    user = User.objects.create_user(username="normaluser", password="testpass123", is_system=False)
    adapter = CustomAccountAdapter()
    request = RequestFactory().get("/")
    result = adapter.pre_login(
        request,
        user,
        email_verification="mandatory",
        signal_kwargs={},
        email=None,
        signup=False,
        redirect_url="/",
    )
    # pre_login returns None when no issues
    assert result is None
