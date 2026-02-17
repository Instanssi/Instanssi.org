from typing import Any

from django.db import migrations, models


def copy_otherinfo(apps: Any, schema_editor: Any) -> None:
    """Copy otherinfo from kompomaatti Profile to User model."""
    Profile = apps.get_model("kompomaatti", "Profile")
    User = apps.get_model("users", "User")
    seen_users: set[int] = set()
    for profile in Profile.objects.order_by("id"):
        if profile.user_id not in seen_users:
            seen_users.add(profile.user_id)
            User.objects.filter(pk=profile.user_id).update(otherinfo=profile.otherinfo)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_user_notification_preferences"),
        ("kompomaatti", "0021_add_sorting_indexes"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="otherinfo",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.RunPython(copy_otherinfo, migrations.RunPython.noop),
    ]
