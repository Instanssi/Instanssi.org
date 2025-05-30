# Generated by Django 1.11.13 on 2018-07-11 17:54
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("kompomaatti", "0001_initial"),
        ("store", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="ticketvotecode",
            name="ticket",
            field=models.ForeignKey(
                blank=True,
                help_text="Lipputuote jonka avainta käytetään äänestysavaimena",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="store.TransactionItem",
                verbose_name="Lipputuote",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Käyttäjä",
            ),
        ),
        migrations.AddField(
            model_name="entry",
            name="compo",
            field=models.ForeignKey(
                help_text="Kompo johon osallistutaan",
                on_delete=django.db.models.deletion.CASCADE,
                to="kompomaatti.Compo",
                verbose_name="kompo",
            ),
        ),
        migrations.AddField(
            model_name="entry",
            name="user",
            field=models.ForeignKey(
                help_text="Käyttäjä jolle entry kuuluu",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="käyttäjä",
            ),
        ),
        migrations.AddField(
            model_name="compo",
            name="event",
            field=models.ForeignKey(
                help_text="Tapahtuma johon kompo kuuluu",
                on_delete=django.db.models.deletion.CASCADE,
                to="kompomaatti.Event",
                verbose_name="tapahtuma",
            ),
        ),
        migrations.AddField(
            model_name="competitionparticipation",
            name="competition",
            field=models.ForeignKey(
                help_text="Kilpailu johon osallistuttu",
                on_delete=django.db.models.deletion.CASCADE,
                to="kompomaatti.Competition",
                verbose_name="Kilpailu",
            ),
        ),
        migrations.AddField(
            model_name="competitionparticipation",
            name="user",
            field=models.ForeignKey(
                help_text="Osallistuja",
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name="Käyttäjä",
            ),
        ),
        migrations.AddField(
            model_name="competition",
            name="event",
            field=models.ForeignKey(
                help_text="Tapahtuma johon kilpailu kuuluu",
                on_delete=django.db.models.deletion.CASCADE,
                to="kompomaatti.Event",
                verbose_name="Tapahtuma",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="votegroup",
            unique_together=set([("user", "compo")]),
        ),
        migrations.AlterUniqueTogether(
            name="votecoderequest",
            unique_together=set([("event", "user")]),
        ),
        migrations.AlterUniqueTogether(
            name="ticketvotecode",
            unique_together=set([("event", "associated_to"), ("event", "ticket")]),
        ),
    ]
