# Generated by Django 2.1.2 on 2018-10-23 15:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_auto_20180711_2110"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="storetransaction",
            options={"verbose_name": "transaktio", "verbose_name_plural": "transaktiot"},
        ),
    ]