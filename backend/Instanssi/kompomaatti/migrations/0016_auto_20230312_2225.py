# Generated by Django 3.2.18 on 2023-03-12 20:25

from django.db import migrations


def forwards(apps, schema_editor):
    """Fill in created_at timestamp with something correct enough."""
    Event = apps.get_model("kompomaatti", "Event")
    for event in Event.objects.filter(tag__isnull=True):
        if event.name.startswith("Instanssi"):
            event.tag = str(event.date.year)
            event.save(update_fields=["tag"])


def backwards(apps, schema_editor):
    Event = apps.get_model("kompomaatti", "Event")
    for event in Event.objects.filter(tag__isnull=False):
        event.tag = None
        event.save(update_fields=["tag"])


class Migration(migrations.Migration):

    dependencies = [
        ("kompomaatti", "0015_event_tag"),
    ]

    operations = (migrations.RunPython(forwards, backwards),)