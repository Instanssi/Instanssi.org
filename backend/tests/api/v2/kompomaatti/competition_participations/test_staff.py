import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/competition_participations/"


@pytest.mark.django_db
def test_staff_can_list_participations(staff_api_client, competition_participation):
    """Test that staff can list all competition participations"""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_participation_detail(staff_api_client, competition_participation):
    """Test that staff can get participation details"""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = staff_api_client.get(f"{base_url}{competition_participation.id}/")
    assert req.status_code == 200
    assert req.data["id"] == competition_participation.id
    assert req.data["competition"] == competition_participation.competition_id
    assert req.data["user"] == competition_participation.user_id
    assert "rank" in req.data


@pytest.mark.django_db
def test_staff_can_create_participation(staff_api_client, competition, base_user):
    """Test that staff can create new competition participation"""
    base_url = get_base_url(competition.event_id)
    req = staff_api_client.post(
        base_url,
        {
            "competition": competition.id,
            "user": base_user.id,
            "participant_name": "Test Participant",
            "score": 100.5,
        },
    )
    assert req.status_code == 201
    assert req.data["participant_name"] == "Test Participant"
    assert req.data["score"] == 100.5


@pytest.mark.django_db
def test_staff_can_update_participation(staff_api_client, competition_participation):
    """Test that staff can update competition participation"""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = staff_api_client.patch(
        f"{base_url}{competition_participation.id}/",
        {"score": 250.0, "disqualified": True, "disqualified_reason": "Test disqualification"},
    )
    assert req.status_code == 200
    assert req.data["score"] == 250.0
    assert req.data["disqualified"] is True


@pytest.mark.django_db
def test_staff_can_delete_participation(staff_api_client, competition_participation):
    """Test that staff can delete competition participation"""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = staff_api_client.delete(f"{base_url}{competition_participation.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_participation_includes_rank(staff_api_client, competition_participation):
    """Test that participation includes calculated rank"""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = staff_api_client.get(f"{base_url}{competition_participation.id}/")
    assert req.status_code == 200
    assert "rank" in req.data


@pytest.mark.django_db
def test_participations_filter_by_competition(staff_api_client, competition, competition_participation):
    """Test filtering participations by competition"""
    base_url = get_base_url(competition.event_id)
    req = staff_api_client.get(base_url, {"competition": competition.id})
    assert req.status_code == 200
    for part in req.data:
        assert part["competition"] == competition.id


@pytest.mark.django_db
def test_participations_filter_by_user(staff_api_client, base_user, competition_participation):
    """Test filtering participations by user"""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = staff_api_client.get(base_url, {"user": base_user.id})
    assert req.status_code == 200
    for part in req.data:
        assert part["user"] == base_user.id


@pytest.mark.django_db
def test_staff_can_always_see_participation_score_rank(staff_api_client, started_competition_participation):
    """Test that staff users can always see score/rank regardless of show_results"""
    started_competition_participation.competition.show_results = False
    started_competition_participation.competition.save()

    base_url = get_base_url(started_competition_participation.competition.event_id)
    req = staff_api_client.get(f"{base_url}{started_competition_participation.id}/")
    assert req.status_code == 200
    assert req.data["score"] is not None
    assert req.data["rank"] is not None


@pytest.mark.django_db
def test_staff_cannot_create_participation_for_other_event_competition(
    staff_api_client, event, base_user, other_competition
):
    """Test that staff cannot create participation with competition from another event."""
    base_url = get_base_url(event.id)
    req = staff_api_client.post(
        base_url,
        {
            "competition": other_competition.id,
            "user": base_user.id,
            "participant_name": "Test Participant",
        },
    )
    assert req.status_code == 400
    assert "competition" in req.data


@pytest.mark.django_db
def test_cannot_update_participation_to_other_event_competition(
    staff_api_client, competition_participation, other_competition
):
    """Test that staff cannot update participation to use competition from another event."""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = staff_api_client.patch(
        f"{base_url}{competition_participation.id}/",
        {"competition": other_competition.id},
    )
    assert req.status_code == 400
    assert "competition" in req.data
