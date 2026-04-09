"""Add live voting support and remove legacy voting fields.

Live voting replaces the old time-window-based voting mechanism.
Entries are revealed one-by-one during a live compo presentation,
and voting opens/closes on demand via LiveVotingState.

Removed fields: voting_start, is_votable (no longer used).
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("kompomaatti", "0024_add_entry_order_index"),
    ]

    operations = [
        migrations.AddField(
            model_name="entry",
            name="live_voting_revealed",
            field=models.BooleanField(default=False, verbose_name="Revealed in live voting"),
        ),
        migrations.CreateModel(
            name="LiveVotingState",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("voting_open", models.BooleanField(default=False, verbose_name="Voting open")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated at")),
                (
                    "compo",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="live_voting_state",
                        to="kompomaatti.compo",
                    ),
                ),
                (
                    "current_entry",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="kompomaatti.entry",
                    ),
                ),
            ],
        ),
        migrations.RemoveField(model_name="compo", name="voting_start"),
        migrations.RemoveField(model_name="compo", name="is_votable"),
    ]
