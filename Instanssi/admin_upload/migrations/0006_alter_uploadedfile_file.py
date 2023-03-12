# Generated by Django 3.2.18 on 2023-03-12 14:33

from django.db import migrations, models

import Instanssi.admin_upload.models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_upload", "0005_auto_20230311_2323"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uploadedfile",
            name="file",
            field=models.FileField(
                max_length=255,
                upload_to=Instanssi.admin_upload.models.generate_file_path,
                verbose_name="Tiedosto",
            ),
        ),
    ]
