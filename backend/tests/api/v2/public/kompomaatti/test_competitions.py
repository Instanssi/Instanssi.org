import pytest


def get_base_url(event_id):
    return f"/api/v2/public/event/{event_id}/kompomaatti/competitions/"


@pytest.mark.django_db
def test_anonymous_can_list_active_competitions(api_client, competition):
    """Test that anonymous users can list active competitions."""
    base_url = get_base_url(competition.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    comp_ids = [c["id"] for c in req.data]
    assert competition.id in comp_ids


@pytest.mark.django_db
def test_anonymous_can_get_active_competition_detail(api_client, competition):
    """Test that anonymous users can get active competition details."""
    base_url = get_base_url(competition.event_id)
    req = api_client.get(f"{base_url}{competition.id}/")
    assert req.status_code == 200
    assert req.data["id"] == competition.id


@pytest.mark.django_db
def test_anonymous_cannot_see_inactive_competitions(api_client, inactive_competition):
    """Test that inactive competitions are not visible."""
    base_url = get_base_url(inactive_competition.event_id)

    # Not in list
    req = api_client.get(base_url)
    assert req.status_code == 200
    comp_ids = [c["id"] for c in req.data]
    assert inactive_competition.id not in comp_ids

    # Not in detail
    req = api_client.get(f"{base_url}{inactive_competition.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 405),
        ("PUT", 405),
        ("PATCH", 405),
        ("DELETE", 405),
    ],
)
def test_anonymous_cannot_modify_competitions(api_client, competition, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    base_url = get_base_url(competition.event_id)
    url = f"{base_url}{competition.id}/"
    assert api_client.generic(method, url).status_code == status
