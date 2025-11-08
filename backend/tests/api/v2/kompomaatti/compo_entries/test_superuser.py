import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/entries/"


@pytest.mark.django_db
def test_superuser_access(super_api_client, votable_compo_entry):
    """Test that superuser has full access"""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = super_api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["id"] == votable_compo_entry.id
