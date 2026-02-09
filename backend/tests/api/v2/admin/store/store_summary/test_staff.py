"""Tests for the store summary endpoint with proper permissions."""

from decimal import Decimal

import pytest

from Instanssi.store.models import TransactionItem


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/store/summary/"


@pytest.fixture
def summary_staff_api_client(api_client, create_user, password):
    """API client authenticated as a user with only store.view_storeitem permission."""
    permissions = ["store.view_storeitem"]
    user = create_user(is_staff=True, permissions=permissions)
    api_client.login(username=user.username, password=password)
    yield api_client
    api_client.logout()


@pytest.mark.django_db
def test_returns_correct_structure(summary_staff_api_client, event):
    """Response has the expected top-level keys."""
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    assert "total_items_sold" in response.data
    assert "total_revenue" in response.data
    assert "items" in response.data
    assert "sales_per_day" in response.data
    assert "sales_per_hour" in response.data


@pytest.mark.django_db
def test_empty_event_returns_zeros(summary_staff_api_client, event):
    """An event with no transactions returns zero totals and empty lists."""
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    assert response.data["total_items_sold"] == 0
    assert Decimal(response.data["total_revenue"]) == Decimal(0)
    assert response.data["items"] == []
    assert response.data["sales_per_day"] == []
    assert response.data["sales_per_hour"] == []


@pytest.mark.django_db
def test_aggregates_paid_transaction_items(
    summary_staff_api_client, transaction_item_a, transaction_item_b, event
):
    """Paid transaction items are correctly aggregated."""
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    assert response.data["total_items_sold"] == 2
    # transaction_item_a = 2.50, transaction_item_b = 1.00
    assert Decimal(response.data["total_revenue"]) == Decimal("3.50")
    assert len(response.data["items"]) == 1  # Both items are for same store_item, no variant
    row = response.data["items"][0]
    assert row["quantity"] == 2
    assert Decimal(row["revenue"]) == Decimal("3.50")
    assert row["variant_id"] is None
    assert row["variant_name"] is None


@pytest.mark.django_db
def test_excludes_unpaid_transactions(summary_staff_api_client, unpaid_ticket, event):
    """Items from unpaid transactions are not included in the summary."""
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    assert response.data["total_items_sold"] == 0
    assert Decimal(response.data["total_revenue"]) == Decimal(0)


@pytest.mark.django_db
def test_sales_per_day_present(summary_staff_api_client, transaction_item_a, event):
    """Sales per day data is returned for paid items."""
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    assert len(response.data["sales_per_day"]) >= 1
    day_row = response.data["sales_per_day"][0]
    assert "date" in day_row
    assert "count" in day_row
    assert day_row["count"] >= 1


@pytest.mark.django_db
def test_sales_per_hour_present(summary_staff_api_client, transaction_item_a, event):
    """Sales per hour data is returned for paid items."""
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    assert len(response.data["sales_per_hour"]) >= 1
    hour_row = response.data["sales_per_hour"][0]
    assert "hour" in hour_row
    assert "count" in hour_row
    assert hour_row["count"] >= 1


@pytest.mark.django_db
def test_no_pii_in_response(summary_staff_api_client, transaction_item_a, event):
    """Response must not contain any PII fields."""
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    response_text = str(response.data)
    # These are values from the store_transaction fixture
    assert "Testi" not in response_text
    assert "Asiakas" not in response_text
    assert "testi.asiakas@instanssi.org" not in response_text
    assert "Kauppakatu" not in response_text
    assert "deadbeef" not in response_text


@pytest.mark.django_db
def test_variant_breakdown(
    summary_staff_api_client,
    variant_item,
    store_item_variant,
    store_transaction,
    event,
):
    """Items with variants show the variant name in the breakdown."""
    TransactionItem.objects.create(
        key="cccc1111dddd2222eeee3333ffff4444",
        item=variant_item,
        variant=store_item_variant,
        transaction=store_transaction,
        purchase_price=variant_item.price,
        original_price=variant_item.price,
    )
    url = get_base_url(event.id)
    response = summary_staff_api_client.get(url)
    assert response.status_code == 200
    assert response.data["total_items_sold"] == 1
    assert len(response.data["items"]) == 1
    row = response.data["items"][0]
    assert row["variant_id"] == store_item_variant.id
    assert row["variant_name"] == "XXL"
