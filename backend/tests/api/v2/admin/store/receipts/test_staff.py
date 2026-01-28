"""Tests for the staff receipts endpoint."""

import pytest


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/receipts/"


@pytest.fixture
def store_staff_api_client(api_client, create_user, password):
    """API client authenticated as a user with store permissions."""
    permissions = [
        "store.view_receipt",
        "store.add_receipt",
        "store.change_receipt",
        "store.delete_receipt",
    ]
    user = create_user(is_staff=True, permissions=permissions)
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.mark.django_db
def test_staff_can_list_receipts(store_staff_api_client, store_receipt, transaction_item_a):
    """Test that staff can list all receipts."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    req = store_staff_api_client.get(base_url)
    assert req.status_code == 200


@pytest.mark.django_db
def test_staff_can_get_receipt_detail(store_staff_api_client, store_receipt, transaction_item_a):
    """Test that staff can get receipt details."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    req = store_staff_api_client.get(f"{base_url}{store_receipt.id}/")
    assert req.status_code == 200
    assert req.data["id"] == store_receipt.id
    assert req.data["subject"] == store_receipt.subject
    assert req.data["mail_to"] == store_receipt.mail_to


@pytest.mark.django_db
def test_staff_can_update_receipt(store_staff_api_client, store_receipt, transaction_item_a):
    """Test that staff can update a receipt."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    req = store_staff_api_client.patch(
        f"{base_url}{store_receipt.id}/",
        {"mail_to": "updated@example.com"},
    )
    assert req.status_code == 200
    assert req.data["mail_to"] == "updated@example.com"


@pytest.mark.django_db
def test_receipt_includes_all_fields(store_staff_api_client, store_receipt, transaction_item_a):
    """Test that receipt response includes all fields."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    req = store_staff_api_client.get(f"{base_url}{store_receipt.id}/")
    assert req.status_code == 200
    assert "id" in req.data
    assert "transaction" in req.data
    assert "subject" in req.data
    assert "mail_to" in req.data
    assert "mail_from" in req.data
    assert "sent" in req.data
    assert "params" in req.data
    assert "content" in req.data
    assert "is_sent" in req.data


@pytest.mark.django_db
def test_staff_can_resend_receipt(store_staff_api_client, store_receipt, transaction_item_a, mailoutbox):
    """Test that staff can resend a receipt."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    req = store_staff_api_client.post(f"{base_url}{store_receipt.id}/resend/")
    assert req.status_code == 200
    assert req.data["is_sent"] is True
    assert req.data["sent"] is not None
    # Check email was sent
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == [store_receipt.mail_to]


@pytest.mark.django_db
def test_resend_receipt_without_content_fails(store_staff_api_client, empty_receipt, transaction_item_a):
    """Test that resending a receipt without content fails."""
    base_url = get_base_url(transaction_item_a.item.event_id)
    req = store_staff_api_client.post(f"{base_url}{empty_receipt.id}/resend/")
    assert req.status_code == 400
    assert "content" in req.data["detail"].lower()
