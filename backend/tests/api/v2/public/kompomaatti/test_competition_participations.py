import pytest


def get_base_url(event_id):
    return f"/api/v2/public/event/{event_id}/kompomaatti/competition_participations/"


@pytest.mark.django_db
def test_anonymous_can_list_started_participations(api_client, started_competition_participation):
    """Test that anonymous users can list participations from started competitions."""
    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [p["id"] for p in req.data]
    assert started_competition_participation.id in ids


@pytest.mark.django_db
def test_anonymous_can_get_started_participation_detail(api_client, started_competition_participation):
    """Test that anonymous users can get participation details."""
    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert req.status_code == 200
    assert req.data["id"] == started_competition_participation.id


@pytest.mark.django_db
def test_anonymous_cannot_see_non_started_participations(api_client, competition_participation):
    """Test that participations from non-started competitions are not visible."""
    base_url = get_base_url(competition_participation.competition.event_id)

    # Not in list
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [p["id"] for p in req.data]
    assert competition_participation.id not in ids

    # Not in detail
    req = api_client.get(f"{base_url}{competition_participation.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
def test_public_entry_does_not_expose_sensitive_fields(api_client, started_competition_participation):
    """Test that public endpoint does not expose sensitive/staff-only fields."""
    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert req.status_code == 200
    assert "user" not in req.data
    assert "disqualified_reason" not in req.data


@pytest.mark.django_db
def test_public_cannot_see_score_rank_before_results_shown(api_client, started_competition_participation):
    """Test that score/rank are hidden when show_results is False."""
    started_competition_participation.competition.show_results = False
    started_competition_participation.competition.save()

    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert req.status_code == 200
    assert req.data["score"] is None
    assert req.data["rank"] is None


@pytest.mark.django_db
def test_public_can_see_score_rank_after_results_shown(api_client, started_competition_participation):
    """Test that score/rank are visible when show_results is True."""
    started_competition_participation.competition.show_results = True
    started_competition_participation.competition.save()

    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert req.status_code == 200
    assert req.data["score"] is not None
    assert req.data["rank"] is not None


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
def test_anonymous_cannot_modify_participations(
    api_client, started_competition_participation, method, status
):
    """Test that write methods return 405 on read-only endpoint."""
    base_url = get_base_url(started_competition_participation.competition.event_id)
    url = f"{base_url}{started_competition_participation.id}/"
    assert api_client.generic(method, url).status_code == status
