import secrets
from decimal import Decimal
from uuid import uuid4

import pytest
from django.utils import timezone

from Instanssi.kompomaatti.models import TicketVoteCode
from Instanssi.store.models import StoreItem, StoreTransaction, TransactionItem


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/user/kompomaatti/ticket_vote_codes/"


@pytest.fixture
def paid_ticket_item(event, faker, image_png) -> StoreItem:
    """A ticket item that can be purchased."""
    return StoreItem.objects.create(
        name="Event Ticket",
        event=event,
        description="Entry ticket with voting rights",
        price=Decimal("25.00"),
        max=100,
        available=True,
        max_per_order=10,
        sort_index=0,
        discount_amount=-1,
        discount_percentage=0,
        is_ticket=True,
        imagefile_original=image_png,
    )


@pytest.fixture
def paid_transaction(event, faker) -> StoreTransaction:
    """A paid transaction."""
    return StoreTransaction.objects.create(
        token=secrets.token_hex(8),
        time_created=timezone.now(),
        time_paid=timezone.now(),  # Paid
        key=uuid4().hex,
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
    )


@pytest.fixture
def claimable_ticket(paid_ticket_item, paid_transaction) -> TransactionItem:
    """A paid ticket that can be claimed for voting rights."""
    return TransactionItem.objects.create(
        key=uuid4().hex,
        item=paid_ticket_item,
        transaction=paid_transaction,
        purchase_price=paid_ticket_item.price,
        original_price=paid_ticket_item.price,
    )


@pytest.mark.django_db
def test_list_own_vote_codes(auth_client, ticket_vote_code):
    """Test that users can list their own vote codes."""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    # Response is a list when no pagination params
    assert len(req.data) == 1
    assert req.data[0]["id"] == ticket_vote_code.id


@pytest.mark.django_db
def test_get_own_vote_code(auth_client, ticket_vote_code):
    """Test that users can retrieve their own vote code."""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = auth_client.get(f"{base_url}{ticket_vote_code.id}/")
    assert req.status_code == 200
    data = req.data
    assert data["id"] == ticket_vote_code.id
    assert data["event"] == ticket_vote_code.event_id
    assert "time" in data


@pytest.mark.django_db
def test_create_vote_code(auth_client, event, claimable_ticket):
    """Test that users can create a vote code by claiming a ticket."""
    base_url = get_base_url(event.id)
    # Use first 8 characters of the ticket key
    partial_key = claimable_ticket.key[:8]
    req = auth_client.post(
        base_url,
        data={
            "event": event.id,
            "ticket_key": partial_key,
        },
    )
    assert req.status_code == 201
    assert req.data["event"] == event.id
    assert "time" in req.data


