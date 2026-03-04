"""Remove legacy voting fields from Compo.

Live voting is now the only voting mechanism. The voting_start, is_votable,
and live_voting_enabled fields are no longer used.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("kompomaatti", "0024_live_voting"),
    ]

    operations = [
        migrations.RemoveField(model_name="compo", name="voting_start"),
        migrations.RemoveField(model_name="compo", name="is_votable"),
        migrations.RemoveField(model_name="compo", name="live_voting_enabled"),
    ]
