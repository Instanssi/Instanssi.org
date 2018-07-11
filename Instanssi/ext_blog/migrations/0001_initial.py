# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-11 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BlogComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, help_text='Lyhyt otsikko kommentille.', max_length=128, verbose_name='Otsikko')),
                ('text', models.TextField(help_text='Kommenttiteksti.', verbose_name='Kommentti')),
                ('date', models.DateTimeField(verbose_name='Aika')),
            ],
            options={
                'verbose_name': 'kommentti',
                'verbose_name_plural': 'kommentit',
            },
        ),
        migrations.CreateModel(
            name='BlogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Lyhyt otsikko entrylle.', max_length=128, verbose_name='Otsikko')),
                ('text', models.TextField(verbose_name='Teksti')),
                ('date', models.DateTimeField(verbose_name='Aika')),
                ('public', models.BooleanField(default=False, help_text='Mikäli entry on julkinen, tulee se näkyviin sekä tapahtuman sivuille että RSS-syötteeseen.', verbose_name='Julkinen')),
            ],
            options={
                'verbose_name': 'entry',
                'verbose_name_plural': 'entryt',
            },
        ),
    ]
