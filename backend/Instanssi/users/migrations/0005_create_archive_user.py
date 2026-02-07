from django.db import migrations


def forwards(apps, schema_editor):
    User = apps.get_model("users", "User")
    user, created = User.objects.get_or_create(
        username="arkisto",
        defaults={
            "email": "admin@instanssi.org",
            "is_active": False,
            "is_system": True,
        },
    )
    if not created:
        user.email = "admin@instanssi.org"
        user.is_active = False
        user.is_system = True
        user.save(update_fields=["is_system", "is_active", "email"])


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_create_default_groups"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
