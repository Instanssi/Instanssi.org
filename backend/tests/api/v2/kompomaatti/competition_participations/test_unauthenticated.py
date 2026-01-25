import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/competition_participations/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 200),  # Public can read list when competition started
        (True, "GET", 200),  # Public can read detail when competition started
        (False, "POST", 401),
        (True, "DELETE", 401),
        (True, "PATCH", 401),
        (True, "PUT", 401),
    ],
)
def test_unauthenticated_competition_participations(
    api_client, event, started_competition_participation, obj, method, status
):
    """Test unauthenticated access (Not logged in). GET is allowed after competition starts."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{started_competition_participation.id}/" if obj else base_url
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthenticated_cannot_see_non_started_participations(api_client, competition_participation):
    """Test that unauthenticated users cannot see participations before competition has started"""
    base_url = get_base_url(competition_participation.competition.event_id)

    # Participation should not appear in list view
    list_req = api_client.get(base_url)
    assert list_req.status_code == 200
    participation_ids = [p["id"] for p in list_req.data]
    assert competition_participation.id not in participation_ids

    # Detail view should return 404
    detail_req = api_client.get(f"{base_url}{competition_participation.id}/")
    assert detail_req.status_code == 404


@pytest.mark.django_db
def test_unauthenticated_can_see_started_participations(api_client, started_competition_participation):
    """Test that unauthenticated users can see participations when competition has started"""
    base_url = get_base_url(started_competition_participation.competition.event_id)

    # Participation should appear in list view
    list_req = api_client.get(base_url)
    assert list_req.status_code == 200
    participation_ids = [p["id"] for p in list_req.data]
    assert started_competition_participation.id in participation_ids

    # Detail view should return 200
    detail_req = api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert detail_req.status_code == 200


@pytest.mark.django_db
def test_public_cannot_see_score_rank_before_results_shown(api_client, started_competition_participation):
    """Test that public users cannot see score/rank before show_results is enabled"""
    started_competition_participation.competition.show_results = False
    started_competition_participation.competition.save()

    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert req.status_code == 200
    assert req.data["score"] is None
    assert req.data["rank"] is None


@pytest.mark.django_db
def test_public_can_see_score_rank_after_results_shown(api_client, started_competition_participation):
    """Test that public users can see score/rank when show_results is enabled"""
    started_competition_participation.competition.show_results = True
    started_competition_participation.competition.save()

    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert req.status_code == 200
    assert req.data["score"] is not None
    assert req.data["rank"] is not None