@pytest.mark.django_db
def test_cannot_claim_already_used_ticket(auth_client, ticket_vote_code, event):
    """Test that users cannot claim a ticket that's already used."""
    base_url = get_base_url(event.id)
    # The ticket_vote_code fixture already claimed a ticket
    partial_key = ticket_vote_code.ticket.key[:8]
    req = auth_client.post(
        base_url,
        data={
            "event": event.id,
            "ticket_key": partial_key,
        },
    )
    assert req.status_code == 400
    assert "already" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_claim_nonexistent_ticket(auth_client, event):
    """Test that users cannot claim a ticket that doesn't exist."""
    base_url = get_base_url(event.id)
    req = auth_client.post(
        base_url,
        data={
            "event": event.id,
            "ticket_key": "abcd1234",  # Nonexistent key
        },
    )
    assert req.status_code == 400
    assert "no valid ticket" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_claim_unpaid_ticket(auth_client, event, paid_ticket_item, faker):
    """Test that users cannot claim an unpaid ticket."""
    # Create an unpaid transaction
    unpaid_transaction = StoreTransaction.objects.create(
        token=secrets.token_hex(8),
        time_created=timezone.now(),
        time_paid=None,  # Not paid
        key=uuid4().hex,
        firstname=faker.first_name(),
        lastname=faker.last_name(),
        email=faker.email(),
        street=faker.street_address(),
        postalcode=faker.postcode(),
        city=faker.city(),
    )
    unpaid_ticket = TransactionItem.objects.create(
        key=uuid4().hex,
        item=paid_ticket_item,
        transaction=unpaid_transaction,
        purchase_price=paid_ticket_item.price,
        original_price=paid_ticket_item.price,
    )

    base_url = get_base_url(event.id)
    req = auth_client.post(
        base_url,
        data={
            "event": event.id,
            "ticket_key": unpaid_ticket.key[:8],
        },
    )
    assert req.status_code == 400
    assert "no valid ticket" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_claim_non_ticket_item(auth_client, event, variant_item, paid_transaction):
    """Test that users cannot claim non-ticket items."""
    # variant_item is not a ticket
    non_ticket = TransactionItem.objects.create(
        key=uuid4().hex,
        item=variant_item,
        transaction=paid_transaction,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )

    base_url = get_base_url(event.id)
    req = auth_client.post(
        base_url,
        data={
            "event": event.id,
            "ticket_key": non_ticket.key[:8],
        },
    )
    assert req.status_code == 400
    assert "no valid ticket" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_have_multiple_vote_codes(auth_client, ticket_vote_code, claimable_ticket):
    """Test that users cannot have multiple vote codes for the same event."""
    base_url = get_base_url(ticket_vote_code.event_id)
    req = auth_client.post(
        base_url,
        data={
            "event": ticket_vote_code.event_id,
            "ticket_key": claimable_ticket.key[:8],
        },
    )
    assert req.status_code == 400
    assert "already have" in str(req.data).lower()


@pytest.mark.django_db
def test_cannot_update_vote_code(auth_client, ticket_vote_code, claimable_ticket):
    """Test that users cannot update their vote codes."""
    base_url = get_base_url(ticket_vote_code.event_id)
    instance_url = f"{base_url}{ticket_vote_code.id}/"
    req = auth_client.patch(
        instance_url,
        data={
            "ticket_key": claimable_ticket.key[:8],
        },
    )
    # Update not supported
    assert req.status_code == 405


@pytest.mark.django_db
def test_cannot_delete_vote_code(auth_client, ticket_vote_code):
    """Test that users cannot delete their vote codes."""
    base_url = get_base_url(ticket_vote_code.event_id)
    instance_url = f"{base_url}{ticket_vote_code.id}/"
    req = auth_client.delete(instance_url)
    # Delete not supported
    assert req.status_code == 405


@pytest.mark.django_db
def test_cannot_see_other_users_vote_codes(auth_client, event, normal_user, transaction_item_a):
    """Test that users can only see their own vote codes."""
    # Create a vote code for a different user
    other_vote_code = TicketVoteCode.objects.create(
        event=event,
        associated_to=normal_user,
        ticket=transaction_item_a,
        time=timezone.now(),
    )

    base_url = get_base_url(event.id)
    req = auth_client.get(base_url)
    assert req.status_code == 200
    # Should not see the other user's vote code
    vote_code_ids = [vc["id"] for vc in req.data]
    assert other_vote_code.id not in vote_code_ids


@pytest.mark.django_db
def test_cannot_access_other_users_vote_code(auth_client, event, normal_user, transaction_item_a):
    """Test that users cannot directly access another user's vote code."""
    # Create a vote code for a different user
    other_vote_code = TicketVoteCode.objects.create(
        event=event,
        associated_to=normal_user,
        ticket=transaction_item_a,
        time=timezone.now(),
    )

    base_url = get_base_url(event.id)
    req = auth_client.get(f"{base_url}{other_vote_code.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
def test_ticket_key_too_short(auth_client, event, claimable_ticket):
    """Test that ticket keys must be at least 8 characters."""
    base_url = get_base_url(event.id)
    req = auth_client.post(
        base_url,
        data={
            "event": event.id,
            "ticket_key": "abc",  # Too short
        },
    )
    assert req.status_code == 400
