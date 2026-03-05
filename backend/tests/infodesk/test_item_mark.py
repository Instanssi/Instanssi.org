import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_item_mark_rejects_get(super_page_client, transaction_item_a):
    """item_mark endpoint only accepts POST requests."""
    url = reverse("infodesk:item_mark", args=[transaction_item_a.id])
    response = super_page_client.get(url)
    assert response.status_code == 405


@pytest.mark.django_db
def test_item_mark_accepts_post(super_page_client, transaction_item_a):
    """item_mark endpoint accepts POST and marks item as delivered."""
    url = reverse("infodesk:item_mark", args=[transaction_item_a.id])
    response = super_page_client.post(url)
    assert response.status_code == 302
    transaction_item_a.refresh_from_db()
    assert transaction_item_a.time_delivered is not None
