"""Create verified EmailAddress records for existing users that have an email.

This ensures existing users are not blocked by mandatory email verification
after migrating from python-social-auth to django-allauth.
"""

from typing import Any

from django.db import migrations


def backfill_email_addresses(apps: Any, schema_editor: Any) -> None:
    User = apps.get_model("users", "User")
    EmailAddress = apps.get_model("account", "EmailAddress")

    for user in User.objects.exclude(email="").exclude(email__isnull=True):
        EmailAddress.objects.update_or_create(
            user=user,
            email=user.email,
            defaults={"verified": True, "primary": True},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0009_alter_user_language"),
        ("account", "0009_emailaddress_unique_primary_email"),
    ]

    operations = [
        migrations.RunPython(backfill_email_addresses, migrations.RunPython.noop),
    ]
