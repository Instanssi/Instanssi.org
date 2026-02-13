"""Tests for notification Celery tasks."""

from datetime import datetime
from datetime import timezone as dt_tz
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.models import Competition, Compo, Event, VoteCodeRequest
from Instanssi.notifications.models import PushSubscription, SentNotification
from Instanssi.notifications.tasks import (
    check_upcoming_events,
    cleanup_old_sent_notifications,
    notify_new_vote_code_request,
)
from Instanssi.users.models import User

FROZEN_TIME = "2025-01-15T12:00:00Z"


@pytest.fixture
def staff_with_subscription(create_user):
    """Create a staff user with a push subscription."""
    user = create_user(is_staff=True)
    PushSubscription.objects.create(
        user=user,
        endpoint="https://push.example.com/sub/staff",
        p256dh="test_p256dh_key",
        auth="test_auth_key",
    )
    return user


@pytest.fixture
def notification_event():
    """Event for notification testing."""
    from datetime import date

    return Event.objects.create(
        name="Notification Test Event",
        tag="notif",
        date=date(2025, 1, 15),
        archived=False,
    )


@pytest.mark.django_db
@patch("Instanssi.notifications.tasks.webpush")
def test_notify_new_vote_code_request(mock_webpush, staff_with_subscription, notification_event):
    """Test that a push notification is sent for new vote code requests."""
    vcr = VoteCodeRequest.objects.create(
        event=notification_event,
        user=staff_with_subscription,
        text="Please give me a vote code",
        status=0,
    )

    notify_new_vote_code_request(vcr.id)

    mock_webpush.assert_called_once()
    call_kwargs = mock_webpush.call_args
    assert call_kwargs.kwargs["subscription_info"]["endpoint"] == "https://push.example.com/sub/staff"
    assert SentNotification.objects.filter(notification_key=f"vcr:{vcr.id}").exists()


@pytest.mark.django_db
@patch("Instanssi.notifications.tasks.webpush")
def test_notify_deduplication(mock_webpush, staff_with_subscription, notification_event):
    """Test that duplicate notifications are not sent."""
    vcr = VoteCodeRequest.objects.create(
        event=notification_event,
        user=staff_with_subscription,
        text="test",
        status=0,
    )

    notify_new_vote_code_request(vcr.id)
    notify_new_vote_code_request(vcr.id)

    # Should only be called once due to deduplication
    assert mock_webpush.call_count == 1


@pytest.mark.django_db
@patch("Instanssi.notifications.tasks.webpush")
def test_notify_respects_user_preference(mock_webpush, staff_with_subscription, notification_event):
    """Test that notifications respect user preferences."""
    staff_with_subscription.notify_vote_code_requests = False
    staff_with_subscription.save()

    vcr = VoteCodeRequest.objects.create(
        event=notification_event,
        user=staff_with_subscription,
        text="test",
        status=0,
    )

    notify_new_vote_code_request(vcr.id)

    # Should not send because preference is disabled
    mock_webpush.assert_not_called()


@pytest.mark.django_db
@patch("Instanssi.notifications.tasks.webpush")
def test_notify_missing_vote_code_request(mock_webpush):
    """Test handling of non-existent vote code request."""
    notify_new_vote_code_request(99999)
    mock_webpush.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("status_code", [404, 410])
@patch("Instanssi.notifications.tasks.webpush")
def test_stale_subscription_cleanup(mock_webpush, staff_with_subscription, notification_event, status_code):
    """Test that subscriptions are removed on 404/410 push responses."""
    from pywebpush import WebPushException

    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_webpush.side_effect = WebPushException("Gone", response=mock_response)

    vcr = VoteCodeRequest.objects.create(
        event=notification_event,
        user=staff_with_subscription,
        text="test",
        status=0,
    )

    notify_new_vote_code_request(vcr.id)

    assert not PushSubscription.objects.filter(user=staff_with_subscription).exists()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
@patch("Instanssi.notifications.tasks.webpush")
def test_check_upcoming_program_events(mock_webpush, staff_with_subscription, notification_event):
    """Test that upcoming program events trigger notifications."""
    ProgrammeEvent.objects.create(
        event=notification_event,
        start=datetime(2025, 1, 15, 12, 10, 0, tzinfo=dt_tz.utc),
        title="Upcoming Talk",
        active=True,
    )

    check_upcoming_events()

    mock_webpush.assert_called_once()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
@patch("Instanssi.notifications.tasks.webpush")
def test_check_upcoming_compos(mock_webpush, staff_with_subscription, notification_event):
    """Test that upcoming compos trigger notifications."""
    Compo.objects.create(
        event=notification_event,
        name="Demo Compo",
        description="Test compo",
        adding_end=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 12, 10, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        active=True,
    )

    check_upcoming_events()

    mock_webpush.assert_called_once()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
