import pytest


def get_base_url(event_id, compo_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/live_voting/{compo_id}/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("PATCH", 401),
    ],
)
def test_unauthenticated_live_voting_detail(api_client, event, live_voting_compo, method, status):
    url = get_base_url(event.id, live_voting_compo.id)
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action,status",
    [
        ("reveal_entry", 401),
        ("hide_entry", 401),
        ("reveal_all", 401),
        ("reset", 401),
    ],
)
def test_unauthenticated_live_voting_actions(api_client, event, live_voting_compo, action, status):
    url = f"{get_base_url(event.id, live_voting_compo.id)}{action}/"
    assert api_client.post(url).status_code == status
