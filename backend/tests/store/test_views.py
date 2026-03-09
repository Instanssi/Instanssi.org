import pytest


@pytest.mark.django_db
def test_ta_anonymous_can_view_paid_transaction(page_client, store_transaction):
    resp = page_client.get(f"/store/ta/{store_transaction.key}/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_ta_returns_404_for_unpaid_transaction(page_client, unpaid_transaction):
    resp = page_client.get(f"/store/ta/{unpaid_transaction.key}/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_ta_returns_404_for_nonexistent_key(page_client):
    resp = page_client.get("/store/ta/nonexistent-key/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_ta_infodesk_user_sees_deliver_button(infodesk_client, store_transaction, claimable_ticket):
    resp = infodesk_client.get(f"/store/ta/{store_transaction.key}/")
    assert resp.status_code == 200
    assert resp.context["has_infodesk_access"] is True
    content = resp.content.decode()
    assert 'name="ta_item_key"' in content
    assert "Merkitse toimitetuksi" in content


@pytest.mark.django_db
def test_ta_anonymous_does_not_see_deliver_button(page_client, store_transaction, claimable_ticket):
    resp = page_client.get(f"/store/ta/{store_transaction.key}/")
    assert resp.status_code == 200
    assert resp.context["has_infodesk_access"] is False
    content = resp.content.decode()
    assert 'name="ta_item_key"' not in content
    assert "Merkitse toimitetuksi" not in content


@pytest.mark.django_db
def test_ta_store_change_user_does_not_see_deliver_button(
    store_change_client, store_transaction, claimable_ticket
):
    """User with store.change_storetransaction should NOT see the deliver button."""
    resp = store_change_client.get(f"/store/ta/{store_transaction.key}/")
    assert resp.status_code == 200
    assert resp.context["has_infodesk_access"] is False
    content = resp.content.decode()
    assert 'name="ta_item_key"' not in content
    assert "Merkitse toimitetuksi" not in content


@pytest.mark.django_db
def test_ti_anonymous_can_view_paid_item(page_client, transaction_item_a):
    resp = page_client.get(f"/store/ti/{transaction_item_a.key}/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_ti_returns_404_for_unpaid_item(page_client, unpaid_ticket):
    resp = page_client.get(f"/store/ti/{unpaid_ticket.key}/")
    assert resp.status_code == 404


@pytest.mark.django_db
def test_ti_infodesk_user_sees_deliver_button(infodesk_client, transaction_item_a):
    resp = infodesk_client.get(f"/store/ti/{transaction_item_a.key}/")
    assert resp.status_code == 200
    assert resp.context["has_infodesk_access"] is True
    content = resp.content.decode()
    assert 'name="ta_item_key"' in content
    assert "Merkitse toimitetuksi" in content


@pytest.mark.django_db
def test_ti_anonymous_does_not_see_deliver_button(page_client, transaction_item_a):
    resp = page_client.get(f"/store/ti/{transaction_item_a.key}/")
    assert resp.status_code == 200
    assert resp.context["has_infodesk_access"] is False
    content = resp.content.decode()
    assert 'name="ta_item_key"' not in content
    assert "Merkitse toimitetuksi" not in content


@pytest.mark.django_db
def test_mark_delivered_infodesk_user_can_mark(infodesk_client, store_transaction, claimable_ticket):
    resp = infodesk_client.post(
        f"/store/ta/{store_transaction.key}/",
        {"ta_item_key": claimable_ticket.key},
    )
    assert resp.status_code == 200
    claimable_ticket.refresh_from_db()
    assert claimable_ticket.time_delivered is not None


@pytest.mark.django_db
def test_mark_delivered_anonymous_is_denied(page_client, store_transaction, claimable_ticket):
    resp = page_client.post(
        f"/store/ta/{store_transaction.key}/",
        {"ta_item_key": claimable_ticket.key},
    )
    assert resp.status_code == 403
    claimable_ticket.refresh_from_db()
    assert claimable_ticket.time_delivered is None


@pytest.mark.django_db
def test_mark_delivered_authenticated_user_without_permission_is_denied(
    login_as, store_transaction, claimable_ticket
):
    with login_as() as client:
        resp = client.post(
            f"/store/ta/{store_transaction.key}/",
            {"ta_item_key": claimable_ticket.key},
        )
    assert resp.status_code == 403
    claimable_ticket.refresh_from_db()
    assert claimable_ticket.time_delivered is None


@pytest.mark.django_db
def test_mark_delivered_store_change_permission_is_denied(
    store_change_client, store_transaction, claimable_ticket
):
    """User with store.change_storetransaction but NOT infodesk permission is denied."""
    resp = store_change_client.post(
        f"/store/ta/{store_transaction.key}/",
        {"ta_item_key": claimable_ticket.key},
    )
    assert resp.status_code == 403
    claimable_ticket.refresh_from_db()
    assert claimable_ticket.time_delivered is None


@pytest.mark.django_db
def test_mark_delivered_infodesk_user_can_mark_via_ti_view(infodesk_client, claimable_ticket):
    resp = infodesk_client.post(
        f"/store/ti/{claimable_ticket.key}/",
        {"ta_item_key": claimable_ticket.key},
    )
    assert resp.status_code == 200
    claimable_ticket.refresh_from_db()
    assert claimable_ticket.time_delivered is not None


@pytest.mark.django_db
def test_mark_delivered_anonymous_is_denied_via_ti_view(page_client, claimable_ticket):
    resp = page_client.post(
        f"/store/ti/{claimable_ticket.key}/",
        {"ta_item_key": claimable_ticket.key},
    )
    assert resp.status_code == 403
    claimable_ticket.refresh_from_db()
    assert claimable_ticket.time_delivered is None
