"""Tests for push notification subscription API endpoints."""

import pytest

from Instanssi.notifications.models import PushSubscription

SUBSCRIPTIONS_URL = "/api/v2/notifications/subscriptions/"
VAPID_KEY_URL = "/api/v2/public/notifications/vapid-key/"


# --- Unauthenticated tests ---


@pytest.mark.django_db
def test_unauthenticated_get(api_client):
    """Unauthenticated users cannot access notification subscription endpoints."""
    assert api_client.get(SUBSCRIPTIONS_URL).status_code == 401


@pytest.mark.django_db
def test_unauthenticated_post_subscription(api_client):
    """Unauthenticated users cannot create subscriptions."""
    assert api_client.post(SUBSCRIPTIONS_URL, {}).status_code == 401


@pytest.mark.django_db
def test_unauthenticated_delete_subscription(api_client):
    """Unauthenticated users cannot delete subscriptions."""
    assert api_client.delete(f"{SUBSCRIPTIONS_URL}1/").status_code == 401


# --- Unauthorized (non-staff) tests ---


@pytest.mark.django_db
def test_unauthorized_get(auth_client):
    """Non-staff users cannot access notification subscription endpoints."""
    assert auth_client.get(SUBSCRIPTIONS_URL).status_code == 403


@pytest.mark.django_db
def test_unauthorized_post_subscription(auth_client):
    """Non-staff users cannot create subscriptions."""
    assert auth_client.post(SUBSCRIPTIONS_URL, {}).status_code == 403


# --- Staff / authorized tests ---


@pytest.mark.django_db
def test_staff_can_subscribe(super_api_client, super_user):
    """Staff users can create push subscriptions."""
    data = {
        "endpoint": "https://push.example.com/sub/1234",
        "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa",
        "auth": "aGVsbG8gd29ybGQ",
    }
    result = super_api_client.post(SUBSCRIPTIONS_URL, data)
    assert result.status_code == 201

    sub = PushSubscription.objects.get(endpoint=data["endpoint"])
    assert sub.user == super_user
    assert sub.p256dh == data["p256dh"]
    assert sub.auth == data["auth"]


@pytest.mark.django_db
def test_staff_subscribe_upsert(super_api_client, super_user):
    """Creating a subscription with the same endpoint updates the existing one."""
    data = {
        "endpoint": "https://push.example.com/sub/5678",
        "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa",
        "auth": "aGVsbG8gd29ybGQ",
    }
    result1 = super_api_client.post(SUBSCRIPTIONS_URL, data)
    assert result1.status_code == 201

    # Post again with updated keys
    data["p256dh"] = "UPDATED_KEY"
    data["auth"] = "UPDATED_AUTH"
    result2 = super_api_client.post(SUBSCRIPTIONS_URL, data)
    assert result2.status_code == 201

    # Should still be one subscription
    subs = PushSubscription.objects.filter(endpoint=data["endpoint"])
    assert subs.count() == 1
    assert subs.first().p256dh == "UPDATED_KEY"


@pytest.mark.django_db
def test_staff_can_list_subscriptions(super_api_client, super_user):
    """Staff users can list their own subscriptions."""
    PushSubscription.objects.create(
        user=super_user,
        endpoint="https://push.example.com/sub/a",
        p256dh="key_a",
        auth="auth_a",
    )
    result = super_api_client.get(SUBSCRIPTIONS_URL)
    assert result.status_code == 200
    assert len(result.data) == 1
    assert result.data[0]["endpoint"] == "https://push.example.com/sub/a"


@pytest.mark.django_db
def test_staff_only_sees_own_subscriptions(super_api_client, super_user, staff_user):
    """Staff users only see their own subscriptions, not others'."""
    PushSubscription.objects.create(
        user=super_user,
        endpoint="https://push.example.com/sub/own",
        p256dh="key_own",
        auth="auth_own",
    )
    PushSubscription.objects.create(
        user=staff_user,
        endpoint="https://push.example.com/sub/other",
        p256dh="key_other",
        auth="auth_other",
    )
    result = super_api_client.get(SUBSCRIPTIONS_URL)
    assert result.status_code == 200
    assert len(result.data) == 1
    assert result.data[0]["endpoint"] == "https://push.example.com/sub/own"


@pytest.mark.django_db
def test_staff_can_delete_subscription(super_api_client, super_user):
    """Staff users can delete their own subscriptions."""
    sub = PushSubscription.objects.create(
        user=super_user,
        endpoint="https://push.example.com/sub/del",
        p256dh="key_del",
        auth="auth_del",
    )
    result = super_api_client.delete(f"{SUBSCRIPTIONS_URL}{sub.id}/")
    assert result.status_code == 204
    assert not PushSubscription.objects.filter(id=sub.id).exists()


@pytest.mark.django_db
def test_staff_cannot_delete_other_users_subscription(super_api_client, staff_user):
    """Staff users cannot delete another user's subscription."""
    sub = PushSubscription.objects.create(
        user=staff_user,
        endpoint="https://push.example.com/sub/other_del",
        p256dh="key_other_del",
        auth="auth_other_del",
    )
    result = super_api_client.delete(f"{SUBSCRIPTIONS_URL}{sub.id}/")
    assert result.status_code == 404
    assert PushSubscription.objects.filter(id=sub.id).exists()


@pytest.mark.django_db
def test_non_superuser_staff_can_subscribe(staff_api_client, staff_user):
    """Non-superuser staff can also create push subscriptions."""
    data = {
        "endpoint": "https://push.example.com/sub/staff-only",
        "p256dh": "BEl62iUYgUivxIkv69yViEuiBIa",
        "auth": "aGVsbG8gd29ybGQ",
    }
    result = staff_api_client.post(SUBSCRIPTIONS_URL, data)
    assert result.status_code == 201

    sub = PushSubscription.objects.get(endpoint=data["endpoint"])
    assert sub.user == staff_user


@pytest.mark.django_db
def test_cross_user_endpoint_reassignment(super_api_client, super_user, staff_user):
    """Subscribing with an endpoint owned by another user reassigns it."""
    PushSubscription.objects.create(
        user=staff_user,
        endpoint="https://push.example.com/sub/shared-browser",
        p256dh="old_key",
        auth="old_auth",
    )

    data = {
        "endpoint": "https://push.example.com/sub/shared-browser",
        "p256dh": "new_key",
        "auth": "new_auth",
    }
    result = super_api_client.post(SUBSCRIPTIONS_URL, data)
    assert result.status_code == 201

    # Should still be exactly one subscription for this endpoint
    subs = PushSubscription.objects.filter(endpoint=data["endpoint"])
    assert subs.count() == 1
    sub = subs.first()
    assert sub.user == super_user
    assert sub.p256dh == "new_key"
    assert sub.auth == "new_auth"


# --- VAPID key tests (public endpoint) ---


@pytest.mark.django_db
def test_anyone_can_get_vapid_key(api_client):
    """Anyone can retrieve the VAPID public key (public endpoint)."""
    result = api_client.get(VAPID_KEY_URL)
    assert result.status_code == 200
    assert "vapid_public_key" in result.data
