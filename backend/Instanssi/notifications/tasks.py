import json
import logging
from collections.abc import Callable
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone, translation
from django.utils.translation import gettext as _
from pywebpush import WebPushException, webpush

from Instanssi.ext_programme.models import ProgrammeEvent
from Instanssi.kompomaatti.models import Competition, Compo, VoteCodeRequest
from Instanssi.notifications.models import PushSubscription, SentNotification
from Instanssi.users.models import User

log = logging.getLogger(__name__)


def _send_push_to_staff(
    get_title: Callable[[], str],
    get_body: Callable[[], str],
    url: str,
    notification_key: str,
    user_wants_notification: Callable[[User], bool],
) -> None:
    """Send a web push notification to all staff users who have an active subscription.

    Iterates over all PushSubscription records belonging to staff users,
    checks each user's individual notification preference via the provided
    callable, and delivers the push payload using the VAPID protocol.

    Deduplication is handled via ``SentNotification``: if a record with
    the given *notification_key* already exists the call is a no-op.

    Stale subscriptions (HTTP 404 / 410 from the push service) are
    automatically removed.

    Args:
        get_title: Callable that returns the notification title (called per-user for i18n).
        get_body: Callable that returns the notification body (called per-user for i18n).
        url: Target URL opened when the user clicks the notification.
        notification_key: Unique key used for deduplication (e.g. ``"vcr:42"``).
        user_wants_notification: Predicate that receives a ``User`` instance
            and returns ``True`` when the user should receive the notification.
    """
    if not settings.VAPID_PRIVATE_KEY:
        log.warning("VAPID_PRIVATE_KEY not set, skipping push notification")
        return

    # Deduplication: get_or_create is atomic and prevents race conditions
    _, created = SentNotification.objects.get_or_create(notification_key=notification_key)
    if not created:
        return

    subscriptions = PushSubscription.objects.filter(
        user__is_staff=True,
    ).select_related("user")

    for subscription in subscriptions:
        if not user_wants_notification(subscription.user):
            continue

        with translation.override(subscription.user.language or settings.LANGUAGE_CODE):
            title = get_title()
            body = get_body()

        payload = json.dumps({"title": title, "body": body, "url": url})

        try:
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth,
                    },
                },
                data=payload,
                vapid_private_key=settings.VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{settings.VAPID_CLAIMS_EMAIL}"},
                ttl=43200,
            )
        except WebPushException as e:
            status_code = None
            if e.response is not None:
                status_code = e.response.status_code
            if status_code in (404, 410):
                log.info("Removing expired push subscription %s", subscription.endpoint)
                subscription.delete()
            else:
                log.error("WebPush error for %s: %s", subscription.endpoint, e)
        except Exception:
            log.exception("Unexpected error sending push to %s", subscription.endpoint)


@shared_task  # type: ignore[untyped-decorator]
def notify_new_vote_code_request(vote_code_request_id: int) -> None:
    """Notify staff about a newly submitted vote code request.

    Looks up the ``VoteCodeRequest`` by primary key and sends a push
    notification to every staff member whose ``notify_vote_code_requests``
    preference is enabled.
    """
    try:
        vcr = VoteCodeRequest.objects.select_related("user", "event").get(id=vote_code_request_id)
    except VoteCodeRequest.DoesNotExist:
        log.warning("VoteCodeRequest %s not found", vote_code_request_id)
        return

    event_name = vcr.event.name if vcr.event else "unknown event"
    username = vcr.user.username

    _send_push_to_staff(
        get_title=lambda: _("New vote code request"),
        get_body=lambda: _("%(user)s requested a vote code for %(event)s")
        % {"user": username, "event": event_name},
        url="/management/",
        notification_key=f"vcr:{vcr.id}",
        user_wants_notification=lambda u: u.notify_vote_code_requests,
    )


@shared_task  # type: ignore[untyped-decorator]
def check_upcoming_events() -> None:
    """Send reminders for program events, compos, and competitions starting soon.

    Queries for active, non-hidden items whose start time falls within the
    next 15 minutes and sends a push notification to each eligible staff
    member.  Each item is sent at most once thanks to the deduplication
    key embedded in ``_send_push_to_staff``.
    """
    now = timezone.now()
    window_start = now
    window_end = now + timedelta(minutes=15)

    # Program events
    upcoming_programs = ProgrammeEvent.objects.filter(
        start__gte=window_start,
        start__lte=window_end,
        active=True,
        event__hidden=False,
    ).select_related("event")

    for prog in upcoming_programs:
        prog_title = prog.title
        prog_event_name = prog.event.name
        prog_id = prog.id
        _send_push_to_staff(
            get_title=lambda: _("Program starting soon: %(title)s") % {"title": prog_title},
            get_body=lambda: _("%(title)s starting soon at %(event)s")
            % {"title": prog_title, "event": prog_event_name},
            url="/management/",
            notification_key=f"prog:{prog_id}:15min",
            user_wants_notification=lambda u: u.notify_program_events,
        )

    # Compos
    upcoming_compos = Compo.objects.filter(
        compo_start__gte=window_start,
        compo_start__lte=window_end,
        active=True,
        event__hidden=False,
    ).select_related("event")

    for compo in upcoming_compos:
        compo_name = compo.name
        compo_event_name = compo.event.name
        compo_id = compo.id
        _send_push_to_staff(
            get_title=lambda: _("Compo starting soon: %(name)s") % {"name": compo_name},
            get_body=lambda: _("%(name)s starting soon at %(event)s")
            % {"name": compo_name, "event": compo_event_name},
            url="/management/",
            notification_key=f"compo:{compo_id}:15min",
            user_wants_notification=lambda u: u.notify_compo_starts,
        )

    # Competitions
    upcoming_competitions = Competition.objects.filter(
        start__gte=window_start,
        start__lte=window_end,
        active=True,
        event__hidden=False,
    ).select_related("event")

    for comp in upcoming_competitions:
        comp_name = comp.name
        comp_event_name = comp.event.name
        comp_id = comp.id
        _send_push_to_staff(
            get_title=lambda: _("Competition starting soon: %(name)s") % {"name": comp_name},
            get_body=lambda: _("%(name)s starting soon at %(event)s")
            % {"name": comp_name, "event": comp_event_name},
            url="/management/",
            notification_key=f"comp:{comp_id}:15min",
            user_wants_notification=lambda u: u.notify_competition_starts,
        )


@shared_task  # type: ignore[untyped-decorator]
def cleanup_old_sent_notifications() -> None:
    """Purge ``SentNotification`` records older than 7 days.

    Keeps the deduplication table from growing indefinitely. Intended to
    be called periodically (e.g. via Celery Beat).
    """
    cutoff = timezone.now() - timedelta(days=7)
    deleted_count, _ = SentNotification.objects.filter(sent_at__lt=cutoff).delete()
    if deleted_count:
        log.info("Cleaned up %d old sent notification records", deleted_count)
