from unittest.mock import patch

import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/vote_code_requests/"


@pytest.mark.django_db
def test_list_own_requests(auth_client, vote_code_request):
    """Test that users can list their own vote code requests."""
    base_url = get_base_url(vote_code_request.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    # Response is a list when no pagination params
    assert len(req.data) == 1
    assert req.data[0]["id"] == vote_code_request.id


@pytest.mark.django_db
def test_get_own_request(auth_client, vote_code_request):
    """Test that users can retrieve their own vote code request."""
    base_url = get_base_url(vote_code_request.event_id)
    req = auth_client.get(f"{base_url}{vote_code_request.id}/")
    assert req.status_code == 200
    data = req.data
    assert data["id"] == vote_code_request.id
    assert data["event"] == vote_code_request.event_id
    assert data["text"] == vote_code_request.text
    assert data["status"] == vote_code_request.status


@pytest.mark.django_db
def test_create_request(auth_client, event):
    """Test that users can create a vote code request and notification task runs."""
    from Instanssi.notifications.models import SentNotification

    base_url = get_base_url(event.id)
    with patch("Instanssi.notifications.tasks.webpush"):
        req = auth_client.post(
            base_url,
            data={
                "event": event.id,
                "text": "Please give me a vote code, I promise to vote responsibly!",
            },
        )
    assert req.status_code == 201
    assert req.data["event"] == event.id
    assert req.data["text"] == "Please give me a vote code, I promise to vote responsibly!"
    assert req.data["status"] == 0  # Pending by default

    # Verify the notification task ran and created a dedup record
    vcr_id = req.data["id"]
    assert SentNotification.objects.filter(notification_key=f"vcr:{vcr_id}").exists()


@pytest.mark.django_db
def test_update_own_request_text(auth_client, vote_code_request):
    """Test that users can update the text of their own request."""
    base_url = get_base_url(vote_code_request.event_id)
    instance_url = f"{base_url}{vote_code_request.id}/"
    req = auth_client.patch(
        instance_url,
        data={
            "text": "Updated request text with more details",
        },
    )
    assert req.status_code == 200
    assert req.data["text"] == "Updated request text with more details"


@pytest.mark.django_db
def test_cannot_update_status(auth_client, vote_code_request):
    """Test that users cannot change the status of their request."""
    base_url = get_base_url(vote_code_request.event_id)
    instance_url = f"{base_url}{vote_code_request.id}/"
    original_status = vote_code_request.status
    req = auth_client.patch(
        instance_url,
        data={
            "status": 1,  # Try to approve own request
        },
    )
    assert req.status_code == 200
    # Status should remain unchanged (it's read-only)
    assert req.data["status"] == original_status


@pytest.mark.django_db
def test_cannot_delete_request(auth_client, vote_code_request):
    """Test that users cannot delete their vote code requests."""
    base_url = get_base_url(vote_code_request.event_id)
    instance_url = f"{base_url}{vote_code_request.id}/"
    req = auth_client.delete(instance_url)
    # Delete is not supported
    assert req.status_code == 405


@pytest.mark.django_db
def test_cannot_create_duplicate_request(auth_client, vote_code_request):
    """Test that users cannot create multiple requests for the same event."""
    base_url = get_base_url(vote_code_request.event_id)
    req = auth_client.post(
        base_url,
        data={
            "event": vote_code_request.event_id,
            "text": "Another request for the same event",
        },
    )
    assert req.status_code == 400
    assert "already requested" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_see_other_users_requests(auth_client, other_user_vote_code_request):
    """Test that users can only see their own vote code requests."""
    base_url = get_base_url(other_user_vote_code_request.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    # Should not see the other user's request
    request_ids = [r["id"] for r in req.data]
    assert other_user_vote_code_request.id not in request_ids


@pytest.mark.django_db
def test_cannot_access_other_users_request(auth_client, other_user_vote_code_request):
    """Test that users cannot directly access another user's request."""
    base_url = get_base_url(other_user_vote_code_request.event_id)
    req = auth_client.get(f"{base_url}{other_user_vote_code_request.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
def test_filter_by_status(auth_client, approved_vote_code_request):
    """Test filtering requests by status."""
    base_url = get_base_url(approved_vote_code_request.event_id)
    req = auth_client.get(f"{base_url}?status=1")
    assert req.status_code == 200
    assert len(req.data) == 1
    assert req.data[0]["id"] == approved_vote_code_request.id
    assert req.data[0]["status"] == 1


@pytest.mark.django_db
def test_user_cannot_list_vote_code_requests_for_hidden_event(auth_client, hidden_event, base_user):
    """User should not see their vote code requests for hidden events."""
    from Instanssi.kompomaatti.models import VoteCodeRequest

    # Create a vote code request for the hidden event
    VoteCodeRequest.objects.create(
        event=hidden_event,
        user=base_user,
        text="Please give me voting rights",
        status=0,
    )
    base_url = get_base_url(hidden_event.id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) == 0


@pytest.mark.django_db
def test_user_cannot_create_vote_code_request_for_hidden_event(auth_client, hidden_event):
    """User should not be able to request vote codes for hidden events."""
    base_url = get_base_url(hidden_event.id)
    req = auth_client.post(
        base_url,
        data={
            "text": "Please give me voting rights",
        },
    )
    assert req.status_code == 400