@patch("Instanssi.notifications.tasks.webpush")
def test_check_upcoming_competitions(mock_webpush, staff_with_subscription, notification_event):
    """Test that upcoming competitions trigger notifications."""
    Competition.objects.create(
        event=notification_event,
        name="Speed Coding",
        description="Test competition",
        participation_end=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        start=datetime(2025, 1, 15, 12, 10, 0, tzinfo=dt_tz.utc),
        end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        score_type="p",
        active=True,
    )

    check_upcoming_events()

    mock_webpush.assert_called_once()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
@patch("Instanssi.notifications.tasks.webpush")
def test_check_skips_inactive_compos(mock_webpush, staff_with_subscription, notification_event):
    """Test that inactive compos don't trigger notifications."""
    Compo.objects.create(
        event=notification_event,
        name="Inactive Compo",
        description="Test compo",
        adding_end=datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc),
        editing_end=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
        compo_start=datetime(2025, 1, 15, 12, 10, 0, tzinfo=dt_tz.utc),
        voting_start=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),
        voting_end=datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc),
        active=False,
    )

    check_upcoming_events()

    mock_webpush.assert_not_called()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
@patch("Instanssi.notifications.tasks.webpush")
def test_check_skips_hidden_event_items(mock_webpush, staff_with_subscription):
    """Test that items from hidden events don't trigger notifications."""
    from datetime import date

    hidden_event = Event.objects.create(
        name="Hidden Event",
        tag="hidden",
        date=date(2025, 1, 15),
        hidden=True,
    )
    ProgrammeEvent.objects.create(
        event=hidden_event,
        start=datetime(2025, 1, 15, 12, 10, 0, tzinfo=dt_tz.utc),
        title="Hidden Talk",
        active=True,
    )

    check_upcoming_events()

    mock_webpush.assert_not_called()


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
@patch("Instanssi.notifications.tasks.webpush")
def test_check_skips_events_outside_window(mock_webpush, staff_with_subscription, notification_event):
    """Test that events outside the 15-minute window are skipped."""
    ProgrammeEvent.objects.create(
        event=notification_event,
        start=datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc),  # 1 hour away
        title="Far Away Talk",
        active=True,
    )

    check_upcoming_events()

    mock_webpush.assert_not_called()


@pytest.mark.django_db
def test_cleanup_old_sent_notifications():
    """Test that old sent notifications are cleaned up."""
    from datetime import timedelta

    from django.utils import timezone

    # Old notification (8 days ago)
    old = SentNotification.objects.create(notification_key="old:1")
    old.sent_at = timezone.now() - timedelta(days=8)
    old.save()

    # Recent notification (1 day ago)
    recent = SentNotification.objects.create(notification_key="recent:1")
    recent.sent_at = timezone.now() - timedelta(days=1)
    recent.save()

    cleanup_old_sent_notifications()

    assert not SentNotification.objects.filter(notification_key="old:1").exists()
    assert SentNotification.objects.filter(notification_key="recent:1").exists()


@pytest.mark.django_db
@patch("Instanssi.notifications.tasks.webpush")
def test_no_notification_without_vapid_key(
    mock_webpush, staff_with_subscription, notification_event, settings
):
    """Test that notifications are skipped when VAPID_PRIVATE_KEY is empty."""
    settings.VAPID_PRIVATE_KEY = ""

    vcr = VoteCodeRequest.objects.create(
        event=notification_event,
        user=staff_with_subscription,
        text="test",
        status=0,
    )

    notify_new_vote_code_request(vcr.id)

    mock_webpush.assert_not_called()


@pytest.mark.django_db
@patch("Instanssi.notifications.tasks.webpush")
def test_webpush_exception_without_response(mock_webpush, staff_with_subscription, notification_event):
    """Test that WebPushException with no response object is handled gracefully."""
    from pywebpush import WebPushException

    mock_webpush.side_effect = WebPushException("Connection failed")

    vcr = VoteCodeRequest.objects.create(
        event=notification_event,
        user=staff_with_subscription,
        text="test",
        status=0,
    )

    notify_new_vote_code_request(vcr.id)

    # Subscription should NOT be deleted (only 404/410 trigger deletion)
    assert PushSubscription.objects.filter(user=staff_with_subscription).exists()


@pytest.mark.django_db
@patch("Instanssi.notifications.tasks.webpush")
def test_webpush_exception_with_server_error(mock_webpush, staff_with_subscription, notification_event):
    """Test that non-404/410 WebPushException status codes preserve the subscription."""
    from pywebpush import WebPushException

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_webpush.side_effect = WebPushException("Rate limited", response=mock_response)

    vcr = VoteCodeRequest.objects.create(
        event=notification_event,
        user=staff_with_subscription,
        text="test",
        status=0,
    )

    notify_new_vote_code_request(vcr.id)

    # Subscription should be kept (not a permanent failure)
    assert PushSubscription.objects.filter(user=staff_with_subscription).exists()
