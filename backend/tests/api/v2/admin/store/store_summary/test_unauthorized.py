import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/summary/"


@pytest.mark.django_db
def test_unauthorized_store_summary(auth_client, event):
    """Authenticated user without store.view_storeitem permission cannot access the summary."""
    base_url = get_base_url(event.id)
    assert auth_client.get(base_url).status_code == 403
