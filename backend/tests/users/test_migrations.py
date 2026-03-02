import importlib

import pytest
from allauth.account.models import EmailAddress
from django.apps import apps

from Instanssi.users.models import User

_migration = importlib.import_module("Instanssi.users.migrations.0010_backfill_allauth_email_addresses")
backfill_email_addresses = _migration.backfill_email_addresses


@pytest.mark.django_db
def test_backfill_creates_verified_email_for_existing_user():
    """Verify the backfill logic: users with emails get verified EmailAddress records."""
    user = User.objects.create_user(username="migrationuser", email="migrate@example.com", password="test")
    EmailAddress.objects.filter(user=user).delete()

    backfill_email_addresses(apps, None)

    ea = EmailAddress.objects.get(user=user)
    assert ea.email == "migrate@example.com"
    assert ea.verified is True
    assert ea.primary is True


@pytest.mark.django_db
def test_backfill_skips_user_without_email():
    """Users without an email should not get an EmailAddress record."""
    user = User.objects.create_user(username="noemail", email="", password="test")

    backfill_email_addresses(apps, None)

    assert not EmailAddress.objects.filter(user=user).exists()


@pytest.mark.django_db
def test_backfill_is_idempotent():
    """Running the backfill twice should not create duplicate records."""
    user = User.objects.create_user(username="idempotent", email="idem@example.com", password="test")
    EmailAddress.objects.filter(user=user).delete()

    backfill_email_addresses(apps, None)
    backfill_email_addresses(apps, None)

    assert EmailAddress.objects.filter(user=user).count() == 1
