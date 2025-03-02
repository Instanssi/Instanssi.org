# Generated by Django 1.11.13 on 2018-07-11 17:54
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("kompomaatti", "0001_initial"),
        ("arkisto", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="othervideocategory",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="kompomaatti.Event",
                verbose_name="Tapahtuma",
            ),
        ),
        migrations.AddField(
            model_name="othervideo",
            name="category",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="arkisto.OtherVideoCategory",
                verbose_name="Kategoria",
            ),
        ),
    ]
