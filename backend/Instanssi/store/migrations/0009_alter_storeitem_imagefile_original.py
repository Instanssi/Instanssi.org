# Generated by Django 3.2.18 on 2023-03-12 14:33

from django.db import migrations, models

import Instanssi.store.models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0008_alter_storeitem_imagefile_original"),
    ]

    operations = [
        migrations.AlterField(
            model_name="storeitem",
            name="imagefile_original",
            field=models.ImageField(
                blank=True,
                help_text="Edustava kuva tuotteelle.",
                max_length=255,
                null=True,
                upload_to=Instanssi.store.models.generate_image_path,
                verbose_name="Tuotekuva",
            ),
        ),
    ]