import logging
from smtplib import SMTPServerDisconnected
from unittest import mock

import pytest
from django.core import mail
from django.test import override_settings

from Instanssi.store.models import StoreTransactionEvent
from Instanssi.store.tasks import send_receipt


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_send_receipt_ok(store_transaction, receipt):
    """Make sure the sending about works. We check the email content elsewhere."""
    receipt.transaction = store_transaction
    receipt.save()

    send_receipt.delay(receipt.id)

    # Ensure mail was sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == receipt.subject
    assert "Instanssi" in mail.outbox[0].body
    assert mail.outbox[0].to == [receipt.mail_to]
    assert mail.outbox[0].from_email == receipt.mail_from

    # Make sure an event log was written
    events = StoreTransactionEvent.objects.all()
    assert events[0].data == {"mail_to": receipt.mail_to, "receipt_id": receipt.id}
    assert events[0].transaction == store_transaction
    assert events[0].message == "Receipt sent"
    assert events[0].created is not None


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_send_receipt_fatal_error(caplog, store_transaction, receipt):
    caplog.set_level(logging.ERROR)

    receipt.transaction = store_transaction
    receipt.save()

    with mock.patch("Instanssi.store.tasks.Receipt.send") as fn:
        fn.side_effect = Exception("poks")
        send_receipt.delay(receipt.id)

    # Make sure we logged
    assert caplog.records[0].message.startswith("Failed to send receipt")

    # Ensure no mail was sent
    assert len(mail.outbox) == 0

    # Make sure an event log was written
    events = StoreTransactionEvent.objects.all()
    assert events.count() == 1
    assert events[0].data == {"mail_to": receipt.mail_to, "receipt_id": receipt.id, "exception": "poks"}
    assert events[0].transaction == store_transaction
    assert events[0].message == "Receipt sending failure"
    assert events[0].created is not None


@pytest.mark.django_db
@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
def test_send_receipt_retryable_error(caplog, store_transaction, receipt):
    caplog.set_level(logging.ERROR)

    receipt.transaction = store_transaction
    receipt.save()

    with mock.patch("Instanssi.store.tasks.Receipt.send") as fn:
        fn.side_effect = SMTPServerDisconnected("boom")
        send_receipt.delay(receipt.id)

    # Make sure we logged (original attempt + retries)
    logs = filter(lambda x: x.message.startswith("Failed to send receipt"), caplog.records)
    assert len(list(logs)) == 11  # Original + 10 retries

    # Ensure no mail was sent
    assert len(mail.outbox) == 0

    # Make sure an event logs were written
    events = StoreTransactionEvent.objects.all()
    assert events.count() == 11
    for event in events:
        assert event.data == {"mail_to": receipt.mail_to, "receipt_id": receipt.id, "exception": "boom"}
        assert event.transaction == store_transaction
        assert event.message == "Receipt sending failure"
        assert event.created is not None
