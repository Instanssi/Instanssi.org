import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/ticket_vote_codes/"


@pytest.mark.django_db
def test_staff_can_list_ticket_vote_codes(staff_api_client, ticket_vote_code):
    """Test that staff can list all ticket vote codes"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_ticket_vote_code_detail(staff_api_client, ticket_vote_code):
    """Test that staff can get ticket vote code details"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.get(f"{base_url}{ticket_vote_code.id}/")
    assert req.status_code == 200
    assert req.data["id"] == ticket_vote_code.id
    assert "associated_username" in req.data


@pytest.mark.django_db
def test_ticket_vote_code_create_not_allowed(staff_api_client, event, base_user, transaction_item_a):
    """Test that create is not allowed (viewset is read-only)"""
    base_url = get_base_url(event.id)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "associated_to": base_user.id,
            "ticket": transaction_item_a.id,
        },
    )
    assert req.status_code == 405


@pytest.mark.django_db
def test_ticket_vote_code_update_not_allowed(staff_api_client, ticket_vote_code, normal_user):
    """Test that update is not allowed (viewset is read-only)"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.patch(f"{base_url}{ticket_vote_code.id}/", {"associated_to": normal_user.id})
    assert req.status_code == 405


@pytest.mark.django_db
def test_ticket_vote_code_delete_not_allowed(staff_api_client, ticket_vote_code):
    """Test that delete is not allowed (viewset is read-only)"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.delete(f"{base_url}{ticket_vote_code.id}/")
    assert req.status_code == 405


@pytest.mark.django_db
def test_filter_ticket_vote_codes_by_event(staff_api_client, event, ticket_vote_code):
    """Test filtering ticket vote codes by event"""
    base_url = get_base_url(event.id)
    req = staff_api_client.get(base_url, {"event": event.id})
    assert req.status_code == 200
    for code in req.data:
        assert code["event"] == event.id


@pytest.mark.django_db
def test_filter_ticket_vote_codes_by_user(staff_api_client, base_user, ticket_vote_code):
    """Test filtering ticket vote codes by associated user"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.get(base_url, {"associated_to": base_user.id})
    assert req.status_code == 200
    for code in req.data:
        assert code["associated_to"] == base_user.id


@pytest.mark.django_db
def test_ticket_vote_code_includes_computed_fields(staff_api_client, ticket_vote_code):
    """Test that ticket vote code includes username"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.get(f"{base_url}{ticket_vote_code.id}/")
    assert req.status_code == 200
    assert "key" not in req.data  # Key is hidden for security
    assert req.data["associated_username"] == ticket_vote_code.associated_username
