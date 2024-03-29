# Generated by Django 3.2.18 on 2023-03-11 21:23

import django.utils.timezone
from django.db import migrations, models

import Instanssi.admin_upload.models


class Migration(migrations.Migration):

    dependencies = [
        ("admin_upload", "0004_alter_uploadedfile_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="uploadedfile",
            name="date",
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name="Aika"),
        ),
        migrations.AlterField(
            model_name="uploadedfile",
            name="file",
            field=models.FileField(
                upload_to=Instanssi.admin_upload.models.generate_file_path, verbose_name="Tiedosto"
            ),
        ),
    ]
