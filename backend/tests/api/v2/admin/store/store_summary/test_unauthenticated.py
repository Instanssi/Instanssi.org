import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/summary/"


@pytest.mark.django_db
def test_unauthenticated_store_summary(api_client, event):
    """Unauthenticated users cannot access the store summary endpoint."""
    base_url = get_base_url(event.id)
    assert api_client.get(base_url).status_code == 401
