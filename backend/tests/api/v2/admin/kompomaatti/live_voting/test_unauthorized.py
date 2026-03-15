import pytest


def get_base_url(event_id, compo_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/live_voting/{compo_id}/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("PATCH", 403),
    ],
)
def test_unauthorized_live_voting_detail(auth_client, event, live_voting_compo, method, status):
    url = get_base_url(event.id, live_voting_compo.id)
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action,status",
    [
        ("reveal_entry", 403),
        ("hide_entry", 403),
        ("reveal_all", 403),
        ("hide_all", 403),
        ("reset", 403),
    ],
)
def test_unauthorized_live_voting_actions(auth_client, event, live_voting_compo, action, status):
    url = f"{get_base_url(event.id, live_voting_compo.id)}{action}/"
    assert auth_client.post(url).status_code == status
