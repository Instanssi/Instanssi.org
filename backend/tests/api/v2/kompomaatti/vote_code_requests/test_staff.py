import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/vote_code_requests/"


@pytest.mark.django_db
def test_staff_can_list_vote_code_requests(staff_api_client, vote_code_request):
    """Test that staff can list all vote code requests"""
    base_url = get_base_url(vote_code_request.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_vote_code_request_detail(staff_api_client, vote_code_request):
    """Test that staff can get vote code request details"""
    base_url = get_base_url(vote_code_request.event_id)
    req = staff_api_client.get(f"{base_url}{vote_code_request.id}/")
    assert req.status_code == 200
    assert req.data["id"] == vote_code_request.id
    assert req.data["user"] == vote_code_request.user_id
    assert req.data["status"] == vote_code_request.status


@pytest.mark.django_db
def test_staff_can_create_vote_code_request(staff_api_client, event, base_user):
    """Test that staff can create a vote code request"""
    base_url = get_base_url(event.id)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "user": base_user.id,
            "text": "Please give me voting rights!",
            "status": 0,
        },
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_staff_can_update_vote_code_request_status(staff_api_client, vote_code_request):
    """Test that staff can approve/reject vote code requests"""
    base_url = get_base_url(vote_code_request.event_id)
    req = staff_api_client.patch(f"{base_url}{vote_code_request.id}/", {"status": 1})
    assert req.status_code == 200
    assert req.data["status"] == 1


@pytest.mark.django_db
def test_staff_can_delete_vote_code_request(staff_api_client, vote_code_request):
    """Test that staff can delete a vote code request"""
    base_url = get_base_url(vote_code_request.event_id)
    req = staff_api_client.delete(f"{base_url}{vote_code_request.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_filter_vote_code_requests_by_status(staff_api_client, vote_code_request):
    """Test filtering vote code requests by status"""
    base_url = get_base_url(vote_code_request.event_id)
    req = staff_api_client.get(base_url, {"status": 0})
    assert req.status_code == 200
    for request in req.data:
        assert request["status"] == 0


@pytest.mark.django_db
def test_filter_vote_code_requests_by_event(staff_api_client, event, vote_code_request):
    """Test filtering vote code requests by event"""
    base_url = get_base_url(event.id)
    req = staff_api_client.get(base_url, {"event": event.id})
    assert req.status_code == 200
    for request in req.data:
        assert request["event"] == event.id


@pytest.mark.django_db
def test_filter_vote_code_requests_by_user(staff_api_client, base_user, vote_code_request):
    """Test filtering vote code requests by user"""
    base_url = get_base_url(vote_code_request.event_id)
    req = staff_api_client.get(base_url, {"user": base_user.id})
    assert req.status_code == 200
    for request in req.data:
        assert request["user"] == base_user.id


@pytest.mark.django_db
def test_vote_code_request_event_from_url_overrides_request_body_on_create(staff_api_client, event, other_event, base_user):
    """Test that event is set from URL, ignoring any value in request body."""
    base_url = get_base_url(event.id)
    req = staff_api_client.post(
        base_url,
        {
            "event": other_event.id,  # This should be ignored
            "user": base_user.id,
            "text": "Please give me voting rights!",
            "status": 0,
        },
    )
    assert req.status_code == 201
    # Event should be from URL, not request body
    assert req.data["event"] == event.id


@pytest.mark.django_db
def test_vote_code_request_event_is_readonly_on_update(staff_api_client, vote_code_request, other_event):
    """Test that event cannot be changed on update (read-only field)."""
    base_url = get_base_url(vote_code_request.event_id)
    original_event_id = vote_code_request.event_id
    req = staff_api_client.patch(
        f"{base_url}{vote_code_request.id}/",
        {"event": other_event.id},
    )
    assert req.status_code == 200
    # Event should remain unchanged (read-only)
    assert req.data["event"] == original_event_id
