import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/summary/"


@pytest.mark.django_db
def test_non_staff_user_denied(auth_client, event):
    """Non-staff authenticated user is denied access."""
    base_url = get_base_url(event.id)
    assert auth_client.get(base_url).status_code == 403


@pytest.mark.django_db
def test_staff_without_view_storeitem_denied(api_client, create_user, password, event):
    """Staff user without store.view_storeitem permission is denied access."""
    user = create_user(is_staff=True)
    api_client.login(email=user.email, password=password)
    base_url = get_base_url(event.id)
    assert api_client.get(base_url).status_code == 403
    api_client.logout()
