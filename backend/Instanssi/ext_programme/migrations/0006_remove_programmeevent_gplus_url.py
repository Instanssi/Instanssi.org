# Generated by Django 3.2.18 on 2023-03-11 21:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ext_programme", "0005_auto_20230311_2323"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="programmeevent",
            name="gplus_url",
        ),
    ]
