import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/votes/"


@pytest.mark.django_db
def test_list_own_votes(auth_client, entry_vote_group):
    """Test that users can list their own vote groups."""
    base_url = get_base_url(entry_vote_group.compo.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) == 1
    assert req.data[0]["id"] == entry_vote_group.id


@pytest.mark.django_db
def test_get_own_vote_group(auth_client, entry_vote_group):
    """Test that users can retrieve their own vote group."""
    base_url = get_base_url(entry_vote_group.compo.event_id)
    req = auth_client.get(f"{base_url}{entry_vote_group.id}/")
    assert req.status_code == 200
    data = req.data
    assert data["id"] == entry_vote_group.id
    assert data["compo"] == entry_vote_group.compo_id
    assert "voted_entries" in data


@pytest.mark.django_db
def test_create_votes_with_ticket_code(
    auth_client, ticket_vote_code, votable_compo_entry, second_votable_entry
):
    """Test that users can vote with a ticket vote code."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo_entry.compo_id,
            "entries": [votable_compo_entry.id, second_votable_entry.id],
        },
        format="json",
    )
    assert req.status_code == 201
    assert req.data["compo"] == votable_compo_entry.compo_id
    assert req.data["voted_entries"] == [votable_compo_entry.id, second_votable_entry.id]


@pytest.mark.django_db
def test_create_votes_with_approved_request(
    auth_client, approved_vote_code_request, votable_compo, votable_compo_entry
):
    """Test that users can vote with an approved vote code request."""
    base_url = get_base_url(approved_vote_code_request.event_id)
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo.id,
            "entries": [votable_compo_entry.id],
        },
        format="json",
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_cannot_vote_without_voting_rights(auth_client, votable_compo_entry):
    """Test that users cannot vote without voting rights."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo_entry.compo_id,
            "entries": [votable_compo_entry.id],
        },
        format="json",
    )
    assert req.status_code == 400
    assert "voting rights" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_vote_with_rejected_request(
    auth_client, rejected_vote_code_request, votable_compo, votable_compo_entry
):
    """Test that users cannot vote with a rejected vote code request."""
    base_url = get_base_url(rejected_vote_code_request.event_id)
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo.id,
            "entries": [votable_compo_entry.id],
        },
        format="json",
    )
    assert req.status_code == 400
    assert "voting rights" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_vote_in_closed_compo(auth_client, ticket_vote_code, closed_compo_entry):
    """Test that users cannot vote in a closed compo."""
    base_url = get_base_url(closed_compo_entry.compo.event_id)
    req = auth_client.post(
        base_url,
        data={
            "compo": closed_compo_entry.compo_id,
            "entries": [closed_compo_entry.id],
        },
        format="json",
    )
    assert req.status_code == 400
    assert "not open" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_vote_for_entry_in_different_compo(
    auth_client, ticket_vote_code, votable_compo, open_compo, editable_compo_entry
):
    """Test that users cannot vote for entries from a different compo."""
    base_url = get_base_url(votable_compo.event_id)
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo.id,
            "entries": [editable_compo_entry.id],  # This entry belongs to open_compo
        },
        format="json",
    )
    assert req.status_code == 400
    assert "does not belong" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_vote_for_same_entry_twice(auth_client, ticket_vote_code, votable_compo_entry):
    """Test that users cannot vote for the same entry twice."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo_entry.compo_id,
            "entries": [votable_compo_entry.id, votable_compo_entry.id],  # Duplicate
        },
        format="json",
    )
    assert req.status_code == 400
    assert "once" in str(req.data).lower()


@pytest.mark.django_db
def test_resubmitting_votes_replaces_previous(
    auth_client, ticket_vote_code, votable_compo_entry, second_votable_entry, third_votable_entry
):
    """Test that resubmitting votes replaces previous votes."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)

    # Submit first votes
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo_entry.compo_id,
            "entries": [votable_compo_entry.id, second_votable_entry.id],
        },
        format="json",
    )
    assert req.status_code == 201
    vote_group_id = req.data["id"]
    assert req.data["voted_entries"] == [votable_compo_entry.id, second_votable_entry.id]

    # Resubmit with different order and entries
    req = auth_client.post(
        base_url,
        data={
            "compo": votable_compo_entry.compo_id,
            "entries": [third_votable_entry.id, votable_compo_entry.id],
        },
        format="json",
    )
    assert req.status_code == 201
    # Should use the same vote group
    assert req.data["id"] == vote_group_id
    assert req.data["voted_entries"] == [third_votable_entry.id, votable_compo_entry.id]


@pytest.mark.django_db
def test_cannot_update_vote_group(auth_client, entry_vote_group, votable_compo_entry):
    """Test that users cannot update vote groups (use POST to resubmit instead)."""
    base_url = get_base_url(entry_vote_group.compo.event_id)
    instance_url = f"{base_url}{entry_vote_group.id}/"
    req = auth_client.patch(
        instance_url,
        data={
            "entries": [votable_compo_entry.id],
        },
        format="json",
    )
    # Update not supported
    assert req.status_code == 405


@pytest.mark.django_db
def test_cannot_delete_vote_group(auth_client, entry_vote_group):
    """Test that users cannot delete vote groups."""
    base_url = get_base_url(entry_vote_group.compo.event_id)
    instance_url = f"{base_url}{entry_vote_group.id}/"
    req = auth_client.delete(instance_url)
    # Delete not supported
    assert req.status_code == 405


@pytest.mark.django_db
def test_cannot_see_other_users_votes(auth_client, other_user_vote_group):
    """Test that users can only see their own vote groups."""
    base_url = get_base_url(other_user_vote_group.compo.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    # Should not see the other user's vote group
    vote_group_ids = [vg["id"] for vg in req.data]
    assert other_user_vote_group.id not in vote_group_ids


@pytest.mark.django_db
def test_user_votes_filter_by_compo(
    auth_client, ticket_vote_code, votable_compo, entry_vote_group, entry_vote
):
    """Test filtering vote groups by compo."""
    base_url = get_base_url(votable_compo.event_id)
    req = auth_client.get(f"{base_url}?compo={votable_compo.id}")
    assert req.status_code == 200
    assert len(req.data) == 1
    assert req.data[0]["id"] == entry_vote_group.id
