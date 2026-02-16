"""Migrate social auth accounts from python-social-auth to django-allauth.

Reads from the old social_auth_usersocialauth table (if it exists) and
inserts matching rows into allauth's socialaccount_socialaccount table.
"""

from typing import Any

from django.db import migrations

# python-social-auth provider → allauth provider
PROVIDER_MAP = {
    "google-oauth2": "google",
    "github": "github",
}


def forwards(apps: Any, schema_editor: Any) -> None:
    connection = schema_editor.connection
    # Check if the old table exists
    tables = connection.introspection.table_names()
    if "social_auth_usersocialauth" not in tables:
        return

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, user_id, provider, uid, extra_data FROM social_auth_usersocialauth")
        rows = cursor.fetchall()

    if not rows:
        return

    SocialAccount = apps.get_model("socialaccount", "SocialAccount")
    for _id, user_id, provider, uid, extra_data in rows:
        new_provider = PROVIDER_MAP.get(provider)
        if not new_provider:
            continue  # Skip unknown providers (e.g. steam)
        if SocialAccount.objects.filter(provider=new_provider, uid=uid).exists():
            continue  # Skip duplicates
        SocialAccount.objects.create(
            user_id=user_id,
            provider=new_provider,
            uid=uid,
            extra_data=extra_data or "{}",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0007_user_notification_preferences"),
        ("socialaccount", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
