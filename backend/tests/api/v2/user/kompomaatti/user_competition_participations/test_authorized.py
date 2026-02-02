import pytest

from Instanssi.kompomaatti.models import CompetitionParticipation


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/participations/"


@pytest.mark.django_db
def test_list_own_participations(auth_client, competition_participation):
    """Test that users can list their own participations."""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    # Response is a list when no pagination params
    assert len(req.data) == 1
    assert req.data[0]["id"] == competition_participation.id


@pytest.mark.django_db
def test_get_own_participation(auth_client, competition_participation):
    """Test that users can retrieve their own participation."""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = auth_client.get(f"{base_url}{competition_participation.id}/")
    assert req.status_code == 200
    data = req.data
    assert data["id"] == competition_participation.id
    assert data["competition"] == competition_participation.competition_id
    assert data["participant_name"] == competition_participation.participant_name


@pytest.mark.django_db
def test_create_participation(auth_client, competition):
    """Test that users can create a participation in an open competition."""
    base_url = get_base_url(competition.event_id)
    req = auth_client.post(
        base_url,
        data={
            "competition": competition.id,
            "participant_name": "Test Participant",
        },
    )
    assert req.status_code == 201
    assert req.data["competition"] == competition.id
    assert req.data["participant_name"] == "Test Participant"


@pytest.mark.django_db
def test_update_own_participation(auth_client, competition_participation):
    """Test that users can update their own participation."""
    base_url = get_base_url(competition_participation.competition.event_id)
    instance_url = f"{base_url}{competition_participation.id}/"
    req = auth_client.patch(
        instance_url,
        data={
            "participant_name": "Updated Participant Name",
        },
    )
    assert req.status_code == 200
    assert req.data["participant_name"] == "Updated Participant Name"


@pytest.mark.django_db
def test_delete_own_participation(auth_client, competition_participation):
    """Test that users can delete their own participation."""
    base_url = get_base_url(competition_participation.competition.event_id)
    instance_url = f"{base_url}{competition_participation.id}/"
    req = auth_client.delete(instance_url)
    assert req.status_code == 204
    assert not CompetitionParticipation.objects.filter(id=competition_participation.id).exists()


@pytest.mark.django_db
def test_cannot_create_after_deadline(auth_client, started_competition):
    """Test that participations cannot be created after the participation deadline."""
    base_url = get_base_url(started_competition.event_id)
    req = auth_client.post(
        base_url,
        data={
            "competition": started_competition.id,
            "participant_name": "Late Participant",
        },
    )
    assert req.status_code == 400
    assert "participation time has ended" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_update_after_deadline(auth_client, started_competition_participation):
    """Test that participations cannot be updated after the participation deadline."""
    base_url = get_base_url(started_competition_participation.competition.event_id)
    instance_url = f"{base_url}{started_competition_participation.id}/"
    req = auth_client.patch(
        instance_url,
        data={
            "participant_name": "Should not work",
        },
    )
    assert req.status_code == 400
    assert "participation time has ended" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_delete_after_deadline(auth_client, started_competition_participation):
    """Test that participations cannot be deleted after the participation deadline."""
    base_url = get_base_url(started_competition_participation.competition.event_id)
    instance_url = f"{base_url}{started_competition_participation.id}/"
    req = auth_client.delete(instance_url)
    assert req.status_code == 400
    assert "participation time has ended" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_create_duplicate_participation(auth_client, competition_participation):
    """Test that users cannot participate twice in the same competition."""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = auth_client.post(
        base_url,
        data={
            "competition": competition_participation.competition_id,
            "participant_name": "Duplicate Participant",
        },
    )
    assert req.status_code == 400
    assert "already participated" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_see_other_users_participations(auth_client, other_user_competition_participation):
    """Test that users can only see their own participations."""
    base_url = get_base_url(other_user_competition_participation.competition.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    # Should not see the other user's participation (response is a list)
    participation_ids = [p["id"] for p in req.data]
    assert other_user_competition_participation.id not in participation_ids


@pytest.mark.django_db
def test_cannot_access_participation_in_inactive_competition(
    auth_client, inactive_competition_participation
):
    """Test that participations in inactive competitions are not accessible."""
    base_url = get_base_url(inactive_competition_participation.competition.event_id)

    # List should not include the participation (response is a list)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    participation_ids = [p["id"] for p in req.data]
    assert inactive_competition_participation.id not in participation_ids

    # Direct access should return 404
    req = auth_client.get(f"{base_url}{inactive_competition_participation.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
def test_cannot_create_participation_in_inactive_competition(auth_client, inactive_competition):
    """Test that participations cannot be created in inactive competitions."""
    base_url = get_base_url(inactive_competition.event_id)
    req = auth_client.post(
        base_url,
        data={
            "competition": inactive_competition.id,
            "participant_name": "Should Fail",
        },
    )
    # The competition should not be in the queryset, so validation fails
    assert req.status_code == 400


@pytest.mark.django_db
def test_user_participations_filter_by_competition(auth_client, competition_participation):
    """Test filtering participations by competition."""
    base_url = get_base_url(competition_participation.competition.event_id)
    req = auth_client.get(f"{base_url}?competition={competition_participation.competition_id}")
    assert req.status_code == 200
    # Response is a list when no pagination params
    assert len(req.data) == 1
    assert req.data[0]["id"] == competition_participation.id


@pytest.mark.django_db
def test_user_cannot_create_participation_for_other_event_competition(auth_client, event, other_competition):
    """Test that user cannot create participation with competition from another event."""
    base_url = get_base_url(event.id)
    req = auth_client.post(
        base_url,
        {
            "competition": other_competition.id,
            "participant_name": "Test Participant",
        },
    )
    assert req.status_code == 400
    assert "competition" in req.data


@pytest.mark.django_db
def test_user_cannot_list_participations_for_hidden_event(
    auth_client, hidden_event, hidden_event_competition, hidden_event_participation
):
    """User should not see their participations for hidden events."""
    base_url = get_base_url(hidden_event.id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) == 0


@pytest.mark.django_db
def test_user_cannot_create_participation_for_hidden_event(
    auth_client, hidden_event, hidden_event_competition
):
    """User should not be able to participate in hidden events."""
    base_url = get_base_url(hidden_event.id)
    req = auth_client.post(
        base_url,
        data={
            "competition": hidden_event_competition.id,
            "participant_name": "Test Participant",
        },
    )
    assert req.status_code == 400
