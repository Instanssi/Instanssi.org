from datetime import datetime
from datetime import timezone as dt_tz

import pytest
from django.conf import settings


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/ticket_vote_codes/"


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
def test_staff_can_create_ticket_vote_code(staff_api_client, event, base_user, transaction_item_a):
    """Test that staff can create a ticket vote code"""
    base_url = get_base_url(event.id)
    vote_code_time = datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt_tz.utc)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "associated_to": base_user.id,
            "ticket": transaction_item_a.id,
            "time": vote_code_time.isoformat(),
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": event.id,
        "ticket": transaction_item_a.id,
        "associated_to": base_user.id,
        "time": vote_code_time.astimezone(settings.ZONE_INFO).isoformat(),
        "associated_username": base_user.username,
    }


@pytest.mark.django_db
def test_staff_can_update_ticket_vote_code(staff_api_client, ticket_vote_code, normal_user):
    """Test that staff can update a ticket vote code"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.patch(f"{base_url}{ticket_vote_code.id}/", {"associated_to": normal_user.id})
    assert req.status_code == 200
    assert req.data["associated_to"] == normal_user.id


@pytest.mark.django_db
def test_staff_can_delete_ticket_vote_code(staff_api_client, ticket_vote_code):
    """Test that staff can delete a ticket vote code"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.delete(f"{base_url}{ticket_vote_code.id}/")
    assert req.status_code == 204


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


@pytest.mark.django_db
def test_event_from_url_overrides_request_body_on_create(
    staff_api_client, event, other_event, base_user, transaction_item_a
):
    """Test that event is set from URL, ignoring any value in request body."""
    base_url = get_base_url(event.id)
    vote_code_time = datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt_tz.utc)
    req = staff_api_client.post(
        base_url,
        {
            "event": other_event.id,  # This should be ignored
            "associated_to": base_user.id,
            "ticket": transaction_item_a.id,
            "time": vote_code_time.isoformat(),
        },
    )
    assert req.status_code == 201
    # Event should be from URL, not request body
    assert req.data["event"] == event.id


@pytest.mark.django_db
def test_cannot_create_ticket_vote_code_with_ticket_from_other_event(
    staff_api_client, event, base_user, other_event_transaction_item
):
    """Test that staff cannot create vote code with ticket from another event."""
    base_url = get_base_url(event.id)
    vote_code_time = datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt_tz.utc)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "associated_to": base_user.id,
            "ticket": other_event_transaction_item.id,  # Ticket from other event
            "time": vote_code_time.isoformat(),
        },
    )
    assert req.status_code == 400
    assert "ticket" in req.data


@pytest.mark.django_db
def test_event_is_readonly_on_update(staff_api_client, ticket_vote_code, other_event):
    """Test that event cannot be changed on update (read-only field)."""
    base_url = get_base_url(ticket_vote_code.event_id)
    original_event_id = ticket_vote_code.event_id
    req = staff_api_client.patch(
        f"{base_url}{ticket_vote_code.id}/",
        {"event": other_event.id},
    )
    assert req.status_code == 200
    # Event should remain unchanged (read-only)
    assert req.data["event"] == original_event_id
