"""Migrate from python-social-auth to django-allauth.

Copies social account data from social_auth_usersocialauth to allauth's
socialaccount_socialaccount table, creates EmailAddress entries for existing
users, and drops the old social_auth tables.
"""

from typing import Any

from django.db import migrations

# Map old python-social-auth provider names to allauth provider IDs
PROVIDER_MAP = {
    "google-oauth2": "google",
    "github": "github",
    # Steam is dropped
}


def migrate_social_accounts(apps: Any, schema_editor: Any) -> None:
    """Copy social accounts from social_auth to allauth tables."""
    db_alias = schema_editor.connection.alias
    SocialAccount = apps.get_model("socialaccount", "SocialAccount")

    # Check if the old table exists
    with schema_editor.connection.cursor() as cursor:
        tables = schema_editor.connection.introspection.table_names(cursor)

    if "social_auth_usersocialauth" not in tables:
        return

    with schema_editor.connection.cursor() as cursor:
        cursor.execute("SELECT user_id, provider, uid, extra_data FROM social_auth_usersocialauth")
        rows = cursor.fetchall()

    for user_id, provider, uid, extra_data in rows:
        new_provider = PROVIDER_MAP.get(provider)
        if new_provider is None:
            continue  # Skip steam and unknown providers
        if not SocialAccount.objects.using(db_alias).filter(provider=new_provider, uid=uid).exists():
            SocialAccount.objects.using(db_alias).create(
                user_id=user_id,
                provider=new_provider,
                uid=uid,
                extra_data=extra_data or "{}",
            )


def create_email_addresses(apps: Any, schema_editor: Any) -> None:
    """Create allauth EmailAddress entries for existing users."""
    db_alias = schema_editor.connection.alias
    User = apps.get_model("users", "User")
    EmailAddress = apps.get_model("account", "EmailAddress")

    for user in User.objects.using(db_alias).exclude(email="").iterator():
        if not EmailAddress.objects.using(db_alias).filter(user=user, email=user.email).exists():
            EmailAddress.objects.using(db_alias).create(
                user=user,
                email=user.email,
                verified=True,
                primary=True,
            )


def drop_social_auth_tables(apps: Any, schema_editor: Any) -> None:
    """Drop old python-social-auth tables."""
    with schema_editor.connection.cursor() as cursor:
        tables = schema_editor.connection.introspection.table_names(cursor)

    tables_to_drop = [
        "social_auth_usersocialauth",
        "social_auth_nonce",
        "social_auth_association",
        "social_auth_code",
        "social_auth_partial",
    ]

    with schema_editor.connection.cursor() as cursor:
        for table in tables_to_drop:
            if table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_user_otherinfo"),
        ("socialaccount", "0001_initial"),
        ("account", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_social_accounts, migrations.RunPython.noop),
        migrations.RunPython(create_email_addresses, migrations.RunPython.noop),
        migrations.RunPython(drop_social_auth_tables, migrations.RunPython.noop),
    ]
