# Generated by Django 2.0.7 on 2018-07-11 18:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ext_programme", "0002_programmeevent_event"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programmeevent",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="kompomaatti.Event",
                verbose_name="Tapahtuma",
            ),
        ),
    ]