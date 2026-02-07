"""One-time command to adopt the custom user model on an existing database.

When switching AUTH_USER_MODEL from 'auth.User' to 'users.User', Django's
migrate command refuses to run because admin.0001_initial (already applied)
depends on users.0001_initial (not yet applied). Neither --fake nor
--fake-initial bypass this consistency check.

This command:
1. Records users.0001_initial as applied (the auth_user table already exists)
2. Updates the content type from auth.user -> users.user

Run this ONCE before 'manage.py migrate' on any existing database.
It is safe to run multiple times (idempotent).
Delete this command after all environments have been migrated.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone


class Command(BaseCommand):
    help = "Record the custom user model migration as applied on an existing database."

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Check if already applied
            cursor.execute(
                "SELECT COUNT(*) FROM django_migrations WHERE app = 'users' AND name = '0001_initial'"
            )
            if cursor.fetchone()[0] > 0:
                self.stdout.write("users.0001_initial is already recorded as applied.")
            else:
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    ["users", "0001_initial", timezone.now()],
                )
                self.stdout.write(self.style.SUCCESS("Recorded users.0001_initial as applied."))

            # Update content type
            cursor.execute(
                "UPDATE django_content_type SET app_label = 'users' WHERE app_label = 'auth' AND model = 'user'"
            )
            if cursor.rowcount:
                self.stdout.write(self.style.SUCCESS("Updated content type auth.user -> users.user."))
            else:
                self.stdout.write("Content type already set to users.user (or not found).")

        self.stdout.write(self.style.SUCCESS("\nDone. You can now run: manage.py migrate"))
