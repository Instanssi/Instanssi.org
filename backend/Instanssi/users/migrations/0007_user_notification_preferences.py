from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_user_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="notify_vote_code_requests",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="notify_program_events",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="notify_compo_starts",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="user",
            name="notify_competition_starts",
            field=models.BooleanField(default=True),
        ),
    ]
