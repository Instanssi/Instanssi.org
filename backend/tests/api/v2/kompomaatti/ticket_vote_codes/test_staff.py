import pytest
from django.utils import timezone


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
    assert "key" in req.data
    assert "associated_username" in req.data


@pytest.mark.django_db
def test_staff_can_create_ticket_vote_code(staff_api_client, event, base_user, transaction_item_a):
    """Test that staff can create a ticket vote code"""
    base_url = get_base_url(event.id)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "associated_to": base_user.id,
            "ticket": transaction_item_a.id,
            "time": timezone.now().isoformat(),
        },
    )
    assert req.status_code == 201


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
    """Test that ticket vote code includes key and username"""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = staff_api_client.get(f"{base_url}{ticket_vote_code.id}/")
    assert req.status_code == 200
    assert req.data["key"] == ticket_vote_code.key
    assert req.data["associated_username"] == ticket_vote_code.associated_username
